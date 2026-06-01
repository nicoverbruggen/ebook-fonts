#!/usr/bin/env python3
"""Download pinned Readerly, Cartisse, and Sourcerer releases into ./fonts/core."""

from __future__ import annotations

import json
import hashlib
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DESTINATION = REPO_ROOT / "fonts" / "core"
LOCKFILE = REPO_ROOT / "fonts.lock"
PINNED_RELEASES = {
    "Readerly": "https://github.com/nicoverbruggen/readerly/releases/download/v1.7/Readerly.zip",
    "Cartisse": "https://github.com/nicoverbruggen/cartisse/releases/download/v2.2/Cartisse.zip",
    "Sourcerer": "https://github.com/nicoverbruggen/sourcerer/releases/download/v1.2/Sourcerer.zip",
}


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_lock() -> dict:
    return json.loads(LOCKFILE.read_text())


def verify_locked_core_fonts() -> None:
    lock = load_lock()
    missing = []
    mismatched = []

    for release in lock["releases"]:
        for font in release["files"]:
            path = DESTINATION / font["name"]
            if not path.is_file():
                missing.append(str(path.relative_to(REPO_ROOT)))
            elif hash_file(path) != font["sha256"]:
                mismatched.append(str(path.relative_to(REPO_ROOT)))

    if missing or mismatched:
        details = []
        if missing:
            details.append(f"missing: {', '.join(missing)}")
        if mismatched:
            details.append(f"hash mismatch: {', '.join(mismatched)}")
        raise RuntimeError(f"Core font lock verification failed ({'; '.join(details)})")


def extract_fonts(archive_path: Path, family: str) -> list[Path]:
    extracted = {}

    with zipfile.ZipFile(archive_path) as archive:
        for item in archive.infolist():
            filename = Path(item.filename).name
            if item.is_dir() or Path(filename).suffix.lower() != ".ttf":
                continue

            target = DESTINATION / filename
            with archive.open(item) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            extracted[filename] = target

    if not extracted:
        raise RuntimeError(f"No .ttf files found in {archive_path}")

    for old_font in DESTINATION.glob(f"{family}*.ttf"):
        if old_font.name not in extracted:
            old_font.unlink()

    return sorted(extracted.values())


def download_core_fonts() -> None:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    lock = {"destination": "fonts/core", "releases": []}

    with tempfile.TemporaryDirectory(prefix="core-fonts-") as temp_dir:
        temp_path = Path(temp_dir)
        for family, url in PINNED_RELEASES.items():
            archive_path = temp_path / f"{family}.zip"
            print(f"Downloading {family} from {url}")
            urllib.request.urlretrieve(url, archive_path)

            extracted = extract_fonts(archive_path, family)
            lock["releases"].append(
                {
                    "family": family,
                    "url": url,
                    "files": [{"name": font.name, "sha256": hash_file(font)} for font in extracted],
                }
            )

            for font in extracted:
                print(f"  {font.relative_to(REPO_ROOT)}")

    LOCKFILE.write_text(json.dumps(lock, indent=2) + "\n")


def main() -> int:
    download_core_fonts()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
