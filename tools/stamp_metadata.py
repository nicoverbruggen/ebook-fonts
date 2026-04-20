#!/usr/bin/env python3
"""Stamp .ttf files with an ebook-fonts release marker.

For each font given on the command line, this script modifies (in place)
Name ID 0 (Copyright): the original copyright is preserved verbatim, and
a short modification notice dated to today is appended beneath it, as
required by the OFL.

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


def build_copyright_notice(date_iso: str) -> str:
    return (
        f"Some modifications for e-readers applied on {date_iso} by "
        f"Nico Verbruggen for `ebook-fonts` ({REPO_URL})."
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
    notice = build_copyright_notice(today)
    name_table = font["name"]

    # Iterate over a copy because setName may mutate the underlying list.
    for rec in list(name_table.names):
        if rec.nameID != 0:
            continue
        new = rec.toUnicode().rstrip() + "\n\n" + notice
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
