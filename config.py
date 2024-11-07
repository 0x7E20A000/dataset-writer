from openai import OpenAI
import os
from datetime import datetime
from converter import DataConverter
from dotenv import load_dotenv

# OpenAI API 설정
OPENAI_MODEL = "gpt-4o-mini"
MAX_TOKENS = 12400  # 최대 토큰 수 수정
TEMPERATURE = 0.75

# 생성 설정
TOPICS = [
    # 보안 기초 개념
    ("보안 3요소(CIA)와 기본 원칙", "security_basics"),
    ("사이버 킬체인의 이해", "cyber_killchain"),
    ("MITRE ATT&CK 프레임워크", "mitre_attack"),
    ("ISO 27001 보안 표준", "iso_27001"),
    ("OWASP Top 10 취약점", "owasp_top_10"),
    ("GDPR과 개인정보 보호", "gdpr_privacy"),
    ("NIST 사이버 보안 프레임워크", "nist_cybersecurity"),
    ("보안 거버넌스 및 컴플라이언스", "security_governance"),

    # 위협 분석
    ("위협 인텔리전스 개념과 활용", "threat_intelligence"),
    ("APT 그룹 분석과 대응", "apt_analysis"),
    ("악성코드 분석 기법과 도구", "malware_analysis"),
    ("랜섬웨어 탐지 및 방어", "ransomware_defense"),
    ("사회공학 공격 및 피싱 방지", "phishing_prevention"),
    ("네트워크 침입 탐지 시스템(NIDS)", "nids"),
    ("위협 헌팅(Threat Hunting)", "threat_hunting"),
    ("제로 트러스트 보안 모델", "zero_trust"),

    # 취약점 관리
    ("취약점 분석 방법론", "vulnerability_assessment"),
    ("CVE와 취약점 스코어링", "cve_scoring"),
    ("제로데이 취약점 연구", "zeroday_research"),
    ("취약점 관리 라이프사이클", "vulnerability_management"),
    ("취약점 평가 및 우선순위 설정", "vulnerability_prioritization"),
    ("취약점 스캐닝 도구 활용", "vulnerability_scanning_tools"),
    ("취약점 패치 관리(Patch Management)", "patch_management"),
    ("시스템 하드닝", "system_hardening"),

    # 공격 기법
    ("Penetration testing", "penetration_testing"),
    ("Exploit escalation", "exploit_escalation"),
    ("Social engineering", "social_engineering"),
    ("Incident response", "incident_response"),
    ("Digital forensics", "digital_forensics"),
    ("Cloud security", "cloud_security"),
    ("애플리케이션 보안(Application Security)", "application_security"),
    ("네트워크 보안(Network Security)", "network_security"),
    ("웹 애플리케이션 방화벽(WAF)", "web_application_firewall"),
    ("사이버 범죄 분석", "cybercrime_analysis"),

    # 클라우드 및 데이터 보호
    ("클라우드 보안 정책", "cloud_security_policies"),
    ("데이터 암호화 기법", "data_encryption_techniques"),
    ("데이터 마스킹(Data Masking)", "data_masking"),
    ("공급망 보안(Supply Chain Security)", "supply_chain_security"),
    ("서버리스 아키텍처 보안", "serverless_security"),
    ("컨테이너 보안", "container_security"),
    ("데이터 분류와 접근 통제", "data_classification_access_control"),
    ("데이터 유출 방지(DLP)", "data_loss_prevention"),

    # 접근 관리
    ("IAM(Identity and Access Management)", "identity_access_management"),
    ("다단계 인증(MFA)", "multi_factor_authentication"),
    ("SSO(Single Sign-On)와 SAML", "single_sign_on_saml"),
    ("역할 기반 접근 제어(RBAC)", "role_based_access_control"),
    ("권한 상승 방지 기법", "privilege_escalation_prevention"),
    ("원격 액세스 보안", "remote_access_security"),

    # 최신 보안 동향 및 기술
    ("AI와 머신러닝을 활용한 보안", "ai_security"),
    ("블록체인 보안", "blockchain_security"),
    ("IoT 보안(IoT Security)", "iot_security"),
    ("모바일 애플리케이션 보안", "mobile_application_security"),
    ("퀀텀 보안(Quantum Security)", "quantum_security"),
    ("SecOps 및 보안 자동화", "secops_automation"),
    ("디지털 ID 및 생체 인증", "digital_identity_biometric_authentication"),
    ("SIEM(보안 정보 및 이벤트 관리)", "siem")
]

