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
- 로그인 및 온보딩이 완료된 계정이다
- BottomNav에서 Signal 탭을 탭하지 않은 상태이다

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
- 시그널 화면에 진입해 있다
- 필터 탭바가 화면에 표시된 상태이다

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
- 시그널 화면에 진입해 있다
- 목업 데이터 기준 모든 시그널이 종료(HIT_TP / HIT_SL / EXPIRED) 상태이거나, Active 필터 적용 시 결과가 없는 환경이다

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
- 시그널 화면에 진입해 있다
- 목업 데이터에 ACTIVE 상태 시그널(예: sig-001 BTC LONG, sig-002 SOL SHORT)이 존재한다

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
- 시그널 화면에 진입해 있다
- 목업 데이터에 HIT_TP 상태(예: sig-003 ETH LONG +2.64%)와 HIT_SL 상태(예: sig-004 XRP SHORT -3.51%) 시그널이 존재한다

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
- 로그인이 완료된 상태이다
- 미읽음 시그널(`unreadCount` > 0) 상태이다
- 현재 Trade 탭에 있으며 Signal 탭에 진입하지 않은 상태이다

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
- 시그널 탭에 이미 진입하여 미읽음 카운트가 0인 상태이다
- 다른 탭(Trade 등)으로 이동한 상태이다

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
- 시그널 화면에 진입해 있다
- ACTIVE 상태의 시그널 카드(예: sig-001 BTC LONG)가 화면에 표시된 상태이다

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
- ACTIVE 시그널의 Execute 버튼을 탭하여 SignalOrderSheet 바텀시트가 열린 상태이다
- 충분한 잔고가 있는 계정이다

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
- ACTIVE 시그널의 Execute 버튼을 탭하여 SignalOrderSheet 바텀시트가 열린 상태이다
- 충분한 잔고가 있는 계정이다

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
- 시그널 화면에 ACTIVE 상태의 LONG 시그널(예: sig-001 BTC LONG)과 SHORT 시그널(예: sig-002 SOL SHORT)이 표시된 상태이다

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
- 시그널 화면에 HIT_TP, HIT_SL, 또는 EXPIRED 상태의 시그널 카드가 표시된 상태이다

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
- ACTIVE 시그널의 Execute 버튼을 탭하여 SignalOrderSheet 바텀시트가 열린 상태이다
- 편집 모드는 OFF 상태이다

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
- SignalOrderSheet 바텀시트가 열린 상태이다
- Modify 버튼을 탭하여 편집 모드가 활성화된 상태이다

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
- SignalOrderSheet 바텀시트가 열린 상태이다
- Modify 버튼을 탭하여 편집 모드가 활성화된 상태이다
- 충분한 잔고가 있는 계정이다

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
- SignalOrderSheet 바텀시트가 열린 상태이다
- 편집 모드가 활성화된 후 Modify 버튼을 다시 탭하여 편집 모드를 OFF로 전환한 상태이다

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
