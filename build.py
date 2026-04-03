#!/usr/bin/env python3
"""Build Kobo-fixed (KF) fonts locally into ./out."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

KOBOFIX_URL = "https://raw.githubusercontent.com/nicoverbruggen/kobo-font-fix/main/kobofix.py"


def download_kobofix(target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(KOBOFIX_URL, target_path)


def process_collection(kobofix_path: Path, source_dir: Path, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    for old_file in output_dir.glob("*.ttf"):
        old_file.unlink()

    source_fonts = sorted(source_dir.glob("*.ttf"))
    if not source_fonts:
        raise RuntimeError(f"No .ttf files found in {source_dir}")

    with tempfile.TemporaryDirectory(prefix="kobofix-") as temp_dir:
        temp_path = Path(temp_dir)
        for font in source_fonts:
            shutil.copy2(font, temp_path / font.name)

        cmd = [sys.executable, str(kobofix_path), "--preset", "kf"] + [font.name for font in source_fonts]
        subprocess.run(cmd, cwd=temp_path, check=True)

        generated_fonts = sorted(temp_path.glob("KF_*.ttf"))
        if not generated_fonts:
            raise RuntimeError(f"kobofix did not generate any KF_*.ttf files for {source_dir}")

        for generated_font in generated_fonts:
            shutil.move(str(generated_font), output_dir / generated_font.name)

        return len(generated_fonts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build KF fonts from ./fonts into ./out.")
    parser.add_argument(
        "--out-dir",
        default="out",
        type=Path,
        help="Directory where generated KF fonts are written (default: ./out).",
    )
    parser.add_argument(
        "--kobofix",
        type=Path,
        help="Path to a local kobofix.py. If omitted, it will be downloaded automatically.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent
    out_dir = (repo_root / args.out_dir).resolve()

    with tempfile.TemporaryDirectory(prefix="kobofix-script-") as temp_dir:
        temp_path = Path(temp_dir)
        kobofix_path = (args.kobofix.resolve() if args.kobofix else temp_path / "kobofix.py")

        if args.kobofix:
            if not kobofix_path.is_file():
                raise FileNotFoundError(f"kobofix.py not found: {kobofix_path}")
        else:
            print(f"Downloading kobofix.py from {KOBOFIX_URL}")
            download_kobofix(kobofix_path)

        core_count = process_collection(kobofix_path, repo_root / "fonts/core", out_dir / "core")
        extra_count = process_collection(kobofix_path, repo_root / "fonts/extra", out_dir / "extra")

    print(f"Generated {core_count} KF fonts in {out_dir / 'core'}")
    print(f"Generated {extra_count} KF fonts in {out_dir / 'extra'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
