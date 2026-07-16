#!/usr/bin/env python3
"""Generate manifest.json listing every font in ./fonts, by collection.

The manifest points at the .ttf files as committed to this repository at a
given tag, so consumers can download individual fonts straight from the forge
without unpacking a release zip. It is only meaningful for tagged releases:
the URLs are pinned to the tag.

The forge is selected with --host, since each one serves raw files from a
different path and hosts the repository under a different owner. The release
workflow for each forge passes its own host.

Families are listed in the curated order below, which mirrors the order the
README presents them in. FAMILY_ORDER is the source of truth for that order
and must stay in sync with what is on disk: generating the manifest fails if a
font under ./fonts is not listed, or if a listed family has no fonts, so a
newly added font cannot silently land in an arbitrary position.

Family names are read from each font's name table (preferring the typographic
family, nameID 16, over the legacy family, nameID 1) rather than derived from
the filename.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont

REPO_ROOT = Path(__file__).resolve().parent.parent

# URL templates per forge, for individual font files ("raw") and for the
# release zips ("asset"). The forges differ in more than the hostname: the
# repository lives under a different owner on each, and Gitea serves tagged
# raw files from /raw/tag/<tag>/ where GitHub uses /raw/refs/tags/<tag>/.
# Release assets happen to share the same /releases/download/ shape.
HOST_URLS = {
    "github.com": {
        "raw": "https://github.com/nicoverbruggen/ebook-fonts/raw/refs/tags/{tag}/{path}",
        "asset": "https://github.com/nicoverbruggen/ebook-fonts/releases/download/{tag}/{name}",
    },
    "git.nicoverbruggen.be": {
        "raw": "https://git.nicoverbruggen.be/fonts/ebook-fonts/raw/tag/{tag}/{path}",
        "asset": "https://git.nicoverbruggen.be/fonts/ebook-fonts/releases/download/{tag}/{name}",
    },
}

# The zips the release workflow builds for each collection, as {key: filename}.
# `kobo` holds the KF_*.ttf fonts patched for the kepub renderer; `other` holds
# the stamped sources. These names are also written in the "Create zip files"
# workflow step; pass --archive-dir so a mismatch fails the build instead of
# publishing URLs that 404.
ARCHIVES = {
    "kobo": "kobo-{collection}-fonts.zip",
    "other": "other-{collection}-fonts.zip",
}

FAMILY_ORDER: dict[str, list[str]] = {
    "core": [
        "Libron",
        "Sourcerer",
        "Cartisse",
        "NV Charis",
        "NV Garamond",
        "NV Jost",
        "NV Bitter",
        "NV Legible Next",
        "NV Palatium",
    ],
    "extra": [
        "Readerly",
        "NV Adelph",
        "NV Alegreya",
        "NV Alizar",
        "NV Ancizar Serif",
        "NV Ancizar Sans",
        "NV Andada",
        "NV Basker",
        "NV Cardo",
        "NV Castoro",
        "NV Charis Literacy",
        "NV Charis Old Style",
        "NV Clara",
        "NV Cooper",
        "NV Disleksio",
        "NV Elstob",
        "NV Erewhon",
        "NV Gentium",
        "NV Georsio",
        "NV Halcyon",
        "NV Junius",
        "NV Kierkegaard",
        "NV Libertinus",
        "NV Literata",
        "NV Lore",
        "NV Membo",
        "NV Newsreader",
        "NV NinePoint",
        "NV Plex Serif",
        "NV Publica",
        "NV Publica Wide",
        "NV Scarlet",
        "NV Source Serif",
        "NV Technical",
        "NV Zilla Slab",
    ],
}

# Fonts ship as a four-style family; list them in the order a reader expects
# rather than alphabetically. Anything unrecognised sorts last, by name.
STYLE_ORDER = {"Regular": 0, "Italic": 1, "Bold": 2, "Bold Italic": 3}


def read_names(font_path: Path) -> tuple[str, str]:
    """Return (family, subfamily) from the font's name table."""
    name_table = TTFont(font_path, lazy=True)["name"]
    family = name_table.getDebugName(16) or name_table.getDebugName(1)
    subfamily = name_table.getDebugName(17) or name_table.getDebugName(2)
    if not family:
        raise RuntimeError(f"{font_path}: no family name in name table")
    return family, subfamily or ""


