"""Exercise Biber conversion with names, page lists, and invalid source data."""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from export_publications import export

ARTICLE = r"""@article{example,
  author = {Schultz, Lane E. and Sava Gallis, Dorina F. and Dingreville, R\'{e}mi},
  title = {A {Mo--S} study},
  journal = {Example Journal},
  year = {2026},
  pages = {12--19, 42},
  doi = {10.1234/example}
}
"""


class BibliographyExportTest(unittest.TestCase):
    def convert(self, text):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "refs.bib"
            source.write_text(text, encoding="utf-8")
            return export(source)

    def test_names_accents_case_and_page_lists_survive_conversion(self):
        paper = self.convert(ARTICLE)["publications"][0]
        self.assertEqual(paper["title"], "A Mo–S study")
        self.assertEqual(paper["pages"], "12–19, 42")
        self.assertEqual([a["name"] for a in paper["authors"]],
                         ["Lane E. Schultz", "Dorina F. Sava Gallis", "Rémi Dingreville"])
        self.assertTrue(paper["authors"][0]["is_owner"])
        self.assertFalse(paper["authors"][1]["is_owner"])

    def test_duplicate_keys_fail_instead_of_silently_dropping_a_paper(self):
        with self.assertRaisesRegex(RuntimeError, "Duplicate entry key"):
            self.convert(ARTICLE + ARTICLE)

    def test_manuscript_requires_an_explicit_status(self):
        text = "@unpublished{draft, author={Schultz, Lane E.}, title={Example draft}, year={2026}}"
        with self.assertRaisesRegex(ValueError, "manuscript status"):
            self.convert(text)


if __name__ == "__main__":
    unittest.main()
