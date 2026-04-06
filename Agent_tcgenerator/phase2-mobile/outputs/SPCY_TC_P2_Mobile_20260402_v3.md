# 최종 테스트 케이스 — Supercycl 모바일 체험

> 확정 일시: 2026-04-02
> 기준 문서: `03_features/feature_list.md`, `04_tc/tc_draft.md`
> 검토 보고서: `05_review/review_report.md`
> 범례: 제목 앞 `★` = 최소 TC 세트 포함

---

## [AUTH] 인증 및 온보딩

### ★ AUTH-OAUTH-001 — Google OAuth 로그인 성공 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login |

**사전 조건**
- 유효한 Google 계정이 있다
- 비로그인 상태이다
- 모바일 브라우저에서 `/login` 페이지에 접속해 있다

**테스트 단계**
1. `Google 로그인` 버튼을 탭한다
2. Google OAuth 팝업에서 유효한 Google 계정을 선택한다
3. 인증을 완료한다

**예상 결과**
- 약관 동의 화면(`/terms`)으로 이동한다
- Google 프로필 정보(이메일)가 서버에 저장된다

---

### AUTH-OAUTH-002 — Google OAuth 인증 취소 시 로그인 실패 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login |

**사전 조건**
- 비로그인 상태이다
- 모바일 브라우저에서 `/login` 페이지에 접속해 있다

**테스트 단계**
1. `Google 로그인` 버튼을 탭한다
2. Google OAuth 팝업에서 `취소` 버튼을 탭한다

**예상 결과**
- `/login` 페이지에 머문다 (화면 이동 없음)
- 오류 메시지 또는 재로그인 안내가 표시된다

---

### ★ AUTH-TERMS-001 — 약관 동의 후 온보딩 진입 확인

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
3. `Accept` 버튼을 탭한다

**예상 결과**
- 약관 동의 상태가 서버에 저장된다
- 온보딩 페이지(`/onboarding`)로 이동한다

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

**예상 결과**
- `Accept` 버튼이 비활성화(disabled) 상태이다
- 버튼을 탭해도 화면 이동이 발생하지 않는다

---

### AUTH-TERMS-003 — Decline 버튼 클릭 시 후속 처리 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
- Google OAuth 로그인이 완료된 상태이다
- `/terms` 페이지에 접속해 있다

**테스트 단계**
1. `Decline` 버튼을 탭한다

**예상 결과**
- LandingPage(`/`)로 이동한다
- 온보딩이 진행되지 않는다

**비고**
- 연관 기능: F-005

---

### ★ AUTH-ONBRD-001 — 온보딩 3단계 자동 진행 성공 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- 약관 동의가 완료된 상태이다
- `/onboarding` 페이지에 접속해 있다

**테스트 단계**
1. 온보딩 화면이 표시되는지 확인한다
2. 지갑 생성 진행 상태(단계 1)가 표시되는지 확인한다
3. Testnet 연결 진행 상태(단계 2)가 표시되는지 확인한다
4. 자금 로딩 진행 상태(단계 3)가 표시되는지 확인한다
5. 온보딩 완료 화면이 표시될 때까지 대기한다

**예상 결과**
- 3단계(지갑 생성 → Testnet 연결 → 자금 로딩)가 순차적으로 진행 상태와 함께 표시된다
- 완료 화면에 "1,000.0 USDC" 잔액이 표시된다
- `Start Trading` 버튼이 표시된다

**비고**
- F-017 기준 초기 잔고 `ACCOUNT.balance = 1,000.0 USDC` 적용

---

### AUTH-ONBRD-002 — 온보딩 단계 실패 시 오류 처리 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- 약관 동의가 완료된 상태이다
- 네트워크 오류 또는 서버 장애 상황을 시뮬레이션할 수 있다

**테스트 단계**
1. 온보딩 페이지로 진입한다
2. 네트워크를 차단하거나 서버 오류를 유발한다
3. 온보딩 단계 중 실패가 발생하는지 확인한다

**예상 결과**
- 실패한 단계에 대해 오류 메시지가 표시된다
- 재시도 버튼 또는 오류 안내가 제공된다
- 이전에 성공한 단계의 상태가 유지된다

**비고**
- 연관 기능: F-016 — 재시도 정책 미정의, 정책 확정 후 보완 필요

---

### ★ AUTH-ONBRD-003 — 온보딩 완료 후 Start Trading 진입 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- 온보딩 3단계가 모두 완료된 상태이다
- 잔액 "1,000.0 USDC"가 표시된 완료 화면이다

**테스트 단계**
1. `Start Trading` 버튼을 탭한다

**예상 결과**
- TradingPage(`/trade`)로 이동한다
- 잔액이 화면에 정상 표시된다

---

### AUTH-IOSBR-001 — iOS Safari에서 전체 인증 플로우 동작 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) - iOS Safari |
| 연관 화면 | /login → /terms → /onboarding → /trade |

**사전 조건**
- iOS Safari 브라우저에서 접속한다
- 유효한 Google 계정이 있다

**테스트 단계**
1. `/login`에서 Google OAuth 로그인을 완료한다
2. `/terms`에서 약관에 동의한다
3. `/onboarding`에서 3단계 자동 진행을 대기한다
4. 온보딩 완료 후 `Start Trading`을 탭한다

**예상 결과**
- 각 단계에서 레이아웃 깨짐 없이 화면이 정상 표시된다
- 각 화면 간 전환이 정상 동작한다
- 최종적으로 `/trade` 페이지까지 정상 진입된다

---

### AUTH-ANBR-001 — Android Chrome에서 전체 인증 플로우 동작 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) - Android Chrome |
| 연관 화면 | /login → /terms → /onboarding → /trade |

**사전 조건**
- Android Chrome 브라우저에서 접속한다
- 유효한 Google 계정이 있다

