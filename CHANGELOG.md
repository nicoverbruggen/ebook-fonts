# Changelog

All notable changes to this collection. Versions are the collection's own; see `VERSION`.

## Unreleased (4.1)

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| NV Alegreya | Extra | ✅ Added | Based on Alegreya (Huerta Tipográfica), designed for literature. |
| NV Alizar | Extra | ✅ Added | Based on Crimson Pro, the modern redraw of the same Crimson that NV Scarlet descends from. Sized to match NV Scarlet exactly so the two can be compared directly. |
| NV Andada | Extra | ✅ Added | Based on Andada Pro (Huerta Tipográfica): an organic slab with moderate contrast. |
| NV Halcyon | Extra | ✅ Added | Based on Merriweather, scaled down 8% to bring its unusually large x-height into line. |
| NV Ibarra | Extra | ✅ Added | Based on Ibarra Real Nova, reviving the types cut for the Madrid printer Joaquín Ibarra. Instanced at weight 450 rather than 400, so its thin strokes hold up on E Ink. Ibarra was part of the original 2024 prototype and returns here. |
| NV Publica | Extra | ✅ Added | Based on PT Serif. |
| NV Publica Wide | Extra | ✅ Added | Based on PT Serif Caption. Regular and Italic only, as no bold was ever drawn for that cut. |
| NV Yrsa | Extra | ✅ Added | Based on Yrsa (Rosetta Type), scaled up 15%. Yrsa was part of the original 2024 prototype and returns here. |
| NV Scarlet | Extra | 👌 Rebased | Now based on Cochineal instead of Crimson (2012). Cochineal is Michael Sharpe's extension of the same Crimson, adding over 1500 glyphs, real small caps, old-style and lining figures, fractions, and Greek and Cyrillic. Scaled 10% so it reads at the same size as before. |
| NV Tabula | Extra | 👌 Renamed | Was NV Plex Serif. The font itself is unchanged. |
| NV Sable | Extra | 👌 Renamed | Was NV Lore. The font itself is unchanged. |
| NV Kierkegaard | Extra | 👌 Updated | Glyph scale increased 9%, since it read a size down from the rest of the collection. |
| NV Libertinus | Extra | 👌 Updated | Glyph scale increased 11%, since it read a size down from the rest of the collection. |

### Removed

| Font | Collection | Change | Details |
|---|---|---|---|
| NV Cooper | Extra | ❌ Removed | |
| NV Source Serif | Extra | ❌ Removed | Superseded by Sourcerer in the Core Collection. |

### Other changes

- Some fonts were renamed to better comply with the OFL license's RFN policy.
- A `manifest.json` is now attached to each release, listing every font by collection with direct download links for the individual files and for the zips.
- Releases are published automatically when a tag is pushed. Tags on `main` are stable releases; tags elsewhere ship as pre-releases.

## v4.0 (2026-07-02)

