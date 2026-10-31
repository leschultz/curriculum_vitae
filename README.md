# Lane E. Schultz — Curriculum Vitae

The LaTeX source and published PDF for my research CV.

- **PDF:** [cv_full_leschultz.pdf](https://leschultz.github.io/curriculum_vitae/cv_full_leschultz.pdf)
- **Research website:** [leschultz.github.io](https://leschultz.github.io/)

## Build

Use a TeX Live or MacTeX installation containing **XeLaTeX**, **Biber**, Source Sans
(the `sourcesans` or older `sourcesanspro` package), `biblatex`, `microtype`,
`geometry`, `ragged2e`, `enumitem`, `needspace`, `tabularx`, `lastpage`, `fancyhdr`,
`csquotes`, `titlesec`, `hyperref`, and `xurl`.

On Debian/Ubuntu, the complete prerequisites are:

```sh
sudo apt-get install texlive-xetex texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra biber poppler-utils
```

From this repository:

```sh
bash build.sh
```

The build runs XeLaTeX → Biber → XeLaTeX → XeLaTeX, then atomically replaces
`cv_full_leschultz.pdf`. A failed build leaves the previously published PDF intact.
Each build keeps its diagnostics and auxiliary files in an ignored `.build/run.*`
directory. The command prints the log location. No `latexmk` dependency is needed.

Optional PDF preview:

```sh
bash build.sh --open
```

The script also works from another directory when invoked with its full path.

## Editing the CV

| File | Responsibility |
| --- | --- |
| `main.tex` | Contact information, profile, section order, PDF metadata |
| `style.sty` | Typography, colors, reusable role/citation formatting |
| `sections/experience.tex` | Current and doctoral research |
| `sections/earlier_experience.tex` | Earlier research and engineering projects |
| `sections/refs.bib` | **Authoritative publication and presentation metadata** |
| `sections/publications.tex` | Publication categories and citation order |
| `sections/presentations.tex` | Conference presentations and posters |
| `sections/service.tex` | Committee membership, volunteering, honor societies |
| `sections/professional_development.tex` | Courses and workshops |
| Other `sections/*.tex` files | Education, skills, teaching, honors, languages/citizenship |

### Publication conventions

- Journal articles: `@article`; use the final journal-issue year when available.
- Use `eid` for article identifiers and `pages` for actual page ranges.
- Manuscripts: `@unpublished`; `note` holds the exact status (`Under review`,
  `In preparation`, `Submitted`, or `Accepted`).
- Public preprints: `@online`, with arXiv DOI, `eprint`, and `eprinttype`.
- Published conference papers: `@inproceedings`, with `booktitle` and DOI.
- Presentations/posters: `@misc`, with `howpublished`, location, and a descriptive `note`.
- Preserve published author order and name variants. Separate multiple initials
  with spaces (`L. E.`) so Biber keeps every initial.
- Bibliography keys are stable identifiers; a key's year need not match the final
  journal year. For example, `schultz_potentials_2024` now cites the 2025 issue.

When a manuscript's status changes, update both its entry type/metadata and its
category in `sections/publications.tex`. Every bibliography entry should be cited
exactly once in either publications or presentations.

The current TMS committee membership has no start date because one has not been
specified. Workshop participation is recorded as professional development, and
the March 15, 2026 workshop role is recorded as volunteer service.

## Checks

Python 3 and Poppler's `pdftotext` are needed for verification:

```sh
python3 scripts/check.py
python3 -m unittest discover -s tests -v
```

The checks verify citation coverage, exported page ranges, publication titles and
DOIs in extracted PDF text, manuscript statuses, career updates, and the final
TeX pass for overfull boxes, unresolved references, or missing characters. A
failure-path regression checks that a compiler error preserves the published PDF,
including when the repository path contains spaces.

Visually inspect all pages after a layout/content change. In particular, check
page breaks, long author lists, and the footer. GitHub Actions rebuilds and checks
the CV and uploads the PDF, page previews, and build diagnostics as artifacts.

## Synchronize the website

`sections/refs.bib` is the source of truth for publication metadata in both
repositories. The exporter uses Biber's BibLaTeXML output to correctly handle
compound names, accents, protected capitalization, and page ranges; Python itself
uses only the standard library.

With both repositories checked out next to each other:

```sh
python3 ../leschultz.github.io/scripts/sync_publications.py --cv .
python3 ../leschultz.github.io/scripts/sync_publications.py --cv . --check
```

For another consumer, export standalone JSON:

```sh
python3 scripts/export_publications.py --output /path/to/publications.json
```

The website stores a snapshot and complete generated HTML, so it deploys
independently and needs no runtime connection to this repository.

## Publishing

Rebuild and check the CV, then include the updated `cv_full_leschultz.pdf` with the
source changes when publishing through this repository's existing GitHub Pages
source. Synchronize and publish the website's metadata/HTML when bibliography
entries change. The PDF filename is the public link used by the website.

## Provenance

The original CV template was by Timmy Chan and adapted by Lane E. Schultz.
Publication dates, article identifiers, and page ranges were reconciled with
Crossref/publisher records in October 2026. The two ongoing manuscripts, workshop
participation, volunteer role, and committee membership were supplied by Lane.
