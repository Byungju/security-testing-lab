#!/usr/bin/env python3
"""Discovery 실행 Runner.

Configuration을 검증하고, Procedure에 정의된 검증 방식만 수행하여
Raw Evidence와 Structured Execution Result를 생성한다.

지원 Verification Method:
- icmp            : ICMP 기반 도달성 관찰 (DO-EXT-001)
- tcp             : 지정 포트 TCP 연결 관찰, 도달성 보조 (DO-EXT-001)
- path            : Network path 관찰, diagnostic (DO-EXT-001)
- tcp_scan        : 지정 Port Range TCP 포트 스캔 (DO-EXT-002)
- tcp_connectivity: 지정 포트 TCP 연결 관찰 (DO-EXT-002, 보조/교차검증)

책임 경계:
- Port Scanning(tcp_scan, nmap)과 TCP Connectivity(tcp_connectivity, nc)를 구분한다.
  tcp_scan 대상은 config의 `port_range`, tcp_connectivity 대상은 config의 `ports`이다.
- Runner가 임의로 포트를 추가/선택하지 않는다(nmap 결과로 nc 포트를 자동 선택하지 않는다).
- Port State/관찰 결과를 임의로 판단하지 않는다(위험/취약/Pass/Fail 판정 금지).
- Finding이나 Assessment Result를 생성하지 않는다.
- Target이 placeholder이거나 필수 설정이 누락되면 실행하지 않는다.
- 기본 동작은 validate-only 이며, 실제 실행은 --execute 와
  environment.allow_execution: true 가 모두 필요하다.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML이 필요합니다. (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ALLOWED_METHODS = {
    "icmp",
    "tcp",
    "path",
    "tcp_scan",
    "tcp_connectivity",
    "service_scan",
    "port_reverify",
    "version_scan",
}
PORT_METHODS = {"tcp", "tcp_connectivity"}
PORTS_LIST_METHODS = {
    "tcp",
    "tcp_connectivity",
    "service_scan",
    "port_reverify",
    "version_scan",
}
# 서비스/버전 상세(details)를 파싱하는 method
SERVICE_PARSE_METHODS = {"service_scan", "version_scan"}
# 포트 목록을 스캔해 결과 라인을 파싱하는 method
PORT_PARSE_METHODS = {"tcp_scan", "port_reverify"}
PLACEHOLDER_MARKERS = ("<", ">", "TODO", "todo", "CHANGEME", "changeme")
SHELL_METACHARS = (";", "|", "&", "$", "`", "\n", ">", "<")

# nmap 출력에서 포트/프로토콜/상태 라인을 파싱한다(예: "22/tcp open ssh").
# 개행을 넘지 않도록 공백은 [ \t]만 사용한다.
NMAP_PORT_RE = re.compile(r"^(\d+)/(tcp|udp)[ \t]+([a-z|]+)", re.MULTILINE)
# nmap -sV 서비스 라인(예: "22/tcp open  ssh     OpenSSH 9.8 (protocol 2.0)").
NMAP_SERVICE_RE = re.compile(
    r"^(\d+)/(tcp|udp)[ \t]+([a-z|]+)[ \t]+(\S+)(?:[ \t]+(.*))?$", re.MULTILINE
)

# Tool별 버전 확인 명령. 지원하지 않는 옵션을 사용해 오류를 버전으로
# 기록하지 않도록 Tool에 맞는 옵션을 지정한다.
TOOL_VERSION_PROBES = {
    "ping": [["-V"]],
    "tracepath": [["-V"]],
    "traceroute": [["--version"], ["-V"]],
    "mtr": [["--version"]],
    "nc": [["-h"]],
    "ncat": [["--version"]],
    "nmap": [["--version"]],
}
DEFAULT_VERSION_PROBES = [["-V"], ["--version"]]
VERSION_ERROR_MARKERS = (
    "invalid option",
    "unrecognized option",
    "unknown option",
    "unrecognized",
    "usage:",
    "try '",
    "command not found",
    "no such",
)

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


def _as_text(value) -> str:
    """bytes/None을 안전하게 str로 변환한다(TimeoutExpired.stdout 등)."""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


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

    errors.extend(_validate_port_range(config))

    return errors


def _validate_port_range(config: dict) -> list[str]:
    """port_range를 검증한다. tcp_scan이 enabled이면 반드시 필요하다."""
    errors: list[str] = []
    scan_enabled = any(
        isinstance(m, dict) and m.get("name") == "tcp_scan" and m.get("enabled", True)
        for m in config.get("verification_methods", [])
    )
    port_range = config.get("port_range")

    if port_range is None:
        if scan_enabled:
            errors.append("port_range is required when tcp_scan is enabled")
        return errors

    if not isinstance(port_range, dict):
        return ["port_range must be a mapping with start and end"]

    start = port_range.get("start")
    end = port_range.get("end")
    for label, value in (("start", start), ("end", end)):
        if isinstance(value, bool) or not isinstance(value, int):
            errors.append(f"port_range.{label} must be an integer")
    if (
        isinstance(start, int)
        and not isinstance(start, bool)
        and isinstance(end, int)
        and not isinstance(end, bool)
        and not (1 <= start <= end <= 65535)
    ):
        errors.append("port_range must satisfy 1 <= start <= end <= 65535")

    return errors


def _validate_method(index: int, method: dict, allowed_tools: list) -> list[str]:
    """Method별 Config를 검증한다. enabled 여부와 무관하게 구조는 검증한다."""
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

    if name in PORTS_LIST_METHODS:
        ports = method.get("ports")
        if not isinstance(ports, list):
            errors.append(
                f"{prefix}.ports must be a list (use [] to disable this method)"
            )
        else:
            for port in ports:
                if isinstance(port, bool) or not isinstance(port, int):
                    errors.append(f"{prefix}.ports contains a non-integer port: {port!r}")
                elif not (1 <= port <= 65535):
                    errors.append(f"{prefix}.ports contains an out-of-range port: {port!r}")

    if name == "tcp_scan" and tool != "nmap":
        errors.append(
            f"{prefix}: tcp_scan must use tool 'nmap' (port scanning); "
            "nc is a connectivity verification tool, not a port scanner"
        )

    if name == "service_scan" and tool != "nmap":
        errors.append(f"{prefix}: service_scan must use tool 'nmap'")

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


def local_now() -> datetime:
    """로컬 타임존이 적용된 현재 시각을 반환한다."""
    return datetime.now().astimezone()


def iso_local(dt: datetime | None = None) -> str:
    """로컬 시간과 타임존 오프셋을 포함한 ISO 8601 문자열을 반환한다."""
    return (dt or local_now()).isoformat(timespec="seconds")


def local_tzname() -> str:
    return local_now().tzname() or ""


def execution_base_dir() -> Path:
    """execution/ 디렉터리를 반환한다(scripts/의 상위)."""
    return Path(__file__).resolve().parent.parent


def resolve_output_dir(value: str) -> Path:
    """상대 output_dir은 execution/ 기준으로 해석한다. 절대 경로는 그대로 사용한다."""
    path = Path(value)
    if path.is_absolute():
        return path
    return execution_base_dir() / path


def enabled_methods(config: dict) -> list[dict]:
    return [m for m in config.get("verification_methods", []) if m.get("enabled", True)]


def build_command(
    method: dict,
    target: str,
    port: int | None = None,
    port_range: dict | None = None,
) -> list[str]:
    tool = method["tool"]
    options = list(method.get("options", []))
    name = method["name"]
    if name in PORT_METHODS:
        if port is None:
            raise ValueError(f"{name} method requires a port")
        return [tool, *options, target, str(port)]
    if name == "tcp_scan":
        if not port_range:
            raise ValueError("tcp_scan requires port_range")
        # TCP connect scan(-sT), host discovery 생략(-Pn), DNS 생략(-n)
        return [
            tool,
            "-sT",
            "-Pn",
            "-n",
            *options,
            "-p",
            f"{port_range['start']}-{port_range['end']}",
            target,
        ]
    if name == "service_scan":
        ports = method.get("ports", [])
        if not ports:
            raise ValueError("service_scan requires ports")
        return [
            tool,
            "-sV",
            "-Pn",
            "-n",
            *options,
            "-p",
            ",".join(str(port) for port in ports),
            target,
        ]
    if name == "port_reverify":
        ports = method.get("ports", [])
        if not ports:
            raise ValueError("port_reverify requires ports")
        return [
            tool,
            "-sT",
            "-Pn",
            "-n",
            *options,
            "-p",
            ",".join(str(port) for port in ports),
            target,
        ]
    if name == "version_scan":
        ports = method.get("ports", [])
        if not ports:
            raise ValueError("version_scan requires ports")
        # --version-all은 tcpwrapped/무응답 포트에서 매우 오래 걸리므로
        # 경량 버전 탐지를 기본으로 사용한다(옵션으로 조정 가능).
        return [
            tool,
            "-sV",
            "--version-light",
            "-Pn",
            "-n",
            *options,
            "-p",
            ",".join(str(port) for port in ports),
            target,
        ]
    return [tool, *options, target]


def plan_items(config: dict) -> list[dict]:
    """실행/계획 대상 항목을 만든다.

    - enabled method만 대상으로 한다.
    - tcp/tcp_connectivity는 `ports` 목록의 각 포트마다 별도 항목을 만든다.
    - tcp_scan은 `port_range` 전체를 한 번에 스캔하는 항목 하나를 만든다.
    - Runner가 임의로 포트를 추가/선택하지 않는다.
    """
    target = str(config["target"])
    port_range = config.get("port_range")
    items: list[dict] = []
    step = 0
    for method in enabled_methods(config):
        name = method["name"]
        if name in PORT_METHODS:
            for port in method.get("ports", []):
                step += 1
                items.append(
                    {
                        "step": step,
                        "method": method,
                        "name": name,
                        "tool": method["tool"],
                        "port": port,
                        "port_range": None,
                        "command": build_command(method, target, port),
                        "timeout_seconds": method.get("timeout_seconds"),
                    }
                )
        elif name == "tcp_scan":
            step += 1
            items.append(
                {
                    "step": step,
                    "method": method,
                    "name": name,
                    "tool": method["tool"],
                    "port": None,
                    "port_range": port_range,
                    "command": build_command(method, target, port_range=port_range),
                    "timeout_seconds": method.get("timeout_seconds"),
                }
            )
        elif name in ("service_scan", "port_reverify", "version_scan"):
            step += 1
            items.append(
                {
                    "step": step,
                    "method": method,
                    "name": name,
                    "tool": method["tool"],
                    "port": None,
                    "port_range": None,
                    "command": build_command(method, target),
                    "timeout_seconds": method.get("timeout_seconds"),
                }
            )
        else:
            step += 1
            items.append(
                {
                    "step": step,
                    "method": method,
                    "name": name,
                    "tool": method["tool"],
                    "port": None,
                    "port_range": None,
                    "command": build_command(method, target),
                    "timeout_seconds": method.get("timeout_seconds"),
                }
            )
    return items


def _first_version_line(text: str) -> str | None:
    """출력에서 버전으로 볼 수 있는 첫 줄을 찾는다. 오류 문구는 건너뛴다."""
    for line in (text or "").splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        lowered = candidate.lower()
        if any(marker in lowered for marker in VERSION_ERROR_MARKERS):
            continue
        return candidate
    return None


def detect_tool_version(tool: str) -> tuple[str | None, list[str] | None]:
    """Tool 버전과, 버전을 확인한 probe 명령을 반환한다.

    - Tool별 올바른 옵션을 사용한다(예: ping/tracepath는 -V, nc는 -h).
    - 오류 문구(invalid option 등)는 버전으로 채택하지 않는다.
    """
    probes = TOOL_VERSION_PROBES.get(tool, DEFAULT_VERSION_PROBES)
    for args in probes:
        try:
            completed = subprocess.run(
                [tool, *args],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        combined = "\n".join(
            part for part in (completed.stdout, completed.stderr) if part
        )
        version = _first_version_line(combined)
        if version:
            return version, [tool, *args]
    return None, None


def classify_observation(method: dict, returncode: int, stderr: str) -> str:
    name = method["name"]
    if name == "icmp":
        if returncode == 0:
            return "icmp_response_observed"
        return "icmp_no_response_observed"
    if name in PORT_METHODS:
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
    if name == "tcp_scan":
        if returncode == 0:
            return "port_scan_completed"
        return "scan_error"
    if name == "service_scan":
        if returncode == 0:
            return "service_scan_completed"
        return "scan_error"
    if name == "port_reverify":
        if returncode == 0:
            return "port_reverify_completed"
        return "scan_error"
    if name == "version_scan":
        if returncode == 0:
            return "version_scan_completed"
        return "scan_error"
    return "unknown"


def parse_nmap_ports(stdout_text: str) -> list[dict]:
    """nmap 일반 출력에서 (port, protocol, state) 목록을 파싱한다."""
    ports: list[dict] = []
    seen: set[tuple[int, str]] = set()
    for match in NMAP_PORT_RE.finditer(stdout_text or ""):
        port = int(match.group(1))
        protocol = match.group(2)
        state = match.group(3)
        key = (port, protocol)
        if key in seen:
            continue
        seen.add(key)
        ports.append({"port": port, "protocol": protocol, "state": state})
    return ports


def parse_nmap_state_counts(stdout_text: str) -> dict:
    """nmap의 'Not shown' 라인에서 상태별 포트 수를 파싱한다.

    예: 'Not shown: 642 filtered tcp ports (no-response), 355 closed tcp ports (conn-refused)'
    """
    counts: dict[str, int] = {}
    match = re.search(r"Not shown:\s*(.+)", stdout_text or "")
    if not match:
        return counts
    for number, state in re.findall(r"(\d+)\s+([a-z|]+)\s+tcp ports", match.group(1)):
        counts[state] = counts.get(state, 0) + int(number)
    return counts


def parse_nmap_services(stdout_text: str) -> list[dict]:
    """nmap -sV 출력에서 (port, protocol, state, service, details) 목록을 파싱한다."""
    services: list[dict] = []
    seen: set[tuple[int, str]] = set()
    for match in NMAP_SERVICE_RE.finditer(stdout_text or ""):
        port = int(match.group(1))
        protocol = match.group(2)
        key = (port, protocol)
        if key in seen:
            continue
        seen.add(key)
        services.append(
            {
                "port": port,
                "protocol": protocol,
                "state": match.group(3),
                "service": match.group(4),
                "details": (match.group(5) or "").strip() or None,
            }
        )
    return services


def build_cross_verification(results: list[dict]) -> list[dict]:
    """tcp_scan의 포트 상태와 tcp_connectivity 결과를 비교해 기록한다.

    이는 판정이 아니라 교차검증 관찰 기록이다. Runner는 이 결과로
    Finding/Risk를 만들지 않는다.
    """
    scan_states: dict[int, str] = {}
    for result in results:
        if result.get("method") == "tcp_scan" and isinstance(result.get("ports"), list):
            for entry in result["ports"]:
                scan_states[entry.get("port")] = entry.get("state")

    cross: list[dict] = []
    for result in results:
        if result.get("method") != "tcp_connectivity":
            continue
        port = result.get("port")
        if port is None:
            continue
        scan_state = scan_states.get(port)
        connectivity = result.get("observation_category")
        scan_open = bool(scan_state) and str(scan_state).startswith("open")
        connect_ok = connectivity == "tcp_connect_succeeded"
        if scan_state is None:
            comparison = "no_scan_observation"
        elif scan_open == connect_ok:
            comparison = "consistent"
        else:
            comparison = "discrepancy"
        cross.append(
            {
                "port": port,
                "scan_state": scan_state,
                "connectivity": connectivity,
                "comparison": comparison,
            }
        )
    return cross


def build_attack_surface(results: list[dict]) -> list[dict]:
    """External Discovery 결과를 포트 중심으로 통합한 관찰(Attack Surface)을 만든다.

    tcp_scan/port_reverify(포트 상태) + service_scan(서비스) +
    version_scan(애플리케이션/버전)을 포트 기준으로 결합한다.
    이는 관찰 통합이며 보안 판단이 아니다.
    """
    state_by_port: dict[int, str] = {}
    service_by_port: dict[int, str] = {}
    app_by_port: dict[int, str] = {}

    for result in results:
        method = result.get("method")
        if method in ("tcp_scan", "port_reverify") and isinstance(result.get("ports"), list):
            for entry in result["ports"]:
                state_by_port[entry.get("port")] = entry.get("state")
        elif method == "service_scan" and isinstance(result.get("services"), list):
            for entry in result["services"]:
                service_by_port[entry.get("port")] = entry.get("service")
        elif method == "version_scan" and isinstance(result.get("services"), list):
            for entry in result["services"]:
                service_by_port.setdefault(entry.get("port"), entry.get("service"))
                app_by_port[entry.get("port")] = entry.get("details") or entry.get("service")

    surface: list[dict] = []
    for port in sorted(set(state_by_port) | set(service_by_port) | set(app_by_port)):
        state = state_by_port.get(port)
        service = service_by_port.get(port)
        application = app_by_port.get(port)
        observed_open = bool(state) and str(state).startswith("open")
        if observed_open or service or application:
            surface.append(
                {
                    "port": port,
                    "protocol": "tcp",
                    "state": state,
                    "service": service,
                    "application_version": application,
                }
            )
    return surface


def run_item(item: dict, target: str, raw_root: Path) -> dict:
    method = item["method"]
    name = item["name"]
    tool = item["tool"]
    port = item["port"]
    command = item["command"]
    timestamp = iso_local()
    version, version_probe = detect_tool_version(tool)

    method_dir = raw_root / name
    method_dir.mkdir(parents=True, exist_ok=True)

    if port is not None:
        base = f"step-{item['step']}-{name}-{sanitize_id(tool)}-port-{port}"
    else:
        base = f"step-{item['step']}-{name}-{sanitize_id(tool)}"

    record: dict = {
        "step": item["step"],
        "method": name,
        "technique": method.get("technique"),
        "tool": tool,
        "tool_version": version,
        "tool_version_probe": version_probe,
        "target": target,
        "port": port,
        "port_range": item.get("port_range"),
        "scan_type": "connect" if (name == "tcp_scan" and "-sT" in command) else None,
        "ports": None,
        "services": None,
        "command": command,
        "execution_conditions": {
            "options": method.get("options", []),
            "timeout_seconds": method.get("timeout_seconds"),
        },
        "timestamp": timestamp,
        "exit_status": None,
        "execution_error": None,
        "observation_category": None,
        "raw_output": {"stdout_file": None, "stderr_file": None},
    }

    stdout_file = method_dir / f"{base}.stdout.txt"
    stderr_file = method_dir / f"{base}.stderr.txt"

    stdout_text = ""
    stderr_text = ""
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
        stdout_text = _as_text(exc.stdout)
        stderr_text = _as_text(exc.stderr)
    except OSError as exc:
        record["execution_error"] = f"os_error: {exc}"
        record["observation_category"] = "execution_error"
        stdout_text = ""
        stderr_text = str(exc)
    else:
        record["exit_status"] = completed.returncode
        record["observation_category"] = classify_observation(
            method, completed.returncode, completed.stderr or ""
        )
        stdout_text = completed.stdout or ""
        stderr_text = completed.stderr or ""

    # Timeout/Error 시에는 부분 출력을 파싱하지 않는다(잘못된 포트 상태 방지).
    if name in PORT_PARSE_METHODS and record["execution_error"] is None:
        parsed_ports = parse_nmap_ports(stdout_text)
        record["ports"] = parsed_ports
        if name == "tcp_scan":
            counts = parse_nmap_state_counts(stdout_text)
            counts["open"] = sum(
                1 for p in parsed_ports if str(p.get("state", "")).startswith("open")
            )
            record["port_state_counts"] = counts

    if name in SERVICE_PARSE_METHODS and record["execution_error"] is None:
        record["services"] = parse_nmap_services(stdout_text)

    stdout_file.write_text(stdout_text, encoding="utf-8")
    stderr_file.write_text(stderr_text, encoding="utf-8")
    record["raw_output"]["stdout_file"] = str(stdout_file)
    record["raw_output"]["stderr_file"] = str(stderr_file)
    return record


METHOD_LABELS = {
    "icmp": "ICMP",
    "tcp": "TCP",
    "path": "Path",
    "tcp_scan": "TCP Scan",
    "tcp_connectivity": "TCP Connectivity",
    "service_scan": "Service Scan",
    "port_reverify": "TCP Re-verify",
    "version_scan": "Version Scan",
}
OBSERVATION_LABELS = {
    "icmp_response_observed": "ICMP response observed",
    "icmp_no_response_observed": "ICMP response not observed",
    "tcp_connect_succeeded": "TCP connection succeeded",
    "tcp_connection_refused": "TCP connection refused",
    "tcp_connect_timeout": "TCP connect timeout",
    "tcp_connect_failed": "TCP connect failed",
    "path_observed": "Path observed",
    "path_incomplete": "Path incomplete",
    "port_scan_completed": "port scan completed",
    "service_scan_completed": "service scan completed",
    "port_reverify_completed": "port re-verify completed",
    "version_scan_completed": "version scan completed",
    "scan_error": "scan error",
    "execution_timeout": "Execution timeout",
    "execution_error": "Execution error",
}


def _method_label(name: str) -> str:
    return METHOD_LABELS.get(name, name)


def _observation_label(category: str | None) -> str:
    if not category:
        return "-"
    return OBSERVATION_LABELS.get(category, category)


def _relative_or_none(path_value: str | None, result_dir: Path) -> str | None:
    if not path_value:
        return None
    return os.path.relpath(path_value, result_dir)


def render_summary(execution_result: dict, result_dir: Path) -> str:
    """execution_result.json을 사람이 읽기 좋은 요약 Markdown으로 만든다.

    이 문서는 Execution Result 요약이며, Assessment Result/Finding/Risk/
    Remediation은 포함하지 않는다.
    """
    scope = execution_result.get("scope") or {}
    include = ", ".join(str(v) for v in scope.get("include", []))
    exclude = ", ".join(str(v) for v in scope.get("exclude", []))

    lines: list[str] = []
    lines.append(f"# {execution_result.get('objective', 'Assessment')} Execution Result")
    lines.append("")
    lines.append(f"- Execution ID: {execution_result.get('execution_id', '-')}")
    lines.append(f"- Objective: {execution_result.get('objective', '-')}")
    lines.append(f"- Test Case: {execution_result.get('test_case', '-')}")
    lines.append(f"- Procedure: {execution_result.get('procedure', '-')}")
    lines.append(f"- Target: {execution_result.get('target', '-')}")
    lines.append(f"- Target Type: {execution_result.get('target_type', '-')}")
    lines.append(f"- Assessment Perspective: {execution_result.get('assessment_perspective', '-')}")
    lines.append(f"- Scope: include=[{include}], exclude=[{exclude}]")
    lines.append(f"- Timezone: {execution_result.get('timezone', '-')}")
    lines.append(f"- Started At: {execution_result.get('started_at', '-')}")
    lines.append(f"- Finished At: {execution_result.get('finished_at', '-')}")
    lines.append(f"- Execution Mode: {execution_result.get('execution_mode', '-')}")
    port_range = execution_result.get("port_range")
    if isinstance(port_range, dict):
        lines.append(f"- Port Range: {port_range.get('start')}-{port_range.get('end')}")
    lines.append("")

    lines.append("## Verification Results")
    lines.append("")
    lines.append("| Step | Method | Technique | Tool | Port | Observation |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for result in execution_result.get("results", []):
        services = result.get("services")
        if isinstance(services, list) and services:
            is_version = result.get("method") == "version_scan"
            for entry in services:
                if is_version:
                    obs = entry.get("details") or entry.get("service") or "-"
                else:
                    obs = entry.get("service", "-")
                lines.append(
                    "| {step} | {method} | {technique} | {tool} | {port} | {obs} |".format(
                        step=result.get("step", "-"),
                        method=_method_label(result.get("method", "")),
                        technique=result.get("technique", "-"),
                        tool=result.get("tool", "-"),
                        port=entry.get("port", "-"),
                        obs=obs,
                    )
                )
            continue
        scan_ports = result.get("ports")
        if isinstance(scan_ports, list) and scan_ports:
            for entry in scan_ports:
                lines.append(
                    "| {step} | {method} | {technique} | {tool} | {port} | {obs} |".format(
                        step=result.get("step", "-"),
                        method=_method_label(result.get("method", "")),
                        technique=result.get("technique", "-"),
                        tool=result.get("tool", "-"),
                        port=entry.get("port", "-"),
                        obs=entry.get("state", "-"),
                    )
                )
        else:
            port = result.get("port")
            port_text = str(port) if port is not None else "-"
            lines.append(
                "| {step} | {method} | {technique} | {tool} | {port} | {obs} |".format(
                    step=result.get("step", "-"),
                    method=_method_label(result.get("method", "")),
                    technique=result.get("technique", "-"),
                    tool=result.get("tool", "-"),
                    port=port_text,
                    obs=_observation_label(result.get("observation_category")),
                )
            )
    lines.append("")

    state_counts: dict[str, int] = {}
    for result in execution_result.get("results", []):
        for state, count in (result.get("port_state_counts") or {}).items():
            state_counts[state] = state_counts.get(state, 0) + count
    if state_counts:
        lines.append("## Port State Summary")
        lines.append("")
        lines.append("| State | Count |")
        lines.append("| --- | --- |")
        for state, count in state_counts.items():
            lines.append(f"| {state} | {count} |")
        lines.append("")

    cross = execution_result.get("cross_verification") or []
    if cross:
        lines.append("## Cross Verification")
        lines.append("")
        lines.append("| Port | Scan State | Connectivity | Comparison |")
        lines.append("| --- | --- | --- | --- |")
        for entry in cross:
            lines.append(
                "| {port} | {scan} | {conn} | {cmp} |".format(
                    port=entry.get("port", "-"),
                    scan=entry.get("scan_state") or "-",
                    conn=_observation_label(entry.get("connectivity")),
                    cmp=entry.get("comparison", "-"),
                )
            )
        lines.append("")

    surface = execution_result.get("attack_surface") or []
    if surface:
        lines.append("## Attack Surface (Observation)")
        lines.append("")
        lines.append("| Port | Protocol | State | Service | Application / Version |")
        lines.append("| --- | --- | --- | --- | --- |")
        for entry in surface:
            lines.append(
                "| {port} | {proto} | {state} | {service} | {app} |".format(
                    port=entry.get("port", "-"),
                    proto=entry.get("protocol", "-"),
                    state=entry.get("state") or "-",
                    service=entry.get("service") or "-",
                    app=entry.get("application_version") or "-",
                )
            )
        lines.append("")

    lines.append("## Evidence")
    lines.append("")
    for result in execution_result.get("results", []):
        step = result.get("step", "-")
        method = _method_label(result.get("method", ""))
        lines.append(f"### Step {step} ({method})")
        raw = result.get("raw_output") or {}
        stdout_rel = _relative_or_none(raw.get("stdout_file"), result_dir)
        stderr_rel = _relative_or_none(raw.get("stderr_file"), result_dir)
        if stdout_rel:
            lines.append(f"- [stdout]({stdout_rel})")
        if stderr_rel:
            lines.append(f"- [stderr]({stderr_rel})")
        lines.append("")

    lines.append(
        "> This document is an Execution Result summary only. "
        "It records what was executed and observed and does not evaluate or judge the result."
    )
    lines.append("")
    return "\n".join(lines)


def write_summary(result_dir: Path, execution_result: dict) -> Path:
    summary_file = result_dir / "summary.md"
    summary_file.write_text(render_summary(execution_result, result_dir), encoding="utf-8")
    return summary_file


def summarize_dir(result_dir: Path) -> int:
    result_file = result_dir / "execution_result.json"
    if not result_file.is_file():
        print(f"[ERROR] execution_result.json not found: {result_file}", file=sys.stderr)
        return 2
    try:
        execution_result = json.loads(result_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"[ERROR] failed to read execution result: {exc}", file=sys.stderr)
        return 2
    summary_file = write_summary(result_dir, execution_result)
    print(f"[DONE] summary: {summary_file}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="DO-EXT-001 Reachability Execution Runner")
    parser.add_argument("--config", help="configuration YAML path")
    parser.add_argument(
        "--summarize",
        metavar="RESULT_DIR",
        help="regenerate summary.md from an existing execution_result.json",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--validate-only", action="store_true", help="validate and print plan (default)")
    mode.add_argument("--execute", action="store_true", help="execute the procedure")
    args = parser.parse_args()

    if args.summarize:
        return summarize_dir(Path(args.summarize))

    if not args.config:
        parser.error("--config is required unless --summarize is used")

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

    items = plan_items(config)
    print(f"[OK] configuration valid: {config_path}")
    print(f"[OK] target: {config['target']} ({config.get('target_type')})")
    print(f"[OK] perspective: {config.get('assessment_perspective')}")
    print(f"[OK] enabled methods: {[m['name'] for m in enabled_methods(config)]}")
    print(f"[OK] planned invocations: {len(items)}")
    for item in items:
        label = item["name"] + (f" port {item['port']}" if item["port"] else "")
        print(f"  - step {item['step']}: {label} via {item['tool']}: {item['command']}")

    if not execute:
        print("[VALIDATE-ONLY] no command executed. Use --execute to run.")
        return 0

    execution_id = config.get("execution_id") or (
        local_now().strftime("%Y%m%dT%H%M%S")
        + "-"
        + sanitize_id(config["objective"])
    )
    output_root = resolve_output_dir(config["evidence"]["output_dir"]) / sanitize_id(execution_id)
    raw_root = output_root / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)

    started_at = iso_local()
    results: list[dict] = []
    for item in items:
        label = item["name"] + (f" port {item['port']}" if item["port"] else "")
        print(f"[RUN] step {item['step']}: {label} via {item['tool']}")
        results.append(run_item(item, str(config["target"]), raw_root))
    finished_at = iso_local()
    cross_verification = build_cross_verification(results)
    attack_surface = build_attack_surface(results)

    execution_result = {
        "execution_id": execution_id,
        "objective": config.get("objective"),
        "test_case": config.get("test_case"),
        "procedure": config.get("procedure"),
        "target": config.get("target"),
        "target_type": config.get("target_type"),
        "assessment_perspective": config.get("assessment_perspective"),
        "scope": config.get("scope"),
        "port_range": config.get("port_range"),
        "timezone": local_tzname(),
        "started_at": started_at,
        "finished_at": finished_at,
        "execution_mode": "execute",
        "results": results,
        "cross_verification": cross_verification,
        "attack_surface": attack_surface,
        "notes": (
            "Execution Result only. Observations are not Pass/Fail, Risk, "
            "Vulnerability, or Finding. Assessment Result is a separate step. "
            "tcp_scan reports port states from the configured port_range; "
            "tcp_connectivity reports TCP connection observations on the "
            "configured ports."
        ),
    }

    result_file = output_root / "execution_result.json"
    result_file.write_text(
        json.dumps(execution_result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    summary_file = write_summary(output_root, execution_result)
    print(f"[DONE] execution result: {result_file}")
    print(f"[DONE] summary: {summary_file}")
    print("[NOTE] observation_category is an observation, not a reachable/unreachable verdict.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
