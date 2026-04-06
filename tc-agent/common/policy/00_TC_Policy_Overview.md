# TC Policy Overview — Supercycl × Youthmeta
**문서 버전:** v1.1
**기준 날짜:** 2026-03-18
**작성 범위:** YouthMeta Partner Version — Leverage 2x 제한 + Auto TP/SL 기능

---

## 1. 테스트 목적 및 범위

### 1.1 대상 기능
| 기능 | 설명 |
|------|------|
| Youthmeta Leverage 2x | 레퍼럴 파트너 계정 레버리지 2배 고정 정책 |
| Auto TP/SL | TP/SL 자동 설정 기능 (Youthmeta 계정 전용) |

### 1.2 테스트 접근법
- **방법론:** 블랙박스 테스트 (Black-Box Testing)
- **순서:** User Journey 기반 순차 진행 (가입 → 설정 → 주문 → 포지션)
- **스타일:** BDD (Given / When / Then) 형식
- **우선도:** Risk-Based 우선순위 적용

### 1.3 테스트 환경
- **테스트 URL:** `https://aggr-dev.supercycl.io/?partner=Youthmeta`
- **OS:** Windows / macOS 병행 테스트
- **브라우저:** Chrome 기준 (보조: Brave)

---

## 2. 계정 준비 방법

### 2.1 Youthmeta 계정 신규 등록
1. 한 번도 로그인하지 않은 신규 계정 준비
   - 또는 기존 계정을 미등록 처리 → master account로 미등록 요청
2. `https://aggr-dev.supercycl.io/?partner=Youthmeta` 접속
3. 최초 로그인 시 Youthmeta 파트너 계정으로 자동 등록

### 2.2 파트너 코드 등록 확인 방법 (API)
브라우저 Network 탭 > `info` API 응답 확인:

```json
// 등록된 경우
"partner": {
  "no": 1,
  "name": "Youthmeta",
  "code": "Youthmeta"
}

// 미등록 계정
"partner": null
```

---

## 3. TC ID 체계

### 3.1 ID 포맷
```
SPCY-{Phase}-{순번}
```

| 구분 | 예시 | 설명 |
|------|------|------|
| Phase 00A | `SPCY-00A-001` | Email 가입/로그인 |
| Phase 00B | `SPCY-00B-001` | Gmail 가입/로그인 |
| Phase 00C | `SPCY-00C-001` | Web3 Wallet 가입/로그인 |
| Phase 01 | `SPCY-01-001` | 신규 가입 & 계정 태깅 |
| Phase 02 | `SPCY-02-001` | 최초 로그인 & 팝업 |
| Phase 03 | `SPCY-03-001` | Auto TP/SL 설정 (Settings) |
| Phase 04 | `SPCY-04-001` | 레버리지 설정 |
| Phase 05~06 | `SPCY-05-001` | 주문 (Market / Limit) |
| Phase 07 | `SPCY-07-001` | 숏 포지션 |
| Phase 08~12 | `SPCY-08-001` | 수동 TP/SL, 추가 주문, 설정 변경 |
| Phase 13 | `SPCY-13-001` | 오류/실패 케이스 |
| Phase 14 | `SPCY-14-001` | 고레버리지 기존 포지션 |
| Phase 15 | `SPCY-15-001` | 경계값 & 동치분할 |
| Phase 16 | `SPCY-16-001` | 탐색적 테스트 |
| Phase 17 | `SPCY-17-001` | 회귀 테스트 |
| Phase 18 | `SPCY-18-001` | 비기능 테스트 |

### 3.2 결과물 파일명 규칙

TC 빌드 결과물(Excel) 파일명은 다음 형식을 따른다:

```
SPCY_TC_SmokeTest_년월일_v{n}
```

| 구성 요소 | 설명 | 예시 |
|-----------|------|------|
| `SPCY` | 프로젝트 접두사 (고정) | `SPCY` |
| `TC` | 테스트 케이스 식별자 (고정) | `TC` |
| `SmokeTest` | 테스트 유형 | `SmokeTest` |
| `년월일` | 빌드 날짜 (YYYYMMDD 형식) | `20260323` |
| `v{n}` | 해당 날짜의 빌드 버전 (1부터 시작) | `v1`, `v2` |

