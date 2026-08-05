"""Gera Job Summary do GitHub Actions a partir do JSON do Behave."""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"
BEHAVE_JSON = REPORTS / "behave.json"


def _load_stats() -> dict[str, int]:
    stats = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
    if not BEHAVE_JSON.exists() or BEHAVE_JSON.stat().st_size == 0:
        return stats

    data = json.loads(BEHAVE_JSON.read_text(encoding="utf-8"))
    for feature in data:
        for element in feature.get("elements", []):
            if element.get("type") not in {"scenario", "scenario_outline"}:
                continue
            stats["total"] += 1
            status = element.get("status", "unknown")
            if status == "passed":
                stats["passed"] += 1
            elif status == "failed":
                stats["failed"] += 1
            else:
                stats["skipped"] += 1
    return stats


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    stats = _load_stats()
    lines = [
        "## D4Sign API Tests — Behave",
        "",
        f"- Total: **{stats['total']}**",
        f"- Passed: **{stats['passed']}**",
        f"- Failed: **{stats['failed']}**",
        f"- Skipped: **{stats['skipped']}**",
        "",
        "Artefatos em `reports/` (HTML, JSON, Allure, evidências HTTP).",
    ]
    content = "\n".join(lines) + "\n"

    summary_path = Path(os.environ.get("GITHUB_STEP_SUMMARY", REPORTS / "job_summary.md"))
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("a", encoding="utf-8") as handle:
        handle.write(content)

    print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
