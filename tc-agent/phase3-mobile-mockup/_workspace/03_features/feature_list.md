# Phase 3 기능 목록

**생성일:** 2026-04-03
**기준 소스:** policy_doc.md + parsed_content.md + tc-rules.md + tc-rules-override.md

---

## 요약

- **총 기능 수:** 42개
- **도메인별:**
  AUTH 8개 / LEVR 4개 / TPSL 5개 / TRAD 9개 / SGNL 7개 / FUND 2개 / MOBL 4개 / SETG 3개

---

## AUTH — 인증/온보딩

> 포함 화면: `/` (랜딩), `/login` (로그인), `/terms` (약관 동의), `/onboarding` (온보딩)

### F-AUTH-001: 랜딩 화면 진입 및 Google 로그인 CTA

- **설명**: 랜딩 화면에서 인증 없이 진입 가능하며, "Continue with Google" 버튼 탭 시 `/login`으로 이동하는 흐름
- **우선순위**: High
- **관련 화면**: `/`
- **예상 TC 수**: 2

### F-AUTH-002: Google 소셜 로그인 (Continue as John Doe)

- **설명**: 로그인 화면에서 목업 계정(John Doe)으로 로그인 버튼 탭 시 `isLoggedIn: true` 상태 전환 후 `/terms`로 이동
- **우선순위**: High
- **관련 화면**: `/login`
- **예상 TC 수**: 3

### F-AUTH-003: 로그인 화면 딤 영역 탭 — 랜딩 복귀

- **설명**: 로그인 화면의 딤(dim) 영역 탭 시 로그인 처리 없이 랜딩(`/`)으로 복귀하는 동작
- **우선순위**: Medium
- **관련 화면**: `/login`
- **예상 TC 수**: 2

### F-AUTH-004: 약관 체크박스 토글 및 Accept 버튼 활성화

- **설명**: 약관 동의 화면에서 체크박스 미체크 시 Accept 버튼 비활성화(opacity 0.4), 체크 시 활성화되는 조건부 UI 동작
- **우선순위**: High
- **관련 화면**: `/terms`
- **예상 TC 수**: 3

### F-AUTH-005: 약관 동의 Accept — 온보딩 이동

- **설명**: 체크박스 체크 상태에서 Accept 버튼 탭 시 `ACCEPT_TERMS` 디스패치 후 `/onboarding`으로 이동
- **우선순위**: High
- **관련 화면**: `/terms`
- **예상 TC 수**: 2

### F-AUTH-006: 약관 외부 링크 오픈 (Terms of Service / Privacy Policy)

- **설명**: 약관 동의 화면의 Terms of Service / Privacy Policy 링크 탭 시 각각 새 탭으로 외부 URL 오픈
- **우선순위**: Medium
- **관련 화면**: `/terms`
- **예상 TC 수**: 2

### F-AUTH-007: 온보딩 자동 3단계 진행 (타이머 기반)

- **설명**: 온보딩 화면에서 유저 입력 없이 타이머 기반으로 3단계(Creating wallet → Connecting to Hyperliquid → Loading test funds)가 순차 진행되고, 3.2초 후 완료 상태로 전환
- **우선순위**: High
- **관련 화면**: `/onboarding`
- **예상 TC 수**: 4

### F-AUTH-008: 온보딩 완료 후 Start Trading 버튼 활성화 및 트레이딩 이동

- **설명**: 온보딩 완료 전 "Start Trading" 버튼 비가시(opacity 0), 완료 후 잔고 카드와 함께 fadeIn 표시되고 탭 시 `/trade`로 이동
- **우선순위**: High
- **관련 화면**: `/onboarding`
- **예상 TC 수**: 3

---

## LEVR — 레버리지

> 포함 화면: AdjustLeverage 모달 (트레이딩 화면 진입)

### F-LEVR-001: 레버리지 모달 오픈

- **설명**: 트레이딩 화면 OrderForm의 레버리지 버튼(`{n}x`) 탭 시 AdjustLeverage 모달이 오픈되는 동작
- **우선순위**: High
- **관련 화면**: `/trade` (탭: trade)
- **예상 TC 수**: 2

### F-LEVR-002: 레버리지 슬라이더 1x~2x 범위 제한

- **설명**: AdjustLeverage 모달 내 슬라이더가 1x~2x 범위로 제한되며, 경고 배너 "Max leverage limited to 2x (User Protection)"가 항상 표시
- **우선순위**: High
- **관련 화면**: AdjustLeverage 모달
- **예상 TC 수**: 3

