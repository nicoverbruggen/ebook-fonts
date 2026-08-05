#!/usr/bin/env python3
"""Build CrossPoint Reader CPFONT v4 files from the relaxed fonts.

CrossPoint Reader does not read TrueType files. It loads pre-rasterized
`.cpfont` bundles from the SD card: one file per family per point size, with
all four styles packed into each file. This script drives the reader project's
own converter, pinned to a commit, over the relaxed builds in `out/relaxed`, so
the looser line spacing carries into the rasterized metrics.

Run `build.py` first; the relaxed builds are the input. For each collection
this writes:

  out/cpfont/<collection>/<family>/<family>_<size>.cpfont

That is the layout the device expects under `/.fonts` or `/fonts` on the SD
card. CrossPoint takes the family name it shows in its font picker from the
directory name, so the ` R` suffix that marks a relaxed build is dropped: these
are the only builds shipped for CrossPoint, and there is nothing on the device
to tell them apart from.
"""

from __future__ import annotations

import argparse
import shutil
import struct
import subprocess
import sys
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont

REPO_ROOT = Path(__file__).resolve().parent.parent

# The converter lives in the CrossPoint firmware repository and is pinned to a
# commit, the same way build.py pins kobofix. `cpfont_version.py` holds the
# format version the converter writes and must come from the same commit.
CONVERTER_COMMIT = "2ceeeccd5ae8f2693eef71388d3f0a4137c1fcc9"
CONVERTER_BASE_URL = (
    "https://raw.githubusercontent.com/crosspoint-reader/crosspoint-reader/"
    f"{CONVERTER_COMMIT}/lib/EpdFont/scripts"
)
CONVERTER_FILES = ("fontconvert_sdcard.py", "cpfont_version.py")

# The reading sizes CrossPoint offers by default. Sizes 8 and 10 are only
# needed for CJK fallback in the device UI, which none of these fonts cover.
DEFAULT_SIZES = "12,14,16,18"

# The converter's own preset for literary fiction: Latin, Greek, Cyrillic,
# math and symbol blocks, supplemental punctuation and CJK quote marks.
DEFAULT_INTERVALS = "reading"

# Subfamily name (from the font's name table) to the converter's style flag.
STYLE_FLAGS = {
    "Regular": "--regular",
    "Bold": "--bold",
    "Italic": "--italic",
    "Bold Italic": "--bolditalic",
}

RELAXED_SUFFIX = " R"

CPFONT_MAGIC = b"CPFONT\x00\x00"
CPFONT_VERSION = 4
CPFONT_FLAGS = 1  # 2-bit greyscale, the only mode the converter writes
CPFONT_HEADER_SIZE = 32


def download_converter(destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    for filename in CONVERTER_FILES:
        target = destination / filename
        if target.is_file():
            continue
        url = f"{CONVERTER_BASE_URL}/{filename}"
        print(f"Downloading pinned CrossPoint converter: {filename}")
        temporary = target.with_suffix(f"{target.suffix}.download")
        try:
            urllib.request.urlretrieve(url, temporary)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
    return destination / "fontconvert_sdcard.py"


def read_names(font_path: Path) -> tuple[str, str]:
    """Return (family, subfamily) from the font's name table."""
    name_table = TTFont(font_path, lazy=True)["name"]
    family = name_table.getDebugName(16) or name_table.getDebugName(1)
    subfamily = name_table.getDebugName(17) or name_table.getDebugName(2)
    if not family:
        raise RuntimeError(f"{font_path}: no family name in name table")
    if not subfamily:
        raise RuntimeError(f"{font_path}: no subfamily name in name table")
    return family, subfamily


def cpfont_name(family: str) -> str:
    """Drop the relaxed marker, so the picker shows `NV Charis`, not `NV Charis R`."""
    if not family.endswith(RELAXED_SUFFIX):
        raise RuntimeError(f"{family}: not a relaxed family; expected a '{RELAXED_SUFFIX}' suffix")
    return family[: -len(RELAXED_SUFFIX)]


def collect_families(relaxed_dir: Path) -> dict[str, dict[str, Path]]:
    """Map each family in a relaxed collection to its {subfamily: path} styles."""
    fonts = sorted(relaxed_dir.glob("*.ttf"))
    if not fonts:
        raise RuntimeError(f"No .ttf files found in {relaxed_dir}; run build.py first")

    families: dict[str, dict[str, Path]] = {}
    for font in fonts:
        family, subfamily = read_names(font)
        if subfamily not in STYLE_FLAGS:
            raise RuntimeError(f"{font}: unexpected subfamily {subfamily!r}")
        styles = families.setdefault(cpfont_name(family), {})
        if subfamily in styles:
            raise RuntimeError(f"{font}: duplicate {subfamily} for {family}")
        styles[subfamily] = font

    for name, styles in families.items():
        if "Regular" not in styles:
            raise RuntimeError(f"{name}: no Regular style; CrossPoint needs one to fall back on")

    return families


def validate_cpfont(path: Path, style_count: int) -> None:
    """Check the file really is a CPFONT v4 bundle holding the styles we passed."""
    with path.open("rb") as handle:
        header = handle.read(CPFONT_HEADER_SIZE)
    if len(header) != CPFONT_HEADER_SIZE:
        raise RuntimeError(f"{path} has a truncated CPFONT header")
    magic, version, flags, styles = struct.unpack("<8sHHB19x", header)
    if magic != CPFONT_MAGIC:
        raise RuntimeError(f"{path} has invalid CPFONT magic")
    if (version, flags, styles) != (CPFONT_VERSION, CPFONT_FLAGS, style_count):
        raise RuntimeError(
            f"{path} has unexpected header values: version={version}, "
            f"flags={flags}, styles={styles} (expected {CPFONT_VERSION}, "
            f"{CPFONT_FLAGS}, {style_count})"
        )


def build_family(
    converter: Path,
    name: str,
    styles: dict[str, Path],
    sizes: list[int],
    intervals: str,
    family_dir: Path,
) -> list[Path]:
    """Convert one family into a `.cpfont` per size, and validate each one."""
    command = [
        sys.executable,
        str(converter),
        "--intervals", intervals,
        "--sizes", ",".join(str(size) for size in sizes),
        "--name", name,
        "--output-dir", str(family_dir),
    ]
    for subfamily, flag in STYLE_FLAGS.items():
        if subfamily in styles:
            command += [flag, str(styles[subfamily])]

    # The converter reports every style it rasterizes on stderr, which is far
    # too much for a 44-family run; keep it for the failure case only.
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"{name}: the converter exited with code {result.returncode}")

    outputs = [family_dir / f"{name}_{size}.cpfont" for size in sizes]
    for output in outputs:
        validate_cpfont(output, len(styles))
    return outputs


