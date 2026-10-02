# Security Assessment

## Overview

`assessments/` 디렉터리는 이 프로젝트에서 사용하는 공통 Security Assessment 프로세스를 정의한다.
이 문서는 평가 작업의 상위 문서이며, Linux Server처럼 특정 대상을 다루는 문서가 이 프로세스를 구체적인 대상에 적용한다.

이 프로젝트는 Security Assessment를 단일 스캔이나 일회성 테스트가 아니라, 관찰한 증적을 Finding, Risk, Remediation으로 연결하는 구조화된 프로세스로 본다.
현재 프로젝트는 NIST SP 800-115를 학습하면서 이 프로세스를 실무 경험에 맞게 발전시키는 단계에 있다.

**NIST SP 800-115와의 관계**

- NIST SP 800-115는 이 프로젝트의 중요한 근거이지만, 유일한 기준은 아니다.
- NIST SP 800-115는 기술적 테스트·점검 기법과 Planning, Execution, Post-Execution 단계를 제시하며, 아래의 종단 간(end-to-end) 프로세스를 정의하지는 않는다.
- 이 문서의 Lifecycle은 NIST 개념을 이 프로젝트의 평가에 맞게 정리하고 확장한 프로젝트 실무 방식이다.
- NIST SP 800-115를 기반으로 하는 부분은 **NIST SP 800-115 basis**로, 그를 넘어 확장한 부분은 **Project practice**로 표기한다.

## Assessment Lifecycle

이 프로젝트는 평가를 다음과 같은 흐름으로 구성한다.

```text
Target Definition
        ↓
Scope Definition
        ↓
Discovery
        ↓
Attack Surface Identification
        ↓
Security Requirements
        ↓
Test Objective
        ↓
Test Case
        ↓
Test Procedure
        ↓
Evidence Collection
        ↓
Result Analysis
        ↓
Finding
        ↓
Risk Assessment
        ↓
Remediation
        ↓
Regression Test
        ↓
Compliance Assessment
        ↓
Final Report
```

아래 표는 각 단계를 요약한다.
이 Lifecycle은 프로젝트 실무 방식이며, NIST SP 800-115가 정의한 Lifecycle이 아니다.
각 단계의 세부 구현은 이 문서에서 의도적으로 확정하지 않는다.

| 단계 | Purpose | 주요 활동 | 주요 Output | 다음 단계와의 관계 |
| --- | --- | --- | --- | --- |
| Target Definition | 무엇을 평가할지 정한다. | 평가 대상(예: 서버, 애플리케이션, 장치)을 식별한다. | Target 정의 | Scope Definition으로 이어진다. |
| Scope Definition | 평가의 경계를 정한다. | 범위 내·외 자산, 환경, 제약을 정의한다. | Assessment Scope | Discovery의 범위를 한정한다. |
| Discovery | 무엇이 존재하고 어떻게 노출되는지 식별한다. | 호스트, 포트, 서비스, 애플리케이션, 버전을 식별한다. | Asset·Port/Service·Application Inventory | Attack Surface Identification으로 이어진다. |
| Attack Surface Identification | 노출된 진입점을 정리한다. | 노출된 포트·서비스·애플리케이션을 공격면으로 정리한다. | Initial Attack Surface | Security Requirements와 대상 선정으로 이어진다. |
| Security Requirements | 대상에 대해 무엇이 참이어야 하는지 정의한다. | 대상과 관련된 보안 요구사항과 기대 보안 상태를 정한다. | Security Requirements | Test Objective로 이어진다. |
| Test Objective | 평가로 무엇을 검증할지 진술한다. | 요구사항과 공격면을 구체적인 목표로 전환한다. | Test Objectives | Test Case로 이어진다. |
| Test Case | 무엇을 테스트할지 정의한다. | 하나의 목표에 대해 검증할 조건을 정의한다. | Test Cases | Test Procedure로 이어진다. |
| Test Procedure | 테스트를 어떻게 수행할지 정의한다. | Test Case를 수행하기 위한 절차와 조건을 기술한다. | Test Procedures | Evidence Collection으로 이어진다. |
| Evidence Collection | 무엇을 관찰했는지 기록한다. | 결과를 뒷받침할 만큼의 맥락과 함께 관찰을 기록한다. | Evidence | Result Analysis로 이어진다. |
| Result Analysis | 증적을 해석한다. | 관찰한 증적을 기대 동작·요구사항과 비교한다. | Analysis Results | Finding으로 이어진다. |
| Finding | 분석 결과의 결론을 진술한다. | 증적에 근거하여 관찰되었거나 충족되지 않은 내용을 기술한다. | Findings | Risk Assessment로 이어진다. |
| Risk Assessment | Finding의 중요도를 판단한다. | 대상 맥락과 관련된 영향과 가능성을 평가한다. | Risk Assessment | Remediation으로 이어진다. |
| Remediation | Finding을 어떻게 다룰지 정의한다. | 교정 조치를 권고하거나 적용한다. | Remediation Actions | Regression Test로 이어진다. |
| Regression Test | Remediation이 효과적인지 확인한다. | 영향받은 영역을 재테스트하여 조치를 검증한다. | Regression Results | Compliance Assessment로 이어진다. |
| Compliance Assessment | 대상이 요구사항을 충족하는지 확인한다. | 적용 가능한 요구사항의 충족 여부를 평가한다. | Compliance Results | Final Report로 이어진다. |
| Final Report | 평가 결과를 종합한다. | 범위, Finding, Risk, Remediation, Compliance 상태를 보고한다. | Final Report | 평가를 마무리한다. |

