# Phase 3 분류표 초안

> 이 문서는 Human Gate 검토 대상입니다.
> 검토 후 `classification_v1_APPROVED.md`로 복사·저장하고 '승인됐어'라고 알려주세요.

---

## 분류 요약

| 대분류 | 중분류 수 | 소분류 수 | 예상 TC |
|--------|----------|----------|--------|
| AUTH   | 3        | 8        | 19     |
| LEVR   | 2        | 4        | 9      |
| TPSL   | 2        | 5        | 14     |
| TRAD   | 4        | 9        | 27     |
| SGNL   | 3        | 7        | 18     |
| FUND   | 2        | 2        | 6      |
| MOBL   | 3        | 4        | 11     |
| SETG   | 3        | 3        | 8      |
| **합계** | **22** | **42** | **112** |

---

## AUTH — 인증/온보딩

### AUTH-LOGN — 로그인

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 랜딩 화면 진입 및 Google 로그인 CTA | 랜딩(`/`) 인증 없이 진입 가능, "Continue with Google" 버튼 탭 → `/login` 이동 흐름 | 2 |
| Google 소셜 로그인 (Continue as John Doe) | 목업 계정(John Doe)으로 로그인 탭 → `isLoggedIn: true` 전환 후 `/terms` 이동 | 3 |
| 로그인 화면 딤 영역 탭 — 랜딩 복귀 | 딤 영역 탭 시 로그인 처리 없이 랜딩(`/`)으로 복귀 | 2 |

**중분류 소계: 소분류 3개 / 예상 TC 7개**

---

### AUTH-TERM — 약관 동의

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 약관 체크박스 토글 및 Accept 버튼 활성화 | 미체크 시 Accept 비활성화(opacity 0.4), 체크 시 활성화 조건부 UI | 3 |
| 약관 동의 Accept — 온보딩 이동 | 체크 상태에서 Accept 탭 → `ACCEPT_TERMS` 디스패치 후 `/onboarding` 이동 | 2 |
| 약관 외부 링크 오픈 (Terms of Service / Privacy Policy) | Terms of Service / Privacy Policy 링크 탭 → 각각 새 탭으로 외부 URL 오픈 | 2 |

**중분류 소계: 소분류 3개 / 예상 TC 7개**

---

### AUTH-ONBD — 온보딩

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 온보딩 자동 3단계 진행 (타이머 기반) | 유저 입력 없이 3단계 순차 진행(Creating wallet → Connecting → Loading), 3.2초 후 완료 전환 | 4 |
| 온보딩 완료 후 Start Trading 버튼 활성화 및 트레이딩 이동 | 완료 전 버튼 비가시(opacity 0), 완료 후 fadeIn + 탭 시 `/trade` 이동 | 3 |

**중분류 소계: 소분류 2개 / 예상 TC 7개**

---

## LEVR — 레버리지

### LEVR-MODL — 레버리지 모달

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 레버리지 모달 오픈 | OrderForm 레버리지 버튼(`{n}x`) 탭 → AdjustLeverage 모달 오픈 | 2 |
| 레버리지 슬라이더 1x~2x 범위 제한 | 슬라이더 1x~2x 범위 제한, 경고 배너 "Max leverage limited to 2x (User Protection)" 항상 표시 | 3 |

**중분류 소계: 소분류 2개 / 예상 TC 5개**

---

### LEVR-CONF — 레버리지 확인/취소

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 레버리지 Confirm — 설정 저장 | 슬라이더 조작 후 Confirm 탭 → `SET_LEVERAGE` 디스패치, 모달 닫힘, OrderForm 버튼 반영 | 2 |
| 레버리지 Cancel — 변경 불저장 | Cancel 탭 → 변경 내용 저장 없이 모달 닫힘 | 2 |

**중분류 소계: 소분류 2개 / 예상 TC 4개**

---

## TPSL — TP/SL 설정

