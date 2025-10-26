from __future__ import annotations

from pathlib import Path

from packs.personal_injury.run import render_documents


def test_render_documents(tmp_path: Path, sample_payload):
    paths = render_documents(sample_payload, output=tmp_path)
    assert any(path.name.endswith("workflow_summary.json") for path in paths)
    assert all(path.exists() for path in paths)
