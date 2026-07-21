## Building `ebook-fonts` variants

When you download the assets from GitHub, Kobo variant assets have likely been built. 

Running these or creating these assets requires running `kobofix.py` and applying specific patches included in this repository.

### Building release outputs locally

To build the release outputs yourself, you can simply run:

```sh
./local_build.sh
```

The build script will use Podman or Docker to run the build in the `fntbld-oci` container, and writes the generated font collections to the ignored `out/` directory in the repository root.

### Regenerating the README example images

The images under `examples/core/` and `examples/extra/` are rendered from the fonts in `./fonts` by `tools/generate_examples.py`. To regenerate all of them, run:

```sh
./tools/generate_examples.sh
```

This uses the same container as the build. Pass `--only "NV Charis"` to re-render a single family. The images are rendered without font hinting, matching how Kobo renders the KF builds. The script needs `uharfbuzz` for text shaping, which the wrapper installs into the throwaway container on each run until `fntbld-oci` ships it.

### Running scripts with a container

If you would like to run these locally, you can do so, but it's highly recommended that you use the prebuilt `fntbld-oci` container instead:

```sh
podman run --rm -v "$PWD:/work" -w /work ghcr.io/nicoverbruggen/fntbld-oci:latest <command>
```

### Sourcing files from other repositories

Some fonts, like Libron, Cartisse, Sourcerer and Readerly, while included, are sourced from separate repositories. 

The versions included in this repository are pinned to a specific font file in `tools/download_fonts.py`, which needs to be updated when new releases are available.

You don't need to manually download these new releases once the pinned URLs have been updated. To refresh the downloaded fonts, simply run:

```sh
podman run --rm -v "$PWD:/work" -w /work ghcr.io/nicoverbruggen/fntbld-oci:latest python3 tools/download_fonts.py
```