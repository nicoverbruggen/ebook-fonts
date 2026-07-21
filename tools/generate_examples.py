#!/usr/bin/env python3
"""Render the README example images for every font in ./fonts.

For each family in fonts/core this draws a full mock reading page (the same
excerpt for every font, at the width of a Kobo Libra Color screen) into
./examples/core. For each family in fonts/extra a shorter card is drawn into
./examples/extra: a short paragraph, then a rule, then a line showing each
available style. The family name is left to the README heading above the card.

Family names are read from each font's name table (preferring the typographic
family, nameID 16), never from the filename, matching generate_manifest.py.
Output filenames are the family name with spaces replaced by hyphens.

Text is shaped with HarfBuzz (uharfbuzz), so kerning and ligatures come out
the way a real renderer would draw them, and rasterized with FreeType with
hinting explicitly disabled (both the fonts' own hint programs and the
autohinter): Kobo does not apply hinting to the KF builds, so hinted images
would misrepresent what the fonts look like on device.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import freetype
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from PIL import Image, ImageOps

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"

FOREGROUND = (16, 16, 16)
BACKGROUND = (255, 255, 255)
RULE_COLOR = (208, 208, 208)
# The spine: a solid block down the right edge, with the family name knocked
# out in white in a fixed-width font, so it renders identically for every
# family. Martian Mono (OFL) is vendored under tools/assets with its license.
SPINE_COLOR = (0, 0, 0)
SPINE_TEXT_COLOR = (255, 255, 255)
SPINE_WIDTH = 64
SPINE_FONT = Path(__file__).resolve().parent / "assets" / "martian-mono" / "MartianMono-sWdRg.ttf"

# Every image gets a thin frame on its left, top and bottom edges, in place
# of the <kbd> styling the README used to lean on; the spine block already
# closes off the right edge.
BORDER_COLOR = (170, 170, 170)  # #AAA
BORDER_WIDTH = 2
# The README displays the cards at 400px wide, about a third of their real
# size, so a rule drawn 6px tall shows up as the intended 2px line.
RULE_HEIGHT = 6

# Kobo Libra Color screen width; the height of each image fits its content.
PAGE_WIDTH = 1264
MARGIN_X = 52

KICKER = "PROLOGUE"
TITLE = "The Firm"
FOOTER_NOTE = "INCLUDED VARIANTS"

# Every core page sets this excerpt in full; the image height follows from
# how the font sets it, so wide-set fonts simply produce a taller image.
PARAGRAPHS = [
    "Trevelyan & Co. designed typefaces and, through its small-press "
    "division, published books set in them, an arrangement Mr. Trevelyan "
    "considered so obviously correct that he rarely bothered to defend it, "
    "in much the same way that he did not defend the usefulness of windows, "
    "decent tea, or the avoidance of badly spaced capitals.",
]

# The extra cards set one short paragraph instead. The wording deliberately
# leans on fi/ffi ligature triggers so shaping problems would be visible.
EXTRA_PARAGRAPH = (
    "Mr. Trevelyan judged a typeface by setting a page of fiction in it and "
    "reading until the letters got out of the way of the story. The "
    "difficult ones never did; the fine ones vanished by the first paragraph."
)

STYLE_ORDER = ["Regular", "Italic", "Bold", "Bold Italic"]

LOAD_FLAGS = (
    freetype.FT_LOAD_RENDER
    | freetype.FT_LOAD_NO_HINTING
    | freetype.FT_LOAD_NO_AUTOHINT
)


class Style:
    """One font file at one pixel size: HarfBuzz shaping, unhinted rendering."""

    def __init__(self, path: Path, size: int):
        face = hb.Face(path.read_bytes())
        self.hb_font = hb.Font(face)
        self.scale = size / face.upem
        self.ft_face = freetype.Face(str(path))
        self.ft_face.set_char_size(size * 64)
        self.ascent = self.ft_face.size.ascender / 64
        self.descent = -self.ft_face.size.descender / 64

    def shape(self, text: str):
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(self.hb_font, buffer)
        return zip(buffer.glyph_infos, buffer.glyph_positions)

    def measure(self, text: str) -> float:
        return sum(pos.x_advance for _, pos in self.shape(text)) * self.scale

    def ink_extents(self, text: str) -> tuple[float, float]:
        """Return (rise above, drop below) the baseline of the actual ink."""
        rise = drop = 0.0
        for info, pos in self.shape(text):
            self.ft_face.load_glyph(info.codepoint, LOAD_FLAGS)
            slot = self.ft_face.glyph
            if slot.bitmap.rows:
                top = slot.bitmap_top + pos.y_offset * self.scale
                rise = max(rise, top)
                drop = max(drop, slot.bitmap.rows - top)
        return rise, drop

    def draw(
        self,
        image: Image.Image,
        xy: tuple[float, float],
        text: str,
        color: tuple[int, int, int] = FOREGROUND,
    ) -> float:
        """Draw text with its baseline starting at xy; return the end x."""
        x, y = xy
        for info, pos in self.shape(text):
            self.ft_face.load_glyph(info.codepoint, LOAD_FLAGS)
            slot = self.ft_face.glyph
            bitmap = slot.bitmap
            if bitmap.width and bitmap.rows:
                rows = range(bitmap.rows)
                data = b"".join(
                    bytes(bitmap.buffer[row * bitmap.pitch : row * bitmap.pitch + bitmap.width])
                    for row in rows
                )
                mask = Image.frombytes("L", (bitmap.width, bitmap.rows), data)
                image.paste(
                    color,
                    (
                        round(x + pos.x_offset * self.scale) + slot.bitmap_left,
                        round(y - pos.y_offset * self.scale) - slot.bitmap_top,
                    ),
                    mask,
                )
            x += pos.x_advance * self.scale
        return x

    def draw_tracked(self, image: Image.Image, xy: tuple[float, float], text: str, tracking: float) -> None:
        """Draw letterspaced text."""
        x, y = xy
        for ch in text:
            self.draw(image, (x, y), ch)
            x += self.measure(ch) + tracking


def read_names(font_path: Path) -> tuple[str, str]:
    """Return (family, subfamily) from the font's name table."""
    name_table = TTFont(font_path, lazy=True)["name"]
    family = name_table.getDebugName(16) or name_table.getDebugName(1)
    subfamily = name_table.getDebugName(17) or name_table.getDebugName(2)
    if not family:
        raise RuntimeError(f"{font_path}: no family name in name table")
    return family, subfamily or ""


