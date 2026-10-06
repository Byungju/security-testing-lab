# Discovery Execution

## 목적

`execution/`은 Linux Server Discovery의 Test Procedure를 재현 가능하고 설정 가능한 방식으로 수행하기 위한 실행 구조를 관리한다.
현재 범위는 `DO-EXT-001 → TC-EXT-001-01 → TP-EXT-001-01`을 실행하는 것이며, 프로젝트 전체 공통 실행 엔진이 아니다.

```text
Linux Server
    ↓
Discovery
    ↓
Test Case / Test Procedure
    ↓
Execution
```

- Configuration으로 대상을 지정하고, Runner가 Procedure에 정의된 검증만 수행한다.
- Runner는 무엇을 실행하고 무엇을 관찰했는지를 기록한다.
- Runner는 검증 결과를 임의로 판단하지 않고 Finding을 생성하지 않는다.
- Assessment(Objective/Expected Result와의 비교·해석)는 별도 단계에서 수행한다.
- Agent 기반 실행 구조는 이 영역의 범위가 아니다.
- 향후 다른 Discovery Objective도 같은 Execution 구조를 재사용할 수 있도록 특정 Objective/Test Case 값은 Configuration에 둔다.

## 구조

```text
execution/
├── README.md
├── config/
│   └── do-ext-001.example.yaml
├── scripts/
│   └── run_discovery.py
└── results/            # 실행 시 생성, repository에 커밋하지 않음
```

- `config/`: 실행 환경값과 대상을 담는 Configuration. 실제 Target을 하드코딩하지 않는다.
- `scripts/`: Runner. Configuration을 읽어 검증하고 절차를 수행한다.
- `results/`: Evidence와 Execution Result가 저장되는 위치. `.gitignore`로 제외한다.

## Configuration 형식

- 형식: YAML.
- 이유: 사람이 읽고 수정하기 쉽고, 목록/중첩 구조(scope, verification_methods)를 자연스럽게 표현할 수 있다. Python 환경에 PyYAML이 제공된다.
- 실제 Target/환경값은 스크립트가 아니라 Configuration에만 둔다.
- 값이 placeholder(`<TARGET>`, `<PORT>` 등)이면 Runner는 실행하지 않는다.

Configuration Schema:

| 필드 | 의미 | 필수 |
| --- | --- | --- |
| execution_id | 실행 식별자(비우면 Runner가 생성) | 선택 |
| objective | Objective ID | 필수 |
| test_case | Test Case ID | 필수 |
| procedure | Test Procedure ID | 필수 |
| target | 대상 주소(hostname 또는 IPv4) | 필수 |
| target_type | 대상 유형(예: linux-server) | 필수 |
| assessment_perspective | 평가 관점(예: external) | 필수 |
| scope.include | 대상이 포함되어야 하는 범위 | 필수 |
| scope.exclude | 제외 대상 | 선택 |
| verification_methods | 수행할 검증 방식 목록 | 필수 |
| verification_methods[].name | 방식 이름(icmp / tcp / path) | 필수 |
| verification_methods[].technique | Verification Method / Technique 명 | 필수 |
| verification_methods[].tool | 사용할 Tool(허용 목록 내) | 필수 |
| verification_methods[].options | Tool 옵션 목록 | 선택 |
| verification_methods[].timeout_seconds | Timeout(초) | 필수 |
| verification_methods[].enabled | 수행 여부 | 선택(기본 true) |
| verification_methods[].ports | tcp 방식에서 관찰할 포트 목록 | tcp일 때 필수([] 가능) |
| evidence.output_dir | Evidence 저장 상위 디렉터리 | 필수 |
| environment.allowed_tools | 허용 Tool 목록 | 필수 |
| environment.allow_execution | 실제 실행 허용 플래그 | 필수 |

### Verification Method별 의미

- `icmp`: 주 Reachability 검증이다. ICMP 응답 성공, 응답 없음, 실행 오류, 권한/환경 문제를 서로 구분하며, ICMP 응답이 없다는 이유만으로 Target을 unreachable이라고 단정하지 않는다.
- `tcp`: 선택적/보조 Reachability 검증이다. `ports`에 명시된 포트에 대해서만 TCP 연결 가능 여부를 관찰한다. `ports`가 비어 있으면 TCP 검증을 실행하지 않으며, 임의 포트를 선택하거나 Port Scan을 수행하지 않는다. TCP 결과는 Port Discovery 결과가 아니다.
- `path`: diagnostic evidence 수집용 보조 방법이다. Path observation 결과가 Reachability 최종 판단을 직접 결정하지 않는다.
- UDP는 이번 DO-EXT-001 구현에 포함하지 않는다. 무응답만으로 비도달을 판단하기 어렵고 현재 목적이 Port Discovery가 아니기 때문이다. 필요 시 별도 Verification Method와 Evidence 해석 기준을 검토해 추가한다.

