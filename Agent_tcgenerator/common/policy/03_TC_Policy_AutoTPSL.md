# TC Policy — Auto TP/SL 기능 정책
**문서 버전:** v1.0
**기준 날짜:** 2026-03-18
**적용 범위:** Youthmeta Partner Version — Auto TP/SL 기능 전체

---

## 1. 기능 개요

Auto TP/SL은 Youthmeta 계정 전용 기능으로, 주문 체결 시 TP(Take Profit) / SL(Stop Loss)을 ROI% 기반으로 자동 설정한다.
Settings > Trading Preferences에서 ON/OFF 및 수치를 설정하며, 주문 시 자동으로 TP/SL 주문이 함께 생성된다.

---

## 2. 거래소별 지원 여부

| 항목 | OKX | Gate | Bybit | Bitget | Hyperliquid |
|------|-----|------|-------|--------|-------------|
| Auto TP/SL 지원 | ✅ | ❌ | ✅ | ✅ | ✅ |
| TP/SL Limit 주문 | ❌ (Market만) | N/A | ❌ (Market만) | ✅ | ✅ |
| Order Form TP/SL 입력 메뉴 | ✅ | ❌ | ✅ | ✅ | ✅ |
| Open Orders TP/SL 컬럼 | ✅ | ❌ | ✅ | ✅ | ✅ |
| Open Orders TP/SL 수정 버튼 | ✅ | ❌ | ✅ | ❌ | ❌ |
| TP/SL 유형 | Partial | N/A | Full | Partial | Partial |

> **Gate:** Auto TP/SL 전체 미지원 → Gate 관련 모든 Auto TP/SL TC는 `N/A` 처리

---

## 3. Settings 화면 — Auto TP/SL 설정

### 3.1 진입 경로
```
Settings > Trading Preferences > Auto TP/SL
```

### 3.2 초기 상태 (신규 계정)
- Auto TP/SL: **OFF**
- TP 표시: `--%`
- SL 표시: `--%`

### 3.3 ON 전환 시 UI
- TP 입력 필드 활성화
- SL 입력 필드 활성화
- Save 버튼 활성화

### 3.4 입력 범위 (유효 값)

| 항목 | 최솟값 | 최댓값 | 단위 | 소수점 |
|------|--------|--------|------|--------|
| TP (Take Profit) | 0.1% | 999.9% | % (양수) | 소수점 1자리까지 허용 |
| SL (Stop Loss) | 0.1% | 99.9% | % (양수 입력, 내부적으로 마이너스) | 소수점 1자리까지 허용 |

> **주의:** SL은 UI 상 양수로 입력받으나 내부적으로 손실 비율로 처리됨.
> 입력값 `5` → SL -5% (5% 손실 시 청산) 를 의미함.

### 3.5 경계값 처리

| 입력 | 처리 결과 |
|------|-----------|
| TP = 0 | 입력 불가 또는 저장 불가 (에러 처리) |
| SL = 0 | 입력 불가 또는 저장 불가 (에러 처리) |
| TP > 999.9 | 입력 제한 또는 자동 리셋 |
| SL > 99.9 | 입력 제한 또는 자동 리셋 |
| 소수점 2자리 이상 | 입력 불가 또는 반올림 |
| 음수 입력 | 입력 불가 |

### 3.6 Toast 메시지 (Settings 저장)

| 동작 | Toast 메시지 |
|------|--------------|
| Auto TP/SL OFF → ON 저장 성공 | `Auto TP/SL settings saved.` |
| Auto TP/SL ON → OFF 저장 성공 | `Auto TP/SL settings saved.` |
| 수치 변경 후 Save | `Auto TP/SL settings saved.` |
| 저장 실패 (네트워크 등) | 에러 Toast (정확한 문구 추가 필요) |

---

## 4. Trigger Price 계산 공식

```
Long 포지션:
  TP Trigger Price = 진입가 × (1 + TP% / Leverage / 100)
  SL Trigger Price = 진입가 × (1 - SL% / Leverage / 100)

Short 포지션:
  TP Trigger Price = 진입가 × (1 - TP% / Leverage / 100)
  SL Trigger Price = 진입가 × (1 + SL% / Leverage / 100)
```

**계산 예시** (Long, 진입가 $2,000 / TP +1.8% / SL -5% / 레버리지 2x):
```
TP = 2,000 × (1 + 0.018 / 2) = 2,000 × 1.009 = $2,018
SL = 2,000 × (1 - 0.05  / 2) = 2,000 × 0.975 = $1,950
```

---

## 5. TP/SL 유형별 동작 규칙

### 5.1 Partial TP/SL (OKX / Bitget / Hyperliquid)

- TP/SL 주문은 **수량 단위**로 생성됨
- 동일 방향 추가 주문 시: 새 TP/SL 주문 **추가 생성** (기존 유지)
- 반대 방향 소량 주문 시: 기존 TP/SL 유지, 수량만 감소
- 반대 방향 대량 주문 (포지션 스위칭) 시: 기존 TP/SL **전체 취소** → 새 방향으로 신규 생성

