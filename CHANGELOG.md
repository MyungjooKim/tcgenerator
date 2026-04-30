# TC 자동화 도구 — 변경 이력 (Release Notes)

릴리즈 간 주요 변경사항을 기록합니다. 동료가 `git pull` 받은 후 이 파일을 먼저 읽으면 변경 내용을 빠르게 파악할 수 있습니다.

> **유지보수 메모 — 버전 업데이트 시**
> `tc-ui/scripts/app_v2.py` 상단의 `APP_VERSION`, `APP_VERSION_DATE`, `APP_VERSION_TAGLINE`,
> `APP_VERSION_HIGHLIGHTS` 4개 상수만 수정하면 UI 배지·What's New 배너·모달·JS 상수가 모두 자동 반영됩니다.
> 추가로 이 `CHANGELOG.md`에 새 섹션을 추가하고 `git tag -a vX.Y.Z` 만 진행하면 끝입니다.

---

## v0.9.26 — 2026-04-29 (입력 소스 부록 표 자동 제거 + 입력 범위 엄격 준수)

> **요약 (중대)**: 동료 보고 — "SCR-809, SCR-810 입력으로 TC 생성했는데 무관한 notifications 케이스가 들어옴". 시뮬레이션 결과 SCR-810.md 본문 끝에 SCR-403/221/410 의 부록 에러 표가 붙어있던 게 원인. 옵션 A (프롬프트 강화) + 옵션 B (자동 감지/제거) 동시 적용.

### 🐛 사용자 보고 + 시뮬레이션

> "SCR-809, 810 md 를 넣고 tc 를 뽑아달라고 했는데, 관련 없는 기능들까지 포함되었다고 하는 리포트가 있어. API key 관련 md 인데, 불필요한 notifications 라는 케이스들이 분류표에 들어왔다고 해."

직접 시뮬레이션 결과:

```
[SCR-810.md 구조]
Line 1~87:    SCR-810: Edit API Keys 본문 (정상)
Line 87:      ---
Line 89:      **에러 케이스 (프로필/알림/PnL)**:    ← 부록 표
Line 91~104:  SCR-403, SCR-221, SCR-410 의 에러 케이스 12개
Line 106:     ---
```

기획서 작성자가 "다른 화면 참고용 부록" 으로 둔 표가 SCR-810.md 안에 섞여있어,
AI 가 SCR-810 입력으로 이걸 같이 보고 "Notifications", "Profile", "PnL" 도
관련 기능으로 판단 → 분류표에 무관한 항목 추가.

### ✨ 변경 — 이중 안전망 (옵션 A + B 동시)

#### 🛡 옵션 B (구조적) — 자동 부록 감지/제거

`strip_appendix_tables()` 신규 함수:
- 부록 헤더 패턴 감지: `**에러 케이스 (...)**:`, `## 부록`, `## 다른 화면` 등
- 부록 영역 안의 SCR 코드가 모두 입력 파일의 primary_scr 와 다르면 → 자동 제거
- 본문에 primary_scr 가 다수 등장하면 보존 (오탐 방지)
- 제거 정보를 사용자 로그로 안내

```python
def strip_appendix_tables(filename, content, primary_scr) -> tuple[str, list]:
    # 부록 헤더 + 다른 SCR 만 있는 영역 감지
    # 다음 '---' / 새 H1/H2 까지 skip
    # 안전장치: primary_scr 가 비어있으면 동작 안 함
```

`step_parse_sources` 가 마크다운 입력 처리 시 자동 호출:
```
[파싱] 부록 자동 제거 — SCR-810.md 의 '**에러 케이스 (프로필/알림/PnL)**'
       (다른 화면: SCR-221, SCR-403, SCR-410)
```

#### 🚨 옵션 A (프롬프트) — 입력 범위 엄격 준수

`build_tc_user_prompt` 의 `screen_code_hint` 섹션 강화:

```
## 🚨 입력 소스 범위 엄격 준수 (v0.9.26~ 절대 규칙)

이 작업의 입력 화면 코드 = `SCR-809`, `SCR-810` — 이 외에는 절대 다루지 마세요.

⚠️ 다음과 같은 상황에 주의하세요:
- 입력 파일 본문에 다른 SCR 코드가 표/참고/링크로 언급될 수 있습니다
- 본문 끝의 부록 표("에러 케이스 (프로필/알림/PnL)" 같은 형식) 에 있을 수 있음
- 인터랙션 설명에서 navigateTo('scr-XXX') 같은 다른 화면 참조 가능

→ 위 모든 경우에 다른 화면들의 분류/TC 는 만들지 마세요.

✅ 올바른 행동: 매핑 표의 SCR 만 사용
❌ 금지: SCR-221 (알림) 정보 봤다고 "Notifications" 중분류 추가
❌ 금지: navigateTo('scr-403') 봤다고 "Profile" 분류 추가
```

### 📊 효과 예측

| 시나리오 | v0.9.25 이하 | v0.9.26 |
|---------|------------|---------|
| SCR-810.md 부록 표 입력 | AI 가 "Notifications" 등 무관 분류 생성 | **자동 제거 (옵션 B) → AI 가 못 봄** |
| 본문에 navigateTo('scr-XXX') 산재 | 일부 화면 환각 가능 | **프롬프트 절대 규칙 (옵션 A) 차단** |
| 부록 패턴 변형 (오탐) | N/A | 안전장치 (`primary_scr` 다수 등장 시 보존) |

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.26, `strip_appendix_tables()` 신규 함수, `step_parse_sources` 마크다운 처리에 자동 호출, `build_tc_user_prompt` 의 `screen_code_hint` 강화 (입력 범위 엄격 준수) |
| `CHANGELOG.md` | v0.9.26 섹션 추가 |

---

## v0.9.25 — 2026-04-29 (시스템 점검용 샘플 기능 제거)

> **요약**: 사용자 결정 — "시스템 점검용 샘플은 이제 삭제해도 될 거 같아.. 앞으로 다른 것으로 사용해도 될 거 같거든". 초기 검증용으로 만들어진 샘플 PDF / 직접입력 기능을 제거하여 코드 정리.

### 🐛 사용자 결정

> "이제 화면 하단에 있는 시스템 점검용 샘플이면 이 기능은 삭제해도 될 거 같아.. 앞으로 다른 것으로 사용해도 될 거 같거든"

실제 입력 소스(SCR-XXX.md 등) 워크플로우가 안정화되어 샘플 검증 기능 불필요.

### 🗑 제거 대상 (8개 영역)

| # | 위치 | 내용 |
|---|------|------|
| 1 | 상수 | `SAMPLE_DOC_FILENAME`, `SAMPLE_DOC_CONTENT` (긴 마크다운 ~130줄) |
| 2 | 상수 | `SAMPLE_PDF_FILENAME`, `STATIC_DIR`, `SAMPLE_PDF_PATH` |
| 3 | 함수 | `_find_korean_font()`, `_find_korean_bold_font()` (PDF 생성 전용) |
| 4 | 함수 | `build_sample_pdf()` (~95줄) |
| 5 | 라우트 | `/sample-download`, `/sample-content` |
| 6 | CSS | `.sample-footer`, `.sample-banner`, `.btn-sample-dl`, `.btn-sample-fill` |
| 7 | HTML | 푸터 영역 (`<footer class="sample-footer">`) |
| 8 | JS | `loadSampleDoc()` 함수 |
| 9 | startup | 서버 시작 시 PDF 사전 생성 로그 |

총 **~280줄** 코드 제거.

### 📊 효과

- **화면**: 푸터 영역 제거로 깔끔
- **코드**: 약 280줄 감소 (450KB → 443KB)
- **시작 속도**: PDF 사전 생성 단계 제거로 약간 빨라짐
- **유지보수**: 사용 안 하는 fpdf2 의존성 사실상 제거 (라이브러리 import 도 함수 안에 있어서 영향 적음)

### 🛡 보존된 것
- `OUTPUTS_DIR`, `WORKSPACE_ROOT`, `SPECS_DIR`, `TC_FILES_DIR` 등 다른 디렉토리는 그대로
- 다른 입력 소스 흐름(PDF / GitHub URL / 웹 / 마크다운 / 텍스트 추가) 은 그대로 작동
- `static/` 폴더는 .gitignore 에 그대로 (다른 정적 자원 위해 보존)

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.25, 샘플 관련 모든 코드 제거 (상수/함수/라우트/CSS/HTML/JS/startup) |
| `CHANGELOG.md` | v0.9.25 섹션 추가 |

---

## v0.9.24 — 2026-04-29 (한글 IME Enter 다중 처리 버그 fix)

> **요약 (중대)**: 사용자 보고 — "대화창에서 마지막으로 입력한 단어가 한 번 더 입력되는 버그", "그래서 AI 가 답변을 정확하게 하지 못해". 한글 IME composition 처리 누락이 원인.

### 🐛 사용자 보고

> "대화창에서 내가 마지막으로 입력한 단어가 한 번 더 입력이 되는 버그가 있어. 그래서 AI 가 답변을 정확하게 하지 못해"

스크린샷 분석:
- 사용자 입력: "Splash 기능은 이번에 삭제되었어... 각 화면별 정리가 필요해"
- 실제 전송 1: "Splash 기능은... 정리가 필요해" (정상) → AI 처리 중
- **실제 전송 2: "해" 한 글자만** ← 버그
- AI 응답: "'해'라는 요청이 모호합니다... 1. 해줘 2. 해(海/sun) 3. 단순 입력 실수..."

→ AI 가 답변을 못한 게 아니라 **잘못 들은 메시지("해")에 정확히 답변**한 것. 진짜 문제는 IME 버그로 잘린 메시지가 전송된 것.

### 🔍 원인

한글 입력기(IME) 동작:
1. 사용자가 "필요해" 입력 후 Enter
2. **첫 번째 Enter** → IME 가 마지막 글자 "해" 를 confirm (한글 조합 완료)
   - 이 시점: `event.key === 'Enter'` 이지만 `event.isComposing === true`
   - textarea value 는 아직 "필요" 상태일 수 있음
3. Enter handler 발동 → "필요" 또는 "필요해" 일부 전송
4. IME composition 완료 → "해" 가 textarea 에 잔류
5. 어떤 추가 이벤트로 다시 Enter 처리 → "해" 단독 전송

**기존 코드** (line 7349, 11100, 11107, 7097):
```javascript
if (e.key === 'Enter' && !e.shiftKey) {
  e.preventDefault();
  submitFromInput(input);
}
```
→ IME composition 중 Enter 도 처리해버려서 한글 마지막 글자가 잘림.

### 🛡 해결 — 표준 IME 가드 추가

```javascript
// v0.9.24: IME (한글/일본어/중국어) 조합 중 Enter 무시
// - e.isComposing: 표준 (Chrome/Firefox/Safari)
// - keyCode === 229: 일부 브라우저에서 IME composition 중 표시
if (e.isComposing || e.keyCode === 229) return;
if (e.key === 'Enter' && !e.shiftKey) {
  e.preventDefault();
  submitFromInput(input);
}
```

### 📌 적용 위치 (4곳)

| 위치 | 용도 |
|------|------|
| 메인 채팅 입력 (`#gateChatInput`) | 분류표 검토 미니 채팅 본체 |
| Floating bar 입력 (`#floatingAiInput`) | 하단 sticky 채팅 |
| 모달 채팅 입력 (`#floatingAiModalInput`) | 확대 모달 채팅 |
| 신규 프로젝트명 (`#newDashProjectName`) | 프로젝트 생성 입력 |

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.24, 4곳 IME 가드 추가 (`event.isComposing` / `keyCode === 229`) |
| `CHANGELOG.md` | v0.9.24 섹션 추가 |

---

## v0.9.23 — 2026-04-29 (원칙 G 강화 — 그룹 정의 + 의미 기반 우선순위 + AI 자기점검)

> **요약**: 사용자 통찰 — "중복 처리 규칙은 이미 tc-rules.md 에 있는데 (원칙 G), AI 가 100% 안 따른다." 검토 후 원칙 G 의 모호한 부분을 정량화 + AI 행동 지시 강화.

### 🐛 사용자 보고 + 분석

> "중복처리는 tc 만들 때 사용하는 규칙 파일에 들어가 있어야 하는 거 아냐? 이미 들어가 있었던 거 같은데... 검토해줘"

검토 결과:
- ✅ 원칙 G (그룹 단위 에러 패턴 통합) 가 v0.9.17 부터 들어가 있음
- ✅ `tc_rules` 가 매 호출마다 AI 에게 system prompt 로 전달됨
- ❌ 그러나 동료의 SCR-010~014 케이스에서 "3G/저사양 로딩 시간" 2개 중복 발생 — **AI 가 부분적으로 어김**

원인 추정 (사용자 피드백 기반):
- "그룹"의 정의가 모호 — AI 가 그룹 vs 화면 헷갈림
- 대표 화면 선택 기준이 SCR 번호 기반 → 사용자 임의 prefix / 분기 표기(007A/B/C) 시 무용지물
- 위반 시 시스템 동작이 명시 안 됨 — AI 가 "안 따라도 큰 문제 없겠지" 안일해질 가능성
- AI 가 자기 출력을 점검하는 단계 없음

### ✨ 변경 — 4가지 개선

#### G-0 신설 — "그룹" 의 정의 (사용자 OK)

```
그룹 = 같은 대분류 단위
- 분류표의 ## 대분류: 헤더로 묶이는 단위
- 보통 5~15개 화면(중분류) 포함
- 그룹 ≠ 화면. 비기능 TC 는 화면 단위가 아닌 그룹 단위로 관리
```

#### G-3 교체 — 의미 기반 대표 화면 우선순위 (사용자 우려 반영 + 대안 채택)

