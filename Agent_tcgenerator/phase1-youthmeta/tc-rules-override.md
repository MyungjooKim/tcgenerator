# TC 작성 규칙 — Phase 1: Youthmeta (Override)

> **이 파일은 Phase 1 (Youthmeta) 전용 규칙이다.**
> `common/tc-rules.md`를 먼저 읽은 후 이 파일로 덮어씌운다.
> 이 파일에 없는 항목은 common/tc-rules.md 규칙을 따른다.

---

## Phase 1 개요

| 항목 | 내용 |
|------|------|
| Phase 코드 | P1_Youthmeta |
| 서비스 | Supercycl × Youthmeta 파트너 버전 |
| 테스트 URL | `https://aggr-dev.supercycl.io/?partner=Youthmeta` |
| 계정 조건 | `partner_code=YOUTHMETA`로 가입한 계정 |
| 핵심 기능 | 레버리지 2x 제한 + Auto TP/SL |

---

## 1. TC ID 규칙 (Override)

Phase 1은 다음 포맷을 사용한다:
```
SPCY-{PhaseNum}-{순번}
예: SPCY-03-001
```

| Phase 번호 | 기능 범위 |
|-----------|----------|
| 00A~00C | 이메일/Gmail/Web3 가입·로그인 |
| 01~02 | 신규 가입, 계정 태깅, 최초 로그인 팝업 |
| 03 | Auto TP/SL 설정 (Settings) |
| 04 | 레버리지 설정 |
| 05~06 | 주문 (Market / Limit) |
| 07 | 숏 포지션 |
| 08~12 | 수동 TP/SL, 추가 주문, 설정 변경 |
| 13 | 오류/실패 케이스 |
| 14 | 고레버리지 기존 포지션 |
| 15 | 경계값 & 동치분할 |
| 16~18 | 탐색적/회귀/비기능 테스트 |

---

## 2. 지원 거래소 및 N/A 규칙

### 거래소 목록 (Excel 컬럼 순서)

| 순서 | 거래소 | 담당 테스터 | 비고 |
|------|--------|------------|------|
| 1 | Gate | Tester 2 | Auto TP/SL 미지원 |
| 2 | OKX | Tester 1 | 인증 Phase 단독 담당 |
| 3 | Bybit | Tester 1 | Full TP/SL 방식 |
| 4 | Bitget | Tester 2 | Open Orders 수정 버튼 없음 |
| 5 | Hyperliquid | Tester 2 | Open Orders 수정 버튼 없음 |

### 테스터 배정 (2인 기준)

| 테스터 | 담당 거래소 | 특이사항 |
|--------|-----------|----------|
| Tester 1 | OKX, Bybit | 인증 Phase(00A~02)는 OKX 단독 |
| Tester 2 | Gate, Bitget, Hyperliquid | Gate는 Auto TP/SL 전체 N/A |

### 확정된 N/A 규칙

**[계정·인증 Phase — Gate/Bybit/Bitget/Hyperliquid]**
- 대상: Phase 00A / 00B / 00C / 01 / 02 전체 TC
- 적용: Gate, Bybit, Bitget, Hyperliquid → **N/A**

**[Gate — Auto TP/SL 관련 TC]**
- 대상: Phase 05 전체 / Phase 06 (001~007) / Phase 07 / Phase 08
- 이유: Gate는 Auto TP/SL 미지원
- 적용: Gate → **N/A**

**[Bitget / Hyperliquid — Open Orders TP/SL 수정]**
- 대상: SPCY-06-002, SPCY-06-006, SPCY-06-007
- 이유: 수정 버튼 없음
- 적용: Bitget, Hyperliquid → **N/A**

**[OKX / Bybit / Bitget — Open Orders 수정 불가 확인 TC]**
- 대상: SPCY-06-008 계열
- 이유: 이 TC는 Gate/Hyperliquid 수정 불가를 검증하는 TC
- 적용: OKX, Bybit, Bitget → **N/A**

> 거래소 특성 상세: `common/policy/01_TC_Policy_Exchange.md` 참조

---

## 3. 플랫폼 표기 (Override)

Phase 1은 Web 브라우저 기반이다:

| 값 | 사용 조건 |
|----|----------|
| `Web` | 기본값 (Chrome 기준) |
| `Web (Brave)` | Brave 특정 동작이 있는 경우 |
| `공통` | 플랫폼 무관 (서버 로직) |

---

## 4. 테스트 환경 (Override)

| 항목 | 내용 |
|------|------|
| 플랫폼 | Web 브라우저 |
| 주요 브라우저 | Chrome (보조: Brave) |
| OS | Windows / macOS 병행 |
| 테스트 계정 | YOUTHMETA 파트너코드로 가입한 계정 |
| 기준 환경 | `https://aggr-dev.supercycl.io/?partner=Youthmeta` |

---

## 5. 파일명 규칙 (Override)

```
SPCY_TC_P1_Youthmeta_{YYYYMMDD}_v{N}.xlsx
예: SPCY_TC_P1_Youthmeta_20260323_v1.xlsx
```