**테스트 단계**
1. `/login`에서 Google OAuth 로그인을 완료한다
2. `/terms`에서 약관에 동의한다
3. `/onboarding`에서 3단계 자동 진행을 대기한다
4. 온보딩 완료 후 `Start Trading`을 탭한다

**예상 결과**
- 각 단계에서 레이아웃 깨짐 없이 화면이 정상 표시된다
- 각 화면 간 전환이 정상 동작한다
- 최종적으로 `/trade` 페이지까지 정상 진입된다

---

### AUTH-TERMS-004 — 체크박스 토글 시 Accept 버튼 상태 전환 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
- `/terms` 페이지에 접속해 있다
- 체크박스 미선택 상태이다

**테스트 단계**
1. 약관 동의 체크박스를 탭하여 선택한다
2. `Accept` 버튼이 활성화되는지 확인한다
3. 체크박스를 다시 탭하여 해제한다
4. `Accept` 버튼 상태를 확인한다

**예상 결과**
- 체크박스 선택 시 `Accept` 버튼이 활성화 상태로 전환된다
- 체크박스 해제 시 `Accept` 버튼이 비활성화 상태로 복귀한다

---

### AUTH-INAP-001 — in-app 브라우저 접속 시 외부 브라우저 안내 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 카카오톡 또는 네이버 앱에서 서비스 URL 링크를 탭한다

**테스트 단계**
1. 카카오톡 채팅방에서 서비스 URL 링크를 탭하여 in-app 브라우저로 접속한다
2. 화면에 표시되는 안내 내용을 확인한다

**예상 결과**
- 외부 브라우저(Safari 또는 Chrome)로 열도록 안내하는 메시지가 표시된다
- in-app 브라우저에서 Google OAuth 로그인이 진행되지 않는다 (또는 안내 후 진행)

**비고**
- 연관 기능: F-008 — 안내 방법 미정의, 정책 확정 후 보완 필요

---

## [REFF] 레퍼럴 코드 자동 등록

### REFF-PARSE-001 — QR 스캔 URL에서 partner_code 정상 파싱 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 비로그인 상태이다
- QR 코드 URL에 `partner_code=YOUTHMETA` 파라미터가 포함되어 있다

**테스트 단계**
1. `https://[도메인]/?partner_code=YOUTHMETA` URL로 접속한다
2. Google OAuth 로그인을 완료한다

**예상 결과**
- 계정에 `partner_code=YOUTHMETA`가 자동 태깅된다
- 서버 DB에서 해당 계정의 partner_code가 `YOUTHMETA`로 확인된다

---

### REFF-PARSE-002 — partner_code 누락 URL 접속 시 처리 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 비로그인 상태이다

**테스트 단계**
1. `https://[도메인]/` (partner_code 파라미터 없이) URL로 접속한다
2. Google OAuth 로그인을 완료한다

**예상 결과**
- 가입은 정상 진행된다
- 계정에 partner_code가 null 또는 기본값으로 저장된다

**비고**
- 연관 기능: F-021 — partner_code 누락 시 처리 정책 미정의, 확정 후 보완 필요

---

### REFF-PARSE-003 — 변조된 partner_code URL 접속 시 처리 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 비로그인 상태이다

**테스트 단계**
1. `https://[도메인]/?partner_code=INVALID_CODE_123` URL로 접속한다
2. Google OAuth 로그인을 완료한다

**예상 결과**
- 유효하지 않은 partner_code에 대해 별도 처리가 실행된다
- 서비스가 비정상 종료되지 않는다

**비고**
- 연관 기능: F-021 — 변조 시 처리 정책 미정의, 확정 후 보완 필요

---

### REFF-PARSE-004 — partner_code에 특수문자 포함 시 파싱 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 비로그인 상태이다

**테스트 단계**
1. `https://[도메인]/?partner_code=YOUTH%20META<script>` URL로 접속한다

**예상 결과**
- XSS 공격 문자열이 실행되지 않는다
- partner_code가 정상적으로 sanitize 처리된다
- 서비스가 비정상 종료되지 않는다

---

### REFF-DISP-001 — 레퍼럴 등록 성공 표시 여부 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
- partner_code=YOUTHMETA 포함 URL로 접속하여 가입을 완료한 상태이다

**테스트 단계**
1. 온보딩 또는 가입 완료 화면에서 레퍼럴 코드 관련 표시를 확인한다

**예상 결과**
- 레퍼럴 코드 등록 완료 표시가 있거나, 미표시 정책에 따라 표시되지 않는다

**비고**
- 연관 기능: F-019~F-020 — 표시 여부 미정의, 확정 후 보완 필요

---

## [LEVR] 레버리지 제한

### LEVR-LIMIT-001 — 레버리지 2x 이내 설정 성공 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Adjust Leverage 모달) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정이다
- 온보딩 완료 후 `/trade` 페이지에 접속해 있다

**테스트 단계**
1. Adjust Leverage 모달을 연다
2. 레버리지를 `2x`로 설정한다
3. 설정을 저장한다

**예상 결과**
- 레버리지가 `2x`로 정상 설정된다
- 설정이 서버에 저장되어 주문 시 적용된다

---

### ★ LEVR-LIMIT-002 — 레버리지 2x 초과 설정 불가 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Adjust Leverage 모달) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정이다
- Adjust Leverage 모달이 열려 있다

**테스트 단계**
1. 레버리지 설정 슬라이더에서 `3x` 이상 값으로 이동을 시도한다

**예상 결과**
- 슬라이더가 2x 초과 위치로 이동하지 않는다 (슬라이더 범위 1~2, step=1)
- UI상 2x 초과 레버리지 선택이 불가하다

---

### ★ LEVR-POPUP-001 — 레버리지 안내 팝업 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 계정으로 최초 로그인하는 상태이다 (`hasSeenLeverageNotice=false`)
- 온보딩이 완료된 상태이다

**테스트 단계**
1. 온보딩 완료 후 `Start Trading`을 탭하여 TradingPage에 최초 진입한다
2. 화면에 팝업이 표시되는지 확인한다
3. 팝업의 문구를 확인한다