**Before**: SCR 번호 기반 → 사용자 우려: "SCR 번호가 항상 시퀀스가 아니고, 분기 표기(007A/B/C) 도 있어서 무의미"

**After**: 화면명/성격 기반 의미 우선순위

```
1순위: entry 성격 화면 — 화면명에 다음 키워드 포함:
       영문: Start, Splash, Entry, Initial, Landing, Sign-in Start, Begin
       한글: 시작, 진입, 처음, 초기
       또는 screen_code_map.md 의 character = "entry"

2순위: 분류표에서 가장 위에 등장하는 중분류 (사용자 작성 순서 존중)

3순위: 분류표 첫 번째 중분류

❌ 사용 금지: SCR 번호 / 알파벳 / 주관적 판단
```

모호 시: `[통합 — 대표 화면 선정 검토 필요]` 태그로 사용자 검토 유도

#### G-7 신설 — AI 와 시스템의 협력 관계 (사용자 우려 반영 + 대안 채택)

**Before 안**: "위반 시 시스템이 자동 제거함" — 사용자 우려: "AI 에게 위협적"

**After**: 협력 관계 어조

```
| 주체 | 역할 |
| AI | G-2 패턴 한 그룹에서 1번만 작성 — 처음부터 깔끔 (이상적) |
| 시스템 | 후처리 자동 검토 — 중복 발견 시 사용자에게 통합 제안 (안전망) |
| 사용자 | 자동 통합 클릭 또는 그대로 진행 결정 |

⚠️ AI 는 "후처리가 잡아줄 거니 적당히 해도 됨" 으로 해석 금지.
처음부터 1개만 작성이 사용자에게 가장 깨끗한 결과 제공.
```

#### G-8 신설 — AI 자기 점검 가이드 (사용자 질문 반영 + 명확화)

**Before 안**: "AI 가 자주 하는 실수" — 사용자 질문: "이게 사용자 안내인지 AI 행동 지시인지 모호"

**After**: AI 의 출력 직전 자기 점검 절차로 명확화

```
TC 작성 후 출력 직전 자기 점검 체크리스트:
1. ✓ 같은 그룹에 G-2 패턴 TC 가 2개 이상인가?
   → 있으면 G-3 우선순위로 1개 대표 화면 선정
2. ✓ "통합 가능"이 아닌 "스펙 명시" 케이스인가?
   → 스펙 에러는 보존 (G-1, G-6)
3. ✓ 대표 화면 비고에 [통합] 태그 있는가?
   → G-4 형식 확인

AI 가 자주 빠지는 함정 4가지:
❌ "Login Options 와 Login Complete 는 다른 화면이니 각각" → 그룹 단위
❌ "Splash 와 Login Start 둘 다 진입 화면이니 둘 다" → G-3 1순위 1개만
❌ "비기능 다양하니 그룹마다 화면당 1개씩" → 비기능 = 그룹 단위
❌ "각 화면마다 검증 필요" → 비기능 그룹 / 기능 화면

자기 점검 통과한 TC 만 출력
```

### 📊 효과 예측

| 개선 | 기대 효과 |
|------|----------|
| G-0 그룹 정의 | AI 가 그룹 vs 화면 헷갈림 해소 — "Login Options 와 Login Complete 가 다른 화면이니 각각" 같은 실수 감소 |
| G-3 의미 기반 | 사용자 임의 prefix / 분기 표기 (007A/B/C) 도 정확히 처리 |
| G-7 협력 관계 | AI 가 부담 없이 따르되 안일해지지 않음 |
| G-8 자기 점검 | 매 호출 마지막에 AI 가 자기 출력 검증 — Self-correction 효과 |

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-agent/common/tc-rules.md` | G-0 신설 (그룹 정의), G-3 교체 (의미 기반 우선순위), G-7 신설 (협력 관계), G-8 신설 (자기 점검 가이드) |
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.23 |
| `CHANGELOG.md` | v0.9.23 섹션 추가 |

---

## v0.9.22 — 2026-04-29 (중복 알림 + 자동 통합 — 양 단계)

> **요약**: 사용자 통찰 — "이미 끝난 작업인데 다음 작업에 참고하라는 안내는 논리 오류". 같은 작업 안에서 정리되도록 양 단계(Step 3 + Step 5) 자동 통합 기능 추가.

### 🐛 사용자 보고 (논리 오류 지적)

> "이미 작성이 끝난 케이스들인데, 다음 작업들은 새로운 케이스들일텐데... 분석 결과 복사를 다음 작업 때 써야 하는 게 맞는 거야?"

이전 v0.9.17~21 의 워크플로우는 결과 화면에서 "다음 작업에 참고" 라고 안내. 그러나 다음 작업은 다른 입력/분류표 → 무관. 즉시 정리 방법 부재.

사용자 결정:
> "분류표 확인 작업에서 중복 알림 및 통합이 있어야 하고, 또한 tc 생성 결과물에서도 중복 알림 및 통합이 되어야 한다고 봐."

### ✨ 신규 — 양 단계 중복 알림 + 자동 통합

| 단계 | 시점 | 잡는 중복 | 통합 방식 |
|------|------|---------|----------|
| **Stage 1** | Step 3 (분류표 검토, TC 작성 전) | 분류표 휴리스틱 (그룹 크기 ≥5 / 동일 키워드 반복) | AI 가 분류표 재구성 — 비기능 소분류를 그룹 대표 화면 1개로 통합 |
| **Stage 2** | Step 5 (Excel 빌드 후) | 실제 TC ID 단위 패턴 (네트워크/타임아웃/로딩 등) | AI 가 통합 후보 TC 제거 + 대표 TC 비고에 [통합] 태그 → Excel 재빌드 |

### 🆕 Stage 1 — 분류표 단계 (Step 3)

#### `predict_classification_duplicates()` 신규 함수
- 휴리스틱 1: 같은 대분류 내 중분류 5개 이상 → 비기능 TC 반복 가능성
- 휴리스틱 2: 같은 대분류 내 여러 중분류에 동일 키워드 (로딩 시간/네트워크/타임아웃 등) 등장

#### `/merge-classification/<sid>` 신규 엔드포인트
- AI 가 분류표 재구성 — 그룹 대표 화면(entry 성격)에 비기능 소분류 통합
- 다른 중분류에선 비기능 소분류 제거 (또는 [통합] 표시)
- 중분류 자체는 보존 (사용자 명시 요청 아니면 함부로 통합 X)

#### Step 3 UI — 노란 알림 박스
- "⚠️ 중복 가능성 N개 그룹 발견 (Stage 1 — TC 작성 전)"
- 예측별 상세 (그룹/키워드/영향 중분류)
- **🔁 분류표 자동 정리** 버튼 (녹색) — 클릭 시 AI 호출 → Viewer 갱신
- **✕ 무시 (그대로 진행)** 버튼

### 🆕 Stage 2 — TC 결과 단계 (Step 5)

#### `/merge-tcs/<sid>` 신규 엔드포인트
- `tc_final.md` 로드 → AI 호출 → 통합 후보 TC 제거 + 대표 TC 에 [통합] 태그
- `step_build_excel()` 재호출 → 새 Excel 생성
- 원본 `tc_final.md` 복원 (재시도 가능하도록)
- 응답: `{filename, removed_count, new_total_tc, new_smoke_tc}`

#### Excel 파일명 정책
- 원본: `SPCY_TC_P_WebApp_20260429_v1.xlsx` (보존)
- 통합본: `SPCY_TC_P_WebApp_20260429_v1_merged.xlsx` (별도)
- 사용자가 비교 가능

#### Step 5 UI — 중복 알림 박스 단순화
**Before** (v0.9.21): 5단계 수동 워크플로우 가이드 + 복사 버튼
**After** (v0.9.22): 녹색 박스 + **🔁 자동 통합 + Excel 재생성** 메인 버튼 + 보조 복사 버튼

```
💡 지금 바로 정리하시겠어요?
아래 버튼을 누르면 AI 가 통합 후보 TC 들을 제거하고
새 Excel 을 만들어줍니다. 원본 Excel 은 보존됩니다 (_merged suffix).

[🔁 자동 통합 + Excel 재생성]  [📋 수동 — 분석 결과 복사]
```

#### 자동 통합 진행 + 결과 표시
- 클릭 → confirm (제거할 TC 수, 소요 시간 안내)
- 진행 중: 버튼 비활성화 + "⏳ 통합 중... (30~60초)"
- 완료: 결과 카드 갱신 (새 파일명/TC 수) + 알림 박스 녹색 ✅ 변경

### 🛡 안전장치
- **원본 보존**: 통합 후 별도 파일, 원본 그대로
- **AI 환상 위험 완화**: confirm 다이얼로그 + 결과 비교 가능
- **잘림 감지**: max_tokens 도달 시 통합 거부 + 사용자에게 수동 정리 안내
- **재시도 가능**: 원본 tc_final.md 항상 보존되어 재호출 가능

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.22, `predict_classification_duplicates()` 신규, `/merge-classification/<sid>` + `/merge-tcs/<sid>` 신규 엔드포인트, `step_gate` 가 prediction 도 SSE 로 전달, `renderClassifyDuplicateNotice` 프론트, `#classifyDuplicateNotice` HTML, `autoMergeClassification()` JS, `renderDuplicateNotice` 단순화 (녹색 박스 + 자동 통합 메인 버튼), `autoMergeTcs()` JS, `step_build_excel` 에 `_excel_filename_suffix` 지원 |
| `CHANGELOG.md` | v0.9.22 섹션 추가 |

---

## v0.9.21 — 2026-04-29 (중복 패턴 분석 — 명확한 사용 단계 가이드)

> **요약**: 사용자 보고 — "분석 결과 복사 버튼은 있는데, 정확히 어떤 단계에서 이 복사된 문구를 써야 할지 명시적으로 알려줘." 추상적 안내를 명시적 단계별 가이드로 개선.

### 🐛 사용자 보고

> "안내 문구에 따르면 '검토 후 다음 실행에서 더 명확한 분류표 / 화면 범위 지정으로 중복을 줄이세요.' 라고 가이드 하지만 정확히 어떤 단계에서 이 복사된 문구를 써야 할지 명시적으로 알려줘."

기존 안내가 너무 추상적이라 사용자가 워크플로우를 못 찾음.

### ✨ 개선

#### 1) UI — 단계별 사용 가이드 박스 추가

기존 한 줄 안내 → 시각적으로 구분된 두 가지 워크플로우:

**단계 2-A. 지금 바로 통합 (권장)** — 녹색 강조 박스
```
① 📋 분석 결과 복사 버튼 클릭
② "🔄 추가 TC 생성" 또는 "📝 범위만 변경하여 재시작" 클릭
③ Step 3 진입 → 하단 AI 도우미 채팅창에 Cmd+V
④ "위 분석에 따라 통합 후보 TC 들을 제거해줘" 추가 입력 → 전송
⑤ AI 가 분류표 정리 → 승인 → 새 Excel 생성
```

**단계 2-B. 다음 신규 작업 시 활용** — 회색 보조 박스
```
① 분석 결과 복사
② 신규 작업 → "TC 생성 범위" 입력란에 붙여넣기
   + "이 패턴들은 그룹당 1개 대표 화면에만 작성 (원칙 G)" 추가
```

#### 2) 클립보드 복사 텍스트 — AI 즉시 실행 가능한 명령형 포함

**Before**: 단순 분석 데이터만
```
# 중복 의심 패턴 분석 (원칙 G)
총 2개 패턴, 통합 시 약 1개 TC 감소 가능

## 3G/저사양 로딩 시간 — Onboarding (2개)
- 유지 권장: SM-LGC-008
- 통합 후보: SM-LGI-006
...
```

**After**: 사용 안내 + AI 가 즉시 실행 가능한 명령
```
# 중복 의심 패턴 통합 요청 (원칙 G)

> 사용 방법: 이 텍스트를 분류표 검토(Step 3) 의 하단 AI 도우미 채팅에 붙여넣고 전송하세요.
> AI 가 자동으로 통합 후보 TC 들을 제거하고 대표 화면에만 1개로 통합합니다.

---

## 분석 요약
- 총 2개 중복 패턴 발견
- 통합 시 약 1개 TC 감소 가능

## 통합 지시

아래 패턴별로 **통합 후보 TC 들을 분류표에서 제거**해줘.
**유지 권장 TC** 는 그대로 두고, 그 TC 의 비고에 '[통합]...' 태그를 추가해줘.

### 1. 3G/저사양 로딩 시간 (Onboarding)
- ✅ 유지: `SM-LGC-008`
- ❌ 제거: `SM-LGI-006`
...

---

**스펙 표에 명시된 에러 케이스는 보존**하고, 위 비기능 패턴만 통합해줘.
```

→ 사용자가 이 텍스트를 그대로 Cmd+V 하면 AI 가 즉시 작업 가능.

#### 3) 토스트 메시지 강화

**Before**: "📋 분석 결과가 클립보드에 복사되었습니다"
**After**: "📋 복사 완료 — Step 3 의 AI 도우미 채팅에 Cmd+V 후 전송하세요"

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.21, `renderDuplicateNotice` 가이드 박스 추가 (단계 2-A 녹색 / 2-B 회색), `copyDuplicateReportToClipboard` 복사 텍스트에 사용법 + 명령형 포함, 토스트 메시지 강화 |
| `CHANGELOG.md` | v0.9.21 섹션 추가 |

---

## v0.9.20 — 2026-04-29 (Gate 채팅 신뢰성 — 명령형 적극 수용 + 변경 안내)

> **요약**: 사용자 보고 — "splash 케이스 삭제 요청 → AI가 '질문 모호'라며 거부 → 그러나 시스템은 '✅ 업데이트되었습니다' 라고 거짓 안내". 3중 fix.

