#!/usr/bin/env python3
"""Validate review-capacity metrics CSV files without external dependencies."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EXTRA_COLUMNS_KEY = "__extra_columns__"


def load_schema(path: Path) -> dict[str, Any]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Cannot read schema {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON schema {path}: {exc}") from exc
    if not isinstance(schema, dict):
        raise SystemExit("Schema root must be an object")
    return schema


def parse_number(value: str, column: str, row_num: int) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"row {row_num}: {column} must be a number") from exc


def parse_integer(value: str, column: str, row_num: int) -> int:
    if not re.fullmatch(r"-?\d+", value):
        raise ValueError(f"row {row_num}: {column} must be an integer")
    return int(value)


def parse_date(value: str, column: str, row_num: int) -> date:
    if not DATE_RE.fullmatch(value):
        raise ValueError(f"row {row_num}: {column} must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"row {row_num}: {column} must be a real calendar date") from exc


def validate_value(value: str, column: str, rules: dict[str, Any], row_num: int) -> None:
    expected_type = rules.get("type")
    if expected_type == "string":
        if rules.get("minLength", 0) and not value:
            raise ValueError(f"row {row_num}: {column} must not be empty")
        if rules.get("format") == "date":
            parse_date(value, column, row_num)
        return

    if expected_type == "integer":
        number: float | int = parse_integer(value, column, row_num)
    elif expected_type == "number":
        number = parse_number(value, column, row_num)
    else:
        return

    minimum = rules.get("minimum")
    maximum = rules.get("maximum")
    if minimum is not None and number < minimum:
        raise ValueError(f"row {row_num}: {column} must be >= {minimum}")
    if maximum is not None and number > maximum:
        raise ValueError(f"row {row_num}: {column} must be <= {maximum}")


def validate_row_constraints(row: dict[str, str], row_num: int) -> list[str]:
    errors: list[str] = []

    date_columns = ["period_start", "period_end"]
    if all(row.get(column) is not None for column in date_columns):
        try:
            period_start = parse_date(row["period_start"], "period_start", row_num)
            period_end = parse_date(row["period_end"], "period_end", row_num)
            if period_start > period_end:
                errors.append(f"row {row_num}: period_start must be <= period_end")
        except ValueError:
            pass

    count_columns = [
        "change_count",
        "zero_review_merges",
        "not_reviewable_count",
        "gate_failure_count",
        "agent_pr_abandonment_count",
    ]
    if all(row.get(column) is not None for column in count_columns):
        try:
            change_count = parse_integer(row["change_count"], "change_count", row_num)
            for column in count_columns[1:]:
                value = parse_integer(row[column], column, row_num)
                if value > change_count:
                    errors.append(f"row {row_num}: {column} must be <= change_count")
        except ValueError:
            pass

    overlap_columns = [
        "valid_ai_findings",
        "false_positive_ai_findings",
        "reviewer_overlap_count",
    ]
    if all(row.get(column) is not None for column in overlap_columns):
        try:
            valid = parse_integer(row["valid_ai_findings"], "valid_ai_findings", row_num)
            false_positive = parse_integer(row["false_positive_ai_findings"], "false_positive_ai_findings", row_num)
            overlap = parse_integer(row["reviewer_overlap_count"], "reviewer_overlap_count", row_num)
            if overlap > valid + false_positive:
                errors.append(
                    f"row {row_num}: reviewer_overlap_count must be <= "
                    "valid_ai_findings + false_positive_ai_findings"
                )
        except ValueError:
            pass

    return errors


def validate_csv(csv_path: Path, schema_path: Path) -> tuple[int, list[str]]:
    schema = load_schema(schema_path)
    required = schema.get("required", [])
    properties = schema.get("properties", {})
    if not isinstance(required, list) or not isinstance(properties, dict):
        raise SystemExit("Schema must define required fields and properties")

    try:
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, restkey=EXTRA_COLUMNS_KEY)
            if reader.fieldnames is None:
                raise ValueError("CSV must include a header row")

            fieldnames = reader.fieldnames
            missing = [column for column in required if column not in fieldnames]
            extra = [column for column in fieldnames if column not in properties]
            errors: list[str] = []
            if missing:
                errors.append(f"missing columns: {', '.join(missing)}")
            if extra and schema.get("additionalProperties") is False:
                errors.append(f"unexpected columns: {', '.join(extra)}")

            present_required = [column for column in required if column in fieldnames]
            row_count = 0
            for row_num, row in enumerate(reader, start=2):
                row_count += 1
                if row.get(EXTRA_COLUMNS_KEY):
                    errors.append(f"row {row_num}: has more values than header columns")
                for column in present_required:
                    value = row.get(column)
                    if value is None:
                        errors.append(f"row {row_num}: {column} is missing a value")
                        continue
                    try:
                        validate_value(value, column, properties.get(column, {}), row_num)
                    except ValueError as exc:
                        errors.append(str(exc))
                errors.extend(validate_row_constraints(row, row_num))
            return row_count, errors
    except OSError as exc:
        raise SystemExit(f"Cannot read metrics CSV {csv_path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate agentic-code-review capacity metrics CSV files.")
    default_asset_dir = Path(__file__).resolve().parents[1] / "assets"
    parser.add_argument("csv_path", nargs="?", default=default_asset_dir / "review-capacity-metrics.template.csv")
    parser.add_argument("--schema", default=default_asset_dir / "review-capacity-metrics.schema.json")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    csv_path = Path(args.csv_path)
    schema_path = Path(args.schema)
    row_count, errors = validate_csv(csv_path, schema_path)
    result = {"csv": str(csv_path), "schema": str(schema_path), "rows": row_count, "errors": errors}

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif errors:
        for error in errors:
            print(error, file=sys.stderr)
    else:
        print(f"review capacity metrics validation passed ({row_count} rows).")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