### F-LEVR-003: 레버리지 Confirm — 설정 저장

- **설명**: 슬라이더 조작 후 Confirm 버튼 탭 시 `SET_LEVERAGE` 디스패치 후 모달 닫힘. 설정값이 OrderForm 레버리지 버튼에 반영됨
- **우선순위**: High
- **관련 화면**: AdjustLeverage 모달
- **예상 TC 수**: 2

### F-LEVR-004: 레버리지 Cancel — 변경 불저장

- **설명**: Cancel 버튼 탭 시 변경 내용을 저장하지 않고 모달 닫힘
- **우선순위**: Medium
- **관련 화면**: AdjustLeverage 모달
- **예상 TC 수**: 2

---

## TPSL — TP/SL 설정

> 포함 화면: AutoTpSlModal (트레이딩/설정 화면 진입), 설정 탭

### F-TPSL-001: AutoTpSlModal 오픈 (트레이딩/설정 화면)

- **설명**: 설정 화면의 Edit 버튼 탭 시 AutoTpSlModal이 오픈되는 동작. 기본값 TP 1.8% / SL 5.0% 표시
- **우선순위**: High
- **관련 화면**: `/trade` (탭: settings), AutoTpSlModal
- **예상 TC 수**: 2

### F-TPSL-002: TP/SL 퍼센트 입력 및 범위 검증

- **설명**: TP(0.1%~999.9%) / SL(0.1%~99.9%) 입력 범위 제한 및 TP+SL 모두 0일 때 Confirm 버튼 비활성화 동작
- **우선순위**: High
- **관련 화면**: AutoTpSlModal
- **예상 TC 수**: 4

### F-TPSL-003: AutoTpSlModal Confirm — 설정 저장

- **설명**: TP 또는 SL 값 > 0인 상태에서 Confirm 탭 시 `UPDATE_TP_SL` 디스패치, `autoTpSlEnabled: true` 전환, 모달 닫힘. 설정 화면에 변경값 반영
- **우선순위**: High
- **관련 화면**: AutoTpSlModal
- **예상 TC 수**: 3

### F-TPSL-004: Auto TP/SL 토글 ON/OFF

- **설명**: 설정 화면 토글 스위치로 `TOGGLE_AUTO_TP_SL` 디스패치. ON 상태에서 생성된 주문에 TP/SL 자동 적용
- **우선순위**: High
- **관련 화면**: `/trade` (탭: settings)
- **예상 TC 수**: 3

### F-TPSL-005: AutoTpSlModal Cancel — 변경 불저장

- **설명**: Cancel 버튼 탭 시 수정 내용을 저장하지 않고 모달 닫힘
- **우선순위**: Medium
- **관련 화면**: AutoTpSlModal
- **예상 TC 수**: 2

---

## TRAD — 트레이딩

> 포함 화면: `/trade` (탭: trade), CoinSelector 바텀시트

### F-TRAD-001: 코인 선택 바텀시트 오픈 및 코인 변경

- **설명**: CoinInfoBar의 코인 페어 탭 시 CoinSelector 바텀시트 오픈. 코인 행 탭 시 `SELECT_COIN` 디스패치 후 바텀시트 닫힘
- **우선순위**: High
- **관련 화면**: `/trade` (탭: trade), CoinSelector
- **예상 TC 수**: 3

### F-TRAD-002: 코인 검색 실시간 필터링

- **설명**: CoinSelector 내 검색 필드 입력 시 심볼/페어명 기반 실시간 필터링 동작. 결과 없는 경우 빈 상태 표시
- **우선순위**: Medium
- **관련 화면**: CoinSelector
- **예상 TC 수**: 3

### F-TRAD-003: Market 주문 실행 (Buy/Long, Sell/Short)

- **설명**: Market 주문 유형 선택 후 수량 입력 → Buy/Long 또는 Sell/Short 버튼 탭 시 `PLACE_ORDER` 디스패치, 포지션 생성, Toast 표시
- **우선순위**: High
- **관련 화면**: `/trade` (탭: trade)
- **예상 TC 수**: 4

### F-TRAD-004: Limit 주문 실행 — 가격 입력 필드 표시 및 미체결 주문 등록

