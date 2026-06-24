#!/usr/bin/env python3
"""Detect optional review-fix-loop availability without initializing configuration."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


CONFIG_PATHS = ["review-fix-loop.gates.json", ".review-fix-loop"]


def git_review_fix_loop_path(root: Path) -> Path | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--git-path", "review-fix-loop"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None

    path_text = result.stdout.strip()
    if not path_text:
        return None

    git_path = Path(path_text)
    if not git_path.is_absolute():
        git_path = root / git_path
    return git_path


def display_path(root: Path, path: Path) -> str:
    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(root).as_posix()
    except ValueError:
        return str(resolved_path)


def detect(root: Path) -> dict[str, object]:
    resolved = root.resolve()
    config_paths = [path for path in CONFIG_PATHS if (resolved / path).exists()]
    git_config = git_review_fix_loop_path(resolved) or (resolved / ".git" / "review-fix-loop")
    if git_config.exists():
        git_config_display = display_path(resolved, git_config)
        if git_config_display not in config_paths:
            config_paths.append(git_config_display)

    cli_path = shutil.which("review-fix-loop")
    return {
        "root": str(resolved),
        "configured": bool(config_paths),
        "config_paths": config_paths,
        "cli_available": cli_path is not None,
        "cli_path": cli_path,
        "should_initialize": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect optional review-fix-loop configuration.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    result = detect(Path(args.root))
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"configured: {str(result['configured']).lower()}")
        print(f"cli_available: {str(result['cli_available']).lower()}")
        if result["config_paths"]:
            print("config_paths:")
            for path in result["config_paths"]:
                print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
