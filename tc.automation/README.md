# TC Automation — Supercycl × Youthmeta

기획서 PDF를 기반으로 BDD 테스트 케이스 명세서를 자동 생성하는 시스템입니다.
**신규 기능 추가 시마다** `specs/`에 기획서 PDF를 넣고 Claude Cowork + 빌드 스크립트를 실행하면
동일한 정책 기준으로 TC 체크리스트 Excel이 자동 생성됩니다.

---

## 폴더 구조

```
tc.automation/
│
├── specs/                  # 기능 기획서 PDF (신규 기능 추가 시 여기에 저장)
│   └── README.md
│
├── policy/                 # TC 작성 정책 문서 (공통 기준 — 변경 시 팀 협의 필요)
│   ├── 00_TC_Policy_Overview.md    # 전체 정책 개요 (컬럼 구조, N/A 규칙 등)
│   ├── 01_TC_Policy_Exchange.md    # 거래소별 지원 기능 정책
│   ├── 02_TC_Policy_Leverage.md    # 레버리지 설정 정책
│   ├── 03_TC_Policy_AutoTPSL.md    # Auto TP/SL 정책
│   └── 99_TC_Template.md           # TC 작성 템플릿 및 예시
│
├── data/                   # TC 원본 데이터 (Python)
│   ├── tc_new_final.py     # Phase 00A/B/C (신규 기능 TC)
│   └── tc_old_final.py     # Phase 01~18 (기존 기능 TC)
│
├── scripts/                # 빌드 스크립트
│   ├── build_tc_v8.py      # v8 빌드 (이전 버전, 참고용)
│   └── build_tc_v7.py      # v7 빌드 (이전 버전, 참고용)
│
├── outputs/                # 생성된 결과물
│   ├── SPCY_TC_Youthmeta_SmokeChecklist_v9.xlsx  # ← 현재 최신 (v9, 수동 배포용)
│   ├── SPCY_TC_Youthmeta_v8_Final.xlsx           # v8 (이전 버전)
│   ├── SPCY_TC_Youthmeta_v7_Final.xlsx           # v7 (이전 버전)
│   └── test_env_checklist.html                   # 테스트 환경 사전 체크리스트
│
├── guide/                  # 팀원 공유용 가이드
│   └── SPCY_QA_TC_AutoGen_System_Guide.pptx      # TC 자동화 시스템 협업 가이드
│
├── README.md               # 이 파일
├── HANDOFF.md              # Claude 세션 인수인계 문서
└── requirements.txt        # Python 패키지 의존성
```

---

## 신규 기능 TC 생성 워크플로우

새 기능이 추가될 때마다 아래 순서로 진행합니다.

```
1. specs/에 기획서 PDF 저장
        ↓
2. Claude Cowork 실행
   → policy/ 문서 + specs/ PDF 첨부
   → "이 기획서 기반으로 TC 작성해줘" 요청
        ↓
3. 생성된 TC 검토
   → N/A 거래소 확인 및 보정
   → data/ Python 파일 업데이트
        ↓
4. 빌드 실행
   → python3 scripts/build_tc_vX.py
        ↓
5. outputs/ Excel 배포
   → 테스터에게 공유
```

---

## 처음 설치하는 경우

### 1. Python 3 확인

```bash
python3 --version
# Python 3.8 이상이면 됩니다
```

없으면 [python.org](https://www.python.org/downloads/)에서 설치하세요.

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. Claude Desktop (Cowork) 설치

TC 자동 생성에 사용합니다. [claude.ai/download](https://claude.ai/download)에서 데스크탑 앱을 설치하세요.

---

## 빌드 실행 (기존 TC 재생성)

```bash
# tc.automation/ 폴더에서 실행
python3 scripts/build_tc_v8.py
```

성공 시 출력 예시:
```
✅ Saved: .../outputs/SPCY_TC_Youthmeta_v8_Final.xlsx
   전체 TC     : 134개
   최소 TC 세트 : 53개 (40%)
   컬럼        : 18개
   시트        : 표지 / TC 전체목록 / TC 통계 / 최소 TC 세트
```

---

## Excel 결과물 구성

| 시트 | 내용 |
|------|------|
| 📋 표지 | 프로젝트 개요, 범례, 판정 기준 |
| 🧪 TC 전체목록 | 전체 134개 TC (BDD 형식, 거래소별 판정 컬럼) |
| 📊 TC 통계 | 대분류 / Phase별 / 우선순위별 통계 |
| 🎯 최소 TC 세트 | 리스크 기반 선별 53개 TC |

### 판정 코드

| 코드 | 의미 |
|------|------|
| `Pass` | 기대 결과와 일치 |
| `Fail` | 버그 발생 → 리포트 필수 |
| `N/T` | 미테스트 (기본값) |
| `N/A` | 해당 없음 (거래소 미지원 등) |

### 테스터 배정

| 테스터 | 담당 거래소 |
|--------|------------|
| Tester 1 | OKX, Bybit |
| Tester 2 | Gate, Bitget, Hyperliquid |

---

## TC 데이터 수정 방법

### 기존 TC 수정

`data/tc_old_final.py` 또는 `data/tc_new_final.py`를 열어 해당 TC 튜플을 수정합니다.

```python
(
    "Phase 03",        # 단계
    "SPCY-03-001",     # TC ID
    "UI/UX",           # 소분류 (테스트 유형)
    "Auto TP/SL",      # 중분류 (기능 영역)
    "시나리오 설명",    # 시나리오 요약
    "P1",              # 우선순위 (P1 / P2 / P3)
    "High",            # 중요도 (High / Medium / Low)
    "GIVEN ...",       # 사전 조건
    "WHEN ...",        # 행동
    "THEN ...",        # 기대 결과
    "",                # 비고
)
```

### N/A 규칙 추가

`scripts/build_tc_v8.py` 상단의 `EXCHANGE_NA` 딕셔너리에 추가합니다.

```python
EXCHANGE_NA["SPCY-XX-XXX"] = ["Gate", "Bitget"]  # 해당 거래소에 N/A 적용
```

N/A 정책 기준은 `policy/00_TC_Policy_Overview.md` 섹션 4.3을 참고하세요.

---

## 버전 히스토리

| 버전 | 주요 변경사항 |
|------|--------------|
| v9 | 기대 결과 실제 동작 기준으로 수정 반영 (내부 테스트 후 확정) |
| v8 | 테스터 배정 서브헤더 / 거래소 N/A 전체 정비 / 최소 TC 세트 시트 추가 |
| v7 | 대분류/중분류/소분류 계층 / 5개 거래소 컬럼 / Tester 1·2 컬럼 |