**예상 결과**
- LeverageNotice 팝업이 자동으로 표시된다
- 팝업에 "This account has a maximum leverage limit of 2x under the user protection policy." 문구가 표시된다
- "I Understand" 버튼이 표시된다

**비고**
- 연관 기능: F-025, F-026 — 팝업 언어(한국어/영어) 확인 필요

---

### ★ LEVR-IUND-001 — LeverageNotice "I Understand" 버튼 동작 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- TradingPage 최초 진입 시 LeverageNotice 팝업이 표시된 상태이다

**테스트 단계**
1. LeverageNotice 팝업에서 `I Understand` 버튼을 탭한다
2. 팝업이 닫히는지 확인한다
3. TradingPage로 이동하거나 TradingPage가 정상 표시되는지 재접속하여 확인한다

**예상 결과**
- `I Understand` 버튼 탭 시 팝업이 닫힌다
- `DISMISS_LEVERAGE_NOTICE`가 디스패치되어 `hasSeenLeverageNotice=true`로 변경된다
- TradingPage를 다시 진입해도 LeverageNotice 팝업이 재표시되지 않는다

**비고**
- 연관 기능: F-027

---

### LEVR-ORDR-001 — LeverageNotice → AdjustLeverage 모달 노출 순서 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 계정으로 최초 TradingPage 진입 상태이다 (`hasSeenLeverageNotice=false`)

**테스트 단계**
1. TradingPage에 진입한다
2. 화면에 표시되는 모달/팝업의 순서를 확인한다

**예상 결과**
- LeverageNotice 팝업이 먼저 표시된다
- LeverageNotice를 닫은 후 AdjustLeverage 모달이 표시된다 (또는 해당 모달 접근 가능 상태)
- AdjustLeverage 모달이 LeverageNotice보다 선행 표시되지 않는다

**비고**
- 연관 기능: F-028

---

### LEVR-WARN-001 — AdjustLeverage 모달 경고 배너 표시 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Adjust Leverage 모달) |

**사전 조건**
- TradingPage에서 AdjustLeverage 모달이 열린 상태이다

**테스트 단계**
1. AdjustLeverage 모달 내 경고 배너 영역을 확인한다
2. 배너 문구와 색상을 확인한다

**예상 결과**
- "Max leverage limited to 2x (User Protection)" 문구가 표시된다
- 배너가 노란색(`--accent-yellow`) 계열로 표시된다

**비고**
- 연관 기능: F-030

---

### LEVR-RANGE-001 — 최소 레버리지 1x 설정 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Adjust Leverage 모달) |

**사전 조건**
- Adjust Leverage 모달이 열려 있다

**테스트 단계**
1. 레버리지를 최소값 `1x`로 설정한다
2. 설정을 저장한다

**예상 결과**
- 레버리지가 `1x`로 정상 설정된다
- 1x 미만 값 입력이 불가하다

---

### LEVR-DFLT-001 — 신규 계정 레버리지 기본값 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Adjust Leverage 모달) |

**사전 조건**
- 신규 YOUTHMETA 계정으로 온보딩을 완료한 상태이다

**테스트 단계**
1. TradingPage에서 Adjust Leverage 모달을 연다
2. 현재 레버리지 기본값을 확인한다

**예상 결과**
- 기본 레버리지 값이 `2x`로 설정되어 있다 (`DEFAULT_LEVERAGE=2` 상수 기준)

**비고**
- 연관 기능: F-024

---

## [TPSL] 자동 TP/SL

### TPSL-TOGL-001 — Auto TP/SL ON 설정 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩 완료 후 Settings 탭에 접속해 있다
- Auto TP/SL이 OFF 상태이다

**테스트 단계**
1. Auto TP/SL 토글을 탭하여 ON으로 전환한다
2. 설정 상태를 확인한다

**예상 결과**
- 토글이 ON(녹색) 상태로 변경된다
- `TOGGLE_AUTO_TP_SL` 디스패치로 `autoTpSlEnabled=true` 상태가 저장된다

---

### TPSL-TOGL-002 — Auto TP/SL OFF 설정 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- Auto TP/SL이 ON 상태이다

**테스트 단계**
1. Auto TP/SL 토글을 탭하여 OFF로 전환한다
2. 설정 상태를 확인한다

**예상 결과**
- 토글이 OFF(기본 배경색) 상태로 변경된다
- 이후 주문 체결 시 TP/SL이 자동 생성되지 않는다

---

### ★ TPSL-AUTO-001 — Auto TP/SL ON 상태에서 주문 체결 시 TP/SL 자동 생성 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- Auto TP/SL이 ON 상태이다
- 기본 TP: +1.8%, SL: -5.0% 설정이다 (`DEFAULT_TP_PERCENT=1.8`, `DEFAULT_SL_PERCENT=5.0`)
- 충분한 mock USDC 잔고가 있다

**테스트 단계**
1. Trade 탭에서 BTC/USDC 시장가 Buy/Long 주문을 실행한다
2. 주문 체결 후 Dashboard 포지션 탭의 포지션 카드를 확인한다

**예상 결과**
- 포지션에 TP(진입가 +1.8%)와 SL(진입가 -5.0%)이 자동 설정된다
- 포지션 카드에 녹색 Auto 배지(9px 폰트)가 표시된다
- TP/SL 값이 포지션 카드에 표시된다

---

### TPSL-AUTO-002 — Auto TP/SL OFF 상태에서 주문 체결 시 TP/SL 미생성 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- Auto TP/SL이 OFF 상태이다
- 충분한 mock USDC 잔고가 있다

**테스트 단계**
1. Trade 탭에서 BTC/USDC 시장가 Buy/Long 주문을 실행한다
2. 주문 체결 후 포지션 카드를 확인한다

