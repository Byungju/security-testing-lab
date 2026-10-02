# Linux Server Assessment

## Overview

이 문서는 `assessments/README.md`에서 정의한 공통 평가 프로세스를 Linux Server 대상에 적용하는 방법을 설명한다.
Linux Server의 하드닝 항목이나 점검 항목 전체를 담는 문서가 아니다.

Linux Server는 이 프로젝트의 첫 번째 실제 평가 대상이다.
네트워크 서비스, 애플리케이션, 설정, 계정, 인증 등 평가할 수 있는 요소가 다양하기 때문에 첫 번째 대상으로 적합하다.
현재 프로젝트는 SSH와 Telnet 기반 Shell Access 환경을 주요 평가 대상으로 삼는다.

이 문서는 공통 프로세스를 적용하는 **Project practice**이다.
Network Discovery, Network Port and Service Identification 등 NIST SP 800-115 개념을 사용하는 부분은 **NIST SP 800-115 basis**이며, 이 프로젝트의 프로세스 안에서 사용한다.

## Assessment Scope

Linux Server의 현재 연구 범위는 다음 영역을 포함한다.
이는 연구 범위이며, 모든 영역이 이미 구현되었다는 의미가 아니다.

- Linux Server
- Network Exposure
- Network Services
- Remote Access
- SSH
- Telnet
- Security Configuration
- Vulnerability
- Compliance

## Linux Server Assessment Flow

공통 Lifecycle을 Linux Server에 연결하면 다음과 같다.

```text
Target Linux Server
        ↓
Network Discovery
        ↓
Port Discovery
        ↓
Service Identification
        ↓
Application / Version Identification
        ↓
Attack Surface
        ↓
SSH / Telnet Assessment Target 선정
        ↓
Security Requirements
        ↓
Test Objectives
        ↓
Test Cases
        ↓
Test Procedures
        ↓
Evidence
        ↓
Findings
        ↓
Risk / Remediation
        ↓
Regression
        ↓
Compliance
```

- 이 흐름의 Discovery 부분은 `discovery/README.md`에서 상세히 다룬다.
- 이후 단계는 `assessments/README.md`의 공통 프로세스를 선정된 대상에 적용한다.
- 이 흐름은 프로젝트 실무 방식이며, NIST SP 800-115가 정의한 Lifecycle이 아니다.

## Discovery Relationship

Linux Server의 Discovery 단계는 `discovery/README.md`에 문서화되어 있다.
이 절에서는 Discovery가 나머지 평가와 어떻게 연결되는지만 설명하고, Discovery의 세부 내용은 반복하지 않는다.

- Discovery는 단순한 Port Scan이 아니다.
- Discovery는 다음 관계를 파악한다:

```text
Host
  → Port
  → Service
  → Application
  → Version
```

- Discovery의 결과는 Attack Surface를 구성하는 데 사용되며, 이는 다시 평가 대상을 결정한다.

## Assessment Areas

Linux Server 평가는 시간이 지나면서 다음 영역으로 확장할 예정이다.
아래 목록은 이미 문서가 있는 영역과 계획된 영역을 함께 담고 있으며, 모두 구현된 것은 아니다.

- Discovery (`discovery/README.md`에 문서화됨).
- Attack Surface (planned).
- SSH Assessment (planned).
- Telnet Assessment (planned).
- Authentication (planned).
- Authorization (planned).
- Security Configuration (planned).
- Vulnerability Assessment (planned).
- Compliance Assessment (planned).
- Remediation (planned).
- Regression Testing (planned).

## Evidence Model

Linux Server 평가에서 사용할 수 있는 증적의 종류는 다음과 같다.
아래 예시는 증적의 범주를 설명하는 것이며, 구체적인 명령어나 Test Case가 아니다.

- Network scan result.
- Port/service information.
- Running process.
- Listening socket.
- Service status.
- Package information.
- Configuration.
- Authentication settings.
- Command output.

구체적인 명령어와 Test Case는 이 문서에서 정의하지 않으며, 이후 단계에서 다룬다.

## Directory Structure

현재 구조는 의도적으로 최소한으로 유지한다.

```text
linux-server/
├── README.md
└── discovery/
    └── README.md
```

SSH, Telnet, Configuration, Vulnerability, Compliance 등의 하위 디렉터리는 필요성이 확인되면 이후에 추가할 수 있다.
현재 단계에서는 다른 하위 디렉터리를 정의하지 않는다.
