#!/usr/bin/env python3
"""Download fonts from external repositories into fonts/core and fonts/extra."""

from __future__ import annotations

import re
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

CORE_DEST = REPO_ROOT / "fonts" / "core"
EXTRA_DEST = REPO_ROOT / "fonts" / "extra"

CORE_RELEASES = {
    "Libron": "https://github.com/nicoverbruggen/libron/releases/download/v0.23/Libron.zip",
    "Cartisse": "https://github.com/nicoverbruggen/cartisse/releases/download/v2.4/Cartisse.zip",
    "Sourcerer": "https://github.com/nicoverbruggen/sourcerer/releases/download/v1.4/Sourcerer.zip",
}
EXTRA_RELEASES = {
    "Readerly": "https://github.com/nicoverbruggen/readerly/releases/download/v1.11/Readerly.zip",
}
VERSION_RE = re.compile(r"\d+(?:\.\d+)+")


def version_from_release_url(url: str) -> str:
    match = re.search(r"/download/v([^/]+)/", url)
    if not match:
        raise ValueError(f"Could not find release tag in URL: {url}")
    return match.group(1)


try:
    from fontTools.ttLib import TTFont
    HAVE_FONTOOLS = True
except ImportError:
    HAVE_FONTOOLS = False


def get_name(font, name_id: int) -> str:
    name_table = font["name"]
    record = name_table.getName(name_id, 3, 1, 0x409) or name_table.getName(name_id, 1, 0, 0)
    return record.toUnicode().strip() if record else ""


def font_version(path: Path) -> str:
    font = TTFont(path)
    version_string = get_name(font, 5)
    match = VERSION_RE.search(version_string)
    if not match:
        raise ValueError(f"{path.relative_to(REPO_ROOT)}: could not find version in name ID 5: {version_string!r}")
    return match.group(0)


def verify_font_versions(releases: dict, destination: Path, label: str) -> int:
    if not HAVE_FONTOOLS:
        print(f"Skipping version verification for {label} fonts (fontTools not available)")
        return 0

    errors = []
    checked = 0

    for family, url in releases.items():
        expected_version = version_from_release_url(url)
        fonts = sorted(destination.glob(f"{family}*.ttf"))

        if not fonts:
            errors.append(f"{family}: no .ttf files found in {destination.relative_to(REPO_ROOT)}")
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
        raise RuntimeError(f"{label} font version verification failed ({'; '.join(errors)})")

    print(f"Verified {label} font versions for {checked} fonts.")
    return checked


def verify_core_font_versions() -> None:
    verify_font_versions(CORE_RELEASES, CORE_DEST, "core")


def extract_fonts(archive_path: Path, family: str, destination: Path) -> list[Path]:
    extracted = {}

    with zipfile.ZipFile(archive_path) as archive:
        for item in archive.infolist():
            filename = Path(item.filename).name
            if item.is_dir() or Path(filename).suffix.lower() != ".ttf":
                continue

            target = destination / filename
            with archive.open(item) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            extracted[filename] = target

    if not extracted:
        raise RuntimeError(f"No .ttf files found in {archive_path}")

    for old_font in destination.glob(f"{family}*.ttf"):
        if old_font.name not in extracted:
            old_font.unlink()

    return sorted(extracted.values())


def download_collection(releases: dict, destination: Path, label: str) -> None:
    destination.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"{label}-fonts-") as temp_dir:
        temp_path = Path(temp_dir)
        for family, url in releases.items():
            archive_path = temp_path / f"{family}.zip"
            print(f"Downloading {family} from {url}")
            urllib.request.urlretrieve(url, archive_path)

            extracted = extract_fonts(archive_path, family, destination)

            for font in extracted:
                print(f"  {font.relative_to(REPO_ROOT)}")


def download_fonts() -> None:
    download_collection(CORE_RELEASES, CORE_DEST, "core")
    download_collection(EXTRA_RELEASES, EXTRA_DEST, "extra")
    verify_core_font_versions()


def main() -> int:
    download_fonts()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
