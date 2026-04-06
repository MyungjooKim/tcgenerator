# TC 초안 — MOBL / SETG / ROUT 도메인 (F-064~F-086)

> 작성 일시: 2026-04-02
> 적용 규칙: common/tc-rules.md + phase2-mobile/tc-rules-override.md
> 담당 기능: F-064~F-086 (23개) + ROUT 도메인 (F-006, F-007)
> 작성 TC 수: 40개

---

## [MOBL] Testnet UI 및 CEX 연동 안내 (F-064~F-068)

---

### MOBL-TNBN-001 — LandingPage "TESTNET MODE" 배너 상시 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 모바일 브라우저에서 `/` (LandingPage)에 접속한 상태이다

**테스트 단계**
1. LandingPage 화면 전체를 확인한다
2. 화면 하단에 "TESTNET MODE" 배너가 표시되는지 확인한다

**예상 결과**
- "TESTNET MODE" 배너가 화면 하단에 표시된다
- 다른 UI 요소와 겹치지 않고 상시 노출된다

---

### MOBL-TNBN-002 — 다른 탭 이동 후에도 "TESTNET MODE" 배너 유지 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage), /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. `/trade` 화면에서 "TESTNET MODE" 배너 노출 여부를 확인한다
2. BottomNav에서 Signal 탭으로 이동한다
3. Signal 화면에서 배너 노출 여부를 확인한다
4. Settings 탭으로 이동한다
5. Settings 화면에서 배너 노출 여부를 확인한다

**예상 결과**
- 탭 이동과 관계없이 "TESTNET MODE" 배너가 모든 화면에서 상시 노출된다

---

### MOBL-EXCH-001 — SettingsPage Exchange Connection 섹션 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- BottomNav에서 Settings 탭을 탭하여 SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage를 스크롤하여 Exchange Connection 섹션을 찾는다
2. Hyperliquid 테스트넷 연결 상태가 표시되는지 확인한다

**예상 결과**
- Exchange Connection 섹션이 표시된다
- Hyperliquid 테스트넷 연결 상태가 표시된다

---

### MOBL-ONCD-001 — 온보딩 완료 화면 CEX 안내 문구 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- 약관 동의가 완료된 상태이다
- `/onboarding` 페이지에서 3단계가 모두 완료된 상태이다

**테스트 단계**
1. 온보딩 완료 화면이 표시되는지 확인한다
2. CEX 통합 예정 안내 문구가 화면에 표시되는지 확인한다

**예상 결과**
- 온보딩 완료 화면에 CEX 통합 예정 안내 문구가 표시된다

**비고**
- [미결] CEX 안내 문구 포함 여부 및 정확한 문구 미확정 — 정책 확정 후 문구 검증 필요

---

### MOBL-TNBG-001 — TESTNET 배지 및 "실제 자금이 아님" 고지 문구 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. `/trade` 화면에서 TESTNET 배지를 찾는다
2. "실제 자금이 아님" 또는 이에 상응하는 고지 문구가 표시되는지 확인한다

**예상 결과**
- TESTNET 배지가 화면에 표시된다
- "실제 자금이 아님" 고지 문구가 표시된다

---

### MOBL-HLAP-001 — HL Testnet API 엔드포인트 연동 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | 공통 |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에서 주문 또는 잔고 조회 동작을 수행할 수 있는 상태이다

**테스트 단계**
1. `/trade` 화면에서 잔고 정보가 표시되는지 확인한다
2. BTC/USDC 코인을 선택하고 시세 정보가 표시되는지 확인한다

**예상 결과**
- 잔고 및 시세 정보가 정상적으로 표시된다 (Testnet 데이터 기준)
- 메인넷 데이터와 혼용되지 않는다

**비고**
- [신규] 코드 근거: HL Testnet API `api.hyperliquid-testnet.xyz`, Chain ID 998 연동 여부 (화면 동작 기준 검증)
- [개발 확인] 실제 API 호출 엔드포인트 및 Chain ID 998 연동 여부 확인 필요

