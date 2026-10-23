#!/bin/sh
# Wraps the artifact source into the GitHub Pages page. The Artifact tool publishes src/dashboard.html as-is.
cd "$(dirname "$0")"
{ printf '<!doctype html>\n<html lang="en">\n<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>\n<body>\n'; cat src/dashboard.html; printf '\n</body>\n</html>\n'; } > index.html
