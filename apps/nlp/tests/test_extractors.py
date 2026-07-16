from __future__ import annotations

import json
from pathlib import Path

from app.extractors import extract_candidates

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "team_wiki_expected.json"


def test_extracts_core_acronyms_from_sample_wiki():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    wiki = ROOT / data["text_file"]
    text = wiki.read_text(encoding="utf-8")
    candidates = extract_candidates(text)
    found = {c.term for c in candidates}
    # Require most planted acronyms; allow some noise
    expected = set(data["expected_terms"])
    hits = expected & found
    recall = len(hits) / len(expected)
    assert recall >= 0.6, f"recall={recall:.2f} hits={sorted(hits)} missing={sorted(expected - found)}"
    for must in ("PIR", "GTM", "BAU"):
        assert must in found


def test_parenthetical_expansion():
    text = "Open a Written Assessment of Risk (WAR) before escalating."
    cands = extract_candidates(text)
    war = next(c for c in cands if c.term == "WAR")
    assert "Written Assessment of Risk" in (war.definition or "") or "Written Assessment of Risk" in war.aliases
