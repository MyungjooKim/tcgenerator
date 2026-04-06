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
- YOUTHMETA 파트너코드로 가입한 체험용 계정이다
- 약관 동의가 완료된 상태이다
- `/onboarding` 페이지에서 온보딩 3단계가 자동으로 진행 완료된 상태이다

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
- `/onboarding` 페이지에 진입한 상태이다
- 온보딩 3단계 진행이 완료되지 않은 상태이다 (3.2초 미만)

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
- 온보딩이 완료된 상태이다
- 포지션이 1개 이상 보유된 상태이다 (기본 포지션: XRP Short 2x, BTC Long 2x)
- Portfolio 탭에 접속해 있다

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
- 온보딩이 완료된 상태이다
- 포지션이 1개 이상 보유된 상태이다
- Portfolio 탭에 접속해 있다

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
- 온보딩이 완료된 상태이다
- 포지션이 1개 이상 보유된 상태이다
- 해당 포지션을 Trading 탭에서 모두 Close 처리한 상태이다

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
- 온보딩이 완료된 상태이다
- 복수 포지션을 보유하여 margin 합계가 ACCOUNT.balance에 근접한 상태이다

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
