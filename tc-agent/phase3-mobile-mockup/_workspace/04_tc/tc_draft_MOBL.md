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
- 온보딩이 완료된 상태이다
- `/trade` 화면에 접속해 있다

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
- 온보딩이 완료된 상태이다
- `/trade` 화면의 Trade 탭이 활성화된 상태이다

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
- 온보딩이 완료된 상태이다
- `/trade` 화면의 Trade 탭이 활성화된 상태이다

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
- 온보딩이 완료된 상태이다
- `/trade` 화면에 접속해 있다

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
- 온보딩이 완료된 상태이다
- 포지션이 1개 이상 보유된 상태이다
- `/trade` 화면의 Trade 탭 > Dashboard > Positions 탭에 접속해 있다

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
- 온보딩이 완료된 상태이다
- 미체결 주문이 1개 이상 있는 상태이다
- `/trade` 화면의 Trade 탭 > Dashboard > Open Orders 탭에 접속해 있다

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
- 온보딩이 완료된 상태이다
- Signal 탭에 ACTIVE 상태 시그널이 1개 이상 존재한다

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
- 온보딩이 완료된 상태이다
- 충분한 잔고가 있는 상태이다
- Trade 탭 주문폼에서 Market 주문 유형이 선택된 상태이다

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
- 온보딩이 완료된 상태이다
- 포지션이 1개 이상 보유된 상태이다 (기본: XRP Short 2x, BTC Long 2x)
- Portfolio 탭에 접속해 있다

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
- 온보딩이 완료된 상태이다
- 보유 포지션이 0개인 상태이다 (모든 포지션을 Close 처리함)
- Portfolio 탭에 접속해 있다

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
- 온보딩이 완료된 상태이다
- Portfolio 탭에 접속해 있다

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
