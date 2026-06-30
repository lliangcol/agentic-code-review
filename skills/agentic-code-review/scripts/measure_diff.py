#!/usr/bin/env python3
"""Measure cheap review-effort signals for the current Git diff."""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG: dict[str, object] = {
    "thresholds": {
        "slice_map_files": 20,
        "slice_map_changed_lines": 800,
        "not_reviewable_files": 40,
        "not_reviewable_changed_lines": 1500,
        "test_change_ratio": 0.5,
    },
    "test_path_patterns": [
        r"(^|/)(tests?|__tests__|spec)(/|$)",
        r"(\.|_)(test|spec)\.[^/]+$",
        r"fixtures?",
    ],
    "generated_path_patterns": [
        r"(^|/)(dist|build|generated|vendor)/",
        r"generated",
        r"\.lock$",
        r"package-lock\.json",
        r"pnpm-lock\.yaml",
        r"yarn\.lock",
    ],
    "gate_path_patterns": [
        r"(^|/)\.github/workflows/",
        r"(^|/)(ci|build|release)(\.|/|$)",
        r"coverage",
        r"lint",
        r"typecheck",
        r"dependabot",
        r"CODEOWNERS",
        r"gates?",
    ],
    "high_risk_path_patterns": [
        r"(^|/)(auth|authorization|permissions?|billing|payments?|money|invoices?)(/|\.|_|-|$)",
        r"(^|/)(migrations?|schemas?|user[-_]?data|deletions?|secrets?)(/|\.|_|-|$)",
        r"(^|/)(prompts?|llm|agents?|tools?)(/|\.|_|-|$)",
        r"(^|/)(production|infra|queues?|cache|retry)(/|\.|_|-|$)",
    ],
}

RISK_TERM_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(auth(?:entication|orization)?|permissions?)\b", re.I), "auth"),
    (re.compile(r"\b(billing|payments?|money|invoices?)\b", re.I), "money"),
    (re.compile(r"\b(user[-_ ]?data|personal data|pii)\b", re.I), "user-data"),
    (re.compile(r"\b(delete|deletion|destructive)\b", re.I), "deletion"),
    (re.compile(r"\b(migration|schema migration|database schema|db schema)\b", re.I), "migration"),
    (re.compile(r"\b(prompt|llm|retrieval|agent[-_ ]loop|tool[-_ ]?(?:call|action))\b", re.I), "llm-tool"),
    (re.compile(r"\b(secret|token|credential)\b", re.I), "secret"),
    (re.compile(r"\b(production|infra(?:structure)?|queue|retry|cache consistency|cache invalidat(?:e|ion))\b", re.I), "operations"),
)

DOC_LIKE_EXTENSIONS = {".md", ".markdown", ".rst", ".txt", ".csv"}
GIT_NOT_FOUND_MESSAGE = "git executable not found on PATH"


def reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


@dataclass
class FileStat:
    path: str
    insertions: int
    deletions: int
    binary: bool = False
    status: str = "M"

    @property
    def changed_lines(self) -> int:
        return self.insertions + self.deletions


@dataclass
class ReviewConfig:
    thresholds: dict[str, float]
    test_path_re: re.Pattern[str]
    generated_path_re: re.Pattern[str]
    gate_path_re: re.Pattern[str]
    high_risk_path_re: re.Pattern[str]


def compile_patterns(patterns: object, field_name: str) -> re.Pattern[str]:
    if not isinstance(patterns, list) or not patterns or not all(isinstance(item, str) for item in patterns):
        raise SystemExit(f"{field_name} must be a non-empty list of regex strings")
    try:
        return re.compile("|".join(f"(?:{pattern})" for pattern in patterns), re.I)
    except re.error as exc:
        raise SystemExit(f"{field_name} contains invalid regex: {exc}") from exc