def collect_families(collection: str, url_template: str, tag: str) -> dict[str, list[str]]:
    """Map each family in a collection to its file URLs, in style order."""
    source_dir = REPO_ROOT / "fonts" / collection
    fonts = sorted(source_dir.glob("*.ttf"))
    if not fonts:
        raise RuntimeError(f"No .ttf files found in {source_dir}")

    styles: dict[str, list[tuple[int, str, str]]] = {}
    for font in fonts:
        family, subfamily = read_names(font)
        url = url_template.format(tag=tag, path=font.relative_to(REPO_ROOT).as_posix())
        styles.setdefault(family, []).append((STYLE_ORDER.get(subfamily, len(STYLE_ORDER)), subfamily, url))

    return {family: [url for _, _, url in sorted(entries)] for family, entries in styles.items()}


def archive_filenames(collection: str) -> dict[str, str]:
    """Map each release zip key for a collection to its filename."""
    return {key: template.format(collection=collection) for key, template in ARCHIVES.items()}


def collect_archives(collection: str, asset_template: str, tag: str) -> dict[str, str]:
    """Map each release zip for a collection to its download URL."""
    return {
        key: asset_template.format(tag=tag, name=filename)
        for key, filename in archive_filenames(collection).items()
    }


def build_manifest(host: str, tag: str, archive_dir: Path | None = None) -> dict:
    urls = HOST_URLS[host]
    collections = []
    missing_archives = []
    for collection, order in FAMILY_ORDER.items():
        families = collect_families(collection, urls["raw"], tag)

        if archive_dir is not None:
            missing_archives += [
                name for name in archive_filenames(collection).values()
                if not (archive_dir / name).is_file()
            ]

        unlisted = sorted(set(families) - set(order))
        if unlisted:
            raise RuntimeError(
                f"fonts/{collection}: {', '.join(unlisted)} not in FAMILY_ORDER; "
                f"add to tools/generate_manifest.py in the intended position"
            )
        missing = [family for family in order if family not in families]
        if missing:
            raise RuntimeError(
                f"fonts/{collection}: FAMILY_ORDER lists {', '.join(missing)} but no such fonts exist"
            )

        collections.append(
            {
                "name": collection,
                "archives": collect_archives(collection, urls["asset"], tag),
                "fonts": [{"family": family, "files": families[family]} for family in order],
            }
        )

    if missing_archives:
        raise RuntimeError(
            f"{archive_dir}: no such zip(s): {', '.join(missing_archives)}; "
            f"ARCHIVES in tools/generate_manifest.py disagrees with the zips the "
            f"release workflow builds, so the manifest would link to files that do not exist"
        )

    return {"collections": collections}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tag", required=True, help="Tag the URLs should be pinned to, e.g. v2026.07.02.")
    parser.add_argument("--host", required=True, choices=sorted(HOST_URLS), help="Forge the URLs should point at.")
    parser.add_argument("--out", default="manifest.json", type=Path, help="Where to write the manifest (default: ./manifest.json).")
    parser.add_argument(
        "--archive-dir",
        type=Path,
        help="Directory holding the built release zips. If given, every archive the manifest "
        "links to must exist there, so a rename cannot silently produce dead URLs. The release "
        "workflow passes the directory it zips into.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build_manifest(args.host, args.tag, args.archive_dir)
    args.out.write_text(json.dumps(manifest, indent=4) + "\n")
    for collection in manifest["collections"]:
        total = sum(len(entry["files"]) for entry in collection["fonts"])
        print(f"{collection['name']}: {len(collection['fonts'])} families, {total} files")
    print(f"-> {args.out} @ {args.tag} ({args.host})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
