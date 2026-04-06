# Parsed Content — Supercycl

> 파싱 일시: 2026-04-01
> 처리 파일: PDF 1개, GitHub 리포 1개

---

## [Supercycl] 모바일 체험 시나리오.pdf

### 슬라이드 1 / 표지

**Supercycl 모바일 체험 시나리오**
4/11 유스메타 협업 행사 · 임시 모바일 웹

| 항목 | 내용 |
|------|------|
| 일시 | 2026.04.11 |
| 대상 | 유스메타 회원 : 선물 거래 이용자 1,000명+ |
| 거래소 | Hyperliquid Testnet |
| 형태 | 임시 모바일 웹 (이벤트 후 폐기) |
| 파트너 | 유스메타 (두찬실장 / 최문창 상무) |

---

### 슬라이드 2 / 01 행사 구조

4/11 행사에서 유스메타 측(최문창 상무)이 Supercycl 협업을 발표하고 시연합니다.
PC 시연과 모바일 체험은 별도 트랙으로 운영됩니다.

**PC 시연 (상용 환경)** — 최문창 상무 발표용
- 상용 Supercycl 웹 사용
- CEX 다중 연동 및 실제 거래 시연
- BingX, Binance, OKX API 연동 데모
- 노트북 지참 유저: 직접 API 연동 체험 가능

**모바일 체험 (임시 버전)** — 1,000명+ 유저 체험용
- 임시 모바일 웹 (이벤트 후 폐기 처분)
- Hyperliquid Testnet 기반 (실제 자금 X)
- 가입 시 지갑 자동 생성 + 테스트 자금 자동 지급
- 가입 시 유스메타 레퍼럴 코드 자동 등록

✓ 지갑 자동 생성 구조: 유저는 Google 로그인만 하면 지갑 + 자금 + HL 연결이 전부 자동 처리됩니다. MetaMask 불필요.

---

### 슬라이드 3 / 02 유스메타 측 요구사항

| 구분 | 항목 | 내용 |
|------|------|------|
| 필수 | 가입 → 연동 → 거래 풀 플로우 | 발표 중 QR 코드 공유, 현장에서 바로 가입~거래 체험. 오프라인 행사에서 직접 가입시켜 가입률 극대화. |
| 필수 | 2배 레버리지 고정 체험 | 유저 보호 정책에 따른 최대 레버리지 2배 제한. Adjust Leverage 모달에서 2배 초과 불가 UI 포함. |
| 필수 | 자동 TP/SL 기능 체험 | 사전 설정한 TP/SL(%)이 주문 체결 시 자동 적용. Settings → 주문 → 포지션 Dashboard 확인 플로우. |
| 필수 | 유스메타 레퍼럴 코드 등록 | 임시 버전이라도 가입 시 partner_code=YOUTHMETA 자동 태깅. 가입 자체가 유스메타 측 핵심 성과 지표. |
| 희망 | 사전 테스트 시간 확보 | 최문창 상무 포함 유스메타 측이 행사 전 프로세스를 직접 테스트. 최소 D-2~3 테스트 환경 제공 필요. |
| 참고 | PC 유저 대상 CEX API 연동 시연 | 노트북 지참 유저에게 BingX, Binance, OKX 등 실제 API 연동 시연. 상용 PC 버전에서 별도 진행. |

확인 필요: Auto TP/SL 기본 상태(ON/OFF 및 Default 수치) | 레버리지 안내 팝업 언어 | CEX 연동 안내 문구 포함 여부

---

### 슬라이드 4 / 03 유저 체험 플로우

가입부터 첫 거래까지 목표 소요시간: 2분 이내. 지갑 자동 생성 구조로 MetaMask 설치 불필요.

