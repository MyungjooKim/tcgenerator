# Supercycl Mobile — 주문 옵션 조합 명세 (그레이박스 TC)

> 화면 중심 TC 와 별개로, **거래 옵션 조합 + 사용자 시나리오** 기반 그레이박스 TC 정의.
> 시드는 SCR-102/104/106 spec 에서 추출. 도메인 룰은 사람이 보강 가능한 markdown 형태.
>
> **사용 모드:** 명시적 ("옵션 조합 TC 생성"). SCR 파이프라인과 독립.
> **출력 시트:** `Combo` (별도 시트, 화면별 시트와 분리)
> **TC ID 패턴:** `SM-COMBO-NNN` (Decision Table) / `SM-FLOW-NNN` (시나리오)
>
> **테스트 성격 (그레이박스 정책):**
> - **기대 결과**: 사용자 가시 동작/결과만 (블랙박스 표현 — DOM ID·state·함수명 노출 안 함)
>   - ✅ "검증 실패 메시지가 표시된다, 저장 거부, 시트 유지"
>   - ⛔ "`#tpSlErr` 표시, `saveTpSl()` 실패" (지나치게 내부 노출)
> - **사전 조건의 마지막 줄에 (선택적) 기술 힌트**: DOM ID·식별자를 1~2개 적어 테스터가 빠르게 검증 위치를 잡을 수 있게.
>   - 예: `3. (기술 참고) TP 입력 필드 #tpSlTpInput, 에러 영역 #tpSlErr`
> - 이 명세 표 안의 `#tpSlErr` 같은 식별자는 **TC 변환 시 사전 조건으로 옮겨지며, 기대 결과 본문에서는 블랙박스 표현으로 재작성**됨

---

## 1. 거래 옵션 차원 (Reference)

| 차원 | 가능한 값 | 비고 |
|------|----------|------|
| **Side** | Long, Short | |
| **Type** | Market, Limit | Limit 은 지정가 + Δ% 표시 + Open Order 등록 |
| **Symbol (코인)** | BTC/USDT, ETH/USDT, SOL/USDT, (외 다수) | 가격대·틱·최소 주문 단위·leverage 상한 코인별 상이 |
| **Margin Mode** | Cross, Isolated | 동일 심볼·방향 포지션 존재 시 🔒 잠금 |
| **Position Mode** | One-way, Hedge | Hedge 는 Long/Short 동시 보유, side 별 leverage 분리 |
| **Leverage** | 1x, 5x, 10x, 25x, 50x, 100x | 거래소별 상한 (OKX 기준 최대 100x) |
| **Auto-protect** | None, Conservative, Balanced, Aggressive, Custom | 프리셋 값 ↓ |
| **Auto-protect 값** | Conservative(+10%/−5%), Balanced(+20%/−10%), Aggressive(+30%/−15%), Custom(사용자 입력) | TP: min=1, max=100 / SL: min=−50, max=−1 |
| **입력 단위** | Margin (USDT), Quantity (BTC) | 메인은 Margin |
| **잔고 상태** | 충분, 거의 한계(80%), 한계 초과 | 80% 초과 시 경고 배너 |
| **시장 상태** | 평시, mark-price-stale(시세 끊김), 변동성 큼 | |
| **포지션 거리** | 평시, near-liquidation(≤15%), liquidated | near-liquidation 시 Add Margin 노출 |

## 2. 도메인 룰 (Reference)

**계산:**
- Position size = Margin × Leverage
- Notional value = Margin × Leverage (USD 환산)
- ROE = (PnL / 투입 증거금) × 100
- Δ% (Limit) = ((Limit price − Mark price) / Mark price) × 100
- Liquidation price = side/leverage/margin 기반 (Long: entry 미만, Short: entry 초과)

**검증 룰:**
- Long TP/SL 방향: TP > entry > SL
- Short TP/SL 방향: TP < entry < SL
- TP/SL 방향 위반 시 `#tpSlErr` 표시, 저장 안 됨, 시트 유지

**상태 전환:**
- 동일 심볼·방향 포지션 존재 → Margin Mode 행 🔒 (편집 불가)
- 동일 심볼·반대 방향만 존재 → Margin Mode 편집 가능 + 상단 배너
- Hedge 모드 ON → 동일 심볼에 Long/Short 별도 카드 + 각자 leverage

**테스트 실행 위험 등급 (Test Execution Risk):**

