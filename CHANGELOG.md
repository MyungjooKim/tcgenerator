# TC 자동화 도구 — 변경 이력 (Release Notes)

릴리즈 간 주요 변경사항을 기록합니다. 동료가 `git pull` 받은 후 이 파일을 먼저 읽으면 변경 내용을 빠르게 파악할 수 있습니다.

> **유지보수 메모 — 버전 업데이트 시**
> `tc-ui/scripts/app_v2.py` 상단의 `APP_VERSION`, `APP_VERSION_DATE`, `APP_VERSION_TAGLINE`,
> `APP_VERSION_HIGHLIGHTS` 4개 상수만 수정하면 UI 배지·What's New 배너·모달·JS 상수가 모두 자동 반영됩니다.
> 추가로 이 `CHANGELOG.md`에 새 섹션을 추가하고 `git tag -a vX.Y.Z` 만 진행하면 끝입니다.

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