| 단계 | 화면/기능 | 담당 | 내용 |
|------|-----------|------|------|
| 1 | QR 코드 스캔 | USER | 발표 중 QR 스캔 → 체험 URL 접속 / 레퍼럴 코드 자동 포함 |
| 2 | Google 로그인 | USER | Google OAuth 원클릭 가입 / 약관 동의 → 계정 생성 |
| 3 | 지갑 + HL 자동 연결 | AUTO | 지갑 자동 생성 + Testnet 연결 / 테스트 자금(mock USDC) 자동 지급 |
| 4 | 2배 레버리지 안내 | AUTO | 최초 로그인 시 안내 팝업 노출 / "최대 레버리지 2배 제한" 고지 |
| 5 | Auto TP/SL 설정 | USER | TP: +1.8%, SL: -5.0% 등 설정 / Order Form에서 ON 확인 |
| 6 | 선물 거래 체험 | USER | BTC-USDC 등 무기한 선물 거래 / 2배 제한 + 자동 TP/SL 확인 |

타임라인: QR 스캔 (5초) → Google 로그인 (20초) → 자동 처리 → 안내 확인 (5초) → TP/SL 설정 (30초) → 거래 시작

---

### 슬라이드 5 / 04 테스트넷 자금 처리 방안

⚠ HL Testnet Faucet 제약: 지갑당 1회 1,000 mock USDC 지급. 단, 해당 지갑이 메인넷에서 최소 $5 USDC 입금 이력 필요.
자동 생성 지갑은 메인넷 이력이 없으므로 Faucet 직접 사용 불가 → 마스터 지갑에서 Transfer 방식 권장.

**권장 방식: 마스터 지갑 → 유저 지갑 Transfer**

| 단계 | 내용 | 시점 |
|------|------|------|
| 1 | 마스터 지갑 다수를 메인넷에서 활성화 ($5 USDC 입금) | 사전 준비 (D-7) |
| 2 | 각 마스터 지갑에서 Testnet Faucet claim (1,000 USDC × N개) | 사전 준비 (D-5~3) |
| 3 | 유저 가입 시 자동 생성된 지갑으로 mock USDC 자동 전송 | 실시간 (가입 즉시) |
| 4 | 유저 화면에 잔고 표시 → 거래 시작 가능 | 전송 후 ~10초 |

Faucet claim은 주소당 1회(1,000 USDC). 유저 1,000명분 확보를 위해 마스터 지갑 1,000개+ 사전 준비 필요.
대안: Hyperliquid 측에 대량 claim 협의 가능 여부 확인.

---

### 슬라이드 6 / 05 기술 요구사항

| 항목 | 현재 상태 | 필요 작업 |
|------|-----------|-----------|
| 모바일 반응형 UI | 웹 데스크탑 전용 | Trading Page 모바일 레이아웃 + 터치 최적화 |
| HL Testnet 분기 | 메인넷만 연동 | API 엔드포인트 분기 (api.hyperliquid-testnet.xyz) / Chain ID 998 |
| 지갑 자동 생성 + 자금 지급 | 지갑 자동 생성 구현됨 | 가입 시 마스터 지갑에서 testnet USDC 자동 전송 추가 |
| 레버리지 2배 고정 | 기획 완료 | YOUTHMETA 계정에 2배 제한 + 안내 팝업 + 모달 제한 UI |
| 자동 TP/SL | 기획 완료 | 설정 모달, Order Form 인디케이터, 자동 생성, Auto 배지 |
| 레퍼럴 코드 등록 | 구조 존재 | 체험 URL에 partner_code 포함 → 가입 시 자동 태깅 |
| Testnet 모드 표시 | 없음 | "TESTNET" 배지 + 실제 자금 아님 고지 + CEX 연동 안내 |

HL Testnet API는 메인넷과 구조 동일. 베이스 URL만 변경: api.hyperliquid.xyz → api.hyperliquid-testnet.xyz / Chain ID 999 → 998

---

### 슬라이드 7 / 06 개발 태스크 및 우선순위

| 우선순위 | 태스크 | 세부 내용 |
|----------|--------|-----------|
| P0 | 모바일 반응형 Trading Page | Order Form, Dashboard, Chart, Coin Info 모바일 레이아웃 |
| P0 | HL Testnet 분기 + 자동 연결 | 가입 시 HL Testnet 자동 연결. 거래소 선택 단계 생략 |
| P0 | 테스트넷 자금 자동 지급 | 마스터 지갑 → 유저 지갑 mock USDC 자동 전송 |
| P0 | 레버리지 2배 고정 기능 | YOUTHMETA 계정 제한, 안내 팝업, Adjust Leverage 모달 |
| P0 | 자동 TP/SL 기능 | 설정 모달, 주문 체결 시 자동 생성, Dashboard Auto 배지 |
| P1 | 레퍼럴 코드 자동 등록 | URL 파라미터 → 가입 시 partner_code=YOUTHMETA 태깅 |
| P1 | Testnet UI + CEX 연동 안내 | TESTNET 배너, 실제 자금 아님 고지, 추후 CEX 연동 안내 |
| P2 | 체험 온보딩 가이드 | 첫 접속 시 단계별 Coach mark, 기능 하이라이트 |

