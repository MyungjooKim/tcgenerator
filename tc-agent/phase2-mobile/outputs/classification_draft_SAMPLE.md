# 기능 분류표 초안 — Supercycl Phase 2 Mobile

> 작성 일시: 2026-04-03
> 작성 주체: feature-classifier (AI 초안)
> 상태: **⏳ STEP 3 — 검토 대기 (승인 전)**
> 기준 TC: tc_final.md (129개, v4)

---

## 사용 방법

1. 아래 표를 검토하여 대분류/중분류/소분류가 올바른지 확인
2. 수정이 필요한 행은 직접 편집
3. `⚠️ 불확실` 행은 반드시 확인 후 결정
4. 검토 완료 후 "승인" → Step 4 TC 작성 시작

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
| Settings | SETG | 계정 설정, TP/SL 설정, Exchange 연결 |
| Routing | ROUT | 라우트 가드, 페이지 이동 순서 |

---

## 기능 분류표 (대분류 / 중분류 / 소분류)

### AUTH — Authentication & Onboarding

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 현재 TC ID | 비고 |
|-----|--------|--------|--------|--------------|-----------|------|
| 1 | AUTH | Login | OAuth 로그인 | SC-AUTH-LOGN | AUTH-OAUTH-001/002 | Google OAuth 단일 방식 |
| 2 | AUTH | Terms | 약관 동의 | SC-AUTH-TERM | AUTH-TERMS-001/002/003/004 | Accept/Decline |
| 3 | AUTH | Terms | 재접근 차단 | SC-AUTH-TERM | AUTH-GUARD-001/002 | ⚠️ 불확실: Guard를 Terms 중분류로 볼지, Routing으로 볼지 |
| 4 | AUTH | Onboarding | 단계 진행 | SC-AUTH-ONBD | AUTH-ONBD-001/002/003 | 3단계 온보딩 |
| 5 | AUTH | Onboarding | In-App 브라우저 | SC-AUTH-INAP | AUTH-INAPP-001 | iOS/Android 전용 |
| 6 | AUTH | Fund | 초기 자금 지급 | SC-AUTH-FUND | AUTH-FUND-001/002/003 | 1,000 USDC 지급 |
| 7 | AUTH | Fund | 초기 잔고 상수 | SC-AUTH-FUND | AUTH-CONST-001 | 상수값 1,000 USDC |

### REFF — Referral

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 현재 TC ID | 비고 |
|-----|--------|--------|--------|--------------|-----------|------|
| 8 | REFF | Partner Code | URL 파싱 | SC-REFF-PARS | REFF-PARS-001/002 | partner_code 파라미터 |
| 9 | REFF | Partner Code | 상수 코드 | SC-REFF-CODE | REFF-CODE-001 | YOUTHMETA 하드코딩 [신규] |

### LEVR — Leverage

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 현재 TC ID | 비고 |
|-----|--------|--------|--------|--------------|-----------|------|
| 10 | LEVR | Adjust Leverage Modal | 슬라이더 범위 | SC-LEVR-ADJM | LEVR-CNST-001/002/003, LEVR-SLDR-001/002 | |
| 11 | LEVR | Adjust Leverage Modal | 입력 제한 | SC-LEVR-ADJM | LEVR-INPT-001/002 | 소수점·0 입력 차단 |
| 12 | LEVR | LeverageNotice Popup | 노출 정책 | SC-LEVR-NOTI | LEVR-POPUP-001/002, LEVR-RPOP-001 | 최초 1회 |
| 13 | LEVR | LeverageNotice Popup | 팝업 문구 | SC-LEVR-NOTI | LEVR-NTXT-001 | |
| 14 | LEVR | LeverageNotice Popup | I Understand 버튼 | SC-LEVR-NOTI | LEVR-IUND-001 | |
| 15 | LEVR | LeverageNotice Popup | 노출 순서 | SC-LEVR-NOTI | LEVR-ORDR-001 | ⚠️ 불확실: Popup과 Modal 순서 정책 기획서에 명확하지 않음 |
| 16 | LEVR | Leverage Policy | 경고 배너 | SC-LEVR-PLCY | LEVR-BNNER-001 | |
| 17 | LEVR | Leverage Policy | 코인 변경 시 동작 | SC-LEVR-PLCY | LEVR-COIN-001/002 | |
| 18 | LEVR | Leverage Policy | 포지션 보유 중 변경 | SC-LEVR-PLCY | LEVR-MRGIN-001 | |

