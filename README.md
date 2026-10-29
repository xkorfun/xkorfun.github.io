# xkorfun.github.io

Site for [xkorfun](https://xkorfun.github.io): small, free, open-source Mac apps.

Plain HTML, no build step. GitHub Pages serves `main` as is.

- `index.html` lists the apps (English and Korean, picked from the browser language).
- To add an app: copy the `<article class="app">` block and put its icon and screenshot in `img/`.

Preview locally: `python3 -m http.server 47821` and open http://localhost:47821/.
