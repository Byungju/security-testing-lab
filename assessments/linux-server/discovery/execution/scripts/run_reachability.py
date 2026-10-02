#!/usr/bin/env python3
"""DO-EXT-001 Network Reachability 실행 Runner.

이 Runner는 Configuration을 검증하고, TP-EXT-001-01에 정의된 검증 방식만
수행하여 Raw Evidence와 Structured Execution Result를 생성한다.

중요:
- 검증 결과를 임의로 판단하지 않는다(reachable/unreachable 판정을 하지 않는다).
- Finding이나 Assessment Result를 생성하지 않는다.
- Target이 placeholder이거나 필수 설정이 누락되면 실행하지 않는다.
- 기본 동작은 validate-only 이며, 실제 실행은 --execute 와
  environment.allow_execution: true 가 모두 필요하다.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML이 필요합니다. (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ALLOWED_METHODS = {"icmp", "tcp", "path"}
PLACEHOLDER_MARKERS = ("<", ">", "TODO", "todo", "CHANGEME", "changeme")
SHELL_METACHARS = (";", "|", "&", "$", "`", "\n", ">", "<")

IPV4_RE = re.compile(
    r"^(25[0-5]|2[0-4]\d|1?\d?\d)(\.(25[0-5]|2[0-4]\d|1?\d?\d)){3}$"
)
HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)([A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?)"
    r"(\.[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*$"
)


def is_placeholder(value) -> bool:
    if value is None:
        return True
    text = str(value).strip()
    if not text:
        return True
    return any(marker in text for marker in PLACEHOLDER_MARKERS)


def load_config(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"configuration file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("configuration root must be a mapping")
    return data


def validate_config(config: dict) -> list[str]:
    errors: list[str] = []

    for key in (
        "objective",
        "test_case",
        "procedure",
        "target",
        "target_type",
        "assessment_perspective",
        "scope",
        "verification_methods",
        "evidence",
        "environment",
    ):
        if key not in config:
            errors.append(f"missing required field: {key}")

    if errors:
        return errors

    if is_placeholder(config.get("target")):
        errors.append("target is a placeholder or empty; refusing to run")

    if is_placeholder(config.get("assessment_perspective")):
        errors.append("assessment_perspective is empty")

    scope = config.get("scope") or {}
    include = scope.get("include")
    if not isinstance(include, list) or not include:
        errors.append("scope.include must be a non-empty list")
    exclude = scope.get("exclude", [])
    if not isinstance(exclude, list):
        errors.append("scope.exclude must be a list")

    evidence = config.get("evidence") or {}
    if is_placeholder(evidence.get("output_dir")):
        errors.append("evidence.output_dir is required")

    environment = config.get("environment") or {}
    allowed_tools = environment.get("allowed_tools")
    if not isinstance(allowed_tools, list) or not allowed_tools:
        errors.append("environment.allowed_tools must be a non-empty list")
    if "allow_execution" not in environment:
        errors.append("environment.allow_execution is required")

    methods = config.get("verification_methods")
    if not isinstance(methods, list) or not methods:
        errors.append("verification_methods must be a non-empty list")
    else:
        for index, method in enumerate(methods, start=1):
            errors.extend(_validate_method(index, method, allowed_tools or []))

    return errors


def _validate_method(index: int, method: dict, allowed_tools: list) -> list[str]:
    errors: list[str] = []
    prefix = f"verification_methods[{index}]"

    if not isinstance(method, dict):
        return [f"{prefix} must be a mapping"]

    name = method.get("name")
    if name not in ALLOWED_METHODS:
        errors.append(f"{prefix}.name must be one of {sorted(ALLOWED_METHODS)}")

    if is_placeholder(method.get("technique")):
        errors.append(f"{prefix}.technique is required")

    tool = method.get("tool")
    if is_placeholder(tool):
        errors.append(f"{prefix}.tool is required")
    elif isinstance(allowed_tools, list) and tool not in allowed_tools:
        errors.append(f"{prefix}.tool '{tool}' is not in environment.allowed_tools")

    timeout = method.get("timeout_seconds")
    if not isinstance(timeout, int) or timeout <= 0:
        errors.append(f"{prefix}.timeout_seconds must be a positive integer")

    options = method.get("options", [])
    if not isinstance(options, list) or not all(isinstance(o, str) for o in options):
        errors.append(f"{prefix}.options must be a list of strings")
    else:
        for option in options:
            if any(ch in option for ch in SHELL_METACHARS):
                errors.append(f"{prefix}.options contains a shell metacharacter: {option!r}")

    if name == "tcp" and is_placeholder(method.get("target_port")):
        errors.append(f"{prefix}.target_port is required for tcp method")

    return errors


def validate_target(config: dict) -> list[str]:
    errors: list[str] = []
    target = str(config.get("target")).strip()

    if not (IPV4_RE.match(target) or HOSTNAME_RE.match(target)):
        errors.append(f"target is not a valid hostname or IPv4 address: {target!r}")

    scope = config.get("scope") or {}
    include = [str(v).strip() for v in scope.get("include", [])]
    exclude = [str(v).strip() for v in scope.get("exclude", [])]

    if target not in include:
        errors.append("target is not within scope.include")
    if target in exclude:
        errors.append("target is listed in scope.exclude")

    return errors


def sanitize_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", str(value)).strip("-") or "exec"


def execution_base_dir() -> Path:
    """execution/ 디렉터리를 반환한다(scripts/의 상위)."""
    return Path(__file__).resolve().parent.parent


def resolve_output_dir(value: str) -> Path:
    """상대 output_dir은 execution/ 기준으로 해석한다. 절대 경로는 그대로 사용한다."""
    path = Path(value)
    if path.is_absolute():
        return path
    return execution_base_dir() / path


def build_command(method: dict, target: str) -> list[str]:
    tool = method["tool"]
    options = list(method.get("options", []))
    name = method["name"]

    if name == "tcp":
        port = str(method["target_port"])
        return [tool, *options, target, port]
    return [tool, *options, target]


def tool_version(tool: str) -> str | None:
    for flag in ("--version", "-V"):
        try:
            completed = subprocess.run(
                [tool, flag],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        output = (completed.stdout or completed.stderr or "").strip()
        if output:
            return output.splitlines()[0].strip()
    return None


def classify_observation(method: dict, returncode: int, stderr: str) -> str:
    name = method["name"]
    if name == "icmp":
        if returncode == 0:
            return "icmp_response_observed"
        return "icmp_no_response_observed"
    if name == "tcp":
        if returncode == 0:
            return "tcp_connect_succeeded"
        lowered = (stderr or "").lower()
        if "refused" in lowered:
            return "tcp_connection_refused"
        if "timed out" in lowered or "timeout" in lowered:
            return "tcp_connect_timeout"
        return "tcp_connect_failed"
    if name == "path":
        if returncode == 0:
            return "path_observed"
        return "path_incomplete"
    return "unknown"


def run_method(method: dict, target: str, raw_dir: Path, step: int) -> dict:
    name = method["name"]
    tool = method["tool"]
    command = build_command(method, target)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    base = f"step-{step}-{name}-{sanitize_id(tool)}"

    record: dict = {
        "step": step,
        "method": name,
        "technique": method.get("technique"),
        "tool": tool,
        "tool_version": tool_version(tool),
        "target": target,
        "command": command,
        "execution_conditions": {
            "options": method.get("options", []),
            "timeout_seconds": method.get("timeout_seconds"),
        },
        "timestamp_utc": timestamp,
        "exit_status": None,
        "execution_error": None,
        "observation_category": None,
        "raw_output": {
            "stdout_file": None,
            "stderr_file": None,
        },
    }

    stdout_file = raw_dir / f"{base}.stdout.txt"
    stderr_file = raw_dir / f"{base}.stderr.txt"

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=method["timeout_seconds"],
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        record["execution_error"] = "timeout"
        record["observation_category"] = "execution_timeout"
        stdout_file.write_text(exc.stdout or "", encoding="utf-8")
        stderr_file.write_text(exc.stderr or "", encoding="utf-8")
    except OSError as exc:
        record["execution_error"] = f"os_error: {exc}"
        record["observation_category"] = "execution_error"
        stdout_file.write_text("", encoding="utf-8")
        stderr_file.write_text(str(exc), encoding="utf-8")
    else:
        record["exit_status"] = completed.returncode
        record["observation_category"] = classify_observation(
            method, completed.returncode, completed.stderr or ""
        )
        stdout_file.write_text(completed.stdout or "", encoding="utf-8")
        stderr_file.write_text(completed.stderr or "", encoding="utf-8")

    record["raw_output"]["stdout_file"] = str(stdout_file)
    record["raw_output"]["stderr_file"] = str(stderr_file)
    return record


def planned_commands(config: dict) -> list[dict]:
    plans = []
    target = str(config["target"])
    step = 0
    for method in config["verification_methods"]:
        if not method.get("enabled", True):
            continue
        step += 1
        plans.append(
            {
                "step": step,
                "method": method.get("name"),
                "tool": method.get("tool"),
                "command": build_command(method, target),
                "timeout_seconds": method.get("timeout_seconds"),
            }
        )
    return plans


def main() -> int:
    parser = argparse.ArgumentParser(description="DO-EXT-001 Reachability Execution Runner")
    parser.add_argument("--config", required=True, help="configuration YAML path")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--validate-only", action="store_true", help="validate and print plan (default)")
    mode.add_argument("--execute", action="store_true", help="execute the procedure")
    args = parser.parse_args()

    config_path = Path(args.config)
    try:
        config = load_config(config_path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"[ERROR] failed to load configuration: {exc}", file=sys.stderr)
        return 2

    errors = validate_config(config) + validate_target(config)
    if errors:
        print("[NOT READY] configuration validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    execute = args.execute
    allow_execution = bool(config["environment"].get("allow_execution"))
    if execute and not allow_execution:
        print(
            "[REFUSED] --execute requested but environment.allow_execution is false.",
            file=sys.stderr,
        )
        return 1

    plans = planned_commands(config)
    print(f"[OK] configuration valid: {config_path}")
    print(f"[OK] target: {config['target']} ({config.get('target_type')})")
    print(f"[OK] perspective: {config.get('assessment_perspective')}")
    print(f"[OK] planned methods: {len(plans)}")
    for plan in plans:
        print(f"  - step {plan['step']}: {plan['method']} via {plan['tool']}: {plan['command']}")

    if not execute:
        print("[VALIDATE-ONLY] no command executed. Use --execute to run.")
        return 0

    execution_id = config.get("execution_id") or (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + sanitize_id(config["objective"])
    )
    output_root = resolve_output_dir(config["evidence"]["output_dir"]) / sanitize_id(execution_id)
    raw_dir = output_root / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results: list[dict] = []
    step = 0
    for method in config["verification_methods"]:
        if not method.get("enabled", True):
            continue
        step += 1
        print(f"[RUN] step {step}: {method.get('name')} via {method.get('tool')}")
        results.append(run_method(method, str(config["target"]), raw_dir, step))
    finished_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    execution_result = {
        "execution_id": execution_id,
        "objective": config.get("objective"),
        "test_case": config.get("test_case"),
        "procedure": config.get("procedure"),
        "target": config.get("target"),
        "target_type": config.get("target_type"),
        "assessment_perspective": config.get("assessment_perspective"),
        "scope": config.get("scope"),
        "started_at_utc": started_at,
        "finished_at_utc": finished_at,
        "execution_mode": "execute",
        "results": results,
        "notes": "Execution Result only. Assessment Result and Finding are out of scope for this runner.",
    }

    result_file = output_root / "execution_result.json"
    result_file.write_text(
        json.dumps(execution_result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[DONE] execution result: {result_file}")
    print("[NOTE] observation_category is an observation, not a reachable/unreachable verdict.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
