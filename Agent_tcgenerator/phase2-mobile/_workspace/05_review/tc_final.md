# TC 최종본 — Supercycl Phase 2 Mobile

> 작성 일시: 2026-04-03
> 검토 버전: v4
> 기준 파일: tc_draft_AUTH.md + tc_draft_LEVR_TPSL.md + tc_draft_TRAD_SGNL_FUND.md + tc_draft_MOBL_SETG_ROUT.md
> 총 TC 수: 127개 (v4 129 → v4.1 127: CEX 팝업 기능 삭제로 -2)
> 커버리지: 84/86 (97.7%) — 삭제된 2기능(AUTH-ONBD-002, MOBL-ONCD-001) 제외
> 적용 수정사항:
>   - [v4] AUTH-INAPP-001 & ROUT-INAP-001 중복 → ROUT-INAP-001 삭제
>   - [v4] AUTH-ONBD-001 THEN: "체크마크 아이콘" → "체크마크 아이콘"
>   - [v4] LEVR-POPUP-002 비고에 [미결] 배경 탭 차단 정책 추가
>   - [v4.1 2026-04-03] AUTH-ONBD-002 삭제 — CEX 안내 팝업 기능 제거됨
>   - [v4.1 2026-04-03] MOBL-ONCD-001 삭제 — CEX 안내 팝업 기능 제거됨
>   - [v4.1 2026-04-03] LEVR-ORDR-001 예상결과 수정 — I Understand 후 Trade 화면 표시 확인으로 명확화

---

## ====== AUTH / REFF 도메인 (F-001~F-021) ======

### ★ AUTH-OAUTH-001 — Google OAuth 로그인 성공 후 약관 페이지 진입 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login → /terms |

**사전 조건**
- 비로그인 상태이다
- `/login` 페이지에 접속해 있다

**테스트 단계**
1. `Sign in with Google` 버튼을 탭한다
2. Google 계정 선택 화면이 표시되면 테스트 계정을 선택한다
3. 화면 이동을 확인한다

**예상 결과**
- Google 계정 선택 완료 후 `/terms` 페이지로 이동한다
- 이메일·비밀번호 입력 필드가 표시되지 않는다

---

### ★ AUTH-OAUTH-002 — 미인증 상태에서 보호 페이지 직접 접근 시 리다이렉트 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade, /onboarding |

**사전 조건**
- 비로그인 상태이다 (Google OAuth 미완료)

**테스트 단계**
1. 브라우저 주소창에 `/trade`를 직접 입력하여 접속을 시도한다
2. 화면 이동을 확인한다
3. 브라우저 주소창에 `/onboarding`을 직접 입력하여 접속을 시도한다
4. 화면 이동을 확인한다

**예상 결과**
- `/trade` 직접 접근 시 `/` (LandingPage)로 리다이렉트된다
- `/onboarding` 직접 접근 시 `/` (LandingPage)로 리다이렉트된다

---

### ★ AUTH-TERMS-001 — 약관 동의 후 온보딩 페이지 진입 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
- Google OAuth 로그인이 완료된 상태이다
- 약관 미동의 상태이다
- `/terms` 페이지에 접속해 있다

**테스트 단계**
1. 약관 내용이 화면에 표시되는지 확인한다
2. 약관 동의 체크박스를 탭한다
3. `Accept` 버튼이 활성화되는지 확인한다
4. `Accept` 버튼을 탭한다

**예상 결과**
- `/onboarding` 페이지로 이동한다

---

### ★ AUTH-TERMS-002 — 체크박스 미선택 시 Accept 버튼 비활성화 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
- Google OAuth 로그인이 완료된 상태이다
- `/terms` 페이지에 접속해 있다

**테스트 단계**
1. 약관 동의 체크박스를 선택하지 않은 상태를 확인한다
2. `Accept` 버튼의 상태를 확인한다
3. `Accept` 버튼을 탭한다

**예상 결과**
- `Accept` 버튼이 비활성화(disabled) 상태이다
- 버튼을 탭해도 페이지 이동이 발생하지 않는다

---

### AUTH-TERMS-003 — 약관 페이지 필수 요소 렌더링 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
- Google OAuth 로그인이 완료된 상태이다
- `/terms` 페이지에 접속해 있다

**테스트 단계**
1. `/terms` 페이지 화면 구성을 확인한다

**예상 결과**
- 약관 본문이 표시된다
- 약관 동의 체크박스가 표시된다
- `Accept` 버튼과 `Decline` 버튼이 표시된다

---

### ★ AUTH-TERMS-004 — Decline 클릭 시 LandingPage 이동 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
- Google OAuth 로그인이 완료된 상태이다
- `/terms` 페이지에 접속해 있다

**테스트 단계**
1. 약관 동의 체크박스를 선택하지 않은 상태에서 `Decline` 버튼을 탭한다

**예상 결과**
- `/` (LandingPage)로 이동한다

---

### ★ AUTH-GUARD-001 — 약관 동의 완료 계정의 /terms 재접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms → /onboarding 또는 /trade |

**사전 조건**
- Google OAuth 로그인이 완료된 상태이다
- 약관 동의가 이미 완료된 계정이다

**테스트 단계**
1. 브라우저 주소창에 `/terms`를 직접 입력하여 접속을 시도한다
2. 화면 이동을 확인한다

**예상 결과**
- `/terms` 페이지가 표시되지 않는다
- 계정 상태에 따라 `/onboarding` 또는 `/trade`로 리다이렉트된다

---

### AUTH-GUARD-002 — 온보딩 완료 계정의 /onboarding 재접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding → /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인된 상태이다

**테스트 단계**
1. 브라우저 주소창에 `/onboarding`을 직접 입력하여 접속을 시도한다
2. 화면 이동을 확인한다

**예상 결과**
- `/onboarding` 페이지가 표시되지 않는다
- `/trade`로 리다이렉트된다

---

### AUTH-INAPP-001 — in-app 브라우저 접속 시 외부 브라우저 안내 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | iOS Safari, Android Chrome |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 카카오톡 또는 네이버 앱 내 채팅창에서 서비스 URL 링크를 탭하여 in-app 브라우저로 접속한 상태이다

**테스트 단계**
1. in-app 브라우저로 서비스 URL에 접속한다
2. 화면에 표시되는 안내를 확인한다

**예상 결과**
- 외부 브라우저(Safari 또는 Chrome)로 열도록 안내하는 메시지가 표시된다

**비고**
- [미결] 안내 방법(모달/배너/페이지 등) 및 구체적인 안내 문구 미정 — 정책 확정 필요

---

## [AUTH] 온보딩 — 지갑 자동 생성 및 자금 지급 (F-009~F-017)

---

### ★ AUTH-ONBD-001 — 온보딩 3단계 순차 진행 및 완료 화면 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- 약관 동의가 완료된 상태이다
- 온보딩 미완료 계정이다
- `/onboarding` 페이지에 접속해 있다

**테스트 단계**
1. 온보딩 화면이 표시되는지 확인한다
2. 단계 1 (지갑 자동 생성) 진행 상태가 표시되는지 확인한다
3. 약 1.2초 후 단계 1이 완료 표시로 전환되는지 확인한다
4. 단계 2 (Testnet 연결) 진행 상태가 표시되는지 확인한다
5. 약 2.2초 후 단계 2가 완료 표시로 전환되는지 확인한다
6. 단계 3 (테스트 자금 로딩) 진행 상태가 표시되는지 확인한다
7. 약 3.2초 후 단계 3이 완료 표시로 전환되는지 확인한다
8. 완료 화면이 표시될 때까지 대기한다

**예상 결과**
- 3단계(지갑 생성 → Testnet 연결 → 테스트 자금 로딩)가 순차적으로 진행 상태와 함께 표시된다
- 각 단계 완료 시 완료 상태(체크마크 아이콘)로 전환된다
- 완료 화면에 체크마크와 USDC 잔액이 표시된다
- `Start Trading` 버튼이 표시된다

**비고**
- [미결] 완료 화면의 초기 잔액 표시 값: 기획서 기준 1,000 USDC / 코드 기준 10,000 USDC — 정책 확정 필요

---

### ★ AUTH-ONBD-003 — "Start Trading" 버튼 탭 후 TradingPage 진입 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding → /trade |

**사전 조건**
- 온보딩 완료 화면이 표시된 상태이다
- `Start Trading` 버튼이 표시된 상태이다

**테스트 단계**
1. `Start Trading` 버튼을 탭한다
2. 화면 이동을 확인한다

**예상 결과**
- `/trade` (TradingPage)로 이동한다

---

### ★ AUTH-FUND-001 — 온보딩 완료 후 초기 USDC 잔고 반영 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | 공통 |
| 연관 화면 | /onboarding, /trade |

**사전 조건**
- 신규 가입 계정이다
- 온보딩 3단계가 완료된 상태이다

**테스트 단계**
1. 온보딩 완료 화면에서 표시된 USDC 잔액을 확인한다
2. `Start Trading` 버튼을 탭하여 TradingPage로 이동한다
3. 잔고 표시를 확인한다

**예상 결과**
- 온보딩 완료 화면에 USDC 잔액이 표시된다
- TradingPage의 잔고 표시가 온보딩 완료 화면의 잔액과 일치한다

**비고**
- [미결] 초기 지급 잔고: 기획서 기준 1,000 USDC / 코드 기준 10,000 USDC — 정책 확정 필요

---

### AUTH-FUND-002 — 자금 전송 지연 시 안내 메시지 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- 온보딩 진행 중 단계 3 (테스트 자금 로딩) 처리가 지연되고 있는 상태이다

**테스트 단계**
1. 단계 3 진행 중 10초 이상 잔고가 표시되지 않는 상황을 확인한다
2. 화면에 표시되는 안내를 확인한다

**예상 결과**
- 잔고 표시 지연 안내 메시지가 화면에 표시된다

**비고**
- [미결] 안내 메시지 구체적인 문구 미정

---

