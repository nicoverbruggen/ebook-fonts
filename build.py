#!/usr/bin/env python3
"""Build release artifacts into ./out.

For each collection (core, extra) this produces two sibling directories:

  out/sources/<collection>/ — the NV/Cartisse/Readerly/Sourcerer fonts,
                              all stamped with the ebook-fonts copyright
                              notice. This is what gets zipped as
                              `other-<collection>-fonts.zip` on release.
  out/kobo/<collection>/    — the KF_*.ttf outputs produced by running
                              kobofix on the stamped sources above.
                              This is what gets zipped as
                              `kobo-<collection>-fonts.zip` on release.

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
from tools.download_core_fonts import verify_core_font_versions

KOBOFIX_URL = "https://raw.githubusercontent.com/nicoverbruggen/kobo-font-fix/v0.6/kobofix.py"
REPO_ROOT = Path(__file__).resolve().parent
STAMP_SCRIPT = REPO_ROOT / "tools" / "stamp_metadata.py"
LOCAL_KOBOFIX = REPO_ROOT / "tools" / "kobofix.py"


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


def build_collection(kobofix_path: Path, name: str, out_dir: Path) -> tuple[int, int]:
    source_dir = REPO_ROOT / "fonts" / name
    staged_dir = out_dir / "sources" / name
    kf_out_dir = out_dir / "kobo" / name

    staged = copy_sources(source_dir, staged_dir)
    stamp_all(staged_dir)
    kf_count = run_kobofix(kobofix_path, staged_dir, kf_out_dir)
    return len(staged), kf_count


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

        core_src, core_kf = build_collection(kobofix_path, "core", out_dir)
        extra_src, extra_kf = build_collection(kobofix_path, "extra", out_dir)

    print(f"core: {core_src} stamped sources -> {out_dir/'sources/core'}, {core_kf} KF -> {out_dir/'kobo/core'}")
    print(f"extra: {extra_src} stamped sources -> {out_dir/'sources/extra'}, {extra_kf} KF -> {out_dir/'kobo/extra'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