---

### 슬라이드 8 / 07 일정

| 기간 | 내용 | 세부 |
|------|------|------|
| 3/31 ~ 4/2 | 모바일 반응형 + HL Testnet 분기 + 자금 자동화 | Trading Page 모바일 대응, API 분기, 지갑+자금 로직 |
| 4/3 ~ 4/5 | 2배 레버리지 고정 + 자동 TP/SL 구현 | 유스메타 파트너 기능: 레버리지 제한 UI, Auto TP/SL |
| 4/6 ~ 4/7 | 레퍼럴 코드 + Testnet UI + 통합 | 레퍼럴 자동 등록, 테스트넷 표시, 전체 통합 테스트 |
| 4/9 | 유스메타 측 테스트 환경 제공 | 최문창 상무 / 두찬실장님 프로세스 직접 테스트 + 자료 준비 |
| 4/9 ~ 4/10 | 버그 수정 + 리허설 | QA 이슈 대응, 소규모(10~20명) 리허설, 최종 점검 |
| 4/11 | 체험 행사 당일 | 1,000명+ 대상 모바일 체험 진행 |

---

### 슬라이드 9 / 08 리스크 및 대응방안

| 리스크 | 영향도 | 대응방안 |
|--------|--------|----------|
| 1,000명 동시 가입 시 자금 전송 병목 | 높음 | 마스터 지갑 다수 분산 처리 + 큐 시스템. 잔고 표시 지연 안내. |
| HL Testnet Faucet 주소당 1회 제한 | 높음 | 마스터 지갑 1,000개+ 사전 준비. HL측 대량 claim 협의. |
| 1,000명 동시 접속 시 HL Testnet 부하 | 중간 | 테스트넷은 트래픽 여유 있음. 사전 부하 테스트 권장. |
| Google OAuth 모바일 브라우저 호환 | 중간 | iOS Safari, Android Chrome 사전 테스트. in-app 브라우저 비호환 시 안내. |
| 레버리지 2배 / Auto TP/SL 개발 일정 | 중간 | 기획 완료 상태. 테스트넷 환경에서 기능 범위 최소화 대응. |

---

### 슬라이드 10 / 09 체험 당일 체크리스트

| # | 항목 | 담당 | 비고 |
|---|------|------|------|
| 1 | HL Testnet API 상태 확인 | Dev | api.hyperliquid-testnet.xyz 응답 정상 여부 |
| 2 | 마스터 지갑 잔고 확인 (mock USDC) | Dev | 1,000명분 이상 확보 확인 |
| 3 | 체험 URL + QR 코드 최종 확인 | PM | 레퍼럴 파라미터 포함 여부 |
| 4 | 모바일 접속 테스트 (iOS/Android) | QA | Google OAuth + 자동 가입 풀 플로우 |
| 5 | 2배 레버리지 + Auto TP/SL 동작 확인 | QA | 안내 팝업, 레버리지 제한, TP/SL 자동 생성 |
| 6 | 유스메타 측 최종 리허설 완료 확인 | PM | 최문창 상무 테스트 완료 여부 |
| 7 | 장애 대응 핫라인 + 실시간 모니터링 | Dev | 자금 전송 실패, 서버 부하 등 즉시 대응 |

---

## GitHub: supercycl-mockup

### 리포지토리 개요

- **URL**: https://github.com/5kyo/supercycl-mockup
- **오너**: 5kyo
- **브랜치**: main
- **언어 구성**: TypeScript 95.2%, CSS 3.7%, 기타 1.1%
- **빌드 도구**: Vite + React + TypeScript
- **라우터**: react-router-dom v7
- **상태 관리**: React Context API (AppContext)