### 🐛 사용자 보고

> "대화창에서 splash 케이스 삭제를 요청했고, ai 가 삭제했다고 했는데. 분류표에 그대로 보이고 있어."

스크린샷 분석:
- 사용자: "splash 케이스 삭제"
- AI 응답: "질문이 완전하지 않은 것 같습니다. 어떤 수정을 원하시는지 구체적으로..."
- 그러나 시스템 메시지: "✅ 분류표가 업데이트되었습니다"
- 분류표는 변경 없음

### 🔍 원인 (3가지)

**1) System prompt 가 너무 보수적**:
- "수정 요청이 없거나 질문인 경우, 기존 문서 그대로" 가 너무 강함
- AI 가 짧은 명령형("splash 케이스 삭제") 도 "질문일 수도 있다" 며 거부

**2) max_tokens=4096**:
- 긴 분류표 (Splash, Login Options, Email Input 등 13개 중분류) 가 4096 토큰 초과
- 출력 잘림 → `[DOCUMENT]` 태그 미완성 → 파싱 시 기본값 (current_doc) 사용

**3) Frontend 메시지 분기 부재**:
- `d.ok` 만 보고 무조건 "✅ 업데이트되었습니다" 표시
- 실제 변경 여부와 무관 → 사용자에게 거짓 안내

### 🛡 해결 (3중 fix)

#### A. System prompt 강화

**Before**: "수정 요청이 없거나 질문인 경우 기존 문서 그대로"
**After**: 강한 적극 수용 가이드

```
1. 짧은 명령형 요청도 명확한 수정 의도로 해석:
   - "splash 케이스 삭제" → Splash 관련 모두 제거
   - "이메일 입력 빼줘" → Email Input 중분류 제거
   - "AUTH 도메인 3번 지워" → AUTH 의 3번째 항목 제거

2. 삭제 요청을 절대 거부하지 마세요. "X 삭제/제거/빼줘" 라고 하면 X 와 관련된 항목을 모두 찾아 제거.

3. 모호한 경우에도 일단 수정 시도, [REPLY] 에 어떤 해석을 했는지 명시.
   거부 대신: "Splash 관련 항목을 모두 제거했습니다. 다른 의도였으면 알려주세요."

4. 진짜 질문일 때만 그대로:
   - "Splash 가 뭐야?" — 질문 → 그대로
   - "splash 삭제" — 명령 → 반드시 수정
```

#### B. max_tokens 4096 → 16384 + 잘림 감지

```python
resp = client.messages.create(
    model=MODEL,
    max_tokens=16384,  # ← 4096 에서 증가
    ...
)
stop_reason = getattr(resp, "stop_reason", None)
if stop_reason == "max_tokens":
    truncated = True
    updated_doc = current_doc  # 잘린 문서로 덮어쓰기 방지 — 원본 유지
    reply_text = "⚠️ 응답이 너무 길어 잘렸습니다..."
```

#### C. Frontend 메시지 분기

응답에 `changed`, `truncated` 필드 추가. Frontend 가 이를 보고 정확한 메시지:

| 상황 | 메시지 |
|------|--------|
| `changed: true` | ✅ 분류표가 업데이트되었습니다. 아래 표에서 확인하세요. |
| `truncated: true` | ⚠️ AI 응답이 너무 길어 잘렸습니다. 분류표는 변경되지 않았어요. 더 작은 단위로 나눠 다시 요청해 주세요. |
| `changed: false` | ℹ️ 분류표가 변경되지 않았습니다. 요청이 모호했을 수 있어요. 더 명확하게 다시 요청해 주세요. (예: "Splash 중분류 삭제해줘") |

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.20, `gate_chat` system_prompt 적극 수용 모드, max_tokens 16384, 잘림 감지, `changed/truncated` 응답 필드, frontend 메시지 분기 |
| `CHANGELOG.md` | v0.9.20 섹션 추가 |

---

## v0.9.19 — 2026-04-29 (이어서 작업 시 화면 식별자 매핑 복원)

> **요약**: 사용자 보고 — "이어서 작업하기 눌렀더니 상단에 화면 코드가 없다는데 말이 안 된다." 진짜 원인: `_source_scr_map` 이 체크포인트에 저장 안 됐던 v0.9.13 누락 버그.

### 🐛 사용자 보고

> "이어서 작업하기 눌렀더니.. 상단에 화면 코드가 없다는데.. 이게 말이 안 되는 거 같아."

스크린샷:
- 노란 박스: `📌 화면 코드 안내 — 입력 소스에서 화면 식별자(SCR-NNN 형식)가 발견되지 않았습니다.`
- 그러나 사용자는 명백히 SCR-001 / SCR-013 등을 입력했음

### 🔍 원인

흐름:
1. 사용자가 SCR-013 등 입력 → `step_parse_sources` 가 `sess["_source_scr_map"]` 캡처 ✓
2. Gate 진입 → `save_pipeline_state(stage="gate_waiting", data=...)` 호출
3. **그러나 `data` 페이로드에 `source_scr_map` 이 빠져 있음** ❌
4. 서버 재시작 → `SESSIONS` 메모리 사라짐 (`_source_scr_map` 도 함께)
5. "이어서 작업" 클릭 → 체크포인트(disk)에서 복원
6. 체크포인트엔 `source_scr_map` 없음 → `sess["_source_scr_map"] = {}` 빈 dict
7. Gate UI 가 매핑 없는 상태로 떠서 노란 안내 박스 노출

이 누락은 v0.9.13 (화면 코드 입력 소스 기반 추출) 시점부터 잠재돼 있었음. 새 기능 추가했으나 체크포인트 직렬화에 포함 누락.

### 🛡 해결

**1) `save_pipeline_state` 5곳 모두 `source_scr_map` 포함**:
- `parsed` / `features` (정책 모드) / `gate_waiting` (정책 모드)
- `features` (Quick 모드) / `gate_waiting` (Quick 모드)

```python
save_pipeline_state(project_name, "gate_waiting", {
    "raw_text": ..., "policy_text": ..., "features_text": ...,
    "classification": ..., "focus_area": ..., "sources_info": ...,
    "source_scr_map": sess.get("_source_scr_map") or {},  # ← v0.9.19
})
```

**2) 복원 시 `_source_scr_map` 복구**:
- 체크포인트에 매핑 있으면 그대로 복원
- 없으면 `raw_text` 에서 SCR 패턴 자동 재추출 (옛 체크포인트 호환)
- 모두 실패 시 빈 dict (정상 — Excel 화면 코드 컬럼 빈 칸)

**3) 복원 로그 출력**:
- `[이어서] 화면 식별자 매핑 복원됨 (N개)` 또는
- `[이어서] 화면 식별자 자동 재추출 (N개) — 옛 체크포인트 보강` 또는
- `[이어서] 화면 식별자 매핑 없음 — Excel 화면 코드 컬럼 빈 칸 출력 (정상)`

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.19, `save_pipeline_state` 5곳에 `source_scr_map` 추가, resume 분기에 `_source_scr_map` 복원 + raw_text 재스캔 폴백 |
| `CHANGELOG.md` | v0.9.19 섹션 추가 |

---

## v0.9.18 — 2026-04-29 (Gate 검토 중 재시작 보호 + 안내 문구 정리)

> **요약**: 사용자가 분류표 검토 중 (gate_waiting 상태) 인데 서버 재시작으로 세션이 사라져 "승인 오류: 세션 없음" 404 발생 — 활성 세션 가드에 gate_waiting 누락이 원인.

### 🐛 사용자 보고

> "분류표 확인 후 tc 만들기 승인을 했는데, 이런 에러가 뜨네 — 승인 오류: 세션 없음"

네트워크 탭: `POST /approve/e0b0c532 → 404 NOT FOUND`

### 🔍 원인

`_ACTIVE_STATUSES` set 에 **`"gate_waiting"` 누락**:

```python
# Before (v0.9.17 이하)
_ACTIVE_STATUSES = {
    "parsing", "inventory", "classifying", "policy_features",
    "tc_writing", "reviewing", "building", "analyzing",
    # gate_waiting 빠짐!
}
```

→ 사용자가 분류표 검토 중(`gate_waiting`)인데 active 로 안 잡혀 → 서버 재시작 시 force 가드 미작동 → SESSIONS 메모리 dict 소실 → 승인 클릭 시 `SESSIONS.get(sid)` None → 404.

이 문제는 v0.9.8b (헤더 재시작 버튼) 도입 시점부터 잠재돼 있었음. 우리가 이번 세션에서 자기 재시작을 여러 번 하면서 표면화됨.

### 🛡 해결

**1) `_ACTIVE_STATUSES` 에 `gate_waiting` 추가**:
```python
_ACTIVE_STATUSES = {
    "parsing", "inventory", "classifying", "policy_features",
    "gate_waiting",  # ← v0.9.18 추가
    "tc_writing", "reviewing", "building", "analyzing",
}
```

이제 분류표 검토 중인 사용자가 있으면 헤더 `🔄 서버 재시작` 버튼 클릭 시 강한 경고 + force=1 필요. 의도치 않은 세션 끊김 방지.

**2) 친화적 에러 메시지** (`/approve`, `/gate-chat` 두 엔드포인트):
- Before: `세션 없음`
- After: `세션이 만료되었습니다. 서버가 재시작됐을 수 있어요.\n페이지를 새로고침하고 '이어서 작업'을 클릭하면 분류표 검토 단계부터 복원됩니다.`

### 📝 추가 — 안내 문구 정리

v0.9.11~12 에서 메인 채팅 패널이 미니/모달로 통합되면서 "우측 Viewer" 표현이 더 이상 맞지 않음. 4곳 모두 수정:

| Before | After |
|--------|-------|
| 채팅으로 수정을 요청하고, **우측 Viewer**에서 결과를 확인 | 하단 AI 도우미로 수정을 요청하고, **아래 표**에서 결과를 확인 |
| ✅ 분류표가 업데이트되었습니다. **우측 Viewer**에서 확인하세요 | ✅ 분류표가 업데이트되었습니다. **아래 표**에서 확인하세요 |

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.18, `_ACTIVE_STATUSES` 에 `gate_waiting` 추가, `/approve` + `/gate-chat` 친화적 에러 메시지, "우측 Viewer" 문구 4곳 → "아래 표" 등으로 정리 |
| `CHANGELOG.md` | v0.9.18 섹션 추가 |

---

## v0.9.17 — 2026-04-29 (원칙 G — 그룹 단위 에러 패턴 통합 + 중복 자동 탐지)

> **요약**: 동료 보고 — "같은 그룹 내 비기능 TC (네트워크/타임아웃/로딩 등) 가 화면마다 반복되어 중복이 많다." 분석: SCR-010, SCR-013 으로 시뮬레이션 → 6가지 패턴이 그룹 내 5개 화면에 반복 → 약 14개 중복 TC 발생. **예방(C) + 탐지(D) 동시 적용**.

### 🐛 사용자 보고

> "중분류, 소분류에서 케이스 작성할 때 에러/예외 케이스들을 추가해서 만들고 있는데, 중복되는 케이스들이 많다고 하네."

### 🔍 분석

SCR-010 + SCR-013 시뮬레이션 결과:

**스펙 명시 케이스** (보존 대상):
- SCR-010: "웹뷰 로드 실패 Modal"
- SCR-013: "권한 거부 Modal", "OAuth 토큰 수신 실패 Modal"

**AI 추가 비기능 케이스** (통합 대상 — 그룹당 1개):
| 패턴 | 같은 그룹 내 화면 수 |
|------|------------------|
| 네트워크 끊김 / 연결 실패 | 5개 (SCR-010, 011, 012, 013, 014) |
| 타임아웃 처리 | 5개 |
| 3G/저사양 로딩 시간 | 5개 |
| 백그라운드/포그라운드 | 5개 (가능) |
| 화면 회전 | 5개 (가능) |
| 메모리/강제 종료 | 5개 (가능) |

→ 한 그룹에서 **최대 30개 동일 패턴 TC** 가능. 통합하면 6개로.

### ✨ 변경 — 이중 안전망 (예방 + 탐지)

#### 🛡 옵션 C — 예방 (tc-rules.md 원칙 G + 프롬프트 강화)

**`tc-rules.md` 원칙 F 다음에 원칙 G 신설**:

- G-1: 명시 vs 추가 — 처리 기준 다름 (명시는 보존, AI 추가는 통합)
- G-2: 통합 대상 6가지 패턴 (네트워크, 타임아웃, 로딩 시간 등)
- G-3: 대표 화면 선택 기준 (entry 성격 우선)
- G-4: 통합 TC 작성 형식 (`[통합]` 비고 태그)
- G-5: ❌ 금지 예시
- G-6: ✅ 허용 예시 (스펙 명시는 화면별 보존)

**`build_tc_user_prompt` 에 `dedup_hint` 섹션 추가** — AI 에게 매 호출 시 한 번 더 강조.

#### 🛡 옵션 D — 탐지 (후처리 자동 감지)

**`detect_duplicate_error_tcs()` 함수 신설**:
- TC 마크다운에서 `### TC-ID — title` + 표의 `대분류` / `중분류` 추출
- 6가지 비기능 패턴 정규식으로 매칭
- 같은 (패턴, 대분류) 에 2개 이상이면 중복으로 보고
- 가장 작은 TC ID 를 대표 (entry 화면 추정), 나머지를 통합 후보로 분류
- 반환: `{patterns, total_duplicates, suggested_keep, suggested_remove}`

**파이프라인 hook**:
- `step_review` 직후 + Excel 빌드 직전에 실행
- SSE `duplicate_warning` 이벤트로 프론트에 전달

