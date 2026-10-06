#!/usr/bin/env bash
set -euo pipefail

# Local builds and CI use the same checksum-verified Nerd Fonts 3.5.1 patcher.
patcher=$(python3 script_helper/fetch_build_dependencies.py nerd-font-patcher)
for style in Regular Italic Bold Bold-Italic; do
    if [[ -f "export/Monofoki-${style}.otf" ]]; then
        fontforge -lang=py -script "$patcher" --no-progressbars --complete \
            --braille rectangle --outputdir export/ "export/Monofoki-${style}.otf"
    fi
    input="export/Monofoki-${style}.ttf"
    hinted="export/Monofoki-${style}-hinted.ttf"
    if [[ -f "$hinted" && "$hinted" -nt "$input" ]]; then
        input="$hinted"
    fi
    if [[ -f "$input" ]]; then
        fontforge -lang=py -script "$patcher" --no-progressbars --complete \
            --braille rectangle --outputdir export/ "$input"
    fi
done
python3 script_helper/preserve_nerd_font_names.py export/MonofokiNerdFont-*.ttf export/MonofokiNerdFont-*.otf
cp licenses/LICENSE-NerdFonts export/LICENSE-nerd-font
cp licenses/license-audit-nerd-font.md export/license-audit-nerd-font.md