- **설명**: Limit 주문 유형 선택 시 가격 입력 필드 표시, 가격 직접 입력 후 주문 실행 시 미체결 주문으로 등록
- **우선순위**: High
- **관련 화면**: `/trade` (탭: trade)
- **예상 TC 수**: 4

### F-TRAD-005: 주문 유형 Market/Limit 드롭다운 전환

- **설명**: OrderForm 주문 유형 드롭다운으로 Market ↔ Limit 전환. Market 선택 시 가격 필드 숨김, Limit 선택 시 표시
- **우선순위**: High
- **관련 화면**: `/trade` (탭: trade)
- **예상 TC 수**: 2

### F-TRAD-006: 수량 슬라이더 조작

- **설명**: 수량 슬라이더(0%~100%, 5개 도트)로 주문 수량 설정. 슬라이더 조작 시 수량 입력 필드에 반영
- **우선순위**: Medium
- **관련 화면**: `/trade` (탭: trade)
- **예상 TC 수**: 2

### F-TRAD-007: 포지션 Close

- **설명**: Dashboard Positions 탭의 PositionCard에서 Close 버튼 탭 시 `CLOSE_POSITION` 디스패치 후 "Position closed" Toast 표시, 포지션 목록에서 제거
- **우선순위**: High
- **관련 화면**: `/trade` (탭: trade)
- **예상 TC 수**: 3

### F-TRAD-008: 미체결 주문 Cancel

- **설명**: Dashboard Open Order 탭의 주문 카드에서 Cancel 버튼 탭 시 `CANCEL_ORDER` 디스패치 후 "Order cancelled" Toast 표시, 주문 목록에서 제거
- **우선순위**: High
- **관련 화면**: `/trade` (탭: trade)
- **예상 TC 수**: 3

### F-TRAD-009: Dashboard 탭 배지 표시 (Positions / Open Order)

- **설명**: Positions 탭: 포지션 수 > 0이면 녹색 배지 표시. Open Order 탭: 미체결 주문 수 > 0이면 노란색 배지 표시. 빈 상태 시 각각 "No open positions" / "No open orders" 표시
- **우선순위**: Medium
- **관련 화면**: `/trade` (탭: trade)
- **예상 TC 수**: 3

---

## SGNL — 시그널

> 포함 화면: `/trade` (탭: signal), SignalOrderSheet 바텀시트

### F-SGNL-001: 시그널 목록 표시 및 퍼포먼스 요약

- **설명**: 시그널 탭 진입 시 최근 30일 퍼포먼스 요약(Hit/Miss/Expired 카운트, Avg PnL, Hit Rate)과 시그널 카드 목록 표시
- **우선순위**: Medium
- **관련 화면**: `/trade` (탭: signal)
- **예상 TC 수**: 2

### F-SGNL-002: 시그널 필터 탭 전환 (All/Long/Short/Active/Closed)

- **설명**: 필터 탭바에서 All / Long / Short / Active / Closed 탭 선택 시 `SET_SIGNAL_FILTER` 디스패치 후 목록 필터링. 결과 없으면 "No signals matching this filter" 표시
- **우선순위**: Medium
- **관련 화면**: `/trade` (탭: signal)
- **예상 TC 수**: 4

### F-SGNL-003: 시그널 카드 상태별 표시 규칙 (ACTIVE/HIT_TP/HIT_SL/EXPIRED)

- **설명**: ACTIVE 상태: Execute 버튼 표시. HIT_TP: PnL 양수 녹색 표시. HIT_SL: PnL 음수 빨강 표시. EXPIRED/CANCELLED: Execute 버튼 없음, PnL 없음
- **우선순위**: Medium
- **관련 화면**: `/trade` (탭: signal)
- **예상 TC 수**: 4

### F-SGNL-004: 미읽음 시그널 배지 표시 및 초기화

- **설명**: BottomNav Signal 아이콘에 미읽음 수(`unreadCount`) > 0이면 배지 표시. 시그널 탭 진입 시 `MARK_SIGNALS_READ` 디스패치 후 배지 0으로 초기화
- **우선순위**: Medium
- **관련 화면**: `/trade` (탭: signal), BottomNav
- **예상 TC 수**: 3

### F-SGNL-005: 시그널 Execute — SignalOrderSheet 오픈

- **설명**: ACTIVE 시그널 카드의 Execute 버튼 탭 시 SignalOrderSheet 바텀시트 오픈. 시그널의 코인/방향/진입가/TP/SL/레버리지 정보 자동 표시
- **우선순위**: High
- **관련 화면**: `/trade` (탭: signal), SignalOrderSheet
- **예상 TC 수**: 2

