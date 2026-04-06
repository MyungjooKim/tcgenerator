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
- 비로그인 상태이다
- 랜딩 화면(`/`)에 접속해 있다

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
- 랜딩에서 "Continue with Google"을 탭하여 `/login` 화면에 진입한 상태이다

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
- `/login` 화면에 진입한 상태이다

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
- 비로그인 상태이다

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
- 로그인이 완료된 상태이다
- `/terms` 화면에 접속해 있다
- 약관 체크박스가 미체크 상태이다

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
- 로그인이 완료된 상태이다
- `/terms` 화면에 접속해 있다
- 약관 체크박스가 미체크 상태이다

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
- 로그인이 완료된 상태이다
- `/terms` 화면에 접속해 있다
- 약관 체크박스가 미체크 상태이다

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
- 로그인이 완료된 상태이다
- `/terms` 화면에 접속해 있다

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
- 로그인이 완료된 상태이다
- `/terms` 화면에 접속해 있다

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
- 로그인이 완료된 상태이다
- `/terms` 화면에서 약관 체크박스를 체크한 상태이다

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
- 약관 동의가 완료된 상태이다
- `/onboarding` 화면에 진입한 상태이다

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
- 약관 동의가 완료된 상태이다
- `/onboarding` 화면에 진입한 직후(온보딩 진행 중)이다

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
- 약관 동의가 완료된 상태이다
- `/onboarding` 화면의 3단계가 자동 완료된 상태이다

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
- 온보딩 3단계가 완료된 상태이다
- "Start Trading" 버튼이 표시된 상태이다

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
- 약관 동의가 완료된 상태이다
- `/onboarding` 화면에 진입한 상태이다

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
- 약관 동의가 완료된 상태이다
- `/onboarding` 화면 진행 중(완료 전)이다

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