Addresses a common complaint about "wobbly" fonts and an uneven baseline on Kobo e-readers. If you had a previous release installed, replacing the fonts and restarting the device is highly recommended.

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| Libron | Core | ✅ Added | Replaces Readerly. |
| NV Clara | Extra | ✅ Added | A version of [Clara](https://ctan.org/pkg/clara) by Seamas O Brogain, with adjusted metrics and an 8% glyph scale increase for e-readers. |
| NV Erewhon | Extra | ✅ Added | A version of [Erewhon](https://ctan.org/pkg/erewhon), derived from Heuristica and Utopia, with adjusted metrics for e-readers. |
| NV Kierkegaard | Extra | ✅ Added | A renamed version of [Kierkegaard Text](https://github.com/jrgdrs/Kierkegaard) by Jörg Drees, with adjusted metrics for e-readers. |
| NV Plex Serif | Extra | ✅ Added | A renamed version of [IBM Plex Serif](https://github.com/IBM/plex), so it works correctly on Kobo devices and can be installed alongside the original. Not mentioned in the release notes; described in the README at the time. |
| Readerly | Core to Extra | 👌 Moved | Superseded by Libron in Core. |
| NV Charis | Core | 👌 Updated | A few small adjustments. |
| NV Ancizar | Extra | 👌 Updated | Scaled up 8% to match the optical size of the other fonts. A kern pair (`n -> quote -> s`) was fixed by hand. |

### Other changes

- Uses the latest `kobo-font-fix`, so all KF fonts render more accurately on Kobo devices.

## v3.2 (2026-05-19)

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| Sourcerer | Core | 👌 Updated | |
| Readerly | Core | 👌 Updated | |

### Other changes

- Fixed an issue with composite glyphs.
- A pinned version of `kobo-font-fix` is now used.
- No fonts were added or removed in this release.

## v3.1 (2026-04-28)

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| Cartisse | Core | ✅ Added | Reintroduced, based on XCharter. Not OFL licensed, so an extended copyright notice is included as part of it. |
| NV Disleksio | Extra | ✅ Added | Replaces NV OpenDyslexic: a more readable variant with tightened character spacing, 10% line height (down from 20%), and italics based on the slanted regular for consistency. |
| NV Charis | Core | 👌 Updated | Corrects an issue with the `i` and `j` glyphs that was very noticeable on Kobo devices with the hinting at the time. |

### Removed

| Font | Collection | Change | Details |
|---|---|---|---|
| NV OpenDyslexic | Extra | ❌ Removed | Replaced by NV Disleksio. |

### Other changes

- KF versions reprocessed with the latest `kobo-font-fix`.

## v3.0 (2026-04-03)

The Core Collection was reorganised substantially in this release. The original notes covered the Core changes and summarised the rest as "various other fonts"; the table below lists what actually moved.

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| Readerly | Core | ✅ Added | A modified font based on [Newsreader (9pt)](https://github.com/productiontype/Newsreader), aiming to be metrically very similar to Bookerly. Announced in the README as NV Readerly. |
| Sourcerer | Core | ✅ Added | A thicker version of [Source Serif 4](https://github.com/adobe-fonts/source-serif) with 20% spacing, renamed so it works correctly on Kobo devices. |
| NV Ancizar Sans | Extra | ✅ Added | A variant of [UNAL Ancizar Sans](https://github.com/UNAL-OMD/UNAL-Ancizar), with metrics altered for line height. The sans serif counterpart to Ancizar Serif. |
| NV Ancizar Serif | Extra | ✅ Added | A variant of [UNAL Ancizar Serif](https://github.com/UNAL-OMD/UNAL-Ancizar), with metrics altered for line height. |
| NV Castoro | Extra | ✅ Added | Based on Castoro. |
| NV NinePoint | Extra | ✅ Added | A variant of [Newsreader](https://fonts.google.com/specimen/Newsreader) based on the 9pt optical size, for maximum readability at smaller sizes. |
| NV OpenDyslexic | Extra | ✅ Added | A variant of [OpenDyslexic](https://forge.hackers.town/antijingoist/opendyslexic), newer than the version shipping on most Kobo and Kindle devices. |
| NV Charis | Extra to Core | 👌 Promoted | Replaces NV Charter, for improved weight and glyph coverage. |
| NV Charter | Core to Extra | 👌 Moved | Displaced from Core by NV Charis. |
| NV Georsio | Core to Extra | 👌 Moved | |
| NV Membo | Core to Extra | 👌 Moved | |

### Removed

| Font | Collection | Change | Details |
|---|---|---|---|
| NV Charter Basic | Extra | ❌ Removed | |
| NV Old Style | Extra | ❌ Removed | The QT Caslan variant added in v2.0. |

### Other changes

- All KF fonts improved: the generating script now applies operations to the outlines that make the font thickness slider work better on Kobo devices.

## v2.2 (2025-10-07)

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| NV Charter Basic | Extra | ✅ Added | Ships as KF Charter Basic in the Kobo collection. |
| NV Charter | Core | 👌 Updated | Also affects its KF variant. |
| NV Garamond | Core | 👌 Updated | Also affects its KF variant. |

### Other changes

- KF fonts are now stripped of their TrueType hints, for better rendering on high resolution E Ink displays. Older devices may prefer an earlier release.

## v2.1 (2025-08-22)

The original notes said only that new fonts had been added to the Extra Collection. The table below lists which.

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| NV Adelph | Extra | ✅ Added | A variant of [Adelphe](https://gitlab.com/bye-bye-binary/adelphe), with metrics altered for line height. OIFL licensed. |
| NV Basker | Extra | ✅ Added | A variant of [ANRT-Baskervville](https://github.com/anrt-type/ANRT-Baskervville), with metrics altered for line height. The medium weight is used for text rather than the regular. |
| NV Lore | Extra | ✅ Added | A variant of [Lora](https://github.com/cyrealtype/Lora-Cyrillic), with metrics altered for line height. |
| NV Scarlet | Core to Extra | 👌 Moved | |

### Other changes

- **KF versions** of the fonts were added, optimised for kerning on Kobo devices. If you read Kobo Store books or `kepub` files converted with Calibre, these are the ones to install.

## v2.0 (2025-07-19)

The collection is now split into a **Core** and an **Extra** set, bundled as two zip files.

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| NV Membo | Core | ✅ Added | Based on fbb. |
| NV Scarlet | Core | ✅ Added | Based on Crimson 2012. |
| NV Georsio | Core | ✅ Added | Based on Gelasio. |
| NV Legible Next | Core | ✅ Added | Based on Atkinson Hyperlegible Next. Announced as "NV Legible"; the font itself has always been NV Legible Next. |
| NV Charis | Extra | ✅ Added | Based on Charis 7.0. |
| NV Cooper | Extra | ✅ Added | Based on Cooper\*. |
| NV Junius | Extra | ✅ Added | Based on Junicode. |
| NV Gentium | Extra | ✅ Added | Based on Gentium 7.0. |
| NV Libertinus | Extra | ✅ Added | Based on Libertinus Serif. |
| NV Old Style | Extra | ✅ Added | A variant of QT Caslan from the [QualiType fonts package](https://ctan.org/pkg/qualitype), renamed and converted to TrueType for Kobo. |
| NV Literata | Extra | ✅ Added | Based on Literata. |
| NV Newsreader | Extra | ✅ Added | A variant of [Newsreader](https://fonts.google.com/specimen/Newsreader), based on a weight suited to e-reading. Not in the release notes; described in the README at the time. |
| NV Technical | Extra | ✅ Added | A variant of [STIX Two Text](https://fonts.google.com/specimen/STIX+Two+Text). Not in the release notes; described in the README at the time. |
| NV Zilla Slab | Extra | ✅ Added | Based on Zilla Slab from Mozilla. |

## v1.2 (2025-02-16)

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| NV Elstob | N.A. | ✅ Added | A renamed version of [Elstob](https://psb1558.github.io/Elstob-font/) at 12pt. |
| NV Elstob Eight | N.A. | ✅ Added | Based on the 8pt version, better suited to smaller text. Shipped as a zip only; never tracked in the repository. |
| NV Palatium | N.A. | ✅ Added | Based on [Domitian](https://github.com/dbenjaminmiller/domitian). Similar to Palatino, which is not present on Kobo devices but is available on Kindles. |
| NV Bitter | N.A. | ✅ Added | Not mentioned in the original release notes. |
| NV Source Serif | N.A. | ✅ Added | Not mentioned in the original release notes. |

## v1.1 (2025-02-08)

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| NV Charter | N.A. | ✅ Added | Has its [own repository](https://github.com/nicoverbruggen/nv-charter). |
| NV Jost | N.A. | 👌 Updated | |

### Removed

| Font | Collection | Change | Details |
|---|---|---|---|
| XCharter | N.A. | ❌ Removed | The unmodified original, dropped from the collection. |
| Cardo (linegap 20) | N.A. | ❌ Removed | One of the three "OG linegap20" builds of the original fonts. |
| EB Garamond (linegap 20) | N.A. | ❌ Removed | As above. |
| Jost (linegap 20) | N.A. | ❌ Removed | As above. |

## v1.0 (2025-01-03)

First numbered release, and a deliberate cleanup: the prototype's seventeen fonts were pared back to seven zips, keeping the tweaked NV fonts, XCharter, and three "OG linegap20" builds of the originals.

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| Cardo (linegap 20) | N.A. | ✅ Added | An original font with only a 20% line gap applied. |
| EB Garamond (linegap 20) | N.A. | ✅ Added | As above. |
| Jost (linegap 20) | N.A. | ✅ Added | As above. |

### Removed

| Font | Collection | Change | Details |
|---|---|---|---|
| Andika eBook | N.A. | ❌ Removed | |
| ChareInk 5 | N.A. | ❌ Removed | |
| Charis eBook | N.A. | ❌ Removed | |
| Charter eBook | N.A. | ❌ Removed | |
| EB Garamond | N.A. | ❌ Removed | |
| EB Garamond Absinthe | N.A. | ❌ Removed | |
| Gelasio eBook | N.A. | ❌ Removed | |
| Ibarra eBook | N.A. | ❌ Removed | Returns in 4.1 as NV Ibarra. |
| Literata eBook | N.A. | ❌ Removed | |
| Newsreader NV | N.A. | ❌ Removed | |
| Newsreader Thirty-Six | N.A. | ❌ Removed | |
| Newsreader eBook | N.A. | ❌ Removed | |
| Yrsa eBook | N.A. | ❌ Removed | Returns in 4.1 as NV Yrsa. |

## v0.1 (2024-03)

Released as "eBook Font Collection". I thought that I was going to publish just one release. Little did I know I would go down an incredibly interesting rabbit hole...

The first public collection, with each font distributed as its own zip. None of these were tracked in the repository at this point.

### New & Modified

| Font | Collection | Change | Details |
|---|---|---|---|
| NV Cardo | N.A. | ✅ Added | Cardo with 20% spacing, renamed so it installs beside the original. |
| NV Garamond | N.A. | ✅ Added | EB Garamond with a number of tweaks. Has its own repository. |
| NV Jost | N.A. | ✅ Added | A Jost variant with an altered lowercase g and single-storey a. Has its own repository. |
| Andika eBook | N.A. | ✅ Added | Based on [Andika](https://software.sil.org/andika/) by SIL. |
| ChareInk 5 | N.A. | ✅ Added | A modified ChareInk, which rendered italics better on Kobo devices. |
| Charis eBook | N.A. | ✅ Added | Based on [Charis SIL](https://software.sil.org/charis/). |
| Charter eBook | N.A. | ✅ Added | Under the original Bitstream license. |
| EB Garamond | N.A. | ✅ Added | The original, distributed with the collection. |
| EB Garamond Absinthe | N.A. | ✅ Added | A tweaked EB Garamond, sourced as-is from MobileRead for archival purposes. |
| Gelasio eBook | N.A. | ✅ Added | Based on [Gelasio](https://github.com/SorkinType/Gelasio). |
| Ibarra eBook | N.A. | ✅ Added | Based on [Ibarra Real Nova](https://github.com/googlefonts/ibarrareal). Returns in 4.1 as NV Ibarra. |
| Literata eBook | N.A. | ✅ Added | Based on [Literata](https://github.com/googlefonts/literata). |
| Newsreader NV | N.A. | ✅ Added | Newsreader 36pt with 20% spacing. |
| Newsreader Thirty-Six | N.A. | ✅ Added | Newsreader 36pt with the original spacing. |
| Newsreader eBook | N.A. | ✅ Added | Based on the 14pt optical size. |
| XCharter | N.A. | ✅ Added | Under the original Bitstream license. |
| Yrsa eBook | N.A. | ✅ Added | Based on [Yrsa](https://github.com/rosettatype/yrsa). Returns in 4.1 as NV Yrsa. |

The tweaks applied at this point were:

- A 20% line height, since some fonts rendered poorly on Kobo devices with the line height slider all the way to the left.
- Some fonts renamed (using [fontname.py](https://github.com/chrissimpkins/fontname.py)), so they can be installed side by side with the originals.
- PANOSE information corrected where necessary (using [panosifier](https://github.com/source-foundry/panosifier)), so the fonts render correctly on Kobo devices.

The glyphs themselves were not modified; no design alterations were made.
