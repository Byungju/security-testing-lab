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
│   └── run_reachability.py
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
| evidence.output_dir | Evidence 저장 상위 디렉터리 | 필수 |
| environment.allowed_tools | 허용 Tool 목록 | 필수 |
| environment.allow_execution | 실제 실행 허용 플래그 | 필수 |

## Runner 사용

```text
python3 assessments/linux-server/discovery/execution/scripts/run_reachability.py \
    --config assessments/linux-server/discovery/execution/config/<config>.yaml --validate-only

python3 assessments/linux-server/discovery/execution/scripts/run_reachability.py \
    --config assessments/linux-server/discovery/execution/config/<config>.yaml --execute
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
Select Verification Method
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
├── execution_result.json
└── raw/
    ├── step-1-icmp-ping.stdout.txt
    ├── step-1-icmp-ping.stderr.txt
    ├── step-2-tcp-nc.stdout.txt
    └── step-2-tcp-nc.stderr.txt
```

Evidence에 포함되는 정보: Execution ID, Target, Assessment Perspective, Timestamp, Verification Method, Tool, Tool Version, 실행 조건, Command/실행 방식, Raw Output, Exit Status, Execution Error, Observation.

- Raw Output은 가능한 한 원본 그대로 보존하고, 별도 파일로 남긴다.

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