**예시:**
```
SPCY_TC_SmokeTest_20260323_v1.xlsx
SPCY_TC_SmokeTest_20260323_v2.xlsx   ← 같은 날 재빌드 시
SPCY_TC_SmokeTest_20260324_v1.xlsx   ← 다음 날 새 빌드
```

**버전 증가 규칙:**
- 같은 날짜에 결과물이 이미 존재하면 `v{n}`을 1씩 증가
- 날짜가 바뀌면 `v1`부터 다시 시작

---

## 4. TC 컬럼 구조

### 4.1 컬럼 정의 (통합 Excel 기준) — v8, 총 18컬럼

| # | 컬럼명 | 설명 | 예시 |
|---|--------|------|------|
| 1 | TC ID | SPCY-{Phase}-{No}. ★ 접두사 = 최소 TC 세트 | ★ SPCY-03-001 |
| 2 | 단계 | Phase 번호 | Phase 03 |
| 3 | 대분류 | 기능 최상위 분류 | Settings |
| 4 | 중분류 | 세부 기능 영역 | Trading Preferences |
| 5 | 소분류 | 개별 케이스 구분 | Auto TP/SL 기본 상태 |
| 6 | 시나리오 요약 | BDD 한 문장 요약 | 신규 계정 최초 진입 시 OFF 상태여야 한다 |
| 7 | 우선순위 | P1 / P2 / P3 | P1 |
| 8 | 중요도 | High / Medium / Low | High |
| 9 | GIVEN (사전 조건) | 테스트 시작 전 상태 | Youthmeta 계정 로그인 완료 |
| 10 | WHEN (테스트 단계) | 번호 매긴 실행 절차 | 1. Settings > Trading Preferences 진입... |
| 11 | THEN (기대 결과) | 기대하는 결과 (UI 텍스트 포함) | OFF 상태, TP: -% / SL: -% 표시 |
| 12 | 실제 결과 | 테스터 기록 칸 (빈칸) | |
| 13 | Gate | Pass / Fail / N/T / N/A — **Tester 2 담당** | N/T |
| 14 | OKX | Pass / Fail / N/T / N/A — **Tester 1 담당** | N/T |
| 15 | Bybit | Pass / Fail / N/T / N/A — **Tester 1 담당** | N/T |
| 16 | Bitget | Pass / Fail / N/T / N/A — **Tester 2 담당** | N/T |
| 17 | Hyperliquid | Pass / Fail / N/T / N/A — **Tester 2 담당** | N/T |
| 18 | 비고 | 거래소별 예외, 참고사항 | Gate: 해당 기능 없음 |

> **거래소 컬럼 = 판정 컬럼:** 별도 Tester 1/Tester 2 판정 컬럼 없음.
> 각 테스터는 자신이 담당하는 거래소 컬럼에 직접 Pass/Fail/N/T를 기입한다.
> Excel Row 2(서브헤더)에 테스터 배정이 색상으로 표시된다 (초록=Tester 1, 파랑=Tester 2).

### 4.1.1 테스터 배정 기준 (기본값)

| 거래소 | 담당 테스터 | 비고 |
|--------|------------|------|
| Gate | Tester 2 | Auto TP/SL 미지원 거래소 |
| OKX | Tester 1 | 최초 테스트 거래소 (계정/인증 TC 단독 담당) |
| Bybit | Tester 1 | Full TP/SL 방식 |
| Bitget | Tester 2 | Partial TP/SL, 수정 버튼 없음 |
| Hyperliquid | Tester 2 | Partial TP/SL, 수정 버튼 없음 |

> 테스터가 1명일 경우 모든 거래소 컬럼을 1인이 담당하며 서브헤더 배정은 참고용으로만 사용.
> 테스터가 4명일 경우 거래소 단위로 분배하거나 Phase 단위로 분배 후 비고 컬럼에 명시.

