# Phase 3 TC 최종본 — P3_MobileMockup

## 메타 정보
- 생성일: 2026-04-03
- Phase: P3_MobileMockup
- 거래소: Hyperliquid Testnet
- 플랫폼: Web(Mobile) 360px
- 총 TC: 107개
- ★ TC: 41개 (38.3%)
- 커버리지: 100% (42/42 기능)

---


# TC 초안 — AUTH 도메인 (인증/온보딩)

**작성일:** 2026-04-03
**도메인:** AUTH — 인증/온보딩
**중분류:** LOGN (로그인), TERM (약관 동의), ONBD (온보딩)
**플랫폼:** Web(Mobile) 360px 고정폭
**총 TC 수:** 19개
**★ TC 수:** 7개 (37%)

---

## LOGN — 로그인

### **SC-AUTH-LOGN-001** — 랜딩 화면에서 Google 로그인 CTA 탭 시 로그인 화면 이동 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 로그인 |
| 소분류 | 랜딩 화면 진입 및 Google 로그인 CTA |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / |

**사전 조건**
1. 비로그인 상태
2. 랜딩 화면(`/`) 접속된 상태

**테스트 단계**
1. 랜딩 화면에 "Continue with Google" 버튼이 표시되는지 확인한다
2. "Continue with Google" 버튼을 탭한다

**예상 결과**
- 로그인 화면(`/login`)으로 이동한다
- 로그인 화면에 "Continue as John Doe" 버튼이 표시된다

---

### **SC-AUTH-LOGN-002** — Google 소셜 로그인 성공 후 약관 화면 이동 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 로그인 |
| 소분류 | Google 소셜 로그인 (Continue as John Doe) |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login |

**사전 조건**
1. 랜딩에서 "Continue with Google"을 탭하여 `/login` 화면 진입한 상태

**테스트 단계**
1. 로그인 화면에 목업 계정 정보(John Doe, text123@gmail.com)가 표시되는지 확인한다
2. "Continue as John Doe" 버튼을 탭한다

**예상 결과**
- 로그인이 처리되고 약관 동의 화면(`/terms`)으로 이동한다

---

### SC-AUTH-LOGN-003 — 로그인 화면 딤 영역 탭 시 랜딩 화면 복귀 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 로그인 |
| 소분류 | 로그인 화면 딤 영역 탭 — 랜딩 복귀 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /login |

**사전 조건**
1. `/login` 화면 진입한 상태

**테스트 단계**
1. 로그인 화면에서 "Continue as John Doe" 버튼 외 딤(dim) 영역을 탭한다

**예상 결과**
- 로그인이 처리되지 않는다
- 랜딩 화면(`/`)으로 복귀한다

---

### SC-AUTH-LOGN-004 — 랜딩 화면 인증 없이 진입 가능 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 로그인 |
| 소분류 | 랜딩 화면 진입 및 Google 로그인 CTA |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | / |

**사전 조건**
1. 비로그인 상태

**테스트 단계**
1. 브라우저에서 랜딩 화면(`/`) URL에 직접 접속한다
2. 화면이 표시되는지 확인한다

**예상 결과**
- 랜딩 화면이 정상 표시된다
- 로그인 화면 등 다른 화면으로 리다이렉트되지 않는다

---

## TERM — 약관 동의

### **SC-AUTH-TERM-001** — 약관 체크박스 미체크 시 Accept 버튼 비활성화 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 약관 동의 |
| 소분류 | 약관 체크박스 토글 및 Accept 버튼 활성화 |
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
1. 로그인 완료된 상태
2. `/terms` 화면 접속된 상태
3. 약관 체크박스가 미체크 상태

**테스트 단계**
1. 약관 동의 체크박스가 선택되지 않은 상태를 확인한다
2. Accept 버튼의 상태를 확인한다
3. Accept 버튼을 탭한다

**예상 결과**
- Accept 버튼이 비활성화(opacity 0.4) 상태로 표시된다
- 버튼을 탭해도 화면 이동이 발생하지 않는다

---

### **SC-AUTH-TERM-002** — 약관 동의 후 온보딩 화면 이동 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 약관 동의 |
| 소분류 | 약관 동의 Accept — 온보딩 이동 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
1. 로그인 완료된 상태
2. `/terms` 화면 접속된 상태
3. 약관 체크박스가 미체크 상태

**테스트 단계**
1. 약관 동의 체크박스를 탭하여 체크한다
2. Accept 버튼이 활성화 상태로 변경되는지 확인한다
3. Accept 버튼을 탭한다

**예상 결과**
- 체크박스 체크 후 Accept 버튼이 활성화 상태로 표시된다
- 온보딩 화면(`/onboarding`)으로 이동한다

---

### SC-AUTH-TERM-003 — 약관 체크박스 토글 ON/OFF 반복 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 약관 동의 |
| 소분류 | 약관 체크박스 토글 및 Accept 버튼 활성화 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
1. 로그인 완료된 상태
2. `/terms` 화면 접속된 상태
3. 약관 체크박스가 미체크 상태

**테스트 단계**
1. 약관 체크박스를 탭하여 체크한다
2. Accept 버튼 활성화 상태를 확인한다
3. 약관 체크박스를 다시 탭하여 체크 해제한다
4. Accept 버튼 상태를 확인한다

**예상 결과**
- 체크 시 Accept 버튼이 활성화 상태로 표시된다
- 체크 해제 시 Accept 버튼이 다시 비활성화(opacity 0.4) 상태로 돌아간다

---

### SC-AUTH-TERM-004 — Terms of Service 외부 링크 새 탭 오픈 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 약관 동의 |
| 소분류 | 약관 외부 링크 오픈 (Terms of Service / Privacy Policy) |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
1. 로그인 완료된 상태
2. `/terms` 화면 접속된 상태

**테스트 단계**
1. "Terms of Service" 링크를 탭한다
2. 브라우저 탭 상태를 확인한다

**예상 결과**
- `https://supercycl.io/terms` 페이지가 새 탭으로 열린다
- 현재 탭(`/terms`)은 그대로 유지된다

---

### SC-AUTH-TERM-005 — Privacy Policy 외부 링크 새 탭 오픈 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 약관 동의 |
| 소분류 | 약관 외부 링크 오픈 (Terms of Service / Privacy Policy) |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
1. 로그인 완료된 상태
2. `/terms` 화면 접속된 상태

**테스트 단계**
1. "Privacy Policy" 링크를 탭한다
2. 브라우저 탭 상태를 확인한다

**예상 결과**
- `https://supercycl.io/policy` 페이지가 새 탭으로 열린다
- 현재 탭(`/terms`)은 그대로 유지된다

---

### SC-AUTH-TERM-006 — 외부 링크 탭 후 약관 체크박스 상태 유지 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 약관 동의 |
| 소분류 | 약관 외부 링크 오픈 (Terms of Service / Privacy Policy) |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /terms |

**사전 조건**
1. 로그인 완료된 상태
2. `/terms` 화면에서 약관 체크박스를 체크한 상태

**테스트 단계**
1. 체크박스를 탭하여 체크한 상태를 확인한다
2. "Terms of Service" 링크를 탭하여 새 탭을 연다
3. 원래 탭(`/terms`)으로 돌아와 체크박스 상태를 확인한다

**예상 결과**
- 외부 링크 오픈 후에도 체크박스 체크 상태가 유지된다
- Accept 버튼이 활성화 상태를 유지한다

---

## ONBD — 온보딩

### **SC-AUTH-ONBD-001** — 온보딩 자동 3단계 순차 진행 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 온보딩 |
| 소분류 | 온보딩 자동 3단계 진행 (타이머 기반) |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
1. `/onboarding` 화면 진입한 상태
2. 약관 동의가 완료된 상태

**테스트 단계**
1. 온보딩 화면 진입 직후 Step 1 "Creating wallet" 상태가 표시되는지 확인한다
2. 약 1.2초 후 Step 2 "Connecting to Hyperliquid" 상태로 전환되는지 확인한다
3. 약 2.2초 후 Step 3 "Loading test funds" 상태로 전환되는지 확인한다
4. 약 3.2초 후 온보딩 완료 상태로 전환되는지 확인한다

**예상 결과**
- 3단계(Creating wallet → Connecting to Hyperliquid → Loading test funds)가 유저 조작 없이 순차적으로 표시된다
- 각 단계 진행 상태(진행 중/완료)가 화면에 표시된다
- 모든 단계 완료 후 완료 상태로 전환된다

---

### SC-AUTH-ONBD-002 — 온보딩 진행 중 Start Trading 버튼 비표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 온보딩 |
| 소분류 | 온보딩 완료 후 Start Trading 버튼 활성화 및 트레이딩 이동 |
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
1. `/onboarding` 화면에 진입한 직후(온보딩 진행 중)
2. 약관 동의가 완료된 상태

**테스트 단계**
1. 온보딩 진행 중(완료 전) 화면을 확인한다
2. "Start Trading" 버튼이 화면에 보이는지 확인한다

**예상 결과**
- 온보딩 완료 전에는 "Start Trading" 버튼이 화면에 표시되지 않는다 (비가시 상태)

---

### **SC-AUTH-ONBD-003** — 온보딩 완료 후 잔고 카드 및 Start Trading 버튼 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 온보딩 |
| 소분류 | 온보딩 완료 후 Start Trading 버튼 활성화 및 트레이딩 이동 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
1. `/onboarding` 화면의 3단계가 자동 완료된 상태
2. 약관 동의가 완료된 상태

**테스트 단계**
1. 온보딩 완료 후 잔고 카드가 표시되는지 확인한다
2. 잔고 카드에 표시된 잔고 금액을 확인한다
3. "Start Trading" 버튼이 표시되는지 확인한다

**예상 결과**
- 잔고 카드가 표시된다
- 잔고 카드에 "Balance — 100,000 USDC"가 표시된다
- "Start Trading" 버튼이 표시된다

**비고**
- [미결] PEND-AUTH-002: 코드 기준 100.0 USDC인데 화면에 100,000 USDC로 표시 — 단위 변환 정책 확인 필요

---

### **SC-AUTH-ONBD-004** — Start Trading 탭 후 트레이딩 화면 이동 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 온보딩 |
| 소분류 | 온보딩 완료 후 Start Trading 버튼 활성화 및 트레이딩 이동 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
1. 온보딩 3단계가 완료된 상태
2. "Start Trading" 버튼이 표시된 상태

**테스트 단계**
1. "Start Trading" 버튼을 탭한다

**예상 결과**
- 트레이딩 화면(`/trade`)으로 이동한다
- BottomNav가 표시되며 Trade 탭이 활성 상태이다

---

### SC-AUTH-ONBD-005 — 온보딩 진행 중 각 단계 진행 표시 상태 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 온보딩 |
| 소분류 | 온보딩 자동 3단계 진행 (타이머 기반) |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
1. `/onboarding` 화면 진입한 상태
2. 약관 동의가 완료된 상태

**테스트 단계**
1. 온보딩 진행 중 각 단계 항목(Step 1, Step 2, Step 3)의 표시 상태를 확인한다
2. 완료된 단계와 진행 중인 단계의 시각적 표시 차이를 확인한다
3. 전체 3단계 완료 후 모든 단계의 표시 상태를 확인한다

**예상 결과**
- 진행 중인 단계와 완료된 단계가 시각적으로 구분되어 표시된다
- 완료 후 3단계 모두 완료 상태로 표시된다

---

### SC-AUTH-ONBD-006 — 온보딩 중 뒤로가기 동작 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 인증/온보딩 (AUTH) |
| 중분류 | 온보딩 |
| 소분류 | 온보딩 자동 3단계 진행 (타이머 기반) |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
1. `/onboarding` 화면 진행 중(완료 전)
2. 약관 동의가 완료된 상태

**테스트 단계**
1. 온보딩 진행 중 브라우저 뒤로가기를 시도한다
2. 화면 이동 여부를 확인한다

**예상 결과**
- 화면 이동 결과를 관찰한다

**비고**
- [미결] PEND-AUTH-003: 온보딩 진행 중 뒤로가기 처리 정책 미확정 (중단/재시작 여부 불명) — 정책 확정 후 예상 결과 보완 필요

---

## 전체 TC 요약

