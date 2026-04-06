# 개발 기능 목록 — Supercycl 모바일 체험

> 작성 일시: 2026-04-01
> 기준 문서: policy_doc.md

---

## [인증 — 가입 및 로그인]

| 기능 ID | 기능명 | 설명 | 우선순위 | 비고 |
|---------|--------|------|----------|------|
| F-001 | Google OAuth 원클릭 가입/로그인 | QR 스캔 후 Google OAuth 단독으로 가입·로그인 처리 (이메일/비밀번호 없음) | High | FE+BE |
| F-002 | 약관 동의 페이지 렌더링 | `/terms` 경로에서 약관 내용, 체크박스, Accept/Decline 버튼 표시 | High | FE |
| F-003 | 약관 체크박스 미동의 시 Accept 버튼 비활성화 | 체크박스 미체크 상태에서 Accept 버튼 클릭 불가 처리 | High | FE |
| F-004 | 약관 동의 후 온보딩 진입 | Accept 클릭 시 `hasAcceptedTerms` 상태 업데이트 후 `/onboarding`으로 이동 | High | FE |
| F-005 | Decline 클릭 시 랜딩 페이지 이동 | Decline 버튼 클릭 시 `/`(LandingPage)로 이동 | High | FE |
| F-006 | 전역 인증 상태 관리 | `isLoggedIn`, `hasAcceptedTerms`, `hasCompletedOnboarding` 상태로 흐름 관리 | High | FE |
| F-007 | 라우트 가드 — 미인증 리다이렉트 | 로그인 필요 페이지 직접 접근 시 `/`로 리다이렉트 | High | FE |
| F-008 | in-app 브라우저 비호환 안내 | 카카오톡, 네이버 등 in-app 브라우저 접속 시 외부 브라우저 안내 메시지 표시 | Medium | FE; [미결] 안내 방법 미정 |

### 상세 설명
- F-001: 목업에서 Google OAuth는 시뮬레이션 처리 (실제 API 호출 없음), iOS Safari 및 Android Chrome 공식 지원
- F-007: `/terms`는 로그인 후 약관 미동의 상태, `/onboarding`은 약관 동의 후 온보딩 미완료 상태, `/trade`는 온보딩 완료 상태에서만 접근 허용

---

## [온보딩 — 지갑 자동 생성 및 자금 지급 (3단계 분리)]

| 기능 ID | 기능명 | 설명 | 우선순위 | 비고 |
|---------|--------|------|----------|------|
| F-009 | 온보딩 단계 1 — 지갑 자동 생성 | 타이머 기반 시뮬레이션, 약 1.2초 후 완료 표시 | High | FE+BE |
| F-010 | 온보딩 단계 2 — Testnet 연결 | 타이머 기반 시뮬레이션, 약 2.2초 후 완료 표시 | High | FE+BE |
| F-011 | 온보딩 단계 3 — 테스트 자금 로딩 | 타이머 기반 시뮬레이션, 약 3.2초 후 완료(`completed=true`) 표시 | High | FE+BE |
| F-012 | 온보딩 완료 화면 표시 | 단계 3 완료 후 체크마크 + USDC 잔액(1,000.0) + CEX 안내 문구 + "Start Trading" 버튼 노출 | High | FE |
| F-013 | "Start Trading" 버튼 동작 | 클릭 시 `COMPLETE_ONBOARDING` 디스패치 후 `/trade`로 이동 | High | FE |
| F-014 | 마스터 지갑 → 유저 지갑 mock USDC 전송 | 가입 즉시 마스터 지갑에서 유저 지갑으로 1,000 mock USDC 전송 (10초 이내 잔고 반영) | High | BE |
| F-015 | 자금 전송 지연 시 안내 메시지 | 잔고 표시 지연(~10초) 발생 시 유저에게 안내 메시지 노출 | Medium | FE |
| F-016 | 자금 전송 실패 처리 | 전송 실패 시 재시도 또는 오류 안내 처리 | High | BE; [미결] 재시도 정책 및 에러 처리 방안 미정 |
| F-017 | 기본 계정 잔고 상수 적용 | `ACCOUNT.balance = 1,000.0 USDC` 상수로 초기 잔고 설정 | High | FE+BE |