**예상 결과**
- 포지션에 TP/SL이 설정되지 않는다
- 포지션 카드에 Auto 배지가 표시되지 않는다

---

### TPSL-EDIT-001 — Settings에서 TP/SL 퍼센트 수정 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- Settings 탭에 접속해 있다
- Auto TP/SL이 ON 상태이다

**테스트 단계**
1. Trading Preferences 섹션에서 Auto TP/SL `Edit` 버튼을 탭한다
2. AutoTpSlModal이 표시되면 TP 퍼센트 값을 `3.0`으로 변경한다
3. SL 퍼센트 값을 `2.0`으로 변경한다
4. 확인 버튼을 탭한다

**예상 결과**
- 변경된 값(TP 3.0%, SL 2.0%)이 Settings 화면에 표시된다
- 이후 새 주문 체결 시 변경된 비율이 적용된다

---

### TPSL-FAIL-001 — TP/SL 자동 생성 실패 시 오류 처리 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- Auto TP/SL이 ON 상태이다
- 네트워크 불안정 상태를 시뮬레이션할 수 있다

**테스트 단계**
1. 시장가 주문을 실행한다
2. 주문 체결 직후 네트워크를 일시 차단한다
3. TP/SL 생성 결과를 확인한다

**예상 결과**
- TP/SL 생성 실패 시 오류 알림이 표시된다
- 재시도 또는 수동 설정 안내가 제공된다

**비고**
- 연관 기능: F-031/F-032 — 처리 정책 미정의, 확정 후 보완 필요

---

### TPSL-DFLT-001 — 신규 가입 시 Auto TP/SL 기본 상태 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 신규 계정으로 온보딩을 완료한 상태이다

**테스트 단계**
1. Settings 탭에서 Auto TP/SL 토글의 기본 상태를 확인한다

**예상 결과**
- 기본 상태가 정책에 따라 ON 또는 OFF로 설정되어 있다

**비고**
- 연관 기능: F-041 — 초기 ON/OFF 여부 미확정, 확정 후 보완 필요

---

### TPSL-INDI-001 — Order Form Auto TP/SL 인디케이터 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Order Form) |

**사전 조건**
- Auto TP/SL이 ON 상태이다
- Trade 탭의 Order Form이 표시되어 있다

**테스트 단계**
1. Order Form 영역에서 Auto TP/SL 인디케이터를 확인한다

**예상 결과**
- Order Form에 TP%/SL% 수치와 Edit 버튼이 포함된 Auto TP/SL 인디케이터가 표시된다

---

## [TRAD] 트레이딩/주문

### ★ TRAD-MRKT-001 — Market 주문(Buy/Long) 실행 성공 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩 완료 후 Trade 탭에 접속해 있다
- 충분한 mock USDC 잔고(1,000 USDC)가 있다

**테스트 단계**
1. CoinSelector에서 `BTC/USDC`를 선택한다
2. 주문 유형을 `Market`으로 선택한다
3. 수량 슬라이더를 `25%`로 설정한다
4. `Buy/Long` 버튼을 탭한다

**예상 결과**
- 주문이 체결되고 Toast 알림이 표시된다
- Dashboard 포지션 탭에 BTC Long 포지션이 표시된다
- 잔고가 주문 금액만큼 차감된다

---

### ★ TRAD-MRKT-002 — Market 주문(Sell/Short) 실행 성공 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩 완료 후 Trade 탭에 접속해 있다
- 충분한 mock USDC 잔고가 있다

**테스트 단계**
1. CoinSelector에서 `ETH/USDC`를 선택한다
2. 주문 유형을 `Market`으로 선택한다
3. 수량 슬라이더를 `50%`로 설정한다
4. `Sell/Short` 버튼을 탭한다

**예상 결과**
- 주문이 체결되고 Toast 알림이 표시된다
- Dashboard 포지션 탭에 ETH Short 포지션이 표시된다

---

### TRAD-LMIT-001 — Limit 주문 제출 성공 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- Trade 탭에 접속해 있다
- 충분한 mock USDC 잔고가 있다

**테스트 단계**
1. CoinSelector에서 `SOL/USDC`를 선택한다
2. 주문 유형을 `Limit`으로 선택한다
3. 지정 가격 입력 필드가 표시되는지 확인한다
4. 지정 가격을 현재가보다 낮게 입력한다
5. 수량 슬라이더를 설정한다
6. `Buy/Long` 버튼을 탭한다

**예상 결과**
- 주문이 제출되고 Toast 알림이 표시된다
- `Market` 선택 시 가격 입력 필드가 숨겨지고, `Limit` 선택 시 표시된다

---

### TRAD-FAIL-001 — 잔고 부족 시 주문 실패 오류 메시지 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- mock USDC 잔고가 거의 없는 상태이다 (이미 대부분 포지션에 투입)

**테스트 단계**
1. 주문 유형을 `Market`으로 선택한다
2. 수량 슬라이더를 `100%`로 설정한다 (잔고 초과 시도)
3. `Buy/Long` 버튼을 탭한다

**예상 결과**
- 주문이 거부된다
- 잔고 부족 관련 오류 메시지가 표시된다
- 포지션이 생성되지 않는다

**비고**
- 연관 기능: F-046 — 오류 메시지 정책 미정의, 확정 후 보완 필요

---

### ★ TRAD-COIN-001 — CoinSelector에서 지원 코인 8개 목록 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (CoinSelector 모달) |

**사전 조건**
- Trade 탭에 접속해 있다

**테스트 단계**
1. CoinSelector 모달을 연다
2. 표시되는 코인 목록을 확인한다

**예상 결과**
- BTC, ETH, SOL, DOGE, ARB, AVAX, MATIC, LINK 8개 코인이 USDC 페어로 표시된다
- 8개 이외의 코인은 표시되지 않는다

---

### TRAD-DASH-001 — Dashboard 3탭 구성 및 포지션 정보 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard) |

**사전 조건**
- 체결된 포지션이 1개 이상 있다

