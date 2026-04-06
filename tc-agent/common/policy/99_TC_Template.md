# TC Template — Supercycl × Youthmeta
**문서 버전:** v1.0
**기준 날짜:** 2026-03-18
**용도:** 테스트 케이스 작성 기준 템플릿 (Excel 입력 참조용)

---

## 1. 컬럼 구조 (Excel 기준)

| # | 컬럼명 | 입력 형식 | 예시 |
|---|--------|-----------|------|
| 1 | TC ID | `SPCY-{Phase}-{No}` | `SPCY-03-001` |
| 2 | 단계 | `Phase XX` | `Phase 03` |
| 3 | 대분류 | 기능 최상위 | `Settings` |
| 4 | 중분류 | 세부 기능 영역 | `Trading Preferences` |
| 5 | 소분류 | 케이스 구분 | `Auto TP/SL 기본 상태` |
| 6 | 시나리오 요약 | BDD 한 문장 (한국어) | `신규 계정 최초 진입 시 OFF 상태여야 한다` |
| 7 | 우선순위 | `P1` / `P2` / `P3` | `P1` |
| 8 | 중요도 | `High` / `Medium` / `Low` | `High` |
| 9 | GIVEN | 사전 조건 (번호 목록) | `1. Youthmeta 계정 로그인 완료...` |
| 10 | WHEN | 실행 단계 (번호 목록) | `1. Settings > Trading Preferences 진입...` |
| 11 | THEN | 기대 결과 (번호 목록) | `1. Auto TP/SL 토글: OFF 상태...` |
| 12 | 실제 결과 | 테스터 기록 (빈칸) | _(빈칸)_ |
| 13 | Tester 1 | `Pass` / `Fail` / `N/T` / `N/A` | `N/T` |
| 14 | Tester 2 | `Pass` / `Fail` / `N/T` / `N/A` | `N/T` |
| 15 | Gate | `Pass` / `Fail` / `N/T` / `N/A` | `N/T` |
| 16 | OKX | `Pass` / `Fail` / `N/T` / `N/A` | `N/T` |
| 17 | Bybit | `Pass` / `Fail` / `N/T` / `N/A` | `N/T` |
| 18 | Bitget | `Pass` / `Fail` / `N/T` / `N/A` | `N/T` |
| 19 | Hyperliquid | `Pass` / `Fail` / `N/T` / `N/A` | `N/T` |
| 20 | 비고 | 거래소별 예외/참고 | `Gate: 해당 기능 없음 (N/A)` |

---

## 2. 판정 코드 정의

| 코드 | 의미 |
|------|------|
| **Pass** | 기대 결과와 일치하여 통과 |
| **Fail** | 기대 결과와 불일치 → 버그 리포트 작성 필요 |
| **N/T** | Not Tested — 미테스트 (기본 초기값) |
| **N/A** | Not Applicable — 해당 거래소/조건에 적용 불가 |

---

## 3. TC 작성 원칙

### 3.1 GIVEN (사전 조건)
- 로그인 계정 유형 명시: `Youthmeta 파트너 코드로 가입한 계정` 또는 `일반 계정`
- 현재 화면 상태 명시: `Trade 메뉴 진입 상태`, `Settings 화면 진입 상태`
- 사전 설정값 명시: `Auto TP/SL ON / TP: 1.8% / SL: 5%`
- 포지션/오더 상태 명시: `Open Orders 없음`, `Long 포지션 보유 상태`

### 3.2 WHEN (테스트 단계)
- 번호 매긴 단계별 기술 (1. 2. 3. ...)
- UI 요소는 정확한 라벨 사용: `[Save]`, `[I Understand]`, `Auto TP/SL 토글`
- URL 포함 시 명시: `https://aggr-dev.supercycl.io/?partner=Youthmeta 접속`
- 거래소별 분기: `*OKX: 수정 버튼 클릭` 형식

### 3.3 THEN (기대 결과)
- 번호 매긴 결과 항목 (1. 2. 3. ...)
- 실제 UI에 표시될 정확한 텍스트 인용: `"Max leverage limited to 2x"` (큰따옴표 사용)
- Toast 메시지: 정확한 문구 기재: `"Auto TP/SL settings saved."`
- 거래소별 차이: `*Bybit: Full TP/SL로 교체됨 / *OKX: 추가 TP/SL 생성됨`

---

