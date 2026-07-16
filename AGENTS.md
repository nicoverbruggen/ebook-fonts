# Working in this repository

## What this is

A curated collection of libre-licensed fonts, tweaked for reading on e-readers (primarily Kobo). The fonts under `fonts/` are the sources, split into two collections: `core` (the recommended picks) and `extra` (everything else).

`build.py` stamps those sources with the project's copyright notice and runs them through `kobofix` to produce the `KF_*` variants, which are patched for the Kobo `kepub` renderer. Each tagged release ships four zips (Kobo and stamped-source builds of each collection) plus a `manifest.json` describing them.

Most fonts are renamed (usually `NV_`-prefixed) so they install alongside the originals without clashing. **README.md is the reference** for the collection itself — what each font is, where it came from, how it was altered, licensing, and installation. Read it before changing anything font-facing; this file only covers how to work on the repository.

## Use the container, never the host

Anything that touches a font file — `fontTools`, `build.py`, `tools/*.py` — runs inside the prebuilt `fntbld-oci` container. The host has no `fontTools` and is not expected to. Prefer Podman; Docker works too.

```sh
podman run --rm -v "$PWD:/work" -w /work ghcr.io/nicoverbruggen/fntbld-oci:latest <command>
```

`./local_build.sh` wraps this for a full build. See BUILD.md for details, including refreshing fonts pinned in `tools/download_fonts.py`.

## Tags are the identity; VERSION is a label

Two separate concepts, easy to conflate:

- **The git tag** (date-based, e.g. `v2026.07.02`) is what everything actually resolves against: manifest raw-file URLs, release asset URLs, the release the assets attach to. Anything that has to *locate a file* uses the tag.
- **`VERSION`** at the repo root (e.g. `4.1`) is user-facing only. It titles the release (`v4.1` — the `v` is added by the workflow, not stored in the file). It must never appear in a URL or a path.

## Releases

Both forges release on tag push, and the two workflows are deliberate mirrors of each other — change one, change the other:

- `.github/workflows/release.yml` → github.com
- `.gitea/workflows/release.yml` → git.nicoverbruggen.be

Rules that hold on both:

- **Publishing is automatic** (`draft: false`). Pushing a tag ships it to the world with no manual gate, so the tree must be right *before* tagging.
- **A tag reachable from `main` is a stable release; a tag anywhere else (e.g. `trunk`) is a pre-release.** Decided by `git merge-base --is-ancestor <tag> origin/main`. This needs `fetch-depth: 0` on checkout and `git` in the build image — without either, the check cannot work.
- **Fail rather than guess.** If the branch check can't resolve `origin/main`, or `VERSION` is empty, the release fails. A mislabelled release is worse than a failed run.

## The manifest

`tools/generate_manifest.py` emits `manifest.json` as a release asset, listing every font by collection with URLs pinned to the tag. Only meaningful for tagged releases.

- `--host` selects the forge. The forges differ in more than the hostname: the repo has a different owner on each, and Gitea serves raw files from `/raw/tag/<tag>/` where GitHub uses `/raw/refs/tags/<tag>/`. Release assets happen to share the same `/releases/download/` shape.
- **Family names come from the font's name table, never the filename.** `NV_SourceSerif-*.ttf` is the family "NV Source Serif"; splitting the filename gets this wrong.
- **`FAMILY_ORDER` is the source of truth for ordering**, and mirrors the order the README presents fonts in. It is intentionally guarded in both directions: the build fails if a font on disk is missing from it, or if it lists a family that no longer ships. Do not defeat these guards — they are what keeps a new or dropped font from silently landing in the wrong place.
- `ARCHIVES` duplicates the zip names from the workflow's "Create zip files" step. CI passes `--archive-dir /tmp`, which asserts every zip the manifest links to actually exists, so renaming the zips on one side only fails the release instead of publishing dead URLs. Keep passing it.

`FAMILY_ORDER` travels with the commit, so in CI it always matches the tag being built. Generating a manifest for an *older* tag is therefore a one-off: check out that tag's tree and use its own README order — trunk's `FAMILY_ORDER` describes trunk, and running it against an older tree will (correctly) trip the guards.

## The README is a source of truth, and it drifts

`FAMILY_ORDER` is authored from the README's order, but the README has been wrong before: missing fonts that ship, and listing fonts that don't. Treat what is on disk as the authority on *membership*, the README as the authority on *order*, and fix the README when they disagree.