**테스트 단계**
1. Dashboard의 포지션(Positions) 탭을 확인한다
2. 미체결주문(Open Orders) 탭을 탭한다
3. 히스토리(History) 탭을 탭한다

**예상 결과**
- 포지션 탭: 코인명, 방향(Long/Short), 진입가, 현재가, PnL, TP/SL이 표시된다
- 미체결주문 탭: "No open orders" 빈 상태 메시지가 표시된다 (미구현 탭)
- 히스토리 탭: "No order history" 빈 상태 메시지가 표시된다 (미구현 탭)

---

### TRAD-NTWK-001 — 네트워크 오류 시 주문 실패 처리 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- Trade 탭에서 주문 준비가 완료된 상태이다

**테스트 단계**
1. 네트워크를 차단한다
2. `Buy/Long` 버튼을 탭한다
3. 결과를 확인한다

**예상 결과**
- 네트워크 오류 메시지가 표시된다
- 포지션이 생성되지 않는다
- 잔고 차감이 발생하지 않는다

---

### TRAD-SLDR-001 — 수량 퍼센트 슬라이더 경계값(0%, 100%) 동작 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Order Form) |

**사전 조건**
- Trade 탭에 접속해 있다
- 충분한 mock USDC 잔고가 있다

**테스트 단계**
1. 수량 슬라이더를 `0%`로 설정한다
2. `Buy/Long` 버튼의 활성화 상태를 확인한다
3. 수량 슬라이더를 `100%`로 설정한다
4. `Buy/Long` 버튼을 탭하여 주문을 실행한다

**예상 결과**
- 0% 설정 시: 주문 버튼이 비활성화되거나 주문 제출 시 거부된다
- 100% 설정 시: 전체 잔고에 해당하는 수량으로 주문이 실행된다

---

### TRAD-MOCK-001 — mock USDC 전용 거래 제한 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | 공통 |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩 완료 후 Trade 탭에 접속해 있다

**테스트 단계**
1. 잔고 표시 영역에서 통화 종류를 확인한다
2. 주문 실행 시 사용되는 자산이 mock USDC인지 확인한다

**예상 결과**
- 화면에 표시되는 잔고가 mock USDC(Testnet)로 명시된다
- 실제 자금 입출금 기능이 없다

---

## [SGNL] 시그널

### SGNL-LIST-001 — Signal 탭 시그널 목록 조회 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- 온보딩 완료 상태이다
- Signal 탭에 접속해 있다

**테스트 단계**
1. Signal 탭에서 "⚡ YouthMeta Signals" 헤더가 표시되는지 확인한다
2. 성과 요약(Hit/Miss/Expired 건수, 평균 PnL%, 성공률%)을 확인한다

**예상 결과**
- 시그널 목록이 1개 이상 표시된다
- 성과 요약 데이터가 화면에 표시된다

**비고**
- 연관 기능: F-056, F-057 — 행사 체험 범위 포함 여부 확인 필요

---

### SGNL-EXEC-001 — Execute Signal로 포지션 생성 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭 → Trade 탭) |

**사전 조건**
- Signal 탭에 Active 시그널이 1개 이상 있다
- 충분한 mock USDC 잔고가 있다

**테스트 단계**
1. Active 시그널 카드에서 `Execute Signal` 버튼을 탭한다
2. SignalOrderSheet 바텀시트가 표시되는지 확인한다
3. 바텀시트에서 코인, 방향, 진입가, 타겟가, 손절가, 레버리지 정보를 확인한다
4. `Execute Order` 버튼을 탭한다

**예상 결과**
- `EXECUTE_SIGNAL_ORDER` 디스패치 후 Toast 알림이 표시된다
- Dashboard 포지션 탭에 새 포지션이 표시된다

---

### SGNL-LEVR-001 — 시그널 주문에 레버리지 2x 제한 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- YOUTHMETA 계정이다
- 시그널에 레버리지 3x 이상이 설정된 시그널이 있다

**테스트 단계**
1. 해당 시그널의 `Execute Signal` 버튼을 탭한다
2. SignalOrderSheet에서 레버리지 표시를 확인한다

**예상 결과**
- 시그널의 레버리지가 2x를 초과하더라도 실제 주문은 최대 2x로 제한되어 실행된다
- 레버리지 제한 적용 안내가 표시된다

**비고**
- 연관 기능: F-062 — 시그널 레버리지 > 2x 시 처리 미정의, 확정 후 보완 필요

---

### SGNL-MODI-001 — Modify 버튼으로 주문 폼 PREFILL 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭 → Trade 탭) |

**사전 조건**
- Signal 탭에 Active 시그널이 있다

**테스트 단계**
1. 시그널 카드에서 `Modify` 버튼을 탭한다
2. Trade 탭의 Order Form 값을 확인한다

**예상 결과**
- Trade 탭으로 전환된다
- Order Form에 시그널의 코인, 방향, 진입가, TP, SL 값이 PREFILL되어 있다
- 사용자가 PREFILL된 값을 수정할 수 있다

---

### SGNL-FILT-001 — 시그널 필터 탭 동작 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Signal 탭) |

**사전 조건**
- Signal 탭에 다양한 상태(Active, Closed, Long, Short)의 시그널이 있다

**테스트 단계**
1. `All` 필터를 탭하고 결과를 확인한다
2. `Long` 필터를 탭하고 결과를 확인한다
3. `Short` 필터를 탭하고 결과를 확인한다
4. `Active` 필터를 탭하고 결과를 확인한다
5. `Closed` 필터를 탭하고 결과를 확인한다

**예상 결과**
- `All`: 전체 시그널이 표시된다
- `Long`/`Short`: 해당 방향 시그널만 표시된다
- `Active`: 활성 시그널만 표시된다
- `Closed`: HIT_TP, HIT_SL, EXPIRED, CANCELLED 상태 시그널이 표시된다

---