**주요 의존성 (package.json):**
```json
{
  "dependencies": {
    "react": "^19.2.4",
    "react-dom": "^19.2.4",
    "react-router-dom": "^7.13.2"
  }
}
```

**전체 디렉토리 구조:**
```
supercycl-mockup/
├── public/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── GoogleIcon.tsx
│   │   │   ├── Logo.tsx
│   │   │   └── Modal.tsx
│   │   ├── dev/
│   │   │   └── DevNav.tsx
│   │   ├── layout/
│   │   ├── modals/
│   │   │   ├── AdjustLeverage.tsx
│   │   │   ├── AutoTpSlModal.tsx
│   │   │   ├── CoinSelector.tsx
│   │   │   ├── LeverageNotice.tsx
│   │   │   └── SignalOrderSheet.tsx
│   │   └── trading/
│   │       ├── Chart.tsx
│   │       ├── CoinInfoBar.tsx
│   │       ├── Dashboard.tsx
│   │       ├── OrderForm.tsx
│   │       ├── Orderbook.tsx
│   │       ├── PositionCard.tsx
│   │       └── SignalCard.tsx
│   ├── constants/
│   │   ├── coins.ts
│   │   ├── defaults.ts
│   │   ├── orderbook.ts
│   │   ├── positions.ts
│   │   ├── scenarios.ts
│   │   └── signals.ts
│   ├── context/
│   │   └── AppContext.tsx
│   ├── pages/
│   │   ├── LandingPage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── OnboardingPage.tsx
│   │   ├── SettingsPage.tsx
│   │   ├── SignalPage.tsx
│   │   ├── TermsPage.tsx
│   │   └── TradingPage.tsx
│   ├── styles/
│   ├── App.tsx
│   └── main.tsx
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

### 라우트 구조 (App.tsx)

```typescript
<Routes>
  <Route path="/"            element={<LandingPage />} />
  <Route path="/login"       element={<LoginPage />} />
  <Route path="/terms"       element={<TermsPage />} />
  <Route path="/onboarding"  element={<OnboardingPage />} />
  <Route path="/trade"       element={<TradingPage />} />
</Routes>
```

- 전역 AppProvider로 상태 공유
- DevNav 컴포넌트가 모든 화면 위에 상시 렌더링 (개발용 빠른 탐색)

---

### 전역 상태 구조 (AppContext)

**AppState 인터페이스:**
```typescript
interface AppState {
  isLoggedIn: boolean;
  hasAcceptedTerms: boolean;
  hasCompletedOnboarding: boolean;
  hasSeenLeverageNotice: boolean;
  selectedCoin: Coin;
  leverage: number;
  orderType: "limit" | "market" | "conditional";
  autoTpSlEnabled: boolean;
  takeProfitPercent: number;
  stopLossPercent: number;
  positions: readonly Position[];
  activeTab: TabKey;
  toastMessage: string | null;
  signalState: SignalState;
  prefillData: SignalPrefill | null;
}
```

**초기값 (defaults.ts):**
```typescript
DEFAULT_TP_PERCENT = 1.8
DEFAULT_SL_PERCENT = 5.0
DEFAULT_LEVERAGE = 2
MAX_LEVERAGE = 2
MIN_LEVERAGE = 1
PARTNER_CODE = "YOUTHMETA"