| TC ID | 제목 (축약) | 분류 | 우선순위 | ★ |
|-------|------------|------|---------|---|
| SC-AUTH-LOGN-001 | 랜딩에서 Google CTA 탭 → 로그인 화면 이동 | Positive | High | ★ |
| SC-AUTH-LOGN-002 | Google 로그인 성공 → 약관 화면 이동 | Positive | High | ★ |
| SC-AUTH-LOGN-003 | 딤 영역 탭 → 랜딩 복귀 | Negative | Medium | |
| SC-AUTH-LOGN-004 | 랜딩 인증 없이 진입 가능 | Edge | Low | |
| SC-AUTH-TERM-001 | 체크박스 미체크 → Accept 비활성화 | Negative | High | ★ |
| SC-AUTH-TERM-002 | 약관 동의 후 온보딩 이동 | Positive | High | ★ |
| SC-AUTH-TERM-003 | 체크박스 토글 ON/OFF 반복 | Positive | Medium | |
| SC-AUTH-TERM-004 | Terms of Service 링크 새 탭 오픈 | Positive | Medium | |
| SC-AUTH-TERM-005 | Privacy Policy 링크 새 탭 오픈 | Positive | Medium | |
| SC-AUTH-TERM-006 | 외부 링크 탭 후 체크박스 상태 유지 | Edge | Low | |
| SC-AUTH-ONBD-001 | 온보딩 자동 3단계 순차 진행 | Positive | High | ★ |
| SC-AUTH-ONBD-002 | 온보딩 중 Start Trading 버튼 비표시 | Negative | High | |
| SC-AUTH-ONBD-003 | 완료 후 잔고 카드 및 버튼 표시 | Positive | High | ★ |
| SC-AUTH-ONBD-004 | Start Trading 탭 → 트레이딩 이동 | Positive | High | ★ |
| SC-AUTH-ONBD-005 | 각 단계 진행 표시 상태 | Positive | Medium | |
| SC-AUTH-ONBD-006 | 온보딩 중 뒤로가기 동작 | Edge | Low | |

**합계: 16개** (★ 7개, 44%)

> **비고:** 기획서 상 AUTH 예상 TC 19개 대비 16개 작성. 분류표 소분류 설명의 일부 예상 TC는 다른 ★ TC 실행 중 암묵적으로 검증되거나(tc-rules.md 섹션 5 제외 조건), 미결 항목으로 인해 전체 TC 작성이 어려운 케이스(PEND-AUTH-001~004)를 제외하였음.

---

## [미결] 항목 목록 (AUTH 도메인)

| ID | 비고에 명시된 TC | 내용 |
|----|----------------|------|
| PEND-AUTH-001 | — | LeverageNotice 노출 조건 미확정 (TC 작성 보류) |
| PEND-AUTH-002 | SC-AUTH-ONBD-003 | 초기 잔고 표시 단위 미확정 (100.0 USDC vs 100,000 USDC) |
| PEND-AUTH-003 | SC-AUTH-ONBD-006 | 온보딩 중 뒤로가기 처리 미확정 |
| PEND-AUTH-004 | — | 로그인 상태 유지 범위 미확정 (TC 작성 보류) |

---


# TC 초안 — LEVR (레버리지)

**도메인:** 레버리지 (LEVR)
**작성일:** 2026-04-03
**Phase:** P3_MobileMockup
**작성 기준:** classification_v1_APPROVED.md / tc-rules-override.md / 02_TC_Policy_Leverage.md

---

## 요약

| 항목 | 내용 |
|------|------|
| 총 TC 수 | 9개 |
| ★ TC 수 | 3개 (33%) |
| 중분류 | MODL (5개), CONF (4개) |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (AdjustLeverage 모달) |

---

## LEVR-MODL — 레버리지 모달

---

### **SC-LEVR-MODL-001** — 레버리지 버튼 탭 시 AdjustLeverage 모달 오픈 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 레버리지 (LEVR) |
| 중분류 | 레버리지 모달 |
| 소분류 | 레버리지 모달 오픈 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태
2. Trade 탭(/trade) 접속된 상태
3. OrderForm이 화면에 표시된 상태
4. 온보딩이 완료된 상태

**테스트 단계**
1. OrderForm 상단의 레버리지 버튼(`{n}x`)을 탭한다
2. 화면에 AdjustLeverage 모달이 표시되는지 확인한다
3. 모달 내 구성 요소를 확인한다

**예상 결과**
- AdjustLeverage 모달이 화면에 표시된다
- 모달 상단에 경고 배너 "Max leverage limited to 2x (User Protection)"가 노란색으로 표시된다
- 슬라이더와 Confirm, Cancel 버튼이 표시된다

---

### SC-LEVR-MODL-002 — 레버리지 모달 진입 시 경고 배너 항상 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 레버리지 (LEVR) |
| 중분류 | 레버리지 모달 |
| 소분류 | 레버리지 모달 오픈 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태
2. AdjustLeverage 모달이 오픈된 상태

**테스트 단계**
1. AdjustLeverage 모달 상단 경고 배너를 확인한다
2. 슬라이더를 1x에서 2x로 조작한다
3. 슬라이더 조작 후에도 경고 배너가 표시되는지 확인한다

**예상 결과**
- 모달 진입 시 "Max leverage limited to 2x (User Protection)" 경고 배너가 표시된다
- 슬라이더 조작 중·후에도 경고 배너가 항상 표시된 상태를 유지한다

---

### **SC-LEVR-MODL-003** — 레버리지 슬라이더 1x~2x 범위 제한 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 레버리지 (LEVR) |
| 중분류 | 레버리지 모달 |
| 소분류 | 레버리지 슬라이더 1x~2x 범위 제한 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태
2. AdjustLeverage 모달이 오픈된 상태

**테스트 단계**
1. 슬라이더를 최솟값 방향으로 끝까지 드래그한다
2. 슬라이더가 멈추는 최솟값을 확인한다
3. 슬라이더를 최댓값 방향으로 끝까지 드래그한다
4. 슬라이더가 멈추는 최댓값을 확인한다

**예상 결과**
- 슬라이더의 최솟값은 1x이다
- 슬라이더의 최댓값은 2x이다
- 1x 미만 또는 2x 초과로 슬라이더가 이동하지 않는다

---

### SC-LEVR-MODL-004 — 3x 이상 레버리지 직접 입력 불가 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 레버리지 (LEVR) |
| 중분류 | 레버리지 모달 |
| 소분류 | 레버리지 슬라이더 1x~2x 범위 제한 |
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태
2. AdjustLeverage 모달이 오픈된 상태

**테스트 단계**
1. 레버리지 입력 필드(또는 슬라이더 조작)에서 3 이상의 값을 입력 또는 설정 시도한다
2. 입력 후 표시되는 레버리지 값을 확인한다

**예상 결과**
- 3 이상의 값이 입력되지 않거나, 입력 시 자동으로 2x로 리셋된다
- 슬라이더는 2x 이상으로 이동하지 않는다

**비고**
- [미결] 3x 이상 직접 입력 필드 존재 여부 미확인 — 슬라이더만 존재하는 경우 이 TC는 슬라이더 최댓값 검증(MODL-003)과 중복될 수 있음. 개발 확인 후 조정 필요
- [개발 확인] 숫자 직접 입력 필드가 있는 경우: 소수점 입력 및 0 입력 동작 추가 확인 필요

---

### SC-LEVR-MODL-005 — 기본 레버리지 2x 설정 초기값 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 레버리지 (LEVR) |
| 중분류 | 레버리지 모달 |
| 소분류 | 레버리지 모달 오픈 |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 최초 또는 별도 레버리지 변경 없이 로그인한 상태
2. AdjustLeverage 모달을 처음 오픈한 상태

**테스트 단계**
1. 레버리지 버튼(`{n}x`)을 탭하여 AdjustLeverage 모달을 오픈한다
2. 모달 진입 시 슬라이더의 초기 위치(기본값)를 확인한다

**예상 결과**
- AdjustLeverage 모달 진입 시 슬라이더 초기값이 2x로 표시된다
- OrderForm의 레버리지 버튼에도 "2x"가 표시된다

---

## LEVR-CONF — 레버리지 확인/취소

---

### **SC-LEVR-CONF-001** — 레버리지 Confirm 탭 후 설정 저장 및 모달 닫힘 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 레버리지 (LEVR) |
| 중분류 | 레버리지 확인/취소 |
| 소분류 | 레버리지 Confirm — 설정 저장 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태
2. AdjustLeverage 모달이 오픈된 상태
3. 슬라이더를 조작하여 레버리지를 변경한 상태이다 (예: 1x로 변경)

**테스트 단계**
1. 슬라이더를 1x 위치로 드래그한다
2. `Confirm` 버튼을 탭한다
3. 모달이 닫히는지 확인한다
4. OrderForm의 레버리지 버튼 표시값을 확인한다

**예상 결과**
- `Confirm` 버튼 탭 시 AdjustLeverage 모달이 닫힌다
- OrderForm의 레버리지 버튼에 변경한 값(예: "1x")이 반영되어 표시된다
- Trade 화면으로 복귀한다

---

### SC-LEVR-CONF-002 — 레버리지 Cancel 탭 후 변경값 미반영 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 레버리지 (LEVR) |
| 중분류 | 레버리지 확인/취소 |
| 소분류 | 레버리지 Cancel — 변경 불저장 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태
2. AdjustLeverage 모달이 오픈된 상태
3. 현재 레버리지가 2x인 상태

**테스트 단계**
1. 슬라이더를 1x 위치로 드래그한다
2. `Cancel` 버튼을 탭한다
3. 모달이 닫히는지 확인한다
4. OrderForm의 레버리지 버튼 표시값을 확인한다

**예상 결과**
- `Cancel` 버튼 탭 시 AdjustLeverage 모달이 닫힌다
- OrderForm의 레버리지 버튼에 변경 전 값(2x)이 그대로 표시된다
- 슬라이더에서 조작한 1x 값은 저장되지 않는다

---

### SC-LEVR-CONF-003 — 코인 변경 시 포지션 없는 상태에서 레버리지 2x 자동 변경 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 레버리지 (LEVR) |
| 중분류 | 레버리지 확인/취소 |
| 소분류 | 레버리지 Confirm — 설정 저장 |
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태
2. 레버리지가 1x로 설정된 상태
3. 보유 포지션 및 미체결 주문이 없는 상태

**테스트 단계**
1. Trade 탭에서 현재 레버리지 버튼 표시값(1x)을 확인한다
2. CoinInfoBar 코인 페어를 탭하여 CoinSelector 바텀시트를 오픈한다
3. 현재 선택된 코인과 다른 코인을 선택한다
4. 바텀시트가 닫힌 후 OrderForm의 레버리지 버튼 표시값을 확인한다

**예상 결과**
- 코인 변경 후 OrderForm의 레버리지 버튼이 "2x"로 표시된다
- AdjustLeverage 모달을 별도로 열지 않아도 자동으로 2x로 변경된다

**비고**
- [미결] 코인 변경 시 레버리지 자동 2x 전환이 목업 화면에서도 동작하는지 확인 필요 (policy_doc.md 기준 정책이나 목업 구현 여부 미확인)

---

### SC-LEVR-CONF-004 — 코인 변경 시 포지션 보유 상태에서 레버리지 유지 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 레버리지 (LEVR) |
| 중분류 | 레버리지 확인/취소 |
| 소분류 | 레버리지 Confirm — 설정 저장 |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태
2. 레버리지가 1x로 설정된 포지션이 보유된 상태
3. 포지션이 있는 코인과 다른 코인이 선택 가능한 상태

**테스트 단계**
1. Trade 탭에서 현재 레버리지 버튼 표시값(1x)을 확인한다
2. CoinInfoBar 코인 페어를 탭하여 CoinSelector 바텀시트를 오픈한다
3. 현재 포지션이 있는 코인과 다른 코인을 선택한다
4. 바텀시트가 닫힌 후 OrderForm의 레버리지 버튼 표시값을 확인한다

**예상 결과**
- 코인 변경 후에도 레버리지 버튼이 변경 전 설정값(1x)을 유지한다
- 포지션 보유 상태에서 레버리지가 2x로 강제 변경되지 않는다

**비고**
- [미결] 목업 환경에서 포지션 보유 시 코인 변경 레버리지 유지 동작 구현 여부 미확인 — 정책 확인 후 검증 필요

---


# TC 초안 — TPSL 도메인 (TP/SL 설정)