### 상세 설명
- F-009~F-011: 3단계 각각 독립적 완료 상태를 가지며, UI에서 단계별 진행 상태(진행 중/완료) 표시
- F-014: Hyperliquid Testnet Faucet은 메인넷 $5 USDC 이력 필요로 자동 생성 지갑에서 직접 사용 불가 → 마스터 지갑 Transfer 방식 사용

---

## [레퍼럴 코드 자동 등록]

| 기능 ID | 기능명 | 설명 | 우선순위 | 비고 |
|---------|--------|------|----------|------|
| F-018 | 파트너 코드 상수 하드코딩 | `PARTNER_CODE = "YOUTHMETA"` 상수 정의 | Medium | FE+BE |
| F-019 | URL 파라미터 `partner_code` 파싱 | 체험 URL의 `partner_code=YOUTHMETA` 파라미터 추출 | Medium | FE |
| F-020 | 가입 시 레퍼럴 코드 자동 태깅 | 가입 프로세스에서 추출한 `YOUTHMETA` 코드를 계정에 자동 등록 | Medium | BE |
| F-021 | `partner_code` 누락 시 처리 | URL에 `partner_code` 파라미터 없는 경우 처리 | Medium | FE+BE; [미결] 수동 등록 가능 여부 등 처리 방안 미정 |

---

## [레버리지 — 2배 고정 제한]

| 기능 ID | 기능명 | 설명 | 우선순위 | 비고 |
|---------|--------|------|----------|------|
| F-022 | `MAX_LEVERAGE=2` 상수 적용 | 레버리지 최대값 2배 하드코딩 상수 정의 및 적용 | High | FE+BE |
| F-023 | `MIN_LEVERAGE=1` 상수 적용 | 레버리지 최소값 1배 하드코딩 상수 정의 및 적용 | High | FE+BE |
| F-024 | `DEFAULT_LEVERAGE=2` 기본값 적용 | 신규 계정 레버리지 기본값 2배 설정 | High | FE+BE |
| F-025 | LeverageNotice 팝업 최초 1회 표시 | `hasSeenLeverageNotice=false` 시 TradingPage 진입 시 최초 1회만 팝업 노출 | High | FE |
| F-026 | LeverageNotice 팝업 문구 표시 | "This account has a maximum leverage limit of 2x under the user protection policy." 문구 표시 | High | FE; [미결] 언어(한국어/영어) 확인 필요 |
| F-027 | LeverageNotice "I Understand" 버튼 동작 | 클릭 시 `DISMISS_LEVERAGE_NOTICE` 디스패치 → 이후 재표시 없음 | High | FE |
| F-028 | LeverageNotice와 AdjustLeverage 모달 노출 순서 | TradingPage 진입 시 LeverageNotice 팝업이 AdjustLeverage 모달보다 선행 표시 | High | FE |
| F-029 | AdjustLeverage 모달 슬라이더 범위 제한 | 슬라이더 범위 1~2 (step=1), 2배 초과 설정 불가 | High | FE |
| F-030 | AdjustLeverage 모달 경고 배너 표시 | "Max leverage limited to 2x (User Protection)" 문구를 `--accent-yellow` 색상으로 표시 | High | FE |

---

## [자동 TP/SL (Auto Take Profit / Stop Loss)]

