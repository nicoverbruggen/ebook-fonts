# Working in this repository

## What this is

A curated collection of libre-licensed fonts, tweaked for reading on e-readers (primarily Kobo). The fonts under `fonts/` are the sources, split into two collections: `core` (the recommended picks) and `extra` (everything else).

`build.py` stamps those sources with the project's copyright notice and runs them through `kobofix` to produce the `KF_*` variants, which are patched for the Kobo `kepub` renderer. It also builds a relaxed variant of every family (`<name> R`, e.g. `NV Charis R` or `Cartisse R`), rebuilt with looser line spacing. Each tagged release ships six zips (Kobo, stamped-source and relaxed builds of each collection) plus a `manifest.json` describing them.

Most fonts are renamed (usually `NV_`-prefixed) so they install alongside the originals without clashing. **README.md is the reference** for the collection itself: what each font is, where it came from, how it was altered, licensing, and installation. Read it before changing anything font-facing; this file only covers how to work on the repository.

## Use the container, never the host

Anything that touches a font file (`fontTools`, `build.py`, `tools/*.py`) runs inside the prebuilt `fntbld-oci` container. The host has no `fontTools` and is not expected to. Prefer Podman; Docker works too.

```sh
podman run --rm -v "$PWD:/work" -w /work ghcr.io/nicoverbruggen/fntbld-oci:latest <command>
```

`./local_build.sh` wraps this for a full build. See BUILD.md for details, including refreshing fonts pinned in `tools/download_fonts.py`.

## Tags are the identity; VERSION is a label

Two separate concepts, easy to conflate:

- **The git tag** (date-based, e.g. `v2026.07.02`) is what everything actually resolves against: manifest raw-file URLs, release asset URLs, the release the assets attach to. Anything that has to *locate a file* uses the tag.
- **`VERSION`** at the repo root (e.g. `4.1`) is user-facing only. It titles the release (`v4.1`, where the `v` is added by the workflow rather than stored in the file). It must never appear in a URL or a path.

## Releases

Both forges release on tag push, and the two workflows are deliberate mirrors of each other, so change one and change the other:

- `.github/workflows/release.yml` → github.com
- `.gitea/workflows/release.yml` → git.nicoverbruggen.be

Rules that hold on both:

- **Publishing is automatic** (`draft: false`). Pushing a tag ships it to the world with no manual gate, so the tree must be right *before* tagging.
- **A tag reachable from `main` is a stable release; a tag anywhere else (e.g. `trunk`) is a pre-release.** Decided by `git merge-base --is-ancestor <tag> origin/main`. This needs `fetch-depth: 0` on checkout and `git` in the build image; without either, the check cannot work.
- **Fail rather than guess.** If the branch check can't resolve `origin/main`, or `VERSION` is empty, the release fails. A mislabelled release is worse than a failed run.

## The manifest

`tools/generate_manifest.py` emits `manifest.json` as a release asset, listing every font by collection with URLs pinned to the tag. Only meaningful for tagged releases.

- `--host` selects the forge. The forges differ in more than the hostname: the repo has a different owner on each, and Gitea serves raw files from `/raw/tag/<tag>/` where GitHub uses `/raw/refs/tags/<tag>/`. Release assets happen to share the same `/releases/download/` shape.
- **Family names come from the font's name table, never the filename.** `NV_SourceSerif-*.ttf` is the family "NV Source Serif"; splitting the filename gets this wrong.
- **`FAMILY_ORDER` is the source of truth for ordering**, and mirrors the order the README presents fonts in. It is intentionally guarded in both directions: the build fails if a font on disk is missing from it, or if it lists a family that no longer ships. Do not defeat these guards: they are what keeps a new or dropped font from silently landing in the wrong place.
- `ARCHIVES` duplicates the zip names from the workflow's "Create zip files" step. CI passes `--archive-dir /tmp`, which asserts every zip the manifest links to actually exists, so renaming the zips on one side only fails the release instead of publishing dead URLs. Keep passing it.

`FAMILY_ORDER` travels with the commit, so in CI it always matches the tag being built. Generating a manifest for an *older* tag is therefore a one-off: check out that tag's tree and use its own README order, because trunk's `FAMILY_ORDER` describes trunk, and running it against an older tree will (correctly) trip the guards.

## Check the Reserved Font Name before naming a font

**Do this for every font you add. It is the trap this repository is most likely to fall into.**

The `NV <original name>` convention works because most upstreams declare no Reserved Font Name. That is not universal, and where an RFN exists the convention is not merely discouraged, it is not permitted: OFL clause 3 bars a Modified Version from using a Reserved Font Name in its primary font name, and a prefix does not cure it. The `nv` preset changes line spacing, so anything built here is unambiguously a Modified Version.

Known cases in this collection: Merriweather reserves `Merriweather` (shipped as NV Halcyon), PT Serif reserves `PT Serif`, `PT Sans` and `ParaType` (NV Publica, NV Publica Wide), Adobe reserves `Source`, IBM reserves `Plex` (NV Tabula), and Lora reserves `Lora` (NV Sable).

Check both the font and its upstream `OFL.txt`, because they disagree: PT Serif declares its RFN only in `OFL.txt` and says nothing in `nameID 0`, so checking the binary alone would have missed it.

```sh
podman run --rm -v "$PWD:/w:ro" -w /w ghcr.io/nicoverbruggen/fntbld-oci:latest python3 -c "
from fontTools.ttLib import TTFont
n = TTFont('path/to/Source-Regular.ttf', lazy=True)['name']
print(n.getDebugName(0))
print('RFN:', 'Reserved Font Name' in (n.getDebugName(0) or ''))
"
```

If an RFN exists, the font needs a genuinely different name; ask rather than inventing one. Avoid near-misses too: SIL's guidance says not to reuse almost all the same letters in the same order, or to sound like the original, so shaving a letter off the reserved word does not count as complying.

Only the *primary* name records must be free of the reserved name: family, full name, PostScript name, unique ID and typographic family. The `copyright` and `trademark` records **must keep** the original notice, RFN declaration and all. NV Castoro and NV Zilla Slab both retain their upstreams' trademark lines, and that is correct.

One accepted exception: **Sourcerer** contains Adobe's reserved `Source`. That is a deliberate call by the repo owner on the grounds that Sourcerer is a word in its own right. Do not "fix" it, and do not use it as precedent for a new font.

## The README is a source of truth, and it drifts

`FAMILY_ORDER` is authored from the README's order, but the README has been wrong before: missing fonts that ship, and listing fonts that don't. Treat what is on disk as the authority on *membership*, the README as the authority on *order*, and fix the README when they disagree.
