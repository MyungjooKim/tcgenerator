# TC Policy — 거래소별 특성 정책
**문서 버전:** v1.0
**기준 날짜:** 2026-03-18
**적용 범위:** YouthMeta Partner Version — 현재 지원 5개 거래소

---

## 1. 지원 거래소 목록

| 거래소 | 코드 | 상태 | 비고 |
|--------|------|------|------|
| OKX | OKX | ✅ 지원 | |
| Gate | Gate | ✅ 지원 | Auto TP/SL 미지원 |
| Bybit | Bybit | ✅ 지원 | Full TP/SL 방식 |
| Bitget | Bitget | ✅ 지원 | |
| Hyperliquid | Hyperliquid | ✅ 지원 | |
| Binance | Binance | 🔜 추가 예정 | — |

> **Binance 추가 시:** 이 문서에 행 추가 + 관련 Policy 파일 업데이트 필요

---

## 2. Youthmeta 계정 내 거래소 정렬 순서

Youthmeta 유저에 한정하여 거래소 드롭다운 정렬 순서:

```
1. OKX
2. Gate
3. Bybit
4. Bitget
5. Hyperliquid
```

---

## 3. 거래소별 특성 비교표

### 3.1 Leverage 관련

| 항목 | OKX | Gate | Bybit | Bitget | Hyperliquid |
|------|-----|------|-------|--------|-------------|
| 레버리지 2x 자동 제한 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Position과 Order Form 레버리지 연동 | ❌ 개별 설정 | ✅ | ✅ | ✅ | ✅ |
| Margin 부족 레버리지 변경 실패 토스트 | ✅ | ✅ | ✅ | ✅ | ✅ |
| Hedge Mode 지원 | ✅ | 확인 필요 | ✅ | 확인 필요 | 확인 필요 |
| Isolated Mode 지원 | ✅ | 확인 필요 | ✅ | 확인 필요 | 확인 필요 |

> **OKX 특이사항:** Position 레버리지와 Order Form 레버리지가 독립적으로 설정 가능.
> Position의 레버리지와 Order Form의 레버리지가 연동되지 않음.

### 3.2 Auto TP/SL 관련

| 항목 | OKX | Gate | Bybit | Bitget | Hyperliquid |
|------|-----|------|-------|--------|-------------|
| Auto TP/SL 기능 지원 | ✅ | ❌ | ✅ | ✅ | ✅ |
| TP/SL Limit 주문 설정 | ❌ | N/A | ❌ | ✅ | ✅ |
| TP/SL 주문 유형 | Partial | N/A | Full | Partial | Partial |
| Order Form TP/SL 입력 메뉴 | ✅ | ❌ (없음) | ✅ | ✅ | ✅ |
| Open Orders TP/SL 컬럼 | ✅ | ❌ (없음) | ✅ | ✅ | ✅ |
| Open Orders TP/SL 수정 버튼 | ✅ | ❌ | ✅ | ❌ | ❌ |
| Open Orders TP/SL 삭제 후 재등록 | ✅ | ❌ | ✅ | ❌ | ❌ |

---

## 4. 거래소별 상세 특성

### 4.1 OKX
- Auto TP/SL: **지원**
- TP/SL 유형: **Partial TP/SL** (수량 단위)
- TP/SL Limit 주문: **미지원** (Market만)
- Leverage 특이사항: Position과 Order Form 레버리지가 **개별 설정**

### 4.2 Gate
- Auto TP/SL: **미지원** → Gate 거래소 전체 Auto TP/SL TC는 `N/A` 처리
- Order Form에 TP/SL 메뉴 **없음** → Order Form 관련 TP/SL TC는 `N/A`
- Open Orders TP/SL 컬럼 **없음** → Open Orders 수정 TC는 `N/A`
- Leverage: 정상 지원

### 4.3 Bybit
- Auto TP/SL: **지원**
- TP/SL 유형: **Full Position TP/SL** (포지션 전체 대상, 1개만 설정 가능)
- TP/SL Limit 주문: **미지원** (Market만)
- Open Orders TP/SL 수정: **지원**
- Full TP/SL 추가 주문 시: 최신 주문의 Auto TP/SL 설정값으로 **교체** (기존 것 대체)