### TPSL-MODL — AutoTpSl 모달

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| AutoTpSlModal 오픈 (설정 화면) | 설정 화면 Edit 버튼 탭 → AutoTpSlModal 오픈, 기본값 TP 1.8% / SL 5.0% 표시 | 2 |
| TP/SL 퍼센트 입력 및 범위 검증 | TP(0.1%~999.9%) / SL(0.1%~99.9%) 범위 제한, TP+SL 모두 0일 때 Confirm 버튼 비활성화 | 4 |
| AutoTpSlModal Confirm — 설정 저장 | TP 또는 SL > 0 상태에서 Confirm → `UPDATE_TP_SL` 디스패치, `autoTpSlEnabled: true`, 모달 닫힘, 설정 화면 반영 | 3 |
| AutoTpSlModal Cancel — 변경 불저장 | Cancel 탭 → 수정 내용 저장 없이 모달 닫힘 | 2 |

**중분류 소계: 소분류 4개 / 예상 TC 11개**

---

### TPSL-TOGL — Auto TP/SL 토글

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| Auto TP/SL 토글 ON/OFF | 설정 화면 토글 스위치 → `TOGGLE_AUTO_TP_SL` 디스패치, ON 시 신규 주문에 TP/SL 자동 적용 | 3 |

**중분류 소계: 소분류 1개 / 예상 TC 3개**

---

## TRAD — 트레이딩

### TRAD-COIN — 코인 선택

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 코인 선택 바텀시트 오픈 및 코인 변경 | CoinInfoBar 코인 페어 탭 → CoinSelector 바텀시트 오픈, 코인 행 탭 → `SELECT_COIN` 디스패치, 바텀시트 닫힘 | 3 |
| 코인 검색 실시간 필터링 | 검색 필드 입력 → 심볼/페어명 기반 실시간 필터링, 결과 없으면 빈 상태 표시 | 3 |

**중분류 소계: 소분류 2개 / 예상 TC 6개**

---

### TRAD-ORDF — 주문 실행

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| Market 주문 실행 (Buy/Long, Sell/Short) | Market 유형 + 수량 입력 → Buy/Long 또는 Sell/Short 탭 → `PLACE_ORDER` 디스패치, 포지션 생성, Toast 표시 | 4 |
| Limit 주문 실행 — 가격 입력 필드 표시 및 미체결 주문 등록 | Limit 유형 선택 → 가격 입력 필드 표시, 가격 입력 후 주문 실행 → 미체결 주문 등록 | 4 |
| 주문 유형 Market/Limit 드롭다운 전환 | 드롭다운으로 Market ↔ Limit 전환, Market 시 가격 필드 숨김 / Limit 시 표시 | 2 |
| 수량 슬라이더 조작 | 수량 슬라이더(0%~100%, 5개 도트) 조작 → 수량 입력 필드 반영 | 2 |

**중분류 소계: 소분류 4개 / 예상 TC 12개**

---

### TRAD-POSN — 포지션 관리

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 포지션 Close | PositionCard Close 버튼 탭 → `CLOSE_POSITION` 디스패치, "Position closed" Toast, 포지션 목록에서 제거 | 3 |

**중분류 소계: 소분류 1개 / 예상 TC 3개**

---

### TRAD-ORDR — 주문 관리 및 대시보드

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 미체결 주문 Cancel | Open Order 카드 Cancel 탭 → `CANCEL_ORDER` 디스패치, "Order cancelled" Toast, 주문 목록에서 제거 | 3 |
| Dashboard 탭 배지 표시 (Positions / Open Order) | 포지션 수 > 0이면 녹색 배지, 미체결 수 > 0이면 노란색 배지, 빈 상태 시 각각 안내 문구 표시 | 3 |

**중분류 소계: 소분류 2개 / 예상 TC 6개**

---

## SGNL — 시그널

