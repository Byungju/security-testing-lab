# Tool Catalog

## 목적

Tool Catalog는 Security Assessment에서 반복적으로 사용하는 검증 도구(Tool)를 프로젝트 공통으로 관리하기 위한 영역이다.
특정 Assessment나 특정 Objective에 종속되지 않도록 관리하며, 여러 Objective에서 같은 Tool을 참조할 수 있게 한다.

## Tool의 정의

Tool은 Security Assessment에서 관찰, 검증, 증거 수집 등을 수행하기 위해 사용하는 소프트웨어, 명령어, 유틸리티를 말한다.

- Tool은 Objective를 검증하기 위한 수단이다.
- Tool은 새로운 방법론의 상위 단계가 아니며, 독립적인 평가 단계도 아니다.
- Tool이 Objective를 정의하지 않는다. Objective와 Verification Method가 먼저 있고, Tool은 그 수단으로 선택된다.

## Tool과 Verification Method / Technique의 관계

```text
Objective
    ↓
Verification Method / Technique
    ↓
Tool
```

- Verification Method / Technique는 "무엇을 어떻게 관찰·검증하는가"를 나타낸다.
- Tool은 그 Method/Technique를 수행하는 구체적인 수단이다.
- Tool과 Technique은 1:1 관계가 아니다.

```text
One Technique
├── Tool A
├── Tool B
└── Tool C

One Tool
├── Technique A
├── Technique B
└── Technique C
```

- 하나의 Technique을 여러 Tool로 수행할 수 있다.
- 하나의 Tool이 여러 Technique에 사용될 수 있다.
- 따라서 Tool 문서는 특정 Objective/Procedure에 중복 생성하지 않고, 이 Catalog에서 한 번만 관리한다.

## Tool 선택 원칙

Tool을 선택할 때 최소한 다음을 고려한다.

- Objective 적합성: Tool이 해당 Objective의 검증에 적합한가.
- 관찰 가능 범위: 어떤 계층/대상을 관찰할 수 있는가.
- 결과의 신뢰성: 결과를 어느 정도 신뢰할 수 있는가.
- 한계 및 오해 가능성: 결과만으로 무엇을 판단하면 안 되는가.
- Evidence 수집 가능성: 재검토 가능한 Evidence를 남길 수 있는가.
- Target 환경과의 호환성: 대상 환경에서 사용 가능한가.
- 필요한 권한: 어떤 권한이 필요한가.
- 네트워크/시스템에 미치는 영향: 대상에 미치는 영향은 어느 정도인가.
- 유지보수 및 버전 변화: 버전에 따라 동작·옵션이 달라지는가.
- 대체 Tool 존재 여부: 동일 Technique을 수행할 대체 Tool이 있는가.

## Tool Lifecycle

Tool은 추가·변경·폐기될 수 있음을 전제로 다음 상태를 사용한다.
필요 이상으로 복잡한 절차는 두지 않는다.

```text
Candidate
    ↓
Active
    ↓
Deprecated
    ↓
Retired
```

- Candidate: 검토 중인 후보 Tool이다.
- Active: 검증에 사용하기로 한 Tool이다.
- Deprecated: 사용을 줄이고 대체를 권장하는 Tool이다.
- Retired: 더 이상 사용하지 않는 Tool이다.
- 상태가 바뀌면 해당 Tool 문서의 관련 필드와 Procedure 참조를 함께 검토한다.

## Tool Version

- Tool은 버전에 따라 동작이나 옵션이 달라질 수 있으므로, 각 Tool 문서의 `Version / Compatibility` 필드에 관리한다.
- 필요한 경우 Test Procedure/Evidence에 실제 사용한 버전을 기록한다.
- 특정 버전을 현재 표준으로 고정하지 않는다.
- 버전 변경이 검증 결과에 영향을 줄 수 있으면 Limitations 또는 Operational Considerations에 기록한다.