## Assessment Axes

이 프로젝트는 최소한 다음 세 가지 평가 관점(axis)을 구분한다.
이들은 서로 관련되어 있지만 동일하지 않으며, 이는 프로젝트의 분류이다.

- Vulnerability Assessment: 취약점과 그로 인한 노출을 식별하고 검증한다.
- Security Configuration Assessment: 시스템이 보안 구성 요구사항에 따라 구성되었는지 평가한다.
- Compliance Assessment: 적용 가능한 컴플라이언스 요구사항이 충족되는지 평가한다.

이 세 가지를 동일한 의미로 취급해서는 안 된다.

- 취약점이 발견되었다는 것이 곧 보안 구성 요구사항을 만족하지 못한다는 것을 의미하지 않는다.
- 보안 구성 요구사항을 만족하지 못했다는 것이 곧 컴플라이언스 요구사항을 충족하지 못한다는 것을 의미하지 않는다.
- 컴플라이언스 요구사항을 충족하지 못했다는 것이 곧 취약점이 존재한다는 것을 의미하지 않는다.
- 세 가지의 관계는 평가 대상 요구사항에 따라 달라지며, 증적에 근거하여 평가한다.

## Input / Process / Output

각 단계는 이전 단계의 Output을 입력으로 받아 다음 단계를 위한 Output을 생성한다.
주요 체인은 다음과 같다.

```text
Discovery
        ↓
Asset / Service Inventory
        ↓
Attack Surface
        ↓
Assessment Target
        ↓
Security Requirement
        ↓
Test Objective
        ↓
Test Case
        ↓
Test Procedure
        ↓
Evidence
        ↓
Result
        ↓
Finding
        ↓
Risk
        ↓
Remediation
```

- 이 체인은 Lifecycle 단계를 추적 가능한 순서로 연결한 프로젝트 실무 방식이다.
- 각 Output은 자신이 나온 Input으로 다시 추적될 수 있어야 하며, 이는 증적 기반 평가를 뒷받침한다.

## Test Case Definition

### 역할과 위치

- Test Case는 하나의 Objective를 검증하기 위한 독립적인 평가 단위이다.
- 전체 흐름에서 Test Case는 Test Objective 다음, Test Procedure 앞에 위치한다.
- 이 문서는 Test Case라는 평가 단위 자체의 공통 구조를 정의하며, 개별 Test Case는 다루지 않는다.
- 이 공통 구조는 Discovery 단계뿐 아니라 Vulnerability Assessment, Security Configuration Assessment, Compliance Assessment에도 적용할 수 있도록 한다.