### SGNL-LIST — 시그널 목록

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 시그널 목록 표시 및 퍼포먼스 요약 | 시그널 탭 진입 → 최근 30일 퍼포먼스 요약(Hit/Miss/Expired, Avg PnL, Hit Rate) + 시그널 카드 목록 표시 | 2 |
| 시그널 필터 탭 전환 (All/Long/Short/Active/Closed) | 필터 탭바 전환 → `SET_SIGNAL_FILTER` 디스패치, 목록 필터링, 결과 없으면 안내 문구 표시 | 4 |
| 시그널 카드 상태별 표시 규칙 (ACTIVE/HIT_TP/HIT_SL/EXPIRED) | ACTIVE: Execute 버튼 표시 / HIT_TP: PnL 녹색 / HIT_SL: PnL 빨강 / EXPIRED: Execute·PnL 없음 | 4 |
| 미읽음 시그널 배지 표시 및 초기화 | BottomNav Signal 아이콘 `unreadCount` > 0이면 배지 표시, 탭 진입 시 `MARK_SIGNALS_READ` 디스패치 → 배지 0 | 3 |

**중분류 소계: 소분류 4개 / 예상 TC 13개**

---

### SGNL-EXEC — 시그널 주문 실행

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 시그널 Execute — SignalOrderSheet 오픈 | ACTIVE 시그널 Execute 탭 → SignalOrderSheet 바텀시트 오픈, 코인/방향/진입가/TP/SL/레버리지 자동 표시 | 2 |
| SignalOrderSheet 주문 실행 (Market/Limit) | 주문 유형 선택 후 Execute Order 탭 → `EXECUTE_SIGNAL_ORDER` 디스패치, Toast("Order executed from signal"), 트레이딩 탭 전환 | 4 |

**중분류 소계: 소분류 2개 / 예상 TC 6개**

---

### SGNL-MODY — 시그널 주문 편집

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| SignalOrderSheet Modify 모드 (Margin/Leverage 편집) | Modify 버튼 탭 → 편집 모드 ON/OFF 토글, 편집 모드에서 Margin 직접 입력 및 Leverage 1~2x 조정 가능 | 3 |

**중분류 소계: 소분류 1개 / 예상 TC 3개**

---

## FUND — 자금

### FUND-INIT — 초기 자금 표시

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 초기 테스트 자금 지급 표시 (100,000 USDC) | 온보딩 완료 후 잔고 카드 "Balance — 100,000 USDC" 표시, 내부값(100.0 USDC)과 화면 표시 단위 관계 확인 | 2 |

**중분류 소계: 소분류 1개 / 예상 TC 2개**

---

### FUND-PTFL — 포트폴리오 잔고

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 포트폴리오 잔고 계산 표시 (totalBalance / available / totalMargin) | totalBalance(ACCOUNT.balance + 포지션 PnL 합계), available(balance - 증거금 합계), totalMargin(증거금 합계), pnlPercent(소수점 2자리) 계산·표시 | 4 |

**중분류 소계: 소분류 1개 / 예상 TC 4개**

---

## MOBL — 모바일 UI

### MOBL-NAV — 내비게이션

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| BottomNav 탭 전환 및 활성 상태 표시 | Trade / Signal / Portfolio / Settings 4탭 전환, 활성 탭 흰색 / 비활성 회색 표시 | 3 |

**중분류 소계: 소분류 1개 / 예상 TC 3개**

---

### MOBL-HEAD — 헤더

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| Header Testnet 배지 표시 | 앱 전체 Header 우측 "Testnet" 배지 항상 표시 | 1 |

**중분류 소계: 소분류 1개 / 예상 TC 1개**

---

### MOBL-TOST — Toast 알림

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| Toast 알림 자동 표시 및 사라짐 | 주문 실행·포지션 닫기·주문 취소·주소 복사·시그널 주문 실행·로그아웃 등 액션 후 화면 하단 Toast 표시 및 자동 사라짐 | 4 |
| 포트폴리오 보유 포지션 및 최근 활동 표시 | 포트폴리오 탭 진입 → 보유 포지션 목록(컬러 바+코인+Side·Leverage+PnL) 및 최근 활동 목업 데이터 표시, 포지션 없으면 안내 문구 | 3 |

**중분류 소계: 소분류 2개 / 예상 TC 7개**

> **비고**: `F-MOBL-004` (포트폴리오 보유 포지션 및 최근 활동 표시)는 포트폴리오 화면의 모바일 UI 표시에 해당하므로 MOBL-TOST 중분류에 함께 편성. 별도 중분류가 필요하면 MOBL-PORT로 분리 가능.

---

## SETG — 설정

