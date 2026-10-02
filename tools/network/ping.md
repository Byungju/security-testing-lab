# ping

## Tool Name

ping (iputils ping, BusyBox ping 등 배포본에 따라 변형이 있다)

## Purpose

ICMP Echo 요청을 보내고 응답을 관찰하여, 대상까지의 IP 계층 도달성에 대한 증거를 수집한다.

## Category

network

## Applicable Techniques

- ICMP Echo 기반 도달성 관찰 (ICMP-based reachability verification)

## Applicable Objectives

- DO-EXT-001 Network Reachability Identification (Primary 후보)

## Capabilities

- 대상 주소로 ICMP Echo 요청을 보내고 응답 여부를 관찰한다.
- 응답이 있는 경우 RTT와 응답률/손실을 제공한다.
- 관찰 결과로 IP 계층 도달성의 한 증거를 남긴다.

## Limitations

- ICMP 응답이 없다는 사실만으로 대상이 도달 불가능하다고 판단해서는 안 된다. ICMP 필터링, rate limiting, 혼잡으로 응답이 없을 수 있다.
- TCP/UDP 도달성이나 특정 서비스 접근 가능 여부는 이 Tool만으로 판단할 수 없다.
- 애플리케이션 계층 도달성은 관찰할 수 없다.
- ICMP 응답이 있다는 사실만으로 모든 네트워크 접근이 가능하다고 판단해서는 안 된다.

## Required Privileges

- 일반적으로 raw socket 또는 CAP_NET_RAW 권한이 필요하다.
- 배포본에 따라 ping capability가 설정되어 있으면 일반 사용자로 실행할 수 있고, 그렇지 않으면 root 권한이 필요할 수 있다.

## Input

- 대상 주소(hostname 또는 IP 주소).
- 필요 시 전송 횟수, 타임아웃, 패킷 크기 등의 옵션.

## Output

- 패킷별 응답 여부와 RTT.
- 요약 통계(전송/수신, 손실률, RTT 통계).
- 종료 상태.

## Evidence Characteristics

- 대상 주소, 평가 위치, 사용한 방식, 시각을 함께 기록한다.
- 명령 출력(원본)을 재검토 가능한 형태로 남긴다.
- 출력 요약만 남기지 않고 원본 결과를 남긴다.

## Operational Considerations

- 일반적으로 대상에 미치는 영향은 낮다.
- ICMP가 차단된 환경에서는 결과가 제한되므로 다른 방식과 함께 사용한다.
- 응답 없음은 관찰 사실로 기록하고, 도달 불가로 확정하지 않는다.

## Version / Compatibility

- iputils, BusyBox 등 배포본에 따라 옵션과 출력 형식이 다르다.
- IPv4/IPv6 지원 방식과 옵션 이름이 버전에 따라 다를 수 있다.
- 사용한 버전과 옵션을 Evidence에 기록한다.

## Related Test Cases / Procedures

- TC-EXT-001-01 Network Reachability Verification.
- TP-EXT-001-01 Network Reachability Verification Procedure.

## References

- ICMP (RFC 792).
- iputils ping(8) man page.
- NIST SP 800-115 Section 4.1 Network Discovery (개념 참고).
