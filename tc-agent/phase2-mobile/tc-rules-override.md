# TC 작성 규칙 — Phase 2: 모바일 체험 (Override)

> **이 파일은 Phase 2 (모바일 체험 서비스) 전용 규칙이다.**
> `common/tc-rules.md`를 먼저 읽은 후 이 파일로 덮어씌운다.

---

## Phase 2 개요

| 항목 | 내용 |
|------|------|
| Phase 코드 | P2_Mobile |
| 서비스 | Supercycl 모바일 체험 |
| 계정 조건 | YOUTHMETA 파트너코드로 가입한 체험용 계정 |
| 핵심 기능 | 모바일 브라우저 기반 체험 서비스 (Hyperliquid Testnet) |

---

## 1. TC ID 규칙 (Override)

Phase 2는 도메인 기반 포맷을 사용한다:
```
[도메인코드]-[기능코드]-[번호]
예: AUTH-OAUTH-001, LEVR-POPUP-001
```

도메인 코드는 `common/tc-rules.md`의 목록을 따른다.

---

## 2. 지원 거래소 및 N/A 규칙

Phase 2는 **단일 거래소(Hyperliquid Testnet)** 기반이다.
별도 거래소 컬럼 없음. 판정 컬럼 = Hyperliquid 단일 컬럼.

| 항목 | 내용 |
|------|------|
| 거래소 | Hyperliquid Testnet |
| API | api.hyperliquid-testnet.xyz |
| Chain ID | 998 |
| 초기 자금 | 10,000 USDC (마스터 지갑 자동 지급) |
| 테스터 배정 | Phase 2는 단일 테스터 또는 팀 내 배정 (별도 지정) |

> 향후 거래소가 추가될 경우 이 파일을 업데이트한다.

---

## 3. 플랫폼 표기 (Override)

Phase 2는 모바일 브라우저 기반이다:

| 값 | 사용 조건 |
|----|----------|
| `Web(Mobile)` | **기본값** — 모바일 브라우저 |
| `iOS Safari` | iOS Safari 특정 동작이 있는 경우 |
| `Android Chrome` | Android Chrome 특정 동작이 있는 경우 |
| `공통` | 플랫폼 무관 (서버 로직, 데이터 검증) |

---

## 4. 테스트 환경 (Override)

| 항목 | 내용 |
|------|------|
| 플랫폼 | Web (모바일 브라우저) |
| 주요 브라우저 | iOS Safari, Android Chrome |
| 뷰포트 | 375px 기준 모바일 |
| 테스트 계정 | YOUTHMETA 파트너코드로 가입한 체험용 계정 |
| 기준 환경 | Hyperliquid Testnet |

---

## 5. 파일명 규칙 (Override)

```
SPCY_TC_P2_Mobile_{YYYYMMDD}_v{N}.xlsx
예: SPCY_TC_P2_Mobile_20260402_v1.xlsx
```

---

## 6. [미결] 항목

| 항목 | 내용 |
|------|------|
| 초기 지급 잔고 | PDF 기준 1,000 USDC / 코드 기준 10,000 USDC — 확정 필요 |
| LeverageNotice 팝업 언어 | 한국어/영어 미확정 |
| LeverageNotice 노출 조건 | 최초 1회 / 매 로그인마다 미확정 |