### 4.2 판정 코드 정의
| 코드 | 의미 |
|------|------|
| **Pass** | 기대 결과와 일치하여 통과 |
| **Fail** | 기대 결과와 불일치, 버그 리포트 작성 필요 |
| **N/T** | Not Tested — 미테스트 (기본 초기값) |
| **N/A** | Not Applicable — 해당 거래소/조건에 적용 불가 |

---

## 4.3 N/A 적용 정책 (거래소별 판정 컬럼)

### 원칙
거래소가 해당 기능을 지원하지 않거나 TC 자체가 다른 거래소를 대상으로 작성된 경우, 해당 거래소 판정 컬럼을 **N/A**로 사전 기입한다. N/A 셀은 회색(#E0E0E0)으로 표시되며 테스터가 별도 기입할 필요가 없다.

### 현재 확정된 N/A 규칙 (v8 기준)

**[계정·인증 Phase — Gate/Bybit/Bitget/Hyperliquid]**
- 대상: Phase 00A / 00B / 00C / 01 / 02 전체 TC
- 이유: 계정 생성·파트너 태깅·팝업은 거래소 독립적 기능. 최초 거래소(OKX)로만 검증.
- 적용: Gate, Bybit, Bitget, Hyperliquid → **N/A**

**[Gate — Auto TP/SL 관련 TC]**
- 대상: Phase 05 전체 / Phase 06 (06-001~007) / Phase 07 / Phase 08
- 이유: Gate는 Auto TP/SL 기능 자체를 미지원. TP/SL 컬럼 없음.
- 적용: Gate → **N/A**

**[Bitget / Hyperliquid — 미체결 TP/SL 수정]**
- 대상: SPCY-06-002 (미체결 주문 TP/SL 수정)
- 이유: Bitget/Hyperliquid는 Open Orders TP/SL 수정 버튼 없음.
- 적용: Bitget, Hyperliquid → **N/A**

**[Gate / Bitget / Hyperliquid — Open Orders TP/SL 수정·추가]**
- 대상: SPCY-06-006 / SPCY-06-007
- 이유: Gate=컬럼 없음, Bitget/HL=수정·추가 버튼 없음.
- 적용: Gate, Bitget, Hyperliquid → **N/A**

**[OKX / Bybit / Bitget — Open Orders TP/SL 수정 불가 확인]**
- 대상: SPCY-06-008
- 이유: 이 TC는 Gate / Hyperliquid의 수정 불가를 확인하는 TC. OKX/Bybit/Bitget은 해당 없음.
- 적용: OKX, Bybit, Bitget → **N/A**

### 신규 기능 기획 시 N/A 적용 방법

기획서에 **"특정 거래소 해당 기능 제외"** 명시가 있을 경우:

1. TC 작성 시 해당 거래소 판정 컬럼을 **N/A**로 지정
2. `build_tc_vX.py` 스크립트의 `EXCHANGE_NA` 딕셔너리에 추가:
   ```python
   EXCHANGE_NA["SPCY-XX-YYY"] = ["Gate", "Bitget"]   # 제외 거래소 명시
   ```
3. TC 비고 컬럼에 이유 기재: `"Gate: [기능명] 미지원 (N/A)"`
4. 해당 정보를 관련 Policy .md 파일에 업데이트

### 최소 TC 세트 (★ 마크)

TC ID 앞에 **★** 가 붙은 항목은 리스크 기반 필수 최소 세트다.
- P1/High 중심의 Happy Path + 거래소별 핵심 동작 차이 검증 TC
- 별도 **'🎯 최소 TC 세트'** 시트에 선별 목록 제공 (전체 134개 → 최소 53개)
- 일정/리소스 제약 시 ★ TC를 우선 수행

---

## 5. 우선순위 정의

| 등급 | 코드 | 기준 |
|------|------|------|
| 최우선 | **P1 / High** | 블로킹 이슈 — 기능 자체가 동작 불가 시 출시 불가 |
| 중간 | **P2 / Medium** | 핵심 흐름 영향 — 우회는 가능하나 UX 저하 |
| 낮음 | **P3 / Low** | 개선 권고 — 기능 동작에는 영향 없음 |

---

## 6. 테스터 배정 원칙

- **거래소 컬럼 = 판정 컬럼:** 각 테스터는 담당 거래소 컬럼에 직접 기입
- **기본 배정:** Tester 1 (OKX/Bybit) · Tester 2 (Gate/Bitget/Hyperliquid)
- **확장 배정:** 4인 시 거래소별 1:1 담당 또는 Phase 단위 분담 후 비고에 명시

### 6.1 2인 배정 기준 (v8 기본값)

| 역할 | 담당 거래소 | 특이사항 |
|------|-----------|----------|
| Tester 1 | OKX, Bybit | 계정/인증 Phase(00A~02)는 OKX 단독 테스트 |
| Tester 2 | Gate, Bitget, Hyperliquid | Gate는 Auto TP/SL 관련 TC 전체 N/A |

> 테스터 배정 변경 시: `scripts/build_tc_vX.py`의 `TESTER_ASSIGNMENT` 딕셔너리 수정 후 빌드 재실행

---

## 7. 테스트 케이스 작성 원칙

### 7.1 GIVEN — 사전 조건 작성 기준
- 로그인 계정 유형 명시 (Youthmeta / 일반 계정 구분)
- 현재 화면/메뉴 상태 명시
- 필요한 사전 설정값 명시 (Auto TP/SL ON/OFF, 수치 등)
- 거래소 특성 관련 조건 명시

### 7.2 WHEN — 테스트 단계 작성 기준
- 번호 매긴 단계별 기술 (1. 2. 3. ...)
- UI 요소 이름은 정확한 라벨 사용 (버튼명, 탭명 등)
- 거래소별 분기가 있을 경우 `*거래소명` 형식으로 표기
- URL 포함 가능

### 7.3 THEN — 기대 결과 작성 기준
- 번호 매긴 결과 항목 (1. 2. 3. ...)
- 실제 UI에 표시될 정확한 텍스트 인용 (따옴표 사용)
- 거래소별 차이는 명확히 구분 기술
- Toast 메시지는 정확한 문구 기재

### 7.4 거래소 N/A 처리 기준
특정 거래소에서 해당 기능이 없거나 미지원인 경우 판정 셀에 `N/A` 기입:

| 상황 | 처리 방법 |
|------|-----------|
| Gate — Auto TP/SL 미지원 | Gate 컬럼 전체 N/A |
| Gate — Open Orders TP/SL 컬럼 없음 | 해당 TC의 Gate N/A |
| Hyperliquid/Bitget — Open Orders 수정 버튼 없음 | 해당 TC의 Hyperliquid/Bitget N/A |
| 기능 자체가 없는 케이스 | 해당 TC 전체를 별도 검증 TC로 분리 |

---

## 8. Policy 파일 체계

| 파일명 | 내용 |
|--------|------|
| `00_TC_Policy_Overview.md` | **이 문서** — 전체 작성 기준 및 구조 |
| `01_TC_Policy_Exchange.md` | 거래소별 특성 및 공통/차이 정리 |
| `02_TC_Policy_Leverage.md` | Youthmeta 레버리지 2x 정책 상세 |
| `03_TC_Policy_AutoTPSL.md` | Auto TP/SL 기능 정책 상세 |
| `99_TC_Template.md` | TC 작성용 샘플 템플릿 |

> **신규 기능 추가 시:** 해당 기능 번호에 맞는 Policy 파일 신규 생성
> **거래소 추가 시 (Binance 등):** `01_TC_Policy_Exchange.md` 업데이트

---

## 9. 용어 정의

| 용어 | 설명 |
|------|------|
| Youthmeta 계정 | `partner_code=YOUTHMETA`가 태깅된 계정 |
| 일반 계정 | 파트너 코드 없이 가입한 계정 |
| Partial TP/SL | 수량 단위 TP/SL (OKX/Bitget/Hyperliquid) |
| Full TP/SL | 포지션 전체 대상 TP/SL (Bybit) |
| ROI% | TP/SL 설정에 사용하는 수익률 기반 비율 |
| Trigger Price | TP/SL 주문이 실행되는 목표 가격 |
| One-Way Mode | 단방향 포지션 모드 |
| Hedge Mode | 양방향 포지션 모드 (Long/Short 독립) |
