# NIST SP 800-115

## 기본 정보

| 항목 | 내용 |
| --- | --- |
| 정식 문서명 | Technical Guide to Information Security Testing and Assessment |
| 문서 식별자 | NIST Special Publication 800-115 (NIST SP 800-115) |
| 발행 기관 | NIST (National Institute of Standards and Technology) |
| 발행일 | September 2008 |

## 문서의 목적

이 문서는 조직이 정보 보안 테스트 및 평가를 계획하고 수행하고, 결과를 분석하여
완화 전략을 마련하는 데 참고할 수 있도록 기술적 측면의 방법과 기법을 제시한다.
완전한 보안 테스트 프로그램 전체를 규정하기보다는, 기술적 보안 테스트와 점검의
핵심 요소를 개요 형태로 다루는 데 초점을 둔다.

## 문서 전체 구조

- Executive Summary
- Section 1: Introduction
- Section 2: Security Assessment
- Section 3: Review Techniques
- Section 4: Target Identification and Analysis Techniques
- Section 5: Target Vulnerability Validation Techniques
- Section 6: Security Assessment Planning
- Section 7: Security Assessment Execution
- Section 8: Post-Testing Activities (Reporting 포함)
- Appendix A ~ G

## 각 Section의 역할

### Section 1: Introduction

문서의 권한(Authority), 목적과 범위, 대상 독자, 문서 구조를 설명한다.
문서 전체를 이해하기 위한 도입부 역할을 한다.

### Section 2: Security Assessment

보안 평가의 기본 방법론을 다룬다. 평가 방법과 기술적 평가 기법의 개념, 테스트와 점검(Examination)의 비교, 그리고 평가를 바라보는 관점 (외부/내부, 공개/비공개)을 설명한다.

### Section 3: Review Techniques

문서 검토, 로그 검토, 규칙(ruleset) 검토, 시스템 구성 검토, 네트워크 스니핑, 파일 무결성 점검 등 검토(Review) 계열 기법을 설명한다.

### Section 4: Target Identification and Analysis Techniques

대상 식별과 분석을 위한 기법을 다룬다. 네트워크 탐색, 네트워크 포트와 서비스 식별, 취약점 스캐닝, 무선 스캐닝 등을 설명한다.

### Section 5: Target Vulnerability Validation Techniques

식별된 취약점을 검증하는 기법을 다룬다. 패스워드 크래킹, 침투 테스트, 소셜 엔지니어링 등을 설명한다.

### Section 6: Security Assessment Planning

보안 평가를 계획하는 방법을 다룬다. 평가 정책 수립, 평가 우선순위와 일정, 기법 선택과 조정, 평가 물류(인력, 장소, 도구), 평가 계획서 작성, 법적 고려사항을 설명한다.

### Section 7: Security Assessment Execution

보안 평가를 실행하는 방법을 다룬다. 조정(Coordination), 평가 수행, 분석, 그리고 데이터 수집·저장·전송·폐기와 같은 데이터 처리(Data Handling)를 설명한다.

### Section 8: Post-Testing Activities

평가 이후 활동을 다룬다. 완화 권고, 보고(Reporting), 재조치/완화(Remediation/Mitigation)를 설명한다. 문서에서 보고는 이 Section의 하위 주제로 다룬다.

## Appendix A ~ G

| Appendix | 내용 |
| --- | --- |
| Appendix A | 보안 테스트에 사용할 수 있는 Live CD 배포판을 소개한다. |
| Appendix B | 평가 시 합의 사항을 정리하는 Rules of Engagement 템플릿을 제공한다. |
| Appendix C | 애플리케이션 보안 테스트 및 점검을 다룬다. |
| Appendix D | 원격 접속(Remote Access) 테스트를 다룬다. |
| Appendix E | 관련 자료와 참고 리소스를 정리한다. |
| Appendix F | 용어(Glossary)를 정의한다. |
| Appendix G | 약어(Acronyms and Abbreviations)를 정리한다. |

## 문서 구조의 구분

문서는 다음 관점으로 구분해서 볼 수 있다.

- Assessment Methodologies
  - Section 2에서 보안 평가의 기본 방법론과 관점을 다룬다.
- Technical Assessment Techniques
  - Section 3(검토), Section 4(대상 식별·분석), Section 5(취약점 검증)에서 기술적 평가 기법을 다룬다. Appendix C, D도 관련 기법을 보완한다.
- Assessment Process
  - Section 6(Planning), Section 7(Execution), Section 8(Post-Testing)에서 평가를 수행하는 전체 과정을 다룬다.
- Planning / Execution / Reporting
  - Planning은 Section 6, Execution은 Section 7, Reporting은 Section 8의 하위 주제로 다룬다.

## 현재 학습에서 중요한 관찰점

- NIST SP 800-115는 하나의 고정된 침투 테스트 방법론만을 정의하는 문서가 아니다.
- 다양한 Assessment Methodology와 Technical Assessment Technique을 함께 다룬다.
- 기술적인 테스트뿐 아니라 Planning, Execution, Reporting까지 포함한다.
- 따라서 향후 제품 보안 테스트 프로세스를 설계할 때 참고할 수 있는 기반 문서로 볼 수 있다.
