# 기능 분류표 v1 — Supercycl Phase 2 Mobile

> 작성 일시: 2026-04-03
> 상태: **✅ STEP 3 완료 — 승인됨**
> TC 기준: tc_final.md v4.1 (127개)
> 검토자 결정사항 4건 반영 완료

---

## 대분류 코드 정의

| 대분류 | 코드 | 설명 |
|--------|------|------|
| Authentication & Onboarding | AUTH | 로그인, 약관, 온보딩, 자금 지급 |
| Referral | REFF | 파트너 코드, 레퍼럴 추적 |
| Leverage | LEVR | 레버리지 설정, 슬라이더, 팝업 |
| TP/SL (Take Profit / Stop Loss) | TPSL | Auto TP/SL 설정, 모달, 포지션 배지 |
| Trading | TRAD | 주문, 포지션, Dashboard, PnL |
| Signal | SGNL | 시그널 목록, 필터, 실행 |
| Mobile UI | MOBL | 반응형 레이아웃, 테마, 네비게이션 |
| Settings | SETG | 계정 설정, TP/SL 설정(Trading Preferences), Exchange 연결 |
| Routing | ROUT | 라우트 가드, 페이지 이동 순서 |

---

## 기능 분류표 (확정)

### AUTH — Authentication & Onboarding

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 해당 TC ID |
|-----|--------|--------|--------|--------------|-----------|
| 1 | AUTH | Login | OAuth 로그인 | SC-AUTH-LOGN | AUTH-OAUTH-001/002 |
| 2 | AUTH | Terms | 약관 동의 | SC-AUTH-TERM | AUTH-TERMS-001/002/003/004 |
| 3 | AUTH | Terms | 재접근 차단 | SC-AUTH-TERM | AUTH-GUARD-001/002 |
| 4 | AUTH | Onboarding | 단계 진행 | SC-AUTH-ONBD | AUTH-ONBD-001/003 |
| 5 | AUTH | Onboarding | In-App 브라우저 | SC-AUTH-INAP | AUTH-INAPP-001 |
| 6 | AUTH | Fund | 초기 자금 지급 | SC-AUTH-FUND | AUTH-FUND-001/002/003 |
| 7 | AUTH | Fund | 초기 잔고 상수 | SC-AUTH-FUND | AUTH-CONST-001 |

> **결정 #1**: AUTH-GUARD-001/002는 AUTH > Terms 중분류로 확정. ROUT로 이동하지 않음.

### REFF — Referral

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 해당 TC ID |
|-----|--------|--------|--------|--------------|-----------|
| 8 | REFF | Partner Code | URL 파싱 | SC-REFF-PARS | REFF-PARS-001/002 |
| 9 | REFF | Partner Code | 상수 코드 | SC-REFF-CODE | REFF-CODE-001 |

### LEVR — Leverage

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 해당 TC ID |
|-----|--------|--------|--------|--------------|-----------|
| 10 | LEVR | Adjust Leverage Modal | 슬라이더 범위 | SC-LEVR-ADJM | LEVR-CNST-001/002/003, LEVR-SLDR-001/002 |
| 11 | LEVR | Adjust Leverage Modal | 입력 제한 | SC-LEVR-ADJM | LEVR-INPT-001/002 |
| 12 | LEVR | LeverageNotice Popup | 노출 정책 | SC-LEVR-NOTI | LEVR-POPUP-001/002, LEVR-RPOP-001 |
| 13 | LEVR | LeverageNotice Popup | 팝업 문구 | SC-LEVR-NOTI | LEVR-NTXT-001 |
| 14 | LEVR | LeverageNotice Popup | I Understand 후 화면 진입 | SC-LEVR-NOTI | LEVR-IUND-001, LEVR-ORDR-001 |
| 15 | LEVR | Leverage Policy | 경고 배너 | SC-LEVR-PLCY | LEVR-BNNER-001 |
| 16 | LEVR | Leverage Policy | 코인 변경 시 동작 | SC-LEVR-PLCY | LEVR-COIN-001/002 |
| 17 | LEVR | Leverage Policy | 포지션 보유 중 변경 | SC-LEVR-PLCY | LEVR-MRGIN-001 |

> **결정 #2**: LEVR-ORDR-001 시나리오 확정 — LeverageNotice 팝업 표시 → I Understand 탭 → 팝업 닫힘 → Trade 화면 표시 확인. TC 예상결과 업데이트 반영됨.