### 4.4 Bitget
- Auto TP/SL: **지원**
- TP/SL 유형: **Partial TP/SL** (수량 단위)
- TP/SL Limit 주문: **지원**
- Open Orders TP/SL 수정 버튼: **없음** (N/A)

### 4.5 Hyperliquid
- Auto TP/SL: **지원**
- TP/SL 유형: **Partial TP/SL** (수량 단위)
- TP/SL Limit 주문: **지원**
- Open Orders TP/SL 수정 버튼: **없음** (N/A)

---

## 5. TP/SL 유형별 동작 차이

### 5.1 Partial TP/SL (OKX / Bitget / Hyperliquid)
- 수량 단위로 TP/SL 주문 생성
- 동일 방향 추가 주문: 새 TP/SL 주문 **추가 생성** (기존 것 유지)
- 반대 방향 소량 주문: 기존 TP/SL 유지, 주문 수량만 감소
- 반대 방향 대량 주문 (포지션 스위칭): 기존 TP/SL **전체 취소** → 새 방향으로 신규 생성

### 5.2 Full Position TP/SL (Bybit)
- 포지션 전체 단위 TP/SL 주문 (1개만 설정 가능)
- 동일 방향 추가 주문: 기존 TP/SL **교체** (최신 주문 기준으로 업데이트)
- 반대 방향 소량 주문: 기존 TP/SL 유지
- 반대 방향 대량 주문 (포지션 스위칭): 기존 TP/SL **교체** → 새 방향으로 업데이트

---

## 6. Trigger Price 공식

```
Long 포지션:
  TP Trigger Price = 진입가 × (1 + ROI% / Leverage / 100)
  SL Trigger Price = 진입가 × (1 - ROI% / Leverage / 100)

Short 포지션:
  TP Trigger Price = 진입가 × (1 - ROI% / Leverage / 100)
  SL Trigger Price = 진입가 × (1 + ROI% / Leverage / 100)
```

**예시** (Long, 진입가 $2,000 / TP +1.8% / 레버리지 2x):
```
TP = 2,000 × (1 + 0.018 / 2) = 2,000 × 1.009 = $2,018
SL = 2,000 × (1 - 0.05  / 2) = 2,000 × 0.975 = $1,950
```

---

## 7. TC 작성 시 거래소별 N/A 처리 가이드

### 7.1 Gate N/A 적용 케이스
아래 TC 유형은 Gate 컬럼에 **N/A** 기입:
- Auto TP/SL Settings 관련 모든 TC
- Order Form Auto TP/SL 표시/연동 TC
- Order Form TP/SL 입력 관련 TC
- Open Orders TP/SL 수정/추가/확인 TC

### 7.2 Hyperliquid + Bitget N/A 적용 케이스
- Open Orders TP/SL 수정 (TC-06-006, TC-06-007 계열)
  → 수정 버튼 없음

### 7.3 OKX + Bybit N/A 적용 케이스
- Open Orders TP/SL 수정 불가 확인 TC (TC-06-008 계열)
  → 수정 가능하므로 해당 TC 적용 불가

---

## 8. 거래소 추가 시 체크리스트 (Binance 등)

신규 거래소 추가 시 아래 항목 확인 후 이 문서 업데이트:

- [ ] Auto TP/SL 지원 여부
- [ ] TP/SL 유형 (Partial / Full)
- [ ] TP/SL Limit 주문 지원 여부
- [ ] Order Form TP/SL 입력 메뉴 존재 여부
- [ ] Open Orders TP/SL 컬럼 존재 여부
- [ ] Open Orders TP/SL 수정 버튼 존재 여부
- [ ] Leverage 연동 방식 (Position ↔ Order Form)
- [ ] Hedge Mode / Isolated Mode 지원 여부
- [ ] 거래소 표시 순서 업데이트