### ★ AUTH-FUND-003 — 자금 전송 실패 시 오류 안내 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | 공통 |
| 연관 화면 | /onboarding |

**사전 조건**
- 온보딩 진행 중 마스터 지갑 → 유저 지갑 자금 전송이 실패한 상태이다

**테스트 단계**
1. 단계 3 (테스트 자금 로딩) 처리 중 전송 실패 상황을 확인한다
2. 화면에 표시되는 오류 안내를 확인한다

**예상 결과**
- 오류 안내 메시지가 화면에 표시된다
- 재시도 또는 다음 단계를 안내하는 UI 요소가 표시된다

**비고**
- [미결] 재시도 정책 및 에러 처리 방안 미정 — 정책 확정 필요 (F-016 비고 항목)

---

### AUTH-CONST-001 — 신규 계정 초기 잔고 상수(1,000 USDC) 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | 공통 |
| 연관 화면 | /onboarding, /trade |

**사전 조건**
- 신규 가입 계정이다
- 온보딩이 완료된 상태이다

**테스트 단계**
1. TradingPage 또는 온보딩 완료 화면에서 잔고를 확인한다

**예상 결과**
- 초기 잔고가 `1,000.0 USDC`로 표시된다

**비고**
- [미결] 코드 기준 10,000 USDC와 상이할 수 있음 — 정책 확정 필요

---

## [REFF] 레퍼럴 코드 자동 등록 (F-018~F-021)

---

### REFF-PARS-001 — URL에 partner_code=YOUTHMETA 포함 시 가입 태깅 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage), /login |

**사전 조건**
- 비로그인 상태이다
- `?partner_code=YOUTHMETA` 파라미터가 포함된 URL로 접속한 상태이다

**테스트 단계**
1. `?partner_code=YOUTHMETA` 파라미터가 포함된 체험 URL로 접속한다
2. Google OAuth 로그인을 완료한다
3. 약관 동의 및 온보딩을 완료한다
4. 계정에 파트너 코드가 등록되었는지 확인한다

**예상 결과**
- 가입 완료 후 계정에 `YOUTHMETA` 파트너 코드가 자동 등록된 상태이다
- 로그인·온보딩 과정에서 파트너 코드 입력 화면이 별도로 표시되지 않는다

**비고**
- [개발 확인] 파트너 코드 태깅 여부는 관리자 화면 또는 API 응답에서 확인 필요

---

### REFF-PARS-002 — URL에 partner_code 누락 시 처리 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage), /login |

**사전 조건**
- 비로그인 상태이다
- `partner_code` 파라미터가 없는 일반 URL로 접속한 상태이다

**테스트 단계**
1. `partner_code` 파라미터 없이 서비스 URL에 접속한다
2. Google OAuth 로그인을 시도한다
3. 로그인 후 화면 흐름을 확인한다

**예상 결과**
- 오류 화면 없이 로그인·약관·온보딩 흐름이 진행된다

**비고**
- [미결] partner_code 누락 시 수동 등록 가능 여부, 기본값 적용 여부 등 처리 방안 미정

---

### REFF-CODE-001 — YOUTHMETA 상수 파트너 코드 적용 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | 공통 |
| 연관 화면 | /login, /onboarding |

**사전 조건**
- `?partner_code=YOUTHMETA`가 포함된 URL로 접속한 신규 가입 계정이다
- 온보딩이 완료된 상태이다

**테스트 단계**
1. 가입 및 온보딩 완료 후 계정 정보 화면(또는 Settings)에서 파트너 코드를 확인한다

**예상 결과**
- 파트너 코드로 `YOUTHMETA`가 등록되어 있다

**비고**
- [신규] 코드 기준 `PARTNER_CODE = "YOUTHMETA"` 상수 정의에서 도출
- [개발 확인] UI에 파트너 코드 노출 화면이 없는 경우 관리자 API 또는 개발자 도구에서 확인 필요

---


## ====== LEVR / TPSL 도메인 (F-022~F-041) ======

### ★ LEVR-CNST-001 — 레버리지 슬라이더 최대값 2배 제한 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- 온보딩이 완료된 상태이다
- TradingPage(`/trade`)에 접속해 있다
- LeverageNotice 팝업을 이미 확인한 상태이다

**테스트 단계**
1. OrderForm 상단의 레버리지 버튼을 탭한다
2. AdjustLeverage 모달이 열리면 슬라이더의 최대값을 확인한다
3. 슬라이더를 오른쪽 끝까지 드래그한다

**예상 결과**
- AdjustLeverage 모달의 슬라이더 최대값이 2x로 표시된다
- 슬라이더를 오른쪽 끝까지 이동해도 2x를 초과하지 않는다
- 레버리지 입력값이 2 이상으로 설정되지 않는다

---

### ★ LEVR-CNST-002 — 레버리지 슬라이더 최솟값 1배 제한 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- TradingPage(`/trade`)에 접속해 있다
- AdjustLeverage 모달이 열려 있는 상태이다

**테스트 단계**
1. 슬라이더를 왼쪽 끝까지 드래그한다
2. 슬라이더의 최솟값을 확인한다

**예상 결과**
- 슬라이더를 왼쪽 끝까지 이동해도 1x 미만으로 내려가지 않는다
- 레버리지 입력값이 1 미만으로 설정되지 않는다

---

### ★ LEVR-CNST-003 — 신규 계정 기본 레버리지 2배 설정 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 신규 계정으로 온보딩을 방금 완료한 상태이다
- TradingPage(`/trade`)에 처음 진입한 상태이다
- LeverageNotice 팝업을 확인한 직후이다

**테스트 단계**
1. OrderForm 상단의 레버리지 버튼을 탭한다
2. AdjustLeverage 모달이 열리면 현재 설정된 레버리지 값을 확인한다

**예상 결과**
- AdjustLeverage 모달에 현재 레버리지 값이 2x로 표시된다

---

### ★ LEVR-POPUP-001 — LeverageNotice 팝업 최초 1회 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정이다
- TradingPage에 최초 진입하는 상태이다 (LeverageNotice를 한 번도 확인하지 않은 상태)
- 온보딩이 완료된 상태이다

**테스트 단계**
1. 온보딩 완료 후 `Start Trading` 버튼을 탭하여 TradingPage에 진입한다
2. 화면에 팝업이 자동으로 표시되는지 확인한다
3. 팝업 내 문구와 버튼을 확인한다

**예상 결과**
- LeverageNotice 팝업이 자동으로 표시된다
- 팝업 제목에 "Leverage Policy Notice"가 표시된다
- "This account has a maximum leverage limit of 2x under the user protection policy." 문구가 표시된다
- `I Understand` 버튼이 표시된다

**비고**
- [미결] 팝업 내 표시 언어(한국어/영어) 미확정 — 정책 확정 후 문구 검증 필요

---

### ★ LEVR-POPUP-002 — LeverageNotice 팝업 배경 클릭 시 닫힘 불가 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- TradingPage에 최초 진입하여 LeverageNotice 팝업이 표시된 상태이다

**테스트 단계**
1. LeverageNotice 팝업 바깥 영역(배경)을 탭한다
2. 팝업의 표시 상태를 확인한다

**예상 결과**
- 배경 탭 후에도 LeverageNotice 팝업이 닫히지 않고 계속 표시된다
- `I Understand` 버튼 외의 방법으로는 팝업을 닫을 수 없다

**비고**
- [미결] 배경 탭으로 팝업 닫힘 차단 여부 — 기획서에 명시되지 않은 동작, 정책 확정 필요

---

### ★ LEVR-IUND-001 — "I Understand" 버튼 탭 후 팝업 닫힘 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- TradingPage에 최초 진입하여 LeverageNotice 팝업이 표시된 상태이다

**테스트 단계**
1. LeverageNotice 팝업에서 `I Understand` 버튼을 탭한다
2. 팝업이 닫히는지 확인한다

**예상 결과**
- `I Understand` 버튼 탭 시 팝업이 닫힌다
- TradingPage 메인 화면이 표시된다

---

### LEVR-RPOP-001 — 재방문 시 LeverageNotice 팝업 미표시 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 이전 세션에서 LeverageNotice 팝업의 `I Understand`를 탭한 계정이다
- TradingPage를 나갔다가 다시 진입하는 상태이다

**테스트 단계**
1. TradingPage(`/trade`)에 재진입한다
2. 화면에 LeverageNotice 팝업이 표시되는지 확인한다

**예상 결과**
- LeverageNotice 팝업이 표시되지 않는다
- TradingPage 메인 화면이 바로 표시된다

**비고**
- [신규] 코드 근거: AppContext의 hasSeenLeverageNotice 상태 유지 여부 (화면 동작 기준으로 검증)

---

### ★ LEVR-NTXT-001 — LeverageNotice 팝업 문구 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정이다
- TradingPage에 최초 진입하여 LeverageNotice 팝업이 표시된 상태이다

**테스트 단계**
1. LeverageNotice 팝업의 본문 텍스트를 확인한다

**예상 결과**
- "This account has a maximum leverage limit of 2x under the user protection policy." 문구가 팝업에 표시된다

**비고**
- [미결] 팝업 문구 언어(한국어/영어) 미확정 — 정책 확정 후 정확한 텍스트 재검증 필요

---

### ★ LEVR-ORDR-001 — LeverageNotice 팝업 확인 후 거래 화면 정상 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정이다
- TradingPage에 최초 진입하는 상태이다 (LeverageNotice 미확인 상태)

**테스트 단계**
1. TradingPage에 진입한다
2. LeverageNotice 팝업이 화면에 표시되는지 확인한다
3. LeverageNotice 팝업에서 `I Understand` 버튼을 탭한다
4. 팝업이 닫히고 표시되는 화면을 확인한다

**예상 결과**
- TradingPage 진입 시 LeverageNotice 팝업이 표시된다
- `I Understand` 버튼 탭 후 팝업이 닫힌다
- 팝업 닫힘 후 TradingPage 거래 화면이 정상적으로 표시된다

