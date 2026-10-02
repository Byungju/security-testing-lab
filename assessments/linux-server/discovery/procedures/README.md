# Discovery Test Procedures

이 디렉터리는 Linux Server Discovery Test Case를 실제로 수행하기 위한 Test Procedure를 저장한다.
이 문서는 Discovery Test Procedure의 공통 규칙과 Schema를 정의한다.

- 상위 공통 정의는 `assessments/README.md`의 Test Case Definition과 Test Execution Model을 따른다.
- Test Case 정의는 `../testcases/`에서 관리하고, Test Procedure는 이 디렉터리에서 관리한다.
- 개별 Test Procedure는 이 문서의 Schema를 사용하고, 파일명은 Test Procedure ID와 동일하게 한다(예: `TP-EXT-001-01.md`).

## Test Procedure의 목적

- Test Case를 실제로 수행하기 위한 구체적인 절차를 정의한다.
- Test Case가 평가 대상과 평가 목적을 정의한다면, Test Procedure는 실제 평가 수행의 순서와 관찰 지점을 정의한다.

## Test Procedure와 Test Case 관계

기본 연결은 다음과 같다.

```text
Objective
    ↓
Test Case
    ↓
Test Procedure
```

- Test Case : Test Procedure 관계를 1:1로 고정하지 않는다.
- 향후 하나의 Test Case에 여러 Test Procedure가 필요할 수 있다.

```text
TC-EXT-001-01
    ├── TP-EXT-001-01
    └── TP-EXT-001-02

DO-EXT-002
    └── TC-EXT-002-01
        └── TP-EXT-002-01
```

- 하나의 Test Procedure가 여러 Test Case에서 부분 재사용될 수 있으나, 완전한 재사용은 지양하고 Test Case의 관찰 목적에 맞게 작성한다.

## Test Procedure ID 규칙

Discovery Test Procedure는 다음 형식을 사용한다.

```text
TP-<Perspective>-<Objective Number>-<Sequence>
```

예:

```text
TP-EXT-001-01
```

각 구성 요소의 의미는 다음과 같다.

- `TP`: Test Procedure를 나타낸다.
- `EXT`: External Discovery를 나타낸다.
- `001`: 연결된 Objective 번호를 나타낸다.
- `01`: 해당 Objective/Test Case의 Test Procedure 순번을 나타낸다.

향후 다음 유형을 수용할 수 있도록 구조 자체는 확장 가능하게 유지한다.

```text
EXT
INT
VULN
CONF
COMP
```

## Test Procedure 공통 필드

| 필드 | 의미 | 필수 여부 |
| --- | --- | --- |
| Test Procedure ID | Test Procedure의 고유 식별자이다. | 필수 |
| Related Objective | 이 Procedure가 연결된 Objective의 식별자와 이름이다. | 필수 |
| Related Test Case | 이 Procedure가 수행하는 Test Case의 식별자와 이름이다. | 필수 |
| Title | Test Procedure의 짧은 이름이다. | 필수 |
| Purpose | 이 Procedure를 수행하는 이유이다. | 필수 |
| Scope | Procedure가 다루는 범위와 다루지 않는 범위이다. | 조건부 |
| Preconditions | Procedure 수행 전에 충족되어야 하는 조건이다. | 필수 |
| Procedure Steps | 순차적으로 수행하는 단계 목록이다. | 필수 |
| Observation Points | 각 단계에서 관찰해야 하는 내용이다. | 필수 |
| Evidence Collection | 각 단계에서 확보해야 하는 Evidence의 요구사항이다. | 필수 |
| Expected Observation | 단계에서 기대되는 관찰 결과이다. | 필수 |
| Completion Criteria | Procedure를 종료하는 조건이다. | 필수 |
| Notes | 제약, 판단 근거, 참고 사항이다. | 선택 |

- `Expected Observation`은 각 Step에 포함해도 되지만, 재검토를 위해 통합 항목으로도 둘 수 있다.
- `Scope`는 Test Case의 Scope로 충분한 경우 생략할 수 있다.

## Procedure Steps 구성

Procedure Steps는 순차적인 작업 단위로 구성하며, 각 Step은 다음을 포함한다.

```text
Step N
  Action
  Observation
  Evidence
```

- Action: 실제로 수행하는 작업이다.
- Observation: 그 단계에서 관찰해야 하는 내용이다.
- Evidence: 그 단계에서 남겨야 하는 Evidence이다.

## Evidence와 Result의 경계

Test Procedure는 어떤 Evidence를 수집해야 하는지와 어떤 관찰 결과가 필요한지를 정의한다.
실제 Evidence 데이터와 Actual Result / Assessment Result는 실제 테스트 실행 단계에서 기록한다.

```text
Test Procedure
    ↓
Evidence Requirements
    ↓
[실제 실행]
    ↓
Actual Evidence
    ↓
Actual Result
    ↓
Assessment Result
```

- Test Procedure 문서에는 Actual Evidence, Actual Result, Assessment Result의 실제 값을 기록하지 않는다.
- Finding은 Procedure 단계에서 미리 정의하지 않고, 실행 결과와 평가 기준에 따라 이후 판단한다.

## Tool Catalog와의 관계

- Procedure는 Verification Method / Technique과 사용 Tool을 참조할 수 있다.
- Tool의 상세 설명·사용법은 프로젝트 공통 Tool Catalog(`tools/`)에서 관리하며, Procedure에 중복 작성하지 않는다.
- Tool은 Objective를 정의하지 않는다. Objective와 Verification Method를 기준으로 Tool을 선택한다.
- 하나의 Technique에 여러 Tool, 하나의 Tool에 여러 Technique이 연결될 수 있다.
- Tool 실행 결과는 Evidence로 남기며, Evidence 자체를 Assessment Result로 취급하지 않는다.

## 작성 원칙

- Procedure는 사람이 읽고 그대로 수행할 수 있을 정도로 구체적으로 작성한다.
- 특정 도구 자체를 방법론으로 정의하지 않는다. 필요한 경우 실제 수행에 사용하는 도구나 명령을 Procedure에 기술할 수 있다.
- 중요한 것은 무엇을 수행하는가, 무엇을 관찰하는가, 무엇을 Evidence로 남기는가를 명확히 하는 것이다.
- Procedure는 특정 도구에 종속되지 않도록 작성한다.
