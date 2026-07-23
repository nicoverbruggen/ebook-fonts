#!/usr/bin/env python3
"""Build release artifacts into ./out.

For each collection (core, extra) this produces three sibling directories:

  out/sources/<collection>/ — the NV/Cartisse/Libron/Sourcerer fonts,
                              all stamped with the ebook-fonts copyright
                              notice. This is what gets zipped as
                              `other-<collection>-fonts.zip` on release.
  out/kobo/<collection>/    — the KF_*.ttf outputs produced by running
                              kobofix on the stamped sources above.
                              This is what gets zipped as
                              `kobo-<collection>-fonts.zip` on release.
  out/relaxed/<collection>/ — the `<name> R` variants: every family, rebuilt
                              with looser line spacing for a more relaxed
                              reading rhythm. NV families keep their prefix
                              (`NV Charis` -> `NV Charis R`); the rest gain an
                              ` R` suffix (`Cartisse` -> `Cartisse R`). This is
                              what gets zipped as `relaxed-<collection>-fonts.zip`
                              on release.

The files under ./fonts are never modified by this script.
Core font versions are verified before building.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from tools.download_fonts import verify_core_font_versions

KOBOFIX_URL = "https://raw.githubusercontent.com/nicoverbruggen/kobo-font-fix/v0.10/kobofix.py"
REPO_ROOT = Path(__file__).resolve().parent
STAMP_SCRIPT = REPO_ROOT / "tools" / "stamp_metadata.py"
LOCAL_KOBOFIX = REPO_ROOT / "tools" / "kobofix.py"

# The stamped NV sources already ship at 20% line spacing (the `nv` preset).
# The relaxed variant loosens that to give a less tight reading rhythm; it is
# the total line height as a percentage above 1em, the same figure kobofix and
# font-line use. Bump this to make the relaxed collection looser or tighter.
RELAXED_LINE_PERCENT = 50

# NV families are renamed through kobofix's prefix mechanism so the `NV_`
# filename and PostScript convention is preserved; every other family is
# renamed in place with just the ` R` suffix and no prefix.
NV_FILENAME_PREFIX = "NV_"


def download_kobofix(target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(KOBOFIX_URL, target_path)


def copy_sources(source_dir: Path, dest_dir: Path) -> list[Path]:
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True)
    copied = []
    for font in sorted(source_dir.glob("*.ttf")):
        out = dest_dir / font.name
        shutil.copy2(font, out)
        copied.append(out)
    return copied


def stamp_all(staged_dir: Path) -> None:
    """Stamp every *.ttf in `staged_dir` with the ebook-fonts copyright notice."""
    fonts = sorted(staged_dir.glob("*.ttf"))
    if not fonts:
        return
    cmd = [sys.executable, str(STAMP_SCRIPT)] + [str(f) for f in fonts]
    subprocess.run(cmd, check=True)


def run_kobofix(kobofix_path: Path, staged_dir: Path, kf_out_dir: Path) -> int:
    if kf_out_dir.exists():
        shutil.rmtree(kf_out_dir)
    kf_out_dir.mkdir(parents=True)

    fonts = sorted(staged_dir.glob("*.ttf"))
    if not fonts:
        raise RuntimeError(f"No .ttf files found in {staged_dir}")

    with tempfile.TemporaryDirectory(prefix="kobofix-") as temp_dir:
        temp_path = Path(temp_dir)
        for font in fonts:
            shutil.copy2(font, temp_path / font.name)

        cmd = [sys.executable, str(kobofix_path), "--preset", "kf", "--stamp"] + [f.name for f in fonts]
        subprocess.run(cmd, cwd=temp_path, check=True)

        generated = sorted(temp_path.glob("KF_*.ttf"))
        if not generated:
            raise RuntimeError(f"kobofix did not generate any KF_*.ttf files for {staged_dir}")

        for font in generated:
            shutil.move(str(font), kf_out_dir / font.name)

        return len(generated)


def relaxed_target(font_path: Path) -> tuple[str, str]:
    """Return (kobofix prefix, base name) for a font's relaxed variant.

    NV families keep the `NV` prefix so kobofix preserves the `NV_` filename and
    PostScript convention: `NV_Legible_Next-Bold.ttf` -> ("NV", "Legible Next"),
    which becomes the `NV Legible Next R` family. Every other family is renamed
    in place with no prefix: `Cartisse-Regular.ttf` -> ("", "Cartisse"),
    yielding `Cartisse R`.
    """
    family_part = font_path.stem.rsplit("-", 1)[0]
    if family_part.startswith(NV_FILENAME_PREFIX):
        return "NV", family_part[len(NV_FILENAME_PREFIX):].replace("_", " ")
    return "", family_part.replace("_", " ")


def sync_typo_to_hhea(font_path: Path) -> bool:
    """Make the OS/2 typographic metrics agree with hhea, saving if changed.

    font-line relaxes the hhea and usWin metrics but leaves the typographic
    metrics untouched for the few fonts whose source typo metrics differ from
    hhea (NV Newsreader, NV NinePoint). Those fonts set USE_TYPO_METRICS, so
    typo-respecting readers such as KOReader would otherwise ignore the relaxed
    spacing. Copying hhea into typo is exactly what font-line already does for
    every other font, so all three metric tables end up agreeing on the relaxed
    line height. A no-op (and no re-save) wherever they already match.
    """
    from fontTools.ttLib import TTFont

    font = TTFont(font_path)
    os2, hhea = font["OS/2"], font["hhea"]
    if (os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap) == (hhea.ascent, hhea.descent, hhea.lineGap):
        return False
    os2.sTypoAscender = hhea.ascent
    os2.sTypoDescender = hhea.descent
    os2.sTypoLineGap = hhea.lineGap
    font.save(font_path)
    return True


def build_relaxed(kobofix_path: Path, staged_dir: Path, relaxed_dir: Path) -> int:
    """Produce `<name> R` variants with looser line spacing for every family.

    Runs kobofix once per family over the stamped sources, appending an ` R`
    suffix and loosening line spacing to RELAXED_LINE_PERCENT. Kerning and
    outlines are left untouched: the only intended difference from the standard
    font is the line spacing. The typographic metrics are then synced to hhea so
    typo-respecting readers (e.g. KOReader) also see the relaxed spacing.
    """
    if relaxed_dir.exists():
        shutil.rmtree(relaxed_dir)
    relaxed_dir.mkdir(parents=True)

    groups: dict[tuple[str, str], list[Path]] = {}
    for font in sorted(staged_dir.glob("*.ttf")):
        groups.setdefault(relaxed_target(font), []).append(font)

    if not groups:
        return 0

    generated = 0
    for (prefix, base), fonts in groups.items():
        with tempfile.TemporaryDirectory(prefix="relaxed-") as temp_dir:
            temp_path = Path(temp_dir)
            input_names = set()
            for font in fonts:
                shutil.copy2(font, temp_path / font.name)
                input_names.add(font.name)

            cmd = [
                sys.executable, str(kobofix_path),
                "--prefix", prefix,
                "--name", f"{base} R",
                "--line-percent", str(RELAXED_LINE_PERCENT),
                "--kern", "skip",
                "--outline", "skip",
            ] + [f.name for f in fonts]
            subprocess.run(cmd, cwd=temp_path, check=True)

            outputs = [p for p in sorted(temp_path.glob("*.ttf")) if p.name not in input_names]
            if not outputs:
                raise RuntimeError(f"kobofix produced no relaxed output for {base}")
            for out in outputs:
                dest = relaxed_dir / out.name
                shutil.move(str(out), dest)
                sync_typo_to_hhea(dest)
                generated += 1

    return generated


def build_collection(kobofix_path: Path, name: str, out_dir: Path) -> tuple[int, int, int]:
    source_dir = REPO_ROOT / "fonts" / name
    staged_dir = out_dir / "sources" / name
    kf_out_dir = out_dir / "kobo" / name
    relaxed_dir = out_dir / "relaxed" / name

    staged = copy_sources(source_dir, staged_dir)
    stamp_all(staged_dir)
    kf_count = run_kobofix(kobofix_path, staged_dir, kf_out_dir)
    relaxed_count = build_relaxed(kobofix_path, staged_dir, relaxed_dir)
    return len(staged), kf_count, relaxed_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--out-dir",
        default="out",
        type=Path,
        help="Directory for release artifacts (default: ./out).",
    )
    parser.add_argument(
        "--kobofix",
        type=Path,
        help="Path to a local kobofix.py. If omitted, it will be downloaded automatically.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = (REPO_ROOT / args.out_dir).resolve()

    if out_dir.exists():
        shutil.rmtree(out_dir)

    verify_core_font_versions()

    with tempfile.TemporaryDirectory(prefix="kobofix-script-") as temp_dir:
        temp_path = Path(temp_dir)
        if args.kobofix:
            kobofix_path = args.kobofix.resolve()
            if not kobofix_path.is_file():
                raise FileNotFoundError(f"kobofix.py not found: {kobofix_path}")
        elif LOCAL_KOBOFIX.exists():
            kobofix_path = LOCAL_KOBOFIX.resolve()
            print(f"Using local kobofix.py at {kobofix_path}")
        else:
            kobofix_path = temp_path / "kobofix.py"
            print(f"Downloading kobofix.py from {KOBOFIX_URL}")
            download_kobofix(kobofix_path)

        core_src, core_kf, core_relaxed = build_collection(kobofix_path, "core", out_dir)
        extra_src, extra_kf, extra_relaxed = build_collection(kobofix_path, "extra", out_dir)

    print(
        f"core: {core_src} stamped sources -> {out_dir/'sources/core'}, "
        f"{core_kf} KF -> {out_dir/'kobo/core'}, "
        f"{core_relaxed} relaxed -> {out_dir/'relaxed/core'}"
    )
    print(
        f"extra: {extra_src} stamped sources -> {out_dir/'sources/extra'}, "
        f"{extra_kf} KF -> {out_dir/'kobo/extra'}, "
        f"{extra_relaxed} relaxed -> {out_dir/'relaxed/extra'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
