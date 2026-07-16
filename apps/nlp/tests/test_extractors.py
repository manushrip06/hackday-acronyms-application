from __future__ import annotations

import json
from pathlib import Path

from app.extractors import extract_candidates

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "team_wiki_expected.json"


def _load_fixtures() -> list[dict[str, object]]:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return [data]


def test_extracts_core_acronyms_from_sample_wiki():
    data = next(item for item in _load_fixtures() if item.get("name") == "team_wiki")
    wiki = ROOT / data["text_file"]
    text = wiki.read_text(encoding="utf-8")
    candidates = extract_candidates(text)
    found = {c.term for c in candidates}
    expected = set(data["expected_terms"])
    hits = expected & found
    recall = len(hits) / len(expected)
    assert recall >= 0.6, f"recall={recall:.2f} hits={sorted(hits)} missing={sorted(expected - found)}"
    for must in ("PIR", "GTM", "BAU"):
        assert must in found


def test_extracts_team_specific_terms_from_product_breakdown():
    data = next(item for item in _load_fixtures() if item.get("name") == "product_breakdown")
    doc = ROOT / data["text_file"]
    text = doc.read_text(encoding="utf-8")
    candidates = extract_candidates(text)
    found = {c.term for c in candidates}
    expected = set(data["expected_terms"])
    hits = expected & found
    recall = len(hits) / len(expected)
    assert recall >= 0.5, f"recall={recall:.2f} hits={sorted(hits)} missing={sorted(expected - found)}"
    for must in ("TLR", "DriftLoop"):
        assert must in found


def test_parenthetical_expansion():
    text = "Open a Written Assessment of Risk (WAR) before escalating."
    cands = extract_candidates(text)
    war = next(c for c in cands if c.term == "WAR")
    assert "Written Assessment of Risk" in (war.definition or "") or "Written Assessment of Risk" in war.aliases

def test_regression_release_captain():
    text = "The ReleaseCaptain owns the release checklist."
    candidates = extract_candidates(text)
    assert any(c.term == "ReleaseCaptain" for c in candidates)