TOPIC_KEYWORDS = {
    # 보안 기초 개념
    "security_basics": [
        "기밀성(Confidentiality)", "무결성(Integrity)", "가용성(Availability)", 
        "보안 정책 수립", "위험 관리 기본 원칙", "보안 통제"
    ],
    "cyber_killchain": [
        "정찰 단계", "무기화 단계", "전달 단계", 
        "공격 실행 단계", "명령제어(C2)", "공격 사슬 완성"
    ],
    "mitre_attack": [
        "전술(Tactics)", "기법(Techniques)", "절차(Procedures)", 
        "공격자 그룹", "완화 방안", "ATT&CK Navigator 활용"
    ],
    "iso_27001": [
        "보안 관리 시스템", "ISO 27001 인증 절차", "리스크 관리", 
        "정보 보안 정책", "감사 및 평가", "정책 유지 관리"
    ],
    "owasp_top_10": [
        "Injection 공격", "Broken Authentication", "Sensitive Data Exposure", 
        "XML External Entities", "Security Misconfiguration", "Cross-Site Scripting"
    ],
    "gdpr_privacy": [
        "데이터 주체 권리", "데이터 보호 책임자(DPO)", "개인정보 유출 신고", 
        "프라이버시 규정 준수", "데이터 보관 기간", "정보 주체의 권리"
    ],
    "nist_cybersecurity": [
        "NIST 프레임워크", "위험 평가", "대응 및 복구", 
        "위협 방지", "침해 대응", "거버넌스 정책"
    ],
    "security_governance": [
        "보안 컴플라이언스", "보안 정책 수립", "위험 관리 전략", 
        "기업 보안 거버넌스", "보안 리더십", "전사적 보안 접근"
    ],

    # 위협 분석
    "threat_intelligence": [
        "위협 정보 수집", "OSINT(Open Source Intelligence)", "위협 인텔리전스 피드", 
        "APT 그룹 분석", "지속적 위협 모니터링", "위협 자동화 도구"
    ],
    "apt_analysis": [
        "APT 공격 분석", "정찰 기법", "명령 제어 통신(C2)", 
        "지속성 유지 기법", "사회공학 활용", "피해 최소화 방안"
    ],
    "malware_analysis": [
        "정적 분석", "동적 분석", "Sandbox 분석", 
        "악성코드 유포 경로", "백도어 탐지", "루트킷 탐지"
    ],
    "ransomware_defense": [
        "랜섬웨어 탐지", "백업 전략", "복구 계획", 
        "데이터 암호화", "사이버 보험", "위협 대응 훈련"
    ],
    "phishing_prevention": [
        "피싱 메일 분석", "훈련 프로그램", "탐지 기법", 
        "이메일 인증", "도메인 보호", "의심 이메일 대응"
    ],
    "nids": [
        "네트워크 트래픽 분석", "시그니처 기반 탐지", "행동 기반 탐지", 
        "침입 탐지 시스템 설치", "이상 징후 모니터링", "정책 설정"
    ],
    "threat_hunting": [
        "위협 헌팅 기법", "악성 코드 조사", "사이버 위협 예측", 
        "위협 패턴 분석", "보안 사고 예방", "사이버 위험 관리"
    ],
    "zero_trust": [
        "제로 트러스트 원칙", "네트워크 세분화", "접근 제어 강화", 
        "다중 인증", "접근 관리 자동화", "데이터 보호"
    ],

    # 취약점 관리
    "vulnerability_assessment": [
        "위험 평가 기법", "취약점 분석", "보안 평가 기준", 
        "취약점 보고", "위험 기반 접근", "위험 완화"
    ],
    "cve_scoring": [
        "CVE 체계 이해", "CVSS 점수 계산", "취약점 심각도 평가", 
        "공격 벡터 분석", "CVE 항목 검색", "취약점 우선순위 설정"
    ],
    "zeroday_research": [
        "제로데이 취약점 정의", "제로데이 익스플로잇 개발", "취약점 공개 절차", 
        "공격 사례 연구", "취약점 탐지 기법", "제로데이 대응 전략"
    ],
    "vulnerability_management": [
        "취약점 관리 프로세스", "취약점 검토", "위험 평가",
        "취약점 제거", "위험 완화 조치", "시스템 유지 보수"
    ],
    "vulnerability_prioritization": [
        "위험 기반 취약점 대응", "보안 패치 적용", "취약점 위험 평가", 
        "보안 정책 설정", "취약점 통합 관리", "위험 점수 산정"
    ],
    "vulnerability_scanning_tools": [
        "취약점 스캐닝 도구", "Nessus 사용법", "OpenVAS 활용", 
        "취약점 보고서 작성", "자동화된 스캐닝", "네트워크 취약점 점검"
    ],
    "patch_management": [
        "패치 관리 프로세스", "패치 스케줄링", "취약점 패치 적용", 
        "보안 업데이트", "시스템 테스트", "취약점 대응 모니터링"
    ],
    "system_hardening": [
        "시스템 보안 강화", "OS 하드닝", "네트워크 보안 설정", 
        "권한 관리", "보안 구성 점검", "보안 정책 설정"
    ],

    # 공격 기법
    "penetration_testing": [
        "정보 수집 기법", "취약점 스캐닝", "Exploit 기법", 
        "보고서 작성", "사회공학 테스트", "Post-Exploitation"
    ],
    "exploit_escalation": [
        "익스플로잇 생성", "권한 상승 기법", "로컬 익스플로잇", 
        "원격 익스플로잇", "시스템 테스트", "취약점 완화"
    ],
    "social_engineering": [
        "사회공학 정의", "피싱 기법", "물리적 접근", 
        "심리적 조작", "사회공학 방지 교육", "실습 훈련"
    ],
    "incident_response": [
        "보안 사고 대응", "침해 사고 분석", "디지털 포렌식", 
        "보고서 작성", "사고 교훈 도출", "사고 후 복구"
    ],
    "digital_forensics": [
        "포렌식 수사 절차", "증거 수집", "로그 분석", 
        "디지털 장치 분석", "메모리 포렌식", "디지털 증거 보존"
    ],
    "cloud_security": [
        "클라우드 보안 책임", "IAM 관리", "데이터 암호화", 
        "클라우드 구성 관리", "서버리스 보안", "멀티 클라우드 보안"
    ],
    "application_security": [
        "애플리케이션 보안 원칙", "코드 리뷰", "애플리케이션 테스트", 
        "취약점 방어 기법", "API 보안", "애플리케이션 패치 관리"
    ],
    "network_security": [
        "네트워크 세분화", "방화벽 설정", "VPN 사용", 
        "네트워크 접근 제어", "위협 탐지 시스템", "보안 로그 관리"
    ],
    "web_application_firewall": [
        "WAF 설정", "웹 보안 정책", "웹 공격 탐지", 
        "SQL 인젝션 방어", "XSS 방어", "WAF 로그 분석"
    ],
    "cybercrime_analysis": [
        "사이버 범죄 기법", "공격 동기 분석", "금융 범죄", 
        "디지털 자산 보호", "범죄 조직 추적", "범죄 예방 전략"
    ],

    # 클라우드 및 데이터 보호
    "cloud_security_policies": [
        "클라우드 보안 정책", "구성 관리", "데이터 암호화", 
        "클라우드 액세스 제어", "멀티 팩터 인증", "클라우드 규정 준수"
    ],
    "data_encryption_techniques": [
        "대칭키 암호화", "비대칭키 암호화", "SSL/TLS", 
        "암호화 키 관리", "데이터 전송 보호", "암호화 알고리즘"
    ],
    "data_masking": [
        "데이터 마스킹 기법", "민감 정보 보호", "데이터 가시성 제한", 
        "개인정보 비식별화", "암호화 대비", "데이터 변형"
    ],
    "supply_chain_security": [
        "공급망 위험 관리", "서드파티 보안", "취약점 평가", 
        "위험 기반 접근", "보안 테스트", "공급망 모니터링"
    ],
    "serverless_security": [
        "서버리스 아키텍처", "보안 구성", "권한 관리", 
        "데이터 보호", "무서버 컴퓨팅", "서버리스 보안 도구"
    ],
    "container_security": [
        "컨테이너 이미지 보안", "데브옵스 보안", "도커 보안", 
        "컨테이너 취약점 스캔", "이미지 무결성", "오케스트레이션 보안"
    ],
    "data_classification_access_control": [
        "데이터 분류 기준", "접근 통제 정책", "데이터 민감도 평가", 
        "접근 권한 설정", "데이터 보호 규정", "보안 정책 관리"
    ],
    "data_loss_prevention": [
        "DLP 정책 설정", "데이터 유출 모니터링", "데이터 흐름 제어", 
        "민감 데이터 보호", "내부 위협 탐지", "DLP 도구 활용"
    ],

    # 접근 관리
    "identity_access_management": [
        "IAM 기본 원칙", "사용자 인증", "역할 기반 접근 제어", 
        "권한 위임", "ID 관리 도구", "액세스 제어"
    ],
    "multi_factor_authentication": [
        "MFA 원리", "인증요소 종류", "OTP 활용", 
        "바이오메트릭 인증", "물리적 토큰", "MFA 설정"
    ],
    "single_sign_on_saml": [
        "SSO 개념", "SAML 원리", "SSO 구현", 
        "인증 토큰 관리", "SSO 보안", "SSO 사례"
    ],
    "role_based_access_control": [
        "RBAC 정의", "역할 할당", "권한 관리", 
        "역할 기반 정책", "접근 통제", "권한 설정"
    ],
    "privilege_escalation_prevention": [
        "권한 상승 탐지", "권한 설정 관리", "민감 데이터 보호", 
        "내부 위협 방지", "액세스 로깅", "보안 로그 분석"
    ],
    "remote_access_security": [
        "원격 액세스 보안", "VPN 설정", "원격 데스크탑 보안", 
        "네트워크 세분화", "인증 강화", "보안 점검"
    ],

    # 최신 보안 동향 및 기술
    "ai_security": [
        "AI 기반 위협 탐지", "머신러닝 알고리즘", "자동화 대응", 
        "보안 분석", "행위 기반 탐지", "위협 예측"
    ],
    "blockchain_security": [
        "블록체인 개념", "스마트 계약 보안", "분산형 네트워크", 
        "합의 알고리즘", "거래 검증", "블록체인 취약점"
    ],
    "iot_security": [
        "IoT 장치 보안", "네트워크 분리", "원격 제어 보호", 
        "IoT 데이터 암호화", "인증 관리", "보안 표준 준수"
    ],
    "mobile_application_security": [
        "모바일 앱 취약점", "앱 검증", "권한 설정", 
        "데이터 암호화", "악성 코드 방어", "모바일 방화벽"
    ],
    "quantum_security": [
        "양자 암호화", "양자 컴퓨팅", "보안 프로토콜", 
        "양자 내성 암호", "양자 암호의 원리", "보안 난이도 개선"
    ],
    "secops_automation": [
        "보안 운영 자동화", "위협 인텔리전스 통합", "자동화 도구", 
        "SecOps 베스트 프랙티스", "보안 모니터링", "사고 대응"
    ],
    "digital_identity_biometric_authentication": [
        "생체 인증", "디지털 ID 관리", "바이오메트릭 보안", 
        "생체 정보 보호", "디지털 ID 사용 사례", "접근 제어"
    ],
    "siem": [
        "SIEM 원리", "보안 로그 관리", "실시간 모니터링", 
        "이벤트 상관관계 분석", "보안 인텔리전스", "SIEM 설정"
    ]
}