| 기능 ID | 기능명 | 설명 | 우선순위 | 비고 |
|---------|--------|------|----------|------|
| F-031 | `DEFAULT_TP_PERCENT=1.8` 상수 적용 | 기본 익절 비율 1.8% 하드코딩 상수 정의 및 적용 | High | FE+BE; [미결] 최종 확정값 여부 확인 필요 |
| F-032 | `DEFAULT_SL_PERCENT=5.0` 상수 적용 | 기본 손절 비율 5.0% 하드코딩 상수 정의 및 적용 | High | FE+BE; [미결] 최종 확정값 여부 확인 필요 |
| F-033 | `autoTpSlEnabled` 전역 상태 관리 | Auto TP/SL 활성화 여부를 전역 상태로 관리 | High | FE |
| F-034 | AutoTpSlModal 표시 | Auto TP/SL 설정 전용 모달 렌더링 | High | FE |
| F-035 | AutoTpSlModal 확인 버튼 활성화 조건 | `tpNum > 0` OR `slNum > 0` 중 하나 이상 충족 시에만 확인 버튼 활성화 | High | FE |
| F-036 | OrderForm Auto TP/SL 인디케이터 표시 | `autoTpSlEnabled=true` 시 OrderForm에 TP%/SL% + Edit 버튼 표시 | High | FE |
| F-037 | PositionCard Auto 배지 표시 | `isAuto=true` 포지션에 녹색 Auto 배지(9px 폰트) 표시 | High | FE |
| F-038 | PositionCard TP/SL 조건부 렌더링 | `position.tp` 또는 `position.sl` 값 존재 시에만 TP/SL 표시 | High | FE |
| F-039 | SettingsPage Auto TP/SL 토글 스위치 | ON=녹색, OFF=기본 배경, 클릭 시 `TOGGLE_AUTO_TP_SL` 디스패치 | High | FE |
| F-040 | Settings → Trading Preferences → Auto TP/SL Edit 접근 | Settings 탭 → Trading Preferences 섹션 → Auto TP/SL Edit 버튼 경로 동작 | High | FE |
| F-041 | Auto TP/SL 초기 기본 상태 | 신규 가입 계정의 Auto TP/SL 초기 ON/OFF 상태 설정 | High | FE; [미결] 초기 ON/OFF 여부 확인 필요 |

---

## [거래 — 주문 및 포지션]

| 기능 ID | 기능명 | 설명 | 우선순위 | 비고 |
|---------|--------|------|----------|------|
| F-042 | 지원 코인 8종 목록 표시 | BTC-USDC, ETH-USDC, SOL-USDC, DOGE-USDC, ARB-USDC, AVAX-USDC, MATIC-USDC, LINK-USDC 표시 | High | FE |
| F-043 | 주문 타입 선택 (limit/market/conditional) | 3종 주문 타입 선택 UI 제공 | High | FE |
| F-044 | limit/conditional 주문 가격 입력 필드 표시 | limit 또는 conditional 선택 시 가격 입력 필드 표시 | High | FE |
| F-045 | market 주문 가격 입력 필드 숨김 | market 선택 시 가격 입력 필드 숨김 처리 | High | FE |
| F-046 | OrderForm 크기 슬라이더 (0~100%) | 주문 수량 퍼센트 슬라이더 0~100% 범위 제공 | High | FE |
| F-047 | Long/Short 주문 실행 | Long/Short 버튼 클릭 → `PLACE_ORDER` 디스패치 → Toast 알림 | High | FE |
| F-048 | OrderConfirm 모달 표시 | 주문 제출 전 주문 내용 확인 모달 노출 | High | FE |
| F-049 | `prefillData` 기반 OrderForm 자동 채움 | `prefillData` 존재 시 OrderForm 초기값 자동 설정 | High | FE |
| F-050 | Dashboard Positions 탭 표시 | 보유 포지션 목록 표시 | High | FE |
| F-051 | Dashboard Open Orders 탭 빈 상태 | "No open orders" 빈 상태 표시 (미구현 탭) | Medium | FE; [미결] 구현 여부 불명확 |
| F-052 | Dashboard History 탭 빈 상태 | "No order history" 빈 상태 표시 (미구현 탭) | Medium | FE; [미결] 구현 여부 불명확 |
| F-053 | PositionCard PnL 색상 표시 | 수익 ≥ 0 → 녹색, 손실 < 0 → 빨간색 (좌측 보더 색상 동일) | High | FE |
| F-054 | CloseConfirm 모달 표시 | 포지션 청산 전 확인 모달 노출 | High | FE |
| F-055 | portfolio 탭 미구현 안내 | "coming in the next version" 메시지 표시 | Low | FE |

