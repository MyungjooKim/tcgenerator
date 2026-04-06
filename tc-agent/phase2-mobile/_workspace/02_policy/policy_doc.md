# 정책 문서 — Supercycl 모바일 체험

> 작성 일시: 2026-04-01
> 기준 문서: parsed_content.md

---

## [행사 개요 및 운영 구조]

### 정책 목표
- 2026.04.11 유스메타 협업 행사에서 1,000명 이상 유저가 Supercycl 모바일 체험을 성공적으로 수행할 수 있도록 한다.

### 핵심 정책 규칙
- 행사 형태: 임시 모바일 웹 (이벤트 후 폐기 처분)
- 거래소: Hyperliquid Testnet (실제 자금 없음)
- 대상: 유스메타 회원 중 선물 거래 이용자 1,000명 이상
- PC 시연과 모바일 체험은 별도 트랙으로 운영된다
  - PC 시연 (상용 환경): BingX, Binance, OKX API 연동 데모, 상용 Supercycl 웹 사용
  - 모바일 체험 (임시 버전): Hyperliquid Testnet 기반
- 가입 → 연동 → 거래까지 목표 소요시간: 2분 이내
- MetaMask 설치 불필요 (지갑 자동 생성 구조)

### 예외/제한 사항
- PC 시연(상용 환경)은 이 정책 문서의 적용 범위 외
- 임시 모바일 웹이므로 행사 종료 후 서비스 폐기

### 미결 사항 (확인 필요)
- 없음

---

## [인증 — 가입 및 로그인]

### 정책 목표
- Google OAuth 원클릭 가입으로 현장 가입률을 극대화하고 비기술 사용자도 즉시 체험을 시작할 수 있도록 한다.

### 핵심 정책 규칙
- 가입 수단: Google OAuth 단독 (이메일/비밀번호 방식 없음)
- 가입 플로우: QR 스캔 → Google 로그인 → 약관 동의 → 온보딩(자동 처리) → 트레이딩
- 라우트 흐름: `/` → `/login` → `/terms` → `/onboarding` → `/trade`
- 약관 동의 페이지(`/terms`)에서 체크박스 미동의 시 Accept 버튼 비활성화
- Decline 버튼 클릭 시 랜딩 페이지(`/`)로 이동
- 목업에서 Google OAuth는 시뮬레이션 처리 (실제 API 호출 없음)
- 전역 상태 `isLoggedIn`, `hasAcceptedTerms`, `hasCompletedOnboarding`으로 인증 흐름 관리

### 예외/제한 사항
- in-app 브라우저(카카오톡, 네이버 등) 비호환 가능성 있음 → 외부 브라우저 안내 필요
- iOS Safari, Android Chrome에서만 정식 지원

### 미결 사항 (확인 필요)
- Google OAuth 모바일 브라우저 호환성 검증 필요 (특히 iOS Safari, Android Chrome in-app 브라우저)

---

## [온보딩 — 지갑 자동 생성 및 자금 지급]

### 정책 목표
- 가입 직후 지갑 생성·Testnet 연결·테스트 자금 지급을 자동으로 처리하여 유저 마찰을 최소화한다.

### 핵심 정책 규칙
- 온보딩 3단계 자동 처리 (타이머 기반 시뮬레이션):
  - 단계 1: 지갑 자동 생성 (~1.2초 후 완료)
  - 단계 2: Testnet 연결 (~2.2초 후 완료)
  - 단계 3: 테스트 자금 로딩 (~3.2초 후 완료, completed=true)
- 완료 후: 체크마크 + USDC 잔액 표시 + CEX 통합 예정 안내 문구 + "Start Trading" 버튼 노출
- "Start Trading" 클릭 시 `COMPLETE_ONBOARDING` 디스패치 후 `/trade`로 이동
- 기본 계정 잔고: 1,000.0 USDC (ACCOUNT.balance 상수)
- 테스트 자금 지급 방식: 마스터 지갑 → 유저 지갑 mock USDC 전송 (실시간, 가입 즉시)
  - 전송 후 유저 화면 잔고 표시까지 ~10초 소요
