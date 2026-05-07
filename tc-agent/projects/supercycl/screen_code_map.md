# Supercycl Mobile — Screen Code Map

> Mobile TC ID 매핑 + **성격(character)** + **네비게이션(navigation)** 지정.
> 포맷: `| {Middle} | {Code} | {성격} | {네비} | {SCR-ID} | {설명} |`
> `load_screen_code_map()`가 파싱하여 프롬프트에 힌트로 전달한다.

## 사용 규칙

- 규칙 1. Middle Name은 스펙의 화면명 또는 중분류 레이블과 **정확히 일치**. 대소문자 구분.
- 규칙 2. ScreenCode는 프로젝트 내 **유니크**.
- 규칙 3. 여기 없는 중분류는 자동 파생 (영문 3자, 한글은 `MIDxxx`).
- 규칙 4. TC ID 포맷: `SM-{ScreenCode}-{NNN}` (화면별 001~).
- 규칙 5. **성격(character)** → 비기능 TC 생성 기준 (원칙 E).
- 규칙 6. **네비게이션(navigation)** → 뒤로가기/스와이프 TC 생성 기준 (원칙 F).

## 성격 (character) — 6종

| 성격 | 의미 | 필수 비기능 TC |
|------|------|--------------|
| `entry` | 앱 진입·로그인 flow 첫 화면 | 로딩 시간 3초 |
| `data-fetch` | API 리스트/상세 조회 | 초기 로딩 5초 + 빈 상태 + Pull-refresh |
| `realtime` | WebSocket 실시간 갱신 | 끊김 복원 + 지연 배너 |
| `form` | 사용자 입력 중심 | 입력 반응 100ms (선택) |
| `overlay` | 바텀시트·모달 | 외부 탭 닫힘 + 애니메이션 |
| `static` | 정적 컨텐츠 | 없음 |

## 네비게이션 (navigation) — 6종

| 네비 | 기대 동작 | 필수 TC |
|------|---------|--------|
| `tab-root` | 탭바 최상위, 뒤로가기 시 앱 종료/Splash | 뒤로가기 시 종료 처리 |
| `one-way` | **이전 화면 복귀 금지** (완료 후) | 뒤로가기/스와이프 차단 또는 홈 이동 |
| `sequential` | 이전 단계 복귀 + 입력값 유지 | 이전 화면 이동 + state preserved |
| `overlay` | 오버레이만 닫힘 | 뒤로가기/외부 탭 → dismiss |
| `detail` | 리스트 복귀 + 스크롤 위치 | 뒤로 → 리스트 + scroll restore |
| `static` | 기본 네비 | 별도 TC 불필요 (depth 2+ 에서만 확인) |

---

## 매핑 테이블

### 온보딩 / 인증 (Login)

