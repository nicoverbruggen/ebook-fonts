#!/usr/bin/env sh
set -eu

IMAGE="${EBOOK_FONTS_CONTAINER_IMAGE:-ghcr.io/nicoverbruggen/fntbld-oci:latest}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(dirname "$SCRIPT_DIR")

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
  echo "Docker or Podman is required to generate the example images." >&2
  exit 1
fi

echo "Generating example images with $RUNTIME container: $IMAGE"

# Text shaping needs uharfbuzz, which the fntbld-oci image doesn't ship yet,
# so install it into the throwaway container on every run for now.
exec "$RUNTIME" run --rm \
  -v "$REPO_ROOT:/work" \
  -w /work \
  "$IMAGE" \
  sh -c 'pip install --quiet uharfbuzz >/dev/null 2>&1 && python3 tools/generate_examples.py "$@"' sh "$@"
