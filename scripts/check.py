#!/usr/bin/env python3
"""Check the built CV, bibliography coverage, and final-pass TeX diagnostics."""

import re
import subprocess
import unicodedata

from export_publications import ROOT, export, parse_bibliography


def normalized(text):
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", "", text).translate(str.maketrans({"‐": "-", "‑": "-", "–": "-", "—": "-", "\u00ad": ""}))


def main():
    source = ROOT / "sections/refs.bib"
    data = export(source)
    entries = parse_bibliography(source)
    keys = {entry.attrib["id"] for entry in entries}
    citations = []
    for path in (ROOT / "sections").glob("*.tex"):
        citations.extend(re.findall(r"\\publication\{([^}]+)\}", path.read_text(encoding="utf-8")))
    if set(citations) != keys or len(citations) != len(set(citations)):
        raise SystemExit(f"Bibliography coverage mismatch: uncited={keys - set(citations)}, missing={set(citations) - keys}, or duplicate citations")

    logs = list((ROOT / ".build").glob("run.*/main.log"))
    if not logs:
        raise SystemExit("Run bash build.sh before checking the CV.")
    log = max(logs, key=lambda path: path.stat().st_mtime).read_text(encoding="utf-8", errors="replace")
    problems = re.findall(r"^.*(?:Overfull|undefined|Please.*rerun|Rerun to get|Missing character).*$", log, flags=re.MULTILINE | re.IGNORECASE)
    if problems:
        raise SystemExit("Final-pass TeX problems:\n" + "\n".join(problems))

    pdf = ROOT / "cv_full_leschultz.pdf"
    result = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"], capture_output=True, text=True, check=True)
    text = normalized(result.stdout)
    for paper in data["publications"]:
        if normalized(paper["title"]) not in text:
            raise SystemExit(f"Publication title missing from PDF: {paper['id']}")
        if paper["doi"] and normalized(paper["doi"]) not in text:
            raise SystemExit(f"DOI missing from PDF: {paper['id']}")
        if paper["category"] == "manuscript" and normalized(paper["status"]) not in text:
            raise SystemExit(f"Manuscript status missing: {paper['id']}")
    for expected in ("174,758", "Computational Materials Science and Engineering Committee", "Mar 15, 2026",
                     "Oct 20–22, 2026", "Sep 10, 2025", "Building AI Agents with Multimodal Models"):
        if normalized(expected) not in text:
            raise SystemExit(f"Expected career update missing from PDF: {expected}")
    gnn_paper = next(p for p in data["publications"] if p["id"] == "schultz_2026")
    if gnn_paper["pages"] != "10836–10853":
        raise SystemExit("Page range was not preserved in the bibliography export.")
    print(f"CV checks passed: {len(citations)} citations, {len(data['publications'])} publication records, career updates, DOI text, and final-pass layout diagnostics.")


if __name__ == "__main__":
    main()