## 디렉터리 구조

현재는 다음과 같이 최소 구조로 시작한다.

```text
tools/
├── README.md
└── network/
    ├── ping.md
    └── nc.md
```

- `network/`: 네트워크 관찰·연결 확인에 사용하는 Tool.
- `linux/` 등 다른 카테고리는 실제로 필요한 Tool이 생길 때 추가한다.
- 빈 카테고리 디렉터리를 미리 만들지 않는다.

## 개별 Tool 문서 Schema

각 Tool 문서는 다음 필드를 포함한다.

| 필드 | 의미 | 필수 여부 |
| --- | --- | --- |
| Tool Name | Tool의 이름과 주요 변형/패키지명이다. | 필수 |
| Purpose | 이 Tool을 사용하는 목적이다. | 필수 |
| Category | Tool의 분류(예: network)이다. | 필수 |
| Applicable Techniques | 이 Tool로 수행할 수 있는 Verification Method / Technique이다. | 필수 |
| Applicable Objectives | 이 Tool을 사용할 수 있는 Objective이다. | 권장 |
| Capabilities | 이 Tool이 할 수 있는 것과 관찰할 수 있는 것이다. | 필수 |
| Limitations | 이 Tool이 할 수 없는 것과, 결과만으로 판단하면 안 되는 것이다. | 필수 |
| Required Privileges | 실행에 필요한 권한이다. | 필수 |
| Input | 실행에 필요한 입력(대상, 옵션 등)이다. | 권장 |
| Output | 일반적으로 얻는 출력 형태이다. | 권장 |
| Evidence Characteristics | Evidence로 남길 수 있는 정보와 원본 재검토 가능성이다. | 필수 |
| Operational Considerations | 영향, 주의사항, 사용 시 제약이다. | 필수 |
| Version / Compatibility | 버전·배포본에 따른 차이와 호환성이다. | 권장 |
| Related Test Cases / Procedures | 연결된 Test Case와 Test Procedure이다. | 권장 |
| References | 참고 자료(공식 문서, 표준 등)이다. | 선택 |

- `Capabilities`와 `Limitations`는 반드시 분리한다.
- Limitations에는 "이 Tool의 결과만으로 무엇을 판단해서는 안 되는가"를 포함한다.

## Procedure 및 Evidence와의 관계

```text
TP-EXT-001-01
    ↓
Technique: ICMP-based reachability verification
    ↓
Tool: ping
    ↓
tools/network/ping.md
```

- Procedure는 Technique과 사용 Tool을 참조할 수 있다.
- Tool의 상세 설명·사용법은 이 Catalog에 두고 Procedure에 중복 작성하지 않는다.
- Tool 실행 결과는 Evidence로 남기며, Evidence 자체를 Assessment Result로 취급하지 않는다.

## 관리 원칙

1. Tool Catalog는 특정 Assessment에 종속되지 않는다.
2. 동일 Tool의 정보를 여러 Procedure에 중복 작성하지 않는다.
3. Tool과 Technique을 동일한 개념으로 취급하지 않는다.
4. Tool이 Objective를 정의하지 않는다.
5. Tool 선택은 Objective와 Verification Method를 기준으로 한다.
6. Tool은 추가/변경/폐기될 수 있음을 전제로 한다.
7. Tool의 장점뿐 아니라 Limitations를 관리한다.
8. Tool의 실행 결과 자체와 Assessment Result를 동일하게 취급하지 않는다.
9. 실제 Target에 대한 테스트 실행은 별도 단계에서 수행한다.
10. Agent 실행 구조는 이 Catalog의 범위에 포함하지 않는다.

## 등록 현황

| Tool | Category | 문서 | 상태 |
| --- | --- | --- | --- |
| ping | network | `network/ping.md` | Candidate |
| nc | network | `network/nc.md` | Candidate |
| traceroute | network | `network/traceroute.md` | Candidate |
