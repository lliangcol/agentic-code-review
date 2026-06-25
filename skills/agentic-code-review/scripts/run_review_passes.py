#!/usr/bin/env python3
"""Run optional configured review passes through pluggable providers."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ASSET_DIR = Path(__file__).resolve().parents[1] / "assets"
MEASURE_DIFF = Path(__file__).resolve().with_name("measure_diff.py")
DEFAULT_CONFIG = ASSET_DIR / "review-runner.config.example.json"
ALLOWED_VERDICTS = {"Ready", "Not ready", "Needs confirmation", "Not reviewable"}
ALLOWED_RISK_TIERS = {"L0", "L1", "L2", "L3", "L4"}
STRUCTURED_REVIEW_FIELD_TYPES = {
    "verdict": str,
    "risk_tier": str,
    "findings": list,
    "needs_confirmation": list,
    "validation": list,
    "ai_review_evidence": dict,
    "residual_risk": list,
}
SENSITIVE_TEXT_PATTERNS = [
    (
        re.compile(r"\b([A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)[A-Z0-9_]*\s*[:=]\s*)([^\s,;\"']+)", re.IGNORECASE),
        r"\1[redacted]",
    ),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE), "Bearer [redacted]"),
    (re.compile(r"\bsk-[A-Za-z0-9]{12,}\b"), "sk-[redacted]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{12,}\b"), "gh[redacted]"),
]


class ConfigError(ValueError):
    """Raised when runner configuration is invalid."""


@dataclass
class ProviderResult:
    provider: str
    model: str
    status: str
    output: str
    attempts: list[dict[str, object]]
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON {path}: {exc}") from exc


def as_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a JSON object")
    return value


def as_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{name} must be a non-empty string")
    return value


def as_non_negative_number(value: Any, name: str) -> float:
    if not isinstance(value, (int, float)) or value < 0:
        raise ConfigError(f"{name} must be a non-negative number")
    return float(value)


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def relative_to_config(path_value: str, config_path: Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return config_path.parent / path


def load_prompt_manifest(config: dict[str, Any], config_path: Path, override: str | None) -> tuple[dict[str, Any], Path]:
    manifest_value = override or as_string(config.get("prompt_manifest"), "prompt_manifest")
    manifest_path = relative_to_config(manifest_value, config_path)
    manifest = as_object(load_json(manifest_path), "prompt manifest")
    return manifest, manifest_path


def prompt_templates(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    templates = manifest.get("templates")
    if not isinstance(templates, list) or not templates:
        raise ConfigError("prompt manifest templates must be a non-empty array")
    result: dict[str, dict[str, Any]] = {}
    for index, template in enumerate(templates):
        template_obj = as_object(template, f"templates[{index}]")
        template_id = as_string(template_obj.get("id"), f"templates[{index}].id")
        as_string(template_obj.get("version"), f"templates[{index}].version")
        as_string(template_obj.get("template"), f"templates[{index}].template")
        result[template_id] = template_obj
    return result


def output_contract(manifest: dict[str, Any], contract_id: str) -> dict[str, Any]:
    contracts = as_object(manifest.get("output_contracts"), "output_contracts")
    contract = as_object(contracts.get(contract_id), f"output_contracts.{contract_id}")
    as_string(contract.get("version"), f"output_contracts.{contract_id}.version")
    as_string(contract.get("instructions"), f"output_contracts.{contract_id}.instructions")
    contract_required_fields(contract, contract_id)
    return contract


def contract_required_fields(contract: dict[str, Any], contract_id: str) -> list[str]:
    fields = contract.get("required_fields")
    if not isinstance(fields, list) or not fields or not all(isinstance(item, str) and item for item in fields):
        raise ConfigError(f"output_contracts.{contract_id}.required_fields must be a non-empty array of strings")
    return fields


def enabled_passes(config: dict[str, Any]) -> list[dict[str, Any]]:
    passes = config.get("review_passes")
    if not isinstance(passes, list) or not passes:
        raise ConfigError("review_passes must be a non-empty array")
    enabled: list[dict[str, Any]] = []
    for index, item in enumerate(passes):
        review_pass = as_object(item, f"review_passes[{index}]")
        if review_pass.get("enabled", True):
            as_string(review_pass.get("id"), f"review_passes[{index}].id")
            as_string(review_pass.get("template_id"), f"review_passes[{index}].template_id")
            enabled.append(review_pass)
    if not enabled:
        raise ConfigError("at least one review pass must be enabled")
    return enabled


def load_context(paths: list[str]) -> str:
    parts: list[str] = []
    for item in paths:
        path = Path(item)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ConfigError(f"Cannot read context file {path}: {exc}") from exc
        parts.append(f"--- {path} ---\n{text}")
    return "\n\n".join(parts) if parts else "No extra context supplied."


def render_prompt(template: dict[str, Any], variables: dict[str, str]) -> str:
    text = as_string(template.get("template"), "template")
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def truncate_output(text: str, max_chars: int) -> tuple[str, bool]:
    if max_chars <= 0 or len(text) <= max_chars:
        return text, False
    return text[:max_chars] + "\n[truncated]", True


def redact_sensitive_text(text: str) -> str:
    redacted = text
    for pattern, replacement in SENSITIVE_TEXT_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def provider_pricing(provider: dict[str, Any]) -> tuple[float, float]:
    pricing = provider.get("pricing", {})
    if pricing is None:
        pricing = {}
    pricing_obj = as_object(pricing, "provider.pricing")
    return (
        as_non_negative_number(pricing_obj.get("input_per_million_tokens_usd", 0), "pricing.input_per_million_tokens_usd"),
        as_non_negative_number(pricing_obj.get("output_per_million_tokens_usd", 0), "pricing.output_per_million_tokens_usd"),
    )


def estimate_cost(provider: dict[str, Any], input_tokens: int, output_tokens: int) -> float:
    input_price, output_price = provider_pricing(provider)
    return round((input_tokens / 1_000_000 * input_price) + (output_tokens / 1_000_000 * output_price), 8)


def mock_output(pass_id: str, template: dict[str, Any], provider_name: str) -> str:
    payload = {
        "verdict": "Needs confirmation",
        "risk_tier": "L2",
        "findings": [],
        "needs_confirmation": [f"{pass_id} used mock provider {provider_name}; no live model judgment was performed."],
        "validation": [],
        "ai_review_evidence": {
            "reviewer": template.get("role", pass_id),
            "provider": provider_name,
            "mode": "mock",
        },
        "residual_risk": ["Mock output is suitable for smoke tests only."],
    }
    return json.dumps(payload, ensure_ascii=False)


def run_command_provider(provider: dict[str, Any], prompt: str) -> subprocess.CompletedProcess[str]:
    command = provider.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
        raise ConfigError("command provider command must be a non-empty array of strings")
    timeout = as_non_negative_number(provider.get("timeout_seconds", 120), "timeout_seconds")
    return subprocess.run(
        command,
        input=prompt,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        shell=False,
    )


def execute_provider(
    provider_name: str,
    providers: dict[str, Any],
    prompt: str,
    pass_id: str,
    template: dict[str, Any],
    dry_run: bool,
    max_output_chars: int,
) -> ProviderResult:
    attempts: list[dict[str, object]] = []
    visited: set[str] = set()
    current_name = provider_name
    input_tokens = estimate_tokens(prompt)

    while current_name:
        if current_name in visited:
            raise ConfigError(f"provider fallback cycle detected at {current_name}")
        visited.add(current_name)
        provider = as_object(providers.get(current_name), f"providers.{current_name}")
        provider_type = as_string(provider.get("type"), f"providers.{current_name}.type")
        model = as_string(provider.get("model", current_name), f"providers.{current_name}.model")
        retries = provider.get("max_retries", 0)
        if type(retries) is not int or retries < 0:
            raise ConfigError(f"providers.{current_name}.max_retries must be a non-negative integer")

        for attempt_index in range(retries + 1):
            started = time.monotonic()
            attempt: dict[str, object] = {
                "provider": current_name,
                "attempt": attempt_index + 1,
                "type": provider_type,
            }
            try:
                if dry_run:
                    elapsed_ms = round((time.monotonic() - started) * 1000, 3)
                    attempt.update({"status": "dry_run", "elapsed_ms": elapsed_ms})
                    attempts.append(attempt)
                    return ProviderResult(current_name, model, "dry_run", "", attempts, input_tokens, 0, estimate_cost(provider, input_tokens, 0))
                if provider_type == "mock":
                    output = mock_output(pass_id, template, current_name)
                    status = "ok"
                    return_code = 0
                    stderr = ""
                elif provider_type == "command":
                    completed = run_command_provider(provider, prompt)
                    output = redact_sensitive_text(completed.stdout)
                    stderr = completed.stderr.strip()
                    return_code = completed.returncode
                    status = "ok" if completed.returncode == 0 and output.strip() else "failed"
                else:
                    raise ConfigError(f"unsupported provider type: {provider_type}")

                elapsed_ms = round((time.monotonic() - started) * 1000, 3)
                output, truncated = truncate_output(output, max_output_chars)
                attempt.update(
                    {
                        "status": status,
                        "return_code": return_code,
                        "elapsed_ms": elapsed_ms,
                        "stderr": redact_sensitive_text(stderr)[:500],
                        "output_truncated": truncated,
                    }
                )
                attempts.append(attempt)
                if status == "ok":
                    output_tokens = estimate_tokens(output)
                    return ProviderResult(
                        current_name,
                        model,
                        "ok" if provider_type != "mock" else "mock",
                        output,
                        attempts,
                        input_tokens,
                        output_tokens,
                        estimate_cost(provider, input_tokens, output_tokens),
                    )
            except subprocess.TimeoutExpired as exc:
                elapsed_ms = round((time.monotonic() - started) * 1000, 3)
                attempts.append({"provider": current_name, "attempt": attempt_index + 1, "type": provider_type, "status": "timeout", "elapsed_ms": elapsed_ms, "stderr": redact_sensitive_text(str(exc))[:500]})
            except OSError as exc:
                elapsed_ms = round((time.monotonic() - started) * 1000, 3)
                attempts.append({"provider": current_name, "attempt": attempt_index + 1, "type": provider_type, "status": "failed", "elapsed_ms": elapsed_ms, "stderr": redact_sensitive_text(str(exc))[:500]})

        fallback = provider.get("fallback")
        current_name = fallback if isinstance(fallback, str) and fallback else ""

    return ProviderResult(provider_name, provider_name, "failed", "", attempts, input_tokens, 0, 0)


def parse_structured_output(output: str) -> dict[str, Any] | None:
    if not output.strip():
        return None
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def validate_structured_output(output: dict[str, Any], contract: dict[str, Any], contract_id: str) -> list[str]:
    errors: list[str] = []
    for field in contract_required_fields(contract, contract_id):
        if field not in output:
            errors.append(f"missing required field: {field}")

    for field, expected_type in STRUCTURED_REVIEW_FIELD_TYPES.items():
        if field in output and not isinstance(output[field], expected_type):
            errors.append(f"{field} must be a {expected_type.__name__}")

    verdict = output.get("verdict")
    if isinstance(verdict, str) and verdict not in ALLOWED_VERDICTS:
        errors.append(f"verdict must be one of: {', '.join(sorted(ALLOWED_VERDICTS))}")

    risk_tier = output.get("risk_tier")
    if isinstance(risk_tier, str) and risk_tier not in ALLOWED_RISK_TIERS:
        errors.append(f"risk_tier must be one of: {', '.join(sorted(ALLOWED_RISK_TIERS))}")

    return errors


def parse_and_validate_structured_output(
    output: str,
    status: str,
    contract: dict[str, Any],
    contract_id: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    if not output.strip() and status in {"dry_run", "failed"}:
        return None, []
    if not output.strip():
        return None, [f"{contract_id} output is empty"]

    structured = parse_structured_output(output)
    if structured is None:
        return None, [f"{contract_id} output must be a JSON object"]

    return structured, validate_structured_output(structured, contract, contract_id)


def summarize_attempt_failures(attempts: list[dict[str, object]]) -> list[str]:
    failures: list[str] = []
    for attempt in attempts:
        status = str(attempt.get("status", ""))
        if status not in {"failed", "timeout"}:
            continue
        provider = str(attempt.get("provider", "unknown-provider"))
        attempt_number = attempt.get("attempt", "?")
        message = f"{provider} attempt {attempt_number} {status}"
        stderr = str(attempt.get("stderr", "")).strip()
        if stderr:
            message = f"{message}: {stderr}"
        failures.append(message)
    return failures


def run_diff_measurement(config: dict[str, Any], no_diff: bool) -> dict[str, Any]:
    run_config = as_object(config.get("run", {}), "run")
    if no_diff or run_config.get("measure_diff", True) is False:
        return {"enabled": False, "report": None, "errors": []}

    args = run_config.get("measure_diff_args", ["--no-untracked"])
    if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
        raise ConfigError("run.measure_diff_args must be an array of strings")
    timeout = as_non_negative_number(run_config.get("measure_diff_timeout_seconds", 30), "run.measure_diff_timeout_seconds")
    command = [sys.executable, str(MEASURE_DIFF), "--format", "json", *args]
    try:
        completed = subprocess.run(
            command,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"enabled": True, "report": None, "errors": ["measure_diff.py timed out"]}
    if completed.returncode != 0:
        return {"enabled": True, "report": None, "errors": measure_diff_errors(completed)}
    try:
        return {"enabled": True, "report": json.loads(completed.stdout), "errors": []}
    except json.JSONDecodeError as exc:
        return {"enabled": True, "report": None, "errors": [f"measure_diff.py returned invalid JSON: {exc}"]}


def measure_diff_errors(completed: subprocess.CompletedProcess[str]) -> list[str]:
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict):
        errors = payload.get("errors")
        if isinstance(errors, list) and errors and all(isinstance(error, str) and error for error in errors):
            return errors
    return [completed.stderr.strip() or "measure_diff.py failed"]


def severity_blocks(findings: Any) -> bool:
    if not isinstance(findings, list):
        return False
    for finding in findings:
        if isinstance(finding, dict) and str(finding.get("severity", "")).upper() in {"P1", "P2"}:
            return True
    return False


def fuse_review(diff: dict[str, Any], pass_results: list[dict[str, Any]]) -> dict[str, Any]:
    diff_report = diff.get("report") if isinstance(diff, dict) else None
    warnings = diff_report.get("warnings", []) if isinstance(diff_report, dict) else []
    statuses = {str(item.get("status")) for item in pass_results}
    structured = [item.get("structured_output") for item in pass_results if isinstance(item.get("structured_output"), dict)]
    blocking_findings = any(severity_blocks(item.get("findings")) for item in structured)
    output_contract_errors = [
        f"{item.get('id')}: {error}"
        for item in pass_results
        for error in item.get("structured_output_errors", [])
    ]
    provider_failures = [
        f"{item.get('id')}: {failure}"
        for item in pass_results
        for failure in item.get("attempt_failures", [])
    ]

    if "large-diff-not-reviewable-threshold" in warnings:
        verdict = "Not reviewable"
    elif blocking_findings:
        verdict = "Not ready"
    elif warnings or output_contract_errors or provider_failures or statuses & {"mock", "dry_run", "failed"}:
        verdict = "Needs confirmation"
    else:
        verdict = "Ready"

    if "risk-tier-escalation-required" in warnings:
        risk_tier = "L3"
    elif warnings:
        risk_tier = "L2"
    else:
        risk_tier = "L1"

    return {
        "verdict": verdict,
        "risk_tier": risk_tier,
        "rule_warnings": warnings,
        "llm_statuses": sorted(statuses),
        "output_contract_errors": output_contract_errors,
        "provider_failures": provider_failures,
        "explanation": "Fusion combines measure_diff.py rule signals with structured reviewer outputs; human owner still decides merge readiness.",
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    config_path = Path(args.config)
    config = as_object(load_json(config_path), "runner config")
    manifest, manifest_path = load_prompt_manifest(config, config_path, args.prompt_manifest)
    templates = prompt_templates(manifest)
    contract_id = as_string(config.get("output_contract"), "output_contract")
    contract = output_contract(manifest, contract_id)
    providers = as_object(config.get("providers"), "providers")
    run_config = as_object(config.get("run", {}), "run")
    max_output_chars = int(as_non_negative_number(run_config.get("max_output_chars", 20000), "run.max_output_chars"))
    include_prompt = bool(args.include_prompts)
    context = load_context(args.context_file or [])
    diff = run_diff_measurement(config, args.no_diff)
    diff_summary = json.dumps(diff.get("report"), indent=2, ensure_ascii=False) if diff.get("report") else "No diff measurement available."
    contract_text = as_string(contract.get("instructions"), "output contract instructions")

    pass_reports: list[dict[str, Any]] = []
    for review_pass in enabled_passes(config):
        pass_id = as_string(review_pass.get("id"), "review_pass.id")
        template_id = as_string(review_pass.get("template_id"), f"review_passes.{pass_id}.template_id")
        if template_id not in templates:
            raise ConfigError(f"unknown prompt template: {template_id}")
        template = templates[template_id]
        provider_name = str(review_pass.get("provider") or config.get("default_provider") or "")
        if not provider_name:
            raise ConfigError(f"review pass {pass_id} has no provider and no default_provider")
        prompt = render_prompt(
            template,
            {
                "target": args.target,
                "context": context,
                "diff_summary": diff_summary,
                "output_contract": contract_text,
            },
        )
        result = execute_provider(provider_name, providers, prompt, pass_id, template, args.dry_run, max_output_chars)
        structured_output, structured_output_errors = parse_and_validate_structured_output(result.output, result.status, contract, contract_id)
        attempt_failures = summarize_attempt_failures(result.attempts)
        pass_report: dict[str, Any] = {
            "id": pass_id,
            "template_id": template_id,
            "template_version": template.get("version"),
            "provider": result.provider,
            "model": result.model,
            "status": result.status,
            "attempts": result.attempts,
            "estimated_input_tokens": result.input_tokens,
            "estimated_output_tokens": result.output_tokens,
            "estimated_cost_usd": result.estimated_cost_usd,
            "structured_output": structured_output,
            "structured_output_errors": structured_output_errors,
            "attempt_failures": attempt_failures,
        }
        if result.output and pass_report["structured_output"] is None:
            pass_report["raw_output"] = result.output
        if include_prompt:
            pass_report["prompt"] = prompt
        pass_reports.append(pass_report)

    total_input = sum(int(item["estimated_input_tokens"]) for item in pass_reports)
    total_output = sum(int(item["estimated_output_tokens"]) for item in pass_reports)
    total_cost = round(sum(float(item["estimated_cost_usd"]) for item in pass_reports), 8)

    return {
        "schema_version": "review-runner-report-v1",
        "run_id": str(uuid.uuid4()),
        "created_at": now_iso(),
        "target": args.target,
        "config": str(config_path),
        "prompt_manifest": str(manifest_path),
        "prompt_manifest_version": manifest.get("manifest_version"),
        "output_contract": contract_id,
        "diff": diff,
        "passes": pass_reports,
        "cost": {
            "estimated_input_tokens": total_input,
            "estimated_output_tokens": total_output,
            "estimated_total_tokens": total_input + total_output,
            "estimated_cost_usd": total_cost,
        },
        "fusion": fuse_review(diff, pass_reports),
        "security": {
            "secrets_in_config": "Do not place API keys in this config; command providers should read secrets from their own environment.",
            "prompt_recording": "Rendered prompts are omitted unless --include-prompts is passed.",
        },
    }


def print_markdown(report: dict[str, Any]) -> None:
    fusion = report["fusion"]
    print("# Review Runner Report")
    print()
    print(f"- Verdict: `{fusion['verdict']}`")
    print(f"- Risk tier: `{fusion['risk_tier']}`")
    print(f"- Target: `{report['target']}`")
    print(f"- Estimated tokens: `{report['cost']['estimated_total_tokens']}`")
    print(f"- Estimated cost USD: `{report['cost']['estimated_cost_usd']}`")
    if fusion["rule_warnings"]:
        print()
        print("## Rule Warnings")
        for warning in fusion["rule_warnings"]:
            print(f"- `{warning}`")
    if fusion["output_contract_errors"]:
        print()
        print("## Output Contract Warnings")
        for error in fusion["output_contract_errors"]:
            print(f"- {error}")
    if fusion["provider_failures"]:
        print()
        print("## Provider Failures")
        for failure in fusion["provider_failures"]:
            print(f"- {failure}")
    print()
    print("## Passes")
    for item in report["passes"]:
        print(f"- `{item['id']}`: `{item['status']}` via `{item['provider']}` (`{item['model']}`)")


def build_error_report(message: str) -> dict[str, Any]:
    return {
        "schema_version": "review-runner-error-v1",
        "ok": False,
        "errors": [message],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run configured agentic-code-review passes.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Runner config JSON path.")
    parser.add_argument("--prompt-manifest", help="Override prompt manifest path.")
    parser.add_argument("--target", default="current Git diff", help="Review target label inserted into prompts.")
    parser.add_argument("--context-file", action="append", help="Additional local context file. May be repeated.")
    parser.add_argument("--dry-run", action="store_true", help="Render and estimate passes without calling providers.")
    parser.add_argument("--no-diff", action="store_true", help="Skip measure_diff.py fusion input.")
    parser.add_argument("--include-prompts", action="store_true", help="Include rendered prompts in the report.")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    try:
        report = build_report(args)
    except ConfigError as exc:
        if args.format == "json":
            print(json.dumps(build_error_report(str(exc)), indent=2, ensure_ascii=False))
        else:
            print(str(exc), file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_markdown(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