### TPSL — Take Profit / Stop Loss

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 현재 TC ID | 비고 |
|-----|--------|--------|--------|--------------|-----------|------|
| 19 | TPSL | Auto TP/SL Modal | 모달 표시 | SC-TPSL-MODL | TPSL-MODL-001 | |
| 20 | TPSL | Auto TP/SL Modal | 확인 버튼 활성화 | SC-TPSL-MODL | TPSL-MODL-002/003 | |
| 21 | TPSL | Auto TP/SL Modal | 경계값 입력 | SC-TPSL-BDRY | TPSL-BDRY-001/002/003/004 | Edge 케이스 |
| 22 | TPSL | Auto TP/SL Modal | 저장 오류 처리 | SC-TPSL-MODL | TPSL-ERRL-001 | |
| 23 | TPSL | Global State | 기본값 및 전역 상태 | SC-TPSL-STAT | TPSL-DFLT-001, TPSL-STAT-001, TPSL-INIT-001 | |
| 24 | TPSL | Order Form Integration | OrderForm 인디케이터 | SC-TPSL-ORDF | TPSL-ORDF-001/002/003 | |
| 25 | TPSL | Order Form Integration | 수동 TP/SL 우선순위 | SC-TPSL-ORDF | TPSL-PRTY-001 | |
| 26 | TPSL | Position Card | Auto 배지 | SC-TPSL-PSTN | TPSL-PSTN-001/002/003 | |
| 27 | TPSL | Settings | 설정값 표시 | SC-TPSL-SETG | TPSL-STNG-001, TPSL-SAVE-001 | |
| 28 | TPSL | Settings | 토글 ON/OFF | SC-TPSL-SETG | TPSL-TOGL-001/002 | |
| 29 | TPSL | Settings | 진입 경로 | SC-TPSL-SETG | TPSL-PATH-001 | |

### TRAD — Trading

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 현재 TC ID | 비고 |
|-----|--------|--------|--------|--------------|-----------|------|
| 30 | TRAD | Coin Selector | 지원 코인 목록 | SC-TRAD-COIN | TRAD-COIN-001/002 | 8종 |
| 31 | TRAD | Order Form | 주문 타입 UI | SC-TRAD-ORDF | TRAD-OTYP-001 | limit/market/conditional |
| 32 | TRAD | Order Form | 가격 입력 필드 | SC-TRAD-ORDF | TRAD-PRIC-001/002/003 | |
| 33 | TRAD | Order Form | 수량 슬라이더 | SC-TRAD-ORDF | TRAD-SLDR-001 | |
| 34 | TRAD | Order Form | 자동 채움 | SC-TRAD-ORDF | TRAD-PRFL-001 | prefillData [신규] |
| 35 | TRAD | Order Execution | 주문 실행 | SC-TRAD-EXEC | TRAD-ORDR-001/002/003 | Long/Short/잔고부족 |
| 36 | TRAD | Order Execution | 주문 확인 모달 | SC-TRAD-EXEC | TRAD-CONF-001/002 | OrderConfirm |
| 37 | TRAD | Dashboard | Positions 탭 | SC-TRAD-DASH | TRAD-DASH-001 | |
| 38 | TRAD | Dashboard | Open Orders 탭 | SC-TRAD-DASH | TRAD-OPEN-001 | |
| 39 | TRAD | Dashboard | History 탭 | SC-TRAD-DASH | TRAD-HIST-001 | |
| 40 | TRAD | Dashboard | Portfolio 탭 | SC-TRAD-DASH | TRAD-PORT-001 | 미구현 안내 |
| 41 | TRAD | Position Card | PnL 색상 분기 | SC-TRAD-PSTN | TRAD-PNL-001/002 | 녹/빨 |
| 42 | TRAD | Position Card | 청산 확인 모달 | SC-TRAD-PSTN | TRAD-CLSE-001/002 | CloseConfirm |

