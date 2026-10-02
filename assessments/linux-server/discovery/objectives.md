# Linux Server Discovery Objectives

이 문서는 Linux Server Assessment의 Discovery 단계에서 **무엇을 식별하고 확인해야 하는가**를 Discovery Objective로 정의한다.
이 문서는 특정 도구나 명령어를 정의하지 않는다. 도구와 명령어는 이후 Test Procedure 단계에서 다룬다.

Discovery Objective는 이후 단계로 다음과 같이 이어지도록 설계한다.
Discovery Objective의 결과는 먼저 Attack Surface 구성에 사용되고, 그 이후에 Test Case로 내려간다.

```text
Discovery Objective
        ↓
Attack Surface
        ↓
Assessment Target
        ↓
Test Case
        ↓
Test Procedure
        ↓
Evidence
        ↓
Result
```

NIST SP 800-115와의 관계는 각 Objective에 표기한다.
NIST SP 800-115에서 직접 가져온 개념은 **NIST SP 800-115 basis**로, Linux Server 평가를 위해 새로 구성한 Objective 구조는 **Project practice**로 구분한다.

## 1. Discovery Objective의 목적

- Discovery Objective는 "어떤 도구를 사용할 것인가"가 아니라 "Discovery를 통해 무엇을 식별하고 확인해야 하는가"를 정의하는 상위 수준의 평가 목적이다.
- 하나의 Objective는 하나의 식별 또는 검증 목적을 나타내며, 이후 Test Case가 이 Objective를 검증하도록 연결된다.
- Objective의 결과(Output)는 이후 Attack Surface 구성과 대상 선정의 입력이 된다.

## 2. Discovery의 분류

Discovery 활동은 목적에 따라 다음 두 영역으로 분류한다.

### External Discovery

- 평가 대상 시스템의 외부에서 관찰 가능한 정보를 식별한다.
- 원격 클라이언트가 보는 것처럼 대상에 접근하여, 네트워크에 노출된 정보를 확인한다.
- 외부에서 관찰 가능한 노출면은 이후 Attack Surface의 기반이 된다.

### Internal Validation

- Internal Validation은 새로운 Discovery 단계가 아니라, External Discovery에서 관찰한 결과를 대상 시스템 내부 상태와 대조·검증하는 활동이다.
- External Discovery가 "외부에서 무엇이 보이는가"를 식별하면, Internal Validation은 그 결과가 내부에서 실제로 어떻게 구현되어 있는지를 대조·검증한다.
- 실제 리스닝 상태, 실행 프로세스, 서비스 관리 상태, 설치 패키지 등 외부에서 직접 관찰할 수 없는 내부 상태를 확인한다.
- 주된 목적은 외부 관찰 결과와 내부 상태를 correlation하는 것이며, 외부에서 보이지 않는 내부 전용 리스닝 서비스처럼 추가로 드러나는 정보도 함께 기록한다.

### 용어 검토: Internal Discovery vs Internal Validation

- 기존 `discovery/README.md`는 내부 관점을 "Internal Discovery"로 표현했다.
- 이 문서에서는 내부 관점이 별도의 Discovery 단계가 아니라 외부 관찰 결과를 내부 상태와 대조·검증하는 활동임을 드러내기 위해 **Internal Validation**을 채택한다.
- 외부에서 관찰하는 활동(External Discovery)과 내부 상태를 대조·검증하는 활동(Internal Validation)은 목적이 다르므로 동일한 Discovery 활동으로 취급하지 않는다.
- 이 용어 구분은 이 프로젝트의 실무적 정의이며, NIST SP 800-115가 정의한 용어가 아니다.

### NIST SP 800-115 개념과 프로젝트 확장의 구분

- NIST SP 800-115에 직접 대응하는 개념: Network Discovery, Network Port and Service Identification, Port Scanning, Service Identification, Version Scanning, Banner Grabbing, 내부 관점(Internal Testing 등).
- 프로젝트가 Linux Server 평가를 위해 확장한 개념: Listening Socket Validation, Service Validation, Process Validation, Package and Application Validation, External/Internal 결과 correlation, Asset Relationship 모델.
- 이 문서는 NIST SP 800-115가 현재 프로젝트의 8개 Objective 구조를 직접 정의한 것처럼 표현하지 않는다.

## 3. External Discovery와 Internal Validation의 관계