## [FUND] 테스트넷 자금

### ★ FUND-TRNS-001 — 마스터 지갑에서 유저 지갑으로 자금 자동 전송 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | 공통 |
| 연관 화면 | /onboarding |

**사전 조건**
- 온보딩 중 자금 로딩 단계이다
- 마스터 지갑에 충분한 mock USDC가 있다

**테스트 단계**
1. 온보딩 자금 로딩 단계 진행을 관찰한다
2. 완료 후 온보딩 완료 화면의 잔고를 확인한다

**예상 결과**
- mock USDC가 유저 지갑으로 자동 전송된다
- 온보딩 완료 화면에 "1,000.0 USDC" 잔고가 표시된다

---

### ★ FUND-TIME-001 — 잔고 10초 이내 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | 공통 |
| 연관 화면 | /onboarding |

**사전 조건**
- 온보딩 중 자금 전송이 시작된 상태이다

**테스트 단계**
1. 자금 전송 시작 시점부터 시간을 측정한다
2. 유저 화면에 잔고가 반영되는 시점을 확인한다

**예상 결과**
- 전송 후 약 10초 이내에 유저 화면에 잔고가 표시된다

---

### FUND-FAIL-001 — 자금 전송 실패 시 재시도 처리 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | 공통 |
| 연관 화면 | /onboarding |

**사전 조건**
- 네트워크 불안정 상태를 시뮬레이션할 수 있다

**테스트 단계**
1. 온보딩 자금 로딩 단계에서 네트워크를 일시 차단한다
2. 전송 실패 발생을 확인한다
3. 네트워크를 복구한다

**예상 결과**
- 전송 실패 시 오류 메시지가 표시된다
- 자동 재시도 또는 수동 재시도 옵션이 제공된다

**비고**
- 연관 기능: F-016 — 재시도 정책 미정의, 확정 후 보완 필요

---

### FUND-AMNT-001 — 유저당 지급 금액 일관성 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | High |
| 플랫폼 | 공통 |
| 연관 화면 | /onboarding |

**사전 조건**
- 신규 계정으로 온보딩을 진행한다

**테스트 단계**
1. 온보딩 완료 후 표시되는 잔고 금액을 확인한다
2. 실제 지갑에 전송된 mock USDC 금액을 확인한다 (API/DB 확인)

**예상 결과**
- 화면 표시 금액이 "1,000.0 USDC"이다 (`ACCOUNT.balance=1,000.0 USDC` 상수 기준)
- 화면 표시 금액과 실제 전송 금액이 일치한다

**비고**
- 연관 기능: F-017 — `ACCOUNT.balance = 1,000.0 USDC` 상수 기준 확정

---

### FUND-CONC-001 — 다수 동시 가입 시 자금 전송 안정성 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | High |
| 플랫폼 | 공통 |
| 연관 화면 | /onboarding |

**사전 조건**
- 부하 테스트 환경이 준비되어 있다

**테스트 단계**
1. 10개 이상의 계정이 동시에 온보딩을 진행한다
2. 각 계정의 자금 전송 결과를 확인한다

**예상 결과**
- 모든 계정에 mock USDC가 정상 전송된다
- 병목으로 인한 전송 실패가 발생하지 않거나 큐 시스템으로 순차 처리된다

**비고**
- 연관 기능: F-014 — 동시 가입 병목 대응 구현 범위 미확정

---

## [MOBL] 모바일 UI

### ★ MOBL-RESP-001 — Trading Page 모바일 반응형 레이아웃 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 모바일 브라우저(375x812 이상)에서 접속해 있다
- 온보딩 완료 상태이다

**테스트 단계**
1. Trade 탭의 전체 레이아웃을 확인한다
2. Order Form, Dashboard, Chart, Coin Info Bar 영역이 모바일에 맞게 배치되는지 확인한다
3. 가로 스크롤 발생 여부를 확인한다

**예상 결과**
- 각 영역이 겹침 없이 최대 너비 320px 모바일 화면에 맞게 배치된다
- 가로 스크롤이 발생하지 않는다
- 모든 텍스트 요소가 읽을 수 있는 크기로 표시된다

---

### MOBL-TUCH-001 — 모바일 터치 버튼 크기 및 탭 영역 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 모바일 브라우저에서 Trade 탭에 접속해 있다

**테스트 단계**
1. `Buy/Long` 버튼을 탭한다
2. `Sell/Short` 버튼을 탭한다
3. 수량 슬라이더를 조작한다
4. 탭 전환 버튼들을 탭한다

**예상 결과**
- 모든 버튼이 한 번의 탭으로 정확히 동작한다
- 터치 영역이 최소 44x44px 이상이다
- 버튼 간 간격이 충분하여 오탭이 발생하지 않는다

---

### MOBL-TEST-001 — TESTNET 배지 상시 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | 공통 |

**사전 조건**
- 온보딩 완료 후 서비스에 접속해 있다

**테스트 단계**
1. Trade 탭에서 TESTNET 배지를 확인한다
2. Signal 탭에서 TESTNET 배지를 확인한다
3. Settings 탭에서 TESTNET 배지를 확인한다

**예상 결과**
- 모든 화면에서 TESTNET 배지가 상시 표시된다
- "실제 자금이 아님" 고지 문구가 확인된다

**비고**
- 연관 기능: F-067 — 구체적 문구 미확정, 확정 후 보완 필요

---

### MOBL-LAND-001 — LandingPage TESTNET 배지 및 면책 고지문 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 비로그인 상태이다
- LandingPage에 접속해 있다

**테스트 단계**
1. LandingPage에서 TESTNET 배지를 확인한다
2. 면책 고지문 표시를 확인한다
3. LandingPage 하단 "TESTNET MODE" 배너를 확인한다

**예상 결과**
- TESTNET 배지가 화면에 표시된다
- 면책 고지문이 화면에 표시된다
- 하단 "TESTNET MODE" 배너가 상시 노출된다

