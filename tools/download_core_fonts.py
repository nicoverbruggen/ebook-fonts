#!/usr/bin/env python3
"""Download Readerly, Cartisse, and Sourcerer releases into ./fonts/core."""

from __future__ import annotations

import re
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DESTINATION = REPO_ROOT / "fonts" / "core"
PINNED_RELEASES = {
    "Readerly": "https://github.com/nicoverbruggen/readerly/releases/download/v1.7/Readerly.zip",
    "Cartisse": "https://github.com/nicoverbruggen/cartisse/releases/download/v2.2/Cartisse.zip",
    "Sourcerer": "https://github.com/nicoverbruggen/sourcerer/releases/download/v1.2/Sourcerer.zip",
}
VERSION_RE = re.compile(r"\d+(?:\.\d+)+")


def version_from_release_url(url: str) -> str:
    match = re.search(r"/download/v([^/]+)/", url)
    if not match:
        raise ValueError(f"Could not find release tag in URL: {url}")
    return match.group(1)


def get_name(font, name_id: int) -> str:
    name_table = font["name"]
    record = name_table.getName(name_id, 3, 1, 0x409) or name_table.getName(name_id, 1, 0, 0)
    return record.toUnicode().strip() if record else ""


def font_version(path: Path) -> str:
    from fontTools.ttLib import TTFont

    font = TTFont(path)
    version_string = get_name(font, 5)
    match = VERSION_RE.search(version_string)
    if not match:
        raise ValueError(f"{path.relative_to(REPO_ROOT)}: could not find version in name ID 5: {version_string!r}")
    return match.group(0)


def verify_core_font_versions() -> None:
    errors = []
    checked = 0

    for family, url in PINNED_RELEASES.items():
        expected_version = version_from_release_url(url)
        fonts = sorted(DESTINATION.glob(f"{family}*.ttf"))

        if not fonts:
            errors.append(f"{family}: no .ttf files found in {DESTINATION.relative_to(REPO_ROOT)}")
            continue

        for path in fonts:
            try:
                reported_version = font_version(path)
            except Exception as error:
                errors.append(str(error))
                continue

            checked += 1
            if reported_version != expected_version:
                errors.append(
                    f"{path.relative_to(REPO_ROOT)}: release tag v{expected_version} "
                    f"does not match font version {reported_version}"
                )

    if errors:
        raise RuntimeError(f"Core font version verification failed ({'; '.join(errors)})")

    print(f"Verified core font versions for {checked} fonts.")


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

    with tempfile.TemporaryDirectory(prefix="core-fonts-") as temp_dir:
        temp_path = Path(temp_dir)
        for family, url in PINNED_RELEASES.items():
            archive_path = temp_path / f"{family}.zip"
            print(f"Downloading {family} from {url}")
            urllib.request.urlretrieve(url, archive_path)

            extracted = extract_fonts(archive_path, family)

            for font in extracted:
                print(f"  {font.relative_to(REPO_ROOT)}")

    verify_core_font_versions()


def main() -> int:
    download_core_fonts()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