External Discovery와 Internal Validation은 서로 다른 관점에서 동일한 자산 관계를 관찰하고, 그 결과를 correlation하여 하나의 Asset Relationship을 구성한다.
External Discovery가 노출된 진입점을 관찰하면, Internal Validation은 그 진입점을 대상 시스템 내부 상태와 대조·검증한다.

프로젝트에서 사용하는 관계 모델은 다음과 같다.

```text
Network Endpoint
    ↓
Port / Listening Socket
    ↓
Network Service
    ↓
Implementation / Application
    ↓
Process
    ↓
Package
```

External과 Internal은 이 관계를 서로 다른 관점에서 관찰한다.

External:

```text
Network Address
    ↓
Port
    ↓
Service
    ↓
Application / Version
```

Internal:

```text
Network Address
    ↓
Listening Socket
    ↓
Service
    ↓
Process
    ↓
Package
    ↓
Application / Version
```

예를 들어 External과 Internal은 다음과 같이 같은 대상을 관찰할 수 있다.

```text
External Observation
  → TCP/22 Open
  → SSH
  → OpenSSH

Internal Validation
  → 0.0.0.0:22 LISTEN
  → sshd process
  → sshd.service
  → openssh-server package
```

- Application은 Process와 Package 사이에 고정된 하나의 계층이라기보다, 외부에서 식별되는 구현체와 내부의 Process/Package 정보를 연결하는 correlation 대상이다.
- 따라서 위 관계 모델을 하나의 고정된 선형 구조로 오해하지 않도록, External과 Internal은 동일한 자산 관계를 서로 다른 관점에서 관찰하고 correlation한다는 점을 명확히 한다.
- 이 Asset Relationship 모델은 Discovery 결과를 해석하고 상호 참조하기 위한 프로젝트 실무 방식이며, NIST SP 800-115가 정의한 모델이 아니다.

## 4. Objective 정의 형식

각 Discovery Objective는 다음 형식으로 정의한다.

- Objective ID: External은 `DO-EXT-###`, Internal Validation은 `DO-INT-###` 형식을 사용한다.
- Objective Name: 명확하고 짧은 이름을 사용한다.
- Purpose: 이 Objective를 수행하는 이유를 설명한다.
- Objective Statement: "무엇을 식별/검증한다" 형태의 명확한 한 문장으로 작성한다.
- Input: Objective 수행에 필요한 사전 정보.
- Expected Output: Objective 수행 후 생성되어야 하는 정보.
- Relationship: 결과가 다른 Objective 또는 Attack Surface 단계와 어떻게 연결되는지 설명한다.
- NIST Relationship: NIST SP 800-115의 관련 개념이 있으면 연결하고, NIST 정의와 프로젝트 확장을 구분한다.

## 5. Discovery Objectives

### External Discovery

#### DO-EXT-001 Network Reachability Identification

- Purpose: 대상이 이미 명시적으로 정의된 경우(Known Target), 광범위한 Host Discovery가 아니라 이후 Port/Service Identification을 수행하기 위한 전제 조건으로서 도달 가능성을 확인한다.
- Objective Statement: Known Target에서는 평가 위치에서 지정된 대상 네트워크 주소로 도달 가능한지 확인한다. 대상이 아직 명시적으로 정의되지 않은 경우(Unknown Target)에는 더 넓은 Network Discovery의 일부로 확장될 수 있다.
- Input: 대상으로 지정된 host 식별자(예: hostname, IP 주소, 주소 범위), 평가 위치(External 관점), 승인된 평가 범위.
- Expected Output: 도달성 관찰 결과(도달 확인, 관찰되지 않음, 제한됨, 불충분), 응답한 네트워크 주소, 관찰 관점 정보.
- Relationship: DO-EXT-002의 전제 조건이다. 도달할 수 없는 경우 이후 포트·서비스 식별이 제한됨을 결과에 기록한다.
- NIST Relationship: NIST SP 800-115 Section 4.1 Network Discovery의 개념과 관련된다. 다만 이 문서는 NIST가 하나의 통합된 "Discovery Phase"를 정의한다고 보지 않는다. Known Target의 도달 가능성 확인은 프로젝트의 평가 흐름에 맞게 정리한 것이며, Unknown Target으로 확장될 때 NIST의 broader Network Discovery 개념에 더 가까워진다.

#### DO-EXT-002 Network Port Identification

