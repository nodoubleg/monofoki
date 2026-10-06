#!/usr/bin/env python3
"""Validate actual outlines with FontForge, including exported font rounding.

    fontforge -lang=py -script script_helper/check_terminal_glyphs.py [fonts ...]

Defaults to the four source SFDs. Supply exported TTF/OTF files to check the build.
"""

import sys
import unicodedata
from pathlib import Path

import fontforge


def check(path):
    font = fontforge.open(str(path))
    try:
        assert font.em == 1024, (path, "em changed")
        assert (font.hhea_ascent, font.hhea_descent, font.hhea_linegap) == (910, -320, 0)
        assert font.os2_typoascent - font.os2_typodescent + font.os2_typolinegap == 1230
        width = font[0x20].width
        assert width == 575
        # Independent expectation from Unicode character names, not the generator.
        columns = {1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 0, 8: 1}
        rows = {1: 0, 2: 1, 3: 2, 4: 0, 5: 1, 6: 2, 7: 3, 8: 3}
        for cp in range(0x2800, 0x2900):
            assert cp in font, (path, hex(cp), "missing")
            glyph = font[cp]
            assert glyph.width == width, (path, hex(cp), "advance")
            assert not glyph.references, (path, hex(cp), "unexpected reference")
            name = unicodedata.name(chr(cp))
            dots = [] if cp == 0x2800 else [int(n) for n in name.split("-")[1]]
            expected = sorted(((columns[n] + 0.5) * width / 2,
                               910 - (rows[n] + 0.5) * 1230 / 4) for n in dots)
            actual = []
            for contour in glyph.foreground:
                assert contour.closed and contour.isClockwise(), (path, hex(cp), "contour")
                points = list(contour)
                assert len(points) == 4 and all(p.on_curve for p in points)
                xs, ys = [p.x for p in points], [p.y for p in points]
                assert len(set(xs)) == 2 and len(set(ys)) == 2
                assert abs(max(xs) - min(xs) - 178) <= 1
                assert abs(max(ys) - min(ys) - 178) <= 1
                actual.append(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2))
            assert len(actual) == len(expected), (path, hex(cp), "dot count")
            for observed, wanted in zip(sorted(actual), expected):
                assert all(abs(a - b) <= 0.5 for a, b in zip(observed, wanted)), (path, hex(cp), observed, wanted)
        # All graphics ranges involved in the fix must survive every export.
        for cp in [*range(0x20, 0x7f), *range(0x2500, 0x25a0), 0x21e8, 0x21e9, 0x21ef]:
            assert cp in font, (path, hex(cp), "missing graphic")
        for cp in (0x21e8, 0x21e9, 0x21ef):
            assert font[cp].width == width
            left, bottom, right, top = font[cp].boundingBox()
            assert right > left and top > bottom, (path, hex(cp), "empty arrow")
        print(f"PASS {path}: 256 Braille patterns, metrics, ASCII, boxes, blocks, arrows")
    finally:
        font.close()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    paths = sys.argv[1:] or sorted((root / "src").glob("*.sfd"))
    for path in paths:
        check(path)
