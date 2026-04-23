# Supercycl — 크로스 플랫폼 TC 네이밍 정책

> PC Web / Mobile Web / Mobile App 간 TC 용어 통일 규칙
> TC Generator 프로그램에서 TC를 생성할 때 이 정책을 반드시 따라야 합니다.

---

## 1. 원칙

- **동일 서비스의 플랫폼 변형**이므로 기획/디자인/개발/QA가 사용하는 **용어는 통일**한다.
- Suite명, 대분류, 중분류는 **PC Web TC와 동일한 이름**을 사용한다.
- 소분류는 플랫폼별 UI 차이를 반영하여 다를 수 있다.
- TC ID의 ProjectCode + SuiteCode는 동일하되, **플랫폼 식별자**로 구분한다.

---

## 2. TC ID 플랫폼 식별

### 형식

```
{ProjectCode}-{SuiteCode}-{SeqNumber}
```

### 플랫폼별 ProjectCode

| 플랫폼 | ProjectCode | 예시 |
|--------|-------------|------|
| PC Web | `SC` | SC-TRD-ACCT-001 |
| Mobile Web | `SM` | SM-TRD-ACCT-001 |
| Mobile App (향후) | `SA` | SA-TRD-ACCT-001 |

### SuiteCode는 플랫폼 간 동일

```
PC Web:     SC-LOGN-001    (Suite: LOGN)
Mobile Web: SM-LOGN-001    (Suite: LOGN)
→ 같은 Suite 코드, 같은 기능 영역
```

---

## 3. 시트명 규칙

### 시트명 = `{대분류}-{중분류}`

시트명은 **대분류와 중분류를 하이픈으로 연결**하여 구성한다.

```
시트명: Trade-Lite
  → 대분류: Trade
  → 중분류: Lite

시트명: Trade-Order
  → 대분류: Trade
  → 중분류: Order

시트명: 로그인-Google
  → 대분류: 로그인
  → 중분류: Google
```

### 거래소별 분기

거래소 전용 TC는 시트명 뒤에 `(거래소명)` 접미사를 붙인다.

```
Trade-Order              → 공통 TC (모든 거래소)
Trade-Order(Hyperliquid) → Hyperliquid 전용 TC
Trade-Order(OKX,Bybit)   → OKX, Bybit 공유 TC
```

### 공통 시트 목록 (PC Web과 동일 이름 사용)

| 시트명 | 대분류 | 중분류 | 설명 |
|--------|--------|--------|------|
| Trade-Account Info | Trade | Account Info | 계좌 정보, 잔고, PnL |
| Trade-Deposit&Withdraw | Trade | Deposit&Withdraw | 입출금 |
| Trade-Coin Info | Trade | Coin Info | 코인 정보, 펀딩비 |
| Trade-Chart | Trade | Chart | 차트 |
| Trade-Orderbook | Trade | Orderbook | 호가창 |
| Trade-MarginMode | Trade | MarginMode | 마진 모드 |
| Trade-Leverage | Trade | Leverage | 레버리지 |
| Trade-Order | Trade | Order | 주문 |
| Trade-TP/SL | Trade | TP/SL | TP/SL 설정 |
| Trade-Positions | Trade | Positions | 포지션 목록 |
| Trade-Close | Trade | Close | 포지션 청산 |
| Trade-Open_Orders | Trade | Open_Orders | 미체결 주문 |
| Trade-Order_History | Trade | Order_History | 주문 내역 |
| 접속 | 접속 | 공통 | 서비스 접속, URL |
| GNB&Footer | GNB | Footer | 네비게이션, 푸터 |
| 로그인 | 로그인 | 공통 | 로그인/로그아웃, OAuth |
| Settings | Settings | 공통 | 설정, 프로필 |

### PC Web 전용 (Mobile Web 해당 없음)

| 시트명 | 이유 |
|---------|------|
| Landing Page | PC 전용 랜딩 페이지 |
| Youthmeta | 파트너 전용 |
| CBT_Whitelist | CBT 전용 |

### Mobile Web 전용 (신규 추가 가능)

| 시트명 | 대분류 | 중분류 | 설명 |
|--------|--------|--------|------|
| Mobile-Navigation | Mobile | Navigation | 하단 탭바, 햄버거 메뉴 |
| Mobile-Gesture | Mobile | Gesture | 스와이프, 풀다운 리프레시 |
| Mobile-Responsive | Mobile | Responsive | 해상도별 레이아웃 |

---

## 4. 대분류 이름 통일

### 규칙

- PC Web TC의 대분류 이름을 **그대로 사용**한다.
- 대소문자, 공백, 특수문자 모두 동일하게 맞춘다.
- 모바일 전용 대분류 추가 시 `[Mobile]` 접두사는 붙이지 않는다 (Suite로 구분).