---

### ★ LEVR-SLDR-001 — AdjustLeverage 모달 슬라이더 1~2 범위 제한 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- LeverageNotice 팝업을 이미 확인한 상태이다
- AdjustLeverage 모달이 열려 있는 상태이다

**테스트 단계**
1. AdjustLeverage 모달의 슬라이더를 확인한다
2. 슬라이더를 왼쪽 끝까지 드래그하여 최솟값을 확인한다
3. 슬라이더를 오른쪽 끝까지 드래그하여 최댓값을 확인한다

**예상 결과**
- 슬라이더의 최솟값이 1x이다
- 슬라이더의 최댓값이 2x이다
- 슬라이더 단계가 1x, 2x 두 가지만 선택 가능하다 (step=1)
- 3x 이상 선택이 불가하다

---

### ★ LEVR-SLDR-002 — AdjustLeverage 모달 3배 초과 입력 불가 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- AdjustLeverage 모달이 열려 있고 레버리지 수동 입력 필드가 표시된 상태이다

**테스트 단계**
1. AdjustLeverage 모달의 레버리지 입력 필드에 "3"을 입력한다
2. 입력 결과 및 적용 가능 여부를 확인한다

**예상 결과**
- 레버리지 값이 3으로 설정되지 않는다
- 입력이 차단되거나 자동으로 2로 리셋된다

---

### ★ LEVR-BNNER-001 — AdjustLeverage 모달 경고 배너 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- AdjustLeverage 모달이 열려 있는 상태이다

**테스트 단계**
1. AdjustLeverage 모달 상단의 경고 배너를 확인한다
2. 배너 문구와 색상을 확인한다

**예상 결과**
- AdjustLeverage 모달 상단에 경고 배너가 표시된다
- 배너에 "Max leverage limited to 2x (User Protection)" 문구가 표시된다
- 배너가 노란색 계열 색상으로 표시된다

---

## [TPSL] Auto TP/SL 도메인 — F-031~F-041

---

### ★ TPSL-DFLT-001 — 신규 계정 Auto TP/SL 기본 상태 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 신규 계정으로 온보딩을 방금 완료한 상태이다
- Settings 탭 → Trading Preferences 섹션에 접속해 있다

**테스트 단계**
1. Settings 탭을 탭한다
2. Trading Preferences 섹션을 확인한다
3. Auto TP/SL 토글의 초기 상태를 확인한다
4. TP/SL 수치 표시를 확인한다

**예상 결과**
- Auto TP/SL 토글이 OFF 상태로 표시된다
- TP 수치 표시란에 `--%`가 표시된다
- SL 수치 표시란에 `--%`가 표시된다

**비고**
- [미결] 초기 ON/OFF 여부 미확정 — 정책 확정 후 검증 필요 (F-041)
- [미결] TP 기본값(`DEFAULT_TP_PERCENT=1.8`) 최종 확정 여부 확인 필요 (F-031)
- [미결] SL 기본값(`DEFAULT_SL_PERCENT=5.0`) 최종 확정 여부 확인 필요 (F-032)

---

### ★ TPSL-STAT-001 — Auto TP/SL 전역 상태 관리 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Settings 탭 → Trading Preferences 섹션에서 Auto TP/SL을 ON으로 설정하고 저장한 상태이다

**테스트 단계**
1. Settings 탭에서 Auto TP/SL 토글 상태를 확인한다
2. BottomNav에서 Trade 탭을 탭하여 TradingPage로 이동한다
3. OrderForm에서 Auto TP/SL 관련 인디케이터가 표시되는지 확인한다
4. 다시 Settings 탭으로 이동하여 Auto TP/SL 토글 상태를 확인한다

**예상 결과**
- Trade 탭 이동 후 OrderForm에 TP%/SL% 값과 Edit 버튼이 표시된다
- Settings 탭으로 돌아와도 Auto TP/SL이 ON 상태로 유지된다

**비고**
- [신규] 코드 근거: AppContext의 autoTpSlEnabled 전역 상태 관리 (화면 동작 기준으로 검증)

---

### ★ TPSL-MODL-001 — AutoTpSlModal 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Settings 탭 → Trading Preferences 섹션에 접속해 있다

**테스트 단계**
1. Trading Preferences 섹션의 Auto TP/SL `Edit` 버튼을 탭한다
2. 모달이 표시되는지 확인한다
3. 모달 내 구성 요소를 확인한다

**예상 결과**
- AutoTpSlModal이 화면에 표시된다
- TP 입력 필드가 표시된다
- SL 입력 필드가 표시된다
- 확인(저장) 버튼이 표시된다

---

### ★ TPSL-MODL-002 — AutoTpSlModal 확인 버튼 활성화 조건 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 표시된 상태이다
- TP 입력 필드와 SL 입력 필드가 모두 0 또는 빈칸 상태이다

**테스트 단계**
1. TP 입력 필드에 `1.8`을 입력한다
2. 확인 버튼의 활성화 상태를 확인한다

**예상 결과**
- TP 값(`1.8`) 입력 후 확인 버튼이 활성화된다

---

### ★ TPSL-MODL-003 — AutoTpSlModal 확인 버튼 비활성화 조건 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 표시된 상태이다

**테스트 단계**
1. TP 입력 필드를 비워 두거나 0으로 설정한다
2. SL 입력 필드를 비워 두거나 0으로 설정한다
3. 확인 버튼의 활성화 상태를 확인한다

**예상 결과**
- TP와 SL 모두 0 또는 빈칸인 경우 확인 버튼이 비활성화(disabled) 상태이다
- 버튼을 탭해도 저장 동작이 발생하지 않는다

---

### ★ TPSL-ORDF-001 — Auto TP/SL ON 시 OrderForm 인디케이터 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Auto TP/SL이 ON 상태이고 TP: 1.8%, SL: 5.0%로 설정된 상태이다
- TradingPage(`/trade`)의 OrderForm이 표시된 상태이다

**테스트 단계**
1. OrderForm 하단의 Auto TP/SL 인디케이터 영역을 확인한다
2. 표시된 TP%, SL% 값과 Edit 버튼을 확인한다

**예상 결과**
- OrderForm에 `TP: +1.8%` 또는 해당 TP 비율이 표시된다
- OrderForm에 `SL: -5.0%` 또는 해당 SL 비율이 표시된다
- `Edit` 버튼이 함께 표시된다

**비고**
- [미결] TP 기본값(`DEFAULT_TP_PERCENT=1.8`) 최종 확정 여부 확인 필요 (F-031)
- [미결] SL 기본값(`DEFAULT_SL_PERCENT=5.0`) 최종 확정 여부 확인 필요 (F-032)

---

### ★ TPSL-ORDF-002 — Auto TP/SL OFF 시 OrderForm 인디케이터 미표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Auto TP/SL이 OFF 상태이다
- TradingPage(`/trade`)의 OrderForm이 표시된 상태이다

**테스트 단계**
1. OrderForm 하단의 Auto TP/SL 인디케이터 영역을 확인한다

**예상 결과**
- OrderForm에 TP%/SL% 인디케이터가 표시되지 않는다 (빈칸 또는 해당 영역 미표시)

---

### ★ TPSL-PSTN-001 — Auto 포지션에 녹색 Auto 배지 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Auto TP/SL이 ON 상태에서 주문을 체결하여 포지션이 생성된 상태이다
- Dashboard 탭의 Positions 목록에 해당 포지션이 표시된 상태이다

**테스트 단계**
1. Dashboard 탭을 탭한다
2. Positions 목록에서 Auto TP/SL이 적용된 포지션 카드를 확인한다
3. 포지션 카드의 배지를 확인한다

**예상 결과**
- Auto TP/SL이 적용된 포지션 카드에 녹색 "Auto" 배지가 표시된다

---

### ★ TPSL-PSTN-002 — PositionCard TP/SL 조건부 렌더링 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Auto TP/SL이 ON 상태에서 주문을 체결하여 TP와 SL이 설정된 포지션이 존재하는 상태이다
- Dashboard 탭의 Positions 목록에 해당 포지션이 표시된 상태이다

**테스트 단계**
1. Dashboard 탭 → Positions 목록에서 Auto TP/SL이 적용된 포지션 카드를 확인한다
2. 포지션 카드에 TP, SL 값이 표시되는지 확인한다

**예상 결과**
- TP 값이 설정된 포지션 카드에 TP 정보가 표시된다
- SL 값이 설정된 포지션 카드에 SL 정보가 표시된다

---

### TPSL-PSTN-003 — TP/SL 미설정 포지션 카드에서 TP/SL 미표시 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- Auto TP/SL이 OFF 상태에서 주문을 체결하여 TP/SL이 없는 포지션이 존재하는 상태이다
- Dashboard 탭의 Positions 목록에 해당 포지션이 표시된 상태이다

**테스트 단계**
1. Dashboard 탭 → Positions 목록에서 TP/SL이 설정되지 않은 포지션 카드를 확인한다
2. 포지션 카드에 TP, SL 영역이 표시되는지 확인한다

**예상 결과**
- TP/SL이 설정되지 않은 포지션 카드에 TP/SL 정보가 표시되지 않는다

**비고**
- [신규] 코드 근거: PositionCard의 position.tp / position.sl 값 존재 여부에 따른 조건부 렌더링 (화면 동작 기준으로 검증)

---

### ★ TPSL-TOGL-001 — SettingsPage Auto TP/SL 토글 ON 전환 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Settings 탭 → Trading Preferences 섹션에 접속해 있다
- Auto TP/SL 토글이 현재 OFF 상태이다

**테스트 단계**
1. Auto TP/SL 토글을 탭하여 ON으로 전환한다
2. 토글 색상 변화를 확인한다

**예상 결과**
- Auto TP/SL 토글이 ON 상태로 전환된다
- 토글 색상이 녹색으로 변경된다

---