**프론트 UI** (결과 카드 card5 안):
- 노란 알림 박스 — `⚠️ 중복 의심 패턴 N개 발견`
- 패턴별 상세 (대분류, 유지 권장 TC, 통합 후보 TC, TC 목록)
- `📋 분석 결과 복사` 버튼 — 클립보드로 마크다운 복사 (다음 실행 시 활용)

### 📊 효과 예측

| 시나리오 | v0.9.16 이하 | v0.9.17 |
|---------|------------|---------|
| 같은 그룹 5개 화면에 "네트워크 끊김" TC | 5개 작성 | **1개 (옵션 C 예방)** 또는 5개+경고 (옵션 D 탐지) |
| 사용자가 중복 발견 시간 | 수동 검토 | **결과 화면에서 즉시 확인** |
| 통합 의사 결정 | 어려움 | 분석 결과 복사 → 다음 실행에 활용 |

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-agent/common/tc-rules.md` | 원칙 G 신설 (G-1 ~ G-6) — 그룹 단위 에러 패턴 통합 |
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.17, `build_tc_user_prompt` 에 `dedup_hint` 추가, `detect_duplicate_error_tcs` 함수 신설, `run_pipeline` 에서 Excel 빌드 전 탐지 + SSE push, 프론트 `duplicate_warning` 핸들러 + `renderDuplicateNotice` + `#duplicateNotice` 컨테이너 + 클립보드 복사 |
| `CHANGELOG.md` | v0.9.17 섹션 추가 |

---

## v0.9.16 — 2026-04-29 (수정 플로우에도 영향도 우선 원칙 적용)

> **요약**: v0.9.15 가 신규 TC 생성 플로우에 "분류표 우선 원칙" 을 적용했지만, 기존 TC 수정 플로우(`run_modify_pipeline`)는 별도 프롬프트라 적용 안 됨. 일관성 확보 fix.

### 🐛 사용자 질문

> "신규 tc 생성 뿐만 아니라 기존 TC 수정 기능에서도 위 내용이 적용 되는거지?"

확인 결과:
- ✅ 신규 TC 생성 (`run_pipeline` → `step_write_tc` → `build_tc_user_prompt`) — v0.9.15 적용됨
- ❌ 수정 플로우 메인 (`run_modify_pipeline` 의 `system_modify` 프롬프트) — 별도 프롬프트, 미적용

### ✨ 변경

**`run_modify_pipeline` 의 `system_modify` 프롬프트 강화**:

```
## 🎯 영향도 분석 우선 원칙 (절대 규칙 — 반드시 준수)

⚠️ 사용자가 검토·승인한 영향도 분석(approved_plan)이 최종 진실 소스입니다.

규칙:
1. approved_plan 에 명시된 변경(삭제/수정/추가)만 정확히 적용하세요.
2. approved_plan 에 없는 TC 는 변경하지 마세요 — 기존 그대로 유지.
3. 기존 TC 의 내용을 보고 영향이 있어 보여도, approved_plan 에 없으면 건드리지 마세요.
4. 임의로 추가 TC 를 생성하지 마세요 — 영향도의 "신규 추가" 항목만 추가.
5. approved_plan 의 지시가 모호하면 보수적으로 판단 (변경 최소화 우선).
```

**`user_modify` 섹션 헤더 강화**:
- "수정 지시사항 (사용자 승인 — 최종 진실 소스)"
- "기존 TC 전체 (참고용 — 승인된 수정 지시사항이 우선)"
- "수정 지시사항에 없는 TC는 그대로 유지 (임의 변경 금지)"

### 📐 효과

| 시나리오 | v0.9.15 | v0.9.16 |
|---------|---------|---------|
| 신규 TC 생성 — 분류표 수정 | ✅ 분류표 우선 | ✅ 변경 없음 |
| 기존 TC 수정 — 영향도 수정 | ⚠️ AI 환상 가능 | ✅ 영향도 우선 |
| 일관성 | 플로우별 다름 | **양쪽 동일한 신뢰성 기준** |

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.16, `run_modify_pipeline` 의 `system_modify` 에 영향도 우선 원칙 추가, `user_modify` 섹션 헤더 강화 |
| `CHANGELOG.md` | v0.9.16 섹션 추가 |

---

## v0.9.15 — 2026-04-29 (Gate 수정 사항 TC 미반영 버그 fix)

> **요약 (중대 버그 fix)**: Gate 채팅에서 분류표 수정 → Viewer 반영 → 그러나 최종 Excel 은 원본 기준 으로 생성되던 문제. 사용자 검토·승인이 무시되던 시스템 핵심 동작 fix.

### 🐛 사용자 보고 (중대)

> "SCR-013 입력 → 분류표 받음 → 체크박스 기능 제거 + 2개 항목 수정 요청 → Viewer 에서는 수정됨 → 그러나 Excel 은 원본대로 생성됨"

### 🔍 진짜 원인

데이터 흐름 분석:

```
1. 입력 소스 → policy_text + features_text 추출 (체크박스 정보 포함)
2. features_text → 분류표 (체크박스 항목 포함)
3. Gate 채팅: "체크박스 제거" → 분류표 만 수정됨
4. TC 작성:
   - approved_classification (수정됨 ✓)
   - features_text (원본 — 체크박스 그대로 ❌)
   - extract_section_from_raw(원본) ← _quick_mode/_section_extract 시 사용 ❌
5. AI 가 분류표 + 본문 모두 보고 판단
   → 본문이 풍부하니 본문 우선 → 체크박스 TC 다시 만듦
```

핵심: **분류표 수정 = "목차"만 바꿈, 본문 (features_text + 원본 raw) 은 그대로** → AI 가 본문 기준으로 환상 복원

### 🛡 해결 — 이중 fix

#### 옵션 C: TC 작성 프롬프트에 "분류표 우선 원칙" 절대 규칙 추가

`build_tc_user_prompt` 에 새 섹션 신설:

```
## 🎯 분류표 우선 원칙 (절대 규칙 — 반드시 준수)

⚠️ 사용자가 검토·승인한 분류표가 최종 진실 소스입니다.

규칙:
1. 분류표에 있는 중분류/소분류만 TC 로 작성하세요.
2. 본문(features_text, 정책)에 추가 기능이 보여도, 분류표에 없으면 TC 만들지 마세요.
3. 분류표 ⊃ 본문이 아닙니다. 본문이 더 자세할 수 있지만 분류표가 우선입니다.
4. 본문은 TC 상세 시나리오 작성을 위한 참고일 뿐.
5. 본문에는 있는데 분류표에는 없는 기능 = 사용자가 의도적으로 제외한 것 → TC 만들지 마세요.
```

또한 features/policy 섹션 헤더에 "참고용 — 분류표가 우선" 강조:
```
## 전체 기능 목록 (참고용 — 분류표가 우선)
⚠️ 아래 정보는 TC 상세 작성을 위한 참고입니다. 항목 포함 여부는 위 분류표 기준으로 결정.
```

#### 옵션 B: Gate 채팅이 분류표 수정 시 features/policy 자동 동기화

새 함수 `_sync_features_policy_with_classification()`:

1. Gate 채팅 응답이 분류표를 수정한 것을 감지 (`updated_doc != current_doc`)
2. 별도 AI 호출로 features/policy 도 분류표와 일관되게 갱신
3. 응답: `[POLICY] ... [FEATURES] ...` 형식 파싱하여 `sess["_policy_text"]`, `sess["_features_text"]` 갱신
4. 사용자에게 동기화 결과 안내 (✅ synced / ⚠️ failed)

`run_pipeline` 수정:
- Gate 진입 전: `sess["_features_text"]`, `sess["_policy_text"]` 에 초기값 저장
- Gate 후: 갱신된 값 (`synced_features`, `synced_policy`) 사용
- `step_review` 에도 동기화된 값 전달

### 📐 효과 예측

| 시나리오 | v0.9.14 이하 | v0.9.15 |
|---------|------------|---------|
| 사용자가 분류표만 수정 | ❌ TC 에 원본 기준 항목 포함 | ✅ 분류표 우선 (옵션 C) |
| Gate 채팅이 본문 동기화 성공 | N/A | ✅ 분류표 + 본문 일관 (옵션 B) |
| Gate 채팅 동기화 AI 호출 실패 | N/A | ⚠️ 분류표만 수정, 사용자 안내 메시지 (옵션 C 가 안전망) |

이중 안전망으로 거의 100% 케이스 해결.

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.15, `build_tc_user_prompt` 에 `classification_priority_hint` 섹션 추가 + features/policy 헤더에 "참고용 — 분류표가 우선" 추가, `gate_chat` 엔드포인트에 `_sync_features_policy_with_classification` 호출, 새 함수 신설, `run_pipeline` 에서 `_features_text`/`_policy_text` 세션 저장 + 갱신본 사용, 프론트 `sendGateChat` 에 sync_status 안내 메시지 |
| `CHANGELOG.md` | v0.9.15 섹션 추가 |

---

## v0.9.14 — 2026-04-29 (테스트 단계 / 예상 결과 마침표 종결 규칙)

> **요약**: 사용자 보고 — 기대결과 셀 안 문장 끝에 마침표가 빠져 있는 문제. tc-rules.md 에 명시적 규칙이 없던 것이 원인. 9-2 절 신설.

### 🐛 사용자 보고

> "결과 문서 검토하니, 기대결과 셀 안의 문장 끝에 마침표가 없네. 다른 곳은 있는데 이 쪽 관련해서 마침표를 제한했던 적이 없는데.. 처음부터 없었을 것으로 예상."

확인 결과 `tc-rules.md` 에 마침표 관련 규칙이 전혀 없었음. AI 가 기본 출력 스타일에 따라 마침표 누락이 종종 발생.

### ✨ 변경

**1) `tc-rules.md` 9-2 절 신설 — 테스트 단계 / 예상 결과 작성 규칙**

| 필드 | 형식 | 마침표 |
|------|------|--------|
| 사전 조건 | 명사형/상태형 종결 (`~인/된/한 상태`) | ❌ 불필요 |
| **테스트 단계** | **완전한 문장 (동사 종결)** | ✅ **필수** |
| **예상 결과** | **완전한 문장 (동사 종결)** | ✅ **필수** |
| 비고 | 자유 | 선택 |
| 분류 / 우선순위 등 단어 필드 | 단어/코드 | ❌ 불필요 |

✅ 올바른 예:
```
**예상 결과**
- Continue 버튼이 활성화된다.
- SCR-005 인증 코드 입력 화면으로 이동한다.
```

❌ 잘못된 예:
```
**예상 결과**
- Continue 버튼이 활성화된다     ← 마침표 누락
- SCR-005 화면으로 이동           ← 단어형 + 마침표 누락
```

**2) `build_tc_user_prompt` 에 마침표 안내 한 번 더 강조**

`tc-rules.md` 가 v0.9.10 부터 전체 전달되므로 9-2 규칙이 자동 적용되지만, 자주 누락되기 쉬운 부분이라 user prompt 에 별도 섹션으로 한 번 더 명시:

```
## ✍️ 문장 종결 규칙 (tc-rules.md 9-2 — 반드시 준수)
**테스트 단계** 와 **예상 결과** 의 **모든 항목은 마침표(`.`)로 끝**나야 합니다.
```

### 🛠 비변경 사항

- **사전 조건** 형식 변경 없음 — 기존 9-1 절 그대로 (`~인 상태` 등 명사형 종결, 마침표 X)
- **TC ID / 분류 / 우선순위 등 단어 필드** — 마침표 불필요 (구분 명확화)
- **TC 후처리 파싱** — 변경 불필요 (마침표 유무는 의미 추출에 영향 없음)

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-agent/common/tc-rules.md` | 9-2 절 신설 — 테스트 단계 / 예상 결과 작성 규칙 (마침표 필수) |
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.14, `build_tc_user_prompt` 에 `period_hint` 섹션 추가 (이중 안전망) |
| `CHANGELOG.md` | v0.9.14 섹션 추가 |

---

## v0.9.13 — 2026-04-27 (화면 코드 → 입력 소스 기반 추출)

> **요약**: 동료 보고 — "TC 와 화면 코드가 상이한 부분이 있다" 의 근본 fix. 화면 코드를 더 이상 AI 환각/자동 파생에 맡기지 않고 **입력 소스 파일에서 직접 추출**.

### 🐛 사용자 보고

> "내 동료가 몇 개 파일을 테스트 했는데, 테스트 케이스와 화면 코드가 상이한 부분들이 보인다고 해.."

코드 리뷰 결과 7개의 미스매치 경로 발견. 진짜 원인:
> AI 에게 화면 코드 매핑 테이블을 직접 주지 않고, 중분류명만 보고 알아서 3글자 코드를 만들라고 했다.

사용자 통찰:
> "테스트 케이스들의 내용은 모두 입력 소스에서 나오는 거니 화면 코드는 입력 소스 기반에서 정확히 뽑는 것이 맞아."

### ✨ 신규 동작

**1) 입력 소스 SCR 식별자 추출 (Phase 1)**

`step_parse_sources` 가 각 마크다운 입력 파일에서 화면 식별자를 추출하여 세션에 저장:

```python
sess["_source_scr_map"] = {filename: scr_id}
# 예: {"SCR-003.md": "SCR-003", "SCR-007A.md": "SCR-007A"}
```

추출 우선순위:
1. **파일명**: `SCR-\d+[A-Z]?` 패턴 (예: `SCR-003.md` → `SCR-003`, `SCR-007A.md` → `SCR-007A`)
2. **본문 H1 첫 줄**: `# SCR-003: Email Input` → `SCR-003`
3. **본문 첫 번째 등장**
4. 위 모두 실패 → **빈 문자열** (AI 환각/추측 금지)

