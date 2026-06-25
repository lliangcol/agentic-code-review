#!/usr/bin/env python3
"""Collect review-capacity metrics from a GitHub PR JSON export."""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_reviewer_comparison import validate_record as validate_reviewer_comparison_record


HEADER = [
    "period_start",
    "period_end",
    "repository",
    "change_count",
    "zero_review_merges",
    "median_time_to_first_review_hours",
    "median_review_duration_hours",
    "median_files_changed",
    "median_changed_lines",
    "median_test_change_ratio",
    "not_reviewable_count",
    "gate_failure_count",
    "rereview_count",
    "valid_ai_findings",
    "false_positive_ai_findings",
    "reviewer_overlap_count",
    "agent_pr_abandonment_count",
    "notes",
]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON {path}: {exc}") from exc


def parse_time(value: Any, field: str) -> datetime | None:
    if is_missing_timestamp(value):
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO timestamp string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO timestamp") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def is_missing_timestamp(value: Any) -> bool:
    return value is None or value == ""


def parse_period_date(value: str, field: str) -> date:
    if not DATE_RE.fullmatch(value):
        raise ValueError(f"{field} must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be a real calendar date") from exc


def validate_period(period_start: str, period_end: str) -> None:
    start = parse_period_date(period_start, "--period-start")
    end = parse_period_date(period_end, "--period-end")
    if start > end:
        raise ValueError("--period-start must be <= --period-end")


def hours_between(start: datetime | None, end: datetime | None) -> float | None:
    if start is None or end is None or end < start:
        return None
    return round((end - start).total_seconds() / 3600, 3)


def median(values: list[float]) -> float:
    return round(statistics.median(values), 3) if values else 0


def is_human_review(review: dict[str, Any]) -> bool:
    user = review.get("user")
    return isinstance(user, dict) and user.get("type") == "User"


def label_names(labels: Any) -> set[str]:
    if not isinstance(labels, list):
        return set()
    names: set[str] = set()
    for label in labels:
        if isinstance(label, dict):
            name = label.get("name")
        else:
            name = label
        if name is not None:
            names.add(str(name).lower())
    return names


