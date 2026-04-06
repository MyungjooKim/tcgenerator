# TC 작성 규칙 — Phase 3: 모바일 확정 사양 (Override)

> **이 파일은 Phase 3 (supercycl-mockup 기반 확정 모바일 사양) 전용 규칙이다.**
> `common/tc-rules.md`를 먼저 읽은 후 이 파일로 덮어씌운다.

---

## Phase 3 개요

| 항목 | 내용 |
|------|------|
| Phase 코드 | P3_MobileMockup |
| 서비스 | Supercycl 모바일 확정 사양 (GitHub 목업 기반) |
| 소스 | https://github.com/5kyo/supercycl-mockup |
| 계정 조건 | YOUTHMETA 파트너코드로 가입한 체험용 계정 |
| 핵심 기능 | 모바일 브라우저 기반 체험 서비스 (Hyperliquid Testnet) |

---

## 1. TC ID 규칙 (Override)

Phase 3는 분류표 기반 신규 형식을 사용한다:
```
SC-{대분류코드}-{중분류코드}-{NNN}
예: SC-AUTH-LOGN-001, SC-TRAD-ORDF-001
```

`classification_v1_APPROVED.md` 기준 대분류코드/중분류코드를 반드시 사용한다.

---

## 2. 지원 거래소 및 N/A 규칙

Phase 3는 **단일 거래소(Hyperliquid Testnet)** 기반이다.
별도 거래소 컬럼 없음. 판정 컬럼 = Hyperliquid 단일 컬럼.

| 항목 | 내용 |
|------|------|
| 거래소 | Hyperliquid Testnet |
| API | api.hyperliquid-testnet.xyz |
| Chain ID | 998 |
| 초기 자금 | 100.0 USDC (constants/defaults.ts 기준) |
| 테스터 배정 | 단일 테스터 또는 팀 내 배정 (별도 지정) |

---

## 3. 플랫폼 표기 (Override)

Phase 3는 360px 고정폭 모바일 브라우저 전용이다:

| 값 | 사용 조건 |
|----|----------|
| `Web(Mobile)` | **기본값** — 360px 고정폭 모바일 브라우저 |
| `iOS Safari` | iOS Safari 특정 동작이 있는 경우 |
| `Android Chrome` | Android Chrome 특정 동작이 있는 경우 |
| `공통` | 플랫폼 무관 (서버 로직, 데이터 검증) |

---

## 4. 테스트 환경 (Override)

| 항목 | 내용 |
|------|------|
| 플랫폼 | Web (모바일 브라우저) |
| 뷰포트 | 360px 고정폭 (반응형 없음) |
| 주요 브라우저 | iOS Safari, Android Chrome |
| 테스트 계정 | YOUTHMETA 파트너코드로 가입한 체험용 계정 |
| 기준 환경 | Hyperliquid Testnet |
| 언어 설정 | EN(기본) / KR 전환 가능 |

---

## 5. 파일명 규칙 (Override)

```
SPCY_TC_P3_MobileMockup_{YYYYMMDD}_v{N}.xlsx
예: SPCY_TC_P3_MobileMockup_20260403_v1.xlsx
```

---

## 6. Phase 3 신규 기능 (Phase 2 대비)

| 신규 기능 | 설명 |
|----------|------|
| 언어 전환 (EN/KR) | Settings > Language 섹션, 전체 UI i18n 적용 |
| 포트폴리오 페이지 | 포지션 PnL 실시간 계산, 종합 수익률 표시 |
| 오더북 컴포넌트 | 거래 화면 내 호가창 표시 |
| 시그널 주문 연동 | SignalOrderSheet — 레버리지/주문유형/수량 설정 후 즉시 주문 |
| About 섹션 | Settings > About (웹사이트/문서 링크, 거래소 Coming Soon 배지) |

---

## 7. 플랫폼 특화 TC 의무 항목 (Phase 3)

Phase 3는 360px 고정폭 모바일 브라우저 전용이므로 아래 플랫폼 TC를 **반드시** 포함해야 한다.
tc-writer는 MOBL 도메인 작성 시 아래 항목을 체크리스트로 확인한다.

### 모바일 공통 필수 TC (Web(Mobile))

| TC 주제 | 검증 포인트 | 우선순위 |
|---------|-----------|---------|
| 360px 고정폭 레이아웃 | 모든 화면에서 가로 스크롤 없이 콘텐츠 표시됨 | High |
| BottomNav 고정 | 콘텐츠 스크롤 시 BottomNav가 하단에 고정 유지됨 | High |
| 바텀시트 스크롤 | CoinSelector, SignalOrderSheet 등 바텀시트 내부 스크롤 정상 동작 | High |
| 소프트 키보드 | 입력 필드(수량, 가격, 검색) 포커스 시 키보드 팝업 → 필드 가려짐 없음 | Medium |
| 터치 탭 정확도 | 주요 버튼이 인접 요소와 충분히 이격되어 오탭 없음 | Medium |

### iOS Safari 필수 TC

| TC 주제 | 검증 포인트 | 플랫폼 |
|---------|-----------|--------|
| Safari 주소창 숨김 | 스크롤 시 주소창 숨김 → BottomNav 위치 밀림 없음 | iOS Safari |
| Safe Area (홈 바) | BottomNav가 홈 바 영역과 겹치지 않음 | iOS Safari |
| iOS 키보드 처리 | iOS 키보드 팝업 시 BottomNav가 키보드 위로 올라오지 않음 | iOS Safari |

### Android Chrome 필수 TC

| TC 주제 | 검증 포인트 | 플랫폼 |
|---------|-----------|--------|
| 뒤로가기 처리 | Android 뒤로가기 시 이전 화면으로 정상 이동 (앱 종료 아님) | Android Chrome |
| Chrome 주소창 크기 변화 | 스크롤 중 Chrome 주소창 축소·확대 시 레이아웃 재조정 정상 | Android Chrome |

> **현재 Phase 3 v1 TC에는 위 항목이 미포함됨.**
> v2 빌드 시 위 항목을 MOBL 도메인에 추가한다.

---

## 8. [미결] 항목

| 항목 | 내용 |
|------|------|
| 초기 지급 잔고 | 코드 기준 100.0 USDC — 실제 지급 정책 확인 필요 |
| LeverageNotice 노출 조건 | 최초 1회 / 매 로그인마다 미확정 (hasSeenLeverageNotice 쿠키/세션 범위) |
| 오더북 데이터 소스 | 목업 데이터 vs 실제 API 연동 미확정 |
| 시그널 주문 수량 단위 | USD 금액 vs 코인 수량 미확정 |
