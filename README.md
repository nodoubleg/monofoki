# Fork of the font Mononoki; *Monofoki*

This is a fork of [datMaffin/monofoki](https://github.com/datMaffin/monofoki), itself based on [Mononoki](https://github.com/madmalik/mononoki).
Compared with datMaffin's fork, it fills terminal-symbol gaps, aligns Braille with Nerd Fonts 3.5.1, restores three italic arrows, and builds all four styles in CI.

Try the [live font specimen](https://nodoubleg.github.io/monofoki/) or [download a release](https://github.com/nodoubleg/monofoki/releases/latest).

## [Specimen](script_helper/specimen.pdf)

## Goals of this fork
The goal of this fork is to change the Mononoki font to use my preferences. 
This means that various glyphs and their dependencies were modified and that the bold style no longer has a larger height than the regular style.

This version also tries to fix all the known issues and at times adds additional glyphs.

**Disclaimer: I am *not* a professional in the field of type-design!**

### Fundamental changes were:
- [x] Make the "m" similar to Ubuntu Mono "m"
- [x] Decrease width of "n" similar to Ubuntu Mono
  + Change glyphs dependent on "n" correspondingly: "h", "r", "u", "k"
- [x] Increase width of "o" similar to Ubuntu Mono
  + Change glyphs dependent on "o" correspondingly: "O", "e", "U", "Q"
  + [x] Also need to check size relation to "C", "c" and "G".
        Looks ok... "O" is a little bit wider than "C" and "G". "C" and "G" 
        have the same width. May increase width of "C" and "G" a little bit.
- [x] Increase width of "s" similar to Ubuntu Mono
  + Study the relation of width from "s" to "S" in other Fonts.
    Fonts vary in  their relation. Decided on mononoki "s" looks perfectly 
    fine.
- [x] Use "l" glyph for the "i" as well
- [x] Increase height of middle line in "a" to line up with "e"
  - [x] May need further refinement
- [x] Italic "J" and BoldItalic "J" have different shapes
- [x] Decrease width of "w" to be more similar in width with "m"
  - [x] May need further refinement
- [x] Fix missing UTF-8 glyphs: ä, ö, ü
  + This problem happens when creating a file with the macOS finder 
    conaining ä, ö, ü: When using iTerm the file name is not printed in the 
    Mononoki-Font.
  + The **fix** was: Add zero width glyph COMBINING DIARESIS (Nr. 776) with 
    diaresis in negative space.
  + Setting all the combining characters to "mark" and having them in the regular (positive) space also seemed to work
- [x] Reduce bold italic "r" stem width to equal all other letters stem widths
- [x] TTF autohinted bold italic "o" is too high (turned out to be an exclusive 
      Java/Intellij Idea issue; probably not related to TTF autohinted)
- [x] CANCELED: Put "E" and "F" middle stroke ontu the same height

#### Further experiments/provide more options
* Lower the bar of "f" similar to Consolas
* Create a build pipeline (with the source being FontForge .sfd files)
  - Use ttfautohint
* Bold currently increases the height of glyphs a little to much for my taste.
  - Bold is now auto generated: Generate the bold sfd's from the regular sfd's with the `script_helper/generate_bold_sfd.sh` script.

## Fork specific problems to solve
* FontForge does not have a tool to create rounded edges

## Automated builds

The [Build fonts workflow](https://github.com/nodoubleg/monofoki/actions/workflows/build-fonts.yml)
runs on pushes to `master`, `v*` tags, pull requests, and manual runs from the
Actions tab. It uses an Ubuntu 24.04 GitHub runner to build all four styles
with `./create_font.sh --hint`, then applies checksum-pinned Nerd Fonts 3.5.1 patching.
Source and exported glyph checks must pass before each artifact is uploaded.

Download `Monofoki-<commit>` or `MonofokiNerdFont-<commit>` from the run's
Artifacts section. The regular bundle contains TTF, hinted TTF, OTF, WOFF2
from OTF, hinted WOFF2 from TTF, and the font license. The Nerd Font bundle
contains patched TTF (from the hinted build), OTF, WOFF2 from OTF, and licenses.
Artifacts are retained for 30 days. Generated fonts are uploaded as artifacts
and are not committed to the repository.

The same run builds the [GitHub Pages specimen](https://nodoubleg.github.io/monofoki/)
using its WOFF2 artifacts and records a terminal demo with VHS. Only `master`
publishes the site. Print all of the site's artwork with
`python3 script_helper/terminal_demo.py --art`.

## Terminal graphics

All four styles include the 256 Unicode Braille patterns (`U+2800–U+28FF`).
These are often used for dotted terminal artwork. The glyphs match Nerd Fonts
3.5.1's default rectangle geometry: upright 172.5 by 184.5-unit dots on a
two-column, four-row grid. The grid fills
Monofoki's existing 575-unit-wide, 1230-unit-high character cell, so the dot
spacing continues across character and line boundaries. Font metrics and
existing glyphs are unchanged. Bold generation leaves Braille unemboldened.

To try the font, build with `./create_font.sh`, install the resulting fonts
from `export/`, select Monofoki in your terminal, and run:

```sh
python3 script_helper/terminal_demo.py
python3 script_helper/terminal_demo.py --all  # also show every Braille pattern
```

The demo includes artwork, a repeated dot grid, box and block joins, arrows,
and ANSI bold/italic samples when output goes to a terminal. `--plain` omits
ANSI styling; `--width 32` makes the artwork smaller. It uses your terminal's
active font; it does not install or select a font. Extra terminal line spacing
can still introduce gaps, and some terminals draw graphics themselves.
For Nerd Font builds, run `./post_create_nerdfonts.sh` after building; it needs
FontForge, Python 3 with fontTools, and curl. It downloads and verifies the pinned 3.5.1
patcher rather than using a different version on `PATH`. It prefers a hinted
TTF only when that file is
newer than the unhinted TTF. To refresh hinted files too, install `ttfautohint`
and build with `./create_font.sh --hint`.

Source maintenance and validation:

```sh
python3 script_helper/add_braille.py          # regenerate Braille records only
python3 script_helper/add_braille.py --check  # verify source geometry
fontforge -lang=py -script script_helper/add_terminal_symbols.py --check
python3 script_helper/check_unicode_data.py
fontforge -lang=py -script script_helper/check_terminal_glyphs.py
fontforge -lang=py -script script_helper/check_terminal_glyphs.py export/Monofoki-Regular.ttf
```

The outline check verifies all 256 encodings against Unicode dot names,
including the blank pattern, grid positions, contour direction, cell width,
unchanged line metrics, and coverage of ASCII, boxes, blocks and restored
arrows. It allows half a font unit of export rounding.

The four sources now have identical encoded character coverage. Three arrows
(`⇨` U+21E8, `⇩` U+21E9, `⇯` U+21EF) were restored in Italic and Bold-Italic
using Monofoki's own glyphs/references at the corresponding weight.

### Unicode symbols on macOS

The terminal-symbol target is the 2,113 assigned printable characters in the
14 ranges listed by `perl script_helper/unicode_specimen.pl --list`, using
Unicode 18.0.0. This update adds 415 symbols that were missing with macOS
system fallback, including ribbon arrows, astrological symbols, and legacy
computing graphics. It preserves existing glyphs and uses matching Unicode
outlines from Nerd Fonts 3.5.1's Iosevka build first, then Noto Sans Symbols 2
and Kreative Square. Sources, transformations and licenses are recorded in
`script_helper/symbol_additions.json` and `licenses/NOTICES-symbols.md`.

The target is Terminal.app and iTerm2 on macOS, with Monofoki selected and no
separate non-ASCII font override. Built-in macOS fonts supply symbols already
covered by system fallback. This is not a claim of all-Unicode coverage.
The macOS release check is:

```sh
swift script_helper/check_macos_symbols.swift export/MonofokiNerdFont-*.otf
perl script_helper/unicode_specimen.pl --font export/MonofokiNerdFont-Regular.otf
```

The Perl specimen uses bundled Unicode 18.0.0 assignment, name and width data,
even when the installed Perl has an older Unicode database. Its default
`--presentation emoji` adds FE0F only to standardized non-ASCII emoji bases;
macOS supplies the color glyphs from Apple Color Emoji. `--presentation text`
requests FE0E; `--presentation native` leaves the characters untouched. Actual
application output chooses its own selectors, so the font cannot force every
emoji-capable character into the same presentation. `!` checks the font file's
base-character map; a character marked absent can still render via fallback.

## Other TODOs
- [x] Fix directions of glyphs in FontForge
- [x] .ttf fonts wont work on macOS (otf is working)
- [x] macOS is still complaining about the name table
- [x] FontForge tutorial says to change layers to quadratic before exporting 
      font as ttfs
- [x] Issues with back- and frontticks: for some reason they get wrongly
      rendered on top of the letter infront.
      Adding all combining accents (from UTF 0x300 onward) did not resolve
      this issue.
      Solution (Fix) was:
      For all affected glyphs set "OT Glyph Class" to "Base Glyph"