## Runner 사용

```text
python3 assessments/linux-server/discovery/execution/scripts/run_discovery.py \
    --config assessments/linux-server/discovery/execution/config/<config>.yaml --validate-only

python3 assessments/linux-server/discovery/execution/scripts/run_discovery.py \
    --config assessments/linux-server/discovery/execution/config/<config>.yaml --execute

python3 assessments/linux-server/discovery/execution/scripts/run_discovery.py \
    --summarize assessments/linux-server/discovery/execution/results/<execution_id>
```

- 기본 동작은 `--validate-only`이다. Configuration/대상/범위/도구를 검증하고 실행 계획만 출력한다.
- `--execute`는 `environment.allow_execution: true`인 경우에만 실제로 Tool을 실행한다.
- `--execute`라도 target이 placeholder이거나 필수 설정이 누락되면 실행하지 않는다.

Runner 흐름:

```text
Load Configuration
        ↓
Validate Configuration
        ↓
Validate Target / Scope
        ↓
Select Enabled Verification Method
        ↓
Validate Method-specific Configuration
        ↓
Invoke Selected Tool
        ↓
Capture Raw Output
        ↓
Store Evidence
        ↓
Generate Structured Execution Result
```

## Evidence 저장 구조

```text
results/<execution_id>/
├── summary.md
├── execution_result.json
└── raw/
    ├── icmp/
    │   └── step-1-icmp-ping.stdout.txt / .stderr.txt
    ├── tcp/
    │   └── step-2-tcp-nc-port-443.stdout.txt / .stderr.txt
    ├── tcp_scan/
    │   └── step-1-tcp_scan-nmap.stdout.txt / .stderr.txt
    ├── tcp_connectivity/
    │   └── step-2-tcp_connectivity-nc-port-22.stdout.txt / .stderr.txt
    └── path/
        └── step-3-path-tracepath.stdout.txt / .stderr.txt
```

- `summary.md`: 사람이 Execution Result를 빠르게 검토하기 위한 읽기용 요약이다. `execution_result.json` 내용을 사람이 읽기 좋게 표현하고, Raw Evidence를 상대 경로로 연결한다. Assessment Result/Finding/Risk/Remediation은 포함하지 않는다.
- `execution_result.json`: 구조화된 Execution Result이다.
- `raw/`: Verification Method별 Raw Evidence이다.
- Runner는 실행 완료 시 `summary.md`를 자동 생성한다. `--summarize <result_dir>`로 기존 `execution_result.json`에서 `summary.md`만 다시 생성할 수 있다(Raw Evidence는 변경하지 않음).

Evidence에 포함되는 정보: Execution ID, Target, Assessment Perspective, Timestamp, Verification Method, Tool, Tool Version, Tool Version Probe, 실행 조건, Command/실행 방식, Raw Output, Exit Status, Execution Error, Observation. TCP의 경우 관찰한 port를 함께 기록한다.

- `tool_version`은 Tool별 올바른 옵션(ping/tracepath는 `-V`, nc는 `-h` 등)으로 확인한다. 오류 문구(`invalid option` 등)는 버전으로 채택하지 않는다.
- `tool_version_probe`는 버전을 확인한 probe 명령을 기록하여 검증 가능하게 한다. 버전을 확인하지 못하면 두 필드 모두 null이 될 수 있다.

- Timestamp는 로컬 시간과 타임존 오프셋을 포함한다(예: `2026-10-02T14:29:30+09:00`). `execution_result.json`에는 `timezone`, `started_at`, `finished_at`, 각 result의 `timestamp` 필드로 기록한다.

### Port Scan 관련 필드 (DO-EXT-002)

