#!/usr/bin/env python3
"""Validate hostile-input fixture JSON files without external dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_FIELDS = {"fixtures"}
FIXTURE_FIELDS = {"id", "surface", "input", "expected_result"}


def build_error_report(message: str) -> dict[str, object]:
    return {
        "schema_version": "hostile-fixtures-validation-error-v1",
        "ok": False,
        "errors": [message],
    }


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON {path}: {exc}") from exc


def validate_fixtures(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["fixtures file must be a JSON object"]

    for field in sorted(set(data) - ROOT_FIELDS):
        errors.append(f"unexpected field: {field}")

    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        errors.append("fixtures must be a non-empty array")
        return errors

    seen_ids: set[str] = set()
    for index, fixture in enumerate(fixtures):
        prefix = f"fixtures[{index}]"
        if not isinstance(fixture, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in sorted(set(fixture) - FIXTURE_FIELDS):
            errors.append(f"{prefix} unexpected field: {field}")
        for field in ["id", "surface", "input", "expected_result"]:
            value = fixture.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}.{field} must be a non-empty string")
        fixture_id = fixture.get("id")
        if isinstance(fixture_id, str):
            if fixture_id in seen_ids:
                errors.append(f"duplicate fixture id: {fixture_id}")
            seen_ids.add(fixture_id)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate hostile-input fixture JSON files.")
    default_path = Path(__file__).resolve().parents[1] / "assets" / "hostile-input-fixtures.json"
    parser.add_argument("fixtures", nargs="?", default=default_path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    fixture_path = Path(args.fixtures)
    try:
        data = load_json(fixture_path)
    except SystemExit as exc:
        message = str(exc)
        if args.format == "json":
            print(json.dumps(build_error_report(message), indent=2, ensure_ascii=False))
        else:
            print(message, file=sys.stderr)
        return 1

    errors = validate_fixtures(data)
    result = {"fixtures": str(fixture_path), "errors": errors}
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print("hostile-input fixture validation passed.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
