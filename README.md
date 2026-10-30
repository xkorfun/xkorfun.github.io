# xkorfun.github.io

Site for [xkorfun](https://xkorfun.github.io): small, free, open-source Mac apps.

Plain HTML, no build step. GitHub Pages serves `main` as is.

- `index.html` lists the apps (English and Korean, picked from the browser language).
- `assets/site.css`, `assets/site.js`: shared by every page (styles, the EN/한국어 switch, copy buttons).
- To add an app: copy the `<article class="app">` block and put its icon and screenshot in `img/`.
- `/<app>/`: the app's own page, written by hand (copy `dockpin/index.html`).
- `/<app>/manual/`: generated from the app repo's `docs/manual.md` and `docs/manual.ko.md`;
  don't edit it, rerun `tools/manual.py <app> <repo>/docs/manual.md <repo>/docs/manual.ko.md`.
  The script copies the images the manual uses into `/<app>/`.

Preview locally: `python3 -m http.server 47821` and open http://localhost:47821/.
