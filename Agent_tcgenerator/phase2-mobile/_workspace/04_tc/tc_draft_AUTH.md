# TC 초안 — AUTH / REFF 도메인 (F-001~F-021)

> 작성 일시: 2026-04-02
> 적용 규칙: common/tc-rules.md + phase2-mobile/tc-rules-override.md
> 담당 기능: F-001~F-021 (21개)
> 작성 TC 수: 19개

---

## [AUTH] 인증 — 가입 및 로그인 (F-001~F-008)

---

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
- 각 단계 완료 시 완료 상태(체크마크 등)로 전환된다
- 완료 화면에 체크마크와 USDC 잔액이 표시된다
- `Start Trading` 버튼이 표시된다

**비고**
- [미결] 완료 화면의 초기 잔액 표시 값: 기획서 기준 1,000 USDC / 코드 기준 10,000 USDC — 정책 확정 필요

---

### AUTH-ONBD-002 — 온보딩 완료 화면 CEX 안내 문구 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- 온보딩 3단계가 모두 완료된 상태이다
- 온보딩 완료 화면이 표시된 상태이다

**테스트 단계**
1. 완료 화면의 텍스트 내용을 확인한다

**예상 결과**
- CEX 통합 예정 안내 문구가 표시된다

**비고**
- [미결] 안내 문구 포함 여부 및 최종 문구 내용 확정 필요

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

## 전체 TC 목록 요약

| TC ID | 제목 | 분류 | 우선순위 | ★ |
|-------|------|------|----------|---|
| AUTH-OAUTH-001 | Google OAuth 로그인 성공 후 약관 페이지 진입 확인 | Positive | High | ★ |
| AUTH-OAUTH-002 | 미인증 상태에서 보호 페이지 직접 접근 시 리다이렉트 확인 | Negative | High | ★ |
| AUTH-TERMS-001 | 약관 동의 후 온보딩 페이지 진입 확인 | Positive | High | ★ |
| AUTH-TERMS-002 | 체크박스 미선택 시 Accept 버튼 비활성화 확인 | Negative | High | ★ |
| AUTH-TERMS-003 | 약관 페이지 필수 요소 렌더링 확인 | Positive | High | |
| AUTH-TERMS-004 | Decline 클릭 시 LandingPage 이동 확인 | Negative | High | ★ |
| AUTH-GUARD-001 | 약관 동의 완료 계정의 /terms 재접근 차단 확인 | Negative | High | ★ |
| AUTH-GUARD-002 | 온보딩 완료 계정의 /onboarding 재접근 차단 확인 | Negative | High | |
| AUTH-INAPP-001 | in-app 브라우저 접속 시 외부 브라우저 안내 표시 확인 | Negative | Medium | |
| AUTH-ONBD-001 | 온보딩 3단계 순차 진행 및 완료 화면 표시 확인 | Positive | High | ★ |
| AUTH-ONBD-002 | 온보딩 완료 화면 CEX 안내 문구 표시 확인 | Positive | High | |
| AUTH-ONBD-003 | "Start Trading" 버튼 탭 후 TradingPage 진입 확인 | Positive | High | ★ |
| AUTH-FUND-001 | 온보딩 완료 후 초기 USDC 잔고 반영 확인 | Positive | High | ★ |
| AUTH-FUND-002 | 자금 전송 지연 시 안내 메시지 표시 확인 | Negative | Medium | |
| AUTH-FUND-003 | 자금 전송 실패 시 오류 안내 표시 확인 | Negative | High | ★ |
| AUTH-CONST-001 | 신규 계정 초기 잔고 상수(1,000 USDC) 적용 확인 | Positive | High | |
| REFF-PARS-001 | URL에 partner_code=YOUTHMETA 포함 시 가입 태깅 확인 | Positive | Medium | |
| REFF-PARS-002 | URL에 partner_code 누락 시 처리 확인 | Negative | Medium | |
| REFF-CODE-001 | YOUTHMETA 상수 파트너 코드 적용 확인 [신규] | Positive | Medium | |

---

## 기능-TC 커버리지 매핑

| 기능 ID | 기능명 | 커버 TC |
|---------|--------|---------|
| F-001 | Google OAuth 원클릭 가입/로그인 | AUTH-OAUTH-001 |
| F-002 | 약관 동의 페이지 렌더링 | AUTH-TERMS-003 |
| F-003 | 약관 체크박스 미동의 시 Accept 버튼 비활성화 | AUTH-TERMS-002 |
| F-004 | 약관 동의 후 온보딩 진입 | AUTH-TERMS-001 |
| F-005 | Decline 클릭 시 랜딩 페이지 이동 | AUTH-TERMS-004 |
| F-006 | 전역 인증 상태 관리 | AUTH-GUARD-001, AUTH-GUARD-002 |
| F-007 | 라우트 가드 — 미인증 리다이렉트 | AUTH-OAUTH-002 |
| F-008 | in-app 브라우저 비호환 안내 | AUTH-INAPP-001 |
| F-009 | 온보딩 단계 1 — 지갑 자동 생성 | AUTH-ONBD-001 |
| F-010 | 온보딩 단계 2 — Testnet 연결 | AUTH-ONBD-001 |
| F-011 | 온보딩 단계 3 — 테스트 자금 로딩 | AUTH-ONBD-001 |
| F-012 | 온보딩 완료 화면 표시 | AUTH-ONBD-001, AUTH-ONBD-002 |
| F-013 | "Start Trading" 버튼 동작 | AUTH-ONBD-003 |
| F-014 | 마스터 지갑 → 유저 지갑 mock USDC 전송 | AUTH-FUND-001 |
| F-015 | 자금 전송 지연 시 안내 메시지 | AUTH-FUND-002 |
| F-016 | 자금 전송 실패 처리 | AUTH-FUND-003 |
| F-017 | 기본 계정 잔고 상수 적용 | AUTH-CONST-001 |
| F-018 | 파트너 코드 상수 하드코딩 | REFF-CODE-001 |
| F-019 | URL 파라미터 partner_code 파싱 | REFF-PARS-001 |
| F-020 | 가입 시 레퍼럴 코드 자동 태깅 | REFF-PARS-001 |
| F-021 | partner_code 누락 시 처리 | REFF-PARS-002 |