### F-SGNL-006: SignalOrderSheet 주문 실행 (Market/Limit)

- **설명**: SignalOrderSheet에서 주문 유형(Market/Limit) 선택 후 Execute Order 버튼 탭 시 `EXECUTE_SIGNAL_ORDER` 디스패치, Toast("Order executed from signal") 표시, 트레이딩 탭으로 전환
- **우선순위**: High
- **관련 화면**: SignalOrderSheet
- **예상 TC 수**: 4

### F-SGNL-007: SignalOrderSheet Modify 모드 (Margin/Leverage 편집)

- **설명**: SignalOrderSheet에서 Modify 버튼 탭 시 편집 모드 ON/OFF 토글. 편집 모드: Margin 직접 입력, Leverage 1~2x 조정 가능
- **우선순위**: Medium
- **관련 화면**: SignalOrderSheet
- **예상 TC 수**: 3

---

## FUND — 자금

> 포함 화면: `/onboarding`, `/trade` (탭: portfolio)

### F-FUND-001: 초기 테스트 자금 지급 표시 (100,000 USDC)

- **설명**: 온보딩 완료 후 잔고 카드에 "Balance — 100,000 USDC" 표시. 내부 상태값 100.0 USDC와 화면 표시 단위 관계 확인
- **우선순위**: High
- **관련 화면**: `/onboarding`
- **예상 TC 수**: 2

### F-FUND-002: 포트폴리오 잔고 계산 표시 (totalBalance / available / totalMargin)

- **설명**: 포트폴리오 탭에서 totalBalance(ACCOUNT.balance + 포지션 PnL 합계), available(ACCOUNT.balance - 증거금 합계), totalMargin(증거금 합계), pnlPercent(소수점 2자리) 계산 및 표시
- **우선순위**: High
- **관련 화면**: `/trade` (탭: portfolio)
- **예상 TC 수**: 4

---

## MOBL — 모바일 UI

> 포함 화면: 전체 화면 공통, BottomNav, Header, Toast

### F-MOBL-001: BottomNav 탭 전환 및 활성 상태 표시

- **설명**: BottomNav의 Trade / Signal / Portfolio / Settings 4탭 전환. 활성 탭 아이콘+라벨 흰색, 비활성 회색 표시
- **우선순위**: High
- **관련 화면**: `/trade` (전체 탭)
- **예상 TC 수**: 3

### F-MOBL-002: Header Testnet 배지 표시

- **설명**: 앱 전체 Header 우측에 "Testnet" 배지가 항상 표시됨을 확인
- **우선순위**: Low
- **관련 화면**: 전체 화면 (Header 포함)
- **예상 TC 수**: 1

### F-MOBL-003: Toast 알림 자동 표시 및 사라짐

- **설명**: 주문 실행, 포지션 닫기, 주문 취소, 주소 복사, 시그널 주문 실행, 로그아웃 등 액션 후 Toast가 화면 하단에 표시되고 자동으로 사라짐
- **우선순위**: Medium
- **관련 화면**: 전체 화면 (Toast)
- **예상 TC 수**: 4

### F-MOBL-004: 포트폴리오 보유 포지션 및 최근 활동 표시

- **설명**: 포트폴리오 탭에서 보유 포지션 목록(컬러 바+코인+Side·Leverage+PnL) 및 최근 활동 목업 데이터 표시. 포지션 없을 시 "No open positions" 표시
- **우선순위**: Medium
- **관련 화면**: `/trade` (탭: portfolio)
- **예상 TC 수**: 3

---

## SETG — 설정

> 포함 화면: `/trade` (탭: settings)

### F-SETG-001: 지갑 주소 복사

- **설명**: 설정 화면 Account 섹션의 Copy 버튼 탭 시 Toast("Address copied!") 표시. 지갑 주소(`0x9834...9948`) 클립보드 복사
- **우선순위**: Medium
- **관련 화면**: `/trade` (탭: settings)
- **예상 TC 수**: 2

### F-SETG-002: 언어 전환 (English / 한국어)

- **설명**: 설정 화면 Language 섹션에서 English / 한국어 선택 시 `SET_LANGUAGE` 디스패치 후 localStorage 저장. 앱 재시작 시 저장된 언어 복원. 활성 언어 녹색 배경 표시
- **우선순위**: Medium
- **관련 화면**: `/trade` (탭: settings)
- **예상 TC 수**: 4