def extract_prs(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ["pull_requests", "prs", "items"]:
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    raise SystemExit("Input must be a JSON array or an object with pull_requests/prs/items")


def extract_adjudication_records(data: Any) -> list[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ["reviewer_comparisons", "adjudications", "items"]:
            value = data.get(key)
            if isinstance(value, list):
                return value
        return [data]
    raise ValueError("adjudication input must be a JSON object, an array, or an object with reviewer_comparisons/adjudications/items")


def validate_adjudication_records(records: list[Any], source: str) -> list[dict[str, Any]]:
    valid_records: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, record in enumerate(records):
        record_errors = validate_reviewer_comparison_record(record)
        if record_errors:
            errors.extend(f"{source}[{index}]: {error}" for error in record_errors)
        elif isinstance(record, dict):
            valid_records.append(record)

    if errors:
        raise ValueError("adjudication validation failed: " + "; ".join(errors))
    return valid_records


def count_reviewer_findings(record: dict[str, Any], field: str) -> int:
    total = 0
    reviewers = record.get("reviewers", [])
    if not isinstance(reviewers, list):
        raise ValueError("adjudication.reviewers must be an array")
    for reviewer_index, reviewer in enumerate(reviewers):
        if not isinstance(reviewer, dict):
            raise ValueError(f"adjudication.reviewers[{reviewer_index}] must be an object")
        value = reviewer.get(field, 0)
        if type(value) is not int or value < 0:
            raise ValueError(f"adjudication.reviewers[{reviewer_index}].{field} must be a non-negative integer")
        total += value
    return total


def count_string_items(record: dict[str, Any], field: str) -> int:
    value = record.get(field, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"adjudication.{field} must be an array of strings")
    return len(set(value))


def summarize_ai_quality(adjudications: list[dict[str, Any]]) -> dict[str, int]:
    valid_ai_findings = 0
    false_positive_ai_findings = 0
    reviewer_overlap_count = 0

    for record in adjudications:
        valid = count_reviewer_findings(record, "valid_findings")
        false_positive = count_reviewer_findings(record, "false_positive_findings")
        unique_adjudicated = count_string_items(record, "confirmed_findings") + count_string_items(record, "rejected_findings")
        total_classified = valid + false_positive

        valid_ai_findings += valid
        false_positive_ai_findings += false_positive
        reviewer_overlap_count += max(0, total_classified - unique_adjudicated)

    return {
        "valid_ai_findings": valid_ai_findings,
        "false_positive_ai_findings": false_positive_ai_findings,
        "reviewer_overlap_count": reviewer_overlap_count,
    }


def collect(
    prs: list[dict[str, Any]],
    repository: str,
    period_start: str,
    period_end: str,
    adjudications: list[dict[str, Any]] | None = None,
) -> dict[str, object]:
    first_review_hours: list[float] = []
    review_duration_hours: list[float] = []
    files_changed: list[float] = []
    changed_lines: list[float] = []
    test_ratios: list[float] = []
    zero_review_merges = 0
    rereview_count = 0
    gate_failure_count = 0
    not_reviewable_count = 0
    agent_pr_abandonment_count = 0

    for pr_index, pr in enumerate(prs):
        prefix = f"pull_requests[{pr_index}]"
        created = parse_time(pr.get("created_at"), f"{prefix}.created_at")
        resolution_field = next(
            (field for field in ["merged_at", "closed_at"] if not is_missing_timestamp(pr.get(field))),
            None,
        )
        resolved_at = parse_time(pr.get(resolution_field), f"{prefix}.{resolution_field}") if resolution_field else None
        reviews = [review for review in pr.get("reviews", []) if isinstance(review, dict)]
        human_reviews = [(review_index, review) for review_index, review in enumerate(reviews) if is_human_review(review)]
        human_review_times = sorted(
            filter(
                None,
                (
                    parse_time(review.get("submitted_at"), f"{prefix}.reviews[{review_index}].submitted_at")
                    for review_index, review in human_reviews
                ),
            )
        )

        if not human_reviews and not is_missing_timestamp(pr.get("merged_at")):
            zero_review_merges += 1
        if human_review_times:
            first = hours_between(created, human_review_times[0])
            if first is not None:
                first_review_hours.append(first)
            duration = hours_between(human_review_times[0], resolved_at)
            if duration is not None:
                review_duration_hours.append(duration)
        if len(human_reviews) > 1:
            rereview_count += len(human_reviews) - 1

        files_changed.append(float(pr.get("changed_files", 0) or 0))
        additions = float(pr.get("additions", 0) or 0)
        deletions = float(pr.get("deletions", 0) or 0)
        changed = additions + deletions
        changed_lines.append(changed)
        test_changed = float(pr.get("test_changed_lines", 0) or 0)
        test_ratios.append(round(min(test_changed / changed, 1), 3) if changed else 0)

        labels = label_names(pr.get("labels", []))
        if "not reviewable" in labels:
            not_reviewable_count += 1
        if "gate failure" in labels or "ci failure" in labels:
            gate_failure_count += 1
        if "agent pr abandonment" in labels:
            agent_pr_abandonment_count += 1

    ai_quality = summarize_ai_quality(adjudications or [])
    notes = "Derived from GitHub PR JSON export; AI finding quality fields require reviewer adjudication."
    if adjudications:
        notes = f"Derived from GitHub PR JSON export and {len(adjudications)} reviewer adjudication record(s)."

    return {
        "period_start": period_start,
        "period_end": period_end,
        "repository": repository,
        "change_count": len(prs),
        "zero_review_merges": zero_review_merges,
        "median_time_to_first_review_hours": median(first_review_hours),
        "median_review_duration_hours": median(review_duration_hours),
        "median_files_changed": median(files_changed),
        "median_changed_lines": median(changed_lines),
        "median_test_change_ratio": median(test_ratios),
        "not_reviewable_count": not_reviewable_count,
        "gate_failure_count": gate_failure_count,
        "rereview_count": rereview_count,
        "valid_ai_findings": ai_quality["valid_ai_findings"],
        "false_positive_ai_findings": ai_quality["false_positive_ai_findings"],
        "reviewer_overlap_count": ai_quality["reviewer_overlap_count"],
        "agent_pr_abandonment_count": agent_pr_abandonment_count,
        "notes": notes,
    }


def build_error_report(message: str) -> dict[str, object]:
    return {
        "schema_version": "github-metrics-error-v1",
        "ok": False,
        "errors": [message],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect review-capacity metrics from GitHub PR JSON.")
    parser.add_argument("input_json")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--period-start", required=True)
    parser.add_argument("--period-end", required=True)
    parser.add_argument(
        "--adjudication-json",
        action="append",
        default=[],
        help="Optional reviewer-comparison/adjudication JSON. May be passed multiple times.",
    )
    parser.add_argument("--format", choices=["csv", "json"], default="csv")
    args = parser.parse_args()

    try:
        validate_period(args.period_start, args.period_end)
        prs = extract_prs(load_json(Path(args.input_json)))
        adjudications: list[dict[str, Any]] = []
        for adjudication_path in args.adjudication_json:
            records = extract_adjudication_records(load_json(Path(adjudication_path)))
            adjudications.extend(validate_adjudication_records(records, str(adjudication_path)))
        row = collect(prs, args.repository, args.period_start, args.period_end, adjudications)
    except (SystemExit, ValueError) as exc:
        message = str(exc) or "collect_github_metrics.py failed"
        if args.format == "json":
            print(json.dumps(build_error_report(message), indent=2, ensure_ascii=False))
        else:
            print(message, file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=HEADER, lineterminator="\n")
        writer.writeheader()
        writer.writerow(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
