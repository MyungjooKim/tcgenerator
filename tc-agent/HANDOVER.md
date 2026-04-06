# TC 자동화 파이프라인 — 핸드오버 가이드

> **이 문서의 목적**: 이 폴더를 처음 받는 동료가 Claude Code를 이용해 동일한 품질의 TC를 즉시 생성할 수 있도록 한다.
> **지원 환경**: Mac / Windows 모두 지원. 명령어가 다른 경우 탭으로 구분하여 표기한다.
> 이 문서를 먼저 읽고, 이해한 뒤 작업을 시작한다.

---

## 1. 프로젝트 개요

**Supercycl TC 자동화 파이프라인**

기획 문서(PDF, GitHub 목업 URL, 텍스트 등)를 입력하면 → BDD 형식의 테스트 케이스(TC)를 자동 생성하고 → Excel 파일로 출력한다.

- **서비스**: Supercycl (암호화폐 모바일 거래 서비스)
- **TC 형식**: BDD (Given / When / Then) 방식의 수동 테스트 케이스
- **출력물**: `.md` 파일 + `.xlsx` 파일 (Excel)

---

## 2. 폴더 구조

```
tc-agent/
│
├── HANDOVER.md                  ← 지금 읽는 이 파일
├── SETUP_CHECKLIST.md           ← 초기 세팅 체크리스트
│
├── common/                      ← 모든 Phase에 공통 적용되는 규칙
│   ├── tc-rules.md              ← ★ 핵심 규칙 파일 (반드시 읽기)
│   ├── tc-sample.md             ← TC 스타일 샘플 (문체/형식 기준)
│   └── policy/                  ← 거래소별 정책 문서
│       ├── 00_TC_Policy_Overview.md
│       ├── 01_TC_Policy_Exchange.md
│       ├── 02_TC_Policy_Leverage.md
│       └── 03_TC_Policy_AutoTPSL.md
│
├── phase3-mobile-mockup/        ← 현재 진행 중인 Phase (Phase 3)
│   ├── tc-rules-override.md     ← Phase 3 전용 규칙 (공통 규칙 덮어씀)
│   ├── _workspace/              ← 파이프라인 중간 산출물
│   │   ├── 00_input/            ← 입력 파일 (기획서, URL 등)
│   │   ├── 01_parsed/           ← 파싱 결과
│   │   ├── 02_policy/           ← 정책 정리
│   │   ├── 03_features/         ← 기능 목록 + 분류표
│   │   │   ├── feature_list.md
│   │   │   └── classification_v1_APPROVED.md  ← 사람이 승인한 분류표
│   │   ├── 04_tc/               ← 도메인별 TC 초안
│   │   │   ├── tc_draft_AUTH.md
│   │   │   ├── tc_draft_TRAD.md
│   │   │   └── ... (도메인 수만큼)
│   │   └── 05_review/           ← 검토 및 최종본
│   │       ├── review_report.md
│   │       └── tc_final.md      ← 명령어로 직접 생성한 병합본
│   └── outputs/                 ← 최종 산출물
│       └── SPCY_TC_P3_MobileMockup_YYYYMMDD_vN.xlsx
│
├── scripts/
│   └── build_excel.py           ← TC → Excel 변환 스크립트
│
└── .claude/skills/              ← Claude Code 에이전트 스킬 파일
    ├── tc-orchestrator/         ← 파이프라인 총괄
    ├── doc-parser/              ← 문서 파싱
    ├── policy-analyst/          ← 정책 정리
    ├── feature-mapper/          ← 기능 목록 추출
    ├── feature-classifier/      ← 분류표 생성
    ├── tc-writer/               ← TC 작성
    ├── tc-reviewer/             ← TC 검토
    └── output-builder/          ← 산출물 생성
```

> **경로 표기**: 이 문서는 `/` 를 기본으로 표기한다. Windows에서는 `/` 와 `\` 모두 동작한다.

---

## 3. TC 파이프라인 전체 흐름

```
[입력] 기획 문서 / GitHub URL / 텍스트
    ↓
① doc-parser       → parsed_content.md
    ↓
② policy-analyst   → policy_doc.md
    ↓
③ feature-mapper   → feature_list.md
    ↓
④ feature-classifier → classification_draft.md
    ↓
⛔ HUMAN GATE      ← 사람이 분류표 검토·승인 (필수)
    ↓ (승인 후 classification_v1_APPROVED.md 저장)