### F-SETG-003: 로그아웃 (목업 동작)

- **설명**: 설정 화면 Logout 버튼 탭 시 Toast("Logged out (mockup)") 표시. 실제 로그아웃 및 상태 초기화 없음
- **우선순위**: Low
- **관련 화면**: `/trade` (탭: settings)
- **예상 TC 수**: 2

---

## [미결] 기능 목록

> 정책 미확정으로 TC 작성 보류 항목

| 보류 ID | 도메인 | 항목 | 미확정 내용 |
|---------|--------|------|------------|
| PEND-AUTH-001 | AUTH | LeverageNotice 노출 조건 | `hasSeenLeverageNotice` 표시 시점 및 쿠키/세션 범위 미확정 (최초 1회 vs 매 로그인) |
| PEND-AUTH-002 | AUTH | 초기 잔고 단위 | 코드 100.0 USDC — 화면 100,000 USDC 단위 변환 정책 확인 필요 |
| PEND-AUTH-003 | AUTH | 온보딩 중 뒤로가기 | 온보딩 진행 중 뒤로가기 시 중단/재시작 여부 미확정 |
| PEND-AUTH-004 | AUTH | 로그인 상태 유지 | 앱 재시작/새로고침 시 `isLoggedIn` localStorage 저장 여부 미확정 |
| PEND-TRAD-001 | TRAD | 오더북 데이터 소스 | 목업 정적 데이터 vs 실제 Hyperliquid API 연동 미확정 |
| PEND-TRAD-002 | TRAD | 수량 0 주문 처리 | 수량 미입력/0 입력 시 주문 버튼 동작 정책 미확정 |
| PEND-TRAD-003 | TRAD | 잔고 부족 검증 | 잔고 부족 시 주문 거부 처리 여부 미확정 |
| PEND-TRAD-004 | TRAD | Limit 주문 가격 미입력 | Limit 주문 유형에서 가격 미입력 상태로 주문 버튼 탭 시 동작 미확정 |
| PEND-SIGN-001 | SGNL | 시그널 주문 수량 단위 | SignalOrderSheet Margin 입력 단위 (USD 금액 vs 코인 수량) 미확정 |
| PEND-SIGN-002 | SGNL | Margin 상한 검증 | Margin 입력값이 가용 잔고 초과 시 처리 정책 미확정 |
| PEND-SIGN-003 | SGNL | 중복 시그널 주문 | 동일 시그널 중복 Execute 방지 정책 미확정 |
| PEND-SIGN-004 | SGNL | 시그널 데이터 갱신 | 목업 고정 데이터 vs 실시간 API 갱신 미확정 |
| PEND-PORT-001 | FUND | 최근 활동 데이터 갱신 | 목업 고정 데이터 — 실제 API 연동 시 동적 표시 정책 미확정 |
| PEND-PORT-002 | FUND | PnL = 0 색상 | PnL이 정확히 0인 경우 표시 색상 미확정 |
| PEND-PORT-003 | FUND | 잔고 0 처리 | ACCOUNT.balance = 0 시 pnlPercent 0 나누기 예외 처리 미확정 |
| PEND-SETS-001 | SETG | Auto TP/SL OFF + Edit | OFF 상태에서 Edit → Confirm 시 ON 자동 전환 여부 미확정 |
| PEND-SETS-002 | SETG | TP 또는 SL 단독 0 | TP=0이고 SL>0인 경우 Confirm 버튼 활성 여부 미확정 |
| PEND-SETS-003 | SETG | 언어 전환 후 Toast | 언어 전환 직후 Toast가 새 언어로 표시되는지 미확정 |
| PEND-SETS-004 | SETG | 저장 실패 Toast 문구 | Auto TP/SL 저장 실패 시 에러 Toast 정확한 문구 미확정 |
| PEND-NAVI-001 | MOBL | Toast 연속 발생 | 복수 Toast 연속 발생 시 표시 순서/덮어쓰기 정책 미확정 |
| PEND-NAVI-002 | MOBL | Toast 자동 사라짐 시간 | HIDE_TOAST 자동 디스패치 타이밍(ms) 기획서 미명시 |
| PEND-NAVI-003 | MOBL | 주문 실행 Toast 문구 | Market/Limit 주문 실행 Toast 정확한 문구 미확정 |
