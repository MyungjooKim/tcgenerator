# Phase 3 정책 문서

**문서 버전:** v1.0
**작성일:** 2026-04-03
**기준 소스:** parsed_content.md + common/policy/* + tc-rules-override.md

---

## Phase 개요

| 항목 | 내용 |
|------|------|
| Phase 코드 | P3_MobileMockup |
| 서비스 | Supercycl 모바일 확정 사양 (GitHub 목업 기반) |
| 거래소 | Hyperliquid Testnet (단일) |
| 플랫폼 | Web(Mobile) 360px 고정폭 |
| API 엔드포인트 | api.hyperliquid-testnet.xyz |
| Chain ID | 998 |
| 초기 자금 | 100.0 USDC (constants/defaults.ts 기준, 화면상 100,000 USDC 표시) |
| 계정 조건 | YOUTHMETA 파트너코드로 가입한 체험용 계정 |
| 언어 | EN (기본) / KO (한국어 전환 가능) |
| 테스트 환경 | 실제 자금 없음 (Testnet 전용) |

---

## TC ID 규칙 (Phase 3 전용)

```
SC-{대분류코드}-{중분류코드}-{NNN}
예: SC-AUTH-LOGN-001, SC-TRAD-ORDF-001
```

`classification_v1_APPROVED.md` 기준 대분류코드/중분류코드를 반드시 사용한다.

---

## 파일명 규칙 (Phase 3 전용)

```
SPCY_TC_P3_MobileMockup_{YYYYMMDD}_v{N}.xlsx
예: SPCY_TC_P3_MobileMockup_20260403_v1.xlsx
```

---

## 도메인별 정책

---

### AUTH — 인증/온보딩

> 포함 화면: 랜딩 (`/`), 로그인 (`/login`), 약관 동의 (`/terms`), 온보딩 (`/onboarding`)

#### 기능 요약

사용자가 앱에 최초 진입하여 Google 계정으로 로그인하고, 이용약관에 동의한 뒤, 자동화된 지갑 생성 및 테스트 자금 입금 절차를 완료하는 일련의 온보딩 플로우다. 플로우 완료 후 트레이딩 메인 화면으로 진입한다.

**사용자 플로우 순서:**
```
랜딩 (/) → 로그인 (/login) → 약관 동의 (/terms) → 온보딩 (/onboarding) → 트레이딩 (/trade)
```

#### 정책 규칙

**[랜딩]**
- 모든 사용자가 인증 없이 진입 가능 (로그인 상태 체크 없음)
- "Continue with Google" 버튼 탭 시 무조건 `/login`으로 이동
- 조건부 리다이렉트 없음

**[로그인]**
- 목업 계정 고정: 이름 "John Doe", 이메일 "text123@gmail.com"
- "Continue as John Doe" 버튼 탭 → `LOGIN` 액션 디스패치 → `isLoggedIn: true` 전환 → `/terms`로 이동
- 딤(dim) 영역 탭 → 로그인 처리 없이 랜딩(`/`)으로 복귀

**[약관 동의]**
- 체크박스 미체크 상태: Accept 버튼 비활성화 (opacity 0.4, cursor not-allowed)
- 체크박스 체크 상태: Accept 버튼 활성화
- Accept 버튼 탭 → `ACCEPT_TERMS` 액션 디스패치 → `hasAcceptedTerms: true` 전환 → `/onboarding`으로 이동
- Terms of Service 링크: `https://supercycl.io/terms` (새 탭 오픈)
- Privacy Policy 링크: `https://supercycl.io/policy` (새 탭 오픈)

**[온보딩]**
- 자동 진행 (유저 입력 불필요), 타이머 기반 3단계 순차 진행:
  - 0ms: Step 1 "Creating wallet" 시작
  - 1200ms: Step 2 "Connecting to Hyperliquid" 시작
  - 2200ms: Step 3 "Loading test funds" 시작
  - 3200ms: 완료 → `COMPLETE_ONBOARDING` 액션 디스패치 → `hasCompletedOnboarding: true`
- 완료 전: "Start Trading" 버튼 비가시 (opacity 0, pointer-events none)
- 완료 후: 잔고 카드 + "Start Trading" 버튼 fadeIn 표시
- 초기 입금 잔고: 100.0 USDC (화면 표시상 "Balance — 100,000 USDC")
- "Start Trading" 버튼은 완료 후에만 탭 가능 → `/trade`로 이동

**[레버리지 안내 팝업 (Leverage Policy Notice)]**
- 목업에서는 `hasSeenLeverageNotice: boolean` 상태로 관리
- 표시 조건 및 노출 시점: [미결] 항목 참조

#### 예외/엣지 케이스

| 케이스 | 처리 방식 |
|--------|-----------|
| 온보딩 완료 전 뒤로가기 | 명시되지 않음 — 기획서 미확정 |
| 이미 로그인된 상태에서 랜딩 재진입 | 조건부 리다이렉트 없음 (목업에서 항상 진입 가능) |
| 약관 링크 탭 후 체크박스 상태 | 체크박스 상태 유지 (외부 링크 오픈은 체크박스에 영향 없음) |
| 딤 영역 탭 시 로그인 상태 변화 | `isLoggedIn` 상태 변경 없이 랜딩으로 복귀 |
| 온보딩 타이머 중 네트워크 이슈 | 목업은 타이머 기반 시뮬레이션이므로 실제 네트워크 오류 없음 |

#### [미결] 항목

| ID | 항목 | 내용 |
|----|------|------|
| PEND-AUTH-001 | LeverageNotice 노출 조건 | 최초 1회 / 매 로그인마다 미확정 (`hasSeenLeverageNotice` 쿠키/세션 범위 불명확) |
| PEND-AUTH-002 | 초기 지급 잔고 표시 | 코드 기준 100.0 USDC인데 화면에 100,000 USDC로 표시 — 단위 변환 정책 확인 필요 |
| PEND-AUTH-003 | 온보딩 중 뒤로가기 처리 | 기획서에 명시 없음 — 중단/재시작 여부 미확정 |
| PEND-AUTH-004 | 로그인 상태 유지 범위 | 앱 재시작/새로고침 시 `isLoggedIn` 상태 유지 여부 미확정 (localStorage 저장 여부 불명) |

---

### TRAD — 트레이딩

> 포함 화면: 트레이딩 화면 (`/trade` 탭: trade), 모달/시트: CoinSelector, AdjustLeverage, AutoTpSlModal

#### 기능 요약

선물 트레이딩 메인 기능. 코인 선택, 레버리지 설정, Market/Limit 주문 실행, 오더북 조회, 포지션 및 미체결 주문 관리를 포함한다. 캔들 차트는 정적 이미지(chart-candle.png)로 표시된다.

#### 정책 규칙

**[코인 선택]**
- 지원 코인 4종: BTC-USDC (기본), ETH-USDC, SOL-USDC, XRP-USDC
- 코인 페어 탭 → CoinSelector 바텀시트 오픈
- 검색: 심볼/페어명 기반 실시간 필터링
- 코인 선택 → `SELECT_COIN` 액션 디스패치 → 바텀시트 닫기

**[레버리지 설정]**
- 기본 레버리지: 2x
- 허용 범위: 1x ~ 2x (Youthmeta 파트너 계정 레버리지 2x 제한 정책 적용)
- 슬라이더: 1x ~ 2x 범위 (1 단위 증분), 범위 밖 이동 불가
- 경고 배너: "Max leverage limited to 2x (User Protection)" 항상 표시
- Confirm → `SET_LEVERAGE` 액션 디스패치 → 모달 닫기
- Cancel → 변경 불저장, 모달 닫기
- 3x 이상 입력: 입력 불가 또는 자동으로 2x로 리셋
- 코인 변경 시 Position/OpenOrders 없는 상태: 레버리지 자동 2x로 변경

**[주문폼 — 주문 유형]**
- 기본 주문 유형: Market
- Market 주문: 가격 입력 필드 숨김, 즉시 포지션 생성
- Limit 주문: 가격 입력 필드 표시, 지정가 직접 입력, 미체결 주문으로 등록
- Signal에서 prefill 진입 시: 가격 필드에 시그널 진입가 자동 입력, 주문 유형 Limit 전환

**[주문 실행]**
- "Buy / Long" 버튼 탭 → `PLACE_ORDER(side: Long)` 디스패치 → 포지션 생성 → Toast 표시
- "Sell / Short" 버튼 탭 → `PLACE_ORDER(side: Short)` 디스패치 → 포지션 생성 → Toast 표시
- Auto TP/SL 활성 상태에서 주문 시: 포지션 생성 시 TP/SL 자동 설정

**[포지션 관리]**
- 초기 포지션: DEFAULT_POSITIONS (XRP Short 2x, BTC Long 2x 2개 기본값)
- PositionCard "Close" 버튼 탭 → `CLOSE_POSITION` 디스패치 → "Position closed" Toast
- Open Order "Cancel" 버튼 탭 → `CANCEL_ORDER` 디스패치 → "Order cancelled" Toast

**[Dashboard 탭 배지]**
- Positions 탭: 포지션 수 > 0이면 녹색 배지 표시
- Open Order 탭: 미체결 주문 수 > 0이면 노란색 배지 표시
- 빈 상태: 각각 "No open positions" / "No open orders" 표시

**[오더북]**
- 매도 호가: 빨간색 텍스트
- 매수 호가: 녹색 텍스트
- 중간 현재가 표시

**[Trigger Price 계산 공식]**
```
Long 포지션:
  TP Trigger Price = 진입가 × (1 + TP% / Leverage / 100)
  SL Trigger Price = 진입가 × (1 - SL% / Leverage / 100)

Short 포지션:
  TP Trigger Price = 진입가 × (1 - TP% / Leverage / 100)
  SL Trigger Price = 진입가 × (1 + SL% / Leverage / 100)

예시 (Long, 진입가 $94,677 / TP +1.8% / SL -5% / 2x):
  TP = 94,677 × (1 + 0.018/2) = 94,677 × 1.009 ≈ $95,529
  SL = 94,677 × (1 - 0.05/2)  = 94,677 × 0.975  ≈ $92,310
```

#### 예외/엣지 케이스

| 케이스 | 처리 방식 |
|--------|-----------|
| 수량 0 입력 상태에서 주문 버튼 탭 | 명시되지 않음 — 검증 로직 미확정 |
| 잔고 부족 상태에서 주문 시도 | 명시되지 않음 — 목업은 잔고 검증 없는 것으로 추정 |
| Limit 주문 가격 미입력 상태에서 주문 버튼 탭 | 명시되지 않음 |
| 코인 변경 시 기존 입력 수량/가격 초기화 여부 | 명시되지 않음 |
| 포지션 보유 상태에서 코인 변경 시 레버리지 | Position/OpenOrders 보유 시 레버리지 변경 없음 (기존 설정 유지) |
| Orderbook 데이터 실시간 여부 | 목업 정적 데이터 vs 실제 API 미확정 |

#### [미결] 항목

| ID | 항목 | 내용 |
|----|------|------|
| PEND-TRAD-001 | 오더북 데이터 소스 | 목업 데이터 vs 실제 Hyperliquid API 연동 미확정 |
| PEND-TRAD-002 | 수량 0 주문 처리 | 수량 미입력 또는 0 입력 시 주문 버튼 동작 정책 미확정 |
| PEND-TRAD-003 | 잔고 부족 검증 | 잔고 부족 시 주문 거부 처리 여부 미확정 (목업에서 검증 없는 것으로 추정) |
| PEND-TRAD-004 | Limit 주문 가격 미입력 처리 | Limit 주문 유형 선택 후 가격 미입력 상태에서 주문 버튼 동작 미확정 |

---

### SIGNAL — 시그널

> 포함 화면: 시그널 탭 (`/trade` 탭: signal), 바텀시트: SignalOrderSheet

#### 기능 요약

AI 트레이딩 시그널 목록을 표시하고, ACTIVE 시그널에 대해 원클릭 주문 실행(SignalOrderSheet)을 제공한다. 필터링, 퍼포먼스 요약, 미읽음 배지 기능을 포함한다.

#### 정책 규칙

**[시그널 목록]**
- 퍼포먼스 요약 표시 (최근 30일): Hit/Miss/Expired 카운트, Avg PnL, Hit Rate
- 필터 탭바: All / Long / Short / Active / Closed
- 필터 결과 없음: "No signals matching this filter" 빈 상태 표시

**[시그널 카드 상태 규칙]**
| 상태 | Execute 버튼 | PnL 표시 |
|------|------------|----------|
| ACTIVE | 표시 | 없음 |
| HIT_TP | 없음 | 표시 (양수 녹색) |
| HIT_SL | 없음 | 표시 (음수 빨강) |
| EXPIRED | 없음 | 없음 |
| CANCELLED | 없음 | 없음 |

**[신뢰도(Confidence) 배지]**
- HIGH / MEDIUM / LOW 3단계

**[미읽음 배지]**
- BottomNav Signal 아이콘: 미읽음 수(`unreadCount`) > 0이면 배지 표시
- 시그널 탭 진입 시: `MARK_SIGNALS_READ` 디스패치 → 미읽음 카운트 0으로 초기화

**[목업 시그널 데이터]**
| ID | 코인 | 방향 | 진입가 | TP | SL | 레버리지 | 신뢰도 | 상태 |
|----|------|------|--------|----|----|---------|--------|------|
| sig-001 | BTC | LONG | $94,200 | $96,800 | $92,500 | 2x | HIGH | ACTIVE |
| sig-002 | SOL | SHORT | $178.5 | $170.0 | $183.0 | 2x | MEDIUM | ACTIVE |
| sig-003 | ETH | LONG | $2,650 | $2,720 | $2,610 | 2x | HIGH | HIT_TP (+2.64%) |
| sig-004 | XRP | SHORT | $2.85 | $2.65 | $2.95 | 2x | LOW | HIT_SL (-3.51%) |

**[SignalOrderSheet — 시그널 주문 확인]**
- 시그널 레버리지 기본 표시 (편집 가능, 1~2x)
- 기본 Margin: ACCOUNT.balance 전액
- 주문 유형: Market / Limit 토글 선택 가능
- Market 주문: 즉시 포지션 생성
- Limit 주문: 미체결 주문으로 등록
- LONG 시그널: Execute 버튼 녹색
- SHORT 시그널: Execute 버튼 빨강
- Execute Order 탭 → `EXECUTE_SIGNAL_ORDER` 디스패치 → Toast("Order executed from signal") → 트레이딩 탭으로 전환
- Modify 버튼 탭 → 편집 모드 ON/OFF 토글
  - 편집 모드: Margin 직접 입력 가능, Leverage 1~2x 조정

**[PREFILL 연동]**
- Modify 버튼의 `onModify` 핸들러: `PREFILL_FROM_SIGNAL` 디스패치 후 트레이딩 탭 이동
- 트레이딩 탭 OrderForm에 시그널 진입가 자동 입력, 주문 유형 Limit 전환

#### 예외/엣지 케이스

| 케이스 | 처리 방식 |
|--------|-----------|
| 모든 시그널이 종료 상태일 때 Active 필터 | "No signals matching this filter" 표시 |
| ACTIVE 시그널 Execute 중 다른 시그널 Execute | 중복 주문 처리 정책 미확정 |
| Margin 입력 > 가용 잔고 | 검증 로직 미확정 |

#### [미결] 항목

| ID | 항목 | 내용 |
|----|------|------|
| PEND-SIGN-001 | 시그널 주문 수량 단위 | USD 금액 vs 코인 수량 미확정 (Margin 입력 단위 정책) |
| PEND-SIGN-002 | Margin 상한 검증 | Margin 입력값이 가용 잔고 초과 시 처리 정책 미확정 |
| PEND-SIGN-003 | 중복 시그널 주문 | 동일 시그널 중복 Execute 방지 정책 미확정 |
| PEND-SIGN-004 | 시그널 데이터 갱신 | 목업 고정 데이터 vs 실시간 API 갱신 미확정 |

---

### PORT — 포트폴리오

> 포함 화면: 포트폴리오 탭 (`/trade` 탭: portfolio)

#### 기능 요약

사용자의 총 자산 현황, 가용 잔고, 증거금 사용량, 보유 포지션 요약, 최근 활동 내역을 읽기 전용으로 표시한다.

#### 정책 규칙

**[잔고 계산 공식]**
```
totalBalance  = ACCOUNT.balance + 전체 포지션 PnL 합계
available     = ACCOUNT.balance - 전체 포지션 margin 합계
totalMargin   = 전체 포지션 margin 합계
pnlPercent    = totalPnl / ACCOUNT.balance × 100 (소수점 2자리 반올림)
```

**[PnL 색상 규칙]**
- PnL > 0: 녹색 (#00de0b)
- PnL < 0: 빨강 (#ff5938)
- PnL = 0: 표시 규칙 미확정

**[보유 포지션]**
- 포지션 없음: "No open positions" 표시
- 포지션 있음: 컬러 바 + 코인명 + Side · Leverage + PnL 행 표시

**[최근 활동]**
- 목업 고정 데이터:
  - "Opened XRPUSDT Short · 2x" (2h ago)
  - "Opened BTCUSDT Long · 2x" (3h ago)
  - "Deposited 100 USDC" (5h ago)
- 포트폴리오 탭은 읽기 전용 (별도 액션 없음)

#### 예외/엣지 케이스

| 케이스 | 처리 방식 |
|--------|-----------|
| 포지션 전체 청산 후 포트폴리오 진입 | "No open positions" 표시, available = ACCOUNT.balance |
| ACCOUNT.balance = 0 시 pnlPercent 계산 | 0으로 나누기 처리 미확정 |

#### [미결] 항목

| ID | 항목 | 내용 |
|----|------|------|
| PEND-PORT-001 | 최근 활동 데이터 갱신 | 목업 고정 데이터 — 실제 API 연동 시 동적 표시 정책 미확정 |
| PEND-PORT-002 | PnL = 0 색상 처리 | PnL이 정확히 0인 경우 표시 색상 미확정 |
| PEND-PORT-003 | ACCOUNT.balance 0 처리 | 잔고 0 시 pnlPercent 계산 (0으로 나누기) 예외 처리 미확정 |

---

### SETS — 설정

> 포함 화면: 설정 탭 (`/trade` 탭: settings), 모달: AutoTpSlModal

#### 기능 요약

계정 정보 확인(지갑 주소 복사), Auto TP/SL 설정(ON/OFF 토글, 비율 편집), 언어 설정(EN/KO), 거래소 연결 정보 확인, 앱 정보 링크, 로그아웃 기능을 제공한다.

#### 정책 규칙

**[Account 섹션]**
- 이메일: `user@gmail.com` (목업 고정값)
- 지갑 주소: `0x9834...9948` (모노스페이스 폰트)
- Copy 버튼 탭 → Toast("Address copied!")

**[Auto TP/SL 설정]**
- Edit 버튼 탭 → AutoTpSlModal 오픈
- 토글 스위치: `TOGGLE_AUTO_TP_SL` 디스패치
- 토글 ON: 이후 생성 주문에 TP/SL 자동 적용
- 현재 설정 표시: `TP: +{n}% | SL: -{n}%`

**[AutoTpSlModal 규칙]**
- TP 입력 필드: 퍼센트(%) 입력
- SL 입력 필드: 퍼센트(%) 입력
- 기본값: TP 1.8%, SL 5.0%
- TP + SL 모두 0이면 Confirm 버튼 비활성화
- Confirm 탭 → `UPDATE_TP_SL` 디스패치 → `autoTpSlEnabled: true` 전환 → 모달 닫기
- Cancel 탭 → 변경 불저장, 모달 닫기
- 안내 문구: "Settings apply to new orders only. Existing positions will not be affected."

**[Auto TP/SL 입력 범위 (공통 정책 기준)]**
| 항목 | 최솟값 | 최댓값 | 소수점 |
|------|--------|--------|--------|
| TP (Take Profit) | 0.1% | 999.9% | 1자리까지 허용 |
| SL (Stop Loss) | 0.1% | 99.9% | 1자리까지 허용 |

- SL은 UI 상 양수로 입력, 내부적으로 손실 비율로 처리
- 경계값 처리: TP/SL = 0 → 저장 불가, > 최댓값 → 입력 제한 또는 자동 리셋, 소수점 2자리 이상 → 입력 불가, 음수 → 입력 불가

**[Language 섹션]**
- 지원 언어: English (en) / 한국어 (ko)
- 선택 → `SET_LANGUAGE` 디스패치 → localStorage 저장
- 앱 재시작 시 localStorage 기반 언어 복원
- 활성 언어: 녹색 배경 / 비활성: 어두운 배경

**[Exchange Connection 섹션]**
- Hyperliquid (Testnet): "Connected ✓" (녹색) — Phase 3 단일 지원 거래소
- Coming Soon: Binance, BingX, OKX, Bybit (인터랙션 없음)

**[About 섹션]**
- Supercycl Website: `https://supercycl.io/` (새 탭)
- Docs: `https://supercycl.gitbook.io/supercycl-docs-1` (새 탭)

**[Logout]**
- Logout 버튼 탭 → Toast("Logged out (mockup)") 표시
- 실제 로그아웃 처리 없음 (목업 전용 동작)

#### 예외/엣지 케이스

| 케이스 | 처리 방식 |
|--------|-----------|
| Auto TP/SL OFF 상태에서 Edit 버튼 탭 | 모달 오픈 가능 — ON 전환 없이도 수치 편집 가능 여부 미확정 |
| TP = 0 / SL = 0 각각 단독 입력 | Confirm 버튼 비활성화 (TP+SL 모두 0이어야 비활성이므로 하나만 0이면 활성 여부 확인 필요) |
| 언어 전환 후 토스트 메시지 언어 | 전환된 언어로 표시 여부 미확정 |
| 로그아웃 후 상태 초기화 | 목업이므로 상태 초기화 없음 (명시 필요) |

#### [미결] 항목

| ID | 항목 | 내용 |
|----|------|------|
| PEND-SETS-001 | Auto TP/SL OFF 시 Edit 버튼 동작 | OFF 상태에서 Edit → 수치 변경 후 Confirm 시 ON 자동 전환 여부 미확정 |
| PEND-SETS-002 | TP or SL 단독 0 입력 처리 | TP=0이고 SL>0인 경우 Confirm 버튼 활성 여부 미확정 (현재 규칙은 "모두 0이면 비활성") |
| PEND-SETS-003 | 언어 전환 후 Toast 메시지 언어 | 언어 전환 직후 Toast가 새 언어로 표시되는지 기존 언어로 표시되는지 미확정 |
| PEND-SETS-004 | 저장 실패 시 Toast 문구 | Auto TP/SL 저장 실패(네트워크 등) 시 에러 Toast 정확한 문구 미확정 |

---

### NAVI — 내비게이션/공통 컴포넌트

> 포함 화면: BottomNav, Header, Toast

#### 기능 요약

앱 전반에 걸쳐 표시되는 하단 탭 내비게이션(BottomNav), 상단 헤더(Header), 알림 토스트(Toast) 컴포넌트의 동작 정책이다.

#### 정책 규칙

**[BottomNav]**
- 탭 구성: Trade / Signal / Portfolio / Settings (4탭)
- 활성 탭: 아이콘 + 라벨 흰색 / 비활성: 회색
- Signal 탭 배지: `unreadCount > 0` 이면 배지 표시
- Signal 탭 전환 시: `MARK_SIGNALS_READ` 자동 호출 → 미읽음 카운트 0으로 초기화

**[Header]**
- 좌측: Supercycl 로고 (로고 아이콘 + 텍스트 SVG)
- 우측: "Testnet" 배지 (항상 표시)

**[Toast]**
- 화면 하단 오버레이 알림
- 자동 사라짐: `HIDE_TOAST` 자동 디스패치
- 트리거 상황:
  | 액션 | Toast 메시지 |
  |------|------------|
  | 주문 실행 (Trading) | 명시 없음 (표시됨) |
  | 포지션 Close | "Position closed" |
  | 주문 Cancel | "Order cancelled" |
  | 주소 복사 | "Address copied!" |
  | 시그널 주문 실행 | "Order executed from signal" |
  | 로그아웃 | "Logged out (mockup)" |

**[플랫폼 표기]**
| 값 | 사용 조건 |
|----|----------|
| `Web(Mobile)` | 기본값 — 360px 고정폭 모바일 브라우저 |
| `iOS Safari` | iOS Safari 특정 동작이 있는 경우 |
| `Android Chrome` | Android Chrome 특정 동작이 있는 경우 |
| `공통` | 플랫폼 무관 (서버 로직, 데이터 검증) |

#### 예외/엣지 케이스

| 케이스 | 처리 방식 |
|--------|-----------|
| 복수 Toast 연속 발생 | 표시 큐(queue) 처리 정책 미확정 (상태에 toastMessage 단일값) |
| Signal 탭 이외 탭 전환 시 unreadCount | Signal 탭이 아닌 탭 전환 시 카운트 초기화 안됨 |

#### [미결] 항목

| ID | 항목 | 내용 |
|----|------|------|
| PEND-NAVI-001 | Toast 연속 발생 처리 | 복수 Toast 연속 발생 시 표시 순서/덮어쓰기 정책 미확정 |
| PEND-NAVI-002 | Toast 자동 사라짐 시간 | HIDE_TOAST 자동 디스패치 타이밍(ms) 기획서 미명시 |
| PEND-NAVI-003 | 주문 실행 Toast 문구 | Market/Limit 주문 실행 Toast 정확한 문구 미확정 (parsed_content에 "Toast 표시"만 명시) |

---

## 공통 정책

### 앱 전역 상태 (AppContext)

| 상태 키 | 타입 | 초기값 | 설명 |
|---------|------|--------|------|
| isLoggedIn | boolean | false | 로그인 여부 |
| hasAcceptedTerms | boolean | false | 약관 동의 여부 |
| hasCompletedOnboarding | boolean | false | 온보딩 완료 여부 |
| hasSeenLeverageNotice | boolean | false | 레버리지 안내 확인 여부 |
| selectedCoin | Coin | BTC-USDC | 선택된 코인 |
| leverage | number | 2 | 현재 레버리지 (1~2) |
| orderType | string | "market" | 주문 유형 (limit/market) |
| autoTpSlEnabled | boolean | true | 자동 TP/SL 활성 여부 |
| takeProfitPercent | number | 1.8 | TP 퍼센트 |
| stopLossPercent | number | 5.0 | SL 퍼센트 |
| positions | Position[] | DEFAULT_POSITIONS | 보유 포지션 (초기 2개: XRP Short, BTC Long) |
| openOrders | OpenOrder[] | [] | 미체결 주문 |
| activeTab | TabKey | "trade" | 현재 활성 탭 |
| toastMessage | string\|null | null | 토스트 메시지 |
| signalState | SignalState | INITIAL_SIGNAL_STATE | 시그널 상태 |
| prefillData | SignalPrefill\|null | null | 시그널→주문폼 자동 채우기 |
| language | Language | "en" | 언어 설정 (localStorage 기반) |

### 색상 규칙 (전역)

| 의미 | 색상 코드 |
|------|-----------|
| Long / 수익 / 긍정 | #00de0b (녹색) |
| Short / 손실 / 경고 | #ff5938 (빨강) |
| 배경 기본 | #050505 |
| 로그인 버튼 | #0b34a4 (파랑) |

### Hyperliquid Testnet 특이사항 (Phase 3 단일 거래소)

| 항목 | 내용 |
|------|------|
| Auto TP/SL 지원 | 지원 (Partial TP/SL 방식) |
| TP/SL 유형 | Partial (수량 단위) |
| TP/SL Limit 주문 | 지원 |
| Open Orders TP/SL 수정 버튼 | 없음 — 해당 TC는 N/A 처리 |
| 레버리지 연동 | Position과 Order Form 레버리지 연동 |
| 초기 자금 | 100 USDC (Testnet 가상 자금) |

### TP/SL 유형 동작 규칙 (Hyperliquid: Partial)

- TP/SL 주문은 수량 단위로 생성
- 동일 방향 추가 주문: 새 TP/SL 주문 추가 생성 (기존 유지)
- 반대 방향 소량 주문: 기존 TP/SL 유지, 수량만 감소
- 반대 방향 대량 주문 (포지션 스위칭): 기존 TP/SL 전체 취소 → 새 방향으로 신규 생성

### 우선순위 규칙

```
수동 TP/SL > Auto TP/SL
```
- 주문폼에서 수동으로 TP/SL 입력한 경우: 수동 입력값 적용
- Auto TP/SL ON 상태라도 수동 입력 있으면 수동값 우선

### 신규 기능 (Phase 3 추가, Phase 2 대비)

| 신규 기능 | 설명 |
|----------|------|
| 언어 전환 (EN/KO) | Settings > Language 섹션, 전체 UI i18n 적용 |
| 포트폴리오 페이지 | 포지션 PnL 실시간 계산, 종합 수익률 표시 |
| 오더북 컴포넌트 | 거래 화면 내 호가창 표시 |
| 시그널 주문 연동 | SignalOrderSheet — 레버리지/주문유형/수량 설정 후 즉시 주문 |
| About 섹션 | Settings > About (웹사이트/문서 링크, 거래소 Coming Soon 배지) |

---

## 전체 [미결] 항목 목록

| ID | 도메인 | 항목 | 내용 | 출처 |
|----|--------|------|------|------|
| PEND-AUTH-001 | AUTH | LeverageNotice 노출 조건 | 최초 1회 / 매 로그인마다 미확정 (`hasSeenLeverageNotice` 쿠키/세션 범위) | tc-rules-override.md |
| PEND-AUTH-002 | AUTH | 초기 지급 잔고 표시 | 코드 기준 100.0 USDC, 화면 100,000 USDC — 단위 변환 정책 확인 필요 | tc-rules-override.md |
| PEND-AUTH-003 | AUTH | 온보딩 중 뒤로가기 처리 | 기획서에 명시 없음 — 중단/재시작 여부 미확정 | parsed_content.md |
| PEND-AUTH-004 | AUTH | 로그인 상태 유지 범위 | 앱 재시작/새로고침 시 `isLoggedIn` 상태 유지 여부 미확정 | parsed_content.md |
| PEND-TRAD-001 | TRAD | 오더북 데이터 소스 | 목업 데이터 vs 실제 Hyperliquid API 연동 미확정 | tc-rules-override.md |
| PEND-TRAD-002 | TRAD | 수량 0 주문 처리 | 수량 미입력 또는 0 입력 시 주문 버튼 동작 정책 미확정 | parsed_content.md |
| PEND-TRAD-003 | TRAD | 잔고 부족 검증 | 잔고 부족 시 주문 거부 처리 여부 미확정 | parsed_content.md |
| PEND-TRAD-004 | TRAD | Limit 주문 가격 미입력 처리 | Limit 선택 후 가격 미입력 시 주문 버튼 동작 미확정 | parsed_content.md |
| PEND-SIGN-001 | SIGNAL | 시그널 주문 수량 단위 | USD 금액 vs 코인 수량 미확정 (Margin 입력 단위) | tc-rules-override.md |
| PEND-SIGN-002 | SIGNAL | Margin 상한 검증 | Margin 입력값이 가용 잔고 초과 시 처리 정책 미확정 | parsed_content.md |
| PEND-SIGN-003 | SIGNAL | 중복 시그널 주문 | 동일 시그널 중복 Execute 방지 정책 미확정 | parsed_content.md |
| PEND-SIGN-004 | SIGNAL | 시그널 데이터 갱신 | 목업 고정 데이터 vs 실시간 API 갱신 미확정 | parsed_content.md |
| PEND-PORT-001 | PORT | 최근 활동 데이터 갱신 | 목업 고정 데이터 — 실제 API 연동 시 동적 표시 정책 미확정 | parsed_content.md |
| PEND-PORT-002 | PORT | PnL = 0 색상 처리 | PnL이 정확히 0인 경우 표시 색상 미확정 | parsed_content.md |
| PEND-PORT-003 | PORT | ACCOUNT.balance 0 처리 | 잔고 0 시 pnlPercent 계산 (0으로 나누기) 예외 처리 미확정 | parsed_content.md |
| PEND-SETS-001 | SETS | Auto TP/SL OFF 시 Edit 동작 | OFF 상태에서 Edit → Confirm 시 ON 자동 전환 여부 미확정 | parsed_content.md |
| PEND-SETS-002 | SETS | TP or SL 단독 0 입력 처리 | TP=0이고 SL>0인 경우 Confirm 버튼 활성 여부 미확정 | parsed_content.md |
| PEND-SETS-003 | SETS | 언어 전환 후 Toast 언어 | 언어 전환 직후 Toast 메시지 언어 적용 시점 미확정 | parsed_content.md |
| PEND-SETS-004 | SETS | 저장 실패 Toast 문구 | Auto TP/SL 저장 실패 시 에러 Toast 정확한 문구 미확정 | 03_TC_Policy_AutoTPSL.md |
| PEND-NAVI-001 | NAVI | Toast 연속 발생 처리 | 복수 Toast 연속 발생 시 표시 순서/덮어쓰기 정책 미확정 | parsed_content.md |
| PEND-NAVI-002 | NAVI | Toast 자동 사라짐 시간 | HIDE_TOAST 자동 디스패치 타이밍(ms) 기획서 미명시 | parsed_content.md |
| PEND-NAVI-003 | NAVI | 주문 실행 Toast 문구 | Market/Limit 주문 실행 Toast 정확한 문구 미확정 | parsed_content.md |

---

*이 문서는 policy-analyst 에이전트가 자동 생성한 정책 문서입니다. 생성일: 2026-04-03*
