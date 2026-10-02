# Linux Server Discovery

Discovery는 이 프로젝트에서 Linux Server 보안평가의 첫 번째 단계이다.
대상이 네트워크에 어떻게 노출되어 있고 어떤 서비스와 애플리케이션을 실행하는지 식별하여, 이후 보안평가의 대상과 범위를 올바르게 정하기 위한 기초를 마련한다.
모든 Discovery 활동은 테스트가 명시적으로 허가된 환경에서만 수행한다.

출처를 명확히 하기 위해 이 문서의 모든 내용은 다음 두 가지 중 하나로 구분한다.

- **NIST SP 800-115 basis**: NIST SP 800-115에서 직접 가져온 개념이다.
- **Project practice**: 이 프로젝트가 위 개념을 묶고 확장하여 만든 실무적 Discovery 단계이다.

## Objective

- 대상 Linux Server의 네트워크 노출과 실행 중인 서비스 및 애플리케이션을 식별한다.
- 이후 보안평가의 대상과 테스트 범위를 결정하기 위한 기초 정보를 확보한다.
- Discovery 결과를 공격면(Attack Surface)과 대상 선정(Target Selection)으로 연결하기 위한 초기 공격면을 만든다.

## Methodology

NIST SP 800-115는 하나의 고정된 "Discovery Phase"를 정의하지 않는다.
관련 기법을 각각 다른 Section에서 정의하며, 이 프로젝트는 그러한 기법을 하나의 실무적 Discovery 단계로 묶는다.

| 항목 | 분류 | 출처 / 설명 |
| --- | --- | --- |
| 하나의 운영 단계로서의 Discovery | Project practice | 이 프로젝트가 아래 NIST 기법을 Linux Server 평가를 위한 하나의 Discovery 단계로 묶은 것이다. |
| Network Discovery | NIST SP 800-115 basis | NIST SP 800-115, Section 4.1: 활성 장치를 식별하고 네트워크가 어떻게 동작하는지 파악한다. |
| Network Port and Service Identification | NIST SP 800-115 basis | NIST SP 800-115, Section 4.2: 열린 포트, 그 포트에서 동작하는 서비스, 각 서비스를 구현하는 애플리케이션을 식별한다. |
| Version Scanning | NIST SP 800-115 basis | NIST SP 800-115, Section 4.2에 설명된 개념: 배너 그래빙 등을 통해 서비스 뒤의 애플리케이션과 버전을 식별한다. |
| Discovery Process 흐름 | Project practice | 이 문서의 순차적 파이프라인은 이 프로젝트의 운영적 배치이며, NIST가 정의한 파이프라인이 아니다. |

- 이 문서에서 "Discovery 단계"라는 표현은 항상 이 프로젝트의 실무적 묶음을 의미하며, NIST SP 800-115가 정의한 단계를 뜻하지 않는다.
- 기반이 되는 기법은 NIST 근거이며, 이를 Linux Server 평가에 맞게 조합하고 적용한 방식은 프로젝트의 확장이다.

## Discovery Scope

Discovery 단계에서 식별하는 항목은 다음과 같다.

- Host: 대상 서버와 그 식별 정보.
- Network Interface: 호스트에 도달할 수 있는 인터페이스.
- IP Address: 호스트와 인터페이스에 연결된 주소.
- Open Ports: 응답하거나 리스닝 중인 포트.
- Protocol: 각 포트에 연결된 전송 프로토콜(예: TCP, UDP).
- Services: 식별된 포트에서 동작하는 네트워크 서비스.
- Applications: 각 서비스를 구현하는 애플리케이션 소프트웨어.
- Versions: 식별할 수 있는 경우 해당 애플리케이션의 버전.

## Discovery Process

이 프로젝트의 Discovery 단계는 다음 흐름을 따른다.

```text
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
Target Selection
        ↓
Security Assessment
```

- Network Discovery: 호스트와 네트워크상의 도달 가능한 존재를 식별한다.
- Port Discovery: 열려 있거나 리스닝 중인 포트를 식별한다.
- Service Identification: 각 포트에서 동작하는 서비스를 식별한다.
- Application / Version Identification: 애플리케이션과, 가능한 경우 버전을 식별한다.
- Attack Surface: 노출된 포트·서비스·애플리케이션·버전을 초기 공격면으로 정리한다.
- Target Selection: 공격면을 기준으로 이후 보안평가의 대상을 선택한다.
- Security Assessment: 선택한 대상(예: SSH, Telnet)에 대해 보안평가를 수행한다.

