"""Read-only proposal source/PDF identity checks; requires Poppler's PDF utilities.

This checks artifact consistency, not visual quality, language, claim accuracy,
live acceptance, recording, registration or submission.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "presentation": "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
}


def pdf_tool(name: str, *args: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise ValueError(f"{name} is required; install Poppler's PDF utilities")
    result = subprocess.run(
        [executable, *args], capture_output=True, text=True, check=False, timeout=30,
    )
    if result.returncode:
        raise ValueError(f"{name} could not read the PDF (exit {result.returncode})")
    return result.stdout


def tokens(text: str) -> Counter:
    return Counter(re.findall(r"\S+", unicodedata.normalize("NFKC", text)))


def check_proposal(source: Path, pdf: Path, max_pages: int = 20) -> dict:
    """Reject page, visible-text and hyperlink mismatches without changing files.

    All pages count toward the budget. Appendices need separate human review;
    the current proposal has none. Notes are excluded from visible text.
    """
    if max_pages < 1:
        raise ValueError("max_pages must be positive")
    source_bytes, pdf_bytes = source.read_bytes(), pdf.read_bytes()
    document = ET.fromstring(source_bytes)
    pages = document.findall("./office:body/office:presentation/draw:page", NS)
    if not 1 <= len(pages) <= max_pages:
        raise ValueError(f"source has {len(pages)} pages; allowed total is 1–{max_pages}")
    info = pdf_tool("pdfinfo", str(pdf))
    count = re.search(r"^Pages:\s+(\d+)\s*$", info, re.MULTILINE)
    if count is None or int(count[1]) != len(pages):
        raise ValueError("source/PDF page counts differ or PDF page count is unavailable")
    source_links = set()
    paragraph_count = 0
    for number, page in enumerate(pages, 1):
        notes = page.find("presentation:notes", NS)
        if notes is not None:
            page.remove(notes)
        paragraphs = page.findall(".//text:p", NS) + page.findall(".//text:h", NS)
        paragraph_count += len(paragraphs)
        visible = " ".join(" ".join(p.itertext()) for p in paragraphs)
        extracted = pdf_tool("pdftotext", "-f", str(number), "-l", str(number), str(pdf), "-")
        if tokens(visible) != tokens(extracted):
            raise ValueError(f"visible source/PDF text differs on page {number}")
        source_links.update(
            link.attrib[f"{{{NS['xlink']}}}href"] for link in page.findall(".//text:a", NS)
        )
    url_info = pdf_tool("pdfinfo", "-url", str(pdf))
    pdf_links = set(re.findall(r"^\s*\d+\s+\S+\s+(\S+)\s*$", url_info, re.MULTILINE))
    if source_links != pdf_links:
        raise ValueError("source/PDF hyperlink destinations differ")
    return {
        "pages": len(pages),
        "visible_paragraphs": paragraph_count,
        "hyperlinks": len(source_links),
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "pdf_sha256": hashlib.sha256(pdf_bytes).hexdigest(),
        "scope": "artifact parity only; human and final acceptance checks remain separate",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "docs/submission/proposal.fodp")
    parser.add_argument("--pdf", type=Path, default=ROOT / "docs/submission/proposal.pdf")
    parser.add_argument("--max-pages", type=int, default=20,
                        help="total-page budget; counts all pages (default: 20)")
    parser.add_argument("--json", action="store_true", help="print a read-only identity report")
    args = parser.parse_args(argv)
    try:
        report = check_proposal(args.source.resolve(), args.pdf.resolve(), args.max_pages)
    except (OSError, ValueError, ET.ParseError, subprocess.TimeoutExpired) as error:
        print(f"FAIL proposal: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"PASS {report['pages']} pages, {report['visible_paragraphs']} paragraphs, "
              f"{report['hyperlinks']} links; source/PDF parity matches")
        print(report["scope"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