- `port_range`: 스캔 대상 TCP 포트 범위(config의 `port_range`)이다.
- `ports`: tcp_scan 결과의 포트별 상태 목록(`{port, protocol, state}`)이다.
- `port_state_counts`: 포트 상태별 집계(예: `open`, `filtered`, `closed`)이다. nmap의 `Not shown` 라인과 open 포트 수에서 파생한다.
- `cross_verification`: tcp_scan의 포트 상태와 tcp_connectivity 결과를 비교한 기록이다.
  - `consistent` / `discrepancy` / `no_scan_observation`으로 표시하며, 이는 판정이 아니라 관찰 기록이다.
  - Runner는 이 결과로 Finding/Risk를 만들지 않는다.
- summary.md에는 `Port State Summary`와 `Cross Verification` 섹션이 추가된다(해당 데이터가 있을 때만).

### Port Re-verification (DO-EXT-002)

광역/고속 스캔은 대상의 rate-limiting 등으로 일부 포트가 no-response로 관찰되어 누락(false negative)될 수 있다. 이를 보완하기 위해 후보 포트를 **저부하 타겟 확인**으로 재검증한다.

- Verification Method: TCP port re-verification.
- method `port_reverify`: `nmap -sT -Pn -n [options] -p <ports> <target>` (기본 타이밍), config의 `ports`만 스캔한다. 결과는 `ports`(포트별 상태)로 기록한다.
- 권장 흐름: `tcp_scan`(port_range, 후보 발견) → `port_reverify`(후보 저부하 재확인) → `service_scan`(서비스 식별).
- 스캔 타이밍/옵션은 Observation Condition으로 기록하며, 포트 상태는 시점/조건 의존 관찰로 취급한다.
- config 예: `config/do-ext-002-reverify.yaml`.

- Raw Output은 가능한 한 원본 그대로 보존하고, Verification Method별 디렉터리(`raw/icmp`, `raw/tcp`, `raw/path`)로 남긴다.
- 기존 Evidence 저장 규칙(`results/<execution_id>/`)을 유지하며, 별도 중복 구조를 만들지 않는다.

## Execution Result와 Assessment Result의 경계

- Execution Result: 실제로 무엇을 실행했고 무엇이 관찰되었는지를 기록한다(`execution_result.json`).
- Assessment Result: Objective/Expected Result 기준의 평가로, 실행 도구가 생성하지 않는다.
- Runner의 `observation_category`는 관찰 분류이며, `reachable`/`unreachable` 같은 판정이 아니다.
- `unreachable`과 `execution error`를 동일하게 처리하지 않는다. 실행 실패는 `execution_error`로 분리한다.

## 안전장치

- Target이 placeholder이면 실행하지 않는다.
- 필수 설정 누락 시 실행하지 않는다.
- Scope(include/exclude)와 Target 불일치 시 실행하지 않는다.
- 허용 Tool 목록 외 도구는 실행하지 않는다.
- Shell을 사용하지 않고 인자 목록으로 실행한다.
- Timeout을 적용한다.
- Raw Evidence를 보존한다.
- TCP: `ports`가 비어 있으면 TCP 검증을 실행하지 않는다.
- TCP: 임의의 포트를 자동으로 선택하지 않는다.
- TCP: Port Scan을 수행하지 않는다.
- TCP: 결과를 Port Discovery 결과로 표현하지 않는다.
- 기본은 `--validate-only`이며, 실제 실행은 명시적 플래그와 설정 플래그가 모두 필요하다.

## 실행 책임 범위

- 포함: Configuration → Execution Runner → Tool → Raw Evidence → Execution Result.
- 제외(이 영역의 책임이 아님): Assessment Result, Finding, Risk Assessment, Remediation.

## 실행 구조와 Tool의 관계

```text
Verification Method
    ↓
Tool
    ↓
Execution
```

- Tool은 프로젝트 공통 Tool Catalog(`tools/`)에서 관리하며, Execution 디렉터리에 중복 정의하지 않는다.
- 현재 등록된 Tool(ping, nc, traceroute)은 Linux Server Discovery에만 종속되지 않고, 향후 다른 Assessment에서도 재사용할 수 있다.
- 이번 단계에서 공통 Tool Catalog를 추가로 확장하지 않는다.

## 관련 문서

- `../procedures/TP-EXT-001-01.md`
- `../testcases/TC-EXT-001-01.md`
- `../objectives.md`
- `../../../../tools/README.md`, `../../../../tools/network/ping.md`, `../../../../tools/network/nc.md`, `../../../../tools/network/traceroute.md`