### 개념 구분: Objective / Test Case / Test Procedure / Evidence / Result

| 개념 | 정의 | 대표 질문 |
| --- | --- | --- |
| Objective | 무엇을 확인하거나 검증해야 하는가를 나타낸다. | 무엇을 확인해야 하는가? |
| Test Case | 특정 Objective를 검증하기 위한 하나의 독립적인 평가 단위이다. | 무엇을 검증하는가? |
| Test Procedure | Test Case를 실제로 수행하기 위해 어떤 순서와 방법으로 검증하는가를 정의한다. | 어떻게 검증하는가? |
| Evidence | Test Procedure 수행 과정에서 수집되는 관찰 가능하고 재현 가능한 증거이다. | 무엇을 관찰했는가? |
| Result | Evidence를 바탕으로 도출한 실제 관찰 결과와 평가 결과이다. | 관찰 결과를 어떻게 해석하는가? |

- 다섯 개념의 관계는 다음과 같다.

```text
Objective
    ↓
Test Case
    ↓
Test Procedure
    ↓
Evidence
    ↓
Result
```

### Objective와 Test Case의 관계

- Objective 하나가 반드시 Test Case 하나와 1:1 관계를 갖는다고 가정하지 않는다.
- 하나의 Objective는 하나 이상의 Test Case로 검증할 수 있다.

```text
DO-EXT-002
Network Port Identification
        │
        ├── TC-EXT-002-01
        │   TCP Port Identification
        │
        └── TC-EXT-002-02
            UDP Port Identification
```

- 정리하면 Objective와 Test Case의 관계는 One Objective → One or More Test Cases이다.
- 반대로 하나의 Test Case가 서로 관계없는 여러 Objective를 무분별하게 검증하도록 설계하지 않는다.
- Test Case는 하나의 Objective(또는 밀접하게 관련된 단일 목적)에 집중하며, 그 목적이 ID와 Objective 필드에 드러나야 한다.

### Test Case와 Test Procedure의 경계

Test Case는 다음을 정의한다.

- 무엇을 검증하는가.
- 왜 검증하는가.
- 어떤 조건에서 검증하는가.
- 무엇을 기대하는가.
- 어떤 Evidence가 필요한가.

Test Procedure는 다음을 정의한다.

- 실제 검증을 어떤 순서로 수행하는가.
- 어떤 방법이나 도구를 사용하는가.
- 어떤 데이터를 수집하는가.

예를 들어 개념적으로 다음과 같이 구분한다. 이 예시는 개념 설명을 위한 것이며 실제 명령어나 도구를 정의하지 않는다.

```text
Test Case
"TCP 포트 노출 여부를 확인한다."

        ↓

Test Procedure
1. 대상 확인
2. TCP 포트 탐색 수행
3. 응답 포트 기록
4. 원본 결과 저장
```

- 즉 Test Case는 "무엇/왜/조건/기대/증적 요구"를 담당하고, Test Procedure는 "어떻게/순서/도구/수집"을 담당한다.
- 실제 절차와 도구는 이 문서에서 정의하지 않는다.

### 공통 Test Case 구조 (Schema)

프로젝트의 표준 Test Case 구조는 다음 필드로 구성한다.

