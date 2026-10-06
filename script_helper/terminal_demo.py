#!/usr/bin/env python3
"""Print a terminal font specimen. No dependencies; uses the terminal's active font."""

import argparse
import math
import shutil
import sys


def artwork(columns, rows):
    # A six-lobed rosette sampled onto a Unicode Braille raster.
    bits = ((1, 8), (2, 16), (4, 32), (64, 128))
    width, height = columns * 2, rows * 4
    for cy in range(rows):
        line = []
        for cx in range(columns):
            mask = 0
            for dy in range(4):
                for dx in range(2):
                    x = (cx * 2 + dx + 0.5 - width / 2) / (width / 2)
                    y = (cy * 4 + dy + 0.5 - height / 2) / (height / 2)
                    radius = math.hypot(x, y)
                    angle = math.atan2(y, x)
                    ribbon = 0.58 + 0.19 * math.cos(6 * angle + radius * 4)
                    if abs(radius - ribbon) < 0.095:
                        mask |= bits[dy][dx]
            line.append(chr(0x2800 + mask))
        yield "".join(line)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=48, help="art width in terminal columns (16–100)")
    parser.add_argument("--all", action="store_true", help="also print all 256 Braille patterns")
    parser.add_argument("--plain", action="store_true", help="omit ANSI bold/italic style samples")
    args = parser.parse_args()
    if not 16 <= args.width <= 100:
        parser.error("--width must be between 16 and 100")
    width = min(args.width, max(16, shutil.get_terminal_size((80, 24)).columns - 2))
    print("Monofoki terminal graphics")
    print("Select the rebuilt font in your terminal, then rerun.")
    print("Dots should stay evenly spaced across text rows.\n")
    print("\n".join(artwork(width, max(8, round(width / 2.14)))))
    print("\nSeam check: this should be one continuous dot grid.")
    for _ in range(6):
        print("⣿" * min(width, 32))
    print("\nBox drawing and solid blocks: look for broken joins.")
    print("┌────────┬────────┐  ████████████")
    print("│        │        │  ████████████")
    print("├────────┼────────┤  ████████████")
    print("│        │        │  ▄▄▄▄▄▄▄▄▄▄▄▄")
    print("└────────┴────────┘  ▀▀▀▀▀▀▀▀▀▀▀▀")
    print("\nArrows: ⇦ ⇧ ⇨ ⇩ ⇯   Shades: ░▒▓█")
    print("Dot order 1–8: ⠁ ⠂ ⠄ ⠈ ⠐ ⠠ ⡀ ⢀")
    print("Blank Braille has one-cell width: |⠀| | |")
    if sys.stdout.isatty() and not args.plain:
        print("\nStyle grid: regular / bold / italic / bold italic")
        for sgr in ("0", "1", "3", "1;3"):
            print(f"\033[{sgr}⣿⣿⣿⣿⣿⣿⣿⣿  ⇨ ⇩ ⇯\033[0m")
    if args.all:
        print("\nAll 256 Braille patterns (16 per row):")
        for start in range(0x2800, 0x2900, 16):
            print(f"{start:04X}  " + "".join(chr(cp) for cp in range(start, start + 16)))


if __name__ == "__main__":
    main()
