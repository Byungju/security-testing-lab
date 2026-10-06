# nmap

## Tool Name

nmap (Nmap, Network Mapper)

## Purpose

대상의 네트워크 노출을 관찰하기 위해 호스트 발견과 TCP/UDP 포트 스캔을 수행하고, 필요 시 서비스/버전 식별에 사용한다.

## Category

network

## Applicable Techniques

- TCP Port Scanning (connect / SYN)
- UDP Port Scanning
- Host Discovery (보조)
- Service / Version Detection (향후 DO-EXT-003/004)

## Applicable Objectives

- DO-EXT-002 Network Port Identification (주 대상)
- DO-EXT-003 / DO-EXT-004 (서비스·애플리케이션/버전 식별, 향후)
- DO-EXT-001 (호스트 발견 보조, 현재는 ping/nc 사용)

## Capabilities

- 승인된 범위의 TCP 포트 상태(open/closed/filtered 등)를 관찰한다.
- UDP 포트 스캔을 수행할 수 있다.
- 호스트 발견과 서비스/버전 감지, OS 감지를 지원한다.
- 일반/XML/grepable 등 다양한 출력 형식을 제공한다.

## Limitations

- `filtered`와 `open|filtered`는 모호할 수 있어 단일 결과로 단정할 수 없다.
- UDP는 무응답이 정상일 수 있어 판단이 불확실하다.
- 스캔 자체가 네트워크 트래픽과 대상 부하를 유발하며 IDS/로그에 남을 수 있다.
- 포트 open 관찰은 서비스 존재/취약점을 의미하지 않는다.
- SYN/OS/UDP 스캔은 raw socket 권한이 필요할 수 있다.
- 결과는 관찰이며 Assessment Result/Finding이 아니다.

## Required Privileges

- TCP connect 스캔은 일반적으로 비특권으로 가능하다.
- SYN 스캔, OS 감지, UDP 스캔은 root 또는 CAP_NET_RAW가 필요할 수 있다.

## Input

- 대상 주소(hostname 또는 IP).
- 승인된 포트 범위/목록과 스캔 유형 옵션.

## Output

- 포트별 상태와 프로토콜.
- 호스트 상태/서비스 정보(옵션에 따라).
- 일반/XML 형식의 스캔 결과.

## Evidence Characteristics

- 대상, 평가 위치, 스캔 범위/옵션, 시각, 원본 출력을 함께 기록한다.
- 원본(예: 정규 출력 또는 XML)을 재검토 가능한 형태로 보존한다.

## Operational Considerations

- 승인된 범위에만 사용하며, 승인되지 않은 대상/범위 스캔은 금지한다.
- 속도/타이밍 조정과 off-hours 등 영향 최소화를 고려한다.
- 스캔 결과를 Port Discovery 이상(서비스/취약점)으로 확대 해석하지 않는다.

## Version / Compatibility

- 현재 환경 설치 버전: Nmap 7.94SVN (Ubuntu 24.04).
- 옵션/출력은 버전에 따라 달라질 수 있으므로 실행 시 버전을 Evidence에 기록한다.

## Related Test Cases / Procedures

- TC-EXT-002-01 Network Port Identification (TCP)
- TP-EXT-002-01 Network Port Identification (TCP) Procedure
- 실제 사용: `execution/results/20261002T153920-DO-EXT-002` (TCP connect scan, port_range 1-1000)

## References

- Nmap 공식 문서(nmap.org).
- NIST SP 800-115 Section 4.2 Network Port and Service Identification (개념 참고).
