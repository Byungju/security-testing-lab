# nc (netcat)

## Tool Name

nc (netcat; ncat, netcat-openbsd, 전통적 netcat 등 배포본/구현에 따라 변형이 있다)

## Purpose

승인된 대상 주소와 포트에 대한 TCP/UDP 연결을 시도하고 결과를 관찰하여, 해당 목적지까지의 연결 도달성에 대한 증거를 수집한다.

## Category

network

## Applicable Techniques

- TCP Connect 기반 도달성 관찰 (TCP connectivity verification)
- 승인된 서비스와의 연결을 통한 배너/응답 관찰 (보조)

## Applicable Objectives

- DO-EXT-001 Network Reachability Identification (TCP 방식 후보)
- 향후 서비스·버전 식별(DO-EXT-003, DO-EXT-004)에서 보조로 참조 가능

## Capabilities

- 지정한 TCP 포트로 연결을 시도하여 연결 성공/거부/타임아웃을 관찰한다.
- UDP 통신을 시도할 수 있다(구현에 따라 지원 범위가 다르다).
- 연결 후 데이터를 보내거나 받아 서비스 응답·배너를 관찰할 수 있다.

## Limitations

- 이 Tool로 관찰한 결과는 ICMP 도달성을 판단하지 못한다.
- 승인된 특정 포트로의 연결 성공은 그 목적지까지의 경로 도달성 증거이지만, 모든 네트워크 접근 가능을 의미하지 않는다.
- 중간 장비가 SYN을 drop하면 타임아웃이 되며, 이는 도달 불가로 확정할 수 없다.
- UDP는 무응답이 정상일 수 있어 판단이 불확실하다.
- 포트 식별(DO-EXT-002)을 목적으로 한 대량 스캔에 사용해서는 안 된다.

## Required Privileges

- TCP Connect 방식은 일반적으로 특수 권한이 필요 없다.
- 일부 옵션(예: 일부 raw/UDP 동작)은 추가 권한이 필요할 수 있다.

## Input

- 대상 주소(hostname 또는 IP 주소).
- 대상 포트와 프로토콜.
- 필요 시 송신 데이터 또는 타임아웃 옵션.

## Output

- 연결 시도 결과(성공/거부/타임아웃).
- 수신 데이터 또는 배너(있는 경우).
- 종료 상태.

## Evidence Characteristics

- 대상 주소, 평가 위치, 사용한 방식/포트, 시각을 함께 기록한다.
- 연결 결과와 수신 데이터(원본)를 재검토 가능한 형태로 남긴다.
- 서비스에 접속해 얻은 출력은 Evidence이며, 그 자체를 Assessment Result로 취급하지 않는다.

## Operational Considerations

- 승인된 포트/서비스에만 사용한다.
- 서비스에 불필요한 입력을 보내지 않도록 주의한다.
- 연결 성공/실패만으로 도달성을 확정하지 않고 다른 방식과 함께 사용한다.

## Version / Compatibility

- ncat, netcat-openbsd, 전통적 netcat 등 구현에 따라 옵션과 동작이 다르다.
- 배포본별 옵션 차이가 크므로 사용한 구현과 버전을 Evidence에 기록한다.

## Related Test Cases / Procedures

- TC-EXT-001-01 Network Reachability Verification.
- TP-EXT-001-01 Network Reachability Verification Procedure.

## References

- TCP (RFC 793).
- nc/ncat man page.
- NIST SP 800-115 Section 4.2 Network Port and Service Identification (개념 참고).