### TPSL — Take Profit / Stop Loss

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 해당 TC ID |
|-----|--------|--------|--------|--------------|-----------|
| 18 | TPSL | Auto TP/SL Modal | 모달 표시 | SC-TPSL-MODL | TPSL-MODL-001 |
| 19 | TPSL | Auto TP/SL Modal | 확인 버튼 활성화 | SC-TPSL-MODL | TPSL-MODL-002/003 |
| 20 | TPSL | Auto TP/SL Modal | 경계값 입력 | SC-TPSL-BDRY | TPSL-BDRY-001/002/003/004 |
| 21 | TPSL | Auto TP/SL Modal | 저장 오류 처리 | SC-TPSL-MODL | TPSL-ERRL-001 |
| 22 | TPSL | Global State | 기본값 및 전역 상태 | SC-TPSL-STAT | TPSL-DFLT-001, TPSL-STAT-001, TPSL-INIT-001 |
| 23 | TPSL | Order Form Integration | OrderForm 인디케이터 | SC-TPSL-ORDF | TPSL-ORDF-001/002/003 |
| 24 | TPSL | Order Form Integration | 수동 TP/SL 우선순위 | SC-TPSL-ORDF | TPSL-PRTY-001 |
| 25 | TPSL | Position Card | Auto 배지 | SC-TPSL-PSTN | TPSL-PSTN-001/002/003 |

### TRAD — Trading

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 해당 TC ID |
|-----|--------|--------|--------|--------------|-----------|
| 26 | TRAD | Coin Selector | 지원 코인 목록 | SC-TRAD-COIN | TRAD-COIN-001/002 |
| 27 | TRAD | Order Form | 주문 타입 UI | SC-TRAD-ORDF | TRAD-OTYP-001 |
| 28 | TRAD | Order Form | 가격 입력 필드 | SC-TRAD-ORDF | TRAD-PRIC-001/002/003 |
| 29 | TRAD | Order Form | 수량 슬라이더 | SC-TRAD-ORDF | TRAD-SLDR-001 |
| 30 | TRAD | Order Form | 자동 채움 | SC-TRAD-ORDF | TRAD-PRFL-001 |
| 31 | TRAD | Order Execution | 주문 실행 | SC-TRAD-EXEC | TRAD-ORDR-001/002/003 |
| 32 | TRAD | Order Execution | 주문 확인 모달 | SC-TRAD-EXEC | TRAD-CONF-001/002 |
| 33 | TRAD | Dashboard | Positions 탭 | SC-TRAD-DASH | TRAD-DASH-001 |
| 34 | TRAD | Dashboard | Open Orders 탭 | SC-TRAD-DASH | TRAD-OPEN-001 |
| 35 | TRAD | Dashboard | History 탭 | SC-TRAD-DASH | TRAD-HIST-001 |
| 36 | TRAD | Dashboard | Portfolio 탭 | SC-TRAD-DASH | TRAD-PORT-001 |
| 37 | TRAD | Position Card | PnL 색상 분기 | SC-TRAD-PSTN | TRAD-PNL-001/002 |
| 38 | TRAD | Position Card | 청산 확인 모달 | SC-TRAD-PSTN | TRAD-CLSE-001/002 |

### SGNL — Signal

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 해당 TC ID |
|-----|--------|--------|--------|--------------|-----------|
| 39 | SGNL | Signal List | 헤더 및 성과 카드 | SC-SGNL-LIST | SGNL-HEAD-001, SGNL-SUMM-001, SGNL-CLRS-001 |
| 40 | SGNL | Signal List | 필터 탭 | SC-SGNL-LIST | SGNL-FILT-001/002, SGNL-CLSD-001 |
| 41 | SGNL | Signal Execution | 바텀시트 | SC-SGNL-EXEC | SGNL-SHTS-001 |
| 42 | SGNL | Signal Execution | Execute 주문 | SC-SGNL-EXEC | SGNL-EXEC-001/002 |
| 43 | SGNL | Signal Execution | Modify 로드 | SC-SGNL-EXEC | SGNL-MODF-001 |

### MOBL — Mobile UI

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 해당 TC ID |
|-----|--------|--------|--------|--------------|-----------|
| 44 | MOBL | Testnet Banner | 배너 노출 | SC-MOBL-TNBN | MOBL-TNBN-001/002 |
| 45 | MOBL | Testnet Banner | 배지·고지 문구 | SC-MOBL-TNBN | MOBL-TNBG-001 |
| 46 | MOBL | Layout | 최대 너비 320px | SC-MOBL-LAYT | MOBL-LAYT-001 |
| 47 | MOBL | Layout | Order Form 터치 | SC-MOBL-LAYT | MOBL-ORDF-001/002 |
| 48 | MOBL | Layout | Dashboard 터치 | SC-MOBL-LAYT | MOBL-DASH-001 |
| 49 | MOBL | Layout | Chart 반응형 | SC-MOBL-LAYT | MOBL-CHRT-001 |
| 50 | MOBL | Layout | Coin Info Bar | SC-MOBL-LAYT | MOBL-COIN-001 |
| 51 | MOBL | Bottom Navigation | 4탭 네비게이션 | SC-MOBL-BNAV | MOBL-BNAV-001/002 |
| 52 | MOBL | Bottom Navigation | 콘텐츠 스크롤 | SC-MOBL-BNAV | MOBL-SCRL-001 |
| 53 | MOBL | Theme & Style | 다크 테마 | SC-MOBL-THME | MOBL-DKTH-001 |
| 54 | MOBL | Theme & Style | CSS 변수 | SC-MOBL-THME | MOBL-CSSV-001 |
| 55 | MOBL | Animation | 페이드인 | SC-MOBL-ANIM | MOBL-LDFN-001, MOBL-LGFN-001 |
| 56 | MOBL | Exchange Integration | Testnet API | SC-MOBL-EXCH | MOBL-EXCH-001, MOBL-HLAP-001 |