**2) AI 프롬프트에 명시적 매핑 주입**

`build_tc_user_prompt` 에 새 파라미터 `source_scr_map` 추가. 매핑이 있으면 AI 에게 표 형식으로 명시:

```
## 📱 화면 코드 매핑 (입력 소스 기반 — 반드시 준수)

| 입력 소스 파일 | 화면 코드 |
|---|---|
| SCR-003.md | SCR-003 |
| SCR-005.md | SCR-005 |

⚠️ 규칙:
1. 각 TC 메타 테이블에 `| 연관 화면 | SCR-NNN |` 형식 정확히 사용
2. 화면명 없이 코드만 ("SCR-001" ✅, "Splash (SCR-001)" ❌)
3. **임의 코드 생성 금지**: 위 매핑 표에 없는 화면 코드(SCR-999, LGI 등) 절대 만들지 말 것
4. **출처 입력 소스에 화면 코드가 매핑돼 있지 않으면 `| 연관 화면 |  |` 빈 칸**
```

매핑이 비어있으면 "임의 코드 생성 금지 + 빈 칸 정책" 명시.

**3) Gate UI 안내 (Step 3 진입 시)**

`gate` SSE 이벤트에 `source_scr_map` 페이로드 추가. 프론트의 `renderSourceScrNotice()` 가 분류표 위에 안내 박스 노출:

- **매핑 발견됨** (녹색 박스): `📌 입력 소스 화면 코드 매핑 (N개)` + 파일별 매핑 나열
- **매핑 없음** (노란 박스): `📌 화면 코드 안내 — 입력 소스에서 SCR 식별자 미발견. Excel 의 화면 코드 컬럼은 빈 칸으로 출력됩니다 (정상).`

### 🛠 비변경 사항 (호환성)

- **TC ID 형식 변경 없음**: `SM-LG-001` 그대로 유지. `SM-SCR003-001` 같은 형식은 사용 안 함.
- **`resolve_screen_code` 함수 유지**: TC ID 의 SuiteCode 결정용으로만 사용 (화면 코드 컬럼과 분리)
- **`screen_code_map.md`**: TC ID SuiteCode 결정 용도로 계속 사용 가능 (옛 모드 호환)
- **`build_excel.py`**: 변경 불필요 — 이미 빈 화면 코드 처리 로직 보유 (`(화면 코드 없음)` 그룹 등)

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `extract_scr_from_source` 헬퍼 신설, `step_parse_sources` 에서 `_source_scr_map` 캡처, `build_tc_user_prompt` 에 `source_scr_map` 파라미터 + 매핑 섹션 주입, `step_gate` 가 SSE payload 에 매핑 포함, 프론트 `renderSourceScrNotice()` + `#sourceScrNotice` 컨테이너, `APP_VERSION` v0.9.13 |
| `CHANGELOG.md` | v0.9.13 섹션 추가 |

---

## v0.9.12 — 2026-04-27 (메인 채팅 정리 + 다국어 + 모달 리사이즈)

> **요약**: v0.9.11 의 미니 채팅 패널 후속 — 중복 UI 정리 + 다국어 + 사용자 모달 리사이즈.

### ✨ 변경

**1) 상단 메인 채팅 패널 시각적 제거**
- 미니 채팅 + 모달 만으로 충분 → 상단 메인 패널 (`💬 AI와 대화하여 수정`) 시각적으로 숨김
- DOM 은 유지 (`display:none`) — `sendGateChat()` / `addGateChatMsg()` 가 `#gateChatInput` / `#gateChatMessages` 직접 참조하므로 단일 진실 소스 보존
- 미니 채팅 가시성 로직도 단순화: viewport 기반 → Step 3 진입 시 항상 표시

**2) 다국어 Placeholder 자동 감지**

지원 언어 4개:

| 언어 | placeholder 예시 |
|------|----------------|
| 한국어 (ko) | 예) AUTH 도메인 케이스 3번 삭제해줘 — Enter로 전송, Shift+Enter 줄바꿈 |
| English (en) | e.g. Delete AUTH domain case #3 — Enter to send, Shift+Enter for newline |
| 日本語 (ja) | 例) AUTH ドメインのケース3を削除して — Enter で送信、Shift+Enter で改行 |
| 中文 (zh) | 例) 删除 AUTH 域名案例 #3 — Enter 发送, Shift+Enter 换行 |

- `navigator.language` 기반 자동 감지
- `localStorage.tc_ui_lang` 우선 (사용자 수동 설정)
- 콘솔에서 `setStickyAiLang('en')` 호출로 수동 변경 + 페이지 자동 새로고침
- 라벨, 힌트, 버튼 라벨, 모달 제목 등 모두 번역됨

**3) 모달 사용자 리사이즈**
- CSS `resize: both` 네이티브 — 우측 하단 모서리 드래그
- 시각 강화: 모달 우측 하단에 작은 줄무늬 표시
- 사용자가 드래그 → ResizeObserver 가 0.3초 후 자동으로 `localStorage.tc_modal_size` 저장
- 다음 모달 오픈 시 저장된 크기 자동 복원
- 최소 크기 360x320, 최대 96vh

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.12, 메인 채팅 패널 `display:none` 적용, IIFE 에 `I18N` 객체 + `detectLang()` + `setStickyAiLang()` + 모든 라벨/placeholder 다국어, 모달 리사이즈 CSS + ResizeObserver 영속 |
| `CHANGELOG.md` | v0.9.12 섹션 추가 |

---

## v0.9.11 — 2026-04-27 (Sticky AI → 미니 채팅 패널)

> **요약**: 하단 Sticky AI 입력바가 입력만 가능했던 한계 해소 — 미니 채팅 패널로 확장하여 응답도 하단에서 즉시 확인 가능.

### 🐛 사용자 보고

> "하단의 AI 도우미를 통해서 입력한 값에 대한 답변은 스크롤 해서 상단 입력 창에서 확인해야 해서 불편해."

이전엔 하단 sticky bar 에 입력하면 응답은 메인 채팅 패널 (card3 상단)에 추가되었음. 사용자가 표 검토하다가 응답 보려면 위로 스크롤해야 했음.

### ✨ 신규 기능

**3가지 상태의 미니 채팅 패널**:

| 상태 | 모습 | 트리거 |
|------|------|--------|
| **접힘 (collapsed)** — 기본 | 헤더(💬 AI 도우미 + 메시지 개수) + 입력 한 줄 (~64px) | 첫 진입, 또는 ▴ 클릭 |
| **펼침 (expanded)** | 헤더 + 메시지 영역(~220px) + 입력 (~340px 총) | 헤더 클릭, ▾ 클릭, 또는 메시지 전송 시 자동 |
| **모달 (full)** | 화면 중앙에 720x800 큰 채팅창 | ⛶ 크게 버튼 클릭 |

### 🎨 디테일

- **메시지 미러링**: 메인 `#gateChatMessages` 가 단일 진실 소스 — MutationObserver 로 변경 감지하여 mini + modal 양쪽 자동 동기화
- **메시지 개수 뱃지**: 헤더에 현재 메시지 수 표시 (📩 3 형태)
- **자동 스크롤**: 새 메시지 도착 시 자동으로 맨 아래로
- **자동 펼침**: 사용자가 메시지를 보내는 순간 접힘 → 펼침으로 자동 전환 (응답이 보이도록)
- **메시지 스타일**:
  - user: 틸 그라데이션 + 흰 텍스트 (오른쪽)
  - assistant: 흰 배경 + 진한 텍스트 (왼쪽)
  - system: 녹색 배경 + 작은 글씨 (가운데)
- **모달 단축키**: Esc 로 닫기 / 바깥 영역 클릭으로 닫기

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.11, `.floating-ai-bar` CSS 전면 재설계 (3가지 상태 + 모달 스타일 추가), IIFE 에서 미니 채팅 DOM 생성 + 모달 DOM + 메시지 미러링 로직(`syncMessages` + MutationObserver) + 모달 열기/닫기 + 단축키 |
| `CHANGELOG.md` | v0.9.11 섹션 추가 |

---

## v0.9.10 — 2026-04-27 (tc-rules.md 컷오프 제거 — TC 품질 개선)

> **요약**: 동료가 단일 화면(email)만 입력했더니 30~50개 자세한 TC가 나왔던 문제의 진짜 원인 — `tc-rules.md` 의 28%만 AI에게 전달되고 있었음. 컷오프 제거.

### 🐛 사용자 보고

> "동료가 입력 소스를 딱 login의 email 부분만 md 파일로 입력하고 tc를 뽑았더니 너무 자세하게 tc가 나왔대"

### 🔍 진짜 원인

`tc-rules.md` 파일 크기는 **28,540자** 인데, 프롬프트 코드에서 강제 컷오프:

```python
# Before
{tc_rules[:8000] if tc_rules else "..."}    # 신규 TC 작성 — 28%만 전달
{tc_rules[:4000] if tc_rules else ""}       # 수정 플로우 영향도 분석 — 14%만
{tc_rules[:4000] if tc_rules else ""}       # 수정 플로우 TC 적용 — 14%만
```

**8,000자 컷오프 위치**: 원칙 F (네비게이션) 중간

→ AI 에게 **전달되지 않던 핵심 규칙들**:

| 규칙 위치 | 내용 | 동료 케이스에 미친 영향 |
|---------|------|--------------------|
| line 198 | "Splash·Landing 같은 단순 화면에 10개 이상 TC 생성 금지" | ❌ 단일 화면이라 폭주 방지 못함 |
| line 334+ | TC 생성 카테고리 4가지 매트릭스 | ❌ 카테고리 비율 가이드 미전달 |
| line 348 | "카테고리 1 (UI/UX)는 화면당 1개의 'UI Spec Compliance' TC로 통합" | ❌ 디자인 TC 폭주 방지 못함 |
| 원칙 D 후반부 | Visual 속성 통합 상세 | ❌ 색상/폰트/간격 TC 분할 가능 |

### 🛡 해결 — 컷오프 제거 (3곳)

```python
# After
{tc_rules if tc_rules else "..."}    # 모든 호출처에서 전체 전달
```

수정 위치:
- **line 1551** — `step_write_tc` (신규 TC 작성, 가장 중요)
- **line 3526** — `run_modify_pipeline` 영향도 분석
- **line 3594** — `run_modify_pipeline` TC 수정 적용

### 📐 비용 / 효과

| 항목 | 영향 |
|------|------|
| 입력 토큰 증가 | ~5k 토큰 (Claude Opus 200k 컨텍스트의 2.5%) |
| 응답 시간 | 거의 동일 (입력 토큰은 출력 대비 매우 빠름) |
| 비용 | ~$0.075/호출 증가 (미미) |
| **TC 품질** | **단일 화면 폭주 방지 + Visual 통합 + 카테고리 균형** |

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.10, `tc_rules[:N]` 3곳 → `tc_rules` 전체 전달 |
| `CHANGELOG.md` | v0.9.10 섹션 추가 |

---

## v0.9.9 — 2026-04-27 (Excel 출력 옵션 — Full / Light / Custom)

> **요약**: Human Gate 승인 시 Excel 출력 시트를 사용자가 선택할 수 있게 — 중간 산출물(빠른 확인용) vs 정식 산출물(배포용) 시나리오 분리.

### ✨ 신규 기능

**🆕 Human Gate에 Excel 출력 옵션 패널 추가** — 승인 버튼 위에 표시:

```
⚙ Excel 출력 옵션
  ◉ 📦 Full Set    — 표지·통계·Smoke·Traceability·변경이력·TC 전체 (정식)
  ○ 🪶 Light       — TC 전체 목록만 (반복 작업용)
  ○ 🛠 Custom      — 시트별 직접 선택
```

**Custom 모드** 선택 시 6개 시트 체크박스 펼침:
- ☑ 📋 표지
- ☑ 📊 TC 통계
- ☑ 🔥 Smoke Test
- ☑ 🔗 Traceability Matrix
- ☑ 📌 TC 전체 목록 *(필수 — 항상 포함)*
- ☑ 🔄 변경 이력 *(수정 모드 전용 — 신규 모드에서는 자동 비활성화)*

실시간 요약 표시: `💡 요약: 표지 + Traceability + TC 목록 = 3개 시트`

### 🛠 동작 디테일

- **프리셋 ↔ Custom 전환**: 프리셋 클릭 시 체크박스 자동 동기화 (시각화)
- **체크박스 직접 변경 시**: 자동으로 Custom 모드로 전환
- **TC 전체 목록 보호**: 항상 ☑ 고정, disabled 처리 (회색)
- **컨텍스트 인식**: 신규 모드면 `🔄 변경 이력` 비활성화, 수정 모드면 활성화
- **localStorage 영속**:
  - 키 `tc_excel_preset` → 마지막 선택 프리셋 (full/light/custom)
  - 키 `tc_excel_custom_sheets` → Custom 체크 상태 JSON
  - 다음 Gate 진입 시 자동 복원

### 🔧 백엔드

- **`build_excel.py` `run_build()`**: `sheets: dict | None` 파라미터 신설
  - `None` 이면 Full Set (하위호환)
  - `tc_list` 키는 항상 True 강제 (안전)
  - 표지가 꺼져있을 때 첫 시트 자리 처리 위해 `_placeholder` 임시 시트 사용 후 제거