### 5.2 Full Position TP/SL (Bybit)

- TP/SL 주문은 **포지션 전체 단위**로 생성됨 (1개만 설정 가능)
- 동일 방향 추가 주문 시: 기존 TP/SL **교체** (최신 주문 기준으로 업데이트)
- 반대 방향 소량 주문 시: 기존 TP/SL 유지
- 반대 방향 대량 주문 (포지션 스위칭) 시: 기존 TP/SL **교체** → 새 방향으로 업데이트

---

## 6. Order Form — TP/SL 연동

### 6.1 Auto TP/SL ON 상태에서 주문 시
- Order Form 하단 TP/SL 항목에 **Settings에서 설정한 값이 자동으로 표시**됨
- 표시 형식: `TP: +X.X% / SL: -X.X%`
- 주문 제출 시 해당 TP/SL 값으로 자동 주문 생성

### 6.2 Auto TP/SL OFF 상태에서 주문 시
- Order Form TP/SL 항목: **빈칸 또는 미표시** 상태
- 수동으로 TP/SL 입력하지 않으면 TP/SL 주문 미생성

### 6.3 Order Form에서 TP/SL 수동 수정
- Auto TP/SL ON 상태에서도 Order Form에서 직접 수정 가능
- 수정 값으로 주문 체결 (Settings 값 우선 표시이나 수동 수정 가능)

---

## 7. Open Orders 화면 — TP/SL 표시

### 7.1 TP/SL 컬럼 존재 여부

| 거래소 | TP/SL 컬럼 | 수정 버튼 |
|--------|------------|-----------|
| OKX | ✅ | ✅ |
| Gate | ❌ | ❌ |
| Bybit | ✅ | ✅ |
| Bitget | ✅ | ❌ |
| Hyperliquid | ✅ | ❌ |

### 7.2 Open Orders TP/SL 수정 (OKX / Bybit만 해당)
- TP/SL 수정 버튼 클릭 → 수정 모달/입력창 표시
- 기존 TP/SL 취소 후 신규 TP/SL 등록 가능
- Bitget / Hyperliquid: 수정 버튼 없음 → 해당 TC `N/A` 처리
- Gate: TP/SL 컬럼 자체 없음 → 해당 TC `N/A` 처리

---

## 8. 우선순위 규칙 (Priority Override)

```
수동 TP/SL (Basic / Advanced) > Auto TP/SL
```

- 주문 폼에서 수동으로 TP/SL을 입력한 경우: 수동 입력값이 적용됨
- Auto TP/SL ON 상태라도 수동 입력이 있으면 수동 값 우선

---

## 9. 네트워크 오류 / 실패 케이스

| 케이스 | 기대 동작 |
|--------|-----------|
| 주문 체결 후 TP/SL 생성 실패 | 에러 Toast 표시, 기존 TP/SL 값은 Settings에 유지됨 |
| Settings 저장 실패 | 에러 Toast 표시, 기존에 저장된 TP/SL 값이 표시됨 |
| 네트워크 복구 후 | 최신 상태로 정상 갱신됨 |

---

## 10. TC 작성 전제 조건 패턴

### 10.1 표준 전제 조건 (Auto TP/SL)

```
GIVEN:
1. Youthmeta 파트너 코드로 회원가입한 계정으로 로그인한 상태
2. Trade 메뉴인 상태
3. [추가 조건 — 아래 중 해당하는 것 선택]
   - Auto TP/SL OFF 상태
   - Auto TP/SL ON / TP: {X}% / SL: {Y}% 설정된 상태
   - 주문 체결 완료 상태 (Position 보유)
   - Open Orders 보유 상태
```

### 10.2 Gate 전제 조건 (Auto TP/SL 관련 TC 제외 처리)

```
GIVEN:
- Gate 거래소 연결 상태
→ Auto TP/SL 관련 TC: Gate 컬럼 N/A 처리
```

---

## 11. TC 범위 및 카테고리

| 카테고리 | 세부 항목 | Phase |
|----------|-----------|-------|
| Settings 기본 상태 | 신규 계정 OFF/미표시 확인 | Phase 03 |
| Settings 전환 | ON/OFF 전환, 수치 저장 | Phase 03 |
| 주문 연동 | Order Form TP/SL 자동 표시, 주문 시 자동 생성 | Phase 05~06 |
| 포지션 화면 | Trigger Price 검증, TP/SL 컬럼 확인 | Phase 07~09 |
| 추가 주문 | 동일 방향/반대 방향 추가 주문 시 TP/SL 동작 | Phase 10~12 |
| 수동 수정 | Open Orders TP/SL 수정/삭제/재등록 | Phase 06 |
| 오류 | 저장 실패, 네트워크 복구 | Phase 13 |
| 경계값 | 0.1%/999.9%, 소수점, 음수 입력 | Phase 15 |

---

## 12. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| v1.0 | 2026-03-18 | 최초 작성 |