### SGNL — Signal

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 현재 TC ID | 비고 |
|-----|--------|--------|--------|--------------|-----------|------|
| 43 | SGNL | Signal List | 헤더 및 성과 카드 | SC-SGNL-LIST | SGNL-HEAD-001, SGNL-SUMM-001, SGNL-CLRS-001 | |
| 44 | SGNL | Signal List | 필터 탭 | SC-SGNL-LIST | SGNL-FILT-001/002, SGNL-CLSD-001 | ALL/LONG/SHORT/ACTIVE/CLOSED |
| 45 | SGNL | Signal Execution | 바텀시트 | SC-SGNL-EXEC | SGNL-SHTS-001 | SignalOrderSheet |
| 46 | SGNL | Signal Execution | Execute 주문 | SC-SGNL-EXEC | SGNL-EXEC-001/002 | 즉시 실행·잔고 부족 |
| 47 | SGNL | Signal Execution | Modify 로드 | SC-SGNL-EXEC | SGNL-MODF-001 | OrderForm 연동 |

### MOBL — Mobile UI

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 현재 TC ID | 비고 |
|-----|--------|--------|--------|--------------|-----------|------|
| 48 | MOBL | Testnet Banner | 배너 노출 | SC-MOBL-TNBN | MOBL-TNBN-001/002 | 상시 고정 |
| 49 | MOBL | Testnet Banner | 배지·고지 문구 | SC-MOBL-TNBN | MOBL-TNBG-001 | |
| 50 | MOBL | Layout | 최대 너비 320px | SC-MOBL-LAYT | MOBL-LAYT-001 | |
| 51 | MOBL | Layout | Order Form 터치 | SC-MOBL-LAYT | MOBL-ORDF-001/002 | |
| 52 | MOBL | Layout | Dashboard 터치 | SC-MOBL-LAYT | MOBL-DASH-001 | |
| 53 | MOBL | Layout | Chart 반응형 | SC-MOBL-LAYT | MOBL-CHRT-001 | |
| 54 | MOBL | Layout | Coin Info Bar | SC-MOBL-LAYT | MOBL-COIN-001 | |
| 55 | MOBL | Bottom Navigation | 4탭 네비게이션 | SC-MOBL-BNAV | MOBL-BNAV-001/002 | |
| 56 | MOBL | Bottom Navigation | 콘텐츠 스크롤 | SC-MOBL-BNAV | MOBL-SCRL-001 | 64px 하단 여백 |
| 57 | MOBL | Theme & Style | 다크 테마 | SC-MOBL-THME | MOBL-DKTH-001 | #0a0a0a |
| 58 | MOBL | Theme & Style | CSS 변수 | SC-MOBL-THME | MOBL-CSSV-001 | |
| 59 | MOBL | Animation | 페이드인 | SC-MOBL-ANIM | MOBL-LDFN-001, MOBL-LGFN-001 | LandingPage·LoginPage |
| 60 | MOBL | Exchange Integration | Testnet API | SC-MOBL-EXCH | MOBL-EXCH-001, MOBL-HLAP-001 | HL Testnet |
| 61 | MOBL | Onboarding UI | CEX 안내 | SC-MOBL-ONBD | MOBL-ONCD-001 | ⚠️ 불확실: AUTH > Onboarding과 중복 가능성 |

### SETG — Settings

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 현재 TC ID | 비고 |
|-----|--------|--------|--------|--------------|-----------|------|
| 62 | SETG | Account | 이메일·지갑 주소 | SC-SETG-ACCT | SETG-ACCT-001 | |
| 63 | SETG | Account | 지갑 주소 복사 | SC-SETG-ACCT | SETG-WCPY-001 | Toast |
| 64 | SETG | Trading Preferences | TP/SL 설정값 표시 | SC-SETG-TPRF | SETG-TPSL-001/002 | |
| 65 | SETG | Trading Preferences | 토글 ON/OFF | SC-SETG-TPRF | SETG-TGTG-001/002 | |
| 66 | SETG | Exchange Connection | 연결 상태 표시 | SC-SETG-EXCO | SETG-EXCO-001 | |
| 67 | SETG | Account | Logout | SC-SETG-ACCT | SETG-LOUT-001/002 | 목업 Toast |
| 68 | SETG | Coach Mark | 단계별 가이드 | SC-SETG-COCH | SETG-COCH-001 | 최초 표시 |

