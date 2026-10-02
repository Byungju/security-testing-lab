# traceroute

## Tool Name

traceroute (구현/옵션에 따라 traceroute, traceroute6, mtr, tracepath 등 유사 도구가 있다)

## Purpose

TTL을 단계적으로 증가시켜 대상까지의 네트워크 경로를 관찰하고, 도달이 어느 지점에서 멈추는지에 대한 단서를 수집한다.

## Category

network

## Applicable Techniques

- Network Path 관찰 (path observation / diagnostic)

## Applicable Objectives

- DO-EXT-001 Network Reachability Identification (진단/Digagnostic 후보)

## Capabilities

- 대상까지의 경로상 홉을 관찰한다.
- 특정 지점에서 응답이 끊기는 경우 그 지점에 대한 단서를 제공한다.
- 도달성 관찰이 되지 않거나 제한되었을 때 원인 추정(경로 문제 vs 정책/필터)을 돕는다.

## Limitations

- 경로 홉을 관찰할 뿐, 종단 도달성을 확립하지 못한다.
- 중간 장비가 ICMP Time Exceeded 응답을 차단하거나 rate limit하면 경로가 보이지 않을 수 있다.
- 비대칭 경로나 로드 밸런싱으로 경로가 일관되지 않을 수 있다.
- 경로에 표시된 홉이 실제 원인 지점이라고 확정할 수 없다.
- traceroute 결과만으로 reachable/unreachable을 판단해서는 안 된다.

## Required Privileges

- 구현에 따라 raw socket 또는 CAP_NET_RAW 권한이 필요할 수 있다.
- tracepath나 일부 구현/모드는 비특권으로 실행할 수 있다.

## Input

- 대상 주소(hostname 또는 IP 주소).
- 필요 시 프로토콜 모드(ICMP/UDP/TCP), 최대 홉 수, 타임아웃 옵션.

## Output

- 홉별 주소와 RTT(응답이 있는 경우).
- 응답이 없는 홉(별표 등) 표시.
- 종료 상태.

## Evidence Characteristics

- 대상 주소, 평가 위치, 사용한 방식/모드, 시각을 함께 기록한다.
- 홉 경로 원본 출력을 재검토 가능한 형태로 남긴다.
- 응답 없는 홉도 결과로 기록한다.

## Operational Considerations

- 일반적으로 대상에 미치는 영향은 낮지만, 반복/대량 실행은 피한다.
- ICMP 차단 환경에서는 결과가 제한되므로 다른 방식과 함께 사용한다.
- 경로 결과는 진단용이며, 도달성 판단의 보조로만 사용한다.

## Version / Compatibility

- traceroute, traceroute6, mtr, tracepath 등 구현에 따라 옵션과 기본 프로토콜이 다르다.
- 사용한 구현·버전·모드를 Evidence에 기록한다.

## DO-EXT-001에서의 사용 목적

- ICMP/TCP 기반 도달성 관찰이 되지 않거나 제한/불충분할 때, 경로 문제 가능성과 정책/필터 차단 가능성을 구분하기 위한 진단(Diagnostic)으로 사용한다.
- 단독 검증 도구가 아니며, Primary 검증(ping, nc)을 대체하지 않는다.

## Related Test Cases / Procedures

- TC-EXT-001-01 Network Reachability Verification.
- TP-EXT-001-01 Network Reachability Verification Procedure.

## References

- ICMP (RFC 792), IP (RFC 791).
- traceroute(8) man page.
- NIST SP 800-115 Section 4.1 Network Discovery (개념 참고).