- **`/approve/<sid>`**: `excel_sheets` 페이로드 받아 `sess["_excel_sheets"]` 에 저장
- **`step_build_excel`**: `sess["_excel_sheets"]` 를 `run_build(sheets=...)` 로 전달

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-agent/scripts/build_excel.py` | `run_build()` 에 `sheets` 파라미터 추가 + 6개 시트 조건부 생성 + placeholder 처리 |
| `tc-ui/scripts/app_v2.py` | Excel 옵션 UI (HTML+CSS), JS 5개 함수(`onExcelPresetChange`, `onExcelSheetCheckChange`, `applySheetChecks`, `collectExcelSheets`, `updateExcelSheetSummary`, `getSelectedExcelSheets`, `restoreExcelOption`), `/approve` 에서 페이로드 수신, `step_build_excel` wiring, gate 이벤트에서 신규/수정 모드별 변경이력 체크박스 토글 |
| `CHANGELOG.md` | v0.9.9 섹션 추가 |

---

## v0.9.8g — 2026-04-27 (파이프라인 중단 후 갈 곳 명확화)

> **요약**: v0.9.8f 의 부작용 — 파이프라인 중단 후 card1 이 숨겨진 채로 남아 사용자가 다음 작업을 시작할 수 없던 문제 fix.

### 🐛 버그 (사용자 보고)

> "파이프라인 중단하고 다시 시작하려고 하니까.. card1 이 없어서 어디로 가야 할지 방향을 잃었어"

**증상** (스크린샷):
- 사용자가 Step 2 (분석 및 분류) 도중 `■ 파이프라인 중단` 클릭
- 로그에 `[중단] 사용자가 파이프라인을 중단했습니다.` 표시
- 화면에는 Step 2 카드만 보이고 어떤 액션 버튼도 없음
- v0.9.8f 부터 card1 이 숨겨져 있어 "처음부터 시작" 버튼도 접근 불가

### 🔍 원인

`stopped` SSE 이벤트 핸들러 (line 8175):
- 중단 배너에 "새 작업을 시작하려면 **위 버튼**을 눌러주세요" 안내
- 하지만 그 "위 버튼"이 있는 card1 이 v0.9.8f 부터 숨겨져 있음
- → 사용자가 갈 곳 없음 (막다른 길)

### 🛡 해결

1. **`stopped` 이벤트 시 card1 명시적 unhide** — 사용자가 입력 영역으로 돌아갈 수 있게
2. **중단 배너에 액션 버튼 직접 추가**:
   - **🏠 처음부터 시작** (primary): `restartFromScratch()` 호출 → card1 보임 + Step 1
   - **🔄 이어서 재시작** (secondary): `retryPipeline()` 호출 → 체크포인트에서 재개

```js
banner.innerHTML = '...' +
  '<button onclick="restartFromScratch()">🏠 처음부터 시작</button>' +
  '<button onclick="retryPipeline()">🔄 이어서 재시작</button>';
document.getElementById('card1').classList.remove('hidden');
```

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.8g, `stopped` 이벤트 핸들러에 액션 버튼 + card1 unhide |
| `CHANGELOG.md` | v0.9.8g 섹션 추가 |

---

## v0.9.8f — 2026-04-27 (card1 누수 fix — 단계 전환 시 입력 카드도 숨김)

> **요약**: card1(Step 1 입력 카드)이 모든 단계에서 visible 로 남아있던 누수 fix. v0.9.8e 의 stepBar3 가드와 함께 Sticky AI bar 노출 조건도 명확해짐.

### 🐛 버그 (사용자 보고)

**증상**: Step 3 진입 후 짧은 분류표(스크롤 불필요)에서도 위로 스크롤하면 Sticky AI bar 가 등장
- 화면을 자세히 보면 card1(입력 설정 + 마크다운 소스 + 파이프라인 시작) 이 card3 사이/위에 끼어 있음
- 사용자 시선이 card1 영역에 도달하면 메인 채팅창(card3 내부)은 viewport 밖 → Sticky bar 노출

### 🔍 진짜 원인

코드를 분석한 결과 **card1 은 어떤 위치에서도 명시적으로 hide 되지 않습니다**. 모든 카드 토글 코드가 `[card2, card3, card5]` 만 다루고 card1 은 항상 visible 유지.

7곳 누락 확인:
- `startPipeline` (line 7959) — 메인 시작
- `resumePipeline` (line 6753) — 이전 작업 이어가기
- `startModify` (line 7460) — 기존 TC 수정
- `restartModify` (line 9205) — 수정 재시작
- `regenerateClassification` (line 8929) — 분류표 재생성
- `approveGate` (line 9011) — Gate 승인
- SSE `gate` 이벤트 핸들러 (line 8115) — Step 3 진입
- SSE `done` 이벤트 핸들러 (line 8148) — 완료 진입

### 🛡 해결

**옵션 B (사용자 선택)**: 단계를 떠날 때 명시적으로 card1 hide, Step 1 복귀 시 명시적으로 card1 show.

- **card1 hide 추가 (7곳 + 1)**: 위 7개 + SSE `done` 핸들러 = 총 8곳에 `document.getElementById('card1').classList.add('hidden')` 추가
- **card1 show 추가 (4곳)**: Step 1 복귀 시점에 `document.getElementById('card1').classList.remove('hidden')` 추가
  - `onProjectDropdownChange` (line 6544) — 프로젝트 변경
  - 빈 프로젝트 변경 (line 6602)
  - `restartFromScratch` (line 6708) — 처음부터 재시작
  - `startNextIteration` (line 6716) — 다음 반복
  - 입력 변경 (line 7596) — 소스 등 입력 바뀌었을 때

### 📐 부수 효과 (긍정)

card1 이 정상적으로 숨겨지면서:
- 페이지 길이 정상화
- 메인 채팅창(`#gateChatInput`)이 viewport 안에 있을 확률 증가
- Sticky AI bar 가 정말 필요한 시점에만 노출 (긴 분류표 스크롤 시)

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.8f, 8곳 card1 hide 추가, 5곳 card1 show 추가 |
| `CHANGELOG.md` | v0.9.8f 섹션 추가 |

---

## v0.9.8e — 2026-04-27 (Sticky AI bar 누수 근본 fix)

> **요약**: v0.9.8c 에서 추가한 가드가 일부 케이스를 못 막던 문제 — 진짜 원인 파악 후 근본 fix.

### 🐛 버그 (사용자 보고)

**증상**: Step 1 입력 화면에 Sticky AI bar 가 노출됨
- 화면 상단: "이전 작업이 있습니다 — 분류표 검토 대기 단계까지 완료" 배너
- 사용자는 "이어서 작업" 클릭 안 한 상태에서 Step 1 만 보고 있음
- 하지만 Sticky bar 가 하단에 떠 있음

### 🔍 진짜 원인

이전 세션이 `gate_waiting` 단계까지 진행된 상태에서 페이지 reload 시:
1. 페이지가 다시 로드되어 Step 1 화면 (card1) 표시
2. **SSE 자동 재연결** 으로 backend 가 `gate_waiting` 이벤트 재전송
3. 클라이언트가 이를 받아 `card3.classList.remove('hidden')` 실행 (line 8115)
4. **card3 가 DOM 에서 unhidden 됨 → `:has(#card3.hidden)` 가드 무효화**
5. Sticky bar 의 `updateVisibility()` 가 card3 visible 로 판정 → 노출

핵심: **card3 가 DOM 에서 unhidden 되어도, 사용자가 실제 보는 화면(stepBar 의 active step)이 Step 3 가 아닐 수 있음** — 우리는 후자를 봐야 했음.

### 🛡 근본 해결

**조건 강화**: `card3.hidden 아님` AND `stepBar3.active` 둘 다 만족할 때만 노출

| 레벨 | 변경 |
|------|------|
| **CSS** | `body:has(#stepBar3:not(.active)) .floating-ai-bar { display: none !important; }` 추가 |
| **JS updateVisibility** | `stepBar3.classList.contains('active')` 체크 추가 → 1차 가드에서 차단 |
| **JS MutationObserver** | stepBar3 의 class 변경도 추가 감시 (SSE 재연결로 card3 만 unhidden 되는 케이스 잡기) |
| **안내 토스트** | `card3 visible AND stepBar3 active` 시점에만 노출 |

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.8e, CSS `:has(#stepBar3:not(.active))` 가드, `updateVisibility` 에 stepBar3Active 체크, stepBar3 MutationObserver 추가, 토스트 조건 보강 |
| `CHANGELOG.md` | v0.9.8e 섹션 추가 |

---

## v0.9.8d — 2026-04-27 (TC 분류 요약 — 소분류 종속 행 + 토글)

> **요약**: 분류 요약 표의 가독성 대폭 개선 — 소분류가 다른 셀보다 압도적으로 길어 시선이 분산되던 문제 해결.

### ✨ UI/UX 개선

**Before**: 한 행에 6컬럼이 모두 들어가는 평평한 표 구조

```
| 시트 | Suite | TC ID | 대분류 | 중분류 | 소분류 (긴 텍스트 5~7줄) |
| Auth | AUTH  | ...   | Auth   | Login  | • Google 로그인 진입... \n • 웹뷰 초기 로드... |
```

→ 소분류가 다른 셀보다 5~10배 긴 텍스트 → 사용자 시선 분산

**After (옵션 E + 토글)**: 메인 행(기본 정보) + 종속 행(소분류 상세) 분리

```
| 시트 | Suite | TC ID | 대분류 | 중분류  | 소분류 |
| Auth | AUTH  | ...   | Auth   | Login   | ▼ 5개  |   ← 메인 행 (한눈에 스캔)
+--------------------------------------------------+
|   ↳ 소분류 (5)                                   |   ← 종속 행 (옅은 배경)
|     • Google 로그인 진입: ...                    |
|     • 웹뷰 초기 로드: ...                        |
|     ...                                          |
+--------------------------------------------------+
```

### 🆕 기능 상세

- **메인 행**: 시트명 / SuiteCode / TC ID / 대분류 / 중분류 + 소분류 토글 셀 (`▼ N개`)
- **종속 행**: `<tr colspan="6">` 으로 폭 전체 사용 + 들여쓰기 + 옅은 배경 + `↳ 소분류 (N)` 헤더
- **개별 토글**: 메인 행의 `▼ N개` 셀 클릭 시 해당 그룹의 소분류 종속 행만 토글 (▼ ↔ ▶)
- **전체 토글**: 표 상단에 `▼ 전체 펼치기` / `▶ 전체 접기` 버튼
- **호버 강조**: 메인 행 위에 마우스 올리면 살짝 푸른 배경, 토글 셀은 더 진한 푸른색
- **기본 펼침**: 첫 진입 시 모든 종속 행이 펼쳐진 상태 (사용자가 직접 접을 수 있음)

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.8d 갱신, `renderGateViewer` 의 표 구조 재설계 (메인 행 + 종속 행), `toggleMinorRow` / `toggleAllMinors` JS 함수 신설, `.tc-summary-table` CSS 추가 |
| `CHANGELOG.md` | v0.9.8d 섹션 추가 |

---

## v0.9.8c — 2026-04-27 (Sticky AI 가시성 가드 + UX 개선)

> **요약**: v0.9.8 에 추가한 Sticky AI 입력바가 Step 1 입력 화면에서 잘못 노출되던 문제 수정 + 디자인 전면 개선.

### 🐛 버그 수정

- **Step 1 에서 Sticky AI bar 가 떠 있던 문제** — 사용자 보고: "분류표 하단으로 스크롤해서 나타나고, 다시 상단으로 올라가면 떠 있는 채로 안 사라짐"
  - **원인**: `getBoundingClientRect()` 가 hidden 부모(card3) 안에서 0/0 반환 + scroll 방향 전환 시 가시성 재판정이 부정확
  - **해결 (이중 안전망)**:
    1. **CSS `:has()` 가드** — `body:has(#card3.hidden) .floating-ai-bar { display: none !important }` 한 줄로 JS race 와 무관하게 표시 차단 (Safari 13+/Chrome 105+)
    2. **JS `rect.width===0 && rect.height===0` 명시 처리** — hidden 부모 안의 입력창은 명시적으로 hide

### 🎨 UI/UX 개선

| 요소 | Before | After |
|------|--------|-------|
| 배경 | 흰색 (`#FFFFFF`) | 네이비/틸 그라데이션 + backdrop-filter blur(8px) |
| 윗 테두리 | 2px solid blue | 3px solid teal (`#14B8A6`) |
| 그림자 | 약함 (`0 -4px 16px ... 0.10`) | 강조 (`0 -8px 24px ... 0.18`) |
| 첫 등장 | 즉시 display | slideUp 0.32s + 1회 펄스 (border 강조) |
| 라벨 | 작은 한 줄 텍스트 | 굵은 메인 + 작은 보조 ("표 검토 중에도 바로 요청하세요") |
| 입력창 | 평범 회색 보더 | 그림자 + focus 시 teal ring |
| 전송 버튼 | 단색 teal | 그라데이션 + hover lift |
| 토글 (▾) | 작은 회색 버튼 | 둥근 칩 (흰 텍스트, 반투명 배경) |
| 모바일 | 동일 | `<small>` 보조 텍스트 자동 숨김 |

### 💡 발견성(Discoverability) 향상

- **Step 3 첫 진입 시 안내 토스트** 1회 노출:
  ```
  💡 분류표를 스크롤하면 하단에 AI 입력바가 자동으로 떠요
  ```
- `localStorage` 키 `tc_sticky_ai_hint_v098c` 로 dismiss 기억
- 1.2초 지연 후 자동 노출 → 사용자가 화면 인지 후 자연스럽게 보임

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.8c 갱신, CSS `:has()` 가드 + 디자인 전면 개편, `updateVisibility()` 에 rect 0/0 가드 추가, MutationObserver 안에 첫 진입 토스트 |
| `CHANGELOG.md` | v0.9.8c 섹션 추가 |

---

## v0.9.8b — 2026-04-27 (헤더 서버 재시작 버튼)

