#!/usr/bin/env python3
"""Snap `i`/`j` stem tops to x-height in Charis TTFs.

Problem
-------
Charis's `i` and `j` stems peak a handful of font units above the declared
x-height — a deliberate optical overshoot that prevents their flat tops from
looking shorter than neighbouring round letters like `e`/`o`. On desktop
renderers this overshoot lands within the same pixel row as the x-height
line and disappears. On Kobo's e-ink renderer, the extra few units push
the stem across a pixel-rounding boundary: `i`'s top rounds *up* to an
extra pixel row while `e`/`v` round *down*, so `i` ends up visibly one
pixel taller than its neighbours. Hinting (native or autohint) does not
fix this because the overshoot is baked into the outline, not the hints.

What this script does
---------------------
For each target glyph it finds the stem contour (the one that reaches
the baseline), computes the overshoot `delta = stem_max_y − OS/2.sxHeight`,
and rigidly translates every stem point above `sxHeight` down by that
delta. The top shape (serif brackets, flare) is preserved rather than
compressed. Any additional contours on the glyph — i.e. the tittle on
`i`/`j` — are translated down by the same delta so the dot-to-stem
spacing designed by SIL is preserved.

Glyphs targeted: `i`, `j`, and the dotless bases `dotlessi`/`uni0237`.
Accented variants (`iacute`, `idieresis`, ...) are composites that
reference the dotless base, so they inherit the fix for free.

Why a script, not a one-off edit
--------------------------------
This modification is kept as a script (rather than hand-edited font files
checked into the repo) so that it can be re-applied to future upstream
releases of Charis without redoing the work manually. When SIL publishes
a new Charis version, the workflow is:
  1. Drop the upstream .ttf files into an input directory.
  2. Run this script against them.
  3. Ship the output.
The fix is derived from each font's own `OS/2.sxHeight`, so it adapts
automatically if SIL adjusts x-height or overshoot in a future release.

Usage
-----
    python snap_ij_xheight.py <input-dir> <output-dir>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

# Flat-topped stems at x-height. Accented variants (iacute, idieresis, ...)
# are composites that reference dotlessi/uni0237, so modifying those bases
# propagates the fix automatically — no need to list every accented form.
STEM_GLYPHS = ["i", "j", "dotlessi", "idotless", "uni0237", "dotlessj"]


def flatten_stem_top(glyph, x_height: int) -> bool:
    """Rigidly translate every stem point above `x_height` down so the
    stem's top sits exactly at `x_height`, and translate the tittle
    (if present) down by the same delta so its spacing to the stem is
    preserved.

    The overshoot region moves as one block, preserving the shape of the
    top (serif brackets, flare) rather than compressing it.

    Returns True if the glyph was modified.
    """
    if glyph.numberOfContours <= 0:
        return False

    coords = glyph.coordinates
    end_pts = glyph.endPtsOfContours

    contours: list[list[int]] = []
    start = 0
    for end in end_pts:
        contours.append(list(range(start, end + 1)))
        start = end + 1

    # The stem is the contour containing the lowest point of the glyph
    # (reaches to baseline / descender). Any other contours are tittles
    # / dots sitting above it.
    stem_idx = min(
        range(len(contours)),
        key=lambda i: min(coords[p][1] for p in contours[i]),
    )
    stem = contours[stem_idx]

    stem_max_y = max(coords[p][1] for p in stem)
    if stem_max_y <= x_height:
        return False  # no overshoot

    delta = stem_max_y - x_height
    modified = False

    for p in stem:
        x, y = coords[p]
        if y > x_height:
            coords[p] = (x, y - delta)
            modified = True

    for i, contour in enumerate(contours):
        if i == stem_idx:
            continue
        for p in contour:
            x, y = coords[p]
            coords[p] = (x, y - delta)
            modified = True

    return modified


def process_font(src: Path, dst: Path) -> int:
    font = TTFont(src)
    x_height = font["OS/2"].sxHeight
    if not x_height:
        raise RuntimeError(f"{src.name}: OS/2.sxHeight is 0 or missing; cannot flatten")

    glyf = font["glyf"]
    modified = 0
    for name in STEM_GLYPHS:
        if name not in glyf:
            continue
        if flatten_stem_top(glyf[name], x_height):
            modified += 1
    font.save(dst)
    return modified


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input_dir", type=Path, help="Directory containing Charis .ttf files")
    parser.add_argument("output_dir", type=Path, help="Where to write modified fonts")
    args = parser.parse_args()

    ttfs = sorted(args.input_dir.glob("*.ttf"))
    if not ttfs:
        print(f"No .ttf files found in {args.input_dir}", file=sys.stderr)
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for src in ttfs:
        dst = args.output_dir / src.name
        n = process_font(src, dst)
        print(f"{src.name}: flattened {n} stem(s) -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