각 TC 는 실행 시 실제 자금 영향이 다름. AI 가 OC 의 옵션 조합을 보고 아래 등급 중 하나를 판단해 **`⚠️ 테스트 실행 시 주의`** 섹션을 TC 마지막에 추가한다 (없으면 생략).

| 등급 | 조건 | 권장 안내 메시지 템플릿 |
|------|------|---------------------|
| 🔴 **고위험** | Leverage ≥ 50x 또는 잔고 사용 ≥ 80% 또는 다수 주문 회전 | "고배율/고비중 주문 — 가격 변동 시 Margin 전액 (≈ {margin} USDT) 손실 가능. 테스트 계정 또는 매우 소액 권장." |
| 🟡 **중위험** | Leverage 10~25x 또는 잔고 사용 50~79% 또는 Hedge 양방향 | "예상 max 손실 약 {margin} USDT. 다른 주문 여력 제한됨. 실데이터 환경 신중 사용." |
| 🟢 **저위험** | Leverage ≤ 5x 또는 작은 Margin (< 50 USDT) | "예상 max 손실 약 {margin} USDT (저배율). 학습용 적합." |
| ⚪ **위험 없음** | 입력 검증 실패 / UI 표시 / Loading / 시세 끊김 등 자금 미이동 케이스 | (`⚠️ 테스트 실행 시 주의` 섹션 생략) |

**판단 시 추가 고려:**
- Limit 주문 (체결 전): 잔고 차감되나 미체결 시 Cancel 로 환원 → 위험 한 단계 낮춤
- Market 주문: 즉시 체결 → 그대로 평가
- Liquidation 임계 근접 시나리오 (near-liquidation): 잔고 영향 없으나 추가 Margin 필요 명시
- 다수 주문 회전 (스캘퍼): 누적 수수료 영향 명시

**코인별 특성 (Symbol 차원):**
- **BTC/USDT**: 메이저, 가격 ~$50K~$70K, 틱 $0.1, 최소 주문 0.0001 BTC, 최대 leverage 100x
- **ETH/USDT**: 메이저, 가격 ~$2K~$4K, 틱 $0.01, 최소 주문 0.001 ETH, 최대 leverage 100x
- **SOL/USDT**: 알트, 가격 ~$100~$200, 틱 $0.001, 최소 주문 0.1 SOL, 최대 leverage 50x (거래소별 상이)
- **표기**: `{qty} {symbol} ($notional)` — quantity 정밀도는 코인별 다름 (BTC 4자리, ETH 3자리, SOL 1자리)
- **틱 미만 입력**: Limit price 입력 시 틱 단위로 자동 반올림 또는 hint 표시
- **최소 주문 미만**: Quantity 가 코인별 min 미만이면 주문 거부
- **알트 leverage 상한**: BTC/ETH 는 100x 까지지만 SOL/기타 알트는 거래소별 25x~50x 제한 — 상한 초과 시 자동 제한 또는 거부

---

## 3. 옵션 조합 매트릭스 (Decision Table)

> 각 행 = 1 TC. `OC-NNN` ID 부여.
> 조합 폭발 회피 위해 **의미있는 조합** 만 정의 (대표값 + 경계값 + 위험 조합).

### 3.1 정상 케이스 (Positive — 표준 흐름)

| OC-ID | Side | Type | Mode | Position Mode | Leverage | Auto-protect | 잔고 | 검증 의도 | 기대 결과 |
|-------|------|------|------|---------------|----------|--------------|------|---------|---------|
| OC-001 | Long | **Limit** | Cross | One-way | 5x | Conservative | 충분 | **타겟 페르소나 — Limit 5x Conservative** | Open Order 등록, Δ% 표시, Mark 도달 시 체결 → Position 생성, TP +10% / SL −5% 자동 |
| OC-002 | Long | Market | Cross | One-way | 3x | Conservative | 충분 | 신규 사용자 기본 (저배율) | 주문 성공, Long 포지션, Liquidation 거리 매우 안전, TP +10% / SL −5% |
| OC-003 | Short | Market | Cross | One-way | 5x | Conservative | 충분 | 신규 사용자 Short | 주문 성공, Short 포지션, TP/SL 자동 |
| OC-004 | Long | Limit | Cross | One-way | 10x | None | 충분 | 지정가 + Auto-protect 미설정 | Open Order 등록, TP/SL 미설정, Open Orders 카드 표시 |
| OC-005 | Long | Market | Cross | One-way | 5x | Balanced | 충분 | 중간 보호 | 주문 성공, TP +20% / SL −10% |
| OC-006 | Short | Limit | Isolated | One-way | 25x | Aggressive | 충분 | 공격형 Limit + Isolated | Open Order 등록, Margin 격리, TP +30% / SL −15% |
| OC-007 | Long | Market | Isolated | One-way | 50x | Custom(+15/−7) | 충분 | 공격형 + Custom 직접 입력 | 주문 성공, TP +15% / SL −7%, 입력값 그대로 저장 |

