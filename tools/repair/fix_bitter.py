#!/usr/bin/env python3
"""Repair two upstream GSUB bugs in the checked-in NV Bitter fonts.

The Bitter italic styles omit many substitutions from their ``smcp`` feature.
Their upright counterparts contain the intended mappings, so copy every mapping
whose input and output glyphs exist in the target italic font.

All four styles also run the ``calt`` lookup before ``liga``.  In sequences such
as ``fi``, ``calt`` changes ``f`` to ``f.alt`` before the ligature lookup can
match it.  Swap the two top-level lookups and remap all references to them so
``liga`` runs first without changing which lookup belongs to which feature.

Run this script with fontTools inside fntbld-oci, as required by AGENTS.md:

    podman run --rm -v "$PWD:/work" -w /work \
      ghcr.io/nicoverbruggen/fntbld-oci:latest \
      python3 tools/repair/fix_bitter.py

Pass ``--check`` to verify the checked-in fonts without modifying them.
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

from fontTools.ttLib import TTFont


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FONT_DIR = REPO_ROOT / "fonts" / "core"
STYLES = ("Regular", "Italic", "Bold", "BoldItalic")
ITALIC_DONORS = {
    "Italic": "Regular",
    "BoldItalic": "Bold",
}


def feature_lookup_indices(font: TTFont, tag: str) -> list[int]:
    gsub = font["GSUB"].table
    indices = [
        index
        for record in gsub.FeatureList.FeatureRecord
        if record.FeatureTag == tag
        for index in record.Feature.LookupListIndex
    ]
    if not indices:
        raise ValueError(f"{font.reader.file.name}: missing {tag!r} feature")
    return indices


def single_substitution_mapping(font: TTFont, tag: str) -> dict[str, str]:
    gsub = font["GSUB"].table
    lookups = [
        gsub.LookupList.Lookup[index]
        for index in feature_lookup_indices(font, tag)
        if gsub.LookupList.Lookup[index].LookupType == 1
    ]
    if len(lookups) != 1 or len(lookups[0].SubTable) != 1:
        raise ValueError(
            f"{font.reader.file.name}: expected one single-substitution lookup "
            f"with one subtable in {tag!r}"
        )
    return lookups[0].SubTable[0].mapping


def expected_italic_smcp_mapping(donor: TTFont, target: TTFont) -> tuple[dict[str, str], set[str]]:
    donor_mapping = single_substitution_mapping(donor, "smcp")
    target_glyphs = set(target.getGlyphOrder())
    expected = {
        source: replacement
        for source, replacement in donor_mapping.items()
        if source in target_glyphs and replacement in target_glyphs
    }
    skipped = {
        glyph
        for source, replacement in donor_mapping.items()
        for glyph in (source, replacement)
        if glyph not in target_glyphs
    }
    return expected, skipped


def repair_italic_smcp(donor: TTFont, target: TTFont, *, check: bool) -> tuple[bool, set[str]]:
    mapping = single_substitution_mapping(target, "smcp")
    expected, skipped = expected_italic_smcp_mapping(donor, target)

    unexpected = set(mapping) - set(expected)
    divergent = {
        source
        for source in set(mapping) & set(expected)
        if mapping[source] != expected[source]
    }
    if unexpected or divergent:
        raise ValueError(
            f"{target.reader.file.name}: italic smcp table is not a compatible "
            f"subset of its upright counterpart (unexpected={sorted(unexpected)}, "
            f"divergent={sorted(divergent)})"
        )

    if mapping == expected:
        return False, skipped
    if check:
        return True, skipped

    mapping.clear()
    mapping.update(copy.deepcopy(expected))
    return True, skipped


def remap_lookup_references(root: object, remapping: dict[int, int]) -> None:
    """Recursively update GSUB lookup indices after reordering the lookup list."""
    seen: set[int] = set()

    def visit(value: object) -> None:
        if value is None or isinstance(value, (str, bytes, int, float, bool)):
            return
        value_id = id(value)
        if value_id in seen:
            return
        seen.add(value_id)

        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        if isinstance(value, dict):
            for item in value.values():
                visit(item)
            return

        if hasattr(value, "LookupListIndex"):
            indices = value.LookupListIndex
            if isinstance(indices, list):
                value.LookupListIndex = [remapping.get(index, index) for index in indices]
            elif isinstance(indices, int):
                value.LookupListIndex = remapping.get(indices, indices)

        for child in vars(value).values():
            visit(child)

    visit(root)


def prioritize_liga(font: TTFont, *, check: bool) -> bool:
    calt_indices = feature_lookup_indices(font, "calt")
    liga_indices = feature_lookup_indices(font, "liga")
    if len(calt_indices) != 1 or len(liga_indices) != 1:
        raise ValueError(
            f"{font.reader.file.name}: expected one lookup each for calt and liga "
            f"(calt={calt_indices}, liga={liga_indices})"
        )

    calt_index, liga_index = calt_indices[0], liga_indices[0]
    if liga_index < calt_index:
        return False
    if check:
        return True

    gsub = font["GSUB"].table
    lookups = gsub.LookupList.Lookup
    lookups[calt_index], lookups[liga_index] = lookups[liga_index], lookups[calt_index]
    remap_lookup_references(gsub, {calt_index: liga_index, liga_index: calt_index})
    return True


def font_paths(font_dir: Path) -> dict[str, Path]:
    paths = {style: font_dir / f"NV_Bitter-{style}.ttf" for style in STYLES}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing NV Bitter fonts: {', '.join(missing)}")
    return paths


def repair_family(font_dir: Path, *, check: bool) -> int:
    paths = font_paths(font_dir)
    fonts = {style: TTFont(path) for style, path in paths.items()}
    changed = {style: False for style in STYLES}

    for target_style, donor_style in ITALIC_DONORS.items():
        needs_repair, skipped = repair_italic_smcp(
            fonts[donor_style],
            fonts[target_style],
            check=check,
        )
        changed[target_style] |= needs_repair
        if skipped:
            print(
                f"{paths[target_style].name}: skipped smcp mappings for absent "
                f"glyphs: {', '.join(sorted(skipped))}"
            )

    for style, font in fonts.items():
        changed[style] |= prioritize_liga(font, check=check)

    if check:
        failures = [paths[style].name for style, needs_repair in changed.items() if needs_repair]
        if failures:
            print(f"NV Bitter repairs required: {', '.join(failures)}")
            return 1
        print("NV Bitter GSUB repairs verified.")
        return 0

    for style, font in fonts.items():
        if changed[style]:
            font.save(paths[style])
            print(f"Repaired {paths[style].relative_to(REPO_ROOT)}")
        else:
            print(f"Already repaired {paths[style].relative_to(REPO_ROOT)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--font-dir",
        type=Path,
        default=DEFAULT_FONT_DIR,
        help="Directory containing the four NV_Bitter-*.ttf files",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the repairs without modifying any font files",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return repair_family(args.font_dir.resolve(), check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