## 4. 샘플 TC — Auto TP/SL Settings (Phase 03)

### SPCY-03-001
| 항목 | 내용 |
|------|------|
| **TC ID** | SPCY-03-001 |
| **단계** | Phase 03 |
| **대분류** | Settings |
| **중분류** | Trading Preferences |
| **소분류** | Auto TP/SL 기본 상태 확인 |
| **시나리오** | 신규 Youthmeta 계정 최초 진입 시 Auto TP/SL이 OFF 상태여야 한다 |
| **우선순위** | P1 |
| **중요도** | High |
| **GIVEN** | 1. Youthmeta 파트너 코드로 회원가입한 계정으로 로그인한 상태<br>2. Auto TP/SL 수치를 한 번도 설정하지 않은 신규 계정인 상태 |
| **WHEN** | 1. Settings 메뉴 진입<br>2. Trading Preferences 탭 선택<br>3. Auto TP/SL 섹션 확인 |
| **THEN** | 1. Auto TP/SL 토글: **OFF** 상태로 표시됨<br>2. TP 입력 필드: `--%` 표시<br>3. SL 입력 필드: `--%` 표시<br>4. Save 버튼: 비활성화 상태 |
| **비고** | Gate: Auto TP/SL 미지원 (N/A) |

---

### SPCY-03-002
| 항목 | 내용 |
|------|------|
| **TC ID** | SPCY-03-002 |
| **단계** | Phase 03 |
| **대분류** | Settings |
| **중분류** | Trading Preferences |
| **소분류** | Auto TP/SL ON 전환 및 수치 저장 |
| **시나리오** | Auto TP/SL을 ON으로 전환하고 TP/SL 수치를 입력한 후 저장하면 설정이 유지되어야 한다 |
| **우선순위** | P1 |
| **중요도** | High |
| **GIVEN** | 1. Youthmeta 파트너 코드로 회원가입한 계정으로 로그인한 상태<br>2. Settings > Trading Preferences 화면인 상태<br>3. Auto TP/SL: OFF 상태 |
| **WHEN** | 1. Auto TP/SL 토글 클릭하여 ON으로 전환<br>2. TP 입력 필드에 `1.8` 입력<br>3. SL 입력 필드에 `5` 입력<br>4. [Save] 버튼 클릭 |
| **THEN** | 1. Toast 메시지: `"Auto TP/SL settings saved."` 표시됨<br>2. TP 필드: `1.8%` 유지됨<br>3. SL 필드: `5%` 유지됨<br>4. 페이지 새로고침 후에도 동일 값 유지됨 |
| **비고** | Gate: N/A |

---

## 5. 샘플 TC — Leverage 설정 (Phase 04)

### SPCY-04-001
| 항목 | 내용 |
|------|------|
| **TC ID** | SPCY-04-001 |
| **단계** | Phase 04 |
| **대분류** | Trade |
| **중분류** | Leverage 설정 |
| **소분류** | 코인 변경 시 자동 2x 설정 |
| **시나리오** | Youthmeta 계정에서 코인 페어 변경 시 레버리지가 자동으로 2x로 변경되어야 한다 |
| **우선순위** | P1 |
| **중요도** | High |
| **GIVEN** | 1. Youthmeta 파트너 코드로 회원가입한 계정으로 로그인한 상태<br>2. Trade 메뉴인 상태<br>3. Open Orders, Position이 없는 상태 |
| **WHEN** | 1. 코인 페어 드롭다운에서 다른 코인 페어 선택 (예: BTC/USDT → ETH/USDT) |
| **THEN** | 1. Order Form 상단 레버리지 표시: `2x`로 자동 변경됨<br>2. Adjust Leverage 모달 진입 시 레버리지: `2x`로 표시됨<br>3. 경고 배너: `"Max leverage limited to 2x"` 표시됨 (노란색) |
| **비고** | — |

---

## 6. 샘플 TC — 주문 및 TP/SL 자동 생성 (Phase 05)

