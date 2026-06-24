#!/usr/bin/env python3
"""Validate batch triage JSON records without external dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CATEGORIES = {"Safe-looking", "Needs work", "High-risk", "Not reviewable"}
RISK_TIERS = {"L0", "L1", "L2", "L3", "L4", "Unknown"}
ROOT_FIELDS = {"items", "human_attention_plan"}
ITEM_FIELDS = {"id", "category", "risk_tier", "reason", "required_next_evidence", "human_owner"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON {path}: {exc}") from exc


def validate_record(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["batch triage record must be a JSON object"]

    for field in sorted(set(data) - ROOT_FIELDS):
        errors.append(f"unexpected field: {field}")

    items = data.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty array")
    else:
        seen_ids: set[str] = set()
        for index, item in enumerate(items):
            prefix = f"items[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for field in sorted(set(item) - ITEM_FIELDS):
                errors.append(f"{prefix} unexpected field: {field}")
            for field in ["id", "category", "reason", "required_next_evidence"]:
                value = item.get(field)
                if not isinstance(value, str):
                    errors.append(f"{prefix}.{field} must be a string")
            item_id = item.get("id")
            if isinstance(item_id, str):
                if not item_id.strip():
                    errors.append(f"{prefix}.id must not be empty")
                if item_id in seen_ids:
                    errors.append(f"duplicate item id: {item_id}")
                seen_ids.add(item_id)
            if item.get("category") not in CATEGORIES:
                errors.append(f"{prefix}.category must be one of {', '.join(sorted(CATEGORIES))}")
            risk_tier = item.get("risk_tier", "Unknown")
            if risk_tier not in RISK_TIERS:
                errors.append(f"{prefix}.risk_tier must be one of {', '.join(sorted(RISK_TIERS))}")
            human_owner = item.get("human_owner")
            if human_owner is not None and not isinstance(human_owner, str):
                errors.append(f"{prefix}.human_owner must be a string")
            if isinstance(item.get("reason"), str) and not item["reason"].strip():
                errors.append(f"{prefix}.reason must not be empty")

    attention_plan = data.get("human_attention_plan")
    if not isinstance(attention_plan, str) or not attention_plan.strip():
        errors.append("human_attention_plan must be a non-empty string")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate batch triage JSON records.")
    default_path = Path(__file__).resolve().parents[1] / "assets" / "batch-triage.template.json"
    parser.add_argument("record", nargs="?", default=default_path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    record_path = Path(args.record)
    errors = validate_record(load_json(record_path))
    result = {"record": str(record_path), "errors": errors}
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print("batch triage validation passed.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