---

## [MOBL] 모바일 반응형 UI (F-069~F-079)

---

### ★ MOBL-LAYT-001 — 전체 앱 최대 너비 320px 모바일 레이아웃 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (전체 화면) |

**사전 조건**
- 모바일 브라우저(iOS Safari 또는 Android Chrome)에서 앱에 접속한 상태이다
- 뷰포트 375px 기준 환경이다

**테스트 단계**
1. LandingPage(`/`)에서 화면 레이아웃을 확인한다
2. `/login` 페이지에서 레이아웃을 확인한다
3. `/trade` 페이지에서 레이아웃을 확인한다

**예상 결과**
- 전체 앱이 최대 너비 320px 이내로 표시되며 가로 스크롤이 발생하지 않는다
- 화면 높이가 100dvh로 표시되어 브라우저 주소창 상하 여백 없이 전체를 채운다

---

### ★ MOBL-ORDF-001 — Order Form 모바일 터치 인터랙션 정상 동작 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면의 Order Form이 표시된 상태이다

**테스트 단계**
1. 주문 타입 선택 버튼(Market/Limit/Conditional)을 손가락으로 탭한다
2. 수량 슬라이더를 손가락으로 드래그하여 조정한다
3. Long/Short 버튼을 손가락으로 탭한다

**예상 결과**
- 주문 타입 버튼 탭 시 선택 상태가 즉각 변경된다
- 슬라이더 드래그 시 수량이 실시간으로 조정된다
- Long/Short 버튼 탭 시 OrderConfirm 모달이 표시된다

---

### MOBL-ORDF-002 — Order Form 모바일 터치 슬라이더 경계값 입력 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면의 Order Form이 표시된 상태이다

**테스트 단계**
1. 수량 슬라이더를 0% 위치(최소)로 드래그한다
2. Long 버튼을 탭하여 주문 시도를 확인한다

**예상 결과**
- 수량 0% 상태에서 주문 버튼이 비활성화되거나 오류 메시지가 표시된다
- 0% 상태에서 주문이 실행되지 않는다

---

### ★ MOBL-DASH-001 — Dashboard 모바일 터치 인터랙션 정상 동작 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- 하나 이상의 포지션이 보유된 상태이다
- Dashboard 탭이 표시된 상태이다

**테스트 단계**
1. Positions 탭을 탭한다
2. 포지션 목록이 표시되는지 확인한다
3. 포지션 카드를 위아래로 스크롤한다

**예상 결과**
- Positions 탭 탭 시 포지션 목록이 표시된다
- 포지션 목록 스크롤이 부드럽게 동작한다

---

### ★ MOBL-CHRT-001 — Chart 컴포넌트 모바일 레이아웃 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. `/trade` 화면에서 Chart 컴포넌트가 표시되는지 확인한다
2. Chart 컴포넌트가 320px 너비 내에 잘린 부분 없이 표시되는지 확인한다

**예상 결과**
- Chart 컴포넌트가 모바일 화면 너비에 맞게 표시된다
- 가로 스크롤이 발생하지 않는다

---

### ★ MOBL-COIN-001 — Coin Info Bar 모바일 레이아웃 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. `/trade` 화면 상단의 Coin Info Bar를 확인한다
2. 코인명, 현재가 등의 정보가 화면 너비 내에 표시되는지 확인한다

**예상 결과**
- Coin Info Bar가 모바일 화면 너비에 맞게 표시된다
- 코인 정보가 잘리거나 겹치지 않고 표시된다

---

### ★ MOBL-BNAV-001 — BottomNav 4탭 고정 하단 네비게이션 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. 화면 하단에 BottomNav가 표시되는지 확인한다
2. trade, signal, portfolio, settings 4개 탭이 표시되는지 확인한다
3. 각 탭을 순서대로 탭하여 이동이 되는지 확인한다

