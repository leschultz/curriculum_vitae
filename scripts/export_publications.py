#!/usr/bin/env python3
"""Export the authoritative BibLaTeX bibliography as portable website metadata.

Biber handles BibTeX parsing, compound names, and TeX accents. Python uses only
the standard library. No DOI lookup or other network request occurs at build time.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {"b": "http://biblatex-biber.sourceforge.net/biblatexml"}
CATEGORIES = {
    "article": "journal",
    "unpublished": "manuscript",
    "online": "preprint",
    "inproceedings": "conference",
}


def plain(element):
    """Flatten Biber's decoded name parts and remove BibTeX case protection."""
    if element is None:
        return ""
    text = " ".join(" ".join(element.itertext()).split())
    for source, target in ((r"\&", "&"), (r"\%", "%"), (r"\_", "_"),
                           ("---", "—"), ("--", "–"), ("{", ""), ("}", "")):
        text = text.replace(source, target)
    if "\\" in text:
        raise ValueError(f"Unsupported TeX command in exported text: {text}")
    return text


def parse_bibliography(source):
    if not shutil.which("biber"):
        raise RuntimeError("Biber is required. See the CV README for installation instructions.")
    with tempfile.TemporaryDirectory(prefix="cv-bibliography-") as directory:
        result = subprocess.run(
            ["biber", "--tool", "--output-format=biblatexml",
             f"--output-directory={directory}", "--output-file=refs.xml", str(source)],
            capture_output=True, text=True, check=False,
        )
        if result.returncode or re.search(r"\b(?:WARN|ERROR)\s+-", result.stdout + result.stderr):
            raise RuntimeError(f"Biber could not parse the bibliography:\n{result.stdout}\n{result.stderr}")
        tree = ET.parse(Path(directory) / "refs.xml")
    return tree.findall("b:entry", NS)


def export(source):
    publications = []
    seen_ids, seen_dois = set(), set()
    for entry in parse_bibliography(source):
        key = entry.attrib["id"]
        kind = entry.attrib["entrytype"]
        if key in seen_ids:
            raise ValueError(f"Duplicate bibliography key: {key}")
        seen_ids.add(key)
        if kind not in CATEGORIES:
            if kind != "misc":
                raise ValueError(f"Unmapped bibliography type for {key}: {kind}")
            continue  # Presentations belong in the CV, not the publication list.

        def field(name):
            if name == "pages":
                ranges = entry.findall("b:pages/b:list/b:item", NS)
                if ranges:
                    parts = []
                    for item in ranges:
                        start, end = plain(item.find("b:start", NS)), plain(item.find("b:end", NS))
                        parts.append("–".join(filter(None, (start, end))) if start or end else plain(item))
                    return ", ".join(parts)
            return plain(entry.find(f"b:{name}", NS))

        authors = []
        for name in entry.findall("b:names[@type='author']/b:name", NS):
            given = plain(name.find("b:namepart[@type='given']", NS))
            family = plain(name.find("b:namepart[@type='family']", NS))
            prefix = plain(name.find("b:namepart[@type='prefix']", NS))
            suffix = plain(name.find("b:namepart[@type='suffix']", NS))
            display = " ".join(part for part in (given, prefix, family) if part)
            if suffix:
                display += f", {suffix}"
            authors.append({"name": display, "is_owner": family == "Schultz" and given.startswith("L")})
        title, date, doi = field("title"), field("date"), field("doi")
        if not title or not authors or not re.match(r"^\d{4}(?:-|$)", date):
            raise ValueError(f"Missing title, authors, or year for {key}")
        if doi:
            if doi.lower() in seen_dois:
                raise ValueError(f"Duplicate DOI: {doi}")
            seen_dois.add(doi.lower())
        category = CATEGORIES[kind]
        note = field("note")
        if category == "manuscript" and note not in {"Under review", "In preparation", "Submitted", "Accepted"}:
            raise ValueError(f"Specify the manuscript status in the note field for {key}")
        if category != "manuscript" and not doi:
            raise ValueError(f"Missing DOI for {key}")
        publications.append({
            "id": key,
            "category": category,
            "title": title,
            "authors": authors,
            "year": int(date[:4]),
            "venue": field("journaltitle") or field("booktitle") or ("arXiv" if category == "preprint" else ""),
            "volume": field("volume"),
            "issue": field("number"),
            "pages": field("pages"),
            "article_number": field("eid"),
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else "",
            "status": note if category == "manuscript" else {"journal": "Published", "preprint": "Preprint", "conference": "Conference paper"}[category],
            "note": note,
        })
    publications.sort(key=lambda p: (
        list(CATEGORIES.values()).index(p["category"]), -p["year"],
        not p["authors"][0]["is_owner"], p["id"],
    ))
    return {"schema_version": 1,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "publications": publications}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "sections/refs.bib")
    parser.add_argument("--output", type=Path, help="Write JSON to this path (default: stdout)")
    parser.add_argument("--bibtex-output", type=Path, help="Also copy the source bibliography to this path")
    args = parser.parse_args()
    try:
        data = export(args.source.resolve())
    except (ValueError, RuntimeError, OSError) as error:
        parser.exit(1, f"{error}\n")
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    if args.bibtex_output:
        args.bibtex_output.write_bytes(args.source.read_bytes())


if __name__ == "__main__":
    main()