### ★ TPSL-TOGL-002 — SettingsPage Auto TP/SL 토글 OFF 전환 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- Auto TP/SL 토글이 현재 ON 상태(녹색)이다
- Settings 탭 → Trading Preferences 섹션에 접속해 있다

**테스트 단계**
1. Auto TP/SL 토글을 탭하여 OFF로 전환한다
2. 토글 색상 변화를 확인한다

**예상 결과**
- Auto TP/SL 토글이 OFF 상태로 전환된다
- 토글 색상이 기본 배경 색상으로 변경된다

---

### ★ TPSL-PATH-001 — Settings → Trading Preferences → Auto TP/SL Edit 진입 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- TradingPage에 접속해 있다

**테스트 단계**
1. BottomNav에서 Settings 탭을 탭한다
2. Trading Preferences 섹션을 확인한다
3. Auto TP/SL 항목 옆의 `Edit` 버튼을 탭한다
4. AutoTpSlModal이 표시되는지 확인한다

**예상 결과**
- Settings 탭 → Trading Preferences 섹션이 표시된다
- Auto TP/SL `Edit` 버튼이 표시된다
- `Edit` 버튼 탭 시 AutoTpSlModal이 표시된다

---

### ★ TPSL-INIT-001 — 신규 계정 Auto TP/SL 초기 ON/OFF 상태 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 신규 계정으로 온보딩을 방금 완료한 상태이다

**테스트 단계**
1. Settings 탭 → Trading Preferences 섹션을 확인한다
2. Auto TP/SL 토글의 초기 상태를 확인한다

**예상 결과**
- Auto TP/SL 토글의 초기 상태가 명확하게 ON 또는 OFF 중 하나로 표시된다

**비고**
- [미결] 초기 ON/OFF 여부 미확정 — 정책 확정 후 예상 결과의 초기값 지정 필요 (F-041)

---

### TPSL-SAVE-001 — Auto TP/SL 설정값 저장 성공 Toast 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있는 상태이다
- TP에 `1.8`, SL에 `5.0`이 입력된 상태이다

**테스트 단계**
1. AutoTpSlModal에서 확인(저장) 버튼을 탭한다
2. Toast 메시지가 표시되는지 확인한다

**예상 결과**
- `Auto TP/SL settings saved.` Toast 메시지가 표시된다
- AutoTpSlModal이 닫힌다
- Settings → Trading Preferences에서 TP: 1.8%, SL: 5.0%로 표시된다

---

### TPSL-BDRY-001 — TP 입력 최솟값 0.1% 미만 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있는 상태이다

**테스트 단계**
1. TP 입력 필드에 `0`을 입력한다
2. 확인 버튼의 활성화 상태를 확인한다
3. 저장 시 동작을 확인한다

**예상 결과**
- TP 값 0 입력 시 입력이 차단되거나 저장이 불가하다
- 확인 버튼이 비활성화 상태이거나 오류 메시지가 표시된다

---

### TPSL-BDRY-002 — SL 입력 최댓값 99.9% 초과 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있는 상태이다

**테스트 단계**
1. SL 입력 필드에 `100`을 입력한다
2. 입력 결과 및 저장 가능 여부를 확인한다

**예상 결과**
- SL 값이 99.9%를 초과하여 저장되지 않는다
- 입력이 차단되거나 자동으로 99.9 이하로 리셋된다

---

### TPSL-BDRY-003 — TP/SL 음수 입력 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있는 상태이다

**테스트 단계**
1. TP 입력 필드에 `-1`을 입력한다
2. 입력 결과를 확인한다

**예상 결과**
- 음수 입력이 차단되어 필드에 `-1`이 입력되지 않는다

---

### TPSL-BDRY-004 — TP/SL 소수점 2자리 이상 입력 제한 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있는 상태이다

**테스트 단계**
1. TP 입력 필드에 `1.85`를 입력한다
2. 입력 결과를 확인한다

**예상 결과**
- 소수점 2자리 이상 입력이 차단되거나 소수점 1자리로 자동 반올림된다

---

### ★ TPSL-STNG-001 — Settings Trading Preferences Auto TP/SL 현재 설정값 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Auto TP/SL이 ON이고 TP: 1.8%, SL: 5.0%로 설정 저장된 상태이다
- Settings 탭 → Trading Preferences 섹션에 접속해 있다

**테스트 단계**
1. Trading Preferences 섹션의 Auto TP/SL 항목을 확인한다
2. 현재 설정된 TP와 SL 수치가 표시되는지 확인한다

**예상 결과**
- Auto TP/SL 항목에 현재 설정된 TP 비율(예: `1.8%`)이 표시된다
- Auto TP/SL 항목에 현재 설정된 SL 비율(예: `5.0%`)이 표시된다
- `Edit` 버튼이 함께 표시된다

---

### LEVR-COIN-001 — 코인 변경 시 레버리지 2배 자동 변경 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- Open Orders 및 Position이 없는 상태이다
- 현재 선택된 코인의 레버리지가 1x로 설정된 상태이다

**테스트 단계**
1. CoinSelector에서 다른 코인을 선택한다 (예: BTC → ETH)
2. OrderForm 상단의 레버리지 표시값을 확인한다

**예상 결과**
- 코인 변경 후 레버리지가 2x로 자동 변경된다
- OrderForm 상단에 2x 레버리지가 표시된다

---

### LEVR-COIN-002 — 포지션 보유 중 코인 변경 시 기존 레버리지 유지 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- 1x 레버리지로 포지션 또는 Open Orders를 보유한 상태이다

**테스트 단계**
1. CoinSelector에서 다른 코인을 선택한다
2. OrderForm 상단의 레버리지 표시값을 확인한다

**예상 결과**
- 포지션/Open Orders 보유 중에는 코인 변경 시 레버리지가 강제로 2x로 변경되지 않는다
- 기존 설정된 레버리지 값이 유지된다

---

### LEVR-MRGIN-001 — 기존 포지션 레버리지 낮추기 성공 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- 2x 레버리지 포지션이 존재하고 Margin이 충분한 상태이다
- AdjustLeverage 모달이 열려 있는 상태이다

**테스트 단계**
1. AdjustLeverage 모달에서 슬라이더를 1x로 변경한다
2. 확인 버튼을 탭한다
3. 변경 결과를 확인한다

**예상 결과**
- 레버리지가 1x로 성공적으로 변경된다
- OrderForm 상단에 1x 레버리지가 표시된다

---

### TPSL-ORDF-003 — Auto TP/SL ON 상태에서 주문 시 OrderForm TP/SL 자동 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- Auto TP/SL이 ON 상태이고 TP: 1.8%, SL: 5.0%로 설정된 상태이다
- TradingPage OrderForm이 표시된 상태이다

**테스트 단계**
1. OrderForm에서 코인을 선택하고 주문 유형을 Market으로 설정한다
2. OrderForm 하단의 TP/SL 표시 영역을 확인한다

**예상 결과**
- OrderForm 하단 TP/SL 항목에 Settings에서 설정한 값이 자동으로 표시된다
- 표시 형식이 `TP: +1.8% / SL: -5.0%` 또는 유사한 형태로 표시된다

---

### TPSL-PRTY-001 — Auto TP/SL ON 상태에서 수동 TP/SL 입력 시 수동값 우선 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- Auto TP/SL이 ON 상태이고 TP: 1.8%, SL: 5.0%로 설정된 상태이다
- TradingPage OrderForm에서 주문 설정 중인 상태이다

**테스트 단계**
1. OrderForm의 TP/SL Edit 버튼을 탭하여 AutoTpSlModal을 연다
2. TP 값을 `3.0`으로 수정하고 확인한다
3. 주문을 체결한다
4. Dashboard Positions 탭에서 생성된 포지션의 TP 값을 확인한다

**예상 결과**
- 체결된 포지션의 TP 값이 Auto 기본값(1.8%)이 아닌 수동 입력값(3.0%)으로 적용된다

---

### TPSL-ERRL-001 — Auto TP/SL 설정 저장 실패 시 오류 Toast 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | 공통 |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있고 유효한 TP/SL 값이 입력된 상태이다
- 네트워크 오류 또는 서버 오류 상황이 시뮬레이션된 상태이다

**테스트 단계**
1. 확인(저장) 버튼을 탭한다
2. Toast 메시지가 표시되는지 확인한다

**예상 결과**
- 오류 Toast 메시지가 표시된다
- 기존에 저장된 TP/SL 값이 Settings 화면에서 유지된다

**비고**
- [미결] 저장 실패 시 정확한 Toast 오류 문구 미확정 — 정책 확정 필요

---

### LEVR-INPT-001 — AdjustLeverage 소수점 입력 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- AdjustLeverage 모달이 열려 있고 레버리지 수동 입력 필드가 표시된 상태이다

**테스트 단계**
1. 레버리지 입력 필드에 `1.5`를 입력한다
2. 입력 결과를 확인한다

**예상 결과**
- 소수점 입력이 차단되어 `1.5`가 입력되지 않는다
- 정수(1 또는 2)만 입력 가능하다

---

### LEVR-INPT-002 — AdjustLeverage 0 입력 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- AdjustLeverage 모달이 열려 있고 레버리지 수동 입력 필드가 표시된 상태이다

**테스트 단계**
1. 레버리지 입력 필드에 `0`을 입력한다
2. 입력 결과 및 저장 가능 여부를 확인한다

**예상 결과**
- 0 입력이 차단되거나 저장이 불가하다

---


## ====== TRAD / SGNL 도메인 (F-042~F-063) ======

### ★ TRAD-COIN-001 — 지원 코인 8종 목록 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에 접속해 있다

**테스트 단계**
1. TradingPage의 코인 선택 영역(CoinSelector)을 탭한다
2. 표시되는 코인 목록을 확인한다

**예상 결과**
- BTC-USDC, ETH-USDC, SOL-USDC, DOGE-USDC, ARB-USDC, AVAX-USDC, MATIC-USDC, LINK-USDC 8개 코인이 목록에 표시된다
- 8개 이외의 코인은 표시되지 않는다

---