⑤ tc-writer        → tc_draft_{도메인}.md (도메인별 순차 실행)
    ↓
⑥ tc-reviewer      → review_report.md (검토만, tc_final.md 생성 안 함)
    ↓
[직접 실행]    → tc_final.md 병합 (섹션 6 명령어 사용)
    ↓
[직접 실행]    → Excel 빌드 (python scripts/build_excel.py)
    ↓
[출력] outputs/*.xlsx
```

> ⚠️ **중요**: `tc_final.md` 생성과 Excel 빌드는 Claude 에이전트가 하지 않는다.
> 아래 섹션 6의 명령어를 직접 실행한다.

---

## 4. TC 작성 핵심 규칙

### 4-1. TC 형식 (템플릿)

```markdown
### **SC-{대분류코드}-{중분류코드}-{NNN}** — {제목}   ← 최소 TC (bold heading)
### SC-{대분류코드}-{중분류코드}-{NNN} — {제목}        ← 일반 TC (plain heading)

| 항목 | 내용 |
|------|------|
| 대분류 | {대분류명} ({대분류코드}) |
| 중분류 | {중분류명} |
| 소분류 | {소분류명} |
| 분류 | Positive / Negative / Edge |
| 우선순위 | High / Medium / Low |
| 플랫폼 | Web(Mobile) / iOS Safari / Android Chrome / 공통 |
| 연관 화면 | /route 또는 컴포넌트명 |

**사전 조건**
1. 조건 A (계정/인증 상태)
2. 조건 B (화면/탭 진입 상태)
3. 조건 C (UI 조작 완료 상태)

**테스트 단계**
1. 단계 1
2. 단계 2

**예상 결과**
- 측정 가능한 결과 명시

**비고**
- (없으면 생략)
```

### 4-2. TC ID 규칙

형식: `SC-{대분류코드}-{중분류코드}-{NNN}`

| 요소 | 설명 | 예시 |
|------|------|------|
| SC | 프로젝트 고정 접두사 | SC |
| 대분류코드 | 도메인 코드 (아래 목록 참조) | AUTH, TRAD |
| 중분류코드 | classification_v1_APPROVED.md 기준 | LOGN, ORDF |
| NNN | 같은 중분류 내 001부터 순차 | 001, 002 |

**도메인 코드 고정 목록:**

| 코드 | 한글명 | 포함 범위 |
|------|--------|----------|
| AUTH | 인증/온보딩 | 로그인, 약관, 온보딩 |
| LEVR | 레버리지 | 레버리지 설정, 안내 팝업 |
| TPSL | TP/SL | Auto TP/SL 설정, 주문 연동 |
| TRAD | 트레이딩 | 주문, 포지션, 대시보드 |
| SGNL | 시그널 | 시그널 카드, 팔로우 |
| FUND | 자금 | 지갑, 잔고 표시 |
| MOBL | 모바일UI | 반응형 레이아웃, BottomNav |
| SETG | 설정 | 로그아웃, 계정 설정 |

### 4-3. 사전 조건(Given) 작성 규칙

- **형식**: 번호 개조식 (`1. 조건A`, `2. 조건B`)
- **어미**: `~인 상태`, `~된 상태`, `~한 상태`로 끝맺음
- **순서**: 설정되는 순서대로 (계정 상태 → 화면 진입 → UI 조작)
- **금지**: 서술형 문장, "이다"로 끝맺음, 불릿(`-`) 사용

```
✅ 올바른 예:
1. YOUTHMETA 파트너코드로 가입한 체험 계정으로 로그인된 상태
2. 트레이딩 화면(/trade)이 표시된 상태
3. 코인 선택 드롭다운에서 BTC가 선택된 상태

❌ 잘못된 예:
- 사용자가 로그인되어 있다
- 트레이딩 화면을 열었다
```

### 4-4. 최소 TC 세트 기준

- **표기**: heading을 bold 처리 (`### **SC-XXX-YYY-001**`)
- **포함 조건**: 우선순위 High + Positive TC 전체 / 서비스 진입 차단 핵심 Negative TC
- **수량 목표**: 전체의 30~40%
- **금지**: `★` 기호 사용 (이전 방식, 현재는 bold heading으로 대체)

### 4-5. 분류별 비율 목표

| 분류 | 비율 | 설명 |
|------|------|------|
| Positive | ~50% | 정상 흐름 확인 |
| Negative | ~30% | 오류/권한 없음/잘못된 입력 |
| Edge | ~20% | 경계값, 동시성, 극단 상황 |

---

## 5. 새 Phase 시작하기

새 기획이 들어왔을 때 Claude Code에게 다음과 같이 요청한다:

```
이 [기획서/URL/내용]을 기반으로 TC를 만들어줘.
Phase 폴더: phase4-{이름}/
Phase 코드: P4_{이름}
```

Claude Code가 자동으로 `/tc-orchestrator` 스킬을 실행하여 파이프라인을 진행한다.

### ⛔ Human Gate 처리 방법

feature-classifier 완료 후 Claude Code가 멈추며 다음 메시지를 보낸다:

```
분류표 초안이 준비됐습니다: phase4-xxx/_workspace/03_features/classification_draft.md
검토 후 수정하시고, 승인 완료 시 파일을 classification_v1_APPROVED.md 로 저장 후 '승인됐어' 라고 알려주세요.
```

**처리 순서:**
1. `classification_draft.md` 열어서 분류 확인
2. 잘못된 분류 항목 수정 (⚠️ 불확실 항목 결정)
3. 파일을 `classification_v1_APPROVED.md`로 복사 저장

   **Mac (터미널):**
   ```bash
   cp phase4-xxx/_workspace/03_features/classification_draft.md \
      phase4-xxx/_workspace/03_features/classification_v1_APPROVED.md
   ```

   **Windows (PowerShell):**
   ```powershell
   Copy-Item "phase4-xxx\_workspace\03_features\classification_draft.md" `
             "phase4-xxx\_workspace\03_features\classification_v1_APPROVED.md"
   ```

4. Claude Code에게 **"승인됐어. 진행해줘"** 라고 입력

---

## 6. 주요 명령어

> 폴더 경로(`ROOT`)는 실제 위치로 변경한다.

---

### 6-1. tc_final.md 생성 (tc-reviewer 완료 후)

**Mac (터미널):**
```bash
ROOT="/Users/사용자명/tc-agent"
PHASE="phase3-mobile-mockup"
REVIEW="$ROOT/$PHASE/_workspace/05_review"
TC_DIR="$ROOT/$PHASE/_workspace/04_tc"

cat > "$REVIEW/tc_final.md" << 'EOF'
# Phase 3 TC 최종본
## 메타 정보
- Phase: P3_MobileMockup
- 총 TC: N개 / 최소 TC: N개 / 커버리지: N%
---
EOF

for domain in AUTH LEVR TPSL TRAD SGNL FUND MOBL SETG; do
  f="$TC_DIR/tc_draft_${domain}.md"
  [ -f "$f" ] && cat "$f" >> "$REVIEW/tc_final.md" && printf "\n---\n\n" >> "$REVIEW/tc_final.md"
done
echo "tc_final.md 생성 완료"
```

**Windows (PowerShell):**
```powershell
$ROOT = "C:\Users\사용자명\tc-agent"
$PHASE = "phase3-mobile-mockup"
$REVIEW = "$ROOT\$PHASE\_workspace\05_review"
$TC_DIR = "$ROOT\$PHASE\_workspace\04_tc"

@"
# Phase 3 TC 최종본
## 메타 정보
- Phase: P3_MobileMockup
- 총 TC: N개 / 최소 TC: N개 / 커버리지: N%
---
"@ | Out-File "$REVIEW\tc_final.md" -Encoding utf8NoBOM

foreach ($domain in @("AUTH","LEVR","TPSL","TRAD","SGNL","FUND","MOBL","SETG")) {
    $f = "$TC_DIR\tc_draft_$domain.md"
    if (Test-Path $f) {
        Get-Content $f -Encoding utf8 | Add-Content "$REVIEW\tc_final.md" -Encoding utf8
        "`n---`n" | Add-Content "$REVIEW\tc_final.md" -Encoding utf8
    }
}
Write-Host "tc_final.md 생성 완료"
```

---

### 6-2. Excel 빌드

**Mac (터미널):**
```bash
cd /Users/사용자명/tc-agent
source .venv/bin/activate
python3 scripts/build_excel.py \
  --phase P3_MobileMockup \
  --tc phase3-mobile-mockup/_workspace/05_review/tc_final.md \
  --output phase3-mobile-mockup/outputs
```

**Windows (PowerShell):**
```powershell
cd "C:\Users\사용자명\tc-agent"
.venv\Scripts\Activate.ps1
python scripts\build_excel.py `
  --phase P3_MobileMockup `
  --tc "phase3-mobile-mockup\_workspace\05_review\tc_final.md" `
  --output "phase3-mobile-mockup\outputs"
```

---

### 6-3. 의존성 설치 (최초 1회)

**Mac (터미널):**
```bash
cd /Users/사용자명/tc-agent
python3 -m venv .venv
source .venv/bin/activate
pip install openpyxl
```

**Windows (PowerShell):**
```powershell
cd "C:\Users\사용자명\tc-agent"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install openpyxl
```

---

## 7. Excel 출력 규칙

- **파일명**: `SPCY_TC_{PhaseCode}_{YYYYMMDD}_v{N}.xlsx`
- **최소 TC 행**: 전체 행 bold 처리 (yellow 강조)
- **최소 TC 감지**: heading이 `### **SC-XXX**` 형식인 TC (bold heading)
- **버전 관리**: 같은 날 재빌드 시 `v2`, `v3` 순서로 증가

---

## 8. 트러블슈팅

### Claude Code가 작업 중간에 멈추는 경우

**원인**: Rate Limit (토큰 한도 초과)

**확인 방법**: `total_tokens: 0` 또는 "You've hit your limit" 메시지

**복구 방법**:
1. `04_tc/` 폴더에서 완료된 도메인 파일 확인
2. 누락된 도메인만 재실행 요청: `"TRAD 도메인 TC 이어서 작성해줘"`
3. `review_report.md` 존재하면 → tc_final.md 병합 명령 직접 실행 (섹션 6-1)
4. Excel은 항상 직접 빌드 (섹션 6-2)

---

### 최소 TC가 Excel에서 감지되지 않는 경우

heading 형식 확인:

**Mac:**
```bash
grep "^### " phase3-mobile-mockup/_workspace/04_tc/tc_draft_AUTH.md | head -5
```

**Windows (PowerShell):**
```powershell
Select-String "^### " "phase3-mobile-mockup\_workspace\04_tc\tc_draft_AUTH.md" | Select-Object -First 5
```

- `### **SC-AUTH-LOGN-001**` → bold heading (최소 TC) ✅
- `### ★ SC-AUTH-LOGN-001` → 구형 형식 ❌

구형 형식 일괄 변환:

**Mac:**
```bash
sed -i '' 's/^### ★ \(SC-[A-Z-]*[0-9]*\)/### **\1**/g' {파일경로}
```

**Windows (PowerShell):**
```powershell
$f = "경로\tc_draft_AUTH.md"
(Get-Content $f -Encoding utf8) `
  -replace '^### ★ (SC-[A-Z]+-[A-Z]+-\d+)', '### **$1**' `
  | Set-Content $f -Encoding utf8NoBOM