- Purpose: 외부에서 접근 가능한 네트워크 포트를 식별하여 네트워크 노출면을 확인한다.
- Objective Statement: 평가 위치에서 대상의 네트워크 주소에 대해 응답하는 TCP/UDP 포트를 식별한다.
- Input: DO-EXT-001의 결과(도달 가능한 주소), 승인된 평가 범위와 대상 포트 범위.
- Expected Output: 응답한 포트 목록, 각 포트의 프로토콜, 관찰 관점 정보.
- Relationship: DO-EXT-003의 입력이며, DO-INT-001의 검증 대상이다.
- NIST Relationship: NIST SP 800-115 Section 4.2 Network Port and Service Identification의 Port Scanning 개념을 기반으로 한다.

#### DO-EXT-003 Network Service Identification

- Purpose: 열린 포트에서 실제로 동작하는 네트워크 서비스를 식별한다.
- Objective Statement: 식별된 각 포트에서 응답하는 네트워크 서비스의 종류를 식별한다.
- Input: DO-EXT-002의 결과(응답한 포트 목록).
- Expected Output: 포트-서비스 매핑, 식별 신뢰 수준(추정/확인).
- Relationship: DO-EXT-004의 입력이며, DO-INT-002와 상호 검증한다.
- NIST Relationship: NIST SP 800-115 Section 4.2의 Service Identification 개념을 기반으로 한다.

#### DO-EXT-004 Application and Version Identification

- Purpose: 서비스를 구현하는 애플리케이션과 버전을 식별하여 Attack Surface 구성의 입력을 마련한다.
- Objective Statement: 식별된 서비스 뒤의 애플리케이션과, 가능한 경우 그 버전을 식별한다.
- Input: DO-EXT-003의 결과(포트-서비스 매핑).
- Expected Output: 애플리케이션 후보와 버전(추정 포함), 식별 신뢰 수준.
- Relationship: Attack Surface 구성의 입력이며, DO-INT-003·DO-INT-004와 correlation하여 내부 상태로 검증한다.
- NIST Relationship: NIST SP 800-115 Section 4.2의 Version Scanning 개념(예: Banner Grabbing)을 기반으로 한다.

### Internal Validation

#### DO-INT-001 Listening Socket Validation

- Purpose: 외부에서 관찰된 포트가 실제로 대상 호스트에서 리스닝 상태인지 검증한다.
- Objective Statement: 대상 호스트 내부에서 외부 관찰 포트에 대응하는 리스닝 소켓(주소와 포트, 프로토콜)을 확인한다.
- Input: DO-EXT-002·DO-EXT-003의 결과, 내부 접근(승인된 범위 내).
- Expected Output: 리스닝 소켓 목록과 외부 관찰 결과와의 일치/불일치 정보.
- Relationship: DO-INT-002로 연결되며, 외부 관찰(DO-EXT-002)을 내부 상태로 검증한다.
- NIST Relationship: NIST SP 800-115의 내부 관점(예: Section 2.4.1 Internal Testing)과 관련되지만, 이 Objective 구조는 프로젝트 확장이다.

#### DO-INT-002 Service Validation

- Purpose: 리스닝 소켓을 실제 관리되는 서비스와 연결하고 그 상태를 확인한다.
- Objective Statement: 리스닝 소켓에 대응하는 서비스와 그 서비스의 관리 상태를 확인한다.
- Input: DO-INT-001의 결과(리스닝 소켓 목록).
- Expected Output: 리스닝 소켓과 서비스의 매핑, 서비스 관리 상태 정보.
- Relationship: DO-INT-003으로 연결되며, 외부 서비스 식별(DO-EXT-003)을 검증한다.
- NIST Relationship: 이 Objective는 Linux Server 내부 상태 확인을 위한 프로젝트 확장이며, 대응하는 NIST 직접 정의는 없다.

#### DO-INT-003 Process Validation

- Purpose: 리스닝 소켓과 서비스를 실제 실행 프로세스와 연결한다.
- Objective Statement: 리스닝 소켓과 서비스를 소유한 실행 프로세스를 확인한다.
- Input: DO-INT-001·DO-INT-002의 결과.
- Expected Output: 프로세스-소켓-서비스 매핑 정보.
- Relationship: DO-INT-004로 연결되며, Asset Relationship 구성에서 Process 계층의 중간 연결을 제공한다.
- NIST Relationship: 이 Objective는 프로젝트 확장이며, 대응하는 NIST 직접 정의는 없다.

#### DO-INT-004 Package and Application Validation