### 3.2 경계값 / 위험 조합 (Boundary)

| OC-ID | Side | Type | Mode | Leverage | Auto-protect | 잔고 | 검증 의도 | 기대 결과 |
|-------|------|------|------|----------|--------------|------|---------|---------|
| OC-010 | Long | Market | Cross | 1x | Conservative | 충분 | 최저 배율 (현물에 가까운) | 주문 성공, Liquidation price 가 entry 와 매우 멀음 |
| OC-011 | Long | Market | Isolated | 100x | Conservative | 충분 | 최대 배율 | 주문 성공, Liquidation price 가 entry 에 매우 근접, 위험 경고 표시 |
| OC-012 | Long | Market | Cross | 100x | Aggressive | 한계 80% | 고배율 + 잔고 한계 | 잔고 비율 경고 배너 표시, 주문은 진행 가능 |
| OC-013 | Long | Market | Cross | 10x | Conservative | 한계 초과 | 잔고 부족 | 주문 거부, "Insufficient balance" 에러, 주문 미제출 |
| OC-014 | Long | Limit | Cross | 10x | None | 충분 | Limit price = Mark price (Δ% 0) | 정상 등록, Δ% 0% 표시 |
| OC-015 | Long | Limit | Cross | 10x | None | 충분 | Limit price 가 Mark price 보다 매우 멀음 (−50%) | 경고 또는 hint 표시, 등록 가능 |

### 3.3 입력 검증 실패 (Negative)

| OC-ID | Side | Type | Auto-protect | Custom 값 | 검증 의도 | 기대 결과 |
|-------|------|------|--------------|----------|---------|---------|
| OC-020 | Long | Market | Custom | TP=−5%, SL=−10% | Long 방향 룰 위반 (TP < entry) | `#tpSlErr` 표시, 저장 안 됨, 시트 유지 |
| OC-021 | Long | Market | Custom | TP=+10%, SL=+5% | Long 방향 룰 위반 (SL > entry) | `#tpSlErr` 표시, 저장 안 됨 |
| OC-022 | Short | Market | Custom | TP=+10%, SL=+5% | Short 방향 룰 위반 (TP > entry) | `#tpSlErr` 표시, 저장 안 됨 |
| OC-023 | Long | Market | Custom | TP=101% | TP 입력 범위 초과 (max=100) | 입력 필드 max 속성에 의해 제한, 100 이상 입력 불가 |
| OC-024 | Long | Market | Custom | SL=−51% | SL 입력 범위 초과 (min=−50) | 입력 필드 min 속성에 의해 제한 |
| OC-025 | Long | Market | Custom | TP=0% | TP 0 (range 위반, min=1) | 입력 필드 min 속성에 의해 제한 |

### 3.4 스캘퍼 조합 (초단타 — 100x + 좁은 TP/SL + 다수 회전)

| OC-ID | Side | Type | Mode | Leverage | Auto-protect | 검증 의도 | 기대 결과 |
|-------|------|------|------|----------|--------------|---------|---------|
| OC-050 | Long | Market | Cross | 100x | Custom(+2/−1) | 100x + 좁은 TP/SL | 주문 성공, 작은 가격 변동에 TP/SL 즉시 트리거 가능 |
| OC-051 | Short | Market | Cross | 100x | None | 100x 보호 미설정 (수동 종료) | 주문 성공, Auto-protect 없이 mark 추적만 |
| OC-052 | Long | Market | Cross | 100x | Custom(+1/−0.5) | 매우 좁은 보호 (스캘퍼 표준) | 주문 성공, 1% 도달 시 즉시 TP 체결 |
| OC-053 | (다수 회전) | Market | Cross | 100x | Conservative | 10개 연속 주문 → Open Orders/Position 카드 다수 | 카드 다수 정상 렌더, 스크롤 부드러움, 성능 저하 없음 |
| OC-054 | Long | Market | Cross | 100x | None | 진입 후 즉시 수동 Close (mark price 변동 후) | Position 카드 생성 즉시 Close 시트 진입 가능, PnL 실시간 |

