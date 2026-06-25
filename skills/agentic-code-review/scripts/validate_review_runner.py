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
    as_object,
    as_string,
    contract_required_fields,
    load_json,
    load_prompt_manifest,
    output_contract,
    prompt_templates,
    validate_fallback_chains,
    validate_provider_config,
    validate_review_passes_config,
    validate_run_config,
)


def validate_top_level_config(config: dict[str, Any]) -> list[str]:
    allowed_fields = {
        "$schema",
        "default_provider",
        "description",
        "output_contract",
        "prompt_manifest",
        "providers",
        "review_passes",
        "run",
        "schema_version",
    }
    return [
        f"{field} is unsupported; remove unknown top-level runner config keys"
        for field in sorted(set(config) - allowed_fields)
    ]


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
    errors.extend(validate_top_level_config(config))

    try:
        providers = as_object(config.get("providers"), "providers")
    except ConfigError as exc:
        providers = {}
        errors.append(str(exc))

    for name, provider in providers.items():
        errors.extend(validate_provider_config(str(name), provider, providers))
    errors.extend(validate_fallback_chains(providers))

    errors.extend(validate_run_config(config))
    if templates is not None:
        errors.extend(validate_review_passes_config(config, templates, providers))

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
