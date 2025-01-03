# Modified fonts for e-reading

This is a selection of fonts that I've tweaked for reading purposes on Kobo devices. 

**If you found these useful, please consider starring the repository!**

Included in the repository right now are my tweaked 'NV' fonts, but [the older release](https://github.com/nicoverbruggen/ebook-fonts/releases/tag/v2024.03) may still be of interest as I've included my initial batch of tweaked fonts mentioned in [the blog post](https://nicoverbruggen.be/blog/patching-fonts-for-kobo) there.

## Included tweaked fonts

### NV Garamond

![](./examples/NV-Garamond.png)

 **NV Garamond** is an EB Garamond version that contains a bunch of tweaks, mostly related to glyph sizes. This one has a [dedicated repository](https://github.com/nicoverbruggen/nv-garamond) that I've linked. OFL licensed.

### NV Jost

![](./examples/NV-Jost.png)

**NV Jost** is a Jost variant, with a slightly altered lowercase G and single storey a (similar to Futura, only accessible via OT feature on the original font). This one has a [dedicated repository](https://github.com/nicoverbruggen/nv-jost) that I've linked, OFL licensed.

### NV Cardo

![](./examples/NV-Cardo.png)

**NV Cardo** is a version of Cardo with 20% spacing and has been renamed so you can keep the original Cardo installed side-by-side as well. Does not have a separate repository because no other changes were applied. OFL licensed.

### Where can I get the fonts?

The fonts are available via the [release](https://github.com/nicoverbruggen/ebook-fonts/releases).

You can learn more about how and why I originally made these tweaked fonts on my blog: [Patching Fonts for my Kobo](https://nicoverbruggen.be/blog/patching-fonts-for-kobo). I explain there why and how.

## How to install

To install these fonts on your Kobo, unzip the files and drag the font files into the `fonts` directory at the root of your Kobo device after connecting your Kobo to your PC via USB cable. You may need to create the `fonts` directory.

**I recommend rebooting your Kobo after installing the fonts to make sure they work correctly. A reboot is REQUIRED if you already had other versions of these fonts installed on your device, or the new versions won't be used.**

To reboot, long-press the power button until your Kobo says it has been shut down. Then, press the power button again and wait for your device to restart.

## FAQ

### What tweaks have been applied to these fonts?

- I've set a 20% line height (using `font-line percent 20`). Some fonts rendered poorly on Kobo devices with the line height slider all the way to the left. This fixes that!
- Most of the fonts have been renamed (using [fontname.py](https://github.com/chrissimpkins/fontname.py)). This way, you can keep them installed side-by-side with the original versions, if you'd like.
- Panose information has been corrected where necessary (using [panosifier](https://github.com/source-foundry/panosifier)). This ensures that the fonts render correctly on Kobo devices.

### How are these fonts licensed?

* Most of these fonts are available under their original [Open Font License](https://openfontlicense.org/).
* _XCharter_ is available under the original Bitstream license, which is included in the respective archive.

### What is your favorite font from the collection?

* For simple books and basic readability, I personally prefer XCharter or NV Jost.
* For fantasy books, I prefer to use NV Garamond or NV Cardo.