### SPCY-05-001
| 항목 | 내용 |
|------|------|
| **TC ID** | SPCY-05-001 |
| **단계** | Phase 05 |
| **대분류** | Trade |
| **중분류** | 주문 (Market) |
| **소분류** | Auto TP/SL ON 상태 Market 매수 주문 |
| **시나리오** | Auto TP/SL ON 상태에서 Market 매수 주문 체결 시 TP/SL이 자동 생성되어야 한다 |
| **우선순위** | P1 |
| **중요도** | High |
| **GIVEN** | 1. Youthmeta 파트너 코드로 회원가입한 계정으로 로그인한 상태<br>2. Auto TP/SL ON / TP: 1.8% / SL: 5% 설정된 상태<br>3. 레버리지 2x 설정 상태<br>4. Open Orders, Position이 없는 상태 |
| **WHEN** | 1. Trade 메뉴 > Buy/Long 탭 선택<br>2. Order Type: Market 선택<br>3. Order Form 하단 TP/SL 확인: TP `+1.8%` / SL `-5%` 자동 표시됨<br>4. 수량 입력 후 [Buy Market] 버튼 클릭 |
| **THEN** | 1. 주문 체결됨<br>2. Position 생성됨<br>3. TP Trigger Price: `진입가 × (1 + 0.018 / 2)` 값으로 TP 주문 생성됨<br>4. SL Trigger Price: `진입가 × (1 - 0.05 / 2)` 값으로 SL 주문 생성됨<br>5. *OKX/Bitget/Hyperliquid: Open Orders에 TP/SL 주문 각각 추가됨<br>6. *Bybit: Full TP/SL 1개 생성됨 |
| **비고** | Gate: Auto TP/SL 미지원 (N/A) |

---

## 7. 샘플 TC — 경계값 (Phase 15)

### SPCY-15-001
| 항목 | 내용 |
|------|------|
| **TC ID** | SPCY-15-001 |
| **단계** | Phase 15 |
| **대분류** | Settings |
| **중분류** | Auto TP/SL 입력값 경계값 |
| **소분류** | TP 최솟값 0.1% 입력 |
| **시나리오** | TP에 최솟값 0.1%를 입력하고 저장할 수 있어야 한다 |
| **우선순위** | P2 |
| **중요도** | Medium |
| **GIVEN** | 1. Youthmeta 파트너 코드로 회원가입한 계정으로 로그인한 상태<br>2. Settings > Trading Preferences 화면인 상태<br>3. Auto TP/SL: ON 상태 |
| **WHEN** | 1. TP 입력 필드 클릭<br>2. `0.1` 입력<br>3. [Save] 버튼 클릭 |
| **THEN** | 1. 입력 허용됨<br>2. Toast: `"Auto TP/SL settings saved."` 표시됨<br>3. TP 필드: `0.1%` 저장됨 |
| **비고** | Gate: N/A |

---

## 8. TC ID 부여 규칙

```
형식: SPCY-{Phase}-{순번}

예시:
  SPCY-00A-001  (Email 가입/로그인)
  SPCY-00B-001  (Gmail 가입/로그인)
  SPCY-00C-001  (Web3 Wallet 가입/로그인)
  SPCY-01-001   (신규 가입 & 계정 태깅)
  SPCY-03-001   (Auto TP/SL Settings)
  SPCY-04-001   (Leverage 설정)
  SPCY-15-001   (경계값)
```

---

## 9. 우선순위 부여 가이드

| 등급 | 기준 |
|------|------|
| **P1 / High** | 기능 자체 동작 불가 → 출시 블로킹 이슈 |
| **P2 / Medium** | 핵심 흐름 영향 — 우회 가능하나 UX 저하 |
| **P3 / Low** | 개선 권고 — 기능 동작에는 영향 없음 |

**일반 기준:**
- 레버리지 자동 제한 동작: P1
- Auto TP/SL 자동 생성: P1
- Toast 메시지 표시: P2
- 경계값 처리: P2~P3
- UI 레이아웃/텍스트 오탈자: P3

---

## 10. N/A 처리 빠른 참고표

| 케이스 | N/A 적용 거래소 |
|--------|----------------|
| Auto TP/SL 관련 모든 TC | Gate |
| Order Form TP/SL 입력 TC | Gate |
| Open Orders TP/SL 컬럼 TC | Gate |
| Open Orders TP/SL **수정** TC (SPCY-06-006/007) | Gate, Hyperliquid, Bitget |
| Open Orders TP/SL **수정 불가 확인** TC (SPCY-06-008) | OKX, Bybit |
| TP/SL Limit 주문 관련 TC | OKX, Bybit |

---

## 11. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| v1.0 | 2026-03-18 | 최초 작성 |