### TRAD-COIN-002 — 지원 코인 목록 외 종목 선택 불가 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에 접속해 있다

**테스트 단계**
1. CoinSelector 목록을 탭한다
2. 목록에 표시된 8종 외에 다른 코인이 없는지 확인한다

**예상 결과**
- 목록에 BTC, ETH, SOL, DOGE, ARB, AVAX, MATIC, LINK 외 다른 코인이 표시되지 않는다
- 목록 밖 코인을 입력하거나 선택할 수 있는 UI가 없다

---

### ★ TRAD-OTYP-001 — 주문 타입 3종(limit/market/conditional) 선택 UI 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에 접속해 있다

**테스트 단계**
1. TradingPage의 주문 타입 선택 영역을 확인한다
2. `limit`, `market`, `conditional` 탭(또는 버튼) 3종이 표시되는지 확인한다
3. 각 탭을 순서대로 탭하여 선택 전환이 되는지 확인한다

**예상 결과**
- limit, market, conditional 3종 주문 타입 선택 UI가 표시된다
- 각 탭을 탭하면 해당 주문 타입으로 전환된다

---

### ★ TRAD-PRIC-001 — limit 주문 선택 시 가격 입력 필드 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에 접속해 있다

**테스트 단계**
1. 주문 타입을 `limit`으로 선택한다
2. 가격 입력 필드가 표시되는지 확인한다

**예상 결과**
- 주문 가격 입력 필드가 화면에 표시된다

---

### TRAD-PRIC-002 — conditional 주문 선택 시 가격 입력 필드 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에 접속해 있다

**테스트 단계**
1. 주문 타입을 `conditional`로 선택한다
2. 가격 입력 필드가 표시되는지 확인한다

**예상 결과**
- 주문 가격 입력 필드가 화면에 표시된다

---

### ★ TRAD-PRIC-003 — market 주문 선택 시 가격 입력 필드 숨김 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에 접속해 있다

**테스트 단계**
1. 주문 타입을 `market`으로 선택한다
2. 가격 입력 필드가 화면에서 사라지는지 확인한다

**예상 결과**
- 가격 입력 필드가 화면에 표시되지 않는다
- 다른 주문 입력 요소(수량 슬라이더 등)는 정상 표시된다

---

### ★ TRAD-SLDR-001 — OrderForm 수량 슬라이더 0~100% 범위 동작 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에 접속해 있다
- 충분한 mock USDC 잔고가 있다

**테스트 단계**
1. OrderForm의 수량 슬라이더를 0%로 이동한다
2. 슬라이더를 25%로 이동한다
3. 슬라이더를 50%로 이동한다
4. 슬라이더를 100%로 이동한다

**예상 결과**
- 슬라이더가 0%, 25%, 50%, 100% 위치로 이동한다
- 슬라이더 위치에 따라 주문 수량(또는 금액)이 변경되어 표시된다
- 100% 설정 시 가용 잔고 전액에 해당하는 수량이 표시된다

---

### ★ TRAD-ORDR-001 — Market Long 주문 실행 성공 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에 접속해 있다
- 충분한 mock USDC 잔고가 있다

**테스트 단계**
1. CoinSelector에서 `BTC-USDC`를 선택한다
2. 주문 타입을 `market`으로 선택한다
3. 수량 슬라이더를 25%로 설정한다
4. `Buy / Long` 버튼을 탭한다

**예상 결과**
- 주문 확인 모달(OrderConfirm)이 표시된다
- 모달 내 주문 내용(코인명, 방향, 수량)이 표시된다
- 확인 버튼 탭 후 주문 처리 중 Toast 알림이 표시된다
- 주문 체결 후 Dashboard 탭 Positions 목록에 해당 포지션이 추가된다

---

### ★ TRAD-ORDR-002 — Market Short 주문 실행 성공 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에 접속해 있다
- 충분한 mock USDC 잔고가 있다

**테스트 단계**
1. CoinSelector에서 임의의 코인을 선택한다
2. 주문 타입을 `market`으로 선택한다
3. 수량 슬라이더를 25%로 설정한다
4. `Sell / Short` 버튼을 탭한다

**예상 결과**
- 주문 확인 모달(OrderConfirm)이 표시된다
- 확인 버튼 탭 후 Toast 알림이 표시된다
- Dashboard 탭 Positions 목록에 Short 포지션이 추가된다

---

### TRAD-ORDR-003 — 잔고 0% 상태에서 주문 실행 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에 접속해 있다

**테스트 단계**
1. 수량 슬라이더를 0%로 설정한다
2. `Buy / Long` 버튼의 상태를 확인한다
3. 버튼을 탭한다

**예상 결과**
- 수량이 0인 상태에서 주문 버튼이 비활성화되거나, 탭해도 주문이 실행되지 않는다
- 오류 메시지 또는 안내가 표시된다

**비고**
- [미결] 버튼 비활성화 처리 여부 또는 오류 메시지 텍스트 미확정 — 정책 확정 필요

---

### ★ TRAD-CONF-001 — 주문 제출 전 OrderConfirm 모달 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에서 주문 타입, 코인, 수량이 설정된 상태이다

**테스트 단계**
1. `Buy / Long` 또는 `Sell / Short` 버튼을 탭한다
2. 화면에 표시되는 모달을 확인한다

**예상 결과**
- OrderConfirm 모달이 표시된다
- 모달에 코인명, 주문 방향(Long/Short), 주문 타입, 수량 등 주문 내용이 표시된다
- 확인 버튼과 취소 버튼이 표시된다

---

### TRAD-CONF-002 — OrderConfirm 모달 취소 시 주문 미실행 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- OrderConfirm 모달이 표시된 상태이다

**테스트 단계**
1. OrderConfirm 모달에서 취소 버튼을 탭한다

**예상 결과**
- 모달이 닫힌다
- 주문이 실행되지 않는다
- Dashboard Positions 목록에 새 포지션이 추가되지 않는다

---

### ★ TRAD-PRFL-001 — prefillData 기반 OrderForm 자동 채움 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 상태이다
- Signal 탭에서 시그널의 `Modify` 버튼을 탭하여 OrderForm으로 이동한 상태이다

**테스트 단계**
1. `/trade` 페이지의 OrderForm 화면을 확인한다
2. 코인, 방향, 가격, 수량 등 입력 필드에 시그널 값이 자동 입력되어 있는지 확인한다
3. 자동 입력된 값을 직접 수정한다

**예상 결과**
- OrderForm의 입력 필드에 시그널에서 전달된 값이 자동으로 채워져 있다
- 사용자가 자동 채워진 값을 직접 수정할 수 있다

**비고**
- [신규] 코드 근거: PREFILL_FROM_SIGNAL 디스패치 후 OrderForm 초기값 설정 동작 (화면 동작 기준으로 작성)

---

### ★ TRAD-DASH-001 — Dashboard Positions 탭 포지션 목록 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- 온보딩이 완료된 상태이다
- 최소 1개 이상의 포지션이 체결된 상태이다

**테스트 단계**
1. TradingPage 하단 또는 Dashboard 탭으로 이동한다
2. `Positions` 탭을 탭한다
3. 포지션 목록을 확인한다

**예상 결과**
- 보유 포지션 목록이 표시된다
- 각 포지션 카드에 코인명, 방향(Long/Short), 진입가, 수량, 미실현 PnL 정보가 표시된다

---

### ★ TRAD-OPEN-001 — Dashboard Open Orders 탭 빈 상태 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지의 Dashboard 탭에 접속해 있다

**테스트 단계**
1. Dashboard 탭에서 `Open Orders` 탭을 탭한다
2. 화면에 표시되는 내용을 확인한다

**예상 결과**
- "No open orders" 문구가 표시된다

**비고**
- [미결] Open Orders 탭 실제 구현 여부 불명확 — 구현 확정 전 검증 필요

---

### ★ TRAD-HIST-001 — Dashboard History 탭 빈 상태 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지의 Dashboard 탭에 접속해 있다

**테스트 단계**
1. Dashboard 탭에서 `History` 탭을 탭한다
2. 화면에 표시되는 내용을 확인한다

**예상 결과**
- "No order history" 문구가 표시된다

**비고**
- [미결] History 탭 실제 구현 여부 불명확 — 구현 확정 전 검증 필요

---

### ★ TRAD-PNL-001 — PositionCard PnL 수익 녹색 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- 온보딩이 완료된 상태이다
- PnL이 0 이상인 포지션이 존재한다

**테스트 단계**
1. Dashboard 탭의 Positions 목록을 확인한다
2. PnL이 양수(수익)인 포지션 카드를 확인한다

**예상 결과**
- PnL 수치가 녹색으로 표시된다
- 포지션 카드 좌측 보더도 녹색으로 표시된다

---

### TRAD-PNL-002 — PositionCard PnL 손실 빨간색 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- 온보딩이 완료된 상태이다
- PnL이 음수(손실)인 포지션이 존재한다

**테스트 단계**
1. Dashboard 탭의 Positions 목록을 확인한다
2. PnL이 음수(손실)인 포지션 카드를 확인한다

**예상 결과**
- PnL 수치가 빨간색으로 표시된다
- 포지션 카드 좌측 보더도 빨간색으로 표시된다

---

### ★ TRAD-CLSE-001 — 포지션 청산 전 CloseConfirm 모달 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- 온보딩이 완료된 상태이다
- 보유 포지션이 1개 이상 존재한다

**테스트 단계**
1. Dashboard 탭의 Positions 목록에서 포지션 카드를 확인한다
2. 포지션 청산(Close) 버튼을 탭한다

**예상 결과**
- CloseConfirm 모달이 표시된다
- 모달에 청산 대상 포지션 정보와 확인/취소 버튼이 표시된다

---

### TRAD-CLSE-002 — CloseConfirm 모달 취소 시 포지션 유지 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- CloseConfirm 모달이 표시된 상태이다

**테스트 단계**
1. CloseConfirm 모달에서 취소 버튼을 탭한다

