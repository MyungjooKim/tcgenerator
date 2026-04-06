# TC 자동화 작업 인수인계 문서

> 이 문서는 새 Claude 세션에서 작업을 이어받을 때 사용합니다.
> 폴더 경로: `/Users/myungjookim/_claude26/tc.automation`

---

## 1. 작업 배경

**프로젝트:** Supercycl × Youthmeta 파트너 버전 1.0
**목적:** BDD 기반 테스트 케이스 명세서를 Python 스크립트로 자동 생성
**대상 기능:** Auto TP/SL 설정 + 유스메타 유입 유저 레버리지 2배 고정
**대상 거래소:** Gate / OKX / Bybit / Bitget / Hyperliquid (5개)
**테스터 배정:** Tester 1 → OKX, Bybit / Tester 2 → Gate, Bitget, Hyperliquid

---

## 2. 시스템 개요 (TC 자동화 파이프라인)

새로운 기능이 추가될 때마다 아래 파이프라인으로 TC를 자동 생성합니다.

```
specs/에 기획서 PDF 저장
        ↓
Claude Cowork 실행
  → policy/ 문서 + specs/ PDF 첨부
  → "이 기획서 기반으로 TC 작성해줘" 요청
        ↓
생성된 TC 검토 및 data/ 업데이트
  → N/A 거래소 확인 및 보정
  → data/tc_new_final.py 업데이트
        ↓
빌드 실행
  → python3 scripts/build_tc_v8.py
        ↓
outputs/ Excel 배포
  → 테스터에게 공유
```

---

## 3. 폴더 구조

```
tc.automation/
├── specs/                  # 기능 기획서 PDF (신규 기능 추가 시 여기에 저장)
│   └── README.md           # 파일 명명 규칙 및 사용법
│
├── policy/                 # TC 작성 정책 문서 (공통 기준 — 변경 시 팀 협의 필요)
│   ├── 00_TC_Policy_Overview.md    # 전체 정책 (컬럼 구조, N/A 규칙 등)
│   ├── 01_TC_Policy_Exchange.md    # 거래소별 지원 기능
│   ├── 02_TC_Policy_Leverage.md    # 레버리지 정책
│   ├── 03_TC_Policy_AutoTPSL.md    # Auto TP/SL 정책
│   └── 99_TC_Template.md           # TC 작성 템플릿 및 예시
│
├── data/                   # TC 원본 데이터 (Python)
│   ├── tc_new_final.py     # Phase 00A/B/C — 신규 기능 TC (24개)
│   └── tc_old_final.py     # Phase 01~18 — 기존 기능 TC (110개)
│
├── scripts/                # 빌드 스크립트
│   ├── build_tc_v8.py      # ← 현재 최신 빌드 스크립트
│   └── build_tc_v7.py      # 이전 버전 (참고용)
│
├── outputs/                # 생성된 결과물
│   ├── SPCY_TC_Youthmeta_SmokeChecklist_v9.xlsx  # ← 현재 최신 (v9, 수동 배포용)
│   ├── SPCY_TC_Youthmeta_v8_Final.xlsx           # v8 (이전 버전)
│   ├── SPCY_TC_Youthmeta_v7_Final.xlsx           # v7 (이전 버전)
│   └── test_env_checklist.html                   # 테스트 환경 사전 체크리스트
│
├── guide/                  # 팀원 공유용 가이드
│   └── SPCY_QA_TC_AutoGen_System_Guide.pptx      # TC 자동화 시스템 협업 가이드 (4슬라이드)
│
├── README.md               # 팀원 공유용 설치/실행 가이드
├── HANDOFF.md              # 이 파일 (Claude 세션 인수인계)
├── requirements.txt        # openpyxl>=3.1.0
└── .gitignore
```

---

## 4. 빌드 방법

```bash
# tc.automation/ 폴더에서 실행
pip install -r requirements.txt
mkdir -p outputs
python3 scripts/build_tc_v8.py
```

출력: `outputs/SPCY_TC_Youthmeta_v8_Final.xlsx`

> **참고:** 현재 최신 배포본은 `outputs/SPCY_TC_Youthmeta_SmokeChecklist_v9.xlsx`이며,
> 이 파일은 v8 빌드 결과물에 실제 테스트 결과를 반영하여 수동으로 수정한 버전입니다.

---

## 5. Excel 결과물 구성 (v9 기준)

| 시트 | 내용 |
|------|------|
| 📋 표지 | 프로젝트 개요, 범례, 판정 기준 |
| 🧪 TC 전체목록 | 전체 134개 TC, 18컬럼, 거래소별 판정 + 드롭다운 |
| 📊 TC 통계 | 대분류/Phase별/우선순위별 통계 (파스텔 색상) |
| 🎯 최소 TC 세트 | 리스크 기반 선별 53개 TC |

**컬럼 구조 (18개):**
TC ID / 단계 / 대분류 / 중분류 / 소분류 / 시나리오 / 우선순위 / 중요도 / GIVEN / WHEN / THEN / 실제결과 / Gate / OKX / Bybit / Bitget / Hyperliquid / 비고

**Row 구조:**
- Row 1: 헤더 (거래소 컬럼은 테스터별 색상)
- Row 2: 테스터 배정 서브헤더 (드롭다운: Tester 1 / Tester 2)
- Row 3+: TC 데이터 (freeze_panes A3)