| Middle Name | ScreenCode | 성격 | 네비 | SCR-ID | 설명 |
|-------------|------------|------|------|--------|------|
| Splash | SPL | entry | tab-root | SCR-001 | 앱 시작 화면 (진입점) — v0.32 이전 별칭 |
| Login Options | LGI | entry | sequential | SCR-002 | 로그인 옵션 선택 — v0.32 이전 별칭 |
| Login | LGN | entry | sequential | SCR-001 | 첫 진입 화면 (v0.32+ 통합 — 슬로건+로고+로그인 옵션 3개 병렬) |
| Email Input | EML | form | sequential | SCR-003 | 이메일 입력 |
| Email 로그인 | EML | form | sequential | SCR-003 | Email Input 별칭 |
| Verification Code | VCD | form | sequential | SCR-005 | 인증 코드 입력 |
| Terms Consent | TRM | form | sequential | SCR-007 | 약관 동의 |
| Terms of Use | TOU | static | static | SCR-007A | 이용약관 본문 |
| Privacy Policy | PRV | static | static | SCR-007B | 개인정보 처리방침 |
| Marketing Consent | MKN | static | static | SCR-007C | 마케팅 수신 동의 |
| Verifying Code | VFY | entry | one-way | SCR-008 | 검증 로딩 (뒤로가기 차단) |
| Login Complete | LGC | entry | one-way | SCR-009 | 로그인 완료 (**뒤로가기 차단** — 인증 재실행 방지) |
| Google Sign-in | GGL | entry | sequential | SCR-010 | Google OAuth 흐름 |
| Google Sign-in Start | GGL | entry | sequential | SCR-010 | Google OAuth 흐름 — Google Sign-in 별칭 (spec v0.47+ 명칭) |
| Google Account Select | GAS | form | sequential | SCR-011 | Google 계정 선택 웹뷰 |
| Google Account List | GAL | form | sequential | SCR-012 | Google 계정 목록 (다수 계정) |
| Supercycl OAuth Confirm | SOC | form | sequential | SCR-013 | Google OAuth 권한 확인 웹뷰 |
| Google Sign-in Complete | GSC | entry | one-way | SCR-014 | Google 로그인 완료 (SCR-009 와 동일 패턴 — 인증 재실행 방지) |
| QR Code Login | QRL | form | sequential | SCR-017 | QR 스캔 로그인 변형 |
| QR Scan (Login) | QRL | form | sequential | SCR-017 | QR Code Login 별칭 (spec v0.47+ 명칭) |
| QR Scan Complete | QRS | entry | one-way | SCR-021 | QR 연결 성공 (**뒤로가기 차단**) |

### Trade (Lite Mode)

| Middle Name | ScreenCode | 성격 | 네비 | SCR-ID | 설명 |
|-------------|------------|------|------|--------|------|
| Trade Lite | TLT | realtime | tab-root | SCR-102 | 탭바 Trade 진입점 |
| Trade (Lite) | TLT | realtime | tab-root | SCR-102 | Trade Lite 별칭 (spec v0.47+ 명칭) |
| Order Confirm | ORC | overlay | overlay | SCR-104 | 주문 확인 시트 |
| Trade Lite Alert | TLA | realtime | tab-root | SCR-105 | 알림 배너 변형 |
| Positions | POS | realtime | detail | SCR-106 | 포지션 카드 (Trade Lite 하위) |
| Order History | OHS | data-fetch | detail | SCR-107 | Lite 주문 내역 |
| Guide | GDE | static | static | SCR-112 | 가이드 섹션 |
| Cross Margin Sheet | CMS | overlay | overlay | SCR-113 | Cross Margin 첫 사용 |
| Margin Mode Sheet | MMS | overlay | overlay | SCR-114 | Isolated/Cross 선택 |
| Cancel Order Modal | COM | overlay | overlay | SCR-115 | 주문 취소 확인 모달 |
| Open Orders | OPO | data-fetch | detail | SCR-116 | 미체결 주문 리스트 |
| Open Orders List | OPO | data-fetch | detail | SCR-116 | Open Orders 별칭 (spec v0.47+ 명칭) |

### Markets / Portfolio

| Middle Name | ScreenCode | 성격 | 네비 | SCR-ID | 설명 |
|-------------|------------|------|------|--------|------|
| Markets | MKT | realtime | tab-root | SCR-401 | 탭바 Markets 진입점 |
| Portfolio | PRT | realtime | tab-root | SCR-402 | 탭바 Portfolio 진입점 |
| PnL Analysis | PNL | data-fetch | detail | SCR-410 | Portfolio 하위 상세 |
| History | HIS | data-fetch | detail | SCR-411 | 거래 이력 허브 (Orders/Positions/Trades 3 탭, 최신 30일) |
| Profile | PRF | data-fetch | tab-root | SCR-403 | 탭바 Profile 진입점 |
| Notifications | NTF | data-fetch | detail | SCR-221 | Profile 하위 상세 |

### Exchange Connect