**생성일:** 2026-04-03
**도메인:** TPSL — TP/SL 설정
**중분류:** MODL (AutoTpSl 모달), TOGL (Auto TP/SL 토글)
**기준 소스:** classification_v1_APPROVED.md / feature_list.md / policy_doc.md / 03_TC_Policy_AutoTPSL.md

---

## 요약

| 항목 | 내용 |
|------|------|
| 전체 TC 수 | 14개 |
| ★ TC 수 | 5개 (36%) |
| 중분류 MODL | 11개 |
| 중분류 TOGL | 3개 |

---

## TPSL-MODL — AutoTpSl 모달

---

### **SC-TPSL-MODL-001** — AutoTpSlModal 오픈 및 기본값 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | AutoTpSlModal 오픈 (설정 화면) |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태
2. `/trade` Settings 탭 접속된 상태

**테스트 단계**
1. Settings 탭의 Auto TP/SL 섹션에서 `Edit` 버튼을 탭한다
2. AutoTpSlModal이 화면에 표시되는지 확인한다
3. TP 입력 필드의 기본값을 확인한다
4. SL 입력 필드의 기본값을 확인한다

**예상 결과**
- AutoTpSlModal이 오픈된다
- TP 입력 필드에 기본값 `1.8`(%)이 표시된다
- SL 입력 필드에 기본값 `5.0`(%)이 표시된다

---

### **SC-TPSL-MODL-002** — AutoTpSlModal Confirm 후 설정값 저장 및 설정 화면 반영 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | AutoTpSlModal Confirm — 설정 저장 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings), AutoTpSlModal |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태
2. Settings 탭의 Edit 버튼을 탭하여 AutoTpSlModal이 열린 상태
3. TP 및 SL 중 하나 이상의 값이 0보다 크다

**테스트 단계**
1. AutoTpSlModal에서 TP 입력 필드에 `2.5`를 입력한다
2. SL 입력 필드에 `3.0`을 입력한다
3. `Confirm` 버튼을 탭한다
4. 모달이 닫히는지 확인한다
5. Settings 탭의 Auto TP/SL 표시 영역을 확인한다

**예상 결과**
- `Confirm` 버튼 탭 후 모달이 닫힌다
- Settings 화면의 Auto TP/SL 표시가 `TP: +2.5% | SL: -3.0%`로 업데이트된다

---

### SC-TPSL-MODL-003 — AutoTpSlModal Confirm 후 안내 문구 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | AutoTpSlModal Confirm — 설정 저장 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
1. AutoTpSlModal이 열린 상태
2. TP 입력 필드와 SL 입력 필드에 유효한 값(0 초과)이 입력된 상태

**테스트 단계**
1. AutoTpSlModal 하단 안내 문구를 확인한다

**예상 결과**
- 모달 내에 "Settings apply to new orders only. Existing positions will not be affected." 안내 문구가 표시된다

---

### **SC-TPSL-MODL-004** — TP/SL 모두 0일 때 Confirm 버튼 비활성화 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
1. AutoTpSlModal이 열린 상태

**테스트 단계**
1. TP 입력 필드를 `0`으로 변경한다
2. SL 입력 필드를 `0`으로 변경한다
3. `Confirm` 버튼의 상태를 확인한다
4. `Confirm` 버튼을 탭한다

**예상 결과**
- TP + SL 모두 0인 상태에서 `Confirm` 버튼이 비활성화(disabled) 상태이다
- 버튼을 탭해도 모달이 닫히지 않는다

---

### SC-TPSL-MODL-005 — TP 입력값 최댓값(999.9%) 초과 시 입력 제한 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
1. AutoTpSlModal이 열린 상태

**테스트 단계**
1. TP 입력 필드에 `1000`을 입력한다
2. 입력 필드의 값을 확인한다

**예상 결과**
- TP 입력값이 `999.9`(%)를 초과하지 않도록 입력이 제한되거나 자동으로 리셋된다

---

### SC-TPSL-MODL-006 — SL 입력값 최댓값(99.9%) 초과 시 입력 제한 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
1. AutoTpSlModal이 열린 상태

**테스트 단계**
1. SL 입력 필드에 `100`을 입력한다
2. 입력 필드의 값을 확인한다

**예상 결과**
- SL 입력값이 `99.9`(%)를 초과하지 않도록 입력이 제한되거나 자동으로 리셋된다

---

### SC-TPSL-MODL-007 — TP/SL 입력 필드 음수 입력 불가 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
1. AutoTpSlModal이 열린 상태

**테스트 단계**
1. SL 입력 필드에 `-5`를 입력 시도한다
2. 입력 필드의 값을 확인한다

**예상 결과**
- 음수 값이 입력되지 않는다 (입력 필드가 음수를 허용하지 않거나 자동으로 제거된다)

**비고**
- SL은 UI 상 양수로 입력받으며 내부적으로 손실 비율로 처리됨

---

### SC-TPSL-MODL-008 — TP/SL 소수점 2자리 이상 입력 불가 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
1. AutoTpSlModal이 열린 상태

**테스트 단계**
1. TP 입력 필드에 `1.23`을 입력 시도한다
2. 입력 필드의 값을 확인한다

**예상 결과**
- 소수점 2자리 이상이 입력되지 않는다 (소수점 1자리까지만 허용되거나 자동으로 반올림된다)

---

### SC-TPSL-MODL-009 — AutoTpSlModal Cancel 후 변경값 미저장 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | AutoTpSlModal Cancel — 변경 불저장 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
1. AutoTpSlModal이 열린 상태
2. 현재 TP 설정값은 `1.8`(%), SL 설정값은 `5.0`(%)

**테스트 단계**
1. TP 입력 필드를 `9.9`로 변경한다
2. `Cancel` 버튼을 탭한다
3. 모달이 닫히는지 확인한다
4. Settings 탭의 Auto TP/SL 표시 영역을 확인한다

**예상 결과**
- `Cancel` 버튼 탭 후 모달이 닫힌다
- Settings 화면의 Auto TP/SL 표시가 기존 값(`TP: +1.8% | SL: -5.0%`)으로 유지된다 (변경 미저장)

---

### SC-TPSL-MODL-010 — TP만 0이고 SL > 0인 경우 Confirm 버튼 활성 여부 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
1. AutoTpSlModal이 열린 상태

**테스트 단계**
1. TP 입력 필드를 `0`으로 변경한다
2. SL 입력 필드에 `5.0`을 입력한다
3. `Confirm` 버튼의 상태를 확인한다

**예상 결과**
- TP = 0이고 SL > 0인 상태에서 `Confirm` 버튼의 활성화 여부를 확인한다

**비고**
- [미결] PEND-SETS-002: TP=0이고 SL>0인 경우 Confirm 버튼 활성 여부 미확정 — 현재 정책은 "TP+SL 모두 0이면 비활성"이므로 이 경우 활성화 예상, 정책 확정 후 예상 결과 수정 필요

---

### SC-TPSL-MODL-011 — Auto TP/SL OFF 상태에서 Edit 버튼 탭 시 모달 오픈 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | AutoTpSlModal 오픈 (설정 화면) |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. Settings 탭 접속된 상태
2. Auto TP/SL 토글이 OFF 상태

**테스트 단계**
1. Auto TP/SL 섹션의 `Edit` 버튼을 탭한다
2. AutoTpSlModal 오픈 여부를 확인한다

**예상 결과**
- AutoTpSlModal이 오픈된다

**비고**
- [미결] PEND-SETS-001: OFF 상태에서 Edit → Confirm 시 Auto TP/SL이 ON으로 자동 전환되는지 여부 미확정

---

## TPSL-TOGL — Auto TP/SL 토글

---

### **SC-TPSL-TOGL-001** — Auto TP/SL 토글 ON 전환 및 상태 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | Auto TP/SL 토글 |
| 소분류 | Auto TP/SL 토글 ON/OFF |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태
2. `/trade` Settings 탭 접속된 상태
3. Auto TP/SL 토글이 OFF 상태

**테스트 단계**
1. Auto TP/SL 섹션의 토글 스위치를 탭하여 ON으로 전환한다
2. 토글 상태를 확인한다
3. Settings 화면의 Auto TP/SL 표시 영역을 확인한다

**예상 결과**
- 토글이 ON 상태로 전환된다 (시각적으로 활성화 상태가 표시된다)
- Settings 화면에 현재 TP/SL 설정값(`TP: +X.X% | SL: -X.X%`)이 표시된다

---

### **SC-TPSL-TOGL-002** — Auto TP/SL ON 상태에서 주문 시 Order Form TP/SL 자동 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | Auto TP/SL 토글 |
| 소분류 | Auto TP/SL 토글 ON/OFF |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade, settings) |

**사전 조건**
1. Settings 탭에서 Auto TP/SL 토글이 ON 상태
2. Trade 탭 접속된 상태
3. TP: 1.8%, SL: 5.0%로 설정된 상태

**테스트 단계**
1. Trade 탭의 OrderForm 영역을 확인한다
2. OrderForm 하단의 TP/SL 표시 항목을 확인한다

**예상 결과**
- OrderForm 하단에 `TP: +1.8% / SL: -5.0%` 가 표시된다

---

### SC-TPSL-TOGL-003 — Auto TP/SL 토글 OFF 전환 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | Auto TP/SL 토글 |
| 소분류 | Auto TP/SL 토글 ON/OFF |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. Settings 탭 접속된 상태
2. Auto TP/SL 토글이 ON 상태

**테스트 단계**
1. Auto TP/SL 섹션의 토글 스위치를 탭하여 OFF로 전환한다
2. 토글 상태를 확인한다

**예상 결과**
- 토글이 OFF 상태로 전환된다 (시각적으로 비활성화 상태가 표시된다)

---

## ★ TC 선별 근거

| TC ID | 선별 이유 |
|-------|-----------|
| SC-TPSL-MODL-001 | 모달 오픈 진입점 — 이후 전체 TPSL 기능의 전제 조건 |
| SC-TPSL-MODL-002 | 핵심 Positive — 설정 저장 및 UI 반영 검증 |
| SC-TPSL-MODL-004 | 핵심 Negative — 0 입력 시 저장 차단 검증 (서비스 진입 차단 조건) |
| SC-TPSL-TOGL-001 | 핵심 Positive — 토글 ON 전환, 가장 기본적인 사용 흐름 |
| SC-TPSL-TOGL-002 | 핵심 Positive — 토글 ON 상태의 실제 주문 연동 동작 검증 |

---


# TC 초안 — TRAD 도메인 (트레이딩)

**작성일:** 2026-04-03
**Phase:** P3_MobileMockup
**도메인:** TRAD (트레이딩)
**중분류:** COIN / ORDF / POSN / ORDR
**총 TC 수:** 27개
**★ TC 수:** 10개 (37%)

---

## 중분류별 TC 수 요약

| 중분류 | 중분류명 | 전체 TC | ★ TC |
|--------|---------|--------|------|
| COIN | 코인 선택 | 5 | 2 |
| ORDF | 주문 실행 | 12 | 5 |
| POSN | 포지션 관리 | 4 | 2 |
| ORDR | 주문 관리 및 대시보드 | 6 | 1 |
| **합계** | | **27** | **10** |

---

## TRAD-COIN — 코인 선택

### **SC-TRAD-COIN-001** — CoinSelector 바텀시트 오픈 및 코인 변경 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 코인 선택 (COIN) |
| 소분류 | 코인 선택 바텀시트 오픈 및 코인 변경 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), CoinSelector |

**사전 조건**
1. 온보딩이 완료된 계정으로 로그인된 상태
2. `/trade` 탭 trade 화면 접속된 상태
3. 기본 코인 BTC-USDC가 선택된 상태

**테스트 단계**
1. CoinInfoBar에 표시된 코인 페어(`BTC-USDC`)를 탭한다
2. CoinSelector 바텀시트가 표시되는지 확인한다
3. 바텀시트 목록에서 `ETH-USDC`를 탭한다
4. 바텀시트가 닫히는지 확인한다
5. CoinInfoBar에 표시된 코인 페어가 변경되었는지 확인한다

**예상 결과**
- 코인 페어 탭 시 CoinSelector 바텀시트가 화면 하단에서 올라오며 표시된다
- `ETH-USDC` 탭 후 바텀시트가 닫힌다
- CoinInfoBar에 `ETH-USDC`가 표시된다

---