- HL Testnet Faucet 제약: 지갑당 1회 1,000 mock USDC, 메인넷 $5 USDC 입금 이력 필요
  - 자동 생성 지갑은 메인넷 이력 없으므로 Faucet 직접 사용 불가 → 마스터 지갑 Transfer 방식 사용
- 마스터 지갑 사전 준비 일정:
  - D-7: 마스터 지갑 다수를 메인넷에서 활성화 ($5 USDC 입금)
  - D-5~3: 각 마스터 지갑에서 Testnet Faucet claim (1,000 USDC × N개)
  - 1,000명분 확보를 위해 마스터 지갑 1,000개 이상 필요

### 예외/제한 사항
- 1,000명 동시 가입 시 자금 전송 병목 발생 가능 → 마스터 지갑 다수 분산 처리 + 큐 시스템으로 대응
- 잔고 표시 지연 시 유저에게 안내 메시지 필요

### 미결 사항 (확인 필요)
- HL Testnet Faucet 주소당 1회 제한에 대해 Hyperliquid 측에 대량 claim 협의 가능 여부 확인 필요
- 자금 전송 실패 시 재시도 정책 및 에러 처리 방안 미정

---

## [레퍼럴 코드 자동 등록]

### 정책 목표
- 가입 시 유스메타 레퍼럴 코드를 자동 태깅하여 파트너 성과 지표를 확보한다.

### 핵심 정책 규칙
- 레퍼럴 코드: `PARTNER_CODE = "YOUTHMETA"` (상수 하드코딩)
- 등록 방식: 체험 URL에 `partner_code=YOUTHMETA` 파라미터 포함 → 가입 시 자동 태깅
- QR 코드에 레퍼럴 파라미터 포함 여부를 행사 당일 PM이 최종 확인
- 유스메타 측 핵심 성과 지표: 가입 건수 (레퍼럴 자동 등록 전제)
- 개발 우선순위: P1

### 예외/제한 사항
- URL 파라미터 누락 시 레퍼럴 미등록 가능성 있음

### 미결 사항 (확인 필요)
- 레퍼럴 코드 미포함 URL로 접속한 유저의 처리 방안 (수동 등록 가능 여부 등) 미정

---

## [레버리지 — 2배 고정 제한]

### 정책 목표
- 유저 보호 정책에 따라 YOUTHMETA 계정의 레버리지를 최대 2배로 제한하여 과도한 손실을 방지한다.

### 핵심 정책 규칙
- `MAX_LEVERAGE = 2` (하드코딩 상수)
- `MIN_LEVERAGE = 1` (하드코딩 상수)
- `DEFAULT_LEVERAGE = 2` (기본값)
- AdjustLeverage 모달 슬라이더 범위: 1~2 (step=1), 2배 초과 불가
- AdjustLeverage 모달 내 경고 배너 문구: "Max leverage limited to 2x (User Protection)" (--accent-yellow 색상)
- LeverageNotice 팝업 문구: "This account has a maximum leverage limit of 2x under the user protection policy."
- LeverageNotice 팝업 표시 조건: `hasSeenLeverageNotice=false`인 경우 TradingPage 진입 시 최초 1회만 표시
- "I Understand" 버튼 클릭 시 `DISMISS_LEVERAGE_NOTICE` 디스패치 → 재표시 없음
- TradingPage 진입 시 LeverageNotice 우선 노출 (AdjustLeverage 모달보다 선행)
- 개발 우선순위: P0

### 예외/제한 사항
- YOUTHMETA 파트너 계정에만 적용 (상용 계정과 구분 필요)
- 목업에서는 모든 계정에 동일 제한 적용

### 미결 사항 (확인 필요)
- 레버리지 안내 팝업 언어 (한국어/영어) 확인 필요

---

## [자동 TP/SL (Auto Take Profit / Stop Loss)]

### 정책 목표
- 주문 체결 시 사전 설정한 TP/SL이 자동 적용되어 유저가 별도 조작 없이 손익 관리를 체험할 수 있도록 한다.