**예상 결과**
- BottomNav가 화면 하단에 고정되어 표시된다
- trade, signal, portfolio, settings 4개 탭이 표시된다
- 각 탭 탭 시 해당 화면으로 이동된다

---

### MOBL-BNAV-002 — 탭 이동 시 BottomNav 고정 상태 유지 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. 탭 콘텐츠 영역을 위아래로 스크롤한다
2. 스크롤 중 BottomNav 위치를 확인한다

**예상 결과**
- 콘텐츠 스크롤 시 BottomNav가 화면 하단에 고정된 채로 유지된다
- BottomNav가 스크롤에 따라 움직이지 않는다

---

### ★ MOBL-SCRL-001 — 탭 콘텐츠 스크롤 및 하단 64px 여백 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. 탭 콘텐츠 영역을 최하단까지 스크롤한다
2. 콘텐츠 최하단이 BottomNav에 가려지지 않는지 확인한다

**예상 결과**
- 탭 콘텐츠 영역이 스크롤 가능하다
- 콘텐츠 최하단이 BottomNav와 겹치지 않고 64px 이상의 여백이 확보된다

---

### MOBL-DKTH-001 — 다크 테마 배경색 #0a0a0a 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (전체 화면) |

**사전 조건**
- 모바일 브라우저에서 앱에 접속한 상태이다

**테스트 단계**
1. LandingPage(`/`)에서 화면 배경색을 확인한다
2. `/trade` 화면에서 배경색을 확인한다

