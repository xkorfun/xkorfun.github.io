#!/usr/bin/env bash
# Builds the site's own icons and share image from brand/.
#   brand/make.sh
# Writes (all committed; the site itself has no build step):
#   img/xkorfun.png         512, the brand icon (header, og.html)
#   favicon.ico             16/32/48, for browsers and crawlers that ask for /favicon.ico
#   favicon-96.png          what pages link as their icon (Google wants a multiple of 48)
#   apple-touch-icon.png    180, on the ink background (iOS fills transparency with black)
#   img/og.png              1200×630 share image, rendered from brand/og.html
# Needs Xcode (Icon Composer's ictool) and Google Chrome; XCODE and CHROME override their locations.
set -euo pipefail
cd "$(dirname "$0")/.."

XCODE="${XCODE:-/Applications/Xcode.app}"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
ictool="$XCODE/Contents/Applications/Icon Composer.app/Contents/Executables/ictool"
src=brand/xkorfun.icon

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

render() {  # size, output
  "$ictool" "$src" --export-image --output-file "$2" --platform macOS --rendition Default \
    --width "$1" --height "$1" --scale 1 >/dev/null
}
render 512 img/xkorfun.png
render 96 favicon-96.png
for s in 16 32 48; do render "$s" "$work/$s.png"; done
render 180 "$work/touch.png"

# favicon.ico: an ICO directory pointing at the PNGs as they are.
python3 - "$work" <<'EOF'
import struct, sys
work = sys.argv[1]
pngs = [open(f"{work}/{s}.png", "rb").read() for s in (16, 32, 48)]
out = struct.pack("<HHH", 0, 1, len(pngs))
offset = 6 + 16 * len(pngs)
for s, data in zip((16, 32, 48), pngs):
    out += struct.pack("<BBBBHHII", s, s, 0, 0, 1, 32, len(data), offset)
    offset += len(data)
open("favicon.ico", "wb").write(out + b"".join(pngs))
EOF

cat > "$work/touch.html" <<EOF
<body style="margin:0;width:180px;height:180px;background:#1c1f26">
<img src="file://$work/touch.png" width="180" height="180" style="display:block;transform:scale(1.22)">
</body>
EOF
shot() {  # size, output, url
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files \
    --force-device-scale-factor=1 --window-size="$1" --screenshot="$2" "$3" >/dev/null 2>&1
}
shot 180,180 apple-touch-icon.png "file://$work/touch.html"
shot 1200,630 img/og.png "file://$PWD/brand/og.html"

echo "wrote img/xkorfun.png, favicon.ico, favicon-96.png, apple-touch-icon.png, img/og.png"
