#!/usr/bin/env python3
"""Builds /<app>/manual/ from the app repo's English and Korean manuals.

    tools/manual.py <app> <app-repo>/docs/manual.md <app-repo>/docs/manual.ko.md

The manuals stay the source of truth in the app repo; rerun this after changing them.
Images they reference (paths relative to docs/) are copied to /<app>/; a GIF with an
MP4 of the same name next to it becomes a looping video.

Handles the Markdown the manuals use: headings, paragraphs, lists (one level of
nesting), tables, fenced code, images, links, **bold** and `code`.
"""
import html
import re
import shutil
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent


def slug(text):
    """GitHub's heading anchor: lowercase, drop punctuation, spaces to hyphens."""
    text = re.sub(r"[^\w\- ]", "", text.lower())
    return text.replace(" ", "-")


class Page:
    def __init__(self, app, lang, src):
        self.app, self.lang, self.src = app, lang, Path(src)
        self.docs = self.src.parent
        self.toc = []
        self.title = app

    def asset(self, path):
        """Copies a docs-relative file to /<app>/ and returns its site URL."""
        if re.match(r"[a-z]+:", path) or path.startswith("#"):
            return path
        dest = SITE / self.app / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.docs / path, dest)
        return f"/{self.app}/{path}"

    def link(self, href):
        if href.startswith("#"):
            return f"#{self.lang}-{href[1:]}"
        return self.asset(href)

    def inline(self, text):
        codes = []

        def keep(m):
            codes.append(f"<code>{html.escape(m.group(1))}</code>")
            return f"\0{len(codes) - 1}\0"

        text = re.sub(r"`([^`]+)`", keep, text)
        text = html.escape(text, quote=False)

        def image(m):
            alt, src = m.group(1), m.group(2)
            if src.endswith(".gif") and (self.docs / src[:-4]).with_suffix(".mp4").exists():
                mp4 = self.asset(src[:-4] + ".mp4")
                return (f'<video src="{mp4}" autoplay muted loop playsinline '
                        f'aria-label="{html.escape(alt)}"></video>')
            return f'<img src="{self.asset(src)}" alt="{html.escape(alt)}" loading="lazy">'

        text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image, text)
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                      lambda m: f'<a href="{self.link(m.group(2))}">{m.group(1)}</a>', text)
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        return re.sub(r"\0(\d+)\0", lambda m: codes[int(m.group(1))], text)

    def render(self):
        lines = self.src.read_text().split("\n")
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
            elif line.startswith("```"):
                j = i + 1
                while not lines[j].startswith("```"):
                    j += 1
                out.append("<pre><code>" + html.escape("\n".join(lines[i + 1:j])) + "</code></pre>")
                i = j + 1
            elif line.startswith("# "):
                self.title = line[2:].strip()
                out.append(f"<h1>{self.inline(self.title)}</h1>")
                i += 1
            elif line.startswith("## "):
                text = line[3:].strip()
                anchor = f"{self.lang}-{slug(text)}"
                self.toc.append((anchor, text))
                out.append(f'<h2 id="{anchor}">{self.inline(text)}</h2>')
                i += 1
            elif line.startswith("|"):
                rows = []
                while i < len(lines) and lines[i].startswith("|"):
                    rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                    i += 1
                head, body = rows[0], rows[2:]
                t = ["<table>"]
                if any(head):
                    t.append("<thead><tr>" + "".join(f"<th>{self.inline(c)}</th>" for c in head) + "</tr></thead>")
                t.append("<tbody>" + "".join(
                    "<tr>" + "".join(f"<td>{self.inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody>")
                out.append("".join(t) + "</table>")
            elif re.match(r"(- |\d+\. )", line):
                i = self.list(lines, i, out)
            else:
                para = []
                while i < len(lines) and lines[i].strip() and not re.match(r"(#|```|\||- |\d+\. )", lines[i]):
                    para.append(lines[i].strip())
                    i += 1
                text = " ".join(para)
                # The language switch and the "watch as MP4" link are page chrome on the site.
                if re.fullmatch(r"(\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\.md\))( · (\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\.md\)))+", text):
                    continue
                if re.fullmatch(r"\[[^\]]+\]\([^)]+\.mp4\)", text):
                    continue
                out.append(f"<p>{self.inline(text)}</p>")
        return "\n".join(out)

    def list(self, lines, i, out):
        ordered = bool(re.match(r"\d+\. ", lines[i]))
        items = []
        while i < len(lines) and re.match(r"(- |\d+\. )", lines[i]):
            text = [re.sub(r"^(- |\d+\. )", "", lines[i])]
            sub = []
            i += 1
            while i < len(lines) and lines[i].startswith("  "):
                if re.match(r"\s+- ", lines[i]):
                    sub.append(re.sub(r"^\s+- ", "", lines[i]))
                elif sub:
                    sub[-1] += " " + lines[i].strip()
                else:
                    text.append(lines[i].strip())
                i += 1
            body = self.inline(" ".join(text))
            if sub:
                body += "<ul>" + "".join(f"<li>{self.inline(s)}</li>" for s in sub) + "</ul>"
            items.append(body)
        # A list of in-page links is the manual's own table of contents; the site builds one.
        if all(re.fullmatch(r'<a href="#[^"]+">[^<]+</a>', it) for it in items):
            return i
        tag = "ol" if ordered else "ul"
        out.append(f"<{tag}>" + "".join(f"<li>{it}</li>" for it in items) + f"</{tag}>")
        return i


def main():
    app, en_src, ko_src = sys.argv[1:4]
    pages = [Page(app, "en", en_src), Page(app, "ko", ko_src)]
    bodies = [p.render() for p in pages]
    en, ko = pages

    def toc(p):
        return "".join(f'<li><a href="#{a}">{html.escape(t)}</a></li>' for a, t in p.toc)

    tmpl = (SITE / "tools" / "manual.html").read_text()
    page = (tmpl.replace("{{app}}", app)
            .replace("{{title_en}}", html.escape(en.title))
            .replace("{{toc_en}}", toc(en)).replace("{{toc_ko}}", toc(ko))
            .replace("{{body_en}}", bodies[0]).replace("{{body_ko}}", bodies[1]))
    dest = SITE / app / "manual" / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page)
    print(f"wrote {dest.relative_to(SITE)}")


if __name__ == "__main__":
    main()