**비고**
- 연관 기능: F-064 — 면책 고지문 문구 미확정, 확정 후 보완 필요

---

### MOBL-NOBD-001 — TESTNET 배지 미표시 시 사용자 혼동 위험 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | 공통 |

**사전 조건**
- 서비스에 접속해 있다

**테스트 단계**
1. 모든 주요 화면(Landing, Trade, Signal, Settings)을 순회한다
2. TESTNET 배지가 누락된 화면이 있는지 확인한다

**예상 결과**
- TESTNET 배지가 누락된 화면이 없다
- 모든 화면에서 테스트넷임을 식별할 수 있다

---

### ★ MOBL-BNAV-001 — BottomNav 4탭 고정 하단 네비게이션 동작 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 온보딩 완료 후 TradingPage에 접속해 있다

**테스트 단계**
1. 화면 하단 네비게이션 바에서 4개 탭(trade, signal, portfolio, settings)이 표시되는지 확인한다
2. `Signal` 탭을 탭한다
3. `Settings` 탭을 탭한다
4. `Portfolio` 탭을 탭한다
5. `Trade` 탭을 탭한다

**예상 결과**
- 하단에 BottomNav가 고정 표시된다
- 각 탭 탭 시 해당 화면으로 전환된다
- 탭 콘텐츠 영역이 BottomNav 위로 64px 여백을 두고 스크롤 가능하다

**비고**
- 연관 기능: F-074, F-075

---

## [SETG] 설정/계정

### SETG-INFO-001 — 계정 정보(이메일, 지갑 주소) 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩 완료 후 Settings 탭에 접속해 있다

**테스트 단계**
1. Account 섹션에서 이메일을 확인한다
2. 지갑 주소를 확인한다

**예상 결과**
- Google 로그인 시 사용한 이메일이 표시된다 (`ACCOUNT.email`)
- 자동 생성된 지갑 주소가 표시된다 (`ACCOUNT.wallet`)

---

### SETG-COPY-001 — 지갑 주소 복사 버튼 동작 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- Settings 탭에서 지갑 주소가 표시되어 있다

**테스트 단계**
1. 지갑 주소 옆 `복사` 버튼을 탭한다
2. 메모장 등에 붙여넣기하여 복사된 내용을 확인한다

**예상 결과**
- 지갑 주소가 클립보드에 복사된다
- 화면에 Toast "Address copied!" 메시지가 표시된다

**비고**
- 연관 기능: F-081

---

### SETG-LGOT-001 — 로그아웃 버튼 탭 시 Toast 메시지 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 로그인 상태이다
- Settings 탭에 접속해 있다

**테스트 단계**
1. 빨간색 테두리 `Logout` 버튼을 탭한다

**예상 결과**
- 목업 Toast 메시지가 표시된다 (실제 세션 종료 없음)

**비고**
- 연관 기능: F-085 — 실제 세션 종료가 구현되지 않은 목업 동작

---

### SETG-RLOG-001 — 재로그인 시 데이터 유지 여부 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / → /trade |

**사전 조건**
- 포지션을 보유한 상태에서 로그아웃한다

**테스트 단계**
1. 로그아웃한다
2. 동일 Google 계정으로 재로그인한다
3. Trade 탭에서 기존 포지션 및 잔고를 확인한다

**예상 결과**
- 재로그인 후 기존 포지션/잔고 유지 여부가 정책에 따라 처리된다

**비고**
- 연관 기능: F-001, F-006 — 유지 여부 미정의, 확정 후 보완 필요

---

### SETG-EXCH-001 — 거래소 연결 상태 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩 완료 후 Settings 탭에 접속해 있다

**테스트 단계**
1. Exchange Connection 섹션을 확인한다

**예상 결과**
- "Hyperliquid (Testnet)" 텍스트가 표시된다
- 연결 상태가 "Connected" 또는 이에 준하는 표시로 확인된다

---

## [ROUT] 라우팅/접근 제어

### ROUT-LAND-001 — 비로그인 상태에서 LandingPage 접근 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / (LandingPage) |

**사전 조건**
- 비로그인 상태이다

**테스트 단계**
1. `/` URL로 접속한다

**예상 결과**
- LandingPage가 정상 표시된다

---

### ROUT-LAND-002 — 로그인 상태에서 LandingPage 접근 시 리다이렉트 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / → /trade |

**사전 조건**
- 온보딩 완료된 로그인 상태이다

**테스트 단계**
1. 브라우저 주소창에 `/` URL을 직접 입력하여 접속한다

**예상 결과**
- LandingPage가 표시되지 않고 `/trade`로 리다이렉트된다

**비고**
- 인증 완료 사용자의 `/` 접근 시 자동 리다이렉트는 의도된 라우트 동작

---

### ★ ROUT-TRAD-001 — 미인증 사용자 TradingPage 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade → / |

**사전 조건**
- 비로그인 상태이다

**테스트 단계**
1. 브라우저 주소창에 `/trade` URL을 직접 입력하여 접속한다

**예상 결과**
- `/trade` 페이지에 접근되지 않는다
- LandingPage(`/`)로 리다이렉트된다

---

### ★ ROUT-TERM-001 — 약관 미동의 상태에서 TradingPage 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade → /terms |

**사전 조건**
- Google OAuth 로그인은 완료했으나 약관 동의를 하지 않은 상태이다

**테스트 단계**
1. 브라우저 주소창에 `/trade` URL을 직접 입력하여 접속한다

**예상 결과**
- `/trade` 페이지에 접근되지 않는다
- `/terms` 페이지로 리다이렉트된다

---

### ★ ROUT-ONBD-001 — 온보딩 미완료 상태에서 TradingPage 접근 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade → /onboarding |

**사전 조건**
- 약관 동의는 완료했으나 온보딩이 미완료 상태이다

**테스트 단계**
1. 브라우저 주소창에 `/trade` URL을 직접 입력하여 접속한다

