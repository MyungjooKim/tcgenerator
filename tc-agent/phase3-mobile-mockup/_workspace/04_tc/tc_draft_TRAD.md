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
- 온보딩이 완료된 계정으로 로그인된 상태이다
- `/trade` 탭 trade 화면에 접속해 있다
- 기본 코인 BTC-USDC가 선택된 상태이다

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
- CoinSelector 바텀시트가 열린 상태이다
- 지원 코인 4종(BTC-USDC, ETH-USDC, SOL-USDC, XRP-USDC)이 목록에 표시된 상태이다

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
- CoinSelector 바텀시트가 열린 상태이다

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
- 포지션 및 미체결 주문이 없는 상태이다
- 레버리지가 1x로 설정된 상태이다
- CoinSelector 바텀시트가 열린 상태이다

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
- 보유 포지션이 1개 이상 존재하는 상태이다
- 레버리지가 1x로 설정된 상태이다
- CoinSelector 바텀시트가 열린 상태이다

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
- 온보딩이 완료된 계정으로 로그인된 상태이다
- `/trade` 탭 trade 화면에 접속해 있다
- 주문 유형이 `Market`으로 선택된 상태이다
- 충분한 잔고가 있는 상태이다

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
- 온보딩이 완료된 계정으로 로그인된 상태이다
- `/trade` 탭 trade 화면에 접속해 있다
- 주문 유형이 `Market`으로 선택된 상태이다
- 충분한 잔고가 있는 상태이다

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
- `/trade` 탭 trade 화면에 접속해 있다
- 주문 유형이 `Market`으로 선택된 상태이다 (가격 입력 필드 숨김 상태)

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
- `/trade` 탭 trade 화면에 접속해 있다
- 주문 유형이 `Limit`으로 선택된 상태이다 (가격 입력 필드 표시 상태)

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
- `/trade` 탭 trade 화면에 접속해 있다
- 주문 유형이 `Limit`으로 선택된 상태이다
- 가격 입력 필드가 표시된 상태이다

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
- `/trade` 탭 trade 화면에 접속해 있다
- 수량 슬라이더가 0% 위치(초기 상태)에 있다

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
- `/trade` 탭 trade 화면에 접속해 있다
- 주문 유형이 `Market`으로 선택된 상태이다
- 수량 슬라이더가 0% 위치이며 수량 입력 필드가 0 또는 비어 있는 상태이다

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
- `/trade` 탭 trade 화면에 접속해 있다
- 주문 유형이 `Limit`으로 선택된 상태이다
- 가격 입력 필드가 비어 있는 상태이다
- 수량 슬라이더가 25% 위치로 설정된 상태이다

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
- Auto TP/SL 토글이 ON 상태이다
- TP 1.8% / SL 5.0% 또는 사용자 설정값이 저장된 상태이다
- Market 주문 유형이 선택된 상태이다

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
- 시그널 탭에서 ACTIVE 시그널의 SignalOrderSheet가 열린 상태이다
- Modify 버튼을 탭하여 `PREFILL_FROM_SIGNAL`이 디스패치된 상태이다

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
- `/trade` 탭 trade 화면에 접속해 있다

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
- 온보딩이 완료된 계정으로 로그인된 상태이다
- 포트폴리오 탭에서 현재 가용 잔고(available)를 기록해 둔 상태이다
- Market 주문 유형이 선택된 상태이다

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
- Dashboard Positions 탭에 포지션이 1개 이상 존재하는 상태이다
- Dashboard Positions 탭에 접속해 있다

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
- Dashboard Positions 탭에 포지션이 정확히 1개 존재하는 상태이다
- Dashboard Positions 탭 배지에 녹색 숫자(1)가 표시된 상태이다

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
- 보유 포지션이 없는 상태이다 (온보딩 직후 또는 모든 포지션 Close 후)
- Dashboard Positions 탭에 접속해 있다

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
- 온보딩 완료 직후 상태이다 (주문 실행 이력 없음)
- Dashboard Positions 탭에 접속해 있다

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
- Dashboard Open Order 탭에 미체결 주문이 1개 이상 존재하는 상태이다
- Dashboard Open Order 탭에 접속해 있다

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
- 미체결 주문이 없는 상태이다
- Dashboard Open Order 탭에 접속해 있다

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
- Dashboard Positions 탭에 포지션이 1개 이상 존재하는 상태이다
- `/trade` 탭 trade 화면에 접속해 있다

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
- Dashboard Open Order 탭에 미체결 주문이 1개 이상 존재하는 상태이다
- `/trade` 탭 trade 화면에 접속해 있다

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
- 보유 포지션이 없는 상태이다
- 미체결 주문이 없는 상태이다

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
- Dashboard Open Order 탭에 미체결 주문이 정확히 1개 존재하는 상태이다
- Open Order 탭에 노란색 배지가 표시된 상태이다

**테스트 단계**
1. Dashboard Open Order 탭으로 이동한다
2. 주문 카드의 `Cancel` 버튼을 탭한다
3. Open Order 탭 배지를 확인한다

**예상 결과**
- `"Order cancelled"` Toast가 표시된다
- Open Order 탭의 노란색 배지가 사라진다
- Open Order 탭 목록에 `"No open orders"` 안내 문구가 표시된다