def build_collection(
    converter: Path,
    collection: str,
    relaxed_dir: Path,
    out_dir: Path,
    sizes: list[int],
    intervals: str,
) -> int:
    families = collect_families(relaxed_dir)
    collection_dir = out_dir / collection
    # Start clean, so a family that was renamed or dropped since the last run
    # does not linger here and end up in the release zip.
    if collection_dir.exists():
        shutil.rmtree(collection_dir)

    total_bytes = 0
    for name in sorted(families):
        styles = families[name]
        family_dir = collection_dir / name
        outputs = build_family(converter, name, styles, sizes, intervals, family_dir)
        size_on_disk = sum(output.stat().st_size for output in outputs)
        total_bytes += size_on_disk
        print(
            f"  {name}: {len(outputs)} files, {len(styles)} styles, "
            f"{size_on_disk / 1024 / 1024:.1f} MB"
        )
    print(f"{collection}: {len(families)} families -> {collection_dir} ({total_bytes / 1024 / 1024:.1f} MB)")
    return len(families)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--relaxed-dir",
        default=Path("out/relaxed"),
        type=Path,
        help="Directory holding the relaxed builds per collection (default: ./out/relaxed).",
    )
    parser.add_argument(
        "--out-dir",
        default=Path("out/cpfont"),
        type=Path,
        help="Directory for the generated .cpfont files (default: ./out/cpfont).",
    )
    parser.add_argument(
        "--collections",
        default="core,extra",
        help="Comma-separated collections to build (default: core,extra).",
    )
    parser.add_argument(
        "--sizes",
        default=DEFAULT_SIZES,
        help=f"Comma-separated point sizes (default: {DEFAULT_SIZES}).",
    )
    parser.add_argument(
        "--intervals",
        default=DEFAULT_INTERVALS,
        help=f"CrossPoint interval preset(s) (default: {DEFAULT_INTERVALS}).",
    )
    parser.add_argument(
        "--converter-dir",
        type=Path,
        help="Directory holding the two converter scripts. If omitted, they are downloaded.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    relaxed_dir = (REPO_ROOT / args.relaxed_dir).resolve()
    out_dir = (REPO_ROOT / args.out_dir).resolve()
    sizes = [int(size.strip()) for size in args.sizes.split(",")]
    collections = [name.strip() for name in args.collections.split(",")]

    if args.converter_dir:
        converter_dir = args.converter_dir.resolve()
        converter = converter_dir / "fontconvert_sdcard.py"
        missing = [name for name in CONVERTER_FILES if not (converter_dir / name).is_file()]
        if missing:
            raise FileNotFoundError(f"{converter_dir}: missing {', '.join(missing)}")
    else:
        converter = download_converter(REPO_ROOT / "tmp" / "crosspoint-converter")

    for collection in collections:
        build_collection(
            converter,
            collection,
            relaxed_dir / collection,
            out_dir,
            sizes,
            args.intervals,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