---

## [시그널 (YouthMeta Signals)]

| 기능 ID | 기능명 | 설명 | 우선순위 | 비고 |
|---------|--------|------|----------|------|
| F-056 | 시그널 탭 헤더 표시 | "⚡ YouthMeta Signals" 헤더 렌더링 | Medium | FE; [미결] 행사 체험 범위 포함 여부 확인 필요 |
| F-057 | 성과 요약 카드 표시 (최근 30일) | Hit/Miss/Expired 건수, 평균 PnL%, 성공률% 표시 | Medium | FE |
| F-058 | 성공률 색상 분기 처리 | ≥70%=녹색, ≥50%=주황색, <50%=빨간색 색상 적용 | Medium | FE |
| F-059 | 시그널 필터 탭 (ALL/LONG/SHORT/ACTIVE/CLOSED) | 가로 스크롤 지원 필터 탭 UI 제공 | Medium | FE |
| F-060 | CLOSED 상태 집합 처리 | HIT_TP, HIT_SL, EXPIRED, CANCELLED 상태를 CLOSED로 분류 | Medium | FE |
| F-061 | SignalOrderSheet 바텀시트 표시 | 코인, 방향, 진입가, 타겟가, 손절가, 레버리지 정보 표시 | Medium | FE |
| F-062 | Execute 시그널 즉시 주문 실행 | `EXECUTE_SIGNAL_ORDER` 디스패치 + Toast 알림 | Medium | FE |
| F-063 | Modify 시그널 값 OrderForm 로드 | `PREFILL_FROM_SIGNAL` 디스패치 → OrderForm에 신호값 자동 입력 후 유저 수정 | Medium | FE |

---

## [Testnet UI 및 CEX 연동 안내]

| 기능 ID | 기능명 | 설명 | 우선순위 | 비고 |
|---------|--------|------|----------|------|
| F-064 | LandingPage "TESTNET MODE" 배너 표시 | 하단 "TESTNET MODE" 배너 상시 노출 | Medium | FE |
| F-065 | SettingsPage Exchange Connection 섹션 표시 | Hyperliquid 테스트넷 연결 상태 표시 | Medium | FE |
| F-066 | OnboardingPage 완료 화면 CEX 안내 문구 | "CEX 통합 예정 안내 문구" 노출 | Medium | FE; [미결] 문구 포함 여부 최종 확인 필요 |
| F-067 | TESTNET 배지 + "실제 자금 아님" 고지 | TESTNET 배지 및 "실제 자금이 아님" 고지 문구 표시 | Medium | FE |
| F-068 | HL Testnet API 엔드포인트 연동 | `api.hyperliquid-testnet.xyz` (Chain ID: 998) 연동 | Medium | BE |

---

## [모바일 반응형 UI]