### 핵심 정책 규칙
- `DEFAULT_TP_PERCENT = 1.8` (기본 익절 비율 %)
- `DEFAULT_SL_PERCENT = 5.0` (기본 손절 비율 %)
- Auto TP/SL 활성화 여부: `autoTpSlEnabled` 전역 상태로 관리
- TP/SL 값 저장: `takeProfitPercent`, `stopLossPercent` 전역 상태
- AutoTpSlModal 확인 버튼 활성화 조건: `tpNum > 0` OR `slNum > 0` 중 하나 이상 충족
- Auto TP/SL 인디케이터: OrderForm에서 `autoTpSlEnabled=true` 시 TP%/SL% 표시 + Edit 버튼
- Auto 배지: PositionCard에서 `isAuto=true`인 포지션에 녹색 Auto 배지 표시 (9px 폰트)
- PositionCard TP/SL 표시 조건: `position.tp` 또는 `position.sl` 값이 존재할 때만 렌더링
- SettingsPage 토글 스위치: ON=녹색, OFF=기본 배경, 클릭 시 `TOGGLE_AUTO_TP_SL` 디스패치
- 설정 경로: Settings 탭 → Trading Preferences 섹션 → Auto TP/SL Edit 버튼
- 개발 우선순위: P0

### 예외/제한 사항
- TP 또는 SL 중 하나만 설정 가능 (둘 다 0인 경우만 확인 버튼 비활성)
- Auto TP/SL이 OFF 상태에서도 수동으로 TP/SL 값을 보유할 수 있음

### 미결 사항 (확인 필요)
- Auto TP/SL 기본 상태 (초기 ON/OFF 여부) 확인 필요 — PDF에서 "확인 필요" 명시됨
- TP/SL 수치의 기본값 (DEFAULT_TP=1.8%, DEFAULT_SL=5.0%)이 최종 확정값인지 확인 필요

---

## [거래 — 주문 및 포지션]

### 정책 목표
- 무기한 선물 거래 체험 화면에서 Long/Short 주문을 실행하고 포지션을 확인할 수 있도록 한다.

### 핵심 정책 규칙
- 지원 코인: BTC-USDC, ETH-USDC, SOL-USDC, DOGE-USDC, ARB-USDC, AVAX-USDC, MATIC-USDC, LINK-USDC (총 8개)
- 주문 타입: limit | market | conditional (3종)
  - limit/conditional 주문: 가격 입력 필드 표시
  - market 주문: 가격 입력 필드 숨김
- 주문 실행: Long/Short 버튼 클릭 → `PLACE_ORDER` 디스패치 → Toast 알림
- OrderForm 크기 슬라이더 범위: 0~100%
- 시그널 연동: `prefillData`가 존재하면 OrderForm 초기값 자동 채움
- Dashboard 탭 구성: Positions | Open Orders | History
  - Open Orders, History 탭: 미구현 ("No open orders"/"No order history" 빈 상태)
- 포지션 카드 PnL 표시: 수익 ≥ 0 → 녹색, 손실 < 0 → 빨간색, 좌측 보더 색상도 동일 규칙 적용
- 거래 대상: BTC-USDC 무기한 선물 등 Hyperliquid Testnet 종목

### 예외/제한 사항
- portfolio 탭: 미구현 ("coming in the next version" 메시지 표시)
- 목업 환경이므로 실제 API 호출 없음

### 미결 사항 (확인 필요)
- Open Orders, History 탭은 이번 체험 범위에서 구현 여부 불명확

---

## [시그널 (YouthMeta Signals)]

### 정책 목표
- 유스메타 시그널을 제공하여 유저가 신호 기반으로 주문을 실행하거나 수정할 수 있도록 한다.

### 핵심 정책 규칙
- 시그널 탭 헤더: "⚡ YouthMeta Signals"
- 성과 요약 카드 (최근 30일): Hit/Miss/Expired 건수, 평균 PnL%, 성공률%
  - 성공률 색상: ≥70%=녹색, ≥50%=주황색, <50%=빨간색
- 필터 타입: ALL | LONG | SHORT | ACTIVE | CLOSED (가로 스크롤 지원)
- CLOSED 상태 집합: HIT_TP | HIT_SL | EXPIRED | CANCELLED
- SignalOrderSheet 바텀시트: 코인, 방향(Long/Short), 진입가, 타겟가, 손절가, 레버리지 표시
- 시그널 실행 방식:
  - Execute: 즉시 주문 실행 (`EXECUTE_SIGNAL_ORDER` 디스패치 + Toast)
  - Modify: 주문 폼에 신호값 로드 후 유저가 직접 수정 (`PREFILL_FROM_SIGNAL` 디스패치)