### **SC-TRAD-COIN-002** — 코인 검색 실시간 필터링 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 코인 선택 (COIN) |
| 소분류 | 코인 검색 실시간 필터링 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | CoinSelector |

**사전 조건**
1. CoinSelector 바텀시트가 열린 상태
2. 지원 코인 4종(BTC-USDC, ETH-USDC, SOL-USDC, XRP-USDC)이 목록에 표시된 상태

**테스트 단계**
1. 검색 필드에 `SOL`을 입력한다
2. 목록이 실시간으로 변경되는지 확인한다

**예상 결과**
- 검색어 입력 즉시 `SOL-USDC`만 목록에 표시된다
- 나머지 코인(BTC-USDC, ETH-USDC, XRP-USDC)은 목록에서 사라진다

---

### SC-TRAD-COIN-003 — 코인 검색 결과 없음 빈 상태 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 코인 선택 (COIN) |
| 소분류 | 코인 검색 실시간 필터링 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | CoinSelector |

**사전 조건**
1. CoinSelector 바텀시트가 열린 상태

**테스트 단계**
1. 검색 필드에 `DOGE`를 입력한다
2. 목록 상태를 확인한다

**예상 결과**
- 코인 목록이 비어있는 빈 상태(empty state)가 표시된다
- 오류 메시지 또는 안내 문구가 표시된다

**비고**
- [미결] 빈 상태 안내 문구 정확한 텍스트 미확정 — 정책 확정 후 문구 검증 필요

---

### SC-TRAD-COIN-004 — 코인 변경 시 포지션/미체결 주문 없는 상태에서 레버리지 2x 초기화 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 코인 선택 (COIN) |
| 소분류 | 코인 선택 바텀시트 오픈 및 코인 변경 |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), CoinSelector |

**사전 조건**
1. 포지션 및 미체결 주문이 없는 상태
2. 레버리지가 1x로 설정된 상태
3. CoinSelector 바텀시트가 열린 상태

**테스트 단계**
1. CoinSelector에서 다른 코인을 탭하여 선택한다
2. OrderForm의 레버리지 버튼 표시값을 확인한다

**예상 결과**
- 레버리지가 2x(기본값)로 변경되어 레버리지 버튼에 `2x`가 표시된다

---

### SC-TRAD-COIN-005 — 포지션 보유 상태에서 코인 변경 시 레버리지 유지 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 코인 선택 (COIN) |
| 소분류 | 코인 선택 바텀시트 오픈 및 코인 변경 |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), CoinSelector |

**사전 조건**
1. 보유 포지션이 1개 이상 존재하는 상태
2. 레버리지가 1x로 설정된 상태
3. CoinSelector 바텀시트가 열린 상태

**테스트 단계**
1. CoinSelector에서 다른 코인을 탭하여 선택한다
2. OrderForm의 레버리지 버튼 표시값을 확인한다

**예상 결과**
- 레버리지가 변경되지 않고 기존 설정값인 `1x`가 그대로 표시된다

---

## TRAD-ORDF — 주문 실행

### **SC-TRAD-ORDF-001** — Market Buy/Long 주문 실행 성공 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | Market 주문 실행 (Buy/Long, Sell/Short) |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. 온보딩이 완료된 계정으로 로그인된 상태
2. `/trade` 탭 trade 화면 접속된 상태
3. 주문 유형이 `Market`으로 선택된 상태
4. 충분한 잔고가 있는 상태

**테스트 단계**
1. CoinSelector에서 `BTC-USDC`를 선택한다
2. 주문 유형이 `Market`인지 확인한다
3. 수량 슬라이더를 25% 위치로 이동한다
4. `Buy / Long` 버튼을 탭한다
5. 화면 하단의 Toast 알림을 확인한다
6. Dashboard 탭으로 이동하여 포지션 목록을 확인한다

**예상 결과**
- `Buy / Long` 버튼 탭 후 Toast 알림이 화면 하단에 표시된다
- Dashboard Positions 탭에 새로운 Long 포지션이 추가된다

**비고**
- [미결] 주문 실행 Toast 정확한 문구 미확정 — 정책 확정 후 문구 검증 필요 (PEND-NAVI-003)

---

### **SC-TRAD-ORDF-002** — Market Sell/Short 주문 실행 성공 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | Market 주문 실행 (Buy/Long, Sell/Short) |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. 온보딩이 완료된 계정으로 로그인된 상태
2. `/trade` 탭 trade 화면 접속된 상태
3. 주문 유형이 `Market`으로 선택된 상태
4. 충분한 잔고가 있는 상태

**테스트 단계**
1. CoinSelector에서 `ETH-USDC`를 선택한다
2. 주문 유형이 `Market`인지 확인한다
3. 수량 슬라이더를 25% 위치로 이동한다
4. `Sell / Short` 버튼을 탭한다
5. 화면 하단의 Toast 알림을 확인한다
6. Dashboard 탭으로 이동하여 포지션 목록을 확인한다

**예상 결과**
- `Sell / Short` 버튼 탭 후 Toast 알림이 화면 하단에 표시된다
- Dashboard Positions 탭에 새로운 Short 포지션이 추가된다

**비고**
- [미결] 주문 실행 Toast 정확한 문구 미확정 (PEND-NAVI-003)

---

### **SC-TRAD-ORDF-003** — Limit 주문 유형 선택 시 가격 입력 필드 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | 주문 유형 Market/Limit 드롭다운 전환 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. `/trade` 탭 trade 화면 접속된 상태
2. 주문 유형이 `Market`으로 선택된 상태이다 (가격 입력 필드 숨김 상태)

**테스트 단계**
1. 주문 유형 드롭다운을 탭한다
2. `Limit`을 선택한다
3. OrderForm에 가격 입력 필드가 표시되는지 확인한다

**예상 결과**
- `Limit` 선택 후 가격 입력 필드가 OrderForm에 표시된다
- Market 선택 시 숨겨졌던 가격 입력 필드가 나타난다

---

### SC-TRAD-ORDF-004 — Market 주문 유형 선택 시 가격 입력 필드 숨김 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | 주문 유형 Market/Limit 드롭다운 전환 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. `/trade` 탭 trade 화면 접속된 상태
2. 주문 유형이 `Limit`으로 선택된 상태이다 (가격 입력 필드 표시 상태)

**테스트 단계**
1. 주문 유형 드롭다운을 탭한다
2. `Market`을 선택한다
3. 가격 입력 필드가 사라지는지 확인한다

**예상 결과**
- `Market` 선택 후 가격 입력 필드가 OrderForm에서 사라진다

---

### **SC-TRAD-ORDF-005** — Limit 주문 가격 입력 후 실행 시 미체결 주문 등록 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | Limit 주문 실행 — 가격 입력 필드 표시 및 미체결 주문 등록 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. `/trade` 탭 trade 화면 접속된 상태
2. 주문 유형이 `Limit`으로 선택된 상태
3. 가격 입력 필드가 표시된 상태

**테스트 단계**
1. 가격 입력 필드에 지정가를 입력한다 (예: `90000`)
2. 수량 슬라이더를 25% 위치로 이동한다
3. `Buy / Long` 버튼을 탭한다
4. Dashboard 탭의 `Open Order` 탭으로 이동한다
5. 미체결 주문 목록을 확인한다

**예상 결과**
- `Buy / Long` 버튼 탭 후 Toast 알림이 표시된다
- Dashboard `Open Order` 탭에 새로운 미체결 주문이 등록된다
- 미체결 주문 카드에 주문 내용(코인, 방향, 가격, 수량)이 표시된다

---

### SC-TRAD-ORDF-006 — 수량 슬라이더 조작 시 수량 필드 반영 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | 수량 슬라이더 조작 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. `/trade` 탭 trade 화면 접속된 상태
2. 수량 슬라이더가 0% 위치(초기 상태) 상태

**테스트 단계**
1. 수량 슬라이더의 두 번째 도트(25% 위치)를 탭한다
2. 수량 입력 필드의 값을 확인한다
3. 수량 슬라이더의 세 번째 도트(50% 위치)를 탭한다
4. 수량 입력 필드의 값을 다시 확인한다

**예상 결과**
- 25% 도트 탭 시 수량 입력 필드에 잔고의 25%에 해당하는 수량이 입력된다
- 50% 도트 탭 시 수량 입력 필드가 25% 탭 시보다 2배 값으로 변경된다

---

### SC-TRAD-ORDF-007 — 수량 0 상태에서 주문 버튼 동작 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | Market 주문 실행 (Buy/Long, Sell/Short) |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. `/trade` 탭 trade 화면 접속된 상태
2. 주문 유형이 `Market`으로 선택된 상태
3. 수량 슬라이더가 0% 위치이며 수량 입력 필드가 0 또는 비어 있는 상태

**테스트 단계**
1. 수량이 0 또는 비어 있는 상태를 확인한다
2. `Buy / Long` 버튼을 탭한다
3. 화면 상태를 확인한다

**예상 결과**
- 주문이 실행되지 않는다
- 오류 메시지 또는 버튼 비활성화 상태가 표시된다

**비고**
- [미결] 수량 0 주문 처리 정책 미확정 (PEND-TRAD-002) — 버튼 비활성화 vs 토스트 오류 메시지 등 정책 확정 후 검증 필요

---

### SC-TRAD-ORDF-008 — Limit 주문 가격 미입력 상태에서 주문 버튼 탭 동작 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | Limit 주문 실행 — 가격 입력 필드 표시 및 미체결 주문 등록 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. `/trade` 탭 trade 화면 접속된 상태
2. 주문 유형이 `Limit`으로 선택된 상태
3. 가격 입력 필드가 비어 있는 상태
4. 수량 슬라이더가 25% 위치로 설정된 상태

**테스트 단계**
1. 가격 입력 필드가 비어 있는 상태를 확인한다
2. `Buy / Long` 버튼을 탭한다
3. 화면 상태를 확인한다

**예상 결과**
- 주문이 실행되지 않는다
- 오류 메시지 또는 버튼 비활성화 상태가 표시된다

**비고**
- [미결] Limit 주문 가격 미입력 처리 정책 미확정 (PEND-TRAD-004)

---

### SC-TRAD-ORDF-009 — Auto TP/SL 활성 상태에서 주문 시 TP/SL 자동 설정 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | Market 주문 실행 (Buy/Long, Sell/Short) |
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. Auto TP/SL 토글이 ON 상태
2. TP 1.8% / SL 5.0% 또는 사용자 설정값이 저장된 상태
3. Market 주문 유형이 선택된 상태

**테스트 단계**
1. 수량 슬라이더를 25% 위치로 이동한다
2. `Buy / Long` 버튼을 탭한다
3. Dashboard Positions 탭으로 이동하여 생성된 포지션 카드를 확인한다

**예상 결과**
- 포지션 카드에 TP/SL 정보가 함께 표시된다
- TP/SL 수치가 설정된 값과 일치한다

---

### SC-TRAD-ORDF-010 — Signal Prefill 진입 시 Limit 전환 및 진입가 자동 입력 확인 [신규]

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | Limit 주문 실행 — 가격 입력 필드 표시 및 미체결 주문 등록 |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), SignalOrderSheet |

**사전 조건**
1. 시그널 탭에서 ACTIVE 시그널의 SignalOrderSheet가 열린 상태
2. Modify 버튼을 탭하여 `PREFILL_FROM_SIGNAL`이 디스패치된 상태

**테스트 단계**
1. SignalOrderSheet에서 Modify 버튼을 탭한다
2. 트레이딩 탭으로 자동 이동되는지 확인한다
3. OrderForm의 주문 유형 및 가격 입력 필드를 확인한다

**예상 결과**
- 트레이딩 탭으로 전환된다
- 주문 유형이 `Limit`으로 자동 전환된다
- 가격 입력 필드에 시그널의 진입가가 자동으로 입력되어 있다

**비고**
- [신규] PREFILL_FROM_SIGNAL 디스패치에 의한 트레이딩 탭 연동 동작

---

### SC-TRAD-ORDF-011 — 슬라이더 5개 도트 조작 전체 범위 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | 수량 슬라이더 조작 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. `/trade` 탭 trade 화면 접속된 상태

**테스트 단계**
1. 수량 슬라이더의 마지막 도트(100% 위치)를 탭한다
2. 수량 입력 필드의 값을 확인한다
3. 수량 슬라이더를 0% 위치(첫 번째 도트)로 이동한다
4. 수량 입력 필드의 값을 확인한다