| 필드 | 의미 | 필요한 이유 | 사용 단계 | 필수 여부 |
| --- | --- | --- | --- | --- |
| Test Case ID | Test Case의 고유 식별자이다. | 추적성과 참조를 가능하게 한다. | 정의 시점부터 결과까지 | 필수 |
| Objective | 이 Test Case가 검증하는 Objective의 식별자이다. | Test Case가 어떤 목적에 속하는지 명확히 한다. | 정의 시점 | 필수 |
| Title | Test Case의 짧은 이름이다. | 빠른 식별과 목록화에 필요하다. | 정의 시점 | 필수 |
| Purpose | 이 Test Case를 수행하는 이유이다. | Objective와의 연결과 판단 근거를 제공한다. | 정의 시점 | 필수 |
| Scope | Test Case가 다루는 범위와 다루지 않는 범위이다. | 과도한 확장과 중복을 막는다. | 정의 시점 | 조건부(범위가 명확히 필요한 경우) |
| Target | 검증 대상이다. | 어떤 대상에 대한 Test Case인지 명확히 한다. | 정의 시점 | 필수 |
| Preconditions | 수행 전에 충족되어야 하는 조건이다. | 재현성과 수행 가능성을 보장한다. | 정의 시점 | 조건부(필요한 경우) |
| Test Method | 의도한 검증 방법이나 기법의 분류이다. | 어떤 방식의 검증인지 나타낸다. 도구·명령어는 Procedure에 둔다. | 정의 시점 | 권장 |
| Expected Result | 수행 전에 정의한 기대 상태이다. | Actual Result와 비교할 기준을 제공한다. | 정의 시점 | 필수 |
| Evidence Requirements | 수집해야 하는 Evidence의 요구사항이다. | 어떤 증적을 남겨야 하는지 명확히 한다. | 정의 시점 | 필수 |
| Actual Result | Procedure 수행 후 Evidence에서 관찰된 실제 상태이다. | 평가 결과의 근거가 된다. | 수행 이후 | 정의 시점에는 비어 있고 수행 후 채운다 |
| Assessment Result | Actual Result를 Objective와 Expected Result 관점에서 해석한 평가 결과이다. | 관찰과 평가를 분리해 기록한다. | 수행 이후 | 정의 시점에는 비어 있고 수행 후 채운다 |
| Notes | 판단 근거, 주의사항, 제약 등 부가 정보이다. | 재현성과 해석을 돕는다. | 전 단계 | 선택 |

- 각 필드는 책임과 경계가 다르며, 정의 시점에 확정되는 필드와 수행 이후에 채워지는 필드를 구분한다.
- Actual Result와 Assessment Result는 Test Case 정의 시점에 미리 채우지 않는다.

### Expected Result / Actual Result / Assessment Result 구분

- Expected Result: Test Case 수행 전에 정의한 기대 상태이다.
- Actual Result: Test Procedure 수행 후 Evidence에서 관찰된 실제 상태이다.
- Assessment Result: Actual Result를 Objective와 Expected Result의 관점에서 해석한 평가 결과이다.

개념적으로 다음과 같이 구분한다. 이것은 개념 예시이며 실제 판정 기준을 이 문서에서 정의하지 않는다.

```text
Expected Result
    ↓
"승인된 포트만 노출되어야 한다."

Actual Result
    ↓
"22/tcp와 23/tcp가 관찰되었다."

Assessment Result
    ↓
"23/tcp가 승인된 노출 범위에 포함되는지 추가 확인이 필요하다."
```

### Evidence와 Test Case

- Evidence는 단순히 "명령어 출력"을 의미하지 않는다.
- Evidence는 다음 구조를 포함할 수 있도록 한다.

```text
Evidence
├── What
├── When
├── Where
├── How
└── Raw / Original Data
```

- Evidence는 다음 질문에 답할 수 있어야 한다.
  - 무엇을 관찰했는가?
  - 언제 관찰했는가?
  - 어떤 대상에서 관찰했는가?
  - 어떤 평가 관점/방법으로 관찰했는가?
  - 원본 데이터를 재검토할 수 있는가?
- 향후 Agent가 Evidence를 자동 수집하고 Result를 생성할 수 있다는 점을 고려하여, Evidence Requirements는 수집 가능한 형태로 정의한다.
- Evidence의 구체적인 형식과 저장 규칙은 별도 절차에서 정의하며, 이 문서에서는 확정하지 않는다.

### Test Case의 독립성과 재현성

- Test Case는 가능한 한 독립적으로 다음을 알 수 있어야 한다.
  - 무엇을 테스트하는가?
  - 어떤 대상인가?
  - 어떤 조건에서 수행하는가?
  - 무엇을 기대하는가?
  - 무엇을 수집해야 하는가?
  - 어떻게 결과를 판단하는가?
- 동일한 조건에서 반복 수행할 수 있도록 재현성을 고려한다.
- 독립성과 재현성은 이후 Test Procedure 작성과 Agent 기반 자동화의 전제가 된다.