ACCOUNT = {
  email: "user@gmail.com",
  wallet: "0x9834...9948",
  balance: 1000.0,
  currency: "USDC"
}
```

**지원 액션 타입 (21개):**
- 인증: LOGIN, ACCEPT_TERMS, COMPLETE_ONBOARDING, DISMISS_LEVERAGE_NOTICE
- 거래 설정: SELECT_COIN, SET_LEVERAGE, SET_ORDER_TYPE
- 손익 관리: UPDATE_TP_SL, TOGGLE_AUTO_TP_SL
- 주문 실행: PLACE_ORDER, EXECUTE_SIGNAL_ORDER
- UI 제어: SET_TAB, SHOW_TOAST, HIDE_TOAST
- 신호 관리: SET_SIGNAL_FILTER, MARK_SIGNALS_READ, PREFILL_FROM_SIGNAL, CLEAR_PREFILL
- 시나리오: JUMP_TO_SCENARIO

**지원 코인 목록 (coins.ts):**
```
BTC  / BTC-USDC  / $94,677 / -7.2% / 1.2B vol
ETH  / ETH-USDC  / $2,015  / +2.1% / 580M vol
SOL  / SOL-USDC  / $148.5  / -3.4% / 320M vol
DOGE / DOGE-USDC / $0.1823 / +5.8% / 180M vol
ARB  / ARB-USDC  / $1.12   / -1.5% / 95M vol
AVAX / AVAX-USDC / $35.8   / +0.8% / 110M vol
MATIC/ MATIC-USDC/ $0.58   / -2.3% / 75M vol
LINK / LINK-USDC / $14.2   / +3.1% / 88M vol
```

---

### [화면 1] LandingPage / 라우트: /

**파일 경로:** `src/pages/LandingPage.tsx`

**UI 요소:**
- Logo 컴포넌트 (size=56)
- 제목 텍스트: "Trade Different, Ride the Supercycl"
- 설명 텍스트: 다중 거래소 통합 플랫폼 홍보문구
- Google 로그인 버튼 (fullWidth, GoogleIcon 포함)
- TESTNET MODE 배너 (하단)
- 방사형 그래디언트 녹색 글로우 오버레이 (절대 위치)

**스타일/레이아웃:**
- 배경색: #0a0a0a
- 전체 높이: 100dvh
- 플렉스 레이아웃, 중앙 정렬
- 최대 너비: 320px
- 연쇄 페이드인 애니메이션 (0.15s, 0.3s, 0.45s 딜레이)

**상태/분기:**
- 없음 (정적 페이지)

**이벤트 핸들러:**
- Google 버튼 클릭 → navigate("/login")

**API 호출:**
- 없음

---

### [화면 2] LoginPage / 라우트: /login

**파일 경로:** `src/pages/LoginPage.tsx`

**UI 요소:**
- 뒤로가기 버튼 (← 화살표, 좌상단)
- Logo 컴포넌트 (size=48)
- 제목: "Log in or sign up"
- 설명: "Connect your existing accounts and start trading instantly"
- Google 로그인 버튼 (variant="google", fullWidth)
  - 버튼 텍스트: "Continue with Google"
  - GoogleIcon 포함
- 약관 동의 안내 텍스트 (Terms of Service, Privacy Policy 링크 포함)

**스타일/레이아웃:**
- 전체 높이: 100dvh
- 패딩: 60px 24px 40px
- 페이드인 애니메이션 0.3s

**상태/분기:**
- AppContext의 dispatch 사용

**이벤트 핸들러:**
- 뒤로가기 버튼 클릭 → navigate("/")
- Google 버튼 클릭 → handleLogin() → dispatch({type: "LOGIN"}) → navigate("/terms")

**API 호출:**
- 없음 (목업: Google OAuth 시뮬레이션)

---

### [화면 3] TermsPage / 라우트: /terms

**파일 경로:** `src/pages/TermsPage.tsx`

**UI 요소:**
- 제목: "Agreement Required" (22px, 굵기 700)
- 설명: "Please review and accept our terms and policies to proceed."
- 약관 체크박스 (동의 여부 선택)
- Accept 버튼 (agreed=true 일 때만 활성화)
- Decline 버튼

**스타일/레이아웃:**
- 전체 높이: 100dvh
- 플렉스 레이아웃, 중앙 정렬
- 최대 너비: 320px (모바일 최적화)
- CSS 변수 활용 (--color-pri-1, --text-secondary 등)

**상태/분기:**
- `agreed: boolean` — 약관 동의 여부 (초기값: false)
- Accept 버튼: agreed=false이면 비활성화

**이벤트 핸들러:**
- 체크박스 변경 → setAgreed(!agreed) 토글
- Accept 버튼 클릭 (agreed=true) → dispatch({type: "ACCEPT_TERMS"}) → navigate("/onboarding")
- Decline 버튼 클릭 → navigate("/")

**API 호출:**
- 없음

---

### [화면 4] OnboardingPage / 라우트: /onboarding

**파일 경로:** `src/pages/OnboardingPage.tsx`

**UI 요소 (진행 중 상태, completed=false):**
- Logo 컴포넌트
- 3단계 진행 상황 표시 (원형 아이콘: 완료/활성/미완료)
  - 단계 1: 지갑 자동 생성 (~1.2초 후 완료)
  - 단계 2: Testnet 연결 (~2.2초 후 완료)
  - 단계 3: 테스트 자금 로딩 (~3.2초 후 완료)
- 회전 스피너 애니메이션

**UI 요소 (완료 상태, completed=true):**
- 체크마크(✓) 아이콘
- USDC 잔액 표시 (테스트넷)
- CEX 통합 예정 안내 문구
- "Start Trading" 버튼 → /trade 이동

**상태/분기:**
- `currentStep: 0~3` — 온보딩 진행 단계
- `completed: boolean` — 온보딩 완료 여부
- completed=false: 스피너 + 단계 표시
- completed=true: 체크마크 + Start Trading 버튼

**타이밍 (타이머 기반):**
- ~1.2초: currentStep=1 (지갑 생성 완료)
- ~2.2초: currentStep=2 (Testnet 연결 완료)
- ~3.2초: currentStep=3, completed=true (자금 로딩 완료)

**이벤트 핸들러:**
- "Start Trading" 버튼 클릭 → dispatch({type: "COMPLETE_ONBOARDING"}) → navigate("/trade")

**API 호출:**
- 없음 (타이머 기반 시뮬레이션)

---

### [화면 5] TradingPage / 라우트: /trade

**파일 경로:** `src/pages/TradingPage.tsx`

**UI 요소:**
- LeverageNotice 모달 (hasSeenLeverageNotice=false일 때 최초 1회 표시)
- CoinInfoBar (상단 코인 정보 바)
- Toast 알림
- 탭 전환 컨텐츠 영역 (스크롤 가능, 하단 64px 여백)
- BottomNav (하단 고정 네비게이션, 4개 탭)

**탭 구성 (activeTab):**
- trade 탭: Chart + Orderbook + OrderForm + Dashboard
- signal 탭: SignalPage 컴포넌트
- portfolio 탭: "coming in the next version" 메시지 (미구현)
- settings 탭: SettingsPage 컴포넌트

**모달 목록:**
- AdjustLeverage 모달 (showLeverage=true일 때)
- AutoTpSlModal (showTpSl=true일 때)
- CoinSelector 모달 (showCoinSelector=true일 때)

**상태/분기:**
- `showLeverage: boolean` — 레버리지 조정 모달
- `showTpSl: boolean` — TP/SL 설정 모달
- `showCoinSelector: boolean` — 코인 선택 모달
- `activeTab` — 현재 활성 탭 (trade/signal/portfolio/settings)

**이벤트 핸들러:**
- onCoinSelect → setShowCoinSelector(true)
- onLeverageTap → setShowLeverage(true)
- onTpSlEdit → setShowTpSl(true)
- 각 모달 onClose → 해당 show 상태 false

**API 호출:**
- 없음 (목업 데이터)

---

### [화면 5-1] Trade 탭 — OrderForm

**파일 경로:** `src/components/trading/OrderForm.tsx`

**UI 요소:**
- 레버리지 표시 버튼 (격리된 마진, 현재 배수 표시, 탭 가능 → AdjustLeverage 모달)
- 주문 타입 탭: "limit" | "market" | "conditional"
- 가격 입력 필드 (limit/conditional 주문 시만 표시, market 시 숨김)
- 크기(Size) 입력 필드
- 백분율 슬라이더 (0~100%)
- Auto TP/SL 인디케이터 (autoTpSlEnabled=true 시 TP%/SL% 표시) + Edit 버튼
- Long 버튼 (초록색)
- Short 버튼 (빨간색)

**상태/분기:**
- orderType: limit/market/conditional에 따라 가격 필드 표시/숨김
- autoTpSlEnabled=true이면 TP/SL 인디케이터 표시
- prefillData 있으면 초기값 자동 채움 (시그널 연동)

**이벤트 핸들러:**
- 주문 타입 탭 전환 → dispatch({type: "SET_ORDER_TYPE"})
- 레버리지 표시 클릭 → onLeverageTap()
- Edit 버튼 클릭 → onTpSlEdit()
- Long 버튼 클릭 → handleOrder("Long") → dispatch({type: "PLACE_ORDER"}) → SHOW_TOAST
- Short 버튼 클릭 → handleOrder("Short") → dispatch({type: "PLACE_ORDER"}) → SHOW_TOAST

---

### [화면 5-2] Trade 탭 — Dashboard

**파일 경로:** `src/components/trading/Dashboard.tsx`

**UI 요소:**
- 탭 바: Positions | Open Orders | History
- Positions 탭 배지: 포지션 개수 표시 (포지션 존재 시)
- Positions 탭: PositionCard 목록 또는 "No open positions" 빈 상태
- Open Orders 탭: "No open orders" 빈 상태 (미구현)
- History 탭: "No order history" 빈 상태 (미구현)

**PositionCard UI 요소:**
- 코인명 + Long/Short 방향 배지 + Auto 배지 (isAuto=true일 때 표시)
- 포지션 크기 (size + sizeUnit)
- Entry Price / Mark Price
- PnL 금액 + PnL% (수익: 녹색, 손실: 빨간색)
- TP/SL 표시 영역 (tp 또는 sl 값 존재 시만 렌더링)
- 좌측 보더 색상: 수익=녹색(--accent-green), 손실=빨간색(--accent-red)

**상태/분기:**
- tab: "positions" | "open" | "history"
- position.isAuto=true이면 Auto 배지 표시 (초록색, 9px 폰트)
- position.pnl >= 0이면 녹색, < 0이면 빨간색
- position.tp 또는 position.sl 존재 시 TP/SL 영역 표시

---

### [화면 5-3] Signal 탭 — SignalPage

**파일 경로:** `src/pages/SignalPage.tsx`

**UI 요소:**
- 헤더: ⚡ YouthMeta Signals
- 성과 요약 카드 (최근 30일)
  - Hit 카운트 (녹색) / Miss 카운트 (빨간색) / Expired 카운트 (회색)
  - 평균 PnL%
  - 성공률% (70% 이상=녹색, 50% 이상=주황색, 미만=빨간색)
- 필터 탭 (가로 스크롤 가능): ALL | Long | Short | Active | Closed
- 신호 목록 (SignalCard 반복)
- SignalOrderSheet 바텀시트 모달 (sheetSignal != null일 때)
- 빈 상태: "이 필터와 일치하는 신호 없음"

**필터 타입:** ALL | LONG | SHORT | ACTIVE | CLOSED
**CLOSED 상태 집합:** HIT_TP | HIT_SL | EXPIRED | CANCELLED

**이벤트 핸들러:**
- 필터 버튼 클릭 → dispatch({type: "SET_SIGNAL_FILTER", filter: key})
- SignalCard onExecute → setSheetSignal(signal) → SignalOrderSheet 표시
- SignalCard onModify → dispatch({type: "PREFILL_FROM_SIGNAL", prefill: {...}}) + SHOW_TOAST
- SignalOrderSheet onExecute → dispatch({type: "EXECUTE_SIGNAL_ORDER", signalId}) + SHOW_TOAST → setSheetSignal(null)
- SignalOrderSheet onModify → dispatch({type: "PREFILL_FROM_SIGNAL"}) → setSheetSignal(null)
- SignalOrderSheet onClose → setSheetSignal(null)

---

### [화면 5-4] Settings 탭 — SettingsPage

**파일 경로:** `src/pages/SettingsPage.tsx`

**UI 섹션:**

1. **Account 섹션**
   - 사용자 이메일 표시 (ACCOUNT.email)
   - 지갑 주소 표시 + 복사 버튼 (ACCOUNT.wallet)
   - 복사 클릭 → dispatch({type: "SHOW_TOAST", message: "Address copied!"})

2. **Trading Preferences 섹션**
   - Auto TP/SL 설정 표시 (takeProfitPercent%, stopLossPercent%)
   - Edit 버튼 (상위 TradingPage에서 AutoTpSlModal 열기)
   - Auto TP/SL 토글 스위치 (autoTpSlEnabled 상태 반영)
     - ON 상태: 녹색 배경
     - OFF 상태: 기본 배경
     - 클릭 → dispatch({type: "TOGGLE_AUTO_TP_SL"})

3. **Exchange Connection 섹션**
   - Hyperliquid 테스트넷 연결 상태 표시

4. **Logout 섹션**
   - 로그아웃 버튼 (빨간색 테두리)
   - 클릭 → dispatch({type: "SHOW_TOAST", message: 목업 메시지})

---

### [모달 1] LeverageNotice

**파일 경로:** `src/components/modals/LeverageNotice.tsx`

**UI 요소:**
- 제목: "Leverage Policy Notice"
- ⚠ 경고 아이콘 (36px, 노란색, --accent-yellow)
- 설명 텍스트: "This account has a maximum leverage limit of 2x under the user protection policy."
- "I Understand" 버튼 (fullWidth)

**상태/분기:**
- state.hasSeenLeverageNotice=true이면 null 렌더링 (표시 안 함)
- 최초 1회만 표시 (dismiss 후 재표시 없음)

**이벤트 핸들러:**
- "I Understand" 버튼 클릭 → dispatch({type: "DISMISS_LEVERAGE_NOTICE"})

---

### [모달 2] AdjustLeverage

**파일 경로:** `src/components/modals/AdjustLeverage.tsx`

**UI 요소:**
- 선택된 코인 정보 표시 (예: BTCUSDT Perp | Isolated)
- 경고 배너: "Max leverage limited to 2x (User Protection)" (--accent-yellow 색상)
- 현재 레버리지 값 표시 (큰 폰트, 예: "2x")
- 범위 슬라이더 (MIN_LEVERAGE=1 ~ MAX_LEVERAGE=2, step=1)
- 취소 버튼 / 확인 버튼

**상태/분기:**
- 슬라이더 범위: MIN_LEVERAGE(1) ~ MAX_LEVERAGE(2)
- 2배 초과 불가 (MAX_LEVERAGE=2 하드코딩)

**이벤트 핸들러:**
- 슬라이더 변경 → 로컬 value 상태 업데이트
- 확인 버튼 → dispatch({type: "SET_LEVERAGE", leverage: value}) → onClose()
- 취소 버튼 → onClose()

---

### [모달 3] AutoTpSlModal

**파일 경로:** `src/components/modals/AutoTpSlModal.tsx`

**UI 요소:**
- Take Profit % 입력 필드 (% 기호 우측 표시)
- Stop Loss % 입력 필드 (% 기호 우측 표시)
- 설정 적용 범위 설명 텍스트
- 취소 버튼 / 확인 버튼

**상태/분기:**
- `tp: string` — 익절 퍼센트 입력값 (초기값: 현재 takeProfitPercent)
- `sl: string` — 손절 퍼센트 입력값 (초기값: 현재 stopLossPercent)
- 확인 버튼: tpNum > 0 OR slNum > 0 조건 충족 시만 활성화

**이벤트 핸들러:**
- 확인 버튼 → dispatch({type: "UPDATE_TP_SL", takeProfitPercent: tpNum, stopLossPercent: slNum}) → onClose()
- 취소 버튼 → onClose()

---

### [모달 4] CoinSelector

**파일 경로:** `src/components/modals/CoinSelector.tsx`

**UI 요소:**
- 코인 목록 (COINS 배열 기반, 8개 코인)
- 각 코인 항목: 심볼, 페어명, 가격, 24h 변동률, 거래량

**이벤트 핸들러:**
- 코인 항목 클릭 → dispatch({type: "SELECT_COIN", coin}) → onClose()

---

### [모달 5] SignalOrderSheet

**파일 경로:** `src/components/modals/SignalOrderSheet.tsx`

**UI 요소:**
- 신호 상세 정보 표시 (코인, 방향 Long/Short, 진입가, 타겟가, 손절가, 레버리지)
- Execute 버튼 (즉시 주문 실행)
- Modify 버튼 (주문 폼에 신호값 로드 후 직접 수정)
- Close 버튼 (X)

**이벤트 핸들러:**
- Execute → onExecute() → dispatch({type: "EXECUTE_SIGNAL_ORDER"}) + SHOW_TOAST
- Modify → onModify() → dispatch({type: "PREFILL_FROM_SIGNAL"})
- Close → onClose()
