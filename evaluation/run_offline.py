from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.mermaid import validate_mermaid
from backend.schemas import ChatResponse

ROOT = Path(__file__).parents[1]


def deterministic_fixture(case: dict[str, Any]) -> dict[str, Any]:
    product = case["product_type"]
    return {
        "request_id": f"eval-{case['id']}",
        "thread_id": f"eval-{case['id']}",
        "output_requirements": f"# Requirements\n\nSupport the core {product} workflow.",
        "output_design": f"# Design\n\nA service-oriented design for {product}.",
        "output_code": "flowchart LR\n  Client --> API\n  API --> Service\n  Service --> Store[(Data Store)]",
        "critique_iterations": 2,
        "estimated_monthly_cost_usd": None,
        "cost_breakdown": [],
    }


def main() -> None:
    cases = json.loads((ROOT / "evaluation" / "dataset.json").read_text(encoding="utf-8"))
    started = time.perf_counter()
    rows: list[dict[str, Any]] = []
    for case in cases:
        output = deterministic_fixture(case)
        ChatResponse.model_validate(output)
        validate_mermaid(output["output_code"])
        rows.append(
            {
                "id": case["id"],
                "schema_valid": True,
                "mermaid_valid": True,
                "required_section_coverage": 1.0,
                "critique_iterations": output["critique_iterations"],
            }
        )

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": "offline deterministic contract fixture",
        "live_model_calls": 0,
        "paid_api_cost_usd": 0,
        "case_count": len(rows),
        "schema_valid_rate": sum(row["schema_valid"] for row in rows) / len(rows),
        "mermaid_valid_rate": sum(row["mermaid_valid"] for row in rows) / len(rows),
        "required_section_coverage": sum(row["required_section_coverage"] for row in rows)
        / len(rows),
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
        "results": rows,
        "limitations": [
            "This checks contracts and evaluator plumbing, not live-model design quality.",
            "Latency and cost are intentionally not reported for a live provider.",
        ],
    }
    output_path = ROOT / "evaluation" / "results" / "offline-contract.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {key: report[key] for key in ("case_count", "schema_valid_rate", "mermaid_valid_rate")}
        )
    )


if __name__ == "__main__":
    main()
