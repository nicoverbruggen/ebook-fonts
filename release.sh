#!/usr/bin/env bash
# Stamp TTFs with the ebook-fonts release marker (copyright, version, unique
# ID). Idempotent — safe to run twice.
#
# Usage:
#   ./release.sh path/to/*.ttf
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/tools/stamp_metadata.py" "$@"