**예상 결과**
- 모달이 닫힌다
- 포지션이 청산되지 않고 Positions 목록에 그대로 유지된다

---

### TRAD-PORT-001 — portfolio 탭 미구현 안내 메시지 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (portfolio 탭) |

**사전 조건**
- 온보딩이 완료된 상태이다
- `/trade` 페이지에 접속해 있다

**테스트 단계**
1. 하단 네비게이션 또는 탭에서 `portfolio` 탭을 탭한다
2. 화면에 표시되는 내용을 확인한다

**예상 결과**
- "coming in the next version" 문구가 포함된 안내 메시지가 표시된다

---

## [SGNL] 시그널 (F-056~F-063)

---

### ★ SGNL-HEAD-001 — 시그널 탭 "⚡ YouthMeta Signals" 헤더 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- 온보딩이 완료된 상태이다
- 하단 네비게이션에서 Signal 탭으로 이동한 상태이다

**테스트 단계**
1. Signal 탭 화면 상단의 헤더 텍스트를 확인한다

**예상 결과**
- "⚡ YouthMeta Signals" 헤더가 표시된다

**비고**
- [미결] 시그널 탭 행사 체험 범위 포함 여부 미확정 — 기능 포함 확정 후 검증 필요

---

### ★ SGNL-SUMM-001 — 성과 요약 카드(최근 30일) 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- 온보딩이 완료된 상태이다
- Signal 탭에 접속해 있다

**테스트 단계**
1. Signal 탭 화면에서 성과 요약 카드를 확인한다
2. 카드 내에 표시된 항목을 확인한다

**예상 결과**
- 성과 요약 카드가 표시된다
- Hit 건수, Miss 건수, Expired 건수가 표시된다
- 평균 PnL%와 성공률%가 표시된다

**비고**
- [미결] 시그널 탭 행사 체험 범위 포함 여부 미확정 — F-056 확정 연동

---

### SGNL-CLRS-001 — 성공률 색상 분기 처리 확인 (≥70% 녹색)

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- Signal 탭에 접속해 있다
- 성과 요약 카드에 성공률이 표시된 상태이다

**테스트 단계**
1. 성과 요약 카드의 성공률 수치를 확인한다
2. 성공률이 70% 이상인 경우 색상을 확인한다
3. 성공률이 50% 이상 70% 미만인 경우 색상을 확인한다
4. 성공률이 50% 미만인 경우 색상을 확인한다

**예상 결과**
- 성공률 ≥ 70%: 녹색으로 표시된다
- 성공률 ≥ 50% (70% 미만): 주황색으로 표시된다
- 성공률 < 50%: 빨간색으로 표시된다

**비고**
- [미결] 시그널 탭 행사 체험 범위 포함 여부 미확정 — F-056 확정 연동

---

### ★ SGNL-FILT-001 — 시그널 필터 탭(ALL/LONG/SHORT/ACTIVE/CLOSED) 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- Signal 탭에 접속해 있다

**테스트 단계**
1. Signal 탭의 필터 탭 영역을 확인한다
2. ALL, LONG, SHORT, ACTIVE, CLOSED 탭이 모두 표시되는지 확인한다
3. 탭 영역이 좌우 스크롤 가능한지 확인한다

**예상 결과**
- ALL, LONG, SHORT, ACTIVE, CLOSED 5개 필터 탭이 표시된다
- 탭 영역이 가로 스크롤된다

**비고**
- [미결] 시그널 탭 행사 체험 범위 포함 여부 미확정 — F-056 확정 연동

---

### SGNL-FILT-002 — LONG 필터 탭 선택 시 LONG 시그널만 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- Signal 탭에 접속해 있다
- LONG 및 SHORT 시그널이 각각 1개 이상 존재한다

**테스트 단계**
1. 필터 탭에서 `LONG` 탭을 탭한다
2. 시그널 목록을 확인한다

**예상 결과**
- LONG 방향의 시그널만 목록에 표시된다
- SHORT 방향의 시그널은 목록에 표시되지 않는다

**비고**
- [미결] 시그널 탭 행사 체험 범위 포함 여부 미확정 — F-056 확정 연동

---

### SGNL-CLSD-001 — CLOSED 필터 탭에서 HIT_TP/HIT_SL/EXPIRED/CANCELLED 상태 시그널 표시 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- Signal 탭에 접속해 있다
- HIT_TP, HIT_SL, EXPIRED, CANCELLED 상태 중 1개 이상의 시그널이 존재한다

**테스트 단계**
1. 필터 탭에서 `CLOSED` 탭을 탭한다
2. 표시되는 시그널 목록의 상태를 확인한다

**예상 결과**
- HIT_TP, HIT_SL, EXPIRED, CANCELLED 상태의 시그널이 CLOSED 탭 목록에 표시된다
- ACTIVE 상태의 시그널은 CLOSED 탭 목록에 표시되지 않는다

**비고**
- [신규] 코드 근거: HIT_TP, HIT_SL, EXPIRED, CANCELLED 상태를 CLOSED로 분류하는 로직 (화면 동작 기준으로 작성)
- [미결] 시그널 탭 행사 체험 범위 포함 여부 미확정 — F-056 확정 연동

---

### ★ SGNL-SHTS-001 — SignalOrderSheet 바텀시트 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- Signal 탭에 접속해 있다
- 시그널 목록에 시그널 카드가 1개 이상 표시된 상태이다

**테스트 단계**
1. 시그널 카드를 탭한다
2. 화면 하단에 표시되는 바텀시트를 확인한다

**예상 결과**
- SignalOrderSheet 바텀시트가 화면 하단에 표시된다
- 바텀시트에 코인명, 방향(Long/Short), 진입가, 타겟가(TP), 손절가(SL), 레버리지 정보가 표시된다

**비고**
- [미결] 시그널 탭 행사 체험 범위 포함 여부 미확정 — F-056 확정 연동

---

### ★ SGNL-EXEC-001 — Execute 버튼으로 시그널 즉시 주문 실행 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- Signal 탭에 접속해 있다
- SignalOrderSheet 바텀시트가 표시된 상태이다
- 충분한 mock USDC 잔고가 있다

**테스트 단계**
1. SignalOrderSheet 바텀시트에서 `Execute` 버튼을 탭한다
2. 화면에 표시되는 결과를 확인한다

**예상 결과**
- 주문 실행 Toast 알림이 표시된다
- Dashboard 탭 Positions 목록에 시그널 기반 포지션이 추가된다

**비고**
- [미결] 시그널 탭 행사 체험 범위 포함 여부 미확정 — F-056 확정 연동

---

### ★ SGNL-MODF-001 — Modify 버튼으로 시그널 값 OrderForm 로드 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭 → Trade 탭) |

**사전 조건**
- Signal 탭에 접속해 있다
- SignalOrderSheet 바텀시트가 표시된 상태이다

**테스트 단계**
1. SignalOrderSheet 바텀시트에서 `Modify` 버튼을 탭한다
2. 화면이 Trade 탭의 OrderForm으로 전환되는지 확인한다
3. OrderForm의 입력 필드 값을 확인한다

**예상 결과**
- Trade 탭의 OrderForm 화면으로 전환된다
- OrderForm의 코인, 방향, 가격 등 입력 필드에 시그널 값이 자동으로 채워져 있다
- 사용자가 자동 입력된 값을 수정할 수 있다

**비고**
- [미결] 시그널 탭 행사 체험 범위 포함 여부 미확정 — F-056 확정 연동
- [신규] 코드 근거: PREFILL_FROM_SIGNAL 디스패치 후 OrderForm 자동 입력 동작 (화면 동작 기준으로 작성)

---

### SGNL-EXEC-002 — 잔고 부족 상태에서 Execute 시그널 주문 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- Signal 탭에 접속해 있다
- SignalOrderSheet 바텀시트가 표시된 상태이다
- 잔고가 시그널 주문 최소 수량보다 부족한 상태이다

**테스트 단계**
1. SignalOrderSheet 바텀시트에서 `Execute` 버튼을 탭한다
2. 화면에 표시되는 결과를 확인한다

**예상 결과**
- 주문이 실행되지 않는다
- 잔고 부족 관련 오류 메시지 또는 알림이 표시된다

**비고**
- [미결] 오류 메시지 텍스트 미확정 — 정책 확정 필요
- [미결] 시그널 탭 행사 체험 범위 포함 여부 미확정 — F-056 확정 연동

## ====== MOBL / SETG / ROUT 도메인 (F-064~F-086) ======

### MOBL-TNBN-001 — LandingPage "TESTNET MODE" 배너 상시 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 모바일 브라우저에서 `/` (LandingPage)에 접속한 상태이다

**테스트 단계**
1. LandingPage 화면 전체를 확인한다
2. 화면 하단에 "TESTNET MODE" 배너가 표시되는지 확인한다

**예상 결과**
- "TESTNET MODE" 배너가 화면 하단에 표시된다
- 다른 UI 요소와 겹치지 않고 상시 노출된다

---

### MOBL-TNBN-002 — 다른 탭 이동 후에도 "TESTNET MODE" 배너 유지 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage), /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. `/trade` 화면에서 "TESTNET MODE" 배너 노출 여부를 확인한다
2. BottomNav에서 Signal 탭으로 이동한다
3. Signal 화면에서 배너 노출 여부를 확인한다
4. Settings 탭으로 이동한다
5. Settings 화면에서 배너 노출 여부를 확인한다

**예상 결과**
- 탭 이동과 관계없이 "TESTNET MODE" 배너가 모든 화면에서 상시 노출된다

---

### MOBL-EXCH-001 — SettingsPage Exchange Connection 섹션 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- BottomNav에서 Settings 탭을 탭하여 SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage를 스크롤하여 Exchange Connection 섹션을 찾는다
2. Hyperliquid 테스트넷 연결 상태가 표시되는지 확인한다

**예상 결과**
- Exchange Connection 섹션이 표시된다
- Hyperliquid 테스트넷 연결 상태가 표시된다