### 3.5 Hedge 모드 조합

| OC-ID | 시나리오 | 기대 결과 |
|-------|---------|---------|
| OC-030 | Hedge ON, 동일 심볼 Long(10x) → Short(20x) 순서 진입 | 두 포지션 별도 카드, side 별 leverage 분리 적용 |
| OC-031 | Hedge ON, Long 포지션 → Margin Mode 편집 시도 | 🔒 잠금 (동일 방향 존재) |
| OC-032 | Hedge ON, Long 포지션 존재 → Short 신규 진입 시 Margin Mode | 편집 가능 + 상단 배너 표시 |
| OC-033 | Hedge OFF (One-way), 동일 심볼 Long → Long 추가 | 기존 포지션에 합산 (평단가 재계산) |

### 3.6 시세/시스템 에러 케이스

| OC-ID | 상태 | 검증 의도 | 기대 결과 |
|-------|------|---------|---------|
| OC-040 | mark-price-stale (시세 끊김) | 시세 갱신 중 주문 시도 | 이전 mark price 유지 + 배너 "Price data delayed. Reconnecting...", 주문 가능하나 경고 |
| OC-041 | 서버 5xx 에러 | 주문 제출 실패 | SCR-602 Order Failed 화면, Retry 옵션 제공 |
| OC-042 | 네트워크 끊김 | 주문 제출 중 끊김 | 타임아웃 후 에러 메시지 |
| OC-043 | near-liquidation (≤15%) 포지션 보유 중 | Add Margin 가능 여부 | Add Margin 버튼 노출, Margin 추가 시 Liquidation 재계산 |

### 3.7 행위 가드 (Double Tap / 빠른 입력)

| OC-ID | 동작 | 속도 | 페르소나 | 검증 의도 | 기대 결과 |
|-------|------|------|---------|---------|---------|
| OC-060 | Confirm 더블 탭 — 일반 속도 | 300~500ms 간격 | S3 실수 사용자 | 일반 사용자 실수 시 중복 주문 방지 (안전 가드) | 1회만 제출, 두 번째 탭 무시 |
| OC-061 | Confirm 더블 탭 — 빠른 속도 | 100ms 이내 (연타) | S6 스캘퍼 | 매우 빠른 연속 입력에도 가드 작동 (성능 가드) | 1회만 제출, 다수 탭 모두 무시, UI 반응성 유지 |
| OC-062 | Close 시트 Confirm Close 더블 탭 | 300~500ms | S3 실수 사용자 | 부분 종료 중복 방지 | 1회만 제출, 두 번째 탭 무시 |

### 3.8 코인 다양성 (Symbol 별 특성 검증)

| OC-ID | Symbol | Side / Type / Leverage | 검증 의도 | 기대 결과 |
|-------|--------|----------------------|---------|---------|
| OC-070 | BTC/USDT | Long Market 10x | 메이저 코인 표준 진입 (틱 $0.1, 최소 0.0001 BTC) | Quantity 표시 4자리 (예: 0.0046 BTC), `0.0046 BTC ($300)` 형식 |
| OC-071 | ETH/USDT | Long Market 10x | 중간가 코인 (틱 $0.01, 최소 0.001 ETH) | Quantity 표시 3자리 (예: 0.087 ETH), Limit price 0.01 USDT 단위 |
| OC-072 | SOL/USDT | Long Market 10x | 저가 알트 (틱 $0.001, 최소 0.1 SOL) | Quantity 표시 1자리 (예: 2.3 SOL), Limit price 0.001 USDT 단위 |
| OC-073 | SOL/USDT | Long Market 100x 시도 | 알트 leverage 상한 (SOL ~50x) | 거부 또는 자동 상한 제한, 안내 메시지 표시 |
| OC-074 | BTC/USDT | Long Limit, 틱 미만 입력 ($0.05 단위) | 틱 사이즈 검증 | 자동 반올림 또는 hint 표시, 정확한 틱 단위로 정렬 |
| OC-075 | SOL/USDT | Long Market, 최소 미만 (0.05 SOL) | min quantity 검증 | 거부 메시지, 주문 미제출 |
| OC-076 | (다중) BTC + ETH + SOL 동시 보유 | One-way, 각자 다른 leverage | 다중 심볼 카드 동시 표시 | SCR-106 에 3개 카드 별도 표시, 각자 정밀도/leverage 정확 |

