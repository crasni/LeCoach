"""Use actual PDF extraction to catch stale text, links and wrong artifact pairs."""

import shutil
import xml.etree.ElementTree as ET

import pytest

from scripts.check_submission import NS, ROOT, check_proposal, main

SOURCE = ROOT / "docs/submission/proposal.fodp"
PDF = ROOT / "docs/submission/proposal.pdf"
requires_poppler = pytest.mark.skipif(
    not all(shutil.which(name) for name in ("pdfinfo", "pdftotext")),
    reason="artifact integration checks require Poppler's PDF utilities",
)


@requires_poppler
def test_tracked_pair_matches_and_is_not_modified():
    before = SOURCE.read_bytes(), PDF.read_bytes()
    report = check_proposal(SOURCE, PDF)
    assert 1 <= report["pages"] <= 20
    assert report["hyperlinks"] > 0
    assert (SOURCE.read_bytes(), PDF.read_bytes()) == before


@requires_poppler
@pytest.mark.parametrize("change,diagnostic", [
    ("text", "text differs on page 1"),
    ("link", "hyperlink destinations differ"),
    ("page", "page counts differ"),
])
def test_stale_source_is_rejected(tmp_path, change, diagnostic):
    document = ET.parse(SOURCE)
    slides = document.find("./office:body/office:presentation", NS)
    assert slides is not None
    if change == "text":
        paragraph = slides.find("draw:page//text:p", NS)
        assert paragraph is not None
        paragraph.text = "Incorrect unpublished replacement title"
    elif change == "link":
        link = slides.find("draw:page//text:a", NS)
        assert link is not None
        link.set(f"{{{NS['xlink']}}}href", "https://example.invalid/stale")
    else:
        page = slides.find("draw:page", NS)
        assert page is not None
        slides.remove(page)
    source = tmp_path / "stale.fodp"
    document.write(source)
    with pytest.raises(ValueError, match=diagnostic):
        check_proposal(source, PDF)


def test_page_budget_is_enforced_before_pdf_tools():
    with pytest.raises(ValueError, match="allowed total"):
        check_proposal(SOURCE, PDF, max_pages=1)


def test_missing_input_fails_with_nonzero_exit(tmp_path, capsys):
    assert main(["--source", str(tmp_path / "missing.fodp"), "--pdf", str(PDF)]) == 1
    assert "FAIL proposal" in capsys.readouterr().err


def test_missing_pdf_utility_has_actionable_error(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _: None)
    with pytest.raises(ValueError, match="install Poppler"):
        check_proposal(SOURCE, PDF)