### Test Case ID / Naming Rule

- Test Case ID는 다음 형식을 사용한다.

```text
TC-EXT-002-01
```

- 각 구성 요소의 의미는 다음과 같다.
  - `TC`: Test Case를 나타낸다.
  - `EXT`: Objective 유형 또는 평가 영역을 나타낸다.
  - `002`: 연결된 Objective를 나타낸다.
  - `01`: 해당 Objective 내 Test Case 순번을 나타낸다.
- ID 규칙이 특정 단계에 종속되지 않도록, 유형 축은 확장 가능하게 둔다. 예를 들어 향후 다음 유형을 수용할 수 있다.

```text
EXT   (External Discovery)
INT   (Internal Validation)
VULN  (Vulnerability Assessment)
CONF  (Security Configuration Assessment)
COMP  (Compliance Assessment)
```

- 따라서 ID의 유형 축은 "현재 단계"가 아니라 "평가 영역/Objective 유형"을 나타내도록 한다.

### Test Case와 Assessment Type의 관계

- Vulnerability Assessment, Security Configuration Assessment, Compliance Assessment는 동일한 공통 Test Case 구조를 사용할 수 있다.
- 공통 부분은 구조(필드와 흐름)이며, 각 평가 유형의 목적과 판정 기준은 별도로 유지한다.

```text
Common Test Case Structure
        │
        ├── Vulnerability Test Case
        ├── Configuration Test Case
        └── Compliance Test Case
```

- 즉 Test Case 모델은 공유하되, 무엇을 기대하고 어떻게 판정하는지는 평가 유형별로 정의한다.

### 전체 Lifecycle과의 연결

- Test Case는 전체 Lifecycle에서 다음 위치에 있다.

```text
Target Definition
        ↓
Scope Definition
        ↓
Discovery
        ↓
Attack Surface
        ↓
Assessment Target
        ↓
Security Requirements
        ↓
Test Objective
        ↓
Test Case
        ↓
Test Procedure
        ↓
Evidence
        ↓
Result
        ↓
Finding
        ↓
Risk Assessment
        ↓
Remediation
        ↓
Regression Test
```

- Discovery Objective와 Security Test Objective는 구분한다.
  - Discovery Objective: Discovery 단계에서 대상의 존재와 특성을 식별·검증하는 목적이다(예: DO-EXT-002).
  - Security Test Objective: Attack Surface와 Security Requirements에서 도출되어 보안 요구사항과 속성을 검증하는 목적이다.
- 공통 Test Case 구조의 Objective 필드는 위 두 종류의 Objective를 모두 참조할 수 있으나, 어느 단계의 Objective인지가 ID와 Objective 필드에서 드러나야 한다.

### Agent 기반 자동화를 고려한 구조

- Test Case 구조는 향후 Agent가 다음 작업을 수행할 수 있는 형태를 고려한다.

```text
Objective 선택
    ↓
Test Case 선택
    ↓
Precondition 확인
    ↓
Procedure 실행
    ↓
Evidence 수집
    ↓
Expected / Actual 비교
    ↓
Assessment Result 생성
```

- 이 단계에서는 Agent 구현이나 자동화 코드를 만들지 않는다. 구조와 데이터의 책임만 정의한다.

### 개별 Test Case 저장 위치 원칙

- 개별 Test Case는 이 공통 구조를 따르며, 향후 평가 대상(assessment target)과 평가 유형(assessment type)에 따라 저장한다.
- 구체적인 디렉터리 구조는 실제 Test Case를 작성하는 시점에 확정한다.
- 이 문서에서는 위치 원칙만 정의하고, 개별 Test Case를 저장할 디렉터리를 미리 만들지 않는다.

## Test Execution Model

### 모델 개요

Test Case 이후의 실행·증거·결과·Finding을 하나의 실행 모델로 정의한다.

```text
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

- 이 모델은 Test Case를 실행하고 그 결과를 Finding으로 연결하는 공통 흐름이다.
- 이 모델은 사람이 수행하는 보안 평가 방법론의 적용과 검증을 기준으로 한다.
- 모든 Test Case가 Finding을 생성하는 것은 아니다.

```text
Test Case
    ↓
