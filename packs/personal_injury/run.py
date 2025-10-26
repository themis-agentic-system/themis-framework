"""CLI utilities for personal injury practice pack."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency guard
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

from packs.personal_injury import (
    PACK_ANALYTICS_TAG,
    catalog_assets,
    load_matter,
    workflow_summary,
)
from packs.personal_injury.config import DOCUMENTS, available_documents, build_generator
from packs.personal_injury.schema import matter_summary
from packs.personal_injury.workflows import active_phase


def _load_payload(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise ValueError("PyYAML must be installed to parse YAML inputs")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    elif suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        raise ValueError("Only JSON or YAML matter files are supported")
    if not isinstance(data, dict):
        raise ValueError("Matter file must contain an object at the root")
    return data


def render_documents(matter_data: dict[str, Any], *, documents: Iterable[str] | None = None, output: Path | None = None) -> list[Path]:
    matter = load_matter(matter_data)
    phase = active_phase(matter)
    selected = list(documents or [doc.key for doc in phase.documents])
    if not selected:
        raise ValueError("No documents selected for rendering")

    output_dir = output or Path("outputs") / _slugify(matter.metadata.title)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for key in selected:
        if key not in DOCUMENTS:
            raise KeyError(f"Unknown document key '{key}'. Available: {', '.join(DOCUMENTS)}")
        generator = build_generator(key, matter)
        rendered = generator.render()
        target = output_dir / f"{key}.txt"
        target.write_text(rendered, encoding="utf-8")
        paths.append(target)

    summary_path = output_dir / "workflow_summary.json"
    summary_payload = {
        "workflow": workflow_summary(matter),
        "analytics": matter_summary(matter),
        "tags": list({tag for cfg in DOCUMENTS.values() for tag in cfg.tags} | {PACK_ANALYTICS_TAG}),
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    paths.append(summary_path)
    return paths


def build_cli(argv: list[str] | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Personal injury pack runner")
    parser.add_argument("--matter", type=Path, required=True, help="Path to matter JSON or YAML file")
    parser.add_argument("--documents", nargs="*", help="Specific document keys to render")
    parser.add_argument("--list", action="store_true", help="List available documents and exit")
    parser.add_argument("--audit", action="store_true", help="Print asset catalog and exit")
    parser.add_argument("--output", type=Path, help="Output directory for rendered documents")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_cli(argv)
    args = parser.parse_args(argv)

    if args.list:
        for config in available_documents():
            print(f"{config.key}\t{config.title}\t[{config.phase}]")
        return

    if args.audit:
        print(json.dumps(catalog_assets(), indent=2))
        return

    payload = _load_payload(args.matter)
    paths = render_documents(payload, documents=args.documents, output=args.output)
    for path in paths:
        print(f"Generated: {path}")


def _slugify(text: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in text)
    cleaned = "-".join(filter(None, cleaned.split("-")))
    return cleaned or "matter"


if __name__ == "__main__":  # pragma: no cover
    main()