---

## 4. 사용자 시나리오 (Use Case Sequence)

> 각 시나리오 = 페르소나 + 흐름 + 검증 포인트. 시나리오 한 단계 = 1 TC.
> `SM-FLOW-S{N}-{step}` 또는 `SM-FLOW-NNN` 순차.

### 페르소나 매트릭스 (한눈에 비교)

| 페르소나 | 거래 경험 | 배율 | Margin | Auto-protect | Hedge | Order Type | 주요 검증 영역 |
|---------|---------|------|--------|--------------|-------|-----------|---------------|
| **S1 신규** | 처음 | **2~5x** | Cross | Conservative | OFF | Market | Default 안전성, 부분 종료 |
| **S2 공격형** | 1년+ | **10~50x** | Isolated | Aggressive/Custom | **ON** | Mixed | Hedge 분리, Margin Mode 잠금 |
| **S3 실수** | 모든 단계 | (실수) | - | (잘못된 값) | - | - | UX 가드, 입력 검증 |
| **S4 위기** | 보유 중 | (보유 포지션) | - | - | - | - | near-liquidation, 시세 끊김 |
| ⭐ **S5 Limit** | 중급+ | 5~25x | Cross | Conservative | OFF | **Limit** | **타겟 페르소나** — Open Order ↔ Position 전환, Δ% |
| **S6 스캘퍼** | 1~3년 | **100x** | Cross | Custom (좁음) | OFF | Market | 초단타, 더블 탭 가드, 성능, 다수 회전 |
| **S7 멀티코인** | 중급+ | 5~25x | Mixed | Conservative/Balanced | OFF | Mixed | **다중 심볼**, 코인별 정밀도/상한, 카드 분리 |

**사용자 분포 추정:** S5 > S1 >> S6 > S3 > S2 > S4 ≈ S7 (S5 가 타겟이므로 가장 핵심)
**비즈니스 위험 우선순위:** S4 ≈ S2 > S6 (100x) > S3 > S7 > S5 > S1

### S1: 조심성 많은 신규 사용자 (Conservative First-time)

**페르소나:** 첫 거래소 연동 직후, 작은 금액 (50 USDT) 으로 시작
**특성:** 손실 두려움 강함, 안내 문구 정독, 학습 중. **저배율 (2~5x)** 만 사용
**총 5 TC**

| Step | 동작 | 사용 OC | 검증 |
|------|------|---------|------|
| S1-1 | SCR-807 온보딩 → 거래소 연결 완료 | - | 연결 성공 + Lite Trade 진입 |
| S1-2 | SCR-102 에서 OC-002 설정 (Long 3x Cross Conservative Market) | OC-002 | 입력 정상, 슬라이더 % 계산, 저배율 표시 |
| S1-3 | SCR-104 Confirm 진입 → 표시값 검증 | OC-002 | Position size = 150 USDT, Liquidation 거리 매우 안전 (3x), TP/SL 미리보기 |
| S1-4 | Confirm 탭 → SCR-601 Order Success | OC-002 | 주문 성공, Position 생성 |
| S1-5 | SCR-106 Position 카드 → 부분 종료 25% | - | 부분 종료 성공, 카드 잔존 (75% remaining) |

### S2: 공격적 단기 트레이더 (Aggressive Hedge)

**페르소나:** 익숙한 사용자, Hedge 모드 + 동일 심볼 양방향
**특성:** 1년+ 경험, **중배율~고배율 (10~50x)**, Isolated, Hedge ON
**총 6 TC**

| Step | 동작 | 사용 OC | 검증 |
|------|------|---------|------|
| S2-1 | 프로필에서 Hedge 모드 활성화 | OC-030 setup | 배너 표시 "Hedge mode active" |
| S2-2 | SCR-102 에서 Long 25x Aggressive Isolated 진입 | OC-005 변형 | Side 별 leverage 표시 |
| S2-3 | 동일 심볼 Short 10x Aggressive 진입 (반대 방향) | OC-030 | Margin Mode 편집 가능 + 배너 |
| S2-4 | SCR-106 에 두 카드 별도 표시 | OC-030 | Long 카드 + Short 카드, 각자 leverage |
| S2-5 | Long 카드만 부분 종료 50% | - | Long 카드 갱신, Short 카드 영향 없음 |
| S2-6 | Short 카드 Edit TP/SL → Aggressive 적용 | - | Short TP < entry < SL 방향 검증 통과 |

