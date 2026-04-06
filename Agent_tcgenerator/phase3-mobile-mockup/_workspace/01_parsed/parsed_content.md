# Supercycl 모바일 목업 파싱 결과

## 파싱 일시
2026-04-03

## 소스
- https://5kyo.github.io/supercycl-mockup/
- https://github.com/5kyo/supercycl-mockup

---

## 사이트 개요

- **앱 유형**: 크립토 선물 트레이딩 모바일 목업 (360px, mobile-only)
- **환경**: 테스트넷 (Testnet) — 실제 자금 없음, Hyperliquid Testnet 연동
- **테마**: 다크 모드 (#050505 기반)
- **프레임워크**: React 19 + TypeScript + Vite + React Router DOM 7
- **상태 관리**: useReducer (AppContext)
- **라우팅 방식**: SPA (Single Page Application), basename `/supercycl-mockup`
- **다국어**: 영어(en) / 한국어(ko) 지원

---

## 사이트 구조

### 화면 목록
| 경로 | 화면명 | 설명 |
|------|--------|------|
| `/` | 랜딩 (Landing) | 앱 진입점, Google 로그인 CTA |
| `/login` | 로그인 (Login) | Google 계정 확인 및 로그인 |
| `/terms` | 약관 동의 (Terms) | 서비스 이용약관 및 개인정보처리방침 동의 |
| `/onboarding` | 온보딩 (Onboarding) | 자동화된 지갑 생성 및 초기 자금 입금 절차 |
| `/trade` (탭: trade) | 트레이딩 (Trading) | 캔들 차트, 주문폼, 오더북, 포지션/주문 대시보드 |
| `/trade` (탭: signal) | 시그널 (Signal) | AI 트레이딩 시그널 목록 및 원클릭 주문 실행 |
| `/trade` (탭: portfolio) | 포트폴리오 (Portfolio) | 전체 자산 요약, 보유 포지션, 최근 활동 |
| `/trade` (탭: settings) | 설정 (Settings) | 계정 정보, 거래 선호도, 언어, 거래소 연결, 앱 정보 |

### 모달/시트 목록 (화면 위 오버레이)
| 컴포넌트명 | 설명 | 진입 경로 |
|------------|------|----------|
| AdjustLeverage | 레버리지 조정 모달 | 트레이딩 화면 OrderForm의 레버리지 버튼 탭 |
| AutoTpSlModal | 자동 TP/SL 설정 모달 | 트레이딩 화면 또는 설정 화면의 Edit 버튼 |
| CoinSelector | 코인 선택 바텀시트 | 트레이딩 화면 상단의 코인 페어 탭 |
| SignalOrderSheet | 시그널 주문 확인 바텀시트 | 시그널 카드의 Execute 버튼 |
| Toast | 알림 토스트 | 주문 실행, 포지션 닫기, 복사 등 액션 후 |

---

## 화면별 상세 분석

### [랜딩] — `/`

**주요 UI 요소**
- Header 컴포넌트 (로고, Testnet 배지)
- PlasmaOrb (Three.js WebGL 3D 비주얼, 배경 중앙)
- 헤드카피: "Trade Different, Ride the Supercycl" (Supercycl은 녹색 #00de0b)
- CTA 버튼: "Continue with Google" (Google 아이콘 포함, 반투명 배경, 32px 라운드)
- 디스클레이머 텍스트: "Test environment. No real funds used." (녹색)

**사용자 액션**
- "Continue with Google" 버튼 탭 → `/login`으로 이동
- (별도 로그인 상태 체크 없음, 모든 사용자가 진입 가능)

**표시 데이터**
- 앱 로고 및 슬로건
- Testnet 환경 안내 문구

**조건부 동작**
- 없음 (무조건 로그인 페이지로 이동)

---

### [로그인] — `/login`

**주요 UI 요소**
- 배경 이미지 (landing-bg.png)
- Header 컴포넌트
- 헤드카피 (랜딩과 동일 문구, 반투명)
- 딤 레이어 (배경 탭 시 랜딩으로 복귀)
- 바텀 시트 (슬라이드업 애니메이션):
  - Supercycl 로고 아이콘
  - 타이틀: "Log in to Supercycl"
  - 계정 카드: 아바타(초록, "J") + 이름("John Doe") + 이메일(text123@gmail.com) + 드롭다운 화살표
  - CTA 버튼: "Continue as John Doe" (파란색 #0b34a4, 44px 높이)

**사용자 액션**
- "Continue as John Doe" 버튼 탭 → `LOGIN` 액션 디스패치 + `/terms`로 이동
- 딤 영역 탭 → `/`(랜딩)으로 뒤로 이동

**표시 데이터**
- 목업 계정 정보: 이름 "John Doe", 이메일 "text123@gmail.com"

**조건부 동작**
- 로그인 버튼 탭 → `isLoggedIn: true` 상태로 전환
- 배경 딤 탭 → 로그인 없이 랜딩 복귀

---

### [약관 동의] — `/terms`

**주요 UI 요소**
- Header 컴포넌트
- 타이틀: "Accept the Terms"
- PlasmaOrb (중앙 시각 요소)
- 체크박스 (원형, 미체크: 회색 테두리, 체크: 녹색 배경 + 체크마크)
- 동의 텍스트: "I agree to the [Terms of Service] and [Privacy Policy]"
  - Terms of Service 링크: https://supercycl.io/terms (새 탭)
  - Privacy Policy 링크: https://supercycl.io/policy (새 탭)
- Accept 버튼 (비활성: opacity 0.4 + cursor not-allowed / 활성: 불투명 + 클릭 가능)

**사용자 액션**
- 체크박스 탭 → 동의 상태 토글 (`agreed: boolean`)
- Terms of Service 링크 탭 → 외부 링크 새 탭 오픈
- Privacy Policy 링크 탭 → 외부 링크 새 탭 오픈
- Accept 버튼 탭 (동의 상태에서만) → `ACCEPT_TERMS` 디스패치 + `/onboarding`으로 이동

**표시 데이터**
- 약관 링크 2개

**조건부 동작**
- 체크박스 미체크 상태: Accept 버튼 비활성화 (opacity 0.4, cursor not-allowed)
- 체크박스 체크 상태: Accept 버튼 활성화, 클릭 가능

---

### [온보딩] — `/onboarding`

**주요 UI 요소**
- PlasmaOrb (완료 전: warm 색상 + 맥동 애니메이션 / 완료 후: green 색상 + 정지)
- 타이틀: "Setting up your trading account" → 완료 후 "You're all set!"
- 진행 단계 표시기 (3단계, 애니메이션 순차 진행):
  - Step 1: "Creating wallet"
  - Step 2: "Connecting to Hyperliquid"
  - Step 3: "Loading test funds"
  - 각 단계: 대기(회색 점) → 진행 중(녹색 스피너) → 완료(녹색 원형 체크)
- 완료 후 표시 (fadeIn + translateY 애니메이션):
  - 안내 텍스트: "Test funds of 100 USDC have been deposited."
  - 잔고 카드 (티켓 디자인): "Balance — 100,000 USDC" 표시
  - "Start Trading" 버튼

**사용자 액션**
- 온보딩은 자동 진행 (유저 입력 불필요, 타이머 기반):
  - 0ms: Step 1 시작
  - 1200ms: Step 2 시작
  - 2200ms: Step 3 시작
  - 3200ms: 완료 + `COMPLETE_ONBOARDING` 디스패치
- "Start Trading" 버튼 탭 (완료 후만) → `/trade`로 이동

**표시 데이터**
- 초기 입금 잔고: 100,000 USDC (ACCOUNT.balance: 100.0 → 표시상 100,000)
- 단계별 진행 상황

**조건부 동작**
- 완료 전: "Start Trading" 버튼 불가시(opacity 0, pointer-events none)
- 완료 후: 잔고 카드 + "Start Trading" 버튼 fadeIn 표시

---

### [트레이딩] — `/trade` (탭: trade)

**주요 UI 요소**

**A. 상단 영역**
- Header 컴포넌트 (로고, Testnet 배지)
- CoinInfoBar:
  - 코인 페어 선택 버튼: `{coin.pair}` + 드롭다운 화살표 (탭 시 CoinSelector 모달)
  - 현재 가격: 숫자 (예: `94,677`)
  - 24시간 변동률: 색상 코드 (양수: 녹색 / 음수: 빨강)

**B. 차트 영역**
- Chart 컴포넌트: 캔들차트 이미지 (chart-candle.png 정적 이미지)

**C. 주문폼 (OrderForm) + 오더북 (Orderbook) — 좌우 분할 레이아웃**

OrderForm (좌측, 170px 고정):
- 주문 유형 드롭다운: Market / Limit (현재 선택 표시)
- Isolated 표시 + 레버리지 버튼: `{leverage}x` + 화살표 (탭 시 AdjustLeverage 모달)
- 가격 입력 (Limit 주문 시만 표시): "Price (USDC)" 라벨 + 숫자 입력
- 수량 입력: 숫자 + 코인 심볼 (녹색)
- 수량 슬라이더: 0% ~ 100%, 5개 도트(0/25/50/75/100%)
- Buy/Long 버튼 (녹색 #00de0b)
- Sell/Short 버튼 (빨강 #ff5938)

Orderbook (우측):
- "Price" / "Size" 헤더
- 매도 호가 목록 (빨간색 텍스트)
- 중간 현재가 표시
- 매수 호가 목록 (녹색 텍스트)

**D. Dashboard (하단)**
- 탭 바: "Positions ({n})" / "Open Order ({n})"
- Positions 탭:
  - PositionCard 목록 (포지션별):
    - 좌측 컬러 바 (Long: 녹색 / Short: 빨강)
    - 코인명 + Side · Leverage × · Isolated
    - Entry 가격
    - PnL 금액 + PnL 퍼센트 (색상: 수익 녹색 / 손실 빨강)
    - 포지션 크기 (수량 + 코인 단위)
    - Auto TP/SL 표시: "Auto" 배지 + TP 가격(녹색) + SL 가격(빨강)
    - Close 버튼
  - 빈 상태: "No open positions"
- Open Order 탭:
  - 주문 카드 (주문별):
    - 좌측 컬러 바 (Long/Short)
    - 코인명 + Side · Leverage × · Limit
    - Price / Size 정보
    - Cancel 버튼
  - 빈 상태: "No open orders"

**사용자 액션**
- 코인 페어 탭 → CoinSelector 바텀시트 오픈
- 레버리지 버튼 탭 → AdjustLeverage 모달 오픈
- 주문 유형 드롭다운 탭 → Market / Limit 선택
- Price 입력 (Limit 주문 시) → 지정가 직접 입력
- 수량 입력 / 슬라이더 조작 → 주문 수량 설정
- "Buy / Long" 버튼 탭 → `PLACE_ORDER(side: Long)` 디스패치 + 포지션 생성 + Toast 표시
- "Sell / Short" 버튼 탭 → `PLACE_ORDER(side: Short)` 디스패치 + 포지션 생성 + Toast 표시
- Dashboard "Positions" / "Open Order" 탭 전환
- PositionCard "Close" 버튼 탭 → `CLOSE_POSITION` 디스패치 + "Position closed" Toast
- 주문 카드 "Cancel" 버튼 탭 → `CANCEL_ORDER` 디스패치 + "Order cancelled" Toast

**표시 데이터**
- 지원 코인: BTC-USDC (기본), ETH-USDC, SOL-USDC, XRP-USDC
- 기본 레버리지: 2x (최소 1x, 최대 2x)
- 기본 주문 유형: Market
- 포지션 정보: 코인, 방향, 레버리지, 수량, 증거금, 진입가, 마크가, 청산가, PnL, TP/SL
- 미체결 주문 정보: 코인, 방향, 레버리지, 지정가, 수량

**조건부 동작**
- 주문 유형 = Limit: 가격 입력 필드 표시
- 주문 유형 = Market: 가격 입력 필드 숨김
- Signal에서 prefill 진입 시: 가격 필드에 시그널 진입가 자동 입력, 주문 유형 Limit 전환
- Auto TP/SL 활성 상태에서 주문 시: 포지션 생성 시 TP/SL 자동 설정
- Open Order 탭: 미체결 주문 수 > 0이면 노란색 배지 표시
- Positions 탭: 포지션 수 > 0이면 녹색 배지 표시

---

### [모달: 레버리지 조정] — AdjustLeverage Modal

**주요 UI 요소**
- 모달 타이틀: "Adjust Leverage"
- 서브텍스트: `{coin.symbol}USDT Perp | Isolated`
- 경고 배너: "Max leverage limited to 2x (User Protection)" (녹색 테두리)
- 현재 레버리지 표시: `{n}x` (박스 형태)
- 슬라이더: 1x ~ 2x (1 단위 증분)
- 범위 표시: "1x" (좌) / "2x" (우)
- Cancel 버튼 (Secondary) / Confirm 버튼

**사용자 액션**
- 슬라이더 조작 → 레버리지 값 변경 (1~2x)
- Confirm 탭 → `SET_LEVERAGE` 디스패치 + 모달 닫기
- Cancel 탭 → 모달 닫기 (변경 불저장)

**조건부 동작**
- 레버리지 범위: MIN_LEVERAGE(1) ~ MAX_LEVERAGE(2)로 제한

---

### [모달: 자동 TP/SL 설정] — AutoTpSlModal

**주요 UI 요소**
- 모달 타이틀: "Auto TP/SL Settings"
- Take Profit 입력 필드: 퍼센트(%) 입력, 현재값 기본 표시
- Stop Loss 입력 필드: 퍼센트(%) 입력, 현재값 기본 표시
- 안내 문구: "Settings apply to new orders only. Existing positions will not be affected."
- Cancel 버튼 / Confirm 버튼 (TP 또는 SL 값 > 0일 때만 활성)

**사용자 액션**
- TP 퍼센트 입력 → takeProfitPercent 임시 변경
- SL 퍼센트 입력 → stopLossPercent 임시 변경
- Confirm 탭 → `UPDATE_TP_SL` 디스패치 (autoTpSlEnabled: true로 전환) + 모달 닫기
- Cancel 탭 → 모달 닫기

**표시 데이터**
- 기본값: TP 1.8%, SL 5.0%

**조건부 동작**
- TP + SL 모두 0이면 Confirm 버튼 비활성화

---

### [바텀시트: 코인 선택] — CoinSelector

**주요 UI 요소**
- 바텀시트 타이틀: "Select Coin"
- 검색 입력 필드: "Search coins..." placeholder
- 코인 목록 (필터링 결과):
  - 코인 페어명 + 현재 선택 시 별표(★) 표시
  - 현재 가격
  - 24시간 변동률 (양수: 녹색 / 음수: 빨강)
  - 선택된 코인: 배경 하이라이트

**지원 코인 목록**
| 심볼 | 페어 | 가격 | 24h 변동 | 거래량 |
|------|------|------|----------|--------|
| BTC | BTC-USDC | $94,677 | -7.2% | 1.2B |
| ETH | ETH-USDC | $2,015 | +2.1% | 580M |
| SOL | SOL-USDC | $148.5 | -3.4% | 320M |
| XRP | XRP-USDC | $2.83 | +1.2% | 210M |

**사용자 액션**
- 검색 입력 → 심볼/페어명 기반 실시간 필터링
- 코인 행 탭 → `SELECT_COIN` 디스패치 + 바텀시트 닫기

---

### [시그널] — `/trade` (탭: signal)

**주요 UI 요소**
- 퍼포먼스 요약 (최근 30일):
  - Hit / Miss / Expired 카운트 (각 색상: 녹색/빨강/회색)
  - Avg PnL: +1.82% (녹색)
  - Hit Rate: 71.9% (녹색)
- 필터 탭바: All / Long / Short / Active / Closed (활성 탭에 흰색 하단 바)
- 시그널 카드 목록 (SignalCard):
  - 코인 페어 + 방향 배지 (LONG: 녹색 / SHORT: 빨강)
  - Confidence 배지: HIGH / MEDIUM / LOW
  - Status 배지: ACTIVE / HIT TP / HIT SL / EXPIRED / CANCELLED
  - 진입가 (Entry)
  - TP 가격 (녹색) + TP 퍼센트
  - SL 가격 (빨강) + SL 퍼센트
  - 레버리지
  - AI 분석 근거 텍스트 (reasoning)
  - 타임스탬프 (상대적 시간: n분/h/d ago)
  - ACTIVE 상태: "Execute" 버튼
  - 종료 상태(HIT_TP/HIT_SL/EXPIRED): PnL 결과 표시

**목업 시그널 데이터**
| ID | 코인 | 방향 | 진입가 | TP | SL | 레버리지 | 신뢰도 | 상태 |
|----|------|------|--------|----|----|---------|--------|------|
| sig-001 | BTC | LONG | $94,200 | $96,800 | $92,500 | 2x | HIGH | ACTIVE |
| sig-002 | SOL | SHORT | $178.5 | $170.0 | $183.0 | 2x | MEDIUM | ACTIVE |
| sig-003 | ETH | LONG | $2,650 | $2,720 | $2,610 | 2x | HIGH | HIT_TP (+2.64%) |
| sig-004 | XRP | SHORT | $2.85 | $2.65 | $2.95 | 2x | LOW | HIT_SL (-3.51%) |

**사용자 액션**
- 필터 탭 선택 → `SET_SIGNAL_FILTER` 디스패치 + 목록 필터링
- "Execute" 버튼 탭 (ACTIVE 시그널) → SignalOrderSheet 바텀시트 오픈
- 시그널 탭 진입 시 → `MARK_SIGNALS_READ` 디스패치 (미읽음 카운트 0으로)

**조건부 동작**
- ACTIVE 상태: Execute 버튼 표시
- 종료 상태(HIT_TP/HIT_SL/EXPIRED/CANCELLED): PnL 결과 표시, Execute 버튼 없음
- 필터 결과 없음: "No signals matching this filter" 빈 상태 표시
- BottomNav Signal 아이콘: 미읽음 수 > 0이면 배지 표시

---

### [바텀시트: 시그널 주문 확인] — SignalOrderSheet

**주요 UI 요소**
- 바텀시트 타이틀: "Signal Order Confirm"
- 시그널 요약: 코인 페어 + LONG/SHORT 배지
- 주문 세부 정보 카드:
  - Order Type 선택: Market / Limit 토글 버튼
  - Entry Price: 시그널 진입가
  - Margin: USDC 기반 수량 (기본: ACCOUNT.balance 전액)
  - Leverage: 시그널 레버리지 (편집 가능)
  - TP 가격 + 퍼센트 (녹색)
  - SL 가격 + 퍼센트 (빨강)
- Modify 버튼 (편집 모드 전환)
- Execute Order 버튼 (Long: 녹색 / Short: 빨강)

**편집 모드 (Modify 탭 후)**
- Margin 필드: 직접 입력 가능 (USDC 금액)
- Leverage: - / + 버튼으로 1~2x 조정

**사용자 액션**
- Order Type 선택 → Market / Limit 전환
- Modify 버튼 탭 → 편집 모드 ON/OFF 토글
- Margin 입력 (편집 모드) → 증거금 변경
- Leverage 조정 (편집 모드) → 1~2x 변경
- Execute Order 버튼 탭 → `EXECUTE_SIGNAL_ORDER` 디스패치 + Toast("Order executed from signal") + 트레이딩 탭으로 전환
- (코드 상 Modify 버튼의 onModify는 `PREFILL_FROM_SIGNAL` 디스패치 후 트레이딩 탭 이동으로 연결)

**조건부 동작**
- LONG 시그널: Execute 버튼 녹색
- SHORT 시그널: Execute 버튼 빨강
- Market 주문: 즉시 포지션 생성
- Limit 주문: 미체결 주문으로 등록

---

### [포트폴리오] — `/trade` (탭: portfolio)

**주요 UI 요소**
- 총 잔고 카드: "Total Balance" → `${ totalBalance }` + PnL 금액 및 퍼센트 (색상: 수익/손실)
- 가용 잔고 카드: "Available" → `${ available }`
- 증거금 사용 카드: "Margin Used" → `${ totalMargin }`
- 보유 포지션 카드 "Open Positions ({n})":
  - 포지션별 행: 컬러 바 + 코인명 + Side · Leverage + PnL
  - 빈 상태: "No open positions"
- 최근 활동 카드 "Recent Activity":
  - 목업 항목: "Opened XRPUSDT Short · 2x" (2h ago), "Opened BTCUSDT Long · 2x" (3h ago), "Deposited 100 USDC" (5h ago)

**표시 데이터**
- totalBalance = ACCOUNT.balance (100 USDC) + 전체 포지션 PnL 합계
- available = ACCOUNT.balance - 전체 증거금 합계
- totalMargin = 전체 포지션 margin 합계
- pnlPercent = totalPnl / ACCOUNT.balance × 100 (반올림 소수점 2자리)

**조건부 동작**
- PnL > 0: 녹색 (#00de0b)
- PnL < 0: 빨강 (#ff5938)
- 포지션 없음: "No open positions" 표시

---

### [설정] — `/trade` (탭: settings)

**주요 UI 요소**

**섹션 1: Account**
- 이메일: `user@gmail.com`
- 지갑 주소: `0x9834...9948` (모노스페이스 폰트) + Copy 버튼

**섹션 2: Trading Preferences**
- "Auto TP/SL" 레이블 + Edit 버튼
- 현재 설정 표시: `TP: +{n}% | SL: -{n}%`
- 토글 스위치: Auto TP/SL ON/OFF

**섹션 3: Language**
- English / 한국어 선택 버튼 (활성: 녹색 배경, 비활성: 어두운 배경)

**섹션 4: Exchange Connection**
- Hyperliquid (Testnet): "Connected ✓" (녹색)
- Coming Soon 거래소: Binance, BingX, OKX, Bybit

**섹션 5: About**
- "Supercycl Website" 링크 → https://supercycl.io/ (새 탭)
- "Docs" 링크 → https://supercycl.gitbook.io/supercycl-docs-1 (새 탭)

**하단: Logout 버튼** (빨간 테두리, 투명 배경)

**사용자 액션**
- Copy 버튼 탭 → Toast("Address copied!")
- Edit 버튼 탭 → AutoTpSlModal 오픈
- Auto TP/SL 토글 → `TOGGLE_AUTO_TP_SL` 디스패치
- English / 한국어 선택 → `SET_LANGUAGE` 디스패치 + localStorage 저장
- Supercycl Website 링크 탭 → 외부 링크 새 탭
- Docs 링크 탭 → 외부 링크 새 탭
- Logout 버튼 탭 → Toast("Logged out (mockup)") (실제 로그아웃 없음)

**조건부 동작**
- 언어 설정: localStorage 기반 유지 (앱 재시작 시 복원)
- Auto TP/SL 토글 ON: 이후 생성 주문에 TP/SL 자동 적용

---

### [공통 컴포넌트]

#### BottomNav (하단 탭 네비게이션)
- 탭 구성: Trade / Signal / Portfolio / Settings
- 활성 탭: 아이콘 + 라벨 흰색, 비활성: 회색
- Signal 탭: 미읽음 시그널 수 배지 표시 (unreadCount > 0)
- 탭 전환 시 Signal 탭: `MARK_SIGNALS_READ` 자동 호출

#### Header
- 좌측: Supercycl 로고 (로고 아이콘 + 텍스트 SVG)
- 우측: "Testnet" 배지

#### Toast
- 화면 하단 오버레이 알림
- 자동 사라짐 (`HIDE_TOAST` 자동 디스패치)
- 트리거 상황: 주문 실행, 포지션 닫기, 주문 취소, 주소 복사, 로그아웃 등

---

## 앱 전역 상태 (AppContext 요약)

| 상태 키 | 타입 | 초기값 | 설명 |
|---------|------|--------|------|
| isLoggedIn | boolean | false | 로그인 여부 |
| hasAcceptedTerms | boolean | false | 약관 동의 여부 |
| hasCompletedOnboarding | boolean | false | 온보딩 완료 여부 |
| hasSeenLeverageNotice | boolean | false | 레버리지 안내 확인 여부 |
| selectedCoin | Coin | BTC-USDC | 선택된 코인 |
| leverage | number | 2 | 현재 레버리지 (1~2) |
| orderType | string | "market" | 주문 유형 (limit/market/conditional) |
| autoTpSlEnabled | boolean | true | 자동 TP/SL 활성 여부 |
| takeProfitPercent | number | 1.8 | TP 퍼센트 |
| stopLossPercent | number | 5.0 | SL 퍼센트 |
| positions | Position[] | DEFAULT_POSITIONS | 보유 포지션 목록 (초기 2개: XRP Short, BTC Long) |
| openOrders | OpenOrder[] | [] | 미체결 주문 목록 |
| activeTab | TabKey | "trade" | 현재 활성 탭 |
| toastMessage | string\|null | null | 토스트 메시지 |
| signalState | SignalState | INITIAL_SIGNAL_STATE | 시그널 상태 (목록, 필터, 미읽음 수) |
| prefillData | SignalPrefill\|null | null | 시그널 → 주문폼 자동 채우기 데이터 |
| language | Language | "en" | 언어 설정 (localStorage 기반) |

---

## 사용자 플로우 전체 요약

```
랜딩 (/)
  └─ "Continue with Google" 탭
     ↓
로그인 (/login)
  └─ "Continue as John Doe" 탭 → [LOGIN 상태 전환]
     ↓
약관 동의 (/terms)
  └─ 체크박스 체크 → Accept 탭 → [ACCEPT_TERMS 상태 전환]
     ↓
온보딩 (/onboarding)
  └─ 자동 진행 (3단계, 3.2초) → [COMPLETE_ONBOARDING 상태 전환]
  └─ "Start Trading" 탭
     ↓
트레이딩 메인 (/trade)
  ├─ Trade 탭 (기본)
  │   ├─ 코인 선택 → CoinSelector
  │   ├─ 레버리지 조정 → AdjustLeverage Modal
  │   ├─ TP/SL 설정 → AutoTpSlModal
  │   ├─ Market/Limit 주문 실행 → 포지션 생성 또는 미체결 주문 등록
  │   ├─ 포지션 Close → 포지션 제거
  │   └─ 주문 Cancel → 미체결 주문 제거
  │
  ├─ Signal 탭
  │   ├─ 필터 선택 (All/Long/Short/Active/Closed)
  │   └─ Execute → SignalOrderSheet
  │       ├─ Market/Limit 선택
  │       ├─ Margin/Leverage 편집 (Modify 모드)
  │       └─ Execute Order → 포지션/주문 생성 + Trade 탭 이동
  │
  ├─ Portfolio 탭
  │   └─ 잔고/포지션/활동 조회 (읽기 전용)
  │
  └─ Settings 탭
      ├─ 지갑 주소 복사
      ├─ Auto TP/SL 토글 및 편집
      ├─ 언어 변경 (EN/KO)
      └─ Logout (목업, 실제 동작 없음)
```
