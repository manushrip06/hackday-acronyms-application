"""Eval helpers for NLP fine-tuning — compare extractor output to fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.extractors import extract_candidates


def precision_recall(found: set[str], expected: set[str]) -> tuple[float, float]:
    if not found:
        return 0.0, 0.0
    hits = found & expected
    precision = len(hits) / len(found) if found else 0.0
    recall = len(hits) / len(expected) if expected else 0.0
    return precision, recall


def eval_fixture(fixture_path: Path, repo_root: Path) -> dict:
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    text = (repo_root / data["text_file"]).read_text(encoding="utf-8")
    candidates = extract_candidates(text)
    found = {c.term for c in candidates}
    expected = set(data["expected_terms"])
    p, r = precision_recall(found, expected)
    return {
        "precision": p,
        "recall": r,
        "found": sorted(found),
        "missing": sorted(expected - found),
        "extra": sorted(found - expected),
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "team_wiki_expected.json"
    print(json.dumps(eval_fixture(fixture, root), indent=2))