Evidence
    ↓
Result
    ↓
┌────────────────────────┐
│ Security Issue exists? │
└───────────┬────────────┘
        No  │  Yes
            │
      Result only     Finding
```

- 이 실행 모델은 Vulnerability Assessment, Security Configuration Assessment, Compliance Assessment에 공통으로 적용한다.
- 각 평가 유형의 차이는 Test Case의 목적, Expected Result, 평가 기준에서 발생한다.

### Test Procedure 정의와 구조

Test Procedure는 Test Case에서 정의한 검증 목적을 실제 환경에서 수행하기 위한 절차이다.

```text
Test Case
= 무엇을 검증하는가?

Test Procedure
= 그것을 어떤 절차로 검증하는가?
```

- Test Case는 무엇/왜/조건/기대/증적 요구를 정의하고, Test Procedure는 그 검증을 위한 수행 순서와 관찰·증적 방법을 정의한다.
- Test Procedure는 특정 도구를 방법론으로 확정하지 않으며, 필요한 경우 실제 도구나 명령을 절차 안에서 사용할 수 있다. 중요한 것은 무엇을 확인하고, 무엇을 관찰하고, 무엇을 Evidence로 남기는가이다.

Test Procedure의 공통 구조는 다음과 같다.

| 필드 | 의미 | 필수 여부 |
| --- | --- | --- |
| Procedure ID | Test Procedure의 고유 식별자이다. | 필수 |
| Test Case | 이 Procedure가 수행하는 Test Case의 식별자이다. | 필수 |
| Preconditions | Procedure 수행 전에 충족되어야 하는 조건이다. | 조건부 |
| Target | Procedure가 수행되는 대상이다. | 필수 |
| Execution Steps | 순차적으로 수행하는 작업 단위의 목록이다. | 필수 |
| Expected Observation | 각 Step에서 기대되는 관찰 결과이다. | 필수 |
| Evidence Collection | 각 Step에서 수집해야 하는 Evidence의 요구사항이다. | 필수 |
| Execution Result | Procedure 수행 후의 실행 결과(성공/실패/부분 수행 등)이다. | 수행 후 |

- Execution Steps는 순차적인 작업 단위로 구성하며, 각 Step은 Action, Expected Observation, Evidence로 이루어질 수 있다.

```text
Step 1
  Action
  Expected Observation
  Evidence

Step 2
  Action
  Expected Observation
  Evidence

Step N
  Action
  Expected Observation
  Evidence
```

- Test Procedure는 특정 도구를 방법론으로 확정하지 않는다. 필요한 경우 실제 도구나 명령을 절차 안에서 사용할 수 있지만, 중요한 것은 무엇을 확인·관찰하고 무엇을 Evidence로 남기는가이다.

### Evidence 정의와 구조

Evidence는 단순한 명령어 출력이나 로그 파일이 아니라, Test Procedure 수행 결과를 뒷받침하는 관찰 가능하고 재검토 가능한 증거이다.

Evidence의 구조는 다음과 같다.

| 필드 | 의미 | 필수 여부 |
| --- | --- | --- |
| Evidence ID | Evidence의 고유 식별자이다. | 필수 |
| Source | Evidence가 수집된 출처이다. | 필수 |
| Target | Evidence가 관찰된 대상이다. | 필수 |
| Timestamp | Evidence가 수집된 시각이다. | 필수 |
| Collection Method | Evidence를 수집한 방법이다. | 필수 |
| Raw Data / Original Artifact | 재검토 가능한 원본 데이터 또는 산출물이다. | 필수 |
| Description | Evidence에 대한 설명이다. | 권장 |

- Evidence는 다음 질문에 답할 수 있어야 한다.
  - 무엇을 관찰했는가?
  - 언제 관찰했는가?
  - 어떤 대상에서 관찰했는가?
  - 어떤 방법으로 수집했는가?
  - 원본 데이터를 다시 확인할 수 있는가?
- 하나의 Test Procedure Step에서 여러 Evidence가 발생할 수 있다.
- 하나의 Evidence가 여러 Result를 지원할 수도 있다.

### Evidence와 Result의 관계

Evidence와 Result는 다음과 같이 구분한다.

```text
Evidence
= 관찰된 원본 또는 근거

