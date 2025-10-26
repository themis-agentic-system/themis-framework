from __future__ import annotations

import json
from pathlib import Path

from packs.personal_injury import catalog_assets
from packs.personal_injury.config import DOCUMENTS
from packs.personal_injury.run import render_documents
FIXTURE_DIR = Path(__file__).resolve().parents[2] / "packs" / "personal_injury" / "fixtures"


def _load_payload(name: str) -> dict[str, object]:
    path = FIXTURE_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_render_documents_full_packet(tmp_path: Path) -> None:
    payload = _load_payload("sample_matter.json")
    paths = render_documents(payload, documents=DOCUMENTS.keys(), output=tmp_path)
    generated = {path.name for path in paths}
    for key in DOCUMENTS:
        assert f"{key}.txt" in generated
    assert "workflow_summary.json" in generated


def test_catalog_assets_lists_documents() -> None:
    catalog = catalog_assets()
    assert set(catalog["documents"].keys()) == set(DOCUMENTS.keys())
    assert "schema_required" in catalog
    assert "phases" in catalog