### S3: 초보 실수 시나리오 (Mistake Recovery)

**페르소나:** UX 가드 검증, 잘못된 입력 시 시스템 보호 동작
**특성:** 모든 사용자에게 발생 가능. 급하거나 부주의한 동작이 시스템 보호로 차단되는지 검증
**총 6 TC**

| Step | 동작 | 사용 OC | 검증 |
|------|------|---------|------|
| S3-1 | 잔고 100 USDT, Margin 110 입력 시도 | OC-013 | 입력 거부 또는 max 슬라이더 100% 제한 |
| S3-2 | Margin 85 (잔고 85%) 입력 후 Confirm | OC-012 | SCR-104 진입, 경고 배너 표시 |
| S3-3 | Long 포지션 + TP −5% (잘못된 방향) 시도 | OC-020 | `#tpSlErr`, 저장 거부, 시트 유지 |
| S3-4 | Confirm 더블 탭 (실수, 300~500ms 간격) | OC-060 | 1회만 제출, 두 번째 탭 무시 (안전 가드) |
| S3-5 | 정정해서 TP +10% 다시 입력 후 Save | - | 검증 통과, 저장 성공 |
| S3-6 | Confirm 후 SCR-602 (가상 실패) → Retry → SCR-601 | OC-041 | 재시도 성공 흐름 |

### S4: 위기 관리 시나리오 (Crisis Management)

**페르소나:** 시장 급락 / 청산 임박 시 사용자 대응
**총 4 TC**

| Step | 동작 | 사용 OC | 검증 |
|------|------|---------|------|
| S4-1 | Long 포지션 보유 중 시세 급락 → near-liquidation | OC-043 | DANGER 게이지 + 경고 배너 + Add Margin 노출 |
| S4-2 | Add Margin 시트 진입 → 50 USDT 추가 | - | Liquidation 재계산 미리보기 |
| S4-3 | Confirm 후 Position 갱신 | - | Margin 증가, Liquidation 거리 회복 |
| S4-4 | 추가 직후 mark-price-stale 발생 | OC-040 | 배너 표시 + PnL 회색 stale 표시 + 자동 재연결 |

### ⭐ S5: Limit Order 추적 시나리오 — **타겟 페르소나** (Order Lifecycle)

**페르소나:** 지정가 주문으로 더 좋은 진입가를 노리는 중급+ 사용자
**특성:** 시장가보다 지정가 선호, Mark price 와 차이 모니터링, 대기/체결/취소 사이클
**비즈니스 가치:** **본 제품의 핵심 타겟 사용자 그룹.** S5 가 잘 동작해야 제품 성공.
**총 6 TC** (타겟이라 확장)

| Step | 동작 | 사용 OC | 검증 |
|------|------|---------|------|
| S5-1 | SCR-102 에서 Long Limit 5x Conservative 입력 (Mark $50,000 → $49,500 지정) | OC-001 | 입력 정상, Limit price 필드 노출, Δ% −1% 실시간 표시 |
| S5-2 | SCR-104 Confirm 진입 → 표시값 검증 | OC-001 | Limit price 행 + Δ% 표시, Mark price 행, Auto-protect Conservative |
| S5-3 | Confirm 탭 → Open Order 카드 등록 | OC-001 | Open Orders 카드 등록, Position 카드 아직 없음 |
| S5-4 | Mark price → $49,500 도달 (시뮬) → 체결 | - | Open Order 카드 사라짐, Position 카드 생성, TP +10% / SL −5% 자동 |
| S5-5 | (대안 경로) Mark 미도달 상태에서 Open Order Cancel | - | 주문 취소, 잔고 환원, 카드 사라짐 |
| S5-6 | Limit price 모니터링 — Mark 변동에 따라 Δ% 실시간 갱신 | OC-014, OC-015 | Δ% 재계산, Mark 와 매우 멀면 hint 표시 |

### S6: 스캘퍼 (Scalper) — 초단타 고빈도 트레이더

