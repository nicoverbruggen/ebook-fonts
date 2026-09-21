#!/usr/bin/env python3
"""Rebuild the collection's synthetic bold styles from the NV text styles.

Run inside fntbld-oci. FreeType expands unhinted outlines by the configured
strength in both directions. Advancing glyphs gain the same horizontal
advance; empty glyphs and zero-width marks keep their advances.
"""

from __future__ import annotations

import argparse
from array import array
from ctypes import byref
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import freetype
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables.ttProgram import Program

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from build import download_kobofix

FAMILIES = {
    "Appleton": {"BoldItalic": 0.025},
    "Cardo": {"BoldItalic": 0.020},
    "Publica Wide": {"Bold": 0.020, "BoldItalic": 0.020},
    "Radley": {"Bold": 0.030, "BoldItalic": 0.030},
}
STYLE_SOURCES = {"Bold": "Regular", "BoldItalic": "Italic"}


def embolden(source: Path, destination: Path, strength_em: float) -> None:
    """Bake FreeType's synthetic weight into static TrueType outlines."""
    face = freetype.Face(str(source))
    with TTFont(source) as font:
        strength = round(font["head"].unitsPerEm * strength_em)
        for glyph_id, name in enumerate(font.getGlyphOrder()):
            face.load_glyph(
                glyph_id,
                freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_NO_BITMAP,
            )
            outline = face.glyph.outline
            if not outline.n_points:
                continue
            if any(tag & 2 for tag in outline.tags):
                raise ValueError(f"{source}: {name} contains cubic curves; expected TrueType outlines")
            error = freetype.FT_Outline_EmboldenXY(byref(outline._FT_Outline), strength, strength)
            if error:
                raise RuntimeError(f"{source}: FreeType error {error} while emboldening {name}")

            # FreeType resolves composites before emboldening, so accents and
            # their bases are thickened once, without changing component offsets.
            glyph = Glyph()
            glyph.numberOfContours = outline.n_contours
            glyph.coordinates = GlyphCoordinates(outline.points)
            glyph.endPtsOfContours = list(outline.contours)
            glyph.flags = array("B", [tag & 1 for tag in outline.tags])
            glyph.program = Program()
            glyph.program.fromBytecode([])
            font["glyf"][name] = glyph
            glyph.recalcBounds(font["glyf"])
            advance, _ = font["hmtx"][name]
            font["hmtx"][name] = (advance + strength if advance else 0, glyph.xMin)

        # Expansion can make neighbouring contours overlap. Remove those
        # overlaps and discard hints that describe the original outlines.
        removeOverlaps(font, removeHinting=True, ignoreErrors=False)
        for tag in ("fpgm", "prep", "cvt ", "DSIG"):
            if tag in font:
                del font[tag]
        glyphs = font["glyf"].glyphs.values()
        os2 = font["OS/2"]
        # Set the bold weight even when the PANOSE family is unspecified.
        # The pinned kobofix skips PANOSE correction for that family.
        os2.panose.bWeight = 8
        os2.usWinAscent = max(os2.usWinAscent, max(getattr(g, "yMax", 0) for g in glyphs))
        os2.usWinDescent = max(os2.usWinDescent, -min(getattr(g, "yMin", 0) for g in glyphs))
        for attribute, character in (("sxHeight", "x"), ("sCapHeight", "H")):
            setattr(os2, attribute, font["glyf"][font.getBestCmap()[ord(character)]].yMax)
        font.save(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, default=REPO_ROOT / "fonts" / "extra")
    parser.add_argument("--family", choices=FAMILIES, help="Rebuild only this family.")
    args = parser.parse_args()
    font_dir = args.font_dir.resolve()
    families = [args.family] if args.family else list(FAMILIES)
    for family in families:
        basename = family.replace(" ", "_")
        for style in FAMILIES[family]:
            source = font_dir / f"NV_{basename}-{STYLE_SOURCES[style]}.ttf"
            if not source.is_file():
                raise FileNotFoundError(source)

    with tempfile.TemporaryDirectory(prefix="synthetic-bold-") as temporary:
        work = Path(temporary)
        kobofix = work / "kobofix.py"
        download_kobofix(kobofix)
        for family in families:
            basename = family.replace(" ", "_")
            styles = FAMILIES[family]
            for style, strength in styles.items():
                source = font_dir / f"NV_{basename}-{STYLE_SOURCES[style]}.ttf"
                embolden(source, work / f"{basename}-{style}.ttf", strength)
            subprocess.run(
                [sys.executable, str(kobofix), "--preset", "nv", "--name", family,
                 *[f"{basename}-{style}.ttf" for style in styles]],
                cwd=work,
                check=True,
            )
        for family in families:
            basename = family.replace(" ", "_")
            for style in FAMILIES[family]:
                filename = f"NV_{basename}-{style}.ttf"
                shutil.copy2(work / filename, font_dir / filename)
                print(f"Built {font_dir / filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
