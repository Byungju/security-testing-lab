# Discovery Test Cases

이 디렉터리는 Linux Server Discovery Objective를 검증하는 개별 Test Case를 저장한다.
이 문서는 Discovery Test Case의 공통 작성 규칙과 Schema를 정의한다.

- 상위 공통 정의는 `assessments/README.md`의 Test Case Definition과 Test Execution Model을 따른다.
- 이 문서는 Discovery 단계에 적용하기 위한 구체화이며, 공통 모델과 충돌하지 않도록 작성한다.
- 개별 Test Case는 이 문서의 Schema를 사용하고, 파일명은 Test Case ID와 동일하게 한다(예: `TC-EXT-001-01.md`).

## 기본 관계

```text
Discovery Objective
        ↓
Test Case
        ↓
Test Procedure
        ↓
Evidence
        ↓
Actual Result
        ↓
Assessment Result
        ↓
Finding
```

- Test Case 하나는 하나의 Objective를 검증하는 독립적인 평가 단위가 될 수 있다.
- 하나의 Objective에 여러 Test Case가 연결될 수 있다.

```text
DO-EXT-001
    └── TC-EXT-001-01

DO-EXT-002
    ├── TC-EXT-002-01
    └── TC-EXT-002-02
```

- 현재는 DO-EXT-001의 Test Case만 작성되어 있으며, 다른 Test Case는 필요 시점에 추가한다.

## Test Case Schema

Discovery Test Case의 표준 구조는 다음 필드로 구성한다.
이 Schema는 `assessments/README.md`의 공통 Schema를 Discovery 단계에 맞게 구체화한 것이며, Discovery 관점을 나타내는 `Assessment Perspective`와 결과 추적을 위한 `Finding`을 포함한다.

| 필드 | 의미 | 필수 여부 |
| --- | --- | --- |
| Test Case ID | Test Case의 고유 식별자이다. | 필수 |
| Objective | 이 Test Case가 검증하는 Discovery Objective의 식별자와 이름이다. | 필수 |
| Title | Test Case의 짧은 이름이다. | 필수 |
| Purpose | 이 Test Case를 수행하는 이유이다. | 필수 |
| Scope | Test Case가 다루는 범위와 다루지 않는 범위이다. | 조건부 |
| Target | 검증 대상이다. | 필수 |
| Assessment Perspective | 어느 관점(External Discovery / Internal Validation)에서 수행하는지 나타낸다. | 필수 |
| Preconditions | 수행 전에 충족되어야 하는 조건이다. | 조건부 |
| Test Method | 의도한 검증 방법의 개념 수준 설명이다. 도구·명령어는 포함하지 않는다. | 필수 |
| Expected Result | 수행 전에 정의한 기대 상태이다. | 필수 |
| Evidence Requirements | 수집해야 하는 Evidence의 요구사항이다. | 필수 |
| Actual Result | 수행 후 실제로 관찰된 상태이다. | 수행 후 채움 |
| Assessment Result | Actual Result를 Objective와 Expected Result 관점에서 해석한 결과이다. | 수행 후 채움 |
| Finding | 추적이 필요한 보안상 문제로 식별되었는지 여부이다. | 수행 후 채움 |
| Notes | 판단 근거, 제약, 참고 사항이다. | 선택 |

### 필드 간 경계

- Objective: 무엇을 확인해야 하는가를 나타낸다.
- Test Case: 하나의 독립적인 평가 단위로 무엇을 검증하는가를 나타낸다.
- Test Method / Procedure: 실제로 어떻게 검증하는가를 나타낸다. Test Case의 Test Method는 개념 수준이며, 구체적인 실행 절차는 Test Procedure에서 정의한다.
- Evidence: 무엇이 관찰되었음을 증명하는가를 나타낸다.
- Actual Result: 실제로 무엇이 관찰되었는가를 나타낸다.
- Assessment Result: 관찰 결과를 Objective와 Expected Result 관점에서 어떻게 해석하는가를 나타낸다.
- Finding: 추적이 필요한 보안상 문제로 식별되었는가를 나타낸다.

## Test Procedure 관리

Test Procedure는 Test Case와 분리된 별도의 관리 단위이며, `../procedures/`에서 관리한다.

- 공통 규칙과 Schema: `../procedures/README.md`.
- 개별 Test Procedure 파일명은 Test Procedure ID와 동일하게 한다(예: `TP-EXT-001-01.md`).
- Test Case는 평가 정의, Expected Result, Evidence Requirements를 정의하고, 실제 수행 순서·관찰 지점·Evidence 수집은 Test Procedure에서 정의한다.
- Test Case : Test Procedure 관계는 1:1로 고정하지 않는다.

## Test Case ID 규칙

Discovery Test Case는 다음 형식을 사용한다.

```text
TC-<Perspective>-<Objective Number>-<Sequence>
```

예:

```text
TC-EXT-001-01
```

각 구성 요소의 의미는 다음과 같다.

- `TC`: Test Case를 나타낸다.
- `EXT`: External Discovery를 나타낸다.
- `001`: 연결된 Objective 번호를 나타낸다.
- `01`: 해당 Objective 내 Test Case 순번을 나타낸다.

향후 다음 유형을 수용할 수 있도록 구조 자체는 확장 가능하게 유지한다.

```text
EXT
INT
VULN
CONF
COMP
```

## 작성 원칙

- Test Case는 하나의 Objective에 집중하며, 서로 관계없는 여러 Objective를 무분별하게 검증하지 않는다.
- Objective의 내용을 그대로 복사하지 않고, Test Case가 수행 가능한 평가 단위가 되도록 구체화한다.
- Test Case에는 특정 도구를 방법론으로 확정하지 않는다. 필요한 경우 Test Procedure에서 실제 도구나 명령을 사용할 수 있다.
- Test Method는 개념 수준의 의도이며, 구체적인 수행 절차는 Test Procedure에서 정의한다.
- Test Procedure는 특정 도구에 종속되지 않도록 작성한다. 중요한 것은 무엇을 확인·관찰하고 무엇을 Evidence로 남기는가이다.
- Actual Result, Assessment Result, Finding은 실행 전에는 값을 추측해서 채우지 않고, 수행 이후에 채운다.
- Actual Result는 관찰 사실, Assessment Result는 해석이며, 두 내용을 한 문장에 섞지 않는다.
- Assessment Result는 Actual Result의 관찰 사실을 그대로 반복하지 않고 Objective와 Expected Result 관점에서 해석한다.
- 모든 Test Case가 Finding을 생성하는 것은 아니다. Result와 평가 기준을 통해 보안상 문제가 확인된 경우에만 Finding으로 연결한다.
- Evidence Requirements는 무엇을/어떤 대상/언제/어떤 관점/어떤 방법으로 관찰했는지와 원본 재검토 가능성을 추적할 수 있어야 한다.
- Evidence는 원본 데이터를 재검토할 수 있는 수준으로 남긴다.
