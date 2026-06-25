#!/usr/bin/env python3
"""Validate reviewer comparison records without external dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_FIELDS = {
    "repository",
    "revision",
    "risk_tier",
    "human_owner",
    "reviewers",
    "confirmed_findings",
    "rejected_findings",
    "residual_human_judgment",
}
REVIEWER_FIELDS = {
    "name",
    "tool_or_model",
    "prompt_or_role",
    "findings",
    "valid_findings",
    "false_positive_findings",
    "notes",
}
RISK_TIERS = {"L0", "L1", "L2", "L3", "L4"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON {path}: {exc}") from exc


def is_non_negative_integer(value: Any) -> bool:
    return type(value) is int and value >= 0


def validate_record(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["record must be a JSON object"]

    for field in sorted(set(data) - ROOT_FIELDS):
        errors.append(f"unexpected field: {field}")

    for field in [
        "repository",
        "revision",
        "risk_tier",
        "human_owner",
        "reviewers",
        "confirmed_findings",
        "rejected_findings",
        "residual_human_judgment",
    ]:
        if field not in data:
            errors.append(f"missing field: {field}")

    for field in ["repository", "revision", "human_owner"]:
        value = data.get(field)
        if not isinstance(value, str) or not value:
            errors.append(f"{field} must be a non-empty string")

    if data.get("risk_tier") not in RISK_TIERS:
        errors.append("risk_tier must be one of L0-L4")

    reviewers = data.get("reviewers")
    if not isinstance(reviewers, list) or not reviewers:
        errors.append("reviewers must be a non-empty array")
    else:
        for index, reviewer in enumerate(reviewers):
            prefix = f"reviewers[{index}]"
            if not isinstance(reviewer, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for field in sorted(set(reviewer) - REVIEWER_FIELDS):
                errors.append(f"{prefix} unexpected field: {field}")
            for field in ["name", "tool_or_model", "prompt_or_role", "findings", "valid_findings", "false_positive_findings"]:
                if field not in reviewer:
                    errors.append(f"{prefix} missing field: {field}")
            for field in ["name", "tool_or_model", "prompt_or_role"]:
                value = reviewer.get(field)
                if not isinstance(value, str) or not value:
                    errors.append(f"{prefix}.{field} must be a non-empty string")
            notes = reviewer.get("notes")
            if notes is not None and not isinstance(notes, str):
                errors.append(f"{prefix}.notes must be a string")
            for field in ["findings", "valid_findings", "false_positive_findings"]:
                value = reviewer.get(field)
                if not is_non_negative_integer(value):
                    errors.append(f"{prefix}.{field} must be a non-negative integer")
            findings = reviewer.get("findings")
            valid = reviewer.get("valid_findings")
            false_positive = reviewer.get("false_positive_findings")
            if (
                is_non_negative_integer(findings)
                and is_non_negative_integer(valid)
                and is_non_negative_integer(false_positive)
            ):
                if valid + false_positive > findings:
                    errors.append(f"{prefix}: valid_findings + false_positive_findings must not exceed findings")

    for field in ["confirmed_findings", "rejected_findings", "residual_human_judgment"]:
        value = data.get(field, [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            errors.append(f"{field} must be an array of strings")

    return errors


def build_error_report(message: str) -> dict[str, object]:
    return {
        "schema_version": "reviewer-comparison-validation-error-v1",
        "ok": False,
        "errors": [message],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate reviewer comparison JSON records.")
    default_asset_dir = Path(__file__).resolve().parents[1] / "assets"
    parser.add_argument("record", nargs="?", default=default_asset_dir / "reviewer-comparison.example.json")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    record_path = Path(args.record)
    try:
        record = load_json(record_path)
    except SystemExit as exc:
        message = str(exc) or "validate_reviewer_comparison.py failed"
        if args.format == "json":
            print(json.dumps(build_error_report(message), indent=2, ensure_ascii=False))
        else:
            print(message, file=sys.stderr)
        return 1

    errors = validate_record(record)
    result = {"record": str(record_path), "errors": errors}
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print("reviewer comparison validation passed.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
