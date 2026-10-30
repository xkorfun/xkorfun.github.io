# xkorfun.github.io

Site for [xkorfun](https://xkorfun.github.io): small, free, open-source Mac apps.

Plain HTML, no build step. GitHub Pages serves `main` as is.

- `index.html` lists the apps.
- Every page is written once with both languages (`data-en` / `data-ko` elements) and is
  served as the English URL. `tools/i18n.py` writes the Korean URLs under `/ko/` (English
  removed, links and canonical on `/ko/`, title and description from the page's
  `<meta name="ko:title">` / `<meta name="ko:description">`), adds hreflang links to both,
  and rewrites `sitemap.xml`. **Rerun it after changing any page**; never edit `ko/`.
  `assets/lang.js` sends Korean browsers from an English URL to `/ko/` unless the reader
  chose English.
- `assets/site.css`, `assets/site.js`: shared by every page (styles, the EN/한국어 switch, copy buttons).
- To add an app: copy the `<article class="app">` block and put its icon and screenshot in `img/`.
- `/<app>/`: the app's own page, written by hand (copy `dockpin/index.html`).
- `/<app>/manual/`: generated from the app repo's `docs/manual.md` and `docs/manual.ko.md`;
  don't edit it, rerun `tools/manual.py <app> <repo>/docs/manual.md <repo>/docs/manual.ko.md`,
  then `tools/i18n.py`.
  The script copies the images the manual uses into `/<app>/`.

- `brand/`: the site's own icon. `xkorfun.icon` is an Icon Composer document (same style
  as the app icons: flat SVG layers, Liquid Glass applied by the system), `og.html` is the
  1200×630 share image. `brand/make.sh` (needs Xcode and Chrome) writes `img/xkorfun.png`,
  `favicon.ico`, `favicon-96.png`, `apple-touch-icon.png` and `img/og.png`. Rerun it after
  adding an app icon to `og.html`.

Preview locally: `python3 -m http.server 47821` and open http://localhost:47821/.