### ROUT — Routing

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 현재 TC ID | 비고 |
|-----|--------|--------|--------|--------------|-----------|------|
| 69 | ROUT | Auth Guard | 미인증 접근 차단 | SC-ROUT-AUTH | ROUT-AUTH-001/002/003 | /trade, /onboarding, /terms |
| 70 | ROUT | Auth Guard | 이미 로그인 차단 | SC-ROUT-AUTH | ROUT-ALRD-001 | /login 재접근 [신규] |
| 71 | ROUT | Step Guard | 약관 미동의 차단 | SC-ROUT-STEP | ROUT-ONBD-001 | |
| 72 | ROUT | Step Guard | 온보딩 미완료 차단 | SC-ROUT-STEP | ROUT-TRAD-001 | |
| 73 | ROUT | Step Guard | 뒤로 가기 차단 | SC-ROUT-STEP | ROUT-BACK-001 | [신규] |
| 74 | ROUT | Navigation Flow | 가입 흐름 시퀀스 | SC-ROUT-FLOW | ROUT-SEQN-001 | |
| 75 | ROUT | Navigation Flow | 로그인 완료 자동이동 | SC-ROUT-FLOW | ROUT-LOGD-001 | |
| 76 | ROUT | Navigation Flow | 전역 상태 조합 분기 | SC-ROUT-FLOW | ROUT-STAT-001 | [신규] |

---

## ⚠️ 불확실 항목 목록 (반드시 확인 필요)

| No. | 항목 | 쟁점 | 선택지 |
|-----|------|------|--------|
| 1 | AUTH-GUARD-001/002 | 약관 완료 계정의 /terms 재접근 차단 — AUTH·Terms에 속하나 ROUT·Auth Guard와 동일 성격 | A) AUTH > Terms > 재접근 차단 / B) ROUT > Auth Guard로 이동 |
| 2 | LEVR-ORDR-001 | LeverageNotice 팝업과 AdjustLeverage 모달 노출 순서 — 별도 중분류가 필요한가 | A) LeverageNotice Popup 중분류 유지 / B) Leverage Policy 중분류로 통합 |
| 3 | MOBL-ONCD-001 | 온보딩 완료 화면 CEX 안내 문구 — AUTH > Onboarding과 내용 중복 가능성 | A) MOBL > Onboarding UI 유지 / B) AUTH > Onboarding으로 이동 |
| 4 | SETG vs TPSL | TP/SL 설정 관련 TC가 TPSL·SETG 두 도메인에 분산 — 분류표에서 SETG > Trading Preferences와 TPSL > Settings가 개념적으로 동일 | A) 현행 유지 (Settings 화면 = SETG, 기능 = TPSL) / B) TPSL로 통합 |

---

## TC ID 변환 규칙 (현재 → 신규)

신규 분류표 승인 후 TC ID를 아래 규칙으로 변환:

```
현재:  {도메인코드}-{기능코드}-{NNN}
        예: TPSL-MODL-001

신규:  SC-{대분류코드}-{중분류코드}-{NNN}
        예: SC-TPSL-MODL-001
```

> 현재 도메인코드와 대분류코드가 일치하므로, `SC-` 프리픽스 추가 + 중분류코드 재검토만 하면 됩니다.
> 실질적인 ID 변화는 최소화됩니다.

---

## 승인 후 작업 범위

승인 시 자동으로 진행:
1. tc_final.md TC ID → `SC-{대분류}-{중분류}-{NNN}` 형식 일괄 변환
2. Excel 컬럼 재구성: `도메인(1열)` → `대분류 | 중분류 | 소분류(3열)`
3. 표지 도메인 목록 업데이트

---

*이 파일을 편집 후 저장하여 승인 의사를 전달하세요.*