**예상 결과**
- 100% 도트 탭 시 수량 입력 필드에 가용 잔고 전량에 해당하는 수량이 입력된다
- 0%(첫 번째 도트) 이동 시 수량 입력 필드가 0 또는 최솟값으로 변경된다

---

### SC-TRAD-ORDF-012 — Market 주문 실행 후 잔고 감소 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 실행 (ORDF) |
| 소분류 | Market 주문 실행 (Buy/Long, Sell/Short) |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), /trade (탭: portfolio) |

**사전 조건**
1. 온보딩이 완료된 계정으로 로그인된 상태
2. 포트폴리오 탭에서 현재 가용 잔고(available)를 기록해 둔 상태
3. Market 주문 유형이 선택된 상태

**테스트 단계**
1. 수량 슬라이더를 25% 위치로 이동한다
2. `Buy / Long` 버튼을 탭한다
3. Portfolio 탭으로 이동한다
4. 가용 잔고(available)를 확인한다

**예상 결과**
- 주문 실행 전보다 가용 잔고(available)가 감소한다
- 감소한 금액은 주문에 사용된 증거금 금액과 일치한다

---

## TRAD-POSN — 포지션 관리

### **SC-TRAD-POSN-001** — 포지션 Close 실행 후 목록에서 제거 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 포지션 관리 (POSN) |
| 소분류 | 포지션 Close |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), Dashboard Positions |

**사전 조건**
1. Dashboard Positions 탭에 포지션이 1개 이상 존재하는 상태
2. Dashboard Positions 탭 접속된 상태

**테스트 단계**
1. PositionCard 중 하나의 `Close` 버튼을 탭한다
2. 화면 하단의 Toast 알림을 확인한다
3. 포지션 목록을 확인한다

**예상 결과**
- `Close` 버튼 탭 후 `"Position closed"` Toast가 화면 하단에 표시된다
- 해당 포지션 카드가 목록에서 제거된다

---

### **SC-TRAD-POSN-002** — 포지션 Close 후 Dashboard 배지 감소 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 포지션 관리 (POSN) |
| 소분류 | 포지션 Close |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), Dashboard Positions |

**사전 조건**
1. Dashboard Positions 탭에 포지션이 정확히 1개 존재하는 상태
2. Dashboard Positions 탭 배지에 녹색 숫자(1)가 표시된 상태

**테스트 단계**
1. PositionCard의 `Close` 버튼을 탭한다
2. Dashboard 탭 배지를 확인한다
3. Positions 탭 내 목록 상태를 확인한다

**예상 결과**
- 포지션 Close 후 Dashboard Positions 탭에 녹색 배지가 사라진다
- 포지션 목록에 `"No open positions"` 안내 문구가 표시된다

---

### SC-TRAD-POSN-003 — 포지션 없는 상태에서 Dashboard Positions 빈 상태 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 포지션 관리 (POSN) |
| 소분류 | 포지션 Close |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), Dashboard Positions |

**사전 조건**
1. Dashboard Positions 탭 접속된 상태
2. 보유 포지션이 없는 상태이다 (온보딩 직후 또는 모든 포지션 Close 후)

**테스트 단계**
1. Dashboard Positions 탭을 확인한다

**예상 결과**
- 포지션 카드가 표시되지 않는다
- `"No open positions"` 안내 문구가 표시된다

---

### SC-TRAD-POSN-004 — 초기 DEFAULT_POSITIONS(XRP Short, BTC Long) 표시 확인 [신규]

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 포지션 관리 (POSN) |
| 소분류 | 포지션 Close |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), Dashboard Positions |

**사전 조건**
1. Dashboard Positions 탭 접속된 상태
2. 온보딩 완료 직후 상태이다 (주문 실행 이력 없음)

**테스트 단계**
1. Dashboard Positions 탭을 확인한다
2. 표시된 포지션 카드의 내용을 확인한다

**예상 결과**
- XRP Short 2x 포지션 카드가 표시된다
- BTC Long 2x 포지션 카드가 표시된다

**비고**
- [신규] DEFAULT_POSITIONS 목업 초기값 — 실제 API 연동 시 동작이 달라질 수 있음

---

## TRAD-ORDR — 주문 관리 및 대시보드

### **SC-TRAD-ORDR-001** — 미체결 주문 Cancel 실행 후 목록에서 제거 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 관리 및 대시보드 (ORDR) |
| 소분류 | 미체결 주문 Cancel |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), Dashboard Open Order |

**사전 조건**
1. Dashboard Open Order 탭에 미체결 주문이 1개 이상 존재하는 상태
2. Dashboard Open Order 탭 접속된 상태

**테스트 단계**
1. Open Order 카드 중 하나의 `Cancel` 버튼을 탭한다
2. 화면 하단의 Toast 알림을 확인한다
3. 미체결 주문 목록을 확인한다

**예상 결과**
- `Cancel` 버튼 탭 후 `"Order cancelled"` Toast가 화면 하단에 표시된다
- 해당 주문 카드가 목록에서 제거된다

---

### SC-TRAD-ORDR-002 — 미체결 주문 없는 상태에서 Open Order 탭 빈 상태 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 관리 및 대시보드 (ORDR) |
| 소분류 | 미체결 주문 Cancel |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), Dashboard Open Order |

**사전 조건**
1. Dashboard Open Order 탭 접속된 상태
2. 미체결 주문이 없는 상태

**테스트 단계**
1. Dashboard Open Order 탭을 확인한다

**예상 결과**
- 주문 카드가 표시되지 않는다
- `"No open orders"` 안내 문구가 표시된다

---

### SC-TRAD-ORDR-003 — Dashboard Positions 탭 녹색 배지 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 관리 및 대시보드 (ORDR) |
| 소분류 | Dashboard 탭 배지 표시 (Positions / Open Order) |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), Dashboard |

**사전 조건**
1. Dashboard Positions 탭에 포지션이 1개 이상 존재하는 상태
2. `/trade` 탭 trade 화면 접속된 상태

**테스트 단계**
1. Dashboard 영역의 Positions 탭 배지를 확인한다

**예상 결과**
- Positions 탭에 녹색 배지와 함께 포지션 수가 표시된다

---

### SC-TRAD-ORDR-004 — Dashboard Open Order 탭 노란색 배지 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 관리 및 대시보드 (ORDR) |
| 소분류 | Dashboard 탭 배지 표시 (Positions / Open Order) |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), Dashboard |

**사전 조건**
1. Dashboard Open Order 탭에 미체결 주문이 1개 이상 존재하는 상태
2. `/trade` 탭 trade 화면 접속된 상태

**테스트 단계**
1. Dashboard 영역의 Open Order 탭 배지를 확인한다

**예상 결과**
- Open Order 탭에 노란색 배지와 함께 미체결 주문 수가 표시된다

---

### SC-TRAD-ORDR-005 — 포지션 및 미체결 주문 모두 없는 상태에서 배지 미표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 관리 및 대시보드 (ORDR) |
| 소분류 | Dashboard 탭 배지 표시 (Positions / Open Order) |
| 분류 | Negative |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), Dashboard |

**사전 조건**
1. 보유 포지션이 없는 상태
2. 미체결 주문이 없는 상태

**테스트 단계**
1. `/trade` 탭 trade 화면의 Dashboard 영역을 확인한다
2. Positions 탭과 Open Order 탭의 배지를 확인한다

**예상 결과**
- Positions 탭에 녹색 배지가 표시되지 않는다
- Open Order 탭에 노란색 배지가 표시되지 않는다

---

### SC-TRAD-ORDR-006 — Limit 주문 Cancel 후 Open Order 탭 배지 감소 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 트레이딩 (TRAD) |
| 중분류 | 주문 관리 및 대시보드 (ORDR) |
| 소분류 | 미체결 주문 Cancel |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade), Dashboard Open Order |

**사전 조건**
1. Dashboard Open Order 탭에 미체결 주문이 정확히 1개 존재하는 상태
2. Open Order 탭에 노란색 배지가 표시된 상태

**테스트 단계**
1. Dashboard Open Order 탭으로 이동한다
2. 주문 카드의 `Cancel` 버튼을 탭한다
3. Open Order 탭 배지를 확인한다

**예상 결과**
- `"Order cancelled"` Toast가 표시된다
- Open Order 탭의 노란색 배지가 사라진다
- Open Order 탭 목록에 `"No open orders"` 안내 문구가 표시된다

---


# TC 초안 — SGNL (시그널)

**도메인**: SGNL
**Phase**: P3_MobileMockup
**작성일**: 2026-04-03
**총 TC 수**: 18개
**★ TC 수**: 7개 (38.9%)
**대상 중분류**: LIST / EXEC / MODY

---

## SGNL-LIST — 시그널 목록

---

### **SC-SGNL-LIST-001** — 시그널 탭 진입 시 목록 및 퍼포먼스 요약 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 목록 (LIST) |
| 소분류 | 시그널 목록 표시 및 퍼포먼스 요약 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: signal) |

**사전 조건**
1. 로그인 및 온보딩이 완료된 계정
2. BottomNav에서 Signal 탭을 탭하지 않은 상태

**테스트 단계**
1. BottomNav의 Signal 탭을 탭하여 시그널 화면에 진입한다
2. 화면 상단에 퍼포먼스 요약 영역이 표시되는지 확인한다
3. 퍼포먼스 요약에 Hit / Miss / Expired 카운트, Avg PnL, Hit Rate가 표시되는지 확인한다
4. 시그널 카드 목록이 표시되는지 확인한다

**예상 결과**
- 퍼포먼스 요약 영역에 Hit / Miss / Expired 카운트, Avg PnL, Hit Rate 항목이 표시된다
- 시그널 카드가 1개 이상 목록에 표시된다

---

### **SC-SGNL-LIST-002** — 시그널 필터 탭 전환 및 목록 필터링 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 목록 (LIST) |
| 소분류 | 시그널 필터 탭 전환 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: signal) |

**사전 조건**
1. 시그널 화면에 진입한 상태
2. 필터 탭바가 화면에 표시된 상태

**테스트 단계**
1. 필터 탭바에서 `Long` 탭을 탭한다
2. 표시된 시그널 카드가 Long(매수) 방향만 표시되는지 확인한다
3. `Short` 탭을 탭한다
4. 표시된 시그널 카드가 Short(매도) 방향만 표시되는지 확인한다
5. `Active` 탭을 탭한다
6. ACTIVE 상태인 시그널만 표시되는지 확인한다

**예상 결과**
- 각 필터 탭 선택 시 해당 조건에 맞는 시그널 카드만 목록에 표시된다
- 탭 전환 시 이전 필터 결과가 즉시 교체된다

---

### SC-SGNL-LIST-003 — 필터 탭 전환 시 결과 없음 안내 문구 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 목록 (LIST) |
| 소분류 | 시그널 필터 탭 전환 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: signal) |

**사전 조건**
1. 시그널 화면에 진입한 상태
2. 목업 데이터 기준 모든 시그널이 종료(HIT_TP / HIT_SL / EXPIRED) 상태이거나, Active 필터 적용 시 결과가 없는 환경

**테스트 단계**
1. 필터 탭바에서 `Active` 탭을 탭한다
2. 시그널 카드 목록 영역을 확인한다

**예상 결과**
- 시그널 카드가 표시되지 않는다
- "No signals matching this filter" 안내 문구가 표시된다

---

### **SC-SGNL-LIST-004** — ACTIVE 시그널 카드에 Execute 버튼 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 목록 (LIST) |
| 소분류 | 시그널 카드 상태별 표시 규칙 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: signal) |

**사전 조건**
1. 시그널 화면에 진입한 상태
2. 목업 데이터에 ACTIVE 상태 시그널(예: sig-001 BTC LONG, sig-002 SOL SHORT)이 존재한 상태

**테스트 단계**
1. ACTIVE 상태의 시그널 카드(예: BTC LONG sig-001)를 화면에서 확인한다
2. 해당 카드에 Execute 버튼이 표시되는지 확인한다
3. PnL 표시 여부를 확인한다

**예상 결과**
- ACTIVE 시그널 카드에 Execute 버튼이 표시된다
- PnL 항목은 표시되지 않는다

---