### SETG-ACCT — 계정 설정

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 지갑 주소 복사 | Account 섹션 Copy 버튼 탭 → Toast("Address copied!"), 지갑 주소(`0x9834...9948`) 클립보드 복사 | 2 |

**중분류 소계: 소분류 1개 / 예상 TC 2개**

---

### SETG-LANG — 언어 설정

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 언어 전환 (English / 한국어) | Language 섹션 EN/KR 선택 → `SET_LANGUAGE` 디스패치, localStorage 저장, 앱 재시작 시 복원, 활성 언어 녹색 배경 표시 | 4 |

**중분류 소계: 소분류 1개 / 예상 TC 4개**

---

### SETG-LOUT — 로그아웃

| 소분류 | 설명 | 예상 TC |
|--------|------|--------|
| 로그아웃 (목업 동작) | Logout 버튼 탭 → Toast("Logged out (mockup)") 표시, 실제 로그아웃 및 상태 초기화 없음 | 2 |

**중분류 소계: 소분류 1개 / 예상 TC 2개**

---

## 중분류 코드 전체 목록

| 대분류 | 중분류코드 | 중분류명 | TC ID 접두사 예시 |
|--------|----------|---------|-----------------|
| AUTH | LOGN | 로그인 | SC-AUTH-LOGN-001 |
| AUTH | TERM | 약관 동의 | SC-AUTH-TERM-001 |
| AUTH | ONBD | 온보딩 | SC-AUTH-ONBD-001 |
| LEVR | MODL | 레버리지 모달 | SC-LEVR-MODL-001 |
| LEVR | CONF | 레버리지 확인/취소 | SC-LEVR-CONF-001 |
| TPSL | MODL | AutoTpSl 모달 | SC-TPSL-MODL-001 |
| TPSL | TOGL | Auto TP/SL 토글 | SC-TPSL-TOGL-001 |
| TRAD | COIN | 코인 선택 | SC-TRAD-COIN-001 |
| TRAD | ORDF | 주문 실행 | SC-TRAD-ORDF-001 |
| TRAD | POSN | 포지션 관리 | SC-TRAD-POSN-001 |
| TRAD | ORDR | 주문 관리 및 대시보드 | SC-TRAD-ORDR-001 |
| SGNL | LIST | 시그널 목록 | SC-SGNL-LIST-001 |
| SGNL | EXEC | 시그널 주문 실행 | SC-SGNL-EXEC-001 |
| SGNL | MODY | 시그널 주문 편집 | SC-SGNL-MODY-001 |
| FUND | INIT | 초기 자금 표시 | SC-FUND-INIT-001 |
| FUND | PTFL | 포트폴리오 잔고 | SC-FUND-PTFL-001 |
| MOBL | NAV | 내비게이션 | SC-MOBL-NAV-001 |
| MOBL | HEAD | 헤더 | SC-MOBL-HEAD-001 |
| MOBL | TOST | Toast 알림 | SC-MOBL-TOST-001 |
| SETG | ACCT | 계정 설정 | SC-SETG-ACCT-001 |
| SETG | LANG | 언어 설정 | SC-SETG-LANG-001 |
| SETG | LOUT | 로그아웃 | SC-SETG-LOUT-001 |

---

## 커버리지 확인