Result
= Evidence를 해석하여 얻은 결과
```

예:

```text
Evidence
→ TCP/23에 대한 응답이 관찰됨

Actual Result
→ TCP/23 포트가 외부에서 접근 가능한 상태로 관찰됨
```

- Evidence 자체를 Finding으로 간주하지 않는다.

### Result 정의

Result는 최소한 두 수준으로 구분한다.

- Actual Result: Test Procedure 수행 후 실제로 관찰된 상태이다.
- Assessment Result: Actual Result를 Objective와 Expected Result의 관점에서 해석한 평가 결과이다.

관계는 다음과 같다.

```text
Expected Result
        ↓
Actual Result
        ↓
Assessment Result
```

예를 들어 개념적으로 다음과 같이 구분한다. 이 예시는 실제 보안 판정 기준을 정의하지 않는다.

```text
Expected Result
"승인된 포트만 외부에 노출되어야 한다."

Actual Result
"22/tcp와 23/tcp가 관찰되었다."

Assessment Result
"23/tcp가 승인된 노출 범위에 포함되는지 확인이 필요하다."
```

### Finding 정의

Finding은 Test Result를 바탕으로 보안상 중요하게 추적해야 할 문제 또는 비정상 상태를 구조화한 평가 결과이다.

```text
Evidence
    ↓
Result
    ↓
Finding
```

- Finding은 Evidence를 직접 대체하지 않는다.
- Finding에는 최소한 다음 정보를 수용할 수 있도록 구조를 검토한다.

```text
Finding ID
Title
Description
Affected Asset
Related Test Case
Related Evidence
Condition
Security Impact
Requirement / Control Reference
Risk
Remediation
Status
```

- Risk Assessment와 Remediation은 별도의 후속 단계이므로, Finding Definition에서 상세한 Risk/Remediation 모델을 선행하지 않는다. 위 구조는 향후 수용 가능성을 검토하기 위한 것이다.

### Result에서 Finding으로: Finding이 항상 발생하는 것은 아님

Result를 바탕으로 Finding 여부를 판단한다.

```text
Result
 ├── 정상 / 요구사항 충족
 ├── 추가 확인 필요
 └── 문제 식별 → Finding
```

- 모든 Test Case가 Finding을 생성한다고 가정하지 않는다.
- `Finding = Vulnerability`로 동일시하지 않는다.
- Finding은 향후 다음 평가 유형에서 발생할 수 있다.
  - Vulnerability Finding.
  - Configuration Finding.
  - Compliance Finding.
- 각 유형의 구체적인 판단 기준은 이후 단계에서 정의한다.

### Test Case → Procedure → Evidence → Result → Finding 관계 예시

전체 관계를 하나의 개념 예시로 나타내면 다음과 같다. 이 예시는 실제 포트 스캔 명령어를 정의하지 않는다.

```text
Test Case
"TCP Port Identification"
        ↓
Test Procedure
"승인된 평가 방법으로 TCP 포트를 식별한다."
        ↓
Execution Steps
        ↓
Evidence
"포트 탐색 원본 결과"
        ↓
Actual Result
"22/tcp, 23/tcp가 관찰됨"
        ↓
Assessment Result
"승인된 노출 범위와 비교 필요"
        ↓
Finding
"요구사항 위반이 확인된 경우 Finding 생성"
```

### 재현성과 추적성

향후 Agent 기반 Security Assessment를 고려하여 다음 Traceability를 유지할 수 있는 구조를 정의한다.

```text
Objective
   ↓
Test Case
   ↓
Test Procedure
   ↓
Procedure Step
   ↓
Evidence
   ↓
Result
   ↓
Finding
```

- 각 단계는 이전 단계와 연결될 수 있어야 한다.
- 특히 Finding이 발생한 경우에는 다음 방향으로 거슬러 올라가도 근거를 확인할 수 있어야 한다.

```text
Finding
   ↓
