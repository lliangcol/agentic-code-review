#!/usr/bin/env python3
"""Validate optional review runner config and prompt manifest assets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from run_review_passes import (
    ConfigError,
    DEFAULT_CONFIG,
    as_non_negative_number,
    as_object,
    as_string,
    contract_required_fields,
    load_json,
    load_prompt_manifest,
    output_contract,
    prompt_templates,
    provider_pricing,
)


def validate_provider(name: str, value: Any, providers: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not name:
        return ["provider names must be non-empty strings"]

    try:
        provider = as_object(value, f"providers.{name}")
        provider_type = as_string(provider.get("type"), f"providers.{name}.type")
        as_string(provider.get("model", name), f"providers.{name}.model")
        as_non_negative_number(provider.get("timeout_seconds", 120), f"providers.{name}.timeout_seconds")
        provider_pricing(provider)
    except ConfigError as exc:
        return [str(exc)]

    allowed_fields = {
        "command",
        "fallback",
        "max_retries",
        "model",
        "pricing",
        "timeout_seconds",
        "type",
    }
    for field in sorted(set(provider) - allowed_fields):
        errors.append(f"providers.{name}.{field} is unsupported; remove unknown provider config keys")

    pricing = provider.get("pricing", {})
    if pricing is not None:
        try:
            pricing_obj = as_object(pricing, f"providers.{name}.pricing")
            allowed_pricing_fields = {
                "input_per_million_tokens_usd",
                "output_per_million_tokens_usd",
            }
            for field in sorted(set(pricing_obj) - allowed_pricing_fields):
                errors.append(f"providers.{name}.pricing.{field} is unsupported; remove unknown pricing config keys")
        except ConfigError as exc:
            errors.append(str(exc))

    retries = provider.get("max_retries", 0)
    if type(retries) is not int or retries < 0:
        errors.append(f"providers.{name}.max_retries must be a non-negative integer")

    if provider_type == "command":
        command = provider.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            errors.append(f"providers.{name}.command must be a non-empty array of strings")
    elif provider_type != "mock":
        errors.append(f"providers.{name}.type must be one of: command, mock")

    fallback = provider.get("fallback")
    if fallback is not None:
        if not isinstance(fallback, str) or not fallback:
            errors.append(f"providers.{name}.fallback must be a non-empty string when set")
        elif fallback not in providers:
            errors.append(f"providers.{name}.fallback references unknown provider: {fallback}")
        elif fallback == name:
            errors.append(f"providers.{name}.fallback must not reference itself")

    return errors


def canonical_cycle(cycle_members: list[str]) -> tuple[str, ...]:
    rotations = [
        tuple(cycle_members[index:] + cycle_members[:index])
        for index in range(len(cycle_members))
    ]
    return min(rotations)


def validate_fallback_chains(providers: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    emitted_cycles: set[tuple[str, ...]] = set()

    for start in providers:
        seen_at: dict[str, int] = {}
        chain: list[str] = []
        current = str(start)

        while current:
            provider = providers.get(current)
            if not isinstance(provider, dict):
                break

            fallback = provider.get("fallback")
            if not isinstance(fallback, str) or not fallback or fallback not in providers:
                break
            if fallback == current:
                break

            if current not in seen_at:
                seen_at[current] = len(chain)
                chain.append(current)

            if fallback in seen_at:
                cycle_members = chain[seen_at[fallback]:]
                canonical = canonical_cycle(cycle_members)
                if canonical not in emitted_cycles:
                    emitted_cycles.add(canonical)
                    cycle_path = [*canonical, canonical[0]]
                    errors.append(f"provider fallback cycle detected: {' -> '.join(cycle_path)}")
                break

            current = fallback

    return errors


def validate_run_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        run_config = as_object(config.get("run", {}), "run")
    except ConfigError as exc:
        return [str(exc)]

    allowed_fields = {
        "measure_diff",
        "measure_diff_args",
        "measure_diff_timeout_seconds",
        "max_output_chars",
    }
    unsupported_fields = {"include_prompt_in_report"}
    for field in sorted(set(run_config) - allowed_fields - unsupported_fields):
        errors.append(f"run.{field} is unsupported; remove unknown run config keys")

    if "measure_diff" in run_config and not isinstance(run_config["measure_diff"], bool):
        errors.append("run.measure_diff must be a boolean")
    if "include_prompt_in_report" in run_config:
        errors.append("run.include_prompt_in_report is unsupported; pass --include-prompts when prompt recording is intentionally required")

    for field, default in [("measure_diff_timeout_seconds", 30), ("max_output_chars", 20000)]:
        try:
            as_non_negative_number(run_config.get(field, default), f"run.{field}")
        except ConfigError as exc:
            errors.append(str(exc))

    args = run_config.get("measure_diff_args", ["--no-untracked"])
    if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
        errors.append("run.measure_diff_args must be an array of strings")

    return errors


def validate_review_passes(config: dict[str, Any], templates: dict[str, dict[str, Any]], providers: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    review_passes = config.get("review_passes")
    if not isinstance(review_passes, list) or not review_passes:
        return ["review_passes must be a non-empty array"]

    default_provider = config.get("default_provider")
    if default_provider is not None:
        if not isinstance(default_provider, str) or not default_provider:
            errors.append("default_provider must be a non-empty string when set")
        elif default_provider not in providers:
            errors.append(f"default_provider references unknown provider: {default_provider}")

    enabled_count = 0
    for index, item in enumerate(review_passes):
        try:
            review_pass = as_object(item, f"review_passes[{index}]")
            pass_id = as_string(review_pass.get("id"), f"review_passes[{index}].id")
            template_id = as_string(review_pass.get("template_id"), f"review_passes[{index}].template_id")
        except ConfigError as exc:
            errors.append(str(exc))
            continue

        enabled = review_pass.get("enabled", True)
        if not isinstance(enabled, bool):
            errors.append(f"review_passes[{index}].enabled must be a boolean when set")
        if enabled:
            enabled_count += 1

        if template_id not in templates:
            errors.append(f"review_passes[{index}] references unknown template: {template_id}")

        provider_name = review_pass.get("provider") or default_provider
        if not isinstance(provider_name, str) or not provider_name:
            errors.append(f"review_passes[{index}] has no provider and no default_provider")
        elif provider_name not in providers:
            errors.append(f"review_passes[{index}] references unknown provider: {provider_name}")

        if not pass_id:
            errors.append(f"review_passes[{index}].id must be non-empty")

    if enabled_count == 0:
        errors.append("at least one review pass must be enabled")

    return errors


def validate_prompt_manifest(config: dict[str, Any], config_path: Path, override: str | None) -> tuple[dict[str, Any] | None, Path | None, dict[str, dict[str, Any]] | None, list[str]]:
    errors: list[str] = []
    try:
        manifest, manifest_path = load_prompt_manifest(config, config_path, override)
        templates = prompt_templates(manifest)
        contracts = as_object(manifest.get("output_contracts"), "output_contracts")
        for contract_id in contracts:
            contract = output_contract(manifest, str(contract_id))
            contract_required_fields(contract, str(contract_id))
        contract_id = as_string(config.get("output_contract"), "output_contract")
        output_contract(manifest, contract_id)
        return manifest, manifest_path, templates, errors
    except ConfigError as exc:
        errors.append(str(exc))
        return None, None, None, errors


def validate_config(config_path: Path, prompt_manifest_override: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    try:
        config = as_object(load_json(config_path), "runner config")
    except ConfigError as exc:
        return {
            "ok": False,
            "config": str(config_path),
            "prompt_manifest": None,
            "providers": [],
            "review_passes": 0,
            "errors": [str(exc)],
        }

    manifest, manifest_path, templates, manifest_errors = validate_prompt_manifest(config, config_path, prompt_manifest_override)
    errors.extend(manifest_errors)

    try:
        providers = as_object(config.get("providers"), "providers")
    except ConfigError as exc:
        providers = {}
        errors.append(str(exc))

    for name, provider in providers.items():
        errors.extend(validate_provider(str(name), provider, providers))
    errors.extend(validate_fallback_chains(providers))

    errors.extend(validate_run_config(config))
    if templates is not None:
        errors.extend(validate_review_passes(config, templates, providers))

    return {
        "ok": not errors,
        "config": str(config_path),
        "prompt_manifest": str(manifest_path) if manifest_path is not None else None,
        "manifest_version": manifest.get("manifest_version") if isinstance(manifest, dict) else None,
        "providers": sorted(str(name) for name in providers),
        "review_passes": len(config.get("review_passes", [])) if isinstance(config.get("review_passes"), list) else 0,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate optional review runner config and prompt manifest.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Runner config JSON path.")
    parser.add_argument("--prompt-manifest", help="Override prompt manifest path.")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    report = validate_config(Path(args.config), args.prompt_manifest)
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif report["ok"]:
        print("review runner validation passed.")
    else:
        for error in report["errors"]:
            print(error, file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