### 예외/제한 사항
- 목업 데이터 기반 (실제 신호 API 없음)

### 미결 사항 (확인 필요)
- 시그널 기능이 행사 당일 체험 플로우에 포함되는지 (P0/P1/P2 범위) 명확히 확인 필요
- 시그널 데이터 갱신 주기 및 실제 신호 연동 시점 미정

---

## [Testnet UI 및 CEX 연동 안내]

### 정책 목표
- 유저가 테스트넷 환경임을 명확히 인식하고, 향후 실거래 연동 가능성을 안내한다.

### 핵심 정책 규칙
- LandingPage 하단에 "TESTNET MODE" 배너 표시
- SettingsPage Exchange Connection 섹션: Hyperliquid 테스트넷 연결 상태 표시
- OnboardingPage 완료 화면: "CEX 통합 예정 안내 문구" 노출
- Testnet 표시: TESTNET 배지 + "실제 자금 아님" 고지 + "추후 CEX 연동 안내" 포함
- HL Testnet API 정보:
  - 베이스 URL: `api.hyperliquid-testnet.xyz` (메인넷: `api.hyperliquid.xyz`)
  - Chain ID: 998 (메인넷: 999)
- 개발 우선순위: P1

### 예외/제한 사항
- CEX 연동 안내는 PC 시연(상용 환경)에서 별도 진행되며, 임시 모바일 웹에서는 안내 문구만 표시

### 미결 사항 (확인 필요)
- CEX 연동 안내 문구 포함 여부 최종 확인 필요 (PDF에서 "확인 필요" 명시)

---

## [모바일 반응형 UI]

### 정책 목표
- 1,000명 이상 모바일 유저가 스마트폰에서 불편 없이 트레이딩 체험을 할 수 있도록 한다.

### 핵심 정책 규칙
- 최대 너비: 320px (모바일 최적화)
- 전체 높이: 100dvh
- Trading Page 모바일 레이아웃 + 터치 최적화 필요 구성요소: Order Form, Dashboard, Chart, Coin Info Bar
- 하단 고정 네비게이션 바 (BottomNav): 4개 탭 (trade / signal / portfolio / settings)
- 탭 컨텐츠 영역: 스크롤 가능, 하단 64px 여백 확보
- 배경색: #0a0a0a (다크 테마)
- CSS 변수 체계 사용: --color-pri-1, --text-secondary, --accent-green, --accent-red, --accent-yellow
- 페이드인 애니메이션: LandingPage(0.15s/0.3s/0.45s 순차), LoginPage(0.3s)
- 개발 우선순위: P0

### 예외/제한 사항
- 현재 상태: 웹 데스크탑 전용 → 모바일 레이아웃 신규 개발 필요

### 미결 사항 (확인 필요)
- 없음

---

## [온보딩 가이드 (Coach Mark)]

### 정책 목표
- 첫 접속 유저가 주요 기능을 직관적으로 파악할 수 있도록 단계별 가이드를 제공한다.

### 핵심 정책 규칙
- 첫 접속 시 단계별 Coach mark 표시
- 기능 하이라이트 포함
- 개발 우선순위: P2 (행사 필수 기능 완료 후 추가 구현)

### 예외/제한 사항
- P2 우선순위로 행사 일정 내 미구현 가능성 있음

### 미결 사항 (확인 필요)
- Coach mark 세부 내용 및 화면별 포인트 미정

---

## [설정 — SettingsPage]

### 정책 목표
- 계정 정보, 거래 환경 설정, 거래소 연결 상태를 한 곳에서 확인·수정할 수 있도록 한다.

### 핵심 정책 규칙
- Account 섹션: 이메일(ACCOUNT.email), 지갑 주소(ACCOUNT.wallet) + 복사 버튼
  - 복사 클릭 시 Toast "Address copied!" 표시
- Trading Preferences 섹션:
  - Auto TP/SL 현재 설정값(%) 표시 + Edit 버튼
  - Auto TP/SL 토글 스위치 (ON=녹색, OFF=기본색)