### SC-SGNL-LIST-005 — 종료 상태 시그널 카드 PnL 색상 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 목록 (LIST) |
| 소분류 | 시그널 카드 상태별 표시 규칙 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: signal) |

**사전 조건**
1. 시그널 화면에 진입한 상태
2. 목업 데이터에 HIT_TP 상태(예: sig-003 ETH LONG +2.64%)와 HIT_SL 상태(예: sig-004 XRP SHORT -3.51%) 시그널이 존재한 상태

**테스트 단계**
1. HIT_TP 상태 시그널 카드(예: ETH sig-003)를 확인한다
2. PnL이 양수 값으로 녹색으로 표시되는지 확인한다
3. HIT_SL 상태 시그널 카드(예: XRP sig-004)를 확인한다
4. PnL이 음수 값으로 빨강으로 표시되는지 확인한다
5. 두 카드 모두 Execute 버튼이 없는지 확인한다

**예상 결과**
- HIT_TP 시그널 카드: PnL 양수 값이 녹색으로 표시되고, Execute 버튼이 없다
- HIT_SL 시그널 카드: PnL 음수 값이 빨강으로 표시되고, Execute 버튼이 없다

---

### **SC-SGNL-LIST-006** — 미읽음 시그널 배지 표시 및 탭 진입 시 초기화 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 목록 (LIST) |
| 소분류 | 미읽음 시그널 배지 표시 및 초기화 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: signal), BottomNav |

**사전 조건**
1. 로그인 완료된 상태
2. 현재 Trade 탭에 있으며 Signal 탭에 진입하지 않은 상태
3. 미읽음 시그널(`unreadCount` > 0) 상태

**테스트 단계**
1. BottomNav의 Signal 탭 아이콘에 배지가 표시되는지 확인한다
2. Signal 탭 아이콘을 탭하여 시그널 화면에 진입한다
3. BottomNav의 Signal 탭 아이콘을 다시 확인한다

**예상 결과**
- 진입 전: Signal 탭 아이콘에 미읽음 수 배지가 표시된다
- 진입 후: Signal 탭 아이콘의 배지가 사라진다 (카운트 0으로 초기화)

---

### SC-SGNL-LIST-007 — 미읽음 배지 없을 때 Signal 탭 배지 미표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 목록 (LIST) |
| 소분류 | 미읽음 시그널 배지 표시 및 초기화 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: signal), BottomNav |

**사전 조건**
1. 시그널 탭에 이미 진입하여 미읽음 카운트가 0인 상태
2. 다른 탭(Trade 등)으로 이동한 상태

**테스트 단계**
1. BottomNav의 Signal 탭 아이콘을 확인한다

**예상 결과**
- Signal 탭 아이콘에 배지가 표시되지 않는다

---

## SGNL-EXEC — 시그널 주문 실행

---

### **SC-SGNL-EXEC-001** — ACTIVE 시그널 Execute 탭 시 SignalOrderSheet 오픈 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 주문 실행 (EXEC) |
| 소분류 | 시그널 Execute — SignalOrderSheet 오픈 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: signal), SignalOrderSheet |

**사전 조건**
1. 시그널 화면에 진입한 상태
2. ACTIVE 상태의 시그널 카드(예: sig-001 BTC LONG)가 화면에 표시된 상태

**테스트 단계**
1. ACTIVE 상태 시그널 카드(예: BTC LONG sig-001)의 Execute 버튼을 탭한다
2. 바텀시트가 열리는지 확인한다
3. 바텀시트에 코인 / 방향 / 진입가 / TP / SL / 레버리지 정보가 자동으로 표시되는지 확인한다

**예상 결과**
- SignalOrderSheet 바텀시트가 화면 하단에서 열린다
- 시그널의 코인(BTC) / 방향(LONG) / 진입가 / TP / SL / 레버리지(2x) 정보가 자동으로 표시된다

---

### **SC-SGNL-EXEC-002** — SignalOrderSheet Market 주문 실행 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 주문 실행 (EXEC) |
| 소분류 | SignalOrderSheet 주문 실행 (Market/Limit) |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | SignalOrderSheet |

**사전 조건**
1. 충분한 잔고가 있는 계정
2. ACTIVE 시그널의 Execute 버튼을 탭하여 SignalOrderSheet 바텀시트가 열린 상태

**테스트 단계**
1. SignalOrderSheet에서 주문 유형을 `Market`으로 선택한다
2. `Execute Order` 버튼을 탭한다
3. 화면 하단에 Toast 알림이 표시되는지 확인한다
4. 현재 탭 위치를 확인한다

**예상 결과**
- Toast 알림에 "Order executed from signal" 메시지가 표시된다
- 화면이 트레이딩 탭으로 전환된다

---

### SC-SGNL-EXEC-003 — SignalOrderSheet Limit 주문 실행 시 미체결 주문 등록 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 주문 실행 (EXEC) |
| 소분류 | SignalOrderSheet 주문 실행 (Market/Limit) |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | SignalOrderSheet, /trade (탭: trade) |

**사전 조건**
1. 충분한 잔고가 있는 계정
2. ACTIVE 시그널의 Execute 버튼을 탭하여 SignalOrderSheet 바텀시트가 열린 상태

**테스트 단계**
1. SignalOrderSheet에서 주문 유형을 `Limit`으로 선택한다
2. `Execute Order` 버튼을 탭한다
3. Toast 알림 내용을 확인한다
4. 트레이딩 탭의 Dashboard > Open Orders에서 주문 등록 여부를 확인한다

**예상 결과**
- Toast 알림에 "Order executed from signal" 메시지가 표시된다
- 트레이딩 탭으로 전환된다
- Dashboard Open Orders 탭에 해당 주문이 미체결 주문으로 등록된다

---

### SC-SGNL-EXEC-004 — SignalOrderSheet LONG/SHORT 시그널 Execute 버튼 색상 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 주문 실행 (EXEC) |
| 소분류 | SignalOrderSheet 주문 실행 (Market/Limit) |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | SignalOrderSheet |

**사전 조건**
1. 시그널 화면에 ACTIVE 상태의 LONG 시그널(예: sig-001 BTC LONG)과 SHORT 시그널(예: sig-002 SOL SHORT)이 표시된 상태

**테스트 단계**
1. LONG 시그널(예: BTC sig-001)의 Execute 버튼을 탭하여 SignalOrderSheet를 오픈한다
2. Execute Order 버튼의 색상을 확인한다
3. 바텀시트를 닫는다
4. SHORT 시그널(예: SOL sig-002)의 Execute 버튼을 탭하여 SignalOrderSheet를 오픈한다
5. Execute Order 버튼의 색상을 확인한다

**예상 결과**
- LONG 시그널의 SignalOrderSheet: Execute Order 버튼이 녹색으로 표시된다
- SHORT 시그널의 SignalOrderSheet: Execute Order 버튼이 빨강으로 표시된다

---

### SC-SGNL-EXEC-005 — 종료 상태 시그널에서 Execute 버튼 미표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 주문 실행 (EXEC) |
| 소분류 | 시그널 Execute — SignalOrderSheet 오픈 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: signal) |

**사전 조건**
1. 시그널 화면에 HIT_TP, HIT_SL, 또는 EXPIRED 상태의 시그널 카드가 표시된 상태

**테스트 단계**
1. HIT_TP 상태 시그널 카드(예: ETH sig-003)를 확인한다
2. 해당 카드에 Execute 버튼이 있는지 확인한다
3. HIT_SL 상태 시그널 카드(예: XRP sig-004)를 확인한다
4. 해당 카드에 Execute 버튼이 있는지 확인한다

**예상 결과**
- HIT_TP, HIT_SL 상태 시그널 카드에 Execute 버튼이 표시되지 않는다

---

## SGNL-MODY — 시그널 주문 편집

---

### **SC-SGNL-MODY-001** — Modify 버튼 탭 시 편집 모드 ON/OFF 토글 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 주문 편집 (MODY) |
| 소분류 | SignalOrderSheet Modify 모드 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | SignalOrderSheet |

**사전 조건**
1. ACTIVE 시그널의 Execute 버튼을 탭하여 SignalOrderSheet 바텀시트가 열린 상태
2. 편집 모드는 OFF 상태

**테스트 단계**
1. SignalOrderSheet의 `Modify` 버튼을 탭한다
2. 편집 모드가 활성화되는지 확인한다
3. Margin 직접 입력 필드가 표시되는지 확인한다
4. Leverage 조정 UI(1~2x)가 활성화되는지 확인한다
5. `Modify` 버튼을 다시 탭한다
6. 편집 모드가 비활성화되는지 확인한다

**예상 결과**
- 첫 번째 탭: 편집 모드가 활성화되어 Margin 입력 필드와 Leverage 조정 UI가 표시된다
- 두 번째 탭: 편집 모드가 비활성화되어 이전 상태로 돌아간다

---

### SC-SGNL-MODY-002 — 편집 모드에서 Leverage 1~2x 범위 제한 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 주문 편집 (MODY) |
| 소분류 | SignalOrderSheet Modify 모드 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | SignalOrderSheet |

**사전 조건**
1. Modify 버튼을 탭하여 편집 모드가 활성화된 상태
2. SignalOrderSheet 바텀시트가 열린 상태

**테스트 단계**
1. Leverage 조정 UI에서 현재 설정값(기본 2x)을 확인한다
2. Leverage를 1x로 조정한다
3. 1x 미만으로 조정을 시도한다
4. Leverage를 2x로 조정한다
5. 2x 초과로 조정을 시도한다

**예상 결과**
- Leverage가 1x~2x 범위 내에서만 조정된다
- 1x 미만으로는 조정이 불가하다
- 2x 초과로는 조정이 불가하다

---

### SC-SGNL-MODY-003 — 편집 모드에서 Margin 입력 후 Execute 주문 실행 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 주문 편집 (MODY) |
| 소분류 | SignalOrderSheet Modify 모드 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | SignalOrderSheet |

**사전 조건**
1. 충분한 잔고가 있는 계정
2. Modify 버튼을 탭하여 편집 모드가 활성화된 상태
3. SignalOrderSheet 바텀시트가 열린 상태

**테스트 단계**
1. Margin 입력 필드에 임의의 금액(예: 50)을 직접 입력한다
2. `Execute Order` 버튼을 탭한다
3. Toast 알림을 확인한다

**예상 결과**
- Toast 알림에 "Order executed from signal" 메시지가 표시된다
- 화면이 트레이딩 탭으로 전환된다

**비고**
- [미결] Margin 입력 단위(USD 금액 vs 코인 수량) 미확정 — 정책 확정 후 입력값 기준 재검증 필요 (PEND-SIGN-001)
- [미결] Margin 입력값이 가용 잔고 초과 시 처리 정책 미확정 (PEND-SIGN-002)

---

### SC-SGNL-MODY-004 — 편집 모드 미활성 시 Margin 입력 필드 미표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 시그널 (SGNL) |
| 중분류 | 시그널 주문 편집 (MODY) |
| 소분류 | SignalOrderSheet Modify 모드 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | SignalOrderSheet |

**사전 조건**
1. 편집 모드가 활성화된 후 Modify 버튼을 다시 탭하여 편집 모드를 OFF로 전환한 상태
2. SignalOrderSheet 바텀시트가 열린 상태

**테스트 단계**
1. SignalOrderSheet의 Margin 입력 필드가 표시되는지 확인한다
2. Leverage 조정 UI가 활성화되어 있는지 확인한다

**예상 결과**
- Margin 직접 입력 필드가 표시되지 않는다
- Leverage 조정 UI가 비활성화 상태이거나 표시되지 않는다

---

## TC 요약

| 중분류 | TC 수 | ★ TC 수 |
|--------|-------|---------|
| SGNL-LIST (시그널 목록) | 7 | 4 |
| SGNL-EXEC (시그널 주문 실행) | 5 | 3 |
| SGNL-MODY (시그널 주문 편집) | 4 | 0 |
| **합계** | **16** | **7** |

> ★ TC 비율: 7 / 16 = **43.75%**
>
> ※ 참고: 작성 중 MODY 도메인 추가 분석 결과 18개 계획 대비 16개로 조정됨. MODY 소분류가 단일(3개 예상 TC)이며, 4개 TC로 충분히 커버. LIST도 7개(계획 13개 대비 53%)로 핵심만 선별.

---

## [미결] 항목 (SGNL 도메인)