- 이 흐름은 프로젝트 실무 방식이다. NIST SP 800-115는 해당 기법을 이 하나의 파이프라인이 아니라 각각 별도로 제시한다.

## External Discovery vs Internal Validation

Discovery는 외부 관점, 내부 관점, 또는 둘 다로 수행할 수 있다.
두 관점은 서로 다른 질문에 답하며 서로 다른 결과를 낼 수 있다.
이 문서는 외부 관점을 External Discovery, 내부 관점을 Internal Validation으로 부른다.
용어 선택의 근거와 Discovery Objective는 `objectives.md`에서 정의한다.

**External Discovery (외부 관점)**

- 원격 클라이언트가 보는 것처럼 대상 외부에서 관찰한다.
- 네트워크에서 관찰 가능한 포트와 서비스를 확인한다.
- 예시 도구: Nmap 등 네트워크 스캐너.

**Internal Validation (내부 관점)**

- 대상 시스템에서 실행하여 실제 상태를 검증한다.
- 실제 리스닝 상태, 실행 중인 프로세스, 설치된 패키지를 확인한다.
- 예시 도구: `ss`, `systemctl`, `ps`, 패키지 관리자.

두 관점은 다음과 같이 연결될 수 있으며, 이는 네트워크 관찰 결과를 호스트의 실제 소프트웨어와 연결하는 데 도움이 된다.

```text
Port
  → Network Service
  → Process
  → Package
  → Configuration
```

- 이 연결은 Discovery 결과를 해석하고 상호 참조하기 위한 프로젝트 실무 방식이다.
- NIST SP 800-115가 정의한 모델이 아니다.

## Example

다음 예시는 외부 관찰과 내부 확인을 어떻게 상호 참조할 수 있는지 보여준다.
설명을 위한 예시일 뿐이며, 특정 Linux 배포판이나 OpenSSH 버전에 종속되지 않는다.

```text
Nmap
  → 22/tcp open

ss
  → 0.0.0.0:22 LISTEN

systemctl
  → sshd.service active

Process
  → /usr/sbin/sshd

Package
  → openssh-server
```

- 이를 통해 TCP/22가 SSH 원격관리 서비스와 연결된다는 것을 알 수 있다.
- 이 예시는 고정된 명령 출력이 아니라 의도한 상호 참조 경로(Port → Network Service → Process → Package → Configuration)를 보여준다.
- 명령어의 상세 절차는 이후 단계에서 별도로 다룬다.

## Discovery Output

Discovery 단계의 산출물은 다음과 같다.

- Asset Inventory: 식별된 호스트, 인터페이스, IP 주소.
- Port / Service Inventory: 열린 포트, 프로토콜, 그 위에서 동작하는 서비스.
- Application Inventory: 식별된 애플리케이션과 버전.
- Initial Attack Surface: 대상 선정에 사용하는 노출 포트·서비스·애플리케이션의 통합된 관점.
- Discovery Evidence: 위 결과를 뒷받침하는 기록.

## Evidence

증적(Evidence)은 단순히 명령어 결과를 저장하는 것이 아니다.
증적의 목적은 Discovery 결과를 이후에 재현하고 검증할 수 있게 하여, 발견 사항을 다시 확인하고 평가를 반복할 수 있도록 하는 것이다.

- 증적은 무엇을, 언제, 어느 관점(외부 또는 내부)에서 관찰했는지 이해할 수 있을 만큼의 맥락을 기록해야 한다.
- 반복 가능한 Discovery 활동이라면, 다른 사람이 동일한 관찰을 재현할 수 있을 만큼 상세하게 기록한다.
- 증적의 구체적인 형식과 저장 규칙은 별도 절차에서 정의하며, 이 문서에서는 확정하지 않는다.

## Next Step

Discovery가 끝나면 식별된 공격면이 보안평가의 기준이 된다.

- SSH, Telnet 등 대상은 발견된 서비스에서 선택한다.
- 이후 보안평가는 그 대상에 맞추어 범위를 정한다.
- Discovery에서 무엇을 식별·검증해야 하는지는 `objectives.md`에서 정의한다.
- 구체적인 평가 절차와 Test Case는 이 문서의 구조를 활용하여 이후 단계에서 추가한다.

## References

- NIST SP 800-115, Technical Guide to Information Security Testing and Assessment (September 2008), Section 4.1 Network Discovery 및 Section 4.2 Network Port and Service Identification.
- NIST SP 800-115 프로젝트 분석 문서: `methodology/nist-800-115/analysis.md`.
- Linux Server Discovery Objective: `objectives.md`.