| Feature ID | 기능명 | 대분류 | 중분류 | 포함 여부 |
|-----------|--------|--------|--------|---------|
| F-AUTH-001 | 랜딩 화면 진입 및 Google 로그인 CTA | AUTH | LOGN | ✓ |
| F-AUTH-002 | Google 소셜 로그인 | AUTH | LOGN | ✓ |
| F-AUTH-003 | 로그인 화면 딤 영역 탭 — 랜딩 복귀 | AUTH | LOGN | ✓ |
| F-AUTH-004 | 약관 체크박스 토글 및 Accept 버튼 활성화 | AUTH | TERM | ✓ |
| F-AUTH-005 | 약관 동의 Accept — 온보딩 이동 | AUTH | TERM | ✓ |
| F-AUTH-006 | 약관 외부 링크 오픈 | AUTH | TERM | ✓ |
| F-AUTH-007 | 온보딩 자동 3단계 진행 (타이머 기반) | AUTH | ONBD | ✓ |
| F-AUTH-008 | 온보딩 완료 후 Start Trading 버튼 활성화 및 트레이딩 이동 | AUTH | ONBD | ✓ |
| F-LEVR-001 | 레버리지 모달 오픈 | LEVR | MODL | ✓ |
| F-LEVR-002 | 레버리지 슬라이더 1x~2x 범위 제한 | LEVR | MODL | ✓ |
| F-LEVR-003 | 레버리지 Confirm — 설정 저장 | LEVR | CONF | ✓ |
| F-LEVR-004 | 레버리지 Cancel — 변경 불저장 | LEVR | CONF | ✓ |
| F-TPSL-001 | AutoTpSlModal 오픈 | TPSL | MODL | ✓ |
| F-TPSL-002 | TP/SL 퍼센트 입력 및 범위 검증 | TPSL | MODL | ✓ |
| F-TPSL-003 | AutoTpSlModal Confirm — 설정 저장 | TPSL | MODL | ✓ |
| F-TPSL-004 | Auto TP/SL 토글 ON/OFF | TPSL | TOGL | ✓ |
| F-TPSL-005 | AutoTpSlModal Cancel — 변경 불저장 | TPSL | MODL | ✓ |
| F-TRAD-001 | 코인 선택 바텀시트 오픈 및 코인 변경 | TRAD | COIN | ✓ |
| F-TRAD-002 | 코인 검색 실시간 필터링 | TRAD | COIN | ✓ |
| F-TRAD-003 | Market 주문 실행 | TRAD | ORDF | ✓ |
| F-TRAD-004 | Limit 주문 실행 | TRAD | ORDF | ✓ |
| F-TRAD-005 | 주문 유형 Market/Limit 드롭다운 전환 | TRAD | ORDF | ✓ |
| F-TRAD-006 | 수량 슬라이더 조작 | TRAD | ORDF | ✓ |
| F-TRAD-007 | 포지션 Close | TRAD | POSN | ✓ |
| F-TRAD-008 | 미체결 주문 Cancel | TRAD | ORDR | ✓ |
| F-TRAD-009 | Dashboard 탭 배지 표시 | TRAD | ORDR | ✓ |
| F-SGNL-001 | 시그널 목록 표시 및 퍼포먼스 요약 | SGNL | LIST | ✓ |
| F-SGNL-002 | 시그널 필터 탭 전환 | SGNL | LIST | ✓ |
| F-SGNL-003 | 시그널 카드 상태별 표시 규칙 | SGNL | LIST | ✓ |
| F-SGNL-004 | 미읽음 시그널 배지 표시 및 초기화 | SGNL | LIST | ✓ |
| F-SGNL-005 | 시그널 Execute — SignalOrderSheet 오픈 | SGNL | EXEC | ✓ |
| F-SGNL-006 | SignalOrderSheet 주문 실행 | SGNL | EXEC | ✓ |
| F-SGNL-007 | SignalOrderSheet Modify 모드 | SGNL | MODY | ✓ |
| F-FUND-001 | 초기 테스트 자금 지급 표시 | FUND | INIT | ✓ |
| F-FUND-002 | 포트폴리오 잔고 계산 표시 | FUND | PTFL | ✓ |
| F-MOBL-001 | BottomNav 탭 전환 및 활성 상태 표시 | MOBL | NAV | ✓ |
| F-MOBL-002 | Header Testnet 배지 표시 | MOBL | HEAD | ✓ |
| F-MOBL-003 | Toast 알림 자동 표시 및 사라짐 | MOBL | TOST | ✓ |
| F-MOBL-004 | 포트폴리오 보유 포지션 및 최근 활동 표시 | MOBL | TOST | ✓ |
| F-SETG-001 | 지갑 주소 복사 | SETG | ACCT | ✓ |
| F-SETG-002 | 언어 전환 (English / 한국어) | SETG | LANG | ✓ |
| F-SETG-003 | 로그아웃 (목업 동작) | SETG | LOUT | ✓ |

**총 42개 기능 전체 포함 확인 완료**