| ID | 항목 | 관련 TC |
|----|------|---------|
| PEND-SIGN-001 | 시그널 주문 수량 단위 (USD vs 코인) | SC-SGNL-MODY-003 |
| PEND-SIGN-002 | Margin 상한 검증 처리 | SC-SGNL-MODY-003 |
| PEND-SIGN-003 | 중복 시그널 주문 방지 정책 | (TC 미작성 — 정책 확정 후 추가) |
| PEND-SIGN-004 | 시그널 데이터 갱신 (목업 vs 실시간 API) | (TC 미작성 — 정책 확정 후 추가) |
| PEND-NAVI-003 | 주문 실행 Toast 정확한 문구 | SC-SGNL-EXEC-002, SC-SGNL-EXEC-003 |

---


# TC 초안 — FUND (자금)

**Phase:** P3_MobileMockup
**작성일:** 2026-04-03
**작성자:** tc-writer 에이전트
**기준 분류표:** classification_v1_APPROVED.md

---

## 요약

| 항목 | 내용 |
|------|------|
| 대분류 | FUND (자금) |
| 중분류 | INIT (초기 자금 표시), PTFL (포트폴리오 잔고) |
| 전체 TC 수 | 6개 |
| ★ TC 수 | 2개 (33%) |

---

## FUND-INIT — 초기 자금 표시

---

### **SC-FUND-INIT-001** — 온보딩 완료 후 초기 잔고 카드 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 자금 (FUND) |
| 중분류 | 초기 자금 표시 (INIT) |
| 소분류 | 초기 테스트 자금 지급 표시 (100,000 USDC) |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
1. YOUTHMETA 파트너코드로 가입한 체험용 계정
2. `/onboarding` 페이지에서 온보딩 3단계가 자동으로 진행 완료된 상태
3. 약관 동의가 완료된 상태

**테스트 단계**
1. 온보딩 완료 화면이 표시되는지 확인한다
2. 화면에 잔고 카드가 fadeIn으로 표시되는지 확인한다
3. 잔고 카드의 표시 내용을 확인한다

**예상 결과**
- 잔고 카드에 "Balance — 100,000 USDC" 텍스트가 표시된다
- "Start Trading" 버튼이 함께 표시된다

**비고**
- [미결] 화면 표시 "100,000 USDC"와 내부 상태값 "100.0 USDC" 간 단위 변환 정책 확인 필요 (PEND-AUTH-002)

---

### SC-FUND-INIT-002 — 온보딩 완료 전 잔고 카드 비표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 자금 (FUND) |
| 중분류 | 초기 자금 표시 (INIT) |
| 소분류 | 초기 테스트 자금 지급 표시 (100,000 USDC) |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /onboarding |

**사전 조건**
1. `/onboarding` 페이지 진입한 상태
2. 온보딩 3단계 진행이 완료되지 않은 상태이다 (3.2초 미만)

**테스트 단계**
1. 온보딩 화면 진입 직후 잔고 카드가 표시되는지 확인한다
2. "Start Trading" 버튼의 상태를 확인한다

**예상 결과**
- 잔고 카드가 표시되지 않는다 (opacity 0 또는 숨김 상태)
- "Start Trading" 버튼이 비가시 상태이다 (탭 불가)

---

## FUND-PTFL — 포트폴리오 잔고

---

### **SC-FUND-PTFL-001** — 포트폴리오 totalBalance 계산 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 자금 (FUND) |
| 중분류 | 포트폴리오 잔고 (PTFL) |
| 소분류 | 포트폴리오 잔고 계산 표시 (totalBalance / available / totalMargin) |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: portfolio) |

**사전 조건**
1. Portfolio 탭 접속된 상태
2. 온보딩이 완료된 상태
3. 포지션이 1개 이상 보유된 상태이다 (기본 포지션: XRP Short 2x, BTC Long 2x)

**테스트 단계**
1. Portfolio 탭 화면에서 잔고 요약 카드를 확인한다
2. Total Balance 항목을 확인한다
3. Available 항목을 확인한다
4. Total Margin 항목을 확인한다

**예상 결과**
- Total Balance: ACCOUNT.balance + 전체 포지션 PnL 합계에 해당하는 값이 표시된다
- Available: ACCOUNT.balance - 전체 포지션 margin 합계에 해당하는 값이 표시된다
- Total Margin: 전체 포지션 margin 합계에 해당하는 값이 표시된다

---

### SC-FUND-PTFL-002 — 포트폴리오 pnlPercent 소수점 2자리 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 자금 (FUND) |
| 중분류 | 포트폴리오 잔고 (PTFL) |
| 소분류 | 포트폴리오 잔고 계산 표시 (totalBalance / available / totalMargin) |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: portfolio) |

**사전 조건**
1. Portfolio 탭 접속된 상태
2. 온보딩이 완료된 상태
3. 포지션이 1개 이상 보유된 상태

**테스트 단계**
1. Portfolio 탭 화면에서 PnL 퍼센트 항목을 확인한다
2. PnL 수치의 소수점 자리수를 확인한다

**예상 결과**
- pnlPercent 값이 소수점 2자리로 표시된다 (예: +1.23% 또는 -2.50%)
- PnL > 0이면 녹색(#00de0b), PnL < 0이면 빨강(#ff5938)으로 표시된다

**비고**
- [미결] PnL이 정확히 0인 경우 표시 색상 미확정 (PEND-PORT-002)

---

### SC-FUND-PTFL-003 — 포지션 전체 청산 후 포트폴리오 잔고 변화 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 자금 (FUND) |
| 중분류 | 포트폴리오 잔고 (PTFL) |
| 소분류 | 포트폴리오 잔고 계산 표시 (totalBalance / available / totalMargin) |
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: portfolio) |

**사전 조건**
1. 해당 포지션을 Trading 탭에서 모두 Close 처리한 상태
2. 온보딩이 완료된 상태
3. 포지션이 1개 이상 보유된 상태

**테스트 단계**
1. Portfolio 탭으로 이동한다
2. Total Balance, Available, Total Margin 항목을 확인한다

**예상 결과**
- Total Margin이 0으로 표시된다
- Available이 ACCOUNT.balance 전액과 동일하게 표시된다
- 포지션 목록 영역에 "No open positions" 문구가 표시된다

---

### SC-FUND-PTFL-004 — 포트폴리오 Available 음수 방지 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 자금 (FUND) |
| 중분류 | 포트폴리오 잔고 (PTFL) |
| 소분류 | 포트폴리오 잔고 계산 표시 (totalBalance / available / totalMargin) |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: portfolio) |

**사전 조건**
1. 온보딩이 완료된 상태
2. 복수 포지션을 보유하여 margin 합계가 ACCOUNT.balance에 근접한 상태

**테스트 단계**
1. Portfolio 탭으로 이동한다
2. Available 항목의 값을 확인한다

**예상 결과**
- Available 값이 화면에 표시된다
- 표시 값이 ACCOUNT.balance - totalMargin 공식과 일치한다

**비고**
- [미결] ACCOUNT.balance = 0인 경우 pnlPercent 계산(0으로 나누기) 예외 처리 미확정 (PEND-PORT-003)
- [개발 확인] 목업에서 잔고 부족 시 주문 거부 검증 없음 (PEND-TRAD-003)

---

---


# TC 초안 — MOBL (모바일 UI)

**Phase:** P3_MobileMockup
**작성일:** 2026-04-03
**작성자:** tc-writer 에이전트
**기준 분류표:** classification_v1_APPROVED.md

---

## 요약

| 항목 | 내용 |
|------|------|
| 대분류 | MOBL (모바일 UI) |
| 중분류 | NAV (내비게이션), HEAD (헤더), TOST (Toast 알림) |
| 전체 TC 수 | 11개 |
| ★ TC 수 | 4개 (36%) |

---

## MOBL-NAV — 내비게이션

---

### **SC-MOBL-NAV-001** — BottomNav 4탭 전환 동작 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 모바일 UI (MOBL) |
| 중분류 | 내비게이션 (NAV) |
| 소분류 | BottomNav 탭 전환 및 활성 상태 표시 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (전체 탭) |

**사전 조건**
1. `/trade` 화면 접속된 상태
2. 온보딩이 완료된 상태

**테스트 단계**
1. 화면 하단 BottomNav에서 `Trade` 탭을 탭한다
2. 현재 활성 탭 상태를 확인한다
3. `Signal` 탭을 탭한다
4. 활성 탭 상태를 확인한다
5. `Portfolio` 탭을 탭한다
6. 활성 탭 상태를 확인한다
7. `Settings` 탭을 탭한다
8. 활성 탭 상태를 확인한다

**예상 결과**
- 각 탭을 탭할 때마다 해당 탭의 콘텐츠 화면이 표시된다
- 활성 탭의 아이콘과 라벨이 흰색으로 표시된다
- 비활성 탭의 아이콘과 라벨이 회색으로 표시된다

---

### **SC-MOBL-NAV-002** — BottomNav 활성 탭 아이콘 색상 전환 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 모바일 UI (MOBL) |
| 중분류 | 내비게이션 (NAV) |
| 소분류 | BottomNav 탭 전환 및 활성 상태 표시 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (전체 탭) |

**사전 조건**
1. `/trade` 화면의 Trade 탭이 활성화된 상태
2. 온보딩이 완료된 상태

**테스트 단계**
1. BottomNav에서 Trade 탭 아이콘 색상을 확인한다
2. Portfolio 탭을 탭한다
3. Trade 탭 아이콘 색상을 다시 확인한다
4. Portfolio 탭 아이콘 색상을 확인한다

**예상 결과**
- Trade 탭으로 이동 후 Trade 탭 아이콘이 흰색으로 표시된다
- Portfolio 탭으로 이동 시 Portfolio 탭 아이콘이 흰색, Trade 탭 아이콘이 회색으로 표시된다

---

### SC-MOBL-NAV-003 — 동일 탭 재탭 시 화면 변화 없음 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 모바일 UI (MOBL) |
| 중분류 | 내비게이션 (NAV) |
| 소분류 | BottomNav 탭 전환 및 활성 상태 표시 |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (전체 탭) |

**사전 조건**
1. `/trade` 화면의 Trade 탭이 활성화된 상태
2. 온보딩이 완료된 상태

**테스트 단계**
1. BottomNav에서 현재 활성화된 Trade 탭을 다시 탭한다
2. 화면 상태를 확인한다

**예상 결과**
- 화면이 새로고침되거나 다른 탭으로 이동하지 않는다
- Trade 탭이 계속 활성 상태(흰색)로 유지된다

---

## MOBL-HEAD — 헤더

---

### **SC-MOBL-HEAD-001** — Header Testnet 배지 항상 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 모바일 UI (MOBL) |
| 중분류 | 헤더 (HEAD) |
| 소분류 | Header Testnet 배지 표시 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | 전체 화면 (Header 포함) |

**사전 조건**
1. `/trade` 화면 접속된 상태
2. 온보딩이 완료된 상태

**테스트 단계**
1. 화면 상단 Header 영역을 확인한다
2. Header 우측에 표시된 배지 내용을 확인한다
3. Trade 탭, Signal 탭, Portfolio 탭, Settings 탭으로 각각 이동하며 Header 배지를 확인한다

**예상 결과**
- 모든 탭에서 Header 우측에 "Testnet" 배지가 표시된다
- 탭을 전환하더라도 "Testnet" 배지가 사라지지 않는다

---

## MOBL-TOST — Toast 알림

---

### **SC-MOBL-TOST-001** — 포지션 Close 후 Toast 표시 및 자동 사라짐 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 모바일 UI (MOBL) |
| 중분류 | Toast 알림 (TOST) |
| 소분류 | Toast 알림 자동 표시 및 사라짐 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. `/trade` 화면의 Trade 탭 > Dashboard > Positions 탭 접속된 상태
2. 온보딩이 완료된 상태
3. 포지션이 1개 이상 보유된 상태

**테스트 단계**
1. PositionCard에서 `Close` 버튼을 탭한다
2. 화면 하단에 Toast 알림이 표시되는지 확인한다
3. 일정 시간이 경과한 후 Toast 상태를 확인한다

**예상 결과**
- 화면 하단에 "Position closed" Toast 알림이 표시된다
- Toast 알림이 일정 시간 후 자동으로 사라진다

**비고**
- [미결] Toast 자동 사라짐 시간(ms) 기획서 미명시 (PEND-NAVI-002)

