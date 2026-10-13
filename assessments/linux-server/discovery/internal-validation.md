# Linux Server Internal Validation (Test Design)

이 문서는 Linux Server Discovery의 **Internal Validation**을 위한 Test Design(정의/학습)이다.
Internal Validation은 External Discovery에서 관찰한 결과를 대상 시스템 내부 상태와 대조·검증하는 활동이다.

- External Discovery: "외부에서 무엇이 보이는가"를 식별한다.
- Internal Validation: 그 결과가 내부에서 실제로 어떻게 구현되어 있는지를 대조·검증하고 correlation한다.
- 이는 새로운 Discovery 단계가 아니며, 보안 판단/Finding이 아니다.

## 1. 전제 조건 (중요)

Internal Validation은 대상 시스템 내부 상태를 확인해야 하므로 **내부 접근/권한(승인)** 이 필요하다.

- 예: 대상에 대한 SSH 접속 계정, 또는 대상 내부에서 명령을 실행할 수 있는 승인된 실행 환경.
- 내부 접근이 없으면 Internal Validation은 실행할 수 없다(External Discovery만 가능).
- 최소 권한/읽기 전용을 우선하고, 승인 범위를 벗어나지 않는다.
- 일부 Objective(예: 패키지 확인)는 배포판에 따라 도구가 달라진다.

## 2. Objective (Test Design)

기존 `objectives.md`의 DO-INT-001~004를 Test Design 관점에서 정리한다.

| Objective | 무엇을 검증하는가 | 외부(External) 대응 | 내부 Method/Tool(수단) | Evidence |
| --- | --- | --- | --- | --- |
| DO-INT-001 Listening Socket Validation | 외부 관찰 포트에 대응하는 리스닝 소켓(주소/포트/프로토콜)이 실제 존재하는가 | DO-EXT-002/003(포트/서비스) | `ss`, `lsof -i` 등 | 리스닝 소켓 목록, 일치/불일치 |
| DO-INT-002 Service Validation | 리스닝 소켓이 실제 관리되는 서비스와 연결되고 상태가 어떠한가 | DO-EXT-003(서비스) | `systemctl`, `service` 등 | 서비스-소켓 매핑, 서비스 상태 |
| DO-INT-003 Process Validation | 리스닝 소켓/서비스를 소유한 실행 프로세스는 무엇인가 | (외부에 직접 대응 없음) | `ps`, `/proc`, `lsof` 등 | 프로세스-소켓-서비스 매핑 |
| DO-INT-004 Package and Application Validation | 프로세스/서비스에 대응하는 설치 패키지/애플리케이션/버전은 무엇인가 | DO-EXT-004(애플리케이션/버전) | 패키지 관리자(`dpkg`/`rpm`), 실행 파일 경로 | 패키지-애플리케이션-버전, 외부와 일치/불일치 |

- Tool은 관련 Objective를 검증하기 위한 수단이며 방법론 계층이 아니다. 실제 사용하는 Tool만 Tool Catalog에 최소 추가한다.

## 3. Correlation (Asset Relationship)

External과 Internal은 동일한 자산 관계를 서로 다른 관점에서 관찰하고, 결과를 correlation한다.

```text
External 관찰: Network Address → Port → Service → Application / Version

Internal 검증: Network Address → Listening Socket → Service → Process → Package → Application / Version
```

- 일치하면 Asset Relationship 신뢰도가 높아진다.
- 불일치하면 추가 확인이 필요한 항목으로 기록한다(자동 판정/Finding 생성 금지).

## 4. Evidence

- 각 Objective는 대상/관점(internal)/Method/Tool/실행 조건/시각/원본 출력을 남긴다.
- Evidence는 External 관찰과의 일치/불일치를 재검토할 수 있어야 한다.
- 내부에서만 드러나는 정보(외부에 보이지 않는 내부 전용 리스닝 소켓 등)도 함께 기록한다.

## 5. Boundary

- Internal Validation은 관찰·대조·검증이며, Pass/Fail·Risk·Vulnerability·Finding이 아니다.
- 외부 관찰 범위와 다른 대상을 임의로 확장하지 않는다. 내부에서 추가로 드러난 항목은 별도로 표시한다.
- 보안 요구사항/판단 기준은 이후 Assessment 단계에서 다룬다.

## 6. 실행 전 확정 사항

- 내부 접근은 **Execution Configuration의 `access` 섹션**(transport/계정/키)으로 정의한다. 설계: `execution/README.md`(Internal Validation 실행 설계), `execution/config/internal-access.example.yaml`.
- 비밀번호/개인키 등 비밀정보는 Configuration에 넣지 않는다(SSH agent 또는 키 파일 경로만).
- 대상 배포판과 사용 가능한 Tool(`ss`, `systemctl`, `ps`, 패키지 관리자 등).
- Evidence 저장 위치/형식, 실행 관점(internal) 정의.
- 어느 Objective부터 시작할지(예: DO-INT-001 Listening Socket Validation).

## 7. 학습 노트

- NIST SP 800-115는 내부 관점(Internal Testing 등)과 호스트 수준 상태(Review/Examination)를 다루지만, DO-INT-001~004 Objective 구조와 correlation 모델은 프로젝트 확장이다.
- External/Internal을 correlation하는 것은 프로젝트 실무 방식이며 NIST가 정의한 모델이 아니다.
- Internal Validation의 실행은 내부 접근 확보 여부에 종속되며, 접근이 없으면 External 결과만으로 남는다.

## 참고

- `objectives.md`(DO-INT-001~004), `README.md`, `testcases/`, `procedures/`, `execution/`
- 프로젝트 공통 Tool Catalog(`tools/`)