- Exchange Connection 섹션: Hyperliquid 테스트넷 연결 상태 표시
- Logout 섹션: 빨간색 테두리 버튼 (목업 Toast 메시지 표시)

### 예외/제한 사항
- 로그아웃 기능은 목업 처리 (실제 세션 종료 없음)

### 미결 사항 (확인 필요)
- 없음

---

## [리스크 및 운영 대응]

### 정책 목표
- 1,000명 이상 동시 접속/가입 상황에서도 서비스가 안정적으로 운영될 수 있도록 사전 대응 방안을 수립한다.

### 핵심 정책 규칙
- 동시 가입 병목 대응: 마스터 지갑 다수 분산 처리 + 큐 시스템, 잔고 표시 지연 안내
- HL Testnet Faucet 1회 제한 대응: 마스터 지갑 1,000개 이상 사전 준비
- HL Testnet 부하: 트래픽 여유 있으나 사전 부하 테스트 권장
- Google OAuth 모바일 호환: iOS Safari, Android Chrome 사전 테스트
- 체험 당일 체크리스트:
  1. HL Testnet API 상태 확인 (Dev) — api.hyperliquid-testnet.xyz 응답 정상 여부
  2. 마스터 지갑 잔고 1,000명분 이상 확인 (Dev)
  3. 체험 URL + QR 코드 레퍼럴 파라미터 포함 여부 확인 (PM)
  4. 모바일 접속 테스트 iOS/Android — Google OAuth + 자동 가입 풀 플로우 (QA)
  5. 2배 레버리지 + Auto TP/SL 동작 확인 — 안내 팝업, 레버리지 제한, TP/SL 자동 생성 (QA)
  6. 유스메타 측 최종 리허설 완료 확인 — 최문창 상무 테스트 완료 여부 (PM)
  7. 장애 대응 핫라인 + 실시간 모니터링 준비 — 자금 전송 실패, 서버 부하 등 즉시 대응 (Dev)
- 유스메타 측 사전 테스트 환경 제공 일정: 4/9 (최문창 상무 / 두찬실장 프로세스 직접 테스트)
- 소규모 리허설: 4/9~4/10, 10~20명 대상

### 예외/제한 사항
- Hyperliquid 측 대량 Faucet claim 협의 결과에 따라 마스터 지갑 준비 수량 조정 가능

### 미결 사항 (확인 필요)
- Hyperliquid 측에 대량 claim 협의 가능 여부 미확인
- in-app 브라우저 비호환 시 유저 안내 방법 미정

---

## [기술 스택 및 상수 요약]

### 정책 목표
- 개발 구현 시 참조해야 할 핵심 상수값과 기술 스택을 명시한다.

### 핵심 정책 규칙

**상수값 (defaults.ts):**
- `DEFAULT_TP_PERCENT = 1.8`
- `DEFAULT_SL_PERCENT = 5.0`
- `DEFAULT_LEVERAGE = 2`
- `MAX_LEVERAGE = 2`
- `MIN_LEVERAGE = 1`
- `PARTNER_CODE = "YOUTHMETA"`
- `ACCOUNT.balance = 1000.0 USDC`

**Testnet API:**
- 베이스 URL: `api.hyperliquid-testnet.xyz`
- Chain ID: 998

**기술 스택:**
- 프레임워크: React 19 + TypeScript + Vite
- 라우터: react-router-dom v7
- 상태 관리: React Context API (AppContext)
- 언어 구성: TypeScript 95.2%, CSS 3.7%

**라우트 구성:**
- `/` — LandingPage
- `/login` — LoginPage
- `/terms` — TermsPage
- `/onboarding` — OnboardingPage
- `/trade` — TradingPage

**전역 상태 주요 필드:**
- `isLoggedIn`, `hasAcceptedTerms`, `hasCompletedOnboarding`, `hasSeenLeverageNotice`
- `leverage`, `autoTpSlEnabled`, `takeProfitPercent`, `stopLossPercent`
- `selectedCoin`, `orderType`, `positions`, `activeTab`
- `signalState`, `prefillData`

### 예외/제한 사항
- DevNav 컴포넌트는 개발용 빠른 탐색 도구로, 프로덕션 배포 시 제거 필요

### 미결 사항 (확인 필요)
- 없음