> **요약**: 코드 변경 후 매번 터미널로 가서 Ctrl+C → 재실행하던 번거로움 해소. 헤더에서 클릭 한 번으로 서버 재시작 + 자동 새로고침.

### ✨ 신규 기능

- **헤더 우측 `🔄 서버 재시작` 버튼** — 코드 변경 사항을 즉시 반영해야 할 때 한 번에 처리.
  - 클릭 → confirm 다이얼로그 → 재시작 요청 전송 → 진행 오버레이 표시
  - 백엔드는 `os.execv(sys.executable, [sys.executable] + sys.argv)` 로 자기 자신 재실행
  - 프론트는 `/admin/status` 폴링으로 서버 살아남 감지 → 자동 `window.location.reload()`
  - 폴링 최대 30초 (그 이후엔 사용자에게 수동 새로고침 안내)

### 🛡 보안 / 안전장치

- **localhost 가드** — `request.remote_addr` 가 `127.0.0.1` / `::1` / `localhost` 가 아니면 403 반환. 같은 LAN의 다른 PC에서 재시작 호출 차단.
- **활성 세션 보호** — `parsing/inventory/classifying/policy_features/tc_writing/reviewing/building/analyzing` 상태인 세션이 1개 이상이면 기본 거부 (409 응답). 프론트에서 활성 세션 개수를 표시하고 사용자가 다시 한 번 confirm하면 `force=1` 으로 재요청.
- **응답 → 재시작 순서** — 응답을 먼저 보내고 1.2초 후 백그라운드 스레드에서 `os.execv` 호출. 클라이언트가 "재시작 시작됨" 응답을 정상 수신하도록 보장.

### 🆕 새 엔드포인트

| 경로 | 메서드 | 용도 |
|---|---|---|
| `/admin/status` | GET | 살아있음 확인 + 버전 + 활성 세션 수 (폴링용) |
| `/admin/restart` | POST | 서버 재시작 (localhost + 활성 세션 가드) |

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.8b 갱신, `_ACTIVE_STATUSES` 상수 + `_count_active_sessions` / `_is_localhost_request` 헬퍼, `/admin/status` + `/admin/restart` 엔드포인트, 헤더에 `btn-restart-server` 버튼 + `restartOverlay` HTML, `restartServer()` + `pollServerAlive()` JS, `window._INITIAL_APP_VERSION` 노출 |
| `CHANGELOG.md` | v0.9.8b 섹션 추가 |

---

## v0.9.8a — 2026-04-27 (TC 분류 요약 접기 기능 추가)

> **요약**: v0.9.8 직후 합류 — 분류 검토 화면에서 TC 분류 요약 카드 자체를 접기/펼치기 가능하도록 개선

### ✨ UI/UX 개선

- **TC 분류 요약 접기/펼치기** — 분류 요약 카드 헤더(`▼ TC 분류 요약 (클릭하여 접기)`)를 클릭하면 표 본문 전체가 접힘. 다시 클릭하면 펼쳐짐. 기존 `📄 분류표 원본 마크다운 보기` 토글과 **동일한 `<details>` 패턴**으로 시각적 일관성 유지.
  - 기본값: **펼친 상태(`open`)** — 첫 진입 시 바로 보임
  - 검토 완료 후 접으면 AI 채팅 영역만 집중 가능
  - 헤더 우측의 `🤖 시스템 규칙 자동 적용` 토글은 `event.stopPropagation()`으로 details 토글과 분리 — 체크박스 클릭이 접힘/펼침으로 오작동하지 않음
  - Safari/WebKit 기본 `▶` 마커는 CSS `::-webkit-details-marker { display:none }` 로 제거하고 직접 그린 `▼/▶` 아이콘으로 통일

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.8a 갱신, `renderGateViewer` 의 분류 요약 카드를 `<details id="tcSummaryDetails" open>` 으로 래핑, 글로벌 toggle 핸들러에 TC 요약 분기 추가, Safari 마커 제거 CSS |
| `CHANGELOG.md` | v0.9.8a 섹션 추가 |

---

## v0.9.8 — 2026-04-27 (입력 소스 일괄 삭제 + Sticky AI 입력바)

> **요약**: 다중 입력 소스 정리 편의성 개선 + 분류 검토 화면 스크롤 UX 대폭 향상

### ✨ UI/UX 개선

- **입력 소스 전체 삭제** — Step 1의 입력 소스 영역에 `🗑 전체 삭제` 버튼 신설. 소스가 **2개 이상**일 때만 노출되어 평소엔 보이지 않음. 클릭 시 개수를 표시한 confirm 다이얼로그로 안전성 확보.
  - 5개 PDF·MD·URL을 새로 시작하기 위해 일일이 ✕ 누르던 번거로움 해소
  - 1개일 때는 노출되지 않으므로 실수 방지

- **Sticky Floating AI 입력바** — Step 3 분류 검토 화면에서 분류 요약 표가 길어 스크롤이 필요할 때, 화면 하단에 떠 있는 AI 수정 요청 입력바 자동 노출. 표를 끝까지 스크롤한 상태에서도 상단으로 돌아가지 않고 즉시 수정 요청 가능.
  - **자동 토글**: 메인 채팅 입력창이 화면에 보이면 숨김, 화면 밖으로 나가면 자동 노출
  - **최소화 토글**: `▾` 버튼으로 입력바 최소화 가능 (방해되지 않게)
  - **Enter 전송 / Shift+Enter 줄바꿈** — 메인 입력창과 동일한 단축키
  - 메인 채팅과 동일한 `sendGateChat()` 흐름을 재사용 — 히스토리·문서 업데이트 등 모든 동작 일관 유지

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` v0.9.8 갱신, `btn-clear-sources` CSS + `clearAllSources()` JS, `floating-ai-bar` CSS + 동적 DOM 삽입 + scroll/resize/MutationObserver 기반 가시성 제어 |
| `CHANGELOG.md` | v0.9.8 섹션 추가 |

---

## v0.9.7c — 2026-04-27 (소분류 중복 차별화 + 버전 SSOT)

> **요약**: 같은 화면에서 동일 소분류가 여러 번 등장할 때 자동 차별화 + 버전 정보 단일 소스화

### ✨ 신규 기능

- **소분류 자동 차별화 (`disambiguate_duplicate_minors`)** — 같은 `(대분류, 중분류, 소분류)` 그룹에 TC가 2개 이상일 때, 각 TC의 `title`에서 차별화 키워드를 추출하여 `소분류 — 키워드` 형태로 자동 부여. 테스터가 TC ID 대신 소분류 이름으로 케이스를 구분할 때 가독성 대폭 향상.
  - 예시: `Splash 화면 진입` × 4개 → `Splash 화면 진입 — UI 요소 표시`, `— Get Started 버튼 탭`, `— 뒤로가기 동작`, `— 로딩 시간`
  - 그룹 TC 1개일 땐 변형하지 않음 (불필요한 노이즈 회피)
  - 한국어 조사/접속어 자동 정리 (`시 키보드 표시` → `키보드 표시`)

- **TC 작성 프롬프트 강화 (예방)** — "같은 중분류 안에서 소분류 이름이 동일하면 안 됨"을 명시. 사후 처리 + 사전 예방의 이중 방어.

- **MD ↔ Excel 일관성 유지** — 후처리는 `step_build_excel` 진입 직후 `tc_content` 자체를 갱신. `tc_final.md` / `tc_files/{project}.md` / Excel 모두 동일한 변형본 사용 → 「기존 TC 수정」 플로우 재실행 시에도 문제 없음.

### 🛠 유지보수성 개선 (SSOT)

- **버전 단일 소스화** — `APP_VERSION`, `APP_VERSION_DATE`, `APP_VERSION_TAGLINE`, `APP_VERSION_HIGHLIGHTS` 4개 상수만 수정하면:
  - UI 헤더 배지 → 자동 반영
  - 첫 방문 What's New 배너 → 자동 반영
  - 자세히 보기 모달 → 자동 반영
  - localStorage dismiss 키 (`_WHATS_NEW_VERSION`) → 자동 반영 (새 배너 자동 노출)
- 이전에는 5곳 수동 업데이트 → 이제 **1곳만** 수정. 동료가 git pull 받은 뒤 옛 버전을 보는 문제 재발 방지.

### 🐛 버그 수정

- 동료 PC에서 git pull 후에도 UI 배지가 옛 버전으로 보이던 문제 — 위 SSOT 도입으로 근본 해결.

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | `APP_VERSION` 상수 도입 + Jinja 변수 주입, `disambiguate_duplicate_minors` + 헬퍼 함수, 후처리 호출 (3곳), TC 작성 프롬프트 강화 |
| `CHANGELOG.md` | v0.9.7c 섹션 추가 + 유지보수 메모 |

---

## v0.9.7b — 2026-04-27 (UI/UX 정비 + 다수 버그 수정)

> **요약**: Gate 화면 통합, 파이프라인 카드 통합, ScreenCode 규칙 개선, 컬럼 순서 재배치, `**SM` 잔여 버그 등 다수 수정

### ✨ UI/UX 개선

- **Gate 화면 통합** — 문서 Viewer + TC 분류 요약을 하나의 표 중심 영역으로 통합. 원본 마크다운은 `<details>` 토글로 선택 노출.
- **파이프라인 카드 통합** — 기존 `card2 + card4` 중복 노출 → `card2` 하나로 통합. 단계 진행 시 제목/배지 동적 전환.
- **Substep 시인성 강화** — 4개 → 6개로 확장 (파싱 → 정책·기능 → 분류 → 검토 → TC 생성 → Excel). 진행 중(파란 펄스 + 테두리), 완료(초록 + ✓ 체크), 대기(회색 테두리)로 3가지 상태 명확화.
- **분류 요약 표 — A안 중분류별 행 분리**. 같은 대분류 그룹은 첫 행에만 시트명/SuiteCode 입력, 이후 `↳ 동일 시트` 표기. 각 중분류의 고유 TC ID 미리보기 표시.
- **Excel 컬럼 순서 재배치** — `TC ID | 대분류 | 중분류 | 소분류 | 사전조건 | 테스트 스텝 | 기대결과 | 중요도 | 대상 거래소 | Smoke | 화면 코드`.
- **컬럼명 명확화** — `우선순위` → `중요도`, `거래소`/`관련 거래소` → `대상 거래소`, `사전 조건` → `사전조건`, `스텝` → `테스트 스텝`, `기대 결과` → `기대결과`. (KEY_MAP에 구 컬럼명 모두 유지 — 하위 호환)
- **표지/통계 시트 라벨 명확화** — `도메인별 구성` → `화면별 TC 수`. 동적으로 `ScreenCode · 중분류 이름` 형태로 표시 → 중복 표기(`EML · EML`) 해결.
- **결과 카드 라벨** — `최소 TC (≈35%)` → `🔥 Smoke TC` (실제 Smoke 개수 표시).
- **상태 컬럼/변경 이력 시트 제외** — 신규 TC 생성 플로우에서는 출력하지 않음. 「기존 TC 수정」 플로우(`/update-tc`)에서만 추가.
- **마크다운 폴더 업로드** (v0.9.7a 기능 보강) — 폴더 선택 후 `.md/.markdown/.txt` 자동 필터, 파일명 정렬, 50개 초과 시 confirm 경고.

### 🐛 버그 수정

- **`**SM · **SM` 잔여 마크업 버그** — AI가 `### **SM-VCD-003 — 제목**` 형태로 라인 전체를 bold로 감쌀 때 parser가 매칭 실패하여 ID에 `**` 흡수. `**` 마크업 제거 후 통일 매칭 + 안전장치로 근본 해결.
- **ScreenCode 충돌** — 같은 prefix (Google ...)로 시작하는 중분류들이 모두 `GOO`로 줄어들어 `GOO/GOO2/GOO3` 의미 없는 접미사 발생. 단어별 앞 2자 + 충돌 시 마지막 단어 1자씩 확장 (예: `GOWE`, `GOLOC`, `GOOAS`, `GOOAC` → 충돌 시 `GOOACO`)으로 해결.
- **SSE 세션 소멸 시 무한 재연결** — 서버 재시작 등으로 세션 사라지면 `⚠️ SSE 연결 오류. 재연결 시도...` 무한 반복. HEAD 요청으로 404 감지 후 명확한 안내 배너 + `🔄 새로고침` 버튼 제공.
- **대분류 체크리스트 제거** — 동작하지 않던 "TC 생성 범위 선택" 영역 + 전체 선택/해제 버튼 삭제. 범위 지정은 Step 1의 `focus_area` textarea로 일원화.
- **`#### 소분류` 헤더 데이터 누락** — 헤더 자체("소분류")가 데이터로 들어가서 모든 행에 "소분류, 소분류" 반복. 헤더는 마커로만 사용하고 실제 데이터는 그 아래 불릿에서만 수집.
- **소분류 40자 제한** — `txt.length < 40` 길이 제한 + `curMinors.length === 0` 단일 항목 제한 모두 제거. 모든 불릿 수집.
- **`extractCategorySummary` 첫 불릿만 수집 버그** — Variant B의 두 번째 소분류가 누락되던 문제 해결.
- **카운트다운 미표시** — 정책·기능 통합 추출 등 일부 단계에 `eta_sec` 누락 + 프론트가 `pct` 정확 매칭에 의존하던 문제. 라벨 텍스트 기반 폴백 도입.
- **TC 통계 시트 중복 섹션** — `─ 중분류별 ─` 와 `─ 도메인별 ─` 가 같은 정보 → 화면별 TC 수 하나로 통합.

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | Gate 통합, 파이프라인 카드 통합, ScreenCode 규칙, 표 A안, SSE 재연결, 카운트다운, 다수 버그 수정 |
| `tc-agent/scripts/build_excel.py` | parser 강화 (`**` 변형 5종 모두 지원), 컬럼 순서/명 재배치, `_tc_list_columns(include_change_columns)` 플래그, 통계 시트 라벨 정비 |
| `CHANGELOG.md` | v0.9.7b 섹션 추가 |