```

---

### Windows: PowerShell 실행 정책 오류

```
Activate.ps1을(를) 실행할 수 없습니다. 스크립트 실행이 사용 안 함으로 설정되어 있습니다.
```

**해결** (PowerShell 관리자 권한 실행 후):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Windows: python 명령을 찾을 수 없는 경우

```powershell
python --version   # 없으면
py --version       # 이것도 시도
```

없으면: https://www.python.org/downloads/ 에서 설치
(설치 시 **"Add Python to PATH"** 체크박스 반드시 선택)

---

### Windows: tc_final.md 인코딩 문제 (Excel 한글 깨짐)

```powershell
# PowerShell 세션 인코딩 UTF-8로 강제 설정
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$OutputEncoding = [Text.Encoding]::UTF8
```

또는 tc_final.md를 VSCode에서 열어 우하단 인코딩이 "UTF-8"인지 확인 후 저장.

---

### 사전 조건이 구형 형식인 경우

```
❌ - 사용자가 로그인되어 있다
✅ 1. 로그인이 완료된 상태
```

Claude Code에게: `"tc_draft_AUTH.md 의 사전 조건을 번호 개조식 ~상태 형식으로 수정해줘"`

---

## 9. Phase 3 현황 (인수인계 시점 기준)

| 항목 | 내용 |
|------|------|
| Phase | P3_MobileMockup |
| 소스 | https://5kyo.github.io/supercycl-mockup/ |
| 총 TC | 107개 |
| 최소 TC | 40개 (37.4%) |
| 커버리지 | 100% |
| 최신 Excel | `phase3-mobile-mockup/outputs/SPCY_TC_P3_MobileMockup_20260403_v4.xlsx` |
| 승인된 분류표 | `phase3-mobile-mockup/_workspace/03_features/classification_v1_APPROVED.md` |
| 도메인 | AUTH / LEVR / TPSL / TRAD / SGNL / FUND / MOBL / SETG (8개) |

**미완료 사항 (다음 v5 빌드 필요)**:
- MOBL 도메인에 플랫폼 특화 TC 미포함 (10개 추가 예정)
  - 모바일 공통 5개 (360px 레이아웃, BottomNav, 바텀시트, 키보드, 터치)
  - iOS Safari 3개 (주소창 숨김, Safe Area, iOS 키보드)
  - Android Chrome 2개 (뒤로가기, Chrome 주소창)
- 세부 내용: `phase3-mobile-mockup/tc-rules-override.md` 섹션 7 참조

---

## 10. Claude Code에게 전달할 첫 번째 지시문

**Mac:**
```
이 폴더(/Users/사용자명/tc-agent)에서 TC 자동화 파이프라인을 운영 중이야.
HANDOVER.md를 먼저 읽고, 이후 작업 요청에 따라 진행해줘.
```

**Windows:**
```
이 폴더(C:\Users\사용자명\tc-agent)에서 TC 자동화 파이프라인을 운영 중이야.
HANDOVER.md를 먼저 읽고, 이후 작업 요청에 따라 진행해줘.
```

이후 원하는 작업을 요청한다:
- **새 TC 추가**: `"Phase 3 MOBL 도메인에 플랫폼 특화 TC를 추가해줘"`
- **새 Phase 시작**: `"이 URL 기반으로 새 Phase TC 만들어줘: [URL]"`
- **Excel 재빌드**: `"tc_final.md 기반으로 Excel 다시 빌드해줘"`

---

## 11. TC 웹앱 (tc-ui)

Claude Code 없이 **웹 브라우저**에서 TC를 생성할 수 있는 별도 웹앱이 있다.
Git 저장소에서 `tc-agent`과 **같은 부모 폴더**에 `tc-ui`이 함께 존재한다.

```
repo/
├── tc-agent/   ← 이 폴더 (Claude Code 파이프라인)
└── tc-ui/              ← 웹 UI (Flask 서버)
```

### 웹앱 실행

**Mac:**
```bash
cd ../tc-ui
python3 scripts/app_v2.py
# → http://localhost:5001 접속
```

**Windows:**
```powershell
cd ..\tc-ui
python scripts\app_v2.py
```

### 웹앱 필수 설정

| 파일 | 설명 |
|------|------|
| `tc-ui/.env` | Anthropic API 키 설정 (각자 본인 키) |
| `tc-ui/config.json` | Google Drive 폴더 ID (Drive 업로드 시) |
| `tc-ui/credentials.json` | Google OAuth 인증 파일 (Drive 업로드 시) |

> ⚠️ `.env`, `config.json`, `credentials.json` 은 모두 Git에서 제외됨.
> 각자 `cp .env.example .env` / `cp config.example.json config.json` 후 본인 값 입력.

---

## 12. 주요 파일 빠른 참조

| 파일 | 역할 | 읽기 빈도 |
|------|------|----------|
| `common/tc-rules.md` | TC 작성 규칙 전체 | 매번 필수 |
| `common/tc-sample.md` | TC 스타일 샘플 (문체·형식 기준) | 매번 필수 |
| `phase3-mobile-mockup/tc-rules-override.md` | Phase 3 전용 규칙 | Phase 3 작업 시 필수 |
| `phase3-mobile-mockup/_workspace/03_features/classification_v1_APPROVED.md` | 승인된 분류표 (TC ID 기준) | TC 작성 시 필수 |
| `scripts/build_excel.py` | Excel 빌드 스크립트 | 빌드 시 |
| `.claude/skills/tc-writer/skill.md` | TC 작성 에이전트 규칙 | (자동 사용) |
| `.claude/skills/tc-orchestrator/skill.md` | 파이프라인 총괄 규칙 | (자동 사용) |
