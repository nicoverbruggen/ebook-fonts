# Modified fonts for e-reading

This is a selection of fonts that I've tweaked for reading purposes on Kobo devices.

> [!IMPORTANT]
> **If you found these fonts useful, please consider starring the repository**, it helps me understand how useful my work has been.

## What is this?

This is a repository that includes various fonts that have been altered in some minor way for better compatibility with e-readers.

For some fonts, font family names have been altered, sometimes glyphs have been altered, sometimes metrics have been altered, all in the interest of consistence and readability.

The main use of these fonts is for usage on an e-reader. I've only selected and altered fonts that I have the rights to alter because of their license (e.g. free/libre license or equivalent).

These alterations were made for my own personal use, but I figure these fonts may be of use to others, so I make them available here. While font names have been changed and this is allowed due to the licensing of each of the source fonts, I have not modified any copyright messages included in the font files and included attribution to the original authors in the document below.

## Included fonts

### NV Bitter

<kbd><img src="./examples/NV-Bitter.png" width='400px'/></kbd>

 **NV Bitter** is a version of [Bitter](https://github.com/solmatas/BitterPro) that has been renamed so it works correctly on Kobo devices.

You can also find the original version of Bitter [on Google Web Fonts](https://fonts.google.com/specimen/Bitter/about). Bitter was designed by [Sol Matas](http://www.solmatas.com/), and available under the [OFL license](https://openfontlicense.org/).

**Note:** _This font is included by default on newer Kobo devices. On older Kobo devices, like the Kobo Libra 2, it is not available without installing this version. Because this font has a different name, you can install it and it will co-exist alongside the included system font on newer devices._

---

_TODO: reorganize and update all descriptions below_

---

### NV Garamond

<kbd><img src="./examples/NV-Garamond.png" width='400px'/></kbd>

 **NV Garamond** is an EB Garamond version that contains a bunch of tweaks, mostly related to glyph sizes. This one has a [dedicated repository](https://github.com/nicoverbruggen/nv-garamond) that I've linked. OFL licensed.

### NV Jost

<kbd><img src="./examples/NV-Jost.png" width='400px'/></kbd>

**NV Jost** is a Jost variant, with a slightly altered lowercase G and single storey a (similar to Futura, only accessible via OT feature on the original font). This one has a [dedicated repository](https://github.com/nicoverbruggen/nv-jost) that I've linked, OFL licensed.

### NV Junius

<kbd><img src="./examples/NV-Junius.png" width='400px'/></kbd>

**NV Junius** is a [Junicode 2](https://github.com/psb1558/Junicode-font) variant based on the variable font, with adjusted metrics and a 10% glyph size increase. This one does not have a repository, but can be easily recreated by using [Slice](https://github.com/source-foundry/Slice), a GUI that allows you to export various fixed configurations.

### NV Bitter

<kbd><img src="./examples/NV-Bitter.png" width='400px'/></kbd>

**NV Bitter** is a renamed version of [Bitter](https://www.huertatipografica.com/en/fonts/bitter-ht) (that can co-exist with Bitter if necessary). Intended for older Kobo devices that do not include an on-board version. Bitter is included by default on Kobo Clara BW and Kobo Libra Color. OFL licensed.

### NV Elstob

<kbd><img src="./examples/NV-Elstob.png" width='400px'/></kbd>

**NV Elstob** is a version of [Elstob](https://github.com/psb1558/Elstob-font) that has been renamed so it works correctly on Kobo devices. It is based on the 12pt version. Does not have a separate repository because no other changes were applied. OFL licensed.

### NV Cardo

<kbd><img src="./examples/NV-Cardo.png" width='400px'/></kbd>

**NV Cardo** is a version of [Cardo](https://github.com/ryanfb/Cardo) with 20% spacing and has been renamed so you can keep the original Cardo installed side-by-side as well. Does not have a separate repository because no other changes were applied. OFL licensed.

### NV Source Serif

<kbd><img src="./examples/NV-SourceSerif.png" width='400px'/></kbd>

**NV Source Serif** is a version of [Source Serif 4](https://github.com/adobe-fonts/source-serif) with 20% spacing and has been renamed so it works correctly on Kobo devices. Does not have a separate repository because no other changes were applied. OFL licensed.

### NV Charter

<kbd><img src="./examples/NV-Charter.png" width='400px'/></kbd>

**NV Charter**, is a renamed version of [XCharter](https://www.ctan.org/tex-archive/fonts/xcharter/), which is an extended version of [Bitstream Charter](https://en.wikipedia.org/wiki/Bitstream_Charter). This one has a [dedicated repository](https://github.com/nicoverbruggen/nv-charter) that I've linked. Available under a [Free license](https://github.com/nicoverbruggen/nv-charter/blob/main/LICENSE).

### NV Palatium

<kbd><img src="./examples/NV-Palatium.png" width='400px'/></kbd>

**NV Palatium**, is a renamed version of [Domitian](https://www.ctan.org/tex-archive/fonts/domitian/), which is an extended version of [URW Palladio](https://tug.org/FontCatalogue/urwpalladio/). This one has a [dedicated repository](https://github.com/nicoverbruggen/nv-palatium) that I've linked. Available under a [Free license](https://github.com/nicoverbruggen/nv-palatium/blob/main/LICENSE).

### Where can I get the fonts?

The fonts are available via the [release](https://github.com/nicoverbruggen/ebook-fonts/releases).

You can learn more about how and why I originally made these tweaked fonts on my blog: [Patching Fonts for my Kobo](https://nicoverbruggen.be/blog/patching-fonts-for-kobo). I explain there why and how.

## How to install

To install these fonts on your Kobo, unzip the files and drag the font files into the `fonts` directory at the root of your Kobo device after connecting your Kobo to your PC via USB cable. You may need to create the `fonts` directory.

**I recommend rebooting your Kobo after installing the fonts to make sure they work correctly. A reboot is REQUIRED if you already had other versions of these fonts installed on your device, or the new versions won't be used.**

To reboot, long-press the power button until your Kobo says it has been shut down. Then, press the power button again and wait for your device to restart.

## FAQ

### Can I test these fonts?

Yes, I recommend grabbing the **Evaluating typefaces for electronic reading** document that I have added as a sample book. It contains markup to test various font styles and some more information about the included fonts. 

You can get the [Kobo epub](/docs/evaluating-typefaces.kepub.epub) or [regular epub](/docs/evaluating-typefaces.epub), which you should be able to copy to your e-reader.

### What tweaks have been applied to these fonts?

- I've normalized all fonts to a **20% line height** (using `font-line percent 20`). Some fonts rendered poorly on Kobo devices with the line height slider all the way to the left. This fixes that!
- Incorrect **PANOSE information has been corrected** where necessary (using [panosifier](https://github.com/source-foundry/panosifier)). This ensures that the fonts render correctly on Kobo devices.
- Certain fonts have had their **glyphs rescaled**. In particular, NV Junius and NV Garamond have had their glyph sizes increased by 10%, making them seem visually larger, and more consistent in size with the other fonts included in this collection.
- All of the **fonts have been renamed** (using [fontname.py](https://github.com/chrissimpkins/fontname.py)). This way, you can keep them installed side-by-side with the original versions, if you'd like. This is also a requirement of the Open Font License, which does not allow you to redistribute the fonts using the original name if they have been altered.

### How are these fonts licensed?

Most of these fonts are available under their original [Open Font License](https://openfontlicense.org/). Because of licensing rules, the font names have been modified to include a prefix to avoid confusion with the original fonts.

_NV Charter_ is available under the original Bitstream license, which is included in the respective archive and directory.

### Is there anything else I should do?

If you are manually transferring books to your Kobo devices, you should consider converting `epub` files to `kepub` files. To do this, you can use [kepubify](https://pgaskin.net/kepubify/) or use [Calibre](https://calibre-ebook.com/). This ensures that your Kobo device will use a superior and faster book renderer. This renderer also gives you broader font compatibility.

### What is your favorite font from the collection?

For simple books and basic readability, I personally prefer NV Charter or NV Jost. For fantasy books, I prefer to use NV Garamond or NV Cardo.

### Why did your prefix the fonts with "NV"?

Well, those are my initials... also, I like to think of the prefix to mean "Nice Version" or "Nico's Version". (I initially suffixed them with "eBook" but I wanted to have shorter font names for display purposes on smaller e-ink devices.)

### In your original blog post, you made various fonts available. Where are those?

Included in the repository right now are only my tweaked fonts, which have all be prefixed with _NV_. However, [the older release](https://github.com/nicoverbruggen/ebook-fonts/releases/tag/v2024.03) may still be of interest as I've included my initial batch of tweaked fonts mentioned in [the blog post](https://nicoverbruggen.be/blog/patching-fonts-for-kobo) there.