Result
   ↓
Evidence
   ↓
Procedure
   ↓
Test Case
   ↓
Objective
```

### Assessment Type과의 관계

Vulnerability Assessment, Security Configuration Assessment, Compliance Assessment는 동일한 Execution Model을 사용할 수 있다.

```text
Test Case
    ↓
Procedure
    ↓
Evidence
    ↓
Result
    ↓
Finding
```

- 공통 부분은 실행 모델과 데이터 구조이며, 차이는 Test Case의 목적, Expected Result, 평가 기준에서 발생한다.
  - Vulnerability: 취약점 존재 여부.
  - Configuration: 보안 설정 요구사항 충족 여부.
  - Compliance: 특정 통제/요구사항 충족 여부.
- 구체적인 평가 기준은 이후 단계에서 정의한다.

### Agent 기반 실행에 대한 현재 입장

- 현재 프로젝트는 Agent 기반 자동 수행을 고려하지 않고, 사람이 수행하는 보안 평가 방법론의 적용과 검증에 집중한다.
- Agent 기반 실행은 장기 방향으로만 고려하며, 이 실행 모델은 사람이 수행하는 절차를 기준으로 정의한다.
- 이 단계에서는 Agent 구현이나 자동화 코드를 만들지 않는다.

### 개념 구분 요약

이 실행 모델에서 사용하는 개념의 책임은 다음과 같다.

```text
Objective
= 무엇을 확인해야 하는가

Test Case
= 어떤 독립적인 평가 단위로 검증하는가

Test Procedure
= 어떤 절차로 검증하는가

Evidence
= 무엇이 관찰되었음을 증명하는가

Actual Result
= 실제로 무엇이 관찰되었는가

Assessment Result
= 그 관찰 결과를 어떻게 평가했는가

Finding
= 추적이 필요한 보안상 문제로 무엇을 식별했는가
```

## Evidence-driven Assessment

평가 결과는 근거 없는 판단이 아니라 증적에 기반해야 한다.

- 증적은 재현성(reproducibility)을 지원해야 한다: 다른 사람이 기록된 증적으로부터 관찰을 재현할 수 있어야 한다.
- 증적은 검증 가능성(verifiability)을 지원해야 한다: 결과를 그 증적과 대조하여 다시 확인할 수 있어야 한다.
- 증적은 추적성(traceability)을 지원해야 한다: Finding을 그 증적과 다루는 목표로 거슬러 추적할 수 있어야 한다.
- 증적은 보고서 작성을 지원해야 한다: 최종 보고서가 자신의 진술에 대한 증적을 인용할 수 있어야 한다.
- 증적은 Regression Test를 지원해야 한다: 동일한 증적 기반을 재사용하여 Remediation을 확인할 수 있어야 한다.

증적의 구체적인 형식과 저장 규칙은 별도 절차에서 정의하며, 이 문서에서는 확정하지 않는다.

## Agent-based Assessment

이 프로젝트의 장기적인 연구 방향 중 하나는 Agent 기반 Security Assessment이다.

- 이것은 향후 연구 방향이며, 현재 구현된 기능이 아니다.
- 구조화된 평가 프로세스가 향후 작업의 기반이 될 수 있다는 관점이다:

```text
Assessment Process
        ↓
Structured Objectives
        ↓
Test Cases
        ↓
Procedures
        ↓
Evidence
        ↓
Results
```

- 현재 단계에서 이 문서에 Agent 워크플로를 정의하거나 구현하지 않는다.

## Assessment-specific Implementations

이 문서의 공통 프로세스는 시간이 지나면서 다양한 평가 대상에 적용할 수 있도록 한다.

- Linux Server (이 프로젝트에서 첫 번째로 사용하는 대상).
- Web Application.
- Network Device.
- Security Appliance.
- 기타 시스템.

`assessments/` 아래의 대상별 문서가 이 공통 프로세스를 구체적인 대상에 적용한다.
Linux Server 이외의 대상은 계획 단계이며 아직 구현되지 않았다.