**예상 결과**
- `/trade` 페이지에 접근되지 않는다
- `/onboarding` 페이지로 리다이렉트된다

---

### ROUT-TERM-002 — 약관 동의 완료 상태에서 TermsPage 재접근 처리 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
- 약관 동의가 완료된 상태이다

**테스트 단계**
1. 브라우저 주소창에 `/terms` URL을 직접 입력하여 접속한다

**예상 결과**
- `/terms` 페이지가 표시되지 않고 다음 단계(온보딩 또는 Trade)로 리다이렉트된다

---

### ROUT-SETG-001 — 온보딩 완료 후 SettingsPage 접근 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- 온보딩 완료 상태이다

**테스트 단계**
1. 하단 네비게이션에서 `Settings` 탭을 탭한다

**예상 결과**
- Settings 화면이 정상 표시된다
- Account 정보, Auto TP/SL 설정, Exchange Connection 상태가 표시된다

---

### ★ ROUT-SEQN-001 — 전체 라우팅 시퀀스 정상 흐름 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / → /login → /terms → /onboarding → /trade |

**사전 조건**
- 신규 사용자, 비로그인 상태이다
- 유효한 Google 계정이 있다

**테스트 단계**
1. LandingPage(`/`)에 접속한다
2. 로그인 페이지(`/login`)로 이동하여 Google OAuth 로그인을 완료한다
3. TermsPage(`/terms`)에서 약관 체크박스를 탭하고 Accept를 탭한다
4. OnboardingPage(`/onboarding`)에서 3단계 완료를 대기한다
5. `Start Trading`을 탭하여 TradingPage(`/trade`)에 진입한다

**예상 결과**
- 전체 시퀀스가 순서대로 정상 진행된다
- 각 단계에서 이전/다음 단계 이외의 페이지로 이동하지 않는다
- 최종적으로 `/trade` 페이지에 도달하여 거래가 가능한 상태이다

---

# TC 통계 (최종)

## 총 개수: 60개 (초안 55개 + 신규 5개)

## 분류별 분포

| 분류 | 개수 | 비율 |
|------|------|------|
| **Positive** | 31 | 51.7% |
| **Negative** | 17 | 28.3% |
| **Edge** | 12 | 20.0% |
| **합계** | **60** | **100%** |

> 기준: Positive 50%, Negative 30%, Edge 20% — 기준 충족

## 우선순위별 분포

| 우선순위 | 개수 | 비율 |
|----------|------|------|
| **High** | 41 | 68.3% |
| **Medium** | 13 | 21.7% |
| **Low** | 6 | 10.0% |
| **합계** | **60** | **100%** |

## 도메인별 분포

| 도메인 | 코드 | TC 수 | Positive | Negative | Edge | ★ 최소 세트 |
|--------|------|-------|----------|----------|------|------------|
| 인증/온보딩 | AUTH | 12 | 7 | 3 | 2 | 5 |
| 레퍼럴 코드 | REFF | 5 | 2 | 2 | 1 | 0 |
| 레버리지 | LEVR | 8 | 5 | 1 | 2 | 4 |
| 자동 TP/SL | TPSL | 8 | 4 | 2 | 2 | 1 |
| 트레이딩/주문 | TRAD | 9 | 5 | 2 | 2 | 3 |
| 시그널 | SGNL | 5 | 3 | 1 | 1 | 0 |
| 테스트넷 자금 | FUND | 5 | 2 | 1 | 2 | 2 |
| 모바일 UI | MOBL | 6 | 5 | 1 | 0 | 2 |
| 설정/계정 | SETG | 5 | 3 | 0 | 2 | 0 |
| 라우팅/접근 제어 | ROUT | 8 | 4 | 4 | 2 | 4 |
| **합계** | | **60** | **31** | **16** | **17** | **20** |

## 최소 TC 세트 (★) — 20개
AUTH-OAUTH-001, AUTH-TERMS-001, AUTH-TERMS-002, AUTH-ONBRD-001, AUTH-ONBRD-003,
LEVR-LIMIT-002, LEVR-POPUP-001, LEVR-IUND-001,
TPSL-AUTO-001,
TRAD-MRKT-001, TRAD-MRKT-002, TRAD-COIN-001,
FUND-TRNS-001, FUND-TIME-001,
MOBL-RESP-001, MOBL-BNAV-001,
ROUT-TRAD-001, ROUT-TERM-001, ROUT-ONBD-001, ROUT-SEQN-001

## 초안 대비 주요 수정 사항
| 구분 | 내용 |
|------|------|
| 잔액 수정 | AUTH-ONBRD-001, TRAD-MRKT-001, FUND-AMNT-001: 10,000 → 1,000 USDC |
| 예상 결과 수정 | AUTH-TERMS-003: Decline 시 `/`로 이동으로 명확화 |
| 예상 결과 수정 | SETG-LGOT-001: 실제 세션 종료 아닌 목업 Toast로 수정 |
| 예상 결과 수정 | LEVR-POPUP-001: 정확한 팝업 문구 추가 |
| 예상 결과 수정 | TRAD-DASH-001: Open Orders/History 빈 상태 표시로 수정 |
| 분류 변경 | ROUT-LAND-002: Negative → Edge |
| 예상 결과 구체화 | AUTH-IOSBR-001, AUTH-ANBR-001: 측정 가능한 관찰 포인트로 수정 |
| 신규 추가 | AUTH-INAP-001: in-app 브라우저 비호환 안내 (F-008) |
| 신규 추가 | LEVR-IUND-001: "I Understand" 버튼 동작 (F-027) |
| 신규 추가 | LEVR-ORDR-001: 모달 노출 순서 (F-028) |
| 신규 추가 | LEVR-WARN-001: AdjustLeverage 경고 배너 (F-030) |
| 신규 추가 | MOBL-BNAV-001: BottomNav 4탭 네비게이션 (F-074) |