**페르소나:** 분~초 단위 초단타, 작은 변동에서 다수의 작은 수익 누적
**특성:** **100x 고정**, 시장가 위주, 좁은 TP/SL (+1~2% / −0.5~1%), 다수 회전 (하루 10~50+), UI 응답성 매우 중요
**총 6 TC**

| Step | 동작 | 사용 OC | 검증 |
|------|------|---------|------|
| S6-1 | SCR-102 에서 Long 100x Market Custom(+2/−1) 진입 | OC-050 | 100x 슬라이더 최대 도달, Custom TP/SL 입력 |
| S6-2 | SCR-104 Confirm → Liquidation 거리 매우 가까움 검증 | OC-050 | Liquidation price 가 entry 와 매우 근접 (1% 미만), 경고 표시 |
| S6-3 | Confirm 더블 탭 — 빠른 연타 (100ms 이내) | OC-061 | 1회만 제출, 다수 탭 모두 무시, UI 반응성 유지 (성능 가드) |
| S6-4 | Position 카드 → 즉시 mark price 변동 (TP +1% 도달) | OC-052 | PnL 실시간 갱신, TP 자동 트리거 → 카드 사라짐 |
| S6-5 | 즉시 다음 100x Short Market 진입 (반복 패턴) | OC-051 | 직전 종료 후 새 진입 정상, 자본 효율 (Cross) 검증 |
| S6-6 | 10 분간 10회 반복 회전 → Open Orders / Position 카드 다수 | OC-053 | 카드 렌더 성능 저하 없음, 스크롤 부드러움, 시세 갱신 지속 |

### S7: 다중 코인 트레이더 (Multi-coin)

**페르소나:** 메이저+알트 동시 모니터링, 코인별로 다른 전략
**특성:** BTC/ETH/SOL 다중 보유, 각자 다른 leverage/Mode, 상관관계·다각화 활용
**총 6 TC**

| Step | 동작 | 사용 OC | 검증 |
|------|------|---------|------|
| S7-1 | SCR-102 에서 BTC/USDT 선택 → Long 10x Market Conservative 진입 | OC-070 | BTC 포지션 카드 생성, Quantity 4자리 정밀도 (예: 0.0046 BTC) |
| S7-2 | 심볼 전환 → ETH/USDT 선택 → Long 25x Market Balanced 진입 | OC-071 | ETH 포지션 카드 생성, Quantity 3자리 정밀도, BTC 카드와 별도 표시 |
| S7-3 | 심볼 전환 → SOL/USDT → Long 5x Limit Conservative 등록 (틱 $0.001) | OC-072 | SOL Open Order 등록, Limit price 가 틱 단위로 정렬 (0.001 USDT 단위) |
| S7-4 | SOL 100x 시도 (상한 초과) | OC-073 | 슬라이더가 SOL 상한 (예: 50x) 까지만 이동 또는 거부 메시지 |
| S7-5 | SCR-106 다중 카드 표시 확인 | OC-076 | BTC + ETH + SOL 3개 카드 동시 표시, 각자 leverage/Quantity 정확 |
| S7-6 | BTC 카드만 부분 종료 50% | - | BTC 카드만 갱신 (50% remaining), ETH/SOL 카드 영향 없음 |

---

## 5. 운영 가이드

### 5.1 추가 방법
- 위 표에 행 추가만 하면 즉시 반영 (TC 생성기 재실행)
- OC-ID / FLOW-ID 는 순차 부여
- 새 시나리오: ### S{N}: 제목 + 페르소나 + 표

### 5.2 TC 변환 시 규칙
- OC 한 행 → 1 TC (`SM-COMBO-NNN`)
- 시나리오 한 step → 1 TC (`SM-FLOW-NNN`)
- 소분류: OC-ID / FLOW-ID 형태 (예: `OC-001 표준 시장가 주문`)
- 연관 화면: 시나리오 흐름 따라 SCR 다수

### 5.3 SCR 기반 TC 와의 관계
- **독립적** — Combo TC 는 SCR md 안 봄, order_combinations.md 만 봄
- 같은 화면 동작이라도 화면 중심 TC 는 "버튼 잘 눌리는가", Combo 는 "옵션 조합 결과 정확한가" 검증
- 중복 OK — 관점이 다름

### 5.4 검증 의도 명확화
- 검증 의도는 **의미있는 한 문장** (이 조합이 왜 중요한가)
- 기대 결과는 **측정 가능한 사실** (값/상태/메시지)
