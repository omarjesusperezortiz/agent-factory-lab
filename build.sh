#!/bin/sh
# Builds the GitHub Pages site from src/:
#   src/landing.html  → index.html            (full page, copied as is)
#   src/console.html  → console/index.html    (fragment, wrapped; also the claude.ai Artifact)
#   src/research.html → research/index.html   (fragment, wrapped)
cd "$(dirname "$0")"
wrap() { mkdir -p "$(dirname "$2")"; { printf '<!doctype html>\n<html lang="en">\n<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>\n<body>\n'; cat "$1"; printf '\n</body>\n</html>\n'; } > "$2"; }
cp src/landing.html index.html
wrap src/console.html console/index.html
wrap src/research.html research/index.html