### 💡 참고

- v0.9.7/7a의 모든 기능 그대로 유지 (Windows 호환성, 마크다운 다중·폴더 업로드)
- v0.9.6의 핵심 기능 (기획서 diff 기반 TC 갱신, Traceability, Quick 모드)도 모두 동작
- 실행 방법 변경 없음

---

## v0.9.7a — 2026-04-24 (마크다운 다중·폴더 업로드)

> **요약**: 쪽대본 묶음 업로드 지원. 파일 여러 개 또는 폴더 통째로 선택 가능. Windows 호환성 수정(v0.9.7) 포함.

### ✨ 신규 기능

- **📄 다중 파일 업로드**: 「마크다운 파일 추가」 카드에서 여러 .md 파일을 한 번에 선택 가능 (Ctrl/Cmd 다중 선택 또는 Shift 범위 선택)
- **📁 폴더 선택 업로드** (신규 버튼): md 카드에 "폴더 선택" 버튼 추가
  - `webkitdirectory` 활용, 네이티브 폴더 선택창
  - 내부 `.md / .markdown / .txt`만 자동 필터 (숨김 파일 제외)
  - **파일명 순 자동 정렬** (쪽대본 01_ → 02_ 순서 보존)
  - **50개 초과 시 confirm 경고** — 대규모 실수 방지
- **중복 파일명 자동 보존**: 같은 이름의 파일을 연속 업로드하면 서버가 `_1`, `_2` 자동 접미사 부여 (덮어쓰기 방지)
- **소스 자동 분할**: 업로드한 파일마다 독립된 md 소스 카드로 자동 생성 → 개별 삭제·관리 가능

### 🔒 안전 / 보안
- 파일명에서 경로 조작 문자 제거 (`<>:"/\|?*`)
- 확장자 화이트리스트: `.md / .markdown / .txt`만 허용
- webkitRelativePath 경로 분리자 제거 (폴더 업로드 시 서버 측 하위폴더 접근 방지)

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | 프론트: `<input webkitdirectory>` + 폴더 선택 버튼 + `onMdFolderChange` 추가 · 서버: `/upload-md` 중복 파일명 접미사 처리 |

### 🧪 테스트 현황 (투명 공개)
- ✅ Python 구문 검사 · 서버 기동 검증
- ✅ 서버 API 중복 파일명 접미사 동작 (3회 업로드 → `_1`/`_2` 확인)
- ✅ UI 렌더 (`webkitdirectory` 속성, 폴더 선택 버튼 노출)
- ⏳ 브라우저에서 실제 폴더 선택 E2E 테스트는 사용자 확인 예정

### 💡 포함되는 이전 버전 수정
- v0.9.7의 Windows cp949 인코딩 / Excel 빌더 모듈화 등 모두 포함

---

## v0.9.7 — 2026-04-23 (Windows 호환성 패치)

> **요약**: Windows 환경에서 Excel 빌드가 fallback으로 빠져 **대분류별 시트 분할·Smoke Test 시트가 누락**되던 문제 해결. Excel 빌더를 모듈 import 방식으로 전환.

### 🐛 버그 수정 (Windows PC 환경)

- **Excel 대분류별 시트 분할 누락 & 🔥 Smoke Test 시트 누락**
  - 원인: Windows 기본 콘솔 인코딩(cp949)에서 `subprocess.run(text=True)`가 이모지(🔥) 디코드 실패 → `UnicodeDecodeError` → fallback 경로 진입
  - fallback은 `TC 전체목록` 한 시트에 모든 TC를 몰아 넣고 Smoke Test 시트도 생성 안 함 → 결과적으로 동료 Windows 환경에서만 Excel 구조 붕괴
  - **해결**: `build_excel.py`의 로직을 `run_build()` 함수로 추출 + `app_v2.py`가 subprocess 대신 **모듈 import로 직접 호출**. cp949 경로 자체를 제거.

- **cp949 인코딩 오류 추가 방어**
  - `build_excel.py` 시작부에 `sys.stdout/stderr.reconfigure(encoding="utf-8", errors="replace")` 추가
  - subprocess 폴백 경로에도 `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1` 환경변수 주입
  - stdout/stderr를 bytes로 받아 `errors='replace'`로 수동 디코드

- **fallback에도 🔥 Smoke Test 시트 생성 추가**
  - 모든 폴백 경로가 실패해서 내부 간이 빌더를 쓰더라도 Smoke Test는 보장

### ✨ 구조 개선

- **Excel 빌더 모듈화**: `build_excel.py`의 `main()` → `run_build(phase, tc_path, output_dir, verbose)` 함수로 분리
- **3단계 폴백 체인**:
  1. **모듈 import** → `run_build()` 호출 (기본 · Windows 호환)
  2. subprocess 호출 (모듈 import 실패 시)
  3. 내부 간이 빌더 (최후 수단 · 시트 분할/Traceability 없음)
- **속도 향상**: 모듈 호출 경로는 subprocess 생성 오버헤드 제거 (~1초 절감)

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-agent/scripts/build_excel.py` | `run_build()` 함수 추출, stdout/stderr UTF-8 강제 |
| `tc-ui/scripts/app_v2.py` | `step_build_excel` 모듈 import 우선 + 3단계 폴백, fallback에 Smoke 시트 추가 |

### 💡 동료 Windows PC 환경 확인 방법

`git pull` 후 재실행 → Excel 빌드 후 시트 목록에 다음이 모두 있어야 정상:
```
📋 표지 / 📊 TC 통계 / 🔥 Smoke Test / 🔗 Traceability / 📑 대분류명 (N개)
```
Flask 터미널 로그에 `[빌드] 모듈 호출 성공 — 총 N TC / Smoke M / 대분류 K시트` 메시지가 나오면 1순위 경로가 정상 동작 중입니다.

---

## v0.9.6 — 2026-04-23

> **요약**: 「기존 TC 수정」 탭 전면 개편 (기획서 diff 기반), 파이프라인 최적화, SCR Traceability, 다수 버그 수정

### ✨ 신규 기능

#### 1. 「기존 TC 수정」 탭 전면 개편 — 기획서 변경 기반 TC 갱신
기존의 "변경사항을 텍스트로 설명" 방식에서 **두 기획서 파일을 비교**하는 방식으로 전환.

- **3-슬롯 입력 UI**: 이전 기획서 · 새 기획서 · 기존 TC 파일 (모두 드래그앤드롭)
- **프로젝트 선택 없이 단발성 작업 가능** — 쪽대본 방식 지원
- **구조 기반 diff**: 기획서를 `SCR-001`, `SCREEN-xxx`, `PAGE-xxx` 단위로 분할 후 신규/수정/삭제/유지 자동 분류
- **GitHub 스타일 unified diff 뷰어**: +/- 라인 하이라이트로 무엇이 바뀌었는지 한눈에
- **체크박스 선택**: 각 변경 항목을 개별 승인 가능, 섹션별 + 전체 "전체 선택/해제"
- **TC ID 유지한 채 AI로 재작성**: 수정 사유 자동 추출
- **기존 TC 파일 지원**: 우리가 생성한 MD / Excel 역파싱 (외부 Spreadsheet는 추후 지원)
- **자동 스냅샷**: 갱신 전 `tc_history/{project}/snapshot_{timestamp}.md`에 백업 저장

#### 2. SCR Traceability — 화면 ↔ TC 양방향 추적성
- **"화면 코드" 컬럼 추가** (TC ID 바로 옆): 각 TC가 검증하는 SCR/SCREEN/PAGE 코드 기록
- **`🔗 Traceability` 시트 신규**: 화면 코드별 TC 개수 · Smoke 개수 · TC ID 목록 역참조
- AI가 중분류 이름 주변에서 화면 코드를 자동 탐지하여 TC 메타에 삽입

#### 3. 파이프라인 생성 모드 선택 UI
- Step 1 입력 설정에 **생성 모드 라디오** 추가
  - **정책 반영 모드 (기본)**: policy·features·분류 3단계 분석 (대용량 문서 적합)
  - **Quick 모드**: 원문을 직접 분류 (200KB 이하 권장, 정확도↑)
- 소스 크기 실시간 표시 + 200KB 초과 시 Quick 자동 비활성

#### 4. 파이프라인 효율 최적화
- **정책 반영 모드**: policy + features 2회 호출 → **1회 통합 호출** (토큰 ~40% 감소)
- **Quick 모드 3단계 재설계**: 인벤토리 → 분류 → 섹션 발췌 TC (누락 방지 구조)
- **TC 작성 시 원문 섹션 발췌**: 중분류당 컨텍스트 44KB → 6KB (**~87% 감소**)
- **Review 단계 누락 보강**: 분류표 vs 초안 비교하여 빠진 중분류의 TC 자동 추가 생성

#### 5. Excel 출력 구조 개선
- **대분류별 시트 분할**: `🧪 TC 전체목록` 제거 → `📑 대분류명` 시트 N개로 분리 (가독성↑)
- **컬럼 재배치** (팀원 의견 반영): `Smoke | TC ID | 화면 코드 | 우선순위 | 거래소 | 대분류 | 중분류 | 소분류 | 사전조건 | 스텝 | 기대결과`
- **변경 이력 컬럼/시트**: 상태(🆕/🔄/🗑️/빈값) + 수정 사유 컬럼 + `🔄 변경 이력` 시트
- **상태별 행 배경색**: 🆕신규(연초록) / 🔄수정(연노랑) / 🗑️Deprecated(회색)
- **TC ID 기반 중복 제거 dedup** 최종 방어선 내장

#### 6. UX 개선
- 📊 결과 화면: "최소 TC" → **"🔥 Smoke TC"** 라벨 교체 (실제 Smoke 개수 표시)
- 진행도 stage 세분화: 82→88→92→98→100 + 서버 전송 `eta_sec` 기반 정확한 카운트다운
- 파이프라인 stop 버튼, 재개(resume) 로직 개선

### 🐛 버그 수정

- **TC 카운트 웹/Excel 불일치**: 웹 102개 vs Excel 81개 → 유니크 TC ID 기반으로 통일
- **ScreenCode 충돌**: 같은 ScreenCode(예: CON)를 여러 중분류가 공유해 TC ID 21개 손실되던 문제 → `CON / CON2 / CON3 ...` 자동 접미사로 회피
- **프로젝트 빈 이름 유령 레코드**: 드롭다운에 삭제된 프로젝트가 `[진행 중]`으로 남는 현상 → 3중 방어 (저장 차단 + 로드 필터 + 렌더 필터)
- **Review 누락 보강 중복 생성**: 마크다운 테이블 형식 TC를 인식 못해 이미 있는 TC를 재생성 → 테이블 패턴까지 인식하도록 파서 강화
- **fetch_web_page TLS 검증 비활성**: `verify=False` 하드코딩 → 기본 활성, `TC_WEB_INSECURE=1` env로만 명시적 opt-out

### 🔐 안전 / 호환성

- **Windows PC 호환성 강화**: `.env` 로더 `utf-8-sig` BOM 처리, 따옴표 자동 제거, `시작하기_v2_Windows.bat` 단순화
- **Excel 빌드 하위 호환**: 상태/수정사유 필드 없는 기존 TC 파일도 정상 처리

### 📁 파일 변경

| 파일 | 용도 |
|---|---|
| `tc-ui/scripts/app_v2.py` | Flask + SSE 웹앱 메인 (신규 엔드포인트 3개, 함수 15개+ 추가) |
| `tc-agent/scripts/build_excel.py` | Excel 빌더 (컬럼 재정의, Traceability / 변경 이력 시트) |
| `tc-ui/시작하기_v2_Windows.bat` | Windows 실행 스크립트 단순화 |
| `tc-ui/.gitignore` | `tc_history/` 제외 추가 |
| `CHANGELOG.md` | 이 파일 (신규) |
| `tc-agent/projects/supercycl/` | 프로젝트별 규칙 파일 추가 |

### 🆕 신규 API 엔드포인트

- `POST /upload-existing-tc` — MD/xlsx 업로드 (TC 개수 미리보기)
- `POST /analyze-diff` — 3-슬롯 분석 → 변경사항 리포트 반환
- `POST /update-tc` — 승인된 변경사항 기반 TC 갱신 실행

### 💻 개발자를 위한 참고

**실행 방법 (변경 없음)**:
```bash
# macOS
./시작하기_v2.command
# Windows
시작하기_v2_Windows.bat
```

**테스트 권장 시나리오**:
1. 「새 TC 생성」 탭에서 Quick 모드로 작은 기획서 처리 → 새 Excel 구조 확인 (📑 대분류별 시트, 🔗 Traceability)
2. 「기존 TC 수정」 탭에서 이전/새 기획서 + 기존 TC MD 업로드 → unified diff 뷰어 + 체크박스 승인 흐름
3. Excel 열어서 `🔄 변경 이력` 시트 확인

**알려진 제약**:
- 기존 TC 파일의 외부 Google Spreadsheet 직접 입력은 미지원 (MD/Excel만)
- SCR 코드가 전혀 없는 기획서는 구조 diff 불가 (화면 코드 체계 필요)

---

## v0.9.5 — 2026-04-21 (이전 릴리즈)

- TC ID 이중 하이픈 버그 수정 (`SC-GNB--006` → `SC-GNB-006`)
- TC 수량 조정
- TC 카테고리 비율 강화 및 Few-shot Negative/Edge 예시 추가
- Human Gate SuiteCode 입력 UX 개선
- 프로젝트 전환 초기화