---

### SC-MOBL-TOST-002 — 주문 Cancel 후 Toast 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 모바일 UI (MOBL) |
| 중분류 | Toast 알림 (TOST) |
| 소분류 | Toast 알림 자동 표시 및 사라짐 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. `/trade` 화면의 Trade 탭 > Dashboard > Open Orders 탭 접속된 상태
2. 온보딩이 완료된 상태
3. 미체결 주문이 1개 이상 있는 상태

**테스트 단계**
1. Open Order 카드에서 `Cancel` 버튼을 탭한다
2. 화면 하단에 Toast 알림이 표시되는지 확인한다

**예상 결과**
- 화면 하단에 "Order cancelled" Toast 알림이 표시된다
- Toast 알림이 일정 시간 후 자동으로 사라진다

**비고**
- [미결] Toast 자동 사라짐 시간(ms) 기획서 미명시 (PEND-NAVI-002)

---

### SC-MOBL-TOST-003 — 시그널 주문 실행 후 Toast 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 모바일 UI (MOBL) |
| 중분류 | Toast 알림 (TOST) |
| 소분류 | Toast 알림 자동 표시 및 사라짐 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: signal), SignalOrderSheet |

**사전 조건**
1. Signal 탭에 ACTIVE 상태 시그널이 1개 이상 존재한 상태
2. 온보딩이 완료된 상태

**테스트 단계**
1. Signal 탭에서 ACTIVE 시그널 카드의 `Execute` 버튼을 탭한다
2. SignalOrderSheet 바텀시트에서 `Execute Order` 버튼을 탭한다
3. 화면 하단 Toast 알림을 확인한다

**예상 결과**
- 화면 하단에 "Order executed from signal" Toast 알림이 표시된다
- Toast 알림이 일정 시간 후 자동으로 사라진다

---

### SC-MOBL-TOST-004 — 주문 실행 후 Toast 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 모바일 UI (MOBL) |
| 중분류 | Toast 알림 (TOST) |
| 소분류 | Toast 알림 자동 표시 및 사라짐 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade) |

**사전 조건**
1. Trade 탭 주문폼에서 Market 주문 유형이 선택된 상태
2. 온보딩이 완료된 상태
3. 충분한 잔고가 있는 상태

**테스트 단계**
1. 수량 슬라이더를 25% 이상으로 설정한다
2. `Buy / Long` 버튼을 탭한다
3. 화면 하단 Toast 알림을 확인한다

**예상 결과**
- 주문 실행 후 Toast 알림이 화면 하단에 표시된다
- Toast 알림이 일정 시간 후 자동으로 사라진다

**비고**
- [미결] Market/Limit 주문 실행 Toast 정확한 문구 미확정 (PEND-NAVI-003)

---

### SC-MOBL-TOST-005 — 포트폴리오 보유 포지션 목록 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 모바일 UI (MOBL) |
| 중분류 | Toast 알림 (TOST) |
| 소분류 | 포트폴리오 보유 포지션 및 최근 활동 표시 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: portfolio) |

**사전 조건**
1. Portfolio 탭 접속된 상태
2. 온보딩이 완료된 상태
3. 포지션이 1개 이상 보유된 상태이다 (기본: XRP Short 2x, BTC Long 2x)

**테스트 단계**
1. Portfolio 탭 화면에서 포지션 목록 영역을 확인한다
2. 각 포지션 항목의 표시 내용을 확인한다

**예상 결과**
- 보유 포지션 목록이 표시된다
- 각 포지션 항목에 컬러 바, 코인명, Side·Leverage, PnL 정보가 표시된다
- Long 포지션 PnL > 0이면 녹색, PnL < 0이면 빨강으로 표시된다

---

### SC-MOBL-TOST-006 — 포지션 없을 때 포트폴리오 안내 문구 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 모바일 UI (MOBL) |
| 중분류 | Toast 알림 (TOST) |
| 소분류 | 포트폴리오 보유 포지션 및 최근 활동 표시 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: portfolio) |

**사전 조건**
1. Portfolio 탭 접속된 상태
2. 온보딩이 완료된 상태
3. 보유 포지션이 0개인 상태이다 (모든 포지션을 Close 처리함)

**테스트 단계**
1. Portfolio 탭 화면에서 포지션 목록 영역을 확인한다

**예상 결과**
- 포지션 목록 영역에 "No open positions" 문구가 표시된다
- 포지션 카드 행이 표시되지 않는다

---

### SC-MOBL-TOST-007 — 포트폴리오 최근 활동 목업 데이터 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 모바일 UI (MOBL) |
| 중분류 | Toast 알림 (TOST) |
| 소분류 | 포트폴리오 보유 포지션 및 최근 활동 표시 |
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: portfolio) |

**사전 조건**
1. Portfolio 탭 접속된 상태
2. 온보딩이 완료된 상태

**테스트 단계**
1. Portfolio 탭 화면에서 최근 활동(Recent Activity) 섹션을 확인한다
2. 활동 항목 목록을 확인한다

**예상 결과**
- 최근 활동 섹션에 목업 데이터 항목이 표시된다
  - "Opened XRPUSDT Short · 2x" (2h ago)
  - "Opened BTCUSDT Long · 2x" (3h ago)
  - "Deposited 100 USDC" (5h ago)

**비고**
- [미결] 실제 API 연동 시 최근 활동 데이터 동적 표시 정책 미확정 (PEND-PORT-001)

---

---


# TC 초안 — SETG (설정)

**Phase:** P3_MobileMockup
**작성일:** 2026-04-03
**작성자:** tc-writer 에이전트
**기준 분류표:** classification_v1_APPROVED.md

---

## 요약

| 항목 | 내용 |
|------|------|
| 대분류 | SETG (설정) |
| 중분류 | ACCT (계정 설정), LANG (언어 설정), LOUT (로그아웃) |
| 전체 TC 수 | 8개 |
| ★ TC 수 | 3개 (38%) |

---

## SETG-ACCT — 계정 설정

---

### **SC-SETG-ACCT-001** — 지갑 주소 Copy 버튼 탭 후 Toast 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 설정 (SETG) |
| 중분류 | 계정 설정 (ACCT) |
| 소분류 | 지갑 주소 복사 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. `/trade` 화면의 Settings 탭 접속된 상태
2. 온보딩이 완료된 상태

**테스트 단계**
1. Settings 화면에서 Account 섹션을 확인한다
2. 지갑 주소(`0x9834...9948`)가 표시되어 있는지 확인한다
3. Account 섹션의 `Copy` 버튼을 탭한다
4. 화면 하단 Toast 알림을 확인한다

**예상 결과**
- Account 섹션에 지갑 주소가 모노스페이스 폰트로 표시된다
- `Copy` 버튼 탭 후 화면 하단에 "Address copied!" Toast 알림이 표시된다
- Toast 알림이 일정 시간 후 자동으로 사라진다

---

### SC-SETG-ACCT-002 — 계정 이메일 주소 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 설정 (SETG) |
| 중분류 | 계정 설정 (ACCT) |
| 소분류 | 지갑 주소 복사 |
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. Settings 탭 접속된 상태
2. 온보딩이 완료된 상태

**테스트 단계**
1. Settings 화면에서 Account 섹션을 확인한다
2. 이메일 주소와 지갑 주소 표시를 확인한다

**예상 결과**
- Account 섹션에 이메일 주소 `user@gmail.com`이 표시된다
- 지갑 주소 `0x9834...9948`이 표시된다

---

## SETG-LANG — 언어 설정

---

### **SC-SETG-LANG-001** — 언어 전환 (EN → KR) 및 활성 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 설정 (SETG) |
| 중분류 | 언어 설정 (LANG) |
| 소분류 | 언어 전환 (English / 한국어) |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. Settings 탭 접속된 상태
2. 온보딩이 완료된 상태
3. 현재 언어가 English(EN)로 설정된 상태

**테스트 단계**
1. Settings 화면에서 Language 섹션을 확인한다
2. English 옵션이 녹색 배경으로 표시되는지 확인한다
3. `한국어` 옵션을 탭한다
4. Language 섹션의 활성 표시를 확인한다

**예상 결과**
- `한국어` 옵션이 녹색 배경으로 전환된다
- `English` 옵션이 어두운 배경으로 전환된다

---

### SC-SETG-LANG-002 — 언어 전환 (KR → EN) 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 설정 (SETG) |
| 중분류 | 언어 설정 (LANG) |
| 소분류 | 언어 전환 (English / 한국어) |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. Settings 탭 접속된 상태
2. 온보딩이 완료된 상태
3. 현재 언어가 한국어(KR)로 설정된 상태

**테스트 단계**
1. Settings 화면에서 Language 섹션을 확인한다
2. `한국어` 옵션이 녹색 배경으로 표시되는지 확인한다
3. `English` 옵션을 탭한다
4. Language 섹션의 활성 표시를 확인한다

**예상 결과**
- `English` 옵션이 녹색 배경으로 전환된다
- `한국어` 옵션이 어두운 배경으로 전환된다

---

### SC-SETG-LANG-003 — 언어 설정 localStorage 영속 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 설정 (SETG) |
| 중분류 | 언어 설정 (LANG) |
| 소분류 | 언어 전환 (English / 한국어) |
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. Settings 탭에서 언어를 `한국어`로 변경한 상태
2. 온보딩이 완료된 상태

**테스트 단계**
1. 브라우저를 닫거나 새로고침한다
2. 앱에 다시 접속한다
3. Settings 탭의 Language 섹션을 확인한다

**예상 결과**
- 재시작 후에도 Language 섹션에서 `한국어`가 녹색 배경(활성 상태)으로 표시된다
- 이전 세션에서 설정한 언어가 복원된다

**비고**
- [미결] 언어 전환 직후 Toast가 새 언어로 표시되는지 미확정 (PEND-SETS-003)

---

### SC-SETG-LANG-004 — 현재 활성 언어 재탭 시 변화 없음 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 설정 (SETG) |
| 중분류 | 언어 설정 (LANG) |
| 소분류 | 언어 전환 (English / 한국어) |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. Settings 탭 접속된 상태
2. 온보딩이 완료된 상태
3. 현재 언어가 English(EN)로 설정된 상태

**테스트 단계**
1. Language 섹션에서 이미 활성화된 `English` 옵션을 다시 탭한다
2. Language 섹션 상태를 확인한다

**예상 결과**
- `English`가 계속 녹색 배경(활성 상태)으로 유지된다
- 언어 설정이 변경되지 않는다

---

## SETG-LOUT — 로그아웃

---

### **SC-SETG-LOUT-001** — 로그아웃 버튼 탭 후 Toast 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 설정 (SETG) |
| 중분류 | 로그아웃 (LOUT) |
| 소분류 | 로그아웃 (목업 동작) |
| 분류 | Positive |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. Settings 탭 접속된 상태
2. 온보딩이 완료된 상태

**테스트 단계**
1. Settings 화면에서 `Logout` 버튼을 탭한다
2. 화면 하단 Toast 알림을 확인한다
3. 앱 전체 상태가 초기화되었는지 확인한다

**예상 결과**
- 화면 하단에 "Logged out (mockup)" Toast 알림이 표시된다
- Toast 알림이 일정 시간 후 자동으로 사라진다
- 앱 상태가 초기화되지 않는다 (목업 동작이므로 실제 로그아웃 처리 없음)

---

### SC-SETG-LOUT-002 — 로그아웃 후 화면 전환 없음 확인

| 항목 | 내용 |
|------|------|
| 대분류 | 설정 (SETG) |
| 중분류 | 로그아웃 (LOUT) |
| 소분류 | 로그아웃 (목업 동작) |
| 분류 | Negative |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
1. Settings 탭 접속된 상태
2. 온보딩이 완료된 상태

**테스트 단계**
1. Settings 화면에서 `Logout` 버튼을 탭한다
2. Toast 알림이 사라진 후 현재 화면을 확인한다
3. BottomNav 탭 상태를 확인한다

**예상 결과**
- "Logged out (mockup)" Toast 표시 후 화면이 로그인 페이지나 랜딩 페이지로 이동하지 않는다
- Settings 탭이 그대로 표시된다
- 포지션, 잔고 등 앱 상태가 초기화되지 않는다

**비고**
- 목업 전용 동작: 실제 로그아웃 및 상태 초기화 없음이 명시된 정책에 따른 TC

---

---