- Purpose: 실행 중인 서비스·프로세스를 설치된 패키지·애플리케이션과 연결하고 버전을 검증한다.
- Objective Statement: 프로세스·서비스에 대응하는 설치 패키지와 애플리케이션 버전을 확인한다.
- Input: DO-INT-003의 결과(프로세스 정보).
- Expected Output: 패키지-애플리케이션-버전 정보와 외부 관찰(DO-EXT-004)과의 일치/불일치 정보.
- Relationship: Package/Application/Version 정보를 확인하여 Attack Surface 구성에 입력한다. Security Requirements와 Test Objective는 이후 단계에서 Attack Surface를 기반으로 도출한다.
- NIST Relationship: 이 Objective는 프로젝트 확장이며, 대응하는 NIST 직접 정의는 없다.

## 6. Objective Relationship

External Discovery와 Internal Validation의 Objective는 다음처럼 연결된다.

| 계층 | External Discovery | Internal Validation |
| --- | --- | --- |
| Network Address | DO-EXT-001 | - |
| Port | DO-EXT-002 | DO-INT-001 |
| Service | DO-EXT-003 | DO-INT-002 |
| Application / Implementation | DO-EXT-004 | DO-INT-003, DO-INT-004와 연계 |
| Version | DO-EXT-004 | DO-INT-004 |
| Process | - | DO-INT-003 |
| Package | - | DO-INT-004 |

- 이 표는 엄격한 1:1 계층 구조를 의미하지 않는다. External Observation과 Internal State를 correlation하기 위한 관점을 나타낸다.
- External Discovery는 "외부에서 무엇이 보이는가"를, Internal Validation은 "내부에서 실제로 무엇이 그러한가"를 다룬다.
- 두 영역의 결과가 일치하면 Asset Relationship의 신뢰도가 높아지고, 불일치하면 추가 확인이 필요한 항목으로 남긴다.

## 7. Discovery 결과에서 Attack Surface로

Discovery Objective의 결과는 Asset Relationship과 Asset/Service Inventory를 거쳐 Attack Surface로 연결된다.
Security Requirements와 Test Objective는 Discovery에서 직접 도출되는 것이 아니라, Attack Surface를 기반으로 이후 단계에서 도출된다.

```text
External Discovery (DO-EXT-001 ~ DO-EXT-004)
        ↓
Internal Validation (DO-INT-001 ~ DO-INT-004)
        ↓
Asset Relationship / Asset·Service Inventory
        ↓
Attack Surface
        ↓
Assessment Target
        ↓
Security Requirements
        ↓
Test Objective
```

- External Discovery는 노출된 포트·서비스·애플리케이션을 식별하여 Attack Surface의 외부 노출면을 구성한다.
- Internal Validation은 그 노출면을 내부 상태와 correlation하여, 실제로 어떤 서비스·애플리케이션·프로세스·패키지가 관련되는지 확인한다.
- Attack Surface는 대상 선정(예: SSH, Telnet)의 입력이며, Security Requirements와 Test Objective는 이후 단계에서 Attack Surface를 기반으로 도출한다.
- 따라서 Discovery Objective(특히 DO-INT-004)의 직접적인 역할은 Attack Surface 구성까지로 제한한다.

## 8. 범위와 다음 단계

이번 단계에서 정의한 범위는 다음과 같다.

- Discovery Objective 목록과 External Discovery / Internal Validation 분류.
- 각 Objective의 Purpose, Objective Statement, Input, Expected Output, Relationship, NIST Relationship.
- Objective 간 관계와 Attack Surface로의 연결 구조.

이번 단계에서 다루지 않은 범위는 다음과 같다.

- Test Case와 Test Procedure.
- 실제 명령어와 도구 선정.
- 실제 평가 결과와 증적.

## 9. Review Notes

- 각 Objective는 도구나 명령어가 아니라 식별·검증 목적을 기준으로 정의했다.
- External Discovery는 외부 관찰, Internal Validation은 외부 관찰 결과를 내부 상태와 대조·검증하는 활동으로 구분했다.
- 서비스·프로세스·패키지처럼 인접한 계층은 목적이 다르므로 별도 Objective로 두되, 명령어 단위로 세분화하지 않았다.
- 모든 Objective의 Expected Output은 먼저 Attack Surface 구성으로 연결되도록 작성했다. Security Requirements와 Test Objective는 Attack Surface를 기반으로 이후 단계에서 도출한다.
- NIST SP 800-115 직접 대응 개념(Network Discovery, Port/Service Identification, Version Scanning, Banner Grabbing, 내부 관점 등)과 프로젝트 확장(Internal Validation, Objective 구조, correlation, Asset Relationship 모델)을 구분해 표기했다.