---

### MOBL-TNBG-001 — TESTNET 배지 및 "실제 자금이 아님" 고지 문구 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. `/trade` 화면에서 TESTNET 배지를 찾는다
2. "실제 자금이 아님" 또는 이에 상응하는 고지 문구가 표시되는지 확인한다

**예상 결과**
- TESTNET 배지가 화면에 표시된다
- "실제 자금이 아님" 고지 문구가 표시된다

---

### MOBL-HLAP-001 — HL Testnet API 엔드포인트 연동 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | 공통 |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에서 주문 또는 잔고 조회 동작을 수행할 수 있는 상태이다

**테스트 단계**
1. `/trade` 화면에서 잔고 정보가 표시되는지 확인한다
2. BTC/USDC 코인을 선택하고 시세 정보가 표시되는지 확인한다

**예상 결과**
- 잔고 및 시세 정보가 정상적으로 표시된다 (Testnet 데이터 기준)
- 메인넷 데이터와 혼용되지 않는다

**비고**
- [신규] 코드 근거: HL Testnet API `api.hyperliquid-testnet.xyz`, Chain ID 998 연동 여부 (화면 동작 기준 검증)
- [개발 확인] 실제 API 호출 엔드포인트 및 Chain ID 998 연동 여부 확인 필요

---

## [MOBL] 모바일 반응형 UI (F-069~F-079)

---

### ★ MOBL-LAYT-001 — 전체 앱 최대 너비 320px 모바일 레이아웃 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (전체 화면) |

**사전 조건**
- 모바일 브라우저(iOS Safari 또는 Android Chrome)에서 앱에 접속한 상태이다
- 뷰포트 375px 기준 환경이다

**테스트 단계**
1. LandingPage(`/`)에서 화면 레이아웃을 확인한다
2. `/login` 페이지에서 레이아웃을 확인한다
3. `/trade` 페이지에서 레이아웃을 확인한다

**예상 결과**
- 전체 앱이 최대 너비 320px 이내로 표시되며 가로 스크롤이 발생하지 않는다
- 화면 높이가 100dvh로 표시되어 브라우저 주소창 상하 여백 없이 전체를 채운다

---

### ★ MOBL-ORDF-001 — Order Form 모바일 터치 인터랙션 정상 동작 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면의 Order Form이 표시된 상태이다

**테스트 단계**
1. 주문 타입 선택 버튼(Market/Limit/Conditional)을 손가락으로 탭한다
2. 수량 슬라이더를 손가락으로 드래그하여 조정한다
3. Long/Short 버튼을 손가락으로 탭한다

**예상 결과**
- 주문 타입 버튼 탭 시 선택 상태가 즉각 변경된다
- 슬라이더 드래그 시 수량이 실시간으로 조정된다
- Long/Short 버튼 탭 시 OrderConfirm 모달이 표시된다

---

### MOBL-ORDF-002 — Order Form 모바일 터치 슬라이더 경계값 입력 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면의 Order Form이 표시된 상태이다

**테스트 단계**
1. 수량 슬라이더를 0% 위치(최소)로 드래그한다
2. Long 버튼을 탭하여 주문 시도를 확인한다

**예상 결과**
- 수량 0% 상태에서 주문 버튼이 비활성화되거나 오류 메시지가 표시된다
- 0% 상태에서 주문이 실행되지 않는다

---

### ★ MOBL-DASH-001 — Dashboard 모바일 터치 인터랙션 정상 동작 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- 하나 이상의 포지션이 보유된 상태이다
- Dashboard 탭이 표시된 상태이다

**테스트 단계**
1. Positions 탭을 탭한다
2. 포지션 목록이 표시되는지 확인한다
3. 포지션 카드를 위아래로 스크롤한다

**예상 결과**
- Positions 탭 탭 시 포지션 목록이 표시된다
- 포지션 목록 스크롤이 부드럽게 동작한다

---

### ★ MOBL-CHRT-001 — Chart 컴포넌트 모바일 레이아웃 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. `/trade` 화면에서 Chart 컴포넌트가 표시되는지 확인한다
2. Chart 컴포넌트가 320px 너비 내에 잘린 부분 없이 표시되는지 확인한다

**예상 결과**
- Chart 컴포넌트가 모바일 화면 너비에 맞게 표시된다
- 가로 스크롤이 발생하지 않는다

---

### ★ MOBL-COIN-001 — Coin Info Bar 모바일 레이아웃 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. `/trade` 화면 상단의 Coin Info Bar를 확인한다
2. 코인명, 현재가 등의 정보가 화면 너비 내에 표시되는지 확인한다

**예상 결과**
- Coin Info Bar가 모바일 화면 너비에 맞게 표시된다
- 코인 정보가 잘리거나 겹치지 않고 표시된다

---

### ★ MOBL-BNAV-001 — BottomNav 4탭 고정 하단 네비게이션 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. 화면 하단에 BottomNav가 표시되는지 확인한다
2. trade, signal, portfolio, settings 4개 탭이 표시되는지 확인한다
3. 각 탭을 순서대로 탭하여 이동이 되는지 확인한다

**예상 결과**
- BottomNav가 화면 하단에 고정되어 표시된다
- trade, signal, portfolio, settings 4개 탭이 표시된다
- 각 탭 탭 시 해당 화면으로 이동된다

---

### MOBL-BNAV-002 — 탭 이동 시 BottomNav 고정 상태 유지 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. 탭 콘텐츠 영역을 위아래로 스크롤한다
2. 스크롤 중 BottomNav 위치를 확인한다

**예상 결과**
- 콘텐츠 스크롤 시 BottomNav가 화면 하단에 고정된 채로 유지된다
- BottomNav가 스크롤에 따라 움직이지 않는다

---

### ★ MOBL-SCRL-001 — 탭 콘텐츠 스크롤 및 하단 64px 여백 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. 탭 콘텐츠 영역을 최하단까지 스크롤한다
2. 콘텐츠 최하단이 BottomNav에 가려지지 않는지 확인한다

**예상 결과**
- 탭 콘텐츠 영역이 스크롤 가능하다
- 콘텐츠 최하단이 BottomNav와 겹치지 않고 64px 이상의 여백이 확보된다

---

### MOBL-DKTH-001 — 다크 테마 배경색 #0a0a0a 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (전체 화면) |

**사전 조건**
- 모바일 브라우저에서 앱에 접속한 상태이다

**테스트 단계**
1. LandingPage(`/`)에서 화면 배경색을 확인한다
2. `/trade` 화면에서 배경색을 확인한다

