#!/usr/bin/env python3
"""Builds the Korean pages under /ko/ and the sitemap from the bilingual pages.

    tools/i18n.py

Every page (index.html outside ko/, assets/, brand/, tools/) is written once, in both
languages: data-en / data-ko elements, English shown by default. That file is the
English URL. This script then, for each page:

- writes ko/<path>/index.html: lang="ko", the data-en elements removed, canonical and
  og:url on the /ko/ URL, links to other pages pointing at their /ko/ version, and the
  title and description taken from the page's <meta name="ko:title"> and
  <meta name="ko:description"> (left in English when those are missing);
- adds hreflang alternates (en, ko, x-default) and assets/lang.js (sends Korean readers
  from the English URL to /ko/) to both versions;
- rewrites sitemap.xml with every URL in both languages.

Rerun it after changing any page (and after tools/manual.py). Don't edit ko/ by hand.
"""
import datetime
import html
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

SITE = Path(__file__).resolve().parent.parent
BASE = "https://xkorfun.github.io"
SKIP = {"ko", "assets", "brand", "tools", "img"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


def pages():
    """URL paths ("/", "/dockpin/", ...) of the bilingual source pages."""
    found = []
    for f in sorted(SITE.rglob("index.html")):
        rel = f.relative_to(SITE)
        if rel.parts[0] in SKIP or rel.parts[0].startswith("."):
            continue
        found.append("/" + "".join(p + "/" for p in rel.parts[:-1]))
    return found


class Strip(HTMLParser):
    """Copies HTML through unchanged, minus the elements carrying a given attribute."""

    def __init__(self, attr):
        super().__init__(convert_charrefs=False)
        self.attr, self.out, self.depth = attr, [], 0

    def emit(self, text):
        if not self.depth:
            self.out.append(text)

    def handle_starttag(self, tag, attrs):
        if self.depth:
            if tag not in VOID:
                self.depth += 1
        elif any(k == self.attr for k, _ in attrs):
            if tag not in VOID:
                self.depth = 1
        else:
            self.out.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if not self.depth and not any(k == self.attr for k, _ in attrs):
            self.out.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1
        else:
            self.out.append(f"</{tag}>")

    def handle_data(self, data): self.emit(data)
    def handle_entityref(self, name): self.emit(f"&{name};")
    def handle_charref(self, name): self.emit(f"&#{name};")
    def handle_comment(self, data): self.emit(f"<!--{data}-->")
    def handle_decl(self, decl): self.emit(f"<!{decl}>")
    def handle_pi(self, data): self.emit(f"<?{data}>")

    def unknown_decl(self, data): self.emit(f"<![{data}]>")


def alternates(path):
    return ("<!-- hreflang: tools/i18n.py -->\n"
            f'<link rel="alternate" hreflang="en" href="{BASE}{path}">\n'
            f'<link rel="alternate" hreflang="ko" href="{BASE}/ko{path}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{BASE}{path}">\n'
            '<script src="/assets/lang.js"></script>\n')


def with_alternates(text, path):
    text = re.sub(r"<!-- hreflang: tools/i18n.py -->\n(<link rel=\"alternate\" hreflang=[^\n]*\n)*(<script src=\"/assets/lang.js\"></script>\n)?", "", text)
    return re.sub(r'(<link rel="canonical"[^>]*>\n)', lambda m: m.group(1) + alternates(path), text, count=1)


def korean(text, path, all_pages):
    text = text.replace('<html lang="en">', '<html lang="ko">', 1)
    stripper = Strip("data-en")
    stripper.feed(text)
    stripper.close()
    text = "".join(stripper.out)

    meta = dict(re.findall(r'<meta name="ko:(title|description)" content="([^"]*)">\n?', text))
    text = re.sub(r'<meta name="ko:(title|description)" content="[^"]*">\n?', "", text)
    if "title" in meta:
        text = re.sub(r"<title>[^<]*</title>", f"<title>{meta['title']}</title>", text, count=1)
        text = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + meta["title"], text)
    if "description" in meta:
        for attr in ('name="description"', 'property="og:description"'):
            text = re.sub(rf'(<meta {attr} content=")[^"]*', lambda m: m.group(1) + meta["description"], text)
    text = text.replace('<meta property="og:locale" content="en_US">', '<meta property="og:locale" content="ko_KR">')

    def link(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"[a-z]+:|#|//", url):
            if url.startswith(BASE + "/"):
                url = url[len(BASE):]
            else:
                return m.group(0)
        target = urljoin(path, url)
        bare = target.split("#")[0].split("?")[0]
        if attr == "href" and bare in all_pages:
            target = "/ko" + target
        if m.group(2).startswith(BASE):
            target = BASE + target
        return f'{attr}="{target}"'

    text = re.sub(r'\b(href|src)="([^"]*)"', link, text)
    for tag in ('<link rel="canonical" href="', '<meta property="og:url" content="'):
        text = re.sub(re.escape(tag) + r'[^"]*', lambda m: tag + BASE + "/ko" + path, text)
    return with_alternates(text, path)


def lastmod(f):
    """Date of the last commit touching the file, or today if it has uncommitted changes."""
    dirty = subprocess.run(["git", "status", "--porcelain", "--", str(f)], cwd=SITE,
                           capture_output=True, text=True).stdout.strip()
    date = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(f)], cwd=SITE,
                          capture_output=True, text=True).stdout.strip()
    return date if date and not dirty else datetime.date.today().isoformat()


def main():
    all_pages = pages()
    shutil.rmtree(SITE / "ko", ignore_errors=True)
    for path in all_pages:
        src = SITE / path.strip("/") / "index.html"
        text = with_alternates(src.read_text(), path)
        src.write_text(text)
        dest = SITE / "ko" / path.strip("/") / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(korean(text, path, all_pages))
        print(f"{path} -> /ko{path}")

    urls = []
    for path in all_pages:
        alt = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{lang}" href="{BASE}{prefix}{path}"/>'
                      for lang, prefix in (("en", ""), ("ko", "/ko"), ("x-default", "")))
        mod = lastmod(SITE / path.strip("/") / "index.html")
        for prefix in ("", "/ko"):
            urls.append(f"  <url>\n    <loc>{BASE}{prefix}{path}</loc>\n    <lastmod>{mod}</lastmod>{alt}\n  </url>\n")
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "".join(urls) + "</urlset>\n")
    print(f"sitemap.xml: {2 * len(all_pages)} URLs")


if __name__ == "__main__":
    main()