def collect_families(collection: str) -> dict[str, dict[str, Path]]:
    """Map each family in a collection to its font files, keyed by style."""
    source_dir = REPO_ROOT / "fonts" / collection
    fonts = sorted(source_dir.glob("*.ttf"))
    if not fonts:
        raise RuntimeError(f"No .ttf files found in {source_dir}")

    families: dict[str, dict[str, Path]] = {}
    for font in fonts:
        family, subfamily = read_names(font)
        families.setdefault(family, {})[subfamily] = font
    return families


def wrap(text: str, style: Style, width: int) -> list[str]:
    """Greedy word wrap using shaped line widths."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if current and style.measure(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_spine(image: Image.Image, family: str) -> None:
    """Solid block down the right edge, the family name reading downwards
    from the top."""
    width, height = image.size
    image.paste(SPINE_COLOR, (width - SPINE_WIDTH, 0, width, height))
    spine = Style(SPINE_FONT, 28)
    # Size the strip from the font's fixed metrics, not the name's ink:
    # per-name bounds would shift the letter stems sideways between images
    # depending on whether the name happens to have descenders.
    ascent, descent = round(spine.ascent), round(spine.descent)
    strip = Image.new("RGB", (round(spine.measure(family)) + 2, ascent + descent), SPINE_COLOR)
    spine.draw(strip, (1, ascent), family, color=SPINE_TEXT_COLOR)
    strip = strip.transpose(Image.Transpose.ROTATE_270)
    image.paste(strip, (width - SPINE_WIDTH + (SPINE_WIDTH - strip.width) // 2, 22))


def render_core_page(family: str, styles: dict[str, Path]) -> Image.Image:
    regular = styles.get("Regular") or next(iter(styles.values()))
    bold = styles.get("Bold", regular)
    # The content keeps a full margin of white between it and the spine.
    content_width = PAGE_WIDTH - 2 * MARGIN_X - SPINE_WIDTH

    kicker = Style(regular, 36)
    title = Style(bold, 100)
    body = Style(regular, 48)
    note = Style(regular, 28)
    variants = [(name, Style(styles[name], 48)) for name in STYLE_ORDER if name in styles]

    line_height = 69
    paragraph_gap = 32
    gap = 64  # margins and rule clearance, measured to the ink

    # Lay everything out first; the page height follows from the content.
    kicker_baseline = gap + round(kicker.ink_extents(KICKER)[0])
    wrapped = [wrap(paragraph, body, content_width) for paragraph in PARAGRAPHS]

    baseline = kicker_baseline + 280
    last_baseline = baseline
    for lines in wrapped:
        last_baseline = baseline + line_height * (len(lines) - 1)
        baseline = last_baseline + line_height + paragraph_gap

    last_line = wrapped[-1][-1]
    rule_y = round(last_baseline + body.ink_extents(last_line)[1]) + gap
    note_baseline = rule_y + RULE_HEIGHT + gap + round(note.ink_extents(FOOTER_NOTE)[0])
    variants_rise = max(style.ink_extents(name)[0] for name, style in variants)
    variants_drop = max(style.ink_extents(name)[1] for name, style in variants)
    variants_baseline = note_baseline + 44 + round(variants_rise)
    height = variants_baseline + round(variants_drop) + gap

    image = Image.new("RGB", (PAGE_WIDTH, height), BACKGROUND)

    kicker.draw_tracked(image, (MARGIN_X, kicker_baseline), KICKER, 12)
    title.draw(image, (MARGIN_X, kicker_baseline + 130), TITLE)

    baseline = kicker_baseline + 280
    for lines in wrapped:
        for line in lines:
            body.draw(image, (MARGIN_X, baseline), line)
            baseline += line_height
        baseline += paragraph_gap

    image.paste(RULE_COLOR, (MARGIN_X, rule_y, MARGIN_X + content_width, rule_y + RULE_HEIGHT))

    note.draw_tracked(image, (MARGIN_X, note_baseline), FOOTER_NOTE, 6)

    x = float(MARGIN_X)
    separator = body.measure("   ")
    for name, style in variants:
        x = style.draw(image, (x, variants_baseline), name) + separator

    draw_spine(image, family)

    return image


def render_extra_card(family: str, styles: dict[str, Path]) -> Image.Image:
    regular = styles.get("Regular") or next(iter(styles.values()))
    body = Style(regular, 50)
    variants = [(name, Style(styles[name], 50)) for name in STYLE_ORDER if name in styles]

    width = PAGE_WIDTH
    # As on the core pages, a full margin of white sits before the spine.
    content_width = width - 2 * MARGIN_X - SPINE_WIDTH
    line_height = 70
    gap = 64  # ink-to-rule distance, identical above and below the rule
    lines = wrap(EXTRA_PARAGRAPH, body, content_width)

    body_baseline = 118
    last_baseline = body_baseline + line_height * (len(lines) - 1)
    rule_y = round(last_baseline + body.ink_extents(lines[-1])[1]) + gap
    variants_rise = max(style.ink_extents(name)[0] for name, style in variants)
    variants_drop = max(style.ink_extents(name)[1] for name, style in variants)
    note = Style(regular, 28)
    note_baseline = rule_y + RULE_HEIGHT + gap + round(note.ink_extents(FOOTER_NOTE)[0])
    variants_baseline = note_baseline + 44 + round(variants_rise)
    height = variants_baseline + round(variants_drop) + gap

    image = Image.new("RGB", (width, height), BACKGROUND)

    baseline = body_baseline
    for line in lines:
        body.draw(image, (MARGIN_X, baseline), line)
        baseline += line_height

    image.paste(RULE_COLOR, (MARGIN_X, rule_y, MARGIN_X + content_width, rule_y + RULE_HEIGHT))

    note.draw_tracked(image, (MARGIN_X, note_baseline), FOOTER_NOTE, 6)

    # One run per available style, set in that style, separated by spaces.
    x = float(MARGIN_X)
    separator = body.measure("   ")
    for name, style in variants:
        x = style.draw(image, (x, variants_baseline), name) + separator

    draw_spine(image, family)

    return image


def output_name(family: str) -> str:
    return family.replace(" ", "-") + ".png"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", metavar="FAMILY", help="Render just this family (exact name, any collection).")
    args = parser.parse_args()

    rendered = 0
    for collection, render in [("core", render_core_page), ("extra", render_extra_card)]:
        out_dir = EXAMPLES_DIR / collection
        out_dir.mkdir(parents=True, exist_ok=True)
        for family, styles in sorted(collect_families(collection).items()):
            if args.only and family != args.only:
                continue
            image = ImageOps.expand(render(family, styles), (BORDER_WIDTH, BORDER_WIDTH, 0, BORDER_WIDTH), BORDER_COLOR)
            # The frame wraps the page only: the spine bleeds to the edges,
            # so repaint its black over the border bands on the right.
            w, h = image.size
            image.paste(SPINE_COLOR, (w - SPINE_WIDTH, 0, w, BORDER_WIDTH))
            image.paste(SPINE_COLOR, (w - SPINE_WIDTH, h - BORDER_WIDTH, w, h))
            destination = out_dir / output_name(family)
            image.save(destination, optimize=True)
            print(f"{family} -> {destination.relative_to(REPO_ROOT)}")
            rendered += 1

    if not rendered:
        raise SystemExit(f"No family named {args.only!r} in fonts/core or fonts/extra")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
