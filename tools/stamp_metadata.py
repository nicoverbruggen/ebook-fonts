#!/usr/bin/env python3
"""Stamp .ttf files with an ebook-fonts release marker.

For each font given on the command line, this script modifies (in place):

  - Name ID 0 (Copyright): appends a modification notice preserving the
    original copyright above it, as required by the OFL.
  - Name ID 5 (Version string): appends `; ebook-fonts <YYYY-MM-DD>`.
  - Name ID 3 (Unique identifier): appends the same suffix so the
    modified font has a unique ID distinct from the upstream release.

Idempotent: running twice on the same file is a no-op — detected via the
`ebook-fonts` marker in the copyright string.

Usage:
    python stamp_metadata.py <font.ttf> [<font.ttf> ...]
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

MOD_MARKER = "ebook-fonts"
REPO_URL = "https://github.com/nicoverbruggen/ebook-fonts"
COPYRIGHT_NOTICE = (
    f"Some modifications for e-readers applied by Nico Verbruggen ({REPO_URL}). "
    "Released under an identical license as the original."
)


def is_already_stamped(font: TTFont) -> bool:
    for rec in font["name"].names:
        if rec.nameID == 0 and MOD_MARKER in rec.toUnicode():
            return True
    return False


def stamp(path: Path) -> bool:
    font = TTFont(path)
    if is_already_stamped(font):
        return False

    today = datetime.date.today().isoformat()
    suffix = f"; {MOD_MARKER} {today}"
    name_table = font["name"]

    # Iterate over a copy because setName may mutate the underlying list.
    for rec in list(name_table.names):
        current = rec.toUnicode()
        if rec.nameID == 0:
            new = current.rstrip() + "\n\n" + COPYRIGHT_NOTICE
        elif rec.nameID in (3, 5):
            new = current + suffix
        else:
            continue
        name_table.setName(new, rec.nameID, rec.platformID, rec.platEncID, rec.langID)

    font.save(path)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("fonts", nargs="+", type=Path, help="TTF files to stamp")
    args = parser.parse_args()

    stamped = skipped = 0
    for path in args.fonts:
        if not path.is_file():
            print(f"skip (not a file): {path}", file=sys.stderr)
            continue
        if stamp(path):
            print(f"stamped: {path}")
            stamped += 1
        else:
            print(f"already stamped, skipped: {path}")
            skipped += 1

    print(f"\n{stamped} stamped, {skipped} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
