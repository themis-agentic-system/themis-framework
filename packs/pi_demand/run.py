"""Command-line entry point for the PI demand practice pack."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Any

from orchestrator.service import OrchestratorService


def load_matter(path: Path) -> dict[str, Any]:
    """Load matter data from YAML once the loader is implemented."""
    # TODO: parse YAML/JSON. For now return a placeholder payload.
    return {"matter_file": str(path)}


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PI demand practice pack")
    parser.add_argument("--matter", type=Path, required=True, help="Path to the matter YAML file")
    args = parser.parse_args()

    service = OrchestratorService()
    matter = load_matter(args.matter)

    result = await service.execute(matter)
    print("Execution complete:\n", result)


if __name__ == "__main__":
    asyncio.run(main())