# 기본 설정
DEFAULT_CONFIG = {
    "domain": "Information Security",
    "style": "focused, applied, and in-depth",  # 집중적이고 응용 중심, 깊이 있는 설명 스타일
    "language": "Korean",
    "num_sets": 1,
}

# 시스템 프롬프트 설정
SYSTEM_PROMPTS = {
    "security_expert": """정보보안 실무 학습에 최적화된, 연속적이고 확장 가능한 대화를 제공합니다. 각 대화는 학습자가 개념을 심화시키고 실무에서의 응용 가능성을 체감할 수 있도록 설계되었습니다. 다음 지침을 따르세요:

    1. **핵심 개념 설명**: 첫 번째 답변에서는 기본 개념을 명확하게 설명하고, 후속 질문을 통해 깊이 있는 내용을 다룰 여지를 남겨 두세요. 각 답변은 최소 500자 이상이 되도록 구체적이고 자세히 작성합니다.
    2. **연속성과 단계적 확장**: 후속 대화에서는 이전 답변의 핵심 내용을 요약하며 시작하고, 새로운 정보나 사례를 추가하여 실무에서의 적용 가능성을 확장하세요.
    3. **자체 평가 및 사고 유도**: 학습자가 스스로 이해도를 점검할 수 있도록 체크 포인트나 질문을 포함하여, 주제를 깊이 있게 이해할 수 있도록 돕습니다.
    4. **실무 예시와 시나리오**: 각 답변에 실무와 연결된 간단한 사례나 시나리오를 포함하여, 개념이 실제 환경에서 어떻게 적용되는지 학습자가 상상할 수 있게 하세요.
    5. **연관 주제와 최신 동향**: 대화의 끝에는 연관된 주제나 최신 보안 동향을 간단히 언급하여, 학습자가 자연스럽게 새로운 질문이나 연관 개념을 생각할 수 있도록 유도하세요.
    
    각 답변에서 다음 요소들을 순차적으로 포함하도록 합니다:
    - 기본 개념과 실무 연결 예시: 첫 답변에서 핵심 개념을 명확히 전달하고, 후속 질문에 확장 가능성을 남깁니다.
    - 단계별 정보 확장: 이전 답변의 핵심을 요약하고, 새 정보와 실무 사례로 확장합니다.
    - 이해도 점검 질문 또는 체크 포인트: 학습자가 자신의 이해도를 점검할 수 있는 간단한 질문을 포함합니다.
    - 사고를 유도하는 질문: 학습자가 스스로 생각해볼 수 있는 문제 해결을 유도하는 질문을 추가합니다.
    - 연관 주제와 최신 동향: 연관된 주제나 최신 보안 트렌드를 언급하여, 대화가 자연스럽게 확장되도록 유도합니다."""
}

# 출력 설정
OUTPUT_DIR = "training_data"