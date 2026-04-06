# TC 초안 — TRAD / SGNL / FUND 도메인 (F-042~F-063)

> 작성 일시: 2026-04-02
> 적용 규칙: common/tc-rules.md + phase2-mobile/tc-rules-override.md
> 담당 기능: F-042~F-063 (22개)
> 작성 TC 수: 31개

> **FUND 도메인 비고:** feature_list.md 기준 FUND 도메인(F-009~F-017)은 담당 범위(F-042~F-063)에 포함되지 않습니다.
> F-042~F-063 내에 FUND 관련 기능이 별도 분류되어 있지 않으므로 TRAD / SGNL 도메인 TC만 작성합니다.

---

## [TRAD] 거래 — 주문 및 포지션 (F-042~F-055)

---

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
