#!/usr/bin/env sh
set -eu

IMAGE="${EBOOK_FONTS_CONTAINER_IMAGE:-ghcr.io/nicoverbruggen/fntbld-oci:latest}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if [ -n "${CONTAINER_RUNTIME:-}" ]; then
  if ! command -v "$CONTAINER_RUNTIME" >/dev/null 2>&1; then
    echo "Requested container runtime not found: $CONTAINER_RUNTIME" >&2
    exit 1
  fi
  RUNTIME="$CONTAINER_RUNTIME"
elif command -v podman >/dev/null 2>&1; then
  RUNTIME="podman"
elif command -v docker >/dev/null 2>&1; then
  RUNTIME="docker"
else
  echo "Docker or Podman is required to build the fonts." >&2
  exit 1
fi

echo "Building fonts with $RUNTIME container: $IMAGE"

exec "$RUNTIME" run --rm \
  -v "$SCRIPT_DIR:/work" \
  -w /work \
  "$IMAGE" \
  python3 build.py "$@"