> **결정 #3**: MOBL-ONCD-001 삭제 — 온보딩 완료 후 CEX 통합 안내 팝업/모달 기능 제거됨. AUTH-ONBD-002도 동일 내용으로 함께 삭제. TC 127개로 조정.

### SETG — Settings

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 해당 TC ID |
|-----|--------|--------|--------|--------------|-----------|
| 57 | SETG | Account | 이메일·지갑 주소 표시 | SC-SETG-ACCT | SETG-ACCT-001 |
| 58 | SETG | Account | 지갑 주소 복사 | SC-SETG-ACCT | SETG-WCPY-001 |
| 59 | SETG | Account | Logout | SC-SETG-ACCT | SETG-LOUT-001/002 |
| 60 | SETG | Trading Preferences | TP/SL 설정값 표시 | SC-SETG-TPRF | SETG-TPSL-001/002, TPSL-STNG-001 |
| 61 | SETG | Trading Preferences | 토글 ON/OFF | SC-SETG-TPRF | SETG-TGTG-001/002, TPSL-TOGL-001/002 |
| 62 | SETG | Trading Preferences | 진입 경로 | SC-SETG-TPRF | TPSL-PATH-001 |
| 63 | SETG | Trading Preferences | 저장 결과 | SC-SETG-TPRF | TPSL-SAVE-001 |
| 64 | SETG | Exchange Connection | 연결 상태 표시 | SC-SETG-EXCO | SETG-EXCO-001 |
| 65 | SETG | Coach Mark | 단계별 가이드 | SC-SETG-COCH | SETG-COCH-001 |

> **결정 #4**: SETG > Trading Preferences = TPSL > Settings — 같은 화면(Settings > Trading Preferences 메뉴). 분류표에서 SETG > Trading Preferences로 통합. TC ID는 현행 유지, 중분류 기준으로 동일하게 분류.

### ROUT — Routing

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 해당 TC ID |
|-----|--------|--------|--------|--------------|-----------|
| 66 | ROUT | Auth Guard | 미인증 접근 차단 | SC-ROUT-AUTH | ROUT-AUTH-001/002/003 |
| 67 | ROUT | Auth Guard | 이미 로그인 차단 | SC-ROUT-AUTH | ROUT-ALRD-001 |
| 68 | ROUT | Step Guard | 약관 미동의 차단 | SC-ROUT-STEP | ROUT-ONBD-001 |
| 69 | ROUT | Step Guard | 온보딩 미완료 차단 | SC-ROUT-STEP | ROUT-TRAD-001 |
| 70 | ROUT | Step Guard | 뒤로 가기 차단 | SC-ROUT-STEP | ROUT-BACK-001 |
| 71 | ROUT | Navigation Flow | 가입 흐름 시퀀스 | SC-ROUT-FLOW | ROUT-SEQN-001 |
| 72 | ROUT | Navigation Flow | 로그인 완료 자동이동 | SC-ROUT-FLOW | ROUT-LOGD-001 |
| 73 | ROUT | Navigation Flow | 전역 상태 조합 분기 | SC-ROUT-FLOW | ROUT-STAT-001 |

---

## 요약

| 항목 | 수치 |
|------|------|
| 대분류 | 9개 |
| 중분류 | 27개 |
| 소분류(행) | 73개 |
| 총 TC | 127개 |
| 불확실 항목 | **0건** (전체 확정) |

---

## 검토자 결정사항 요약

| # | 항목 | 결정 | TC 변경 |
|---|------|------|---------|
| 1 | AUTH-GUARD-001/002 배치 | AUTH > Terms > 재접근 차단 유지 | 없음 |
| 2 | LEVR-ORDR-001 시나리오 | I Understand → 팝업 닫힘 → Trade 화면 표시 = PASS | TC 예상결과 수정 완료 |
| 3 | CEX 안내 팝업/모달 | 기능 삭제됨 → TC 2개 제거 (AUTH-ONBD-002, MOBL-ONCD-001) | TC 삭제 완료 (129 → 127) |
| 4 | SETG vs TPSL TP/SL 설정 | SETG > Trading Preferences로 통합 분류 | TC ID 현행 유지 |