| Middle Name | ScreenCode | 성격 | 네비 | SCR-ID | 설명 |
|-------------|------------|------|------|--------|------|
| OAuth Connect | OAC | entry | sequential | SCR-801 | OAuth 연동 안내 |
| Connection Result | ECR | entry | one-way | SCR-802 | 연결 결과 (**재연동 방지**) |
| Connecting | ECG | entry | one-way | SCR-803 | 연결 진행 중 (뒤로가기 차단) |
| Connecting... | ECG | entry | one-way | SCR-803 | Connecting 별칭 (spec 의 ... 포함 명칭) |
| Connect Exchange Onboarding | ECO | entry | sequential | SCR-807 | 온보딩 중 최초 연결 |
| Connect Exchange (Onboarding) | ECO | entry | sequential | SCR-807 | Connect Exchange Onboarding 별칭 (spec v0.47+ 괄호 표기) |
| OKX OAuth Webview | OKX | entry | sequential | SCR-808 | OKX 인증 웹뷰 |
| API Key Input | API | form | sequential | SCR-809 | API Key 직접 입력 |
| Edit API Keys | APE | form | detail | SCR-810 | API Key 수정 (Exchange Detail 하위) |
| Fast API Key Conflict | FKC | static | one-way | SCR-811 | OKX fast API key 1개 제한 안내 (해결 가이드 + 재시도 CTA) |
| Connect Exchange | CXM | data-fetch | detail | SCR-205 | 거래소 연결 관리 |
| Disconnect Confirm | EDC | overlay | overlay | SCR-804 | 연결 해제 확인 |
| Reconnect | ERC | entry | sequential | SCR-805 | 재연결 |
| Exchange Detail | EXD | data-fetch | detail | SCR-806 | 거래소 상세 |

### Shared Errors

| Middle Name | ScreenCode | 성격 | 네비 | SCR-ID | 설명 |
|-------------|------------|------|------|--------|------|
| Email Error | EER | static | static | SCR-501 | 이메일 오류 |
| Code Error | CER | static | static | SCR-502 | 인증 코드 오류 |
| Insufficient Balance | IBE | static | static | SCR-503 | 잔액 부족 |
| Network Error | NER | static | static | SCR-504 | 네트워크 오류 |
| Server Error | SER | static | static | SCR-505 | 서버 오류 |

### Shared Order Results

| Middle Name | ScreenCode | 성격 | 네비 | SCR-ID | 설명 |
|-------------|------------|------|------|--------|------|
| Order Success | ORS | entry | one-way | SCR-601 | 주문 성공 (**재주문 방지**) |
| Order Failed | ORF | entry | one-way | SCR-602 | 주문 실패 (**재주문 방지**) |

### Shared Components

| Middle Name | ScreenCode | 성격 | 네비 | SCR-ID | 설명 |
|-------------|------------|------|------|--------|------|
| Coin Selector | CSL | overlay | overlay | SCR-701 | 코인 선택 바텀시트 |

---

## Code Collision Check

```
예약 ScreenCode:
  SPL LGI EML VCD TRM TOU PRV MKN VFY LGC GGL QRL QRS
  TLT ORC TLA POS OHS GDE CMS MMS COM OPO
  MKT PRT PNL PRF NTF
  OAC ECR ECG ECO OKX API APE CXM EDC ERC EXD
  EER CER IBE NER SER ORS ORF CSL
```

## 자동 추론 (맵에 없을 때)

- **ScreenCode**: 영문 3자 uppercase → 부족하면 `MID{hash}`
- **성격**: `form` (기본 — 상호작용 화면 가정)
- **네비게이션**: 성격 기반 추론 (overlay→overlay, static→static, 그 외 sequential)

**⚠️ `one-way` / `tab-root` / `detail`은 자동 추론하지 않음** — 잘못된 차단 로직은 UX 훼손이므로 사람이 직접 매핑해야 한다.