| 기능 ID | 기능명 | 설명 | 우선순위 | 비고 |
|---------|--------|------|----------|------|
| F-069 | 최대 너비 320px 모바일 레이아웃 | 전체 앱 최대 너비 320px, 전체 높이 100dvh 적용 | High | FE |
| F-070 | Order Form 모바일 터치 최적화 | Order Form 터치 인터랙션 최적화 | High | FE |
| F-071 | Dashboard 모바일 터치 최적화 | Dashboard 터치 인터랙션 최적화 | High | FE |
| F-072 | Chart 모바일 레이아웃 | Chart 컴포넌트 모바일 최적화 | High | FE |
| F-073 | Coin Info Bar 모바일 레이아웃 | Coin Info Bar 모바일 최적화 | High | FE |
| F-074 | BottomNav 4탭 고정 하단 네비게이션 | trade/signal/portfolio/settings 4탭 하단 고정 네비게이션 바 | High | FE |
| F-075 | 탭 콘텐츠 스크롤 + 하단 64px 여백 | 탭 콘텐츠 영역 스크롤 가능, 하단 BottomNav 64px 여백 확보 | High | FE |
| F-076 | 다크 테마 배경색 `#0a0a0a` 적용 | 전체 배경색 `#0a0a0a` 다크 테마 적용 | High | FE |
| F-077 | CSS 변수 체계 적용 | `--color-pri-1`, `--text-secondary`, `--accent-green`, `--accent-red`, `--accent-yellow` CSS 변수 사용 | High | FE |
| F-078 | LandingPage 페이드인 애니메이션 | 0.15s/0.3s/0.45s 순차 페이드인 애니메이션 적용 | Low | FE |
| F-079 | LoginPage 페이드인 애니메이션 | 0.3s 페이드인 애니메이션 적용 | Low | FE |

---

## [설정 — SettingsPage]

| 기능 ID | 기능명 | 설명 | 우선순위 | 비고 |
|---------|--------|------|----------|------|
| F-080 | Account 섹션 이메일/지갑 주소 표시 | `ACCOUNT.email`, `ACCOUNT.wallet` 정보 표시 | Medium | FE |
| F-081 | 지갑 주소 복사 버튼 | 복사 클릭 시 Toast "Address copied!" 표시 | Medium | FE |
| F-082 | Trading Preferences — Auto TP/SL 설정값 표시 | 현재 TP/SL %(%) 값 표시 + Edit 버튼 | High | FE |
| F-083 | Trading Preferences — Auto TP/SL 토글 | ON=녹색, OFF=기본색 토글 스위치 | High | FE |
| F-084 | Exchange Connection 섹션 — 테스트넷 연결 상태 | Hyperliquid 테스트넷 연결 상태 표시 | Medium | FE |
| F-085 | Logout 버튼 (목업 Toast) | 빨간색 테두리 Logout 버튼 클릭 시 목업 Toast 메시지 표시 (실제 세션 종료 없음) | Medium | FE |

---

## [온보딩 가이드 (Coach Mark)]

| 기능 ID | 기능명 | 설명 | 우선순위 | 비고 |
|---------|--------|------|----------|------|
| F-086 | Coach Mark 단계별 가이드 표시 | 첫 접속 시 단계별 Coach Mark 및 기능 하이라이트 표시 | Low | FE; [미결] 세부 내용 및 화면별 포인트 미정 (P2, 미구현 가능) |

---

## 기술 고려사항
- `MAX_LEVERAGE=2`, `MIN_LEVERAGE=1`, `DEFAULT_LEVERAGE=2`, `DEFAULT_TP_PERCENT=1.8`, `DEFAULT_SL_PERCENT=5.0`, `PARTNER_CODE="YOUTHMETA"`, `ACCOUNT.balance=1000.0`은 `defaults.ts` 상수 파일에 집중 관리
- 기술 스택: React 19 + TypeScript + Vite, react-router-dom v7, React Context API (AppContext)
- 라우트 구성: `/`(LandingPage), `/login`(LoginPage), `/terms`(TermsPage), `/onboarding`(OnboardingPage), `/trade`(TradingPage)
- HL Testnet API: `api.hyperliquid-testnet.xyz`, Chain ID 998 (메인넷과 혼동 주의)
- DevNav 컴포넌트는 개발용 도구로 프로덕션 배포 전 반드시 제거
- 1,000명 동시 가입 시 자금 전송 병목 가능 → 마스터 지갑 분산 처리 + 큐 시스템으로 대응 필요
- iOS Safari, Android Chrome in-app 브라우저 Google OAuth 호환성 사전 검증 필수
- LeverageNotice → AdjustLeverage 모달 노출 순서 준수 (F-028)
- `[미결]` 표시 항목은 TC 작성 전 PM/개발팀 확인 후 스펙 확정 필요