**예상 결과**
- 전체 앱의 배경색이 짙은 다크(#0a0a0a에 상응하는 어두운 배경) 테마로 표시된다
- 흰 배경이나 밝은 배경이 표시되지 않는다

---

### MOBL-CSSV-001 — CSS 변수 색상 시스템 정상 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- 수익 포지션과 손실 포지션이 각 1개 이상 존재하는 상태이다

**테스트 단계**
1. Dashboard 탭에서 포지션 목록을 확인한다
2. 수익(PnL ≥ 0) 포지션의 색상을 확인한다
3. 손실(PnL < 0) 포지션의 색상을 확인한다

**예상 결과**
- 수익 포지션의 PnL이 녹색(`--accent-green`)으로 표시된다
- 손실 포지션의 PnL이 빨간색(`--accent-red`)으로 표시된다

---

### MOBL-LDFN-001 — LandingPage 페이드인 애니메이션 순차 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 모바일 브라우저에서 `/` (LandingPage)에 처음 접속하는 상태이다

**테스트 단계**
1. LandingPage에 접속한다
2. 화면 요소들이 순차적으로 나타나는지 확인한다

**예상 결과**
- LandingPage의 UI 요소들이 순차적으로 페이드인되어 표시된다
- 모든 요소가 한번에 표시되지 않고 시차를 두고 나타난다

---

### MOBL-LGFN-001 — LoginPage 페이드인 애니메이션 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login |

**사전 조건**
- 모바일 브라우저에서 `/login` 페이지에 접속한 상태이다

**테스트 단계**
1. LoginPage에 접속한다
2. 화면 요소가 페이드인되어 나타나는지 확인한다

**예상 결과**
- LoginPage의 UI 요소가 페이드인 애니메이션으로 표시된다

---

## [SETG] 설정 (F-080~F-086)

---

### SETG-ACCT-001 — Account 섹션 이메일 및 지갑 주소 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- BottomNav에서 Settings 탭을 탭하여 SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage에서 Account 섹션을 확인한다
2. 이메일 주소가 표시되는지 확인한다
3. 지갑 주소가 표시되는지 확인한다

**예상 결과**
- Account 섹션에 가입 시 사용한 이메일 주소가 표시된다
- 온보딩에서 생성된 지갑 주소가 표시된다

---

### SETG-WCPY-001 — 지갑 주소 복사 버튼 동작 및 Toast 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage의 Account 섹션에서 지갑 주소가 표시된 상태이다

**테스트 단계**
1. 지갑 주소 옆의 복사 버튼을 탭한다
2. 화면에 Toast 메시지가 표시되는지 확인한다

**예상 결과**
- 복사 버튼 탭 시 "Address copied!" Toast 메시지가 화면에 표시된다
- Toast 메시지가 일정 시간 후 사라진다

---

### ★ SETG-TPSL-001 — Trading Preferences Auto TP/SL 설정값 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage에서 Trading Preferences 섹션을 확인한다
2. Auto TP/SL 설정값(TP%, SL%)이 표시되는지 확인한다
3. Edit 버튼이 표시되는지 확인한다

**예상 결과**
- Trading Preferences 섹션에 현재 TP% 및 SL% 값이 표시된다
- Edit 버튼이 표시된다

---

### SETG-TPSL-002 — Edit 버튼 탭 시 AutoTpSlModal 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage의 Trading Preferences 섹션에서 Edit 버튼이 표시된 상태이다

**테스트 단계**
1. Trading Preferences 섹션의 Auto TP/SL Edit 버튼을 탭한다
2. AutoTpSlModal이 표시되는지 확인한다

**예상 결과**
- Edit 버튼 탭 시 AutoTpSlModal이 표시된다
- 모달에 TP% 및 SL% 입력 필드가 표시된다

---

### ★ SETG-TGTG-001 — Auto TP/SL 토글 스위치 ON/OFF 상태 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage의 Trading Preferences 섹션이 표시된 상태이다

**테스트 단계**
1. Auto TP/SL 토글 스위치의 현재 상태를 확인한다
2. 토글 스위치를 탭한다
3. 토글 상태가 변경되는지 확인한다
4. 다시 토글 스위치를 탭한다
5. 토글 상태가 원래대로 되돌아오는지 확인한다

**예상 결과**
- 토글 ON 상태일 때 녹색으로 표시된다
- 토글 OFF 상태일 때 기본 배경색으로 표시된다
- 탭할 때마다 ON/OFF 상태가 즉각 전환된다

---

### SETG-TGTG-002 — Auto TP/SL 토글 OFF 시 OrderForm 인디케이터 미표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭), /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage에서 Auto TP/SL 토글이 OFF 상태이다

**테스트 단계**
1. SettingsPage에서 Auto TP/SL 토글을 OFF로 설정한다
2. BottomNav에서 trade 탭을 탭하여 TradingPage로 이동한다
3. Order Form에 TP%/SL% 인디케이터가 표시되는지 확인한다

**예상 결과**
- Auto TP/SL 토글이 OFF 상태일 때 Order Form에 TP%/SL% 인디케이터가 표시되지 않는다

---

### SETG-EXCO-001 — Exchange Connection 섹션 테스트넷 연결 상태 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage를 스크롤하여 Exchange Connection 섹션을 찾는다
2. Hyperliquid 테스트넷 연결 상태를 확인한다

**예상 결과**
- Exchange Connection 섹션에 Hyperliquid 테스트넷 연결 상태가 표시된다

---

### SETG-LOUT-001 — Logout 버튼 탭 시 Toast 메시지 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage에서 Logout 버튼을 찾는다
2. Logout 버튼의 외형(빨간색 테두리)을 확인한다
3. Logout 버튼을 탭한다
4. Toast 메시지가 표시되는지 확인한다

**예상 결과**
- Logout 버튼이 빨간색 테두리로 표시된다
- Logout 버튼 탭 시 목업 Toast 메시지가 표시된다

---

### SETG-LOUT-002 — Logout 버튼 탭 후 실제 세션 종료 미발생 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage에서 Logout 버튼을 탭한다
2. Toast 메시지가 표시되는지 확인한다
3. Toast 메시지가 사라진 후 현재 화면 상태를 확인한다

**예상 결과**
- Logout 버튼 탭 후 Toast 메시지가 표시된다
- 실제 로그아웃이 발생하지 않는다 (SettingsPage가 그대로 표시된다)
- 로그인 페이지로 이동하지 않는다

**비고**
- [신규] 코드 근거: F-085 명세 — 실제 세션 종료 없음 (목업 Toast 처리)

---

### SETG-COCH-001 — Coach Mark 단계별 가이드 최초 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 후 최초로 `/trade`에 접속한 상태이다
- Coach Mark를 한 번도 본 적 없는 계정이다

**테스트 단계**
1. 온보딩 완료 후 `Start Trading` 버튼을 탭하여 TradingPage에 진입한다
2. 화면에 Coach Mark 가이드가 표시되는지 확인한다

**예상 결과**
- 단계별 Coach Mark 및 기능 하이라이트가 표시된다

**비고**
- [미결] Coach Mark 세부 내용 및 화면별 가이드 포인트 미정 — 정책 확정 후 단계별 문구 검증 필요 (P2, 미구현 가능)

---

## [ROUT] 라우팅 및 접근 제어 (F-006, F-007 기반)

---

### ★ ROUT-AUTH-001 — 미인증 사용자 /trade 직접 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 비로그인 상태이다 (인증 토큰 없음)

**테스트 단계**
1. 브라우저에서 `/trade` URL에 직접 접속한다

**예상 결과**
- `/trade` 페이지가 표시되지 않는다
- `/` (LandingPage) 또는 `/login` 페이지로 리다이렉트된다

---

### ★ ROUT-AUTH-002 — 미인증 사용자 /onboarding 직접 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- 비로그인 상태이다 (인증 토큰 없음)

**테스트 단계**
1. 브라우저에서 `/onboarding` URL에 직접 접속한다

**예상 결과**
- `/onboarding` 페이지가 표시되지 않는다
- `/` (LandingPage) 또는 `/login` 페이지로 리다이렉트된다

---

### ★ ROUT-AUTH-003 — 미인증 사용자 /terms 직접 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
- 비로그인 상태이다 (인증 토큰 없음)

**테스트 단계**
1. 브라우저에서 `/terms` URL에 직접 접속한다

**예상 결과**
- `/terms` 페이지가 표시되지 않는다
- `/` (LandingPage) 또는 `/login` 페이지로 리다이렉트된다

---

### ★ ROUT-ONBD-001 — 약관 미동의 상태에서 /onboarding 직접 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- Google OAuth 로그인은 완료된 상태이다
- 약관 미동의 상태이다 (`hasAcceptedTerms = false`)

**테스트 단계**
1. 브라우저에서 `/onboarding` URL에 직접 접속한다

**예상 결과**
- `/onboarding` 페이지가 표시되지 않는다
- `/terms` 페이지로 리다이렉트된다

---

### ★ ROUT-TRAD-001 — 온보딩 미완료 상태에서 /trade 직접 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- Google OAuth 로그인이 완료된 상태이다
- 약관 동의는 완료되었으나 온보딩이 미완료된 상태이다 (`hasCompletedOnboarding = false`)

**테스트 단계**
1. 브라우저에서 `/trade` URL에 직접 접속한다

**예상 결과**
- `/trade` 페이지가 표시되지 않는다
- `/onboarding` 페이지로 리다이렉트된다

---

### ★ ROUT-SEQN-001 — 정상 가입 흐름 라우팅 시퀀스 순서 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login → /terms → /onboarding → /trade |

**사전 조건**
- 체험 URL(`?partner_code=YOUTHMETA`)에서 접속한 신규 사용자 상태이다

**테스트 단계**
1. LandingPage에서 로그인 버튼을 탭하여 `/login`으로 이동한다
2. Google OAuth 로그인을 완료한다
3. `/terms` 페이지로 자동 이동되는지 확인한다
4. 약관 체크박스를 탭하고 Accept 버튼을 탭한다
5. `/onboarding` 페이지로 자동 이동되는지 확인한다
6. 온보딩 3단계 완료 후 `Start Trading` 버튼을 탭한다
7. `/trade` 페이지로 이동되는지 확인한다

**예상 결과**
- 로그인 → `/terms` → `/onboarding` → `/trade` 순서로 라우팅된다
- 각 단계에서 이전 단계를 건너뛰거나 역방향 이동이 발생하지 않는다

---

### ROUT-BACK-001 — 온보딩 완료 후 뒤로 가기 접근 차단 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade, /onboarding |

**사전 조건**
- 온보딩이 완료된 계정으로 `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. `/trade` 화면에서 모바일 브라우저 뒤로 가기 제스처 또는 버튼을 사용한다
2. `/onboarding` 페이지로 이동되는지 확인한다

**예상 결과**
- 온보딩 완료 후 뒤로 가기 시 `/onboarding` 페이지가 표시되지 않는다
- `/trade` 화면이 유지되거나 LandingPage로 이동된다

**비고**
- [신규] 코드 근거: F-007 라우트 가드 — 완료 상태에서의 역방향 접근 처리

---

### ROUT-INAP-001 — in-app 브라우저 접속 시 외부 브라우저 안내 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 카카오톡 또는 네이버 앱 내 브라우저에서 체험 URL에 접속한 상태이다

**테스트 단계**
1. 카카오톡 채팅방에서 체험 URL 링크를 탭하여 in-app 브라우저로 접속한다
2. 화면에 외부 브라우저 안내 메시지가 표시되는지 확인한다

**예상 결과**
- in-app 브라우저 접속 감지 시 외부 브라우저 사용을 안내하는 메시지가 표시된다
- Google OAuth 로그인 버튼이 동작하지 않거나 외부 브라우저 안내를 우선 표시한다

**비고**
- [미결] in-app 브라우저 안내 방법(팝업, 인터셉트 화면 등) 미정 — 정책 확정 후 검증 필요

---

### ROUT-LOGD-001 — 로그인 완료 후 /terms로 자동 이동 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login, /terms |

**사전 조건**
- 비로그인 상태이다
- `/login` 페이지에 접속한 상태이다
- 약관 미동의 상태의 신규 계정이다

**테스트 단계**
1. `/login` 페이지에서 Google 로그인 버튼을 탭한다
2. Google OAuth 로그인 절차를 완료한다
3. 로그인 후 이동되는 페이지를 확인한다

**예상 결과**
- 로그인 완료 후 `/terms` 페이지로 자동 이동된다
- `/trade` 또는 다른 페이지로 이동되지 않는다

---

### ROUT-ALRD-001 — 이미 로그인된 사용자 /login 직접 접근 시 리다이렉트 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login, /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인된 상태이다

**테스트 단계**
1. 브라우저에서 `/login` URL에 직접 접속한다

**예상 결과**
- `/login` 페이지가 표시되지 않는다
- `/trade` 페이지로 리다이렉트된다

**비고**
- [신규] 코드 근거: F-006 전역 인증 상태 관리 — 이미 로그인된 사용자의 역방향 접근 처리

---

### ROUT-STAT-001 — 전역 인증 상태 3종 조합에 따른 라우팅 분기 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms, /onboarding, /trade |

**사전 조건**
- 로그인 완료, 약관 동의 완료, 온보딩 완료 상태의 계정이 있다

**테스트 단계**
1. 해당 계정으로 로그인한다
2. 앱 진입 후 이동되는 화면을 확인한다

**예상 결과**
- 로그인(`isLoggedIn=true`) + 약관 동의(`hasAcceptedTerms=true`) + 온보딩 완료(`hasCompletedOnboarding=true`) 상태에서 `/trade`로 직접 이동된다
- 중간 단계 페이지를 거치지 않는다

**비고**
- [신규] 코드 근거: F-006 전역 인증 상태 관리 — `isLoggedIn`, `hasAcceptedTerms`, `hasCompletedOnboarding` 3종 상태 분기