def load_review_config(path: str | None) -> ReviewConfig:
    config = copy.deepcopy(DEFAULT_CONFIG)
    if path:
        try:
            user_config = json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject_json_constant)
        except OSError as exc:
            raise SystemExit(f"Cannot read config {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON config {path}: {exc}") from exc
        except ValueError as exc:
            raise SystemExit(f"Invalid JSON config {path}: {exc}") from exc
        if not isinstance(user_config, dict):
            raise SystemExit("Config root must be a JSON object")

        for key, value in user_config.items():
            if key == "thresholds":
                if not isinstance(value, dict):
                    raise SystemExit("thresholds must be a JSON object")
                merged = dict(config["thresholds"])
                merged.update(value)
                config["thresholds"] = merged
            elif key in {
                "test_path_patterns",
                "generated_path_patterns",
                "gate_path_patterns",
                "high_risk_path_patterns",
            }:
                config[key] = value
            else:
                raise SystemExit(f"Unsupported config key: {key}")

    thresholds = config["thresholds"]
    if not isinstance(thresholds, dict):
        raise SystemExit("thresholds must be a JSON object")
    required_thresholds = {
        "slice_map_files",
        "slice_map_changed_lines",
        "not_reviewable_files",
        "not_reviewable_changed_lines",
        "test_change_ratio",
    }
    missing = sorted(required_thresholds - set(thresholds))
    if missing:
        raise SystemExit(f"Missing threshold keys: {', '.join(missing)}")
    numeric_thresholds: dict[str, float] = {}
    for key in sorted(required_thresholds):
        value = thresholds[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
            raise SystemExit(f"Threshold {key} must be numeric")
        numeric_thresholds[key] = float(value)

    return ReviewConfig(
        thresholds=numeric_thresholds,
        test_path_re=compile_patterns(config["test_path_patterns"], "test_path_patterns"),
        generated_path_re=compile_patterns(config["generated_path_patterns"], "generated_path_patterns"),
        gate_path_re=compile_patterns(config["gate_path_patterns"], "gate_path_patterns"),
        high_risk_path_re=compile_patterns(config["high_risk_path_patterns"], "high_risk_path_patterns"),
    )


def run_git(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise SystemExit(GIT_NOT_FOUND_MESSAGE) from exc
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout


def diff_prefix(args: argparse.Namespace) -> list[str]:
    if args.base:
        return ["diff", args.base]
    if args.staged:
        return ["diff", "--cached"]
    return ["diff"]


def normalize_numstat_path(path: str) -> str:
    """Return the post-change path for Git rename/copy numstat entries."""
    if " => " not in path:
        return path
    if "{" in path and "}" in path:
        before, rest = path.split("{", 1)
        inside, after = rest.split("}", 1)
        return before + inside.split(" => ", 1)[1] + after
    return path.split(" => ", 1)[1]


def parse_numstat(args: argparse.Namespace) -> dict[str, FileStat]:
    output = run_git([*diff_prefix(args), "--numstat", "--"])
    stats: dict[str, FileStat] = {}
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added, deleted, path = parts[0], parts[1], normalize_numstat_path(parts[2])
        binary = added == "-" or deleted == "-"
        stats[path] = FileStat(
            path=path,
            insertions=0 if binary else int(added),
            deletions=0 if binary else int(deleted),
            binary=binary,
        )
    return stats


def apply_name_status(args: argparse.Namespace, stats: dict[str, FileStat]) -> None:
    output = run_git([*diff_prefix(args), "--name-status", "--"])
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0]
        path = parts[2] if (status.startswith("R") or status.startswith("C")) and len(parts) >= 3 else parts[-1]
        if path in stats:
            stats[path].status = status
        else:
            stats[path] = FileStat(path=path, insertions=0, deletions=0, status=status)


def list_untracked() -> list[str]:
    output = run_git(["ls-files", "--others", "--exclude-standard"])
    return [line for line in output.splitlines() if line]


def classify(paths: list[str], pattern: re.Pattern[str]) -> list[str]:
    return sorted(path for path in paths if pattern.search(path.replace("\\", "/")))


def is_doc_like_path(path: str) -> bool:
    return Path(path.replace("\\", "/")).suffix.lower() in DOC_LIKE_EXTENSIONS


def detect_risk_terms(path: str, changed_line: str) -> list[str]:
    if is_doc_like_path(path):
        return []
    return sorted({label for pattern, label in RISK_TERM_RULES if pattern.search(changed_line)})


def scan_diff_risk_terms(args: argparse.Namespace) -> dict[str, list[str]]:
    output = run_git([*diff_prefix(args), "--unified=0", "--no-ext-diff", "--"])
    current_path: str | None = None
    old_path: str | None = None
    hits: dict[str, set[str]] = {}

    for line in output.splitlines():
        if line.startswith("diff --git "):
            current_path = None
            old_path = None
            parts = line.split(" b/", 1)
            if len(parts) == 2:
                current_path = parts[1]
            continue
        if line.startswith("--- a/"):
            old_path = line.removeprefix("--- a/")
            continue
        if line.startswith("--- /dev/null"):
            old_path = None
            continue
        if line.startswith("+++ b/"):
            current_path = line.removeprefix("+++ b/")
            continue
        if line.startswith("+++ /dev/null"):
            current_path = old_path
            continue
        if (
            not current_path
            or not line
            or line.startswith(("+++", "---", "@@", "index ", "new file ", "deleted file ", "similarity ", "rename "))
            or line[0] not in "+-"
        ):
            continue

        terms = detect_risk_terms(current_path, line[1:])
        if terms:
            hits.setdefault(current_path, set()).update(terms)

    return {path: sorted(terms) for path, terms in sorted(hits.items())}


def build_report(args: argparse.Namespace) -> dict[str, object]:
    config = load_review_config(args.config)
    stats = parse_numstat(args)
    apply_name_status(args, stats)
    files = sorted(stats.values(), key=lambda item: item.path)
    paths = [item.path for item in files]
    untracked = [] if args.no_untracked else list_untracked()
    all_paths = sorted(set(paths + untracked))

    changed_lines = sum(item.changed_lines for item in files)
    test_paths = classify(all_paths, config.test_path_re)
    generated_paths = classify(all_paths, config.generated_path_re)
    gate_paths = classify(all_paths, config.gate_path_re)
    risk_symbol_terms = scan_diff_risk_terms(args)
    risk_path_matches = {
        path
        for path in classify(all_paths, config.high_risk_path_re)
        if not is_doc_like_path(path)
    }
    risk_paths = sorted(risk_path_matches | set(risk_symbol_terms))
    binary_paths = sorted(item.path for item in files if item.binary)
    test_lines = sum(item.changed_lines for item in files if item.path in test_paths)
    test_ratio = round(test_lines / changed_lines, 3) if changed_lines else 0

    warnings: list[str] = []
    if len(all_paths) > config.thresholds["not_reviewable_files"] or changed_lines > config.thresholds["not_reviewable_changed_lines"]:
        warnings.append("large-diff-not-reviewable-threshold")
    elif len(all_paths) > config.thresholds["slice_map_files"] or changed_lines > config.thresholds["slice_map_changed_lines"]:
        warnings.append("slice-map-recommended")
    if test_ratio > config.thresholds["test_change_ratio"]:
        warnings.append("tests-dominate-diff")
    if generated_paths and len(set(all_paths) - set(generated_paths)) > 0:
        warnings.append("generated-mixed-with-behavior")
    if gate_paths:
        warnings.append("ci-gate-review-required")
    if risk_paths:
        warnings.append("risk-tier-escalation-required")
    if untracked:
        warnings.append("untracked-files-present")

    return {
        "mode": "base" if args.base else "staged" if args.staged else "working-tree",
        "base": args.base,
        "config": args.config,
        "files_changed": len(all_paths),
        "tracked_files_changed": len(paths),
        "untracked_files": untracked,
        "insertions": sum(item.insertions for item in files),
        "deletions": sum(item.deletions for item in files),
        "changed_lines": changed_lines,
        "binary_files": binary_paths,
        "test_files": test_paths,
        "test_changed_lines": test_lines,
        "test_change_ratio": test_ratio,
        "generated_or_vendor_files": generated_paths,
        "ci_gate_files": gate_paths,
        "risk_signal_files": risk_paths,
        "risk_signal_terms": risk_symbol_terms,
        "warnings": warnings,
    }


def print_markdown(report: dict[str, object]) -> None:
    print("# Diff Measurement")
    print()
    print(f"- Mode: `{report['mode']}`")
    if report.get("base"):
        print(f"- Base: `{report['base']}`")
    if report.get("config"):
        print(f"- Config: `{report['config']}`")
    print(f"- Files changed: {report['files_changed']} ({report['tracked_files_changed']} tracked)")
    print(f"- Lines changed: {report['changed_lines']} (+{report['insertions']} / -{report['deletions']})")
    print(f"- Test-change ratio: {report['test_change_ratio']}")
    for key, title in [
        ("warnings", "Warnings"),
        ("risk_signal_files", "Risk Signal Files"),
        ("risk_signal_terms", "Risk Signal Terms"),
        ("ci_gate_files", "CI Gate Files"),
        ("generated_or_vendor_files", "Generated Or Vendor Files"),
        ("test_files", "Test Files"),
        ("binary_files", "Binary Files"),
        ("untracked_files", "Untracked Files"),
    ]:
        values = report.get(key) or []
        if values:
            print()
            print(f"## {title}")
            if isinstance(values, dict):
                for value, terms in values.items():
                    print(f"- `{value}`: {', '.join(f'`{term}`' for term in terms)}")
            else:
                for value in values:
                    print(f"- `{value}`")


def build_error_report(message: str) -> dict[str, object]:
    return {
        "schema_version": "diff-measurement-error-v1",
        "ok": False,
        "errors": [message],
    }


def print_error(message: str, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(build_error_report(message), indent=2, ensure_ascii=False))
    else:
        print(message, file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure cheap review-effort signals for a Git diff.")
    parser.add_argument("--base", help="Compare working tree or HEAD against this Git revision.")
    parser.add_argument("--staged", action="store_true", help="Measure staged changes instead of the working tree.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--config", help="Optional JSON config overriding thresholds or path patterns.")
    parser.add_argument("--no-untracked", action="store_true", help="Do not include untracked files in path classification.")
    args = parser.parse_args()

    if args.base and args.staged:
        if args.format == "json":
            print_error("--base and --staged cannot be used together", args.format)
            return 2
        parser.error("--base and --staged cannot be used together")

    try:
        run_git(["rev-parse", "--show-toplevel"])
    except SystemExit as exc:
        message = str(exc)
        if message == GIT_NOT_FOUND_MESSAGE:
            print_error(message, args.format)
        else:
            print_error("measure_diff.py must run inside a Git repository", args.format)
        return 2

    try:
        report = build_report(args)
    except SystemExit as exc:
        message = str(exc) or "measure_diff.py failed"
        print_error(message, args.format)
        return 1

    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_markdown(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