---

## 6. 버전 히스토리

| 버전 | 주요 변경 |
|------|---------|
| v9 | 기대 결과를 실제 동작 기준으로 수정 반영 (7개 셀: K74, K96, K141, K142, K147, F148, K148). 실제결과(L열) 초기화. Pass/Fail → N/T 리셋. 내부 테스트 후 확정. |
| v8 | 테스터 배정 서브헤더 / N/A 전체 정비 / 최소 TC 세트 시트 / 파스텔 통계 색상 / Tester 드롭다운 |
| v7 | 대분류/중분류/소분류 계층 / 5개 거래소 컬럼 |

---

## 7. 주요 결정사항 및 규칙

### TC ID 규칙
- 형식: `SPCY-{Phase}-{순번}` (예: SPCY-03-001)
- 최소 TC 세트 선정 항목: `★ ` 접두어 추가 (예: ★ SPCY-03-001)

### TC 데이터 튜플 형식
```python
(
    "Phase 03",      # 단계
    "SPCY-03-001",   # TC ID
    "UI/UX",         # 소분류 (테스트 유형)
    "Auto TP/SL",    # 중분류 (기능 영역)
    "시나리오 설명",  # 시나리오 요약
    "P1",            # 우선순위 (P1/P2/P3)
    "High",          # 중요도 (High/Medium/Low)
    "GIVEN ...",     # 사전 조건
    "WHEN ...",      # 행동
    "THEN ...",      # 기대 결과
    "",              # 비고
)
```

### N/A 정책 (EXCHANGE_NA dict)
`build_tc_v8.py` 상단의 `EXCHANGE_NA` 딕셔너리에서 관리

| 대상 TC | N/A 거래소 | 이유 |
|---------|-----------|------|
| Phase 00A/B/C, 01, 02 (33개) | Gate, Bybit, Bitget, Hyperliquid | 인증 단계는 OKX만 테스트 |
| Phase 05~08, 07, 08 (일부) | Gate | Auto TP/SL 미지원 |
| SPCY-06-002, 006, 007 | Gate, Bitget, Hyperliquid | TP/SL 수정 불가 |
| SPCY-06-008 | OKX, Bybit, Bitget | Gate/HL만 테스트 |

### 색상 규칙
- `PHASE_COLORS`: TC 전체목록 시트 Phase 구분 헤더 (진한 원색)
- `PHASE_COLORS_PASTEL`: TC 통계 시트 Phase별 행 (파스텔, 직접 정의)
- Tester 1: `1C6E38` (초록) / Tester 2: `2E4057` (어두운 파랑)

### 판정 코드
- `Pass` / `Fail` / `N/T` (미테스트, 기본값) / `N/A` (해당 없음)

### 최소 TC 세트 선정 기준
- P1/High 우선순위 TC
- Happy Path (대표 시나리오)
- 거래소별 동작 차이가 있는 TC
- 총 53개 / 134개 (40%)

---

## 8. 테스트 환경 체크리스트

**파일:** `outputs/test_env_checklist.html`
**형식:** 브라우저에서 열어 표 선택 → Ctrl+C → Confluence 붙여넣기

**구성 (11개 섹션):**
1. 개발 환경 배포
2. 접속 URL (Youthmeta 파트너 URL / 일반 URL)
3. 로그인 (이메일 + Web3 Wallet 5종)
4. Youthmeta 파트너 태깅 확인
5. 거래소 연동 (PortX SA / OAuth / 수동 API × 5개 거래소)
6. Hyperliquid 최초 신규 가입
7. 신규 기능 UI 노출 확인 (레버리지 Max 2x, Auto TP/SL 토글)
8. 모바일 접속 환경
9. One-way Mode 거래 확인 (5개 거래소)
10. Hedge Mode 거래 확인 (4개 거래소, Hyperliquid 제외)
11. Trading Performance / Daily P&L

---

## 9. 협업 가이드

팀원과 TC 자동화 시스템을 함께 사용하기 위한 가이드는 `guide/` 폴더를 참조하세요.

**공유 대상 파일:**
- `policy/` 폴더 전체 (TC 작성 정책 5개 문서)
- `guide/SPCY_QA_TC_AutoGen_System_Guide.pptx` (시스템 설명 PPT)
- `README.md` (설치 및 실행 가이드)
- `requirements.txt`

**설치 요구사항:**
- Claude Desktop (Cowork 모드) — TC 자동 생성에 사용
- Python 3.8 이상 + openpyxl (`pip install -r requirements.txt`)
- Excel / Google Sheets (결과물 검토용)

---

## 10. 앞으로의 작업 원칙

- 새 기능 추가 시: `specs/`에 PDF 저장 → `policy/` 문서 첨부하여 Claude Cowork 실행 → `data/` 업데이트 → `EXCHANGE_NA` 검토 → 빌드 순서로 진행
- 모든 산출물은 팀원과 공유 가능한 상태를 유지
- 테스트 환경 체크리스트는 Known Issue 해결 시 해당 행 삭제, 신규 이슈 발견 시 행 추가
- Excel outputs는 `.gitignore`에 포함 (빌드로 재생성)
- 이 HANDOFF.md는 새 Claude 세션 시작 시 첨부하여 컨텍스트를 전달하세요