**예상 결과**
- 전체 앱의 배경색이 짙은 다크(#0a0a0a에 상응하는 어두운 배경) 테마로 표시된다
- 흰 배경이나 밝은 배경이 표시되지 않는다

---

### MOBL-CSSV-001 — CSS 변수 색상 시스템 정상 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- 수익 포지션과 손실 포지션이 각 1개 이상 존재하는 상태이다

**테스트 단계**
1. Dashboard 탭에서 포지션 목록을 확인한다
2. 수익(PnL ≥ 0) 포지션의 색상을 확인한다
3. 손실(PnL < 0) 포지션의 색상을 확인한다

**예상 결과**
- 수익 포지션의 PnL이 녹색(`--accent-green`)으로 표시된다
- 손실 포지션의 PnL이 빨간색(`--accent-red`)으로 표시된다

---

### MOBL-LDFN-001 — LandingPage 페이드인 애니메이션 순차 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 모바일 브라우저에서 `/` (LandingPage)에 처음 접속하는 상태이다

**테스트 단계**
1. LandingPage에 접속한다
2. 화면 요소들이 순차적으로 나타나는지 확인한다

**예상 결과**
- LandingPage의 UI 요소들이 순차적으로 페이드인되어 표시된다
- 모든 요소가 한번에 표시되지 않고 시차를 두고 나타난다

---

### MOBL-LGFN-001 — LoginPage 페이드인 애니메이션 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login |

**사전 조건**
- 모바일 브라우저에서 `/login` 페이지에 접속한 상태이다

**테스트 단계**
1. LoginPage에 접속한다
2. 화면 요소가 페이드인되어 나타나는지 확인한다

**예상 결과**
- LoginPage의 UI 요소가 페이드인 애니메이션으로 표시된다

---

## [SETG] 설정 (F-080~F-086)

---

### SETG-ACCT-001 — Account 섹션 이메일 및 지갑 주소 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- BottomNav에서 Settings 탭을 탭하여 SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage에서 Account 섹션을 확인한다
2. 이메일 주소가 표시되는지 확인한다
3. 지갑 주소가 표시되는지 확인한다

**예상 결과**
- Account 섹션에 가입 시 사용한 이메일 주소가 표시된다
- 온보딩에서 생성된 지갑 주소가 표시된다

---

### SETG-WCPY-001 — 지갑 주소 복사 버튼 동작 및 Toast 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage의 Account 섹션에서 지갑 주소가 표시된 상태이다

**테스트 단계**
1. 지갑 주소 옆의 복사 버튼을 탭한다
2. 화면에 Toast 메시지가 표시되는지 확인한다

**예상 결과**
- 복사 버튼 탭 시 "Address copied!" Toast 메시지가 화면에 표시된다
- Toast 메시지가 일정 시간 후 사라진다

---

### ★ SETG-TPSL-001 — Trading Preferences Auto TP/SL 설정값 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage에서 Trading Preferences 섹션을 확인한다
2. Auto TP/SL 설정값(TP%, SL%)이 표시되는지 확인한다
3. Edit 버튼이 표시되는지 확인한다

**예상 결과**
- Trading Preferences 섹션에 현재 TP% 및 SL% 값이 표시된다
- Edit 버튼이 표시된다

---

### SETG-TPSL-002 — Edit 버튼 탭 시 AutoTpSlModal 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage의 Trading Preferences 섹션에서 Edit 버튼이 표시된 상태이다

**테스트 단계**
1. Trading Preferences 섹션의 Auto TP/SL Edit 버튼을 탭한다
2. AutoTpSlModal이 표시되는지 확인한다

**예상 결과**
- Edit 버튼 탭 시 AutoTpSlModal이 표시된다
- 모달에 TP% 및 SL% 입력 필드가 표시된다

---

### ★ SETG-TGTG-001 — Auto TP/SL 토글 스위치 ON/OFF 상태 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage의 Trading Preferences 섹션이 표시된 상태이다

**테스트 단계**
1. Auto TP/SL 토글 스위치의 현재 상태를 확인한다
2. 토글 스위치를 탭한다
3. 토글 상태가 변경되는지 확인한다
4. 다시 토글 스위치를 탭한다
5. 토글 상태가 원래대로 되돌아오는지 확인한다

**예상 결과**
- 토글 ON 상태일 때 녹색으로 표시된다
- 토글 OFF 상태일 때 기본 배경색으로 표시된다
- 탭할 때마다 ON/OFF 상태가 즉각 전환된다

---

### SETG-TGTG-002 — Auto TP/SL 토글 OFF 시 OrderForm 인디케이터 미표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭), /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage에서 Auto TP/SL 토글이 OFF 상태이다

**테스트 단계**
1. SettingsPage에서 Auto TP/SL 토글을 OFF로 설정한다
2. BottomNav에서 trade 탭을 탭하여 TradingPage로 이동한다
3. Order Form에 TP%/SL% 인디케이터가 표시되는지 확인한다

**예상 결과**
- Auto TP/SL 토글이 OFF 상태일 때 Order Form에 TP%/SL% 인디케이터가 표시되지 않는다

---

### SETG-EXCO-001 — Exchange Connection 섹션 테스트넷 연결 상태 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage를 스크롤하여 Exchange Connection 섹션을 찾는다
2. Hyperliquid 테스트넷 연결 상태를 확인한다

**예상 결과**
- Exchange Connection 섹션에 Hyperliquid 테스트넷 연결 상태가 표시된다

---

### SETG-LOUT-001 — Logout 버튼 탭 시 Toast 메시지 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage에서 Logout 버튼을 찾는다
2. Logout 버튼의 외형(빨간색 테두리)을 확인한다
3. Logout 버튼을 탭한다
4. Toast 메시지가 표시되는지 확인한다

**예상 결과**
- Logout 버튼이 빨간색 테두리로 표시된다
- Logout 버튼 탭 시 목업 Toast 메시지가 표시된다

---

### SETG-LOUT-002 — Logout 버튼 탭 후 실제 세션 종료 미발생 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인되어 있다
- SettingsPage에 접속한 상태이다

**테스트 단계**
1. SettingsPage에서 Logout 버튼을 탭한다
2. Toast 메시지가 표시되는지 확인한다
3. Toast 메시지가 사라진 후 현재 화면 상태를 확인한다

**예상 결과**
- Logout 버튼 탭 후 Toast 메시지가 표시된다
- 실제 로그아웃이 발생하지 않는다 (SettingsPage가 그대로 표시된다)
- 로그인 페이지로 이동하지 않는다

**비고**
- [신규] 코드 근거: F-085 명세 — 실제 세션 종료 없음 (목업 Toast 처리)

---

### SETG-COCH-001 — Coach Mark 단계별 가이드 최초 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩이 완료된 후 최초로 `/trade`에 접속한 상태이다
- Coach Mark를 한 번도 본 적 없는 계정이다

**테스트 단계**
1. 온보딩 완료 후 `Start Trading` 버튼을 탭하여 TradingPage에 진입한다
2. 화면에 Coach Mark 가이드가 표시되는지 확인한다

**예상 결과**
- 단계별 Coach Mark 및 기능 하이라이트가 표시된다

**비고**
- [미결] Coach Mark 세부 내용 및 화면별 가이드 포인트 미정 — 정책 확정 후 단계별 문구 검증 필요 (P2, 미구현 가능)

---

## [ROUT] 라우팅 및 접근 제어 (F-006, F-007 기반)

---

### ★ ROUT-AUTH-001 — 미인증 사용자 /trade 직접 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 비로그인 상태이다 (인증 토큰 없음)

**테스트 단계**
1. 브라우저에서 `/trade` URL에 직접 접속한다

**예상 결과**
- `/trade` 페이지가 표시되지 않는다
- `/` (LandingPage) 또는 `/login` 페이지로 리다이렉트된다

---

### ★ ROUT-AUTH-002 — 미인증 사용자 /onboarding 직접 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- 비로그인 상태이다 (인증 토큰 없음)

**테스트 단계**
1. 브라우저에서 `/onboarding` URL에 직접 접속한다

**예상 결과**
- `/onboarding` 페이지가 표시되지 않는다
- `/` (LandingPage) 또는 `/login` 페이지로 리다이렉트된다

---

### ★ ROUT-AUTH-003 — 미인증 사용자 /terms 직접 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
- 비로그인 상태이다 (인증 토큰 없음)

**테스트 단계**
1. 브라우저에서 `/terms` URL에 직접 접속한다

**예상 결과**
- `/terms` 페이지가 표시되지 않는다
- `/` (LandingPage) 또는 `/login` 페이지로 리다이렉트된다

---

### ★ ROUT-ONBD-001 — 약관 미동의 상태에서 /onboarding 직접 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- Google OAuth 로그인은 완료된 상태이다
- 약관 미동의 상태이다 (`hasAcceptedTerms = false`)

**테스트 단계**
1. 브라우저에서 `/onboarding` URL에 직접 접속한다

**예상 결과**
- `/onboarding` 페이지가 표시되지 않는다
- `/terms` 페이지로 리다이렉트된다

---

### ★ ROUT-TRAD-001 — 온보딩 미완료 상태에서 /trade 직접 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- Google OAuth 로그인이 완료된 상태이다
- 약관 동의는 완료되었으나 온보딩이 미완료된 상태이다 (`hasCompletedOnboarding = false`)

**테스트 단계**
1. 브라우저에서 `/trade` URL에 직접 접속한다

**예상 결과**
- `/trade` 페이지가 표시되지 않는다
- `/onboarding` 페이지로 리다이렉트된다

---

### ★ ROUT-SEQN-001 — 정상 가입 흐름 라우팅 시퀀스 순서 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login → /terms → /onboarding → /trade |

**사전 조건**
- 체험 URL(`?partner_code=YOUTHMETA`)에서 접속한 신규 사용자 상태이다

**테스트 단계**
1. LandingPage에서 로그인 버튼을 탭하여 `/login`으로 이동한다
2. Google OAuth 로그인을 완료한다
3. `/terms` 페이지로 자동 이동되는지 확인한다
4. 약관 체크박스를 탭하고 Accept 버튼을 탭한다
5. `/onboarding` 페이지로 자동 이동되는지 확인한다
6. 온보딩 3단계 완료 후 `Start Trading` 버튼을 탭한다
7. `/trade` 페이지로 이동되는지 확인한다

**예상 결과**
- 로그인 → `/terms` → `/onboarding` → `/trade` 순서로 라우팅된다
- 각 단계에서 이전 단계를 건너뛰거나 역방향 이동이 발생하지 않는다

---

### ROUT-BACK-001 — 온보딩 완료 후 뒤로 가기 접근 차단 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade, /onboarding |

**사전 조건**
- 온보딩이 완료된 계정으로 `/trade` 화면에 접속한 상태이다

**테스트 단계**
1. `/trade` 화면에서 모바일 브라우저 뒤로 가기 제스처 또는 버튼을 사용한다
2. `/onboarding` 페이지로 이동되는지 확인한다

**예상 결과**
- 온보딩 완료 후 뒤로 가기 시 `/onboarding` 페이지가 표시되지 않는다
- `/trade` 화면이 유지되거나 LandingPage로 이동된다

**비고**
- [신규] 코드 근거: F-007 라우트 가드 — 완료 상태에서의 역방향 접근 처리

---

### ROUT-LOGD-001 — 로그인 완료 후 /terms로 자동 이동 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login, /terms |

**사전 조건**
- 비로그인 상태이다
- `/login` 페이지에 접속한 상태이다
- 약관 미동의 상태의 신규 계정이다

**테스트 단계**
1. `/login` 페이지에서 Google 로그인 버튼을 탭한다
2. Google OAuth 로그인 절차를 완료한다
3. 로그인 후 이동되는 페이지를 확인한다

**예상 결과**
- 로그인 완료 후 `/terms` 페이지로 자동 이동된다
- `/trade` 또는 다른 페이지로 이동되지 않는다

---

### ROUT-ALRD-001 — 이미 로그인된 사용자 /login 직접 접근 시 리다이렉트 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login, /trade |

**사전 조건**
- 온보딩이 완료된 계정으로 로그인된 상태이다

**테스트 단계**
1. 브라우저에서 `/login` URL에 직접 접속한다

**예상 결과**
- `/login` 페이지가 표시되지 않는다
- `/trade` 페이지로 리다이렉트된다

**비고**
- [신규] 코드 근거: F-006 전역 인증 상태 관리 — 이미 로그인된 사용자의 역방향 접근 처리

---

### ROUT-STAT-001 — 전역 인증 상태 3종 조합에 따른 라우팅 분기 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms, /onboarding, /trade |

**사전 조건**
- 로그인 완료, 약관 동의 완료, 온보딩 완료 상태의 계정이 있다

**테스트 단계**
1. 해당 계정으로 로그인한다
2. 앱 진입 후 이동되는 화면을 확인한다

**예상 결과**
- 로그인(`isLoggedIn=true`) + 약관 동의(`hasAcceptedTerms=true`) + 온보딩 완료(`hasCompletedOnboarding=true`) 상태에서 `/trade`로 직접 이동된다
- 중간 단계 페이지를 거치지 않는다

**비고**
- [신규] 코드 근거: F-006 전역 인증 상태 관리 — `isLoggedIn`, `hasAcceptedTerms`, `hasCompletedOnboarding` 3종 상태 분기
