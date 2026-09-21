"""Run with python3 -m unittest discover -s tools/repair inside fntbld-oci."""

from pathlib import Path
import tempfile
import unittest

from fontTools.ttLib import TTFont

from build_synthetic_bolds import REPO_ROOT, FAMILIES, STYLE_SOURCES, embolden


class SyntheticBoldMetadataTests(unittest.TestCase):
    def test_radley_bold_weight_with_unspecified_panose_family(self):
        font_dir = REPO_ROOT / "fonts" / "extra"
        with tempfile.TemporaryDirectory() as temporary:
            for style, strength in FAMILIES["Radley"].items():
                with self.subTest(style=style):
                    source = font_dir / f"NV_Radley-{STYLE_SOURCES[style]}.ttf"
                    target = Path(temporary) / f"Radley-{style}.ttf"
                    with TTFont(source) as font:
                        self.assertEqual(font["OS/2"].panose.bFamilyType, 0)
                        self.assertEqual(font["OS/2"].panose.bWeight, 5)
                    embolden(source, target, strength)
                    with TTFont(target) as font:
                        self.assertEqual(font["OS/2"].panose.bFamilyType, 0)
                        self.assertEqual(font["OS/2"].panose.bWeight, 8)
                    with TTFont(font_dir / f"NV_Radley-{style}.ttf") as font:
                        self.assertEqual(font["OS/2"].usWeightClass, 700)
                        self.assertEqual(font["OS/2"].panose.bWeight, 8)


if __name__ == "__main__":
    unittest.main()