### 예시 (PC Web과 동일하게 사용)

```
Suite: 로그인
  대분류: 접속                  ← PC/Mobile 동일
  대분류: 로그인 동작            ← PC/Mobile 동일
  대분류: Log in               ← PC/Mobile 동일
  대분류: Wallet 로그인          ← PC/Mobile 동일

Suite: Trade-Order
  대분류: 공통                  ← PC/Mobile 동일
  대분류: Market Order          ← PC/Mobile 동일
  대분류: Limit Order           ← PC/Mobile 동일
  대분류: Conditional Order     ← PC/Mobile 동일
```

---

## 5. 중분류 이름 통일

### 규칙

- PC Web TC의 중분류 이름을 **그대로 사용**한다.
- 모바일에서 동일 기능이 다른 UI로 제공되더라도 **중분류 이름은 통일**한다.

### 예시

```
Suite: Trade-Account Info
  대분류: 거래소 연동 후
    중분류: Total Equity        ← PC/Mobile 동일
    중분류: 정보 표시            ← PC/Mobile 동일

Suite: Trade-Close
  대분류: Close
    중분류: 청산 공통            ← PC/Mobile 동일
    중분류: Market Close        ← PC/Mobile 동일
    중분류: Limit Close         ← PC/Mobile 동일
```

---

## 6. 소분류 — 플랫폼별 차이 허용

### 규칙

- 소분류는 **플랫폼별 UI 차이를 반영**하여 다를 수 있다.
- PC Web에서 사용하는 소분류가 모바일에도 해당되면 동일 이름 사용.
- 모바일 전용 소분류는 자유롭게 추가.

### 예시

```
Suite: Trade-Order, 대분류: Market Order, 중분류: 매수

PC Web 소분류:
  - 수량 입력
  - 슬라이더
  - 주문 확인 모달

Mobile Web 소분류:
  - 수량 입력           ← 동일
  - 슬라이더           ← 동일
  - 주문 확인 바텀시트    ← 모바일 전용 (PC의 "모달" → 모바일의 "바텀시트")
  - 스와이프 주문        ← 모바일 전용
```

---

## 7. 거래소 분기 규칙

- PC Web과 동일한 거래소 분기 패턴을 따른다.
- 거래소 코드: Bitget, Gate, Hyperliquid, Bybit, OKX
- 거래소별 차이가 있는 TC는 `관련 거래소` 컬럼에 표기

---

## 8. 사전 조건 작성 규칙

### 플랫폼 명시

- Mobile Web TC의 사전 조건에는 **모바일 브라우저 환경**을 명시한다.

```
PC Web:
  1. Chrome 브라우저에서 Supercycl 접속한 상태
  2. 로그인 완료 상태

Mobile Web:
  1. 모바일 브라우저(iOS Safari / Android Chrome)에서 Supercycl 접속한 상태
  2. 로그인 완료 상태
```

### 해상도/디바이스 조건

```
  1. iPhone 15 Pro (390x844) 기준 모바일 브라우저에서 접속한 상태
  또는
  1. 모바일 브라우저에서 Supercycl 접속한 상태 (화면 너비 480px 이하)
```

---

## 9. TC Generator 적용 규칙 요약

TC Generator에서 Supercycl Mobile Web TC를 생성할 때:

1. **ProjectCode**: `SM` 사용 (PC Web의 `SC`와 구분)
2. **SuiteCode**: PC Web과 동일한 코드 사용 (LOGN, TRD-ACCT, TRD-ORDR 등)
3. **대분류/중분류 이름**: `tc_category_reference.md`의 이름과 **정확히 일치**시킬 것
4. **소분류**: 모바일 UI에 맞게 자유 작성 (PC와 동일한 기능이면 동일 이름 유지)
5. **사전 조건**: "모바일 브라우저에서 접속한 상태" 포함
6. **거래소 분기**: PC Web과 동일 패턴
7. **Smoke Test**: 아래 10절의 Smoke 선별 기준을 따른다
8. **SeqNumber 전역 유니크**: 한 Suite 내 모든 중분류에 걸쳐 NNN은 연속 증가. 중분류가 바뀔 때 001로 리셋 금지 (기존 `SM-ONBD-001` × 4회 중복 버그 방지).
9. **스펙 기반 생성**: `common/tc-rules.md` 섹션 1-1, 1-2 원칙을 최우선 준수. 스펙 에러 케이스 테이블은 1:1 매핑, 추측 기반 Edge/Offline TC 금지.

### 모바일 TC 생성 체크리스트 (Pre-flight)

TC 작성 전 반드시 스펙(기획서)에서 확인:

- [ ] 화면 `상태 (status)`가 `active`인가? (`deferred`/`archived`는 제외)
- [ ] 해당 화면의 `에러 케이스` 테이블이 있는가? (있으면 1:1 매핑, 없으면 Negative TC 생성 금지)
- [ ] Impact 수준 (자산=5 / 보안=4 / 데이터=3 / 설정=2 / 브랜딩=1)에 맞는 쿼터인가?
- [ ] 시각 속성(색·폰트·radius)은 화면당 1개 "UI Spec Compliance" TC로 통합했는가?
- [ ] 오프라인/타임아웃/성능 임계치는 스펙 명시가 있을 때만 생성했는가?

---

## 10. Smoke Test 선별 기준

### 목적

새 빌드 배포 직후, 핵심 기능이 기본적으로 동작하는지 빠르게 확인하기 위한 TC 세트.
전체 TC의 **20~30%** 를 목표로 선별한다.

### 선별 로직 (우선순위 순)

| 순서 | 조건 | 선별 개수 | 설명 |
|------|------|----------|------|
| 1 | **중분류별 대표 Positive 1개** | 중분류당 1개 | 우선순위 High > Medium > Low 순으로 Positive TC를 1개 선별. 해당 중분류의 핵심 정상 흐름을 대표한다. |
| 2 | **중분류별 High Negative 1개** | 중분류당 최대 1개 | 우선순위 High인 Negative TC만 선별. 서비스 진입 차단, 권한 오류 등 핵심 실패 시나리오를 커버한다. 해당 중분류에 High Negative가 없으면 건너뛴다. |
| 3 | **대분류별 최소 1개 보장** | 대분류당 최소 1개 | 위 1, 2 조건으로 선별된 TC가 하나도 없는 대분류가 있으면, 해당 대분류의 첫 번째 TC를 Smoke로 포함한다. 모든 기능 영역이 최소 1개는 커버되도록 보장. |

### 선별 흐름

```
전체 TC
  │
  ├─ 중분류별 그룹핑
  │    │
  │    ├─ [1] Positive 중 우선순위 가장 높은 TC 1개 → Smoke ✓
  │    │
  │    └─ [2] High + Negative TC 1개 (있으면) → Smoke ✓
  │
  └─ 대분류별 검증
       │
       └─ [3] Smoke가 0개인 대분류 → 첫 TC 1개 → Smoke ✓
```

### 예시

```
Suite: Trade-Order (중분류 3개)
  ├─ 중분류: 시장가
  │    ├─ SC-TRD-ORDR-001  High   Positive  → Smoke ✓ (대표 Positive)
  │    ├─ SC-TRD-ORDR-002  Medium Positive
  │    └─ SC-TRD-ORDR-003  High   Negative  → Smoke ✓ (핵심 Negative)
  │
  ├─ 중분류: 지정가
  │    ├─ SC-TRD-ORDR-004  High   Positive  → Smoke ✓ (대표 Positive)
  │    └─ SC-TRD-ORDR-005  Medium Negative
  │
  └─ 중분류: 조건부
       ├─ SC-TRD-ORDR-006  Medium Positive  → Smoke ✓ (High 없으므로 Medium)
       └─ SC-TRD-ORDR-007  Low    Edge

→ 전체 7개 중 Smoke 4개 (57%) — 중분류 3개 모두 커버
```

### 분류(Positive/Negative/Edge) 값

Smoke 선별에 사용되는 분류 값은 TC 마크다운의 `분류` 필드에서 추출된다.
Excel 출력에는 분류 컬럼이 표시되지 않지만, 내부 데이터로 보존되어 Smoke 선별과 통계에 활용된다.

| 분류 | 의미 | Smoke 대상 |
|------|------|-----------|
| Positive | 정상 흐름 (Happy Path) | 중분류당 1개 선별 |
| Negative | 오류/실패 흐름 | High일 때만 중분류당 1개 |
| Edge | 경계값/예외 흐름 | Smoke 대상 아님 |

---

## 11. 용어 사전 (PC/Mobile 공통)

| 용어 | 의미 | 사용 위치 |
|------|------|----------|
| Total Equity | 총 자산 (USDC + Unrealized PnL) | Account Info |
| Available to Trade | 주문 가능 잔고 | Account Info |
| Unrealized P&L | 미실현 손익 | Account Info, Positions |
| Margin Mode | 마진 모드 (Cross/Isolated) | MarginMode |
| Leverage | 레버리지 배수 | Leverage |
| Market Order | 시장가 주문 | Order |
| Limit Order | 지정가 주문 | Order |
| Conditional Order | 조건부 주문 | Order |
| Take Profit | 이익 실현 가격 | TP/SL |
| Stop Loss | 손절 가격 | TP/SL |
| Funding Rate | 펀딩비 | Coin Info |
| Position Mode | Net Mode / Hedge Mode | PositionMode |
| Orderbook | 호가창 (Asks/Bids) | Orderbook |
