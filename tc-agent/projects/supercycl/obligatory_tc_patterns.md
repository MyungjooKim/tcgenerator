# Supercycl Mobile — 의무 TC 패턴 체크리스트

> 생성된 TC 에 **반드시 있어야 할 패턴**을 정의. AI 가 통합/누락하기 쉬운 케이스 검출용.
>
> 동작: TC 의 제목·소분류·테스트 단계에서 키워드 매칭. 누락 시 `obligatory_tc_check` 시트에 표시 (자동 정정 X).
>
> 형식: `| ScreenCode | Pattern Name | Keywords | Why |`
> · `ScreenCode`: SCR 의 ScreenCode (3자) 또는 `*` (전 화면 적용)
> · `Pattern Name`: 의무 TC 의 의도 (예: "Notional value 계산")
> · `Keywords`: TC 본문(제목·소분류·스텝)에 등장해야 할 키워드 — 콤마 구분 OR, `+` 는 AND
> · `Why`: 왜 의무인지 (분리 이유)

---

## Order Confirm (ORC) — SCR-104

| ScreenCode | Pattern Name | Keywords | Why |
|------------|-------------|----------|-----|
| ORC | Liquidation price 계산 | Liquidation price+공식, Liquidation price+계산 | 공식별 분리 (다른 계산과 통합 금지) |
| ORC | Position size 계산 | Position size+공식, Position size+계산, Position size+Margin × Leverage | 공식별 분리 |
| ORC | Notional value 계산 | Notional value, notional+계산, notional+USD | Position size 와 통합되기 쉬운 별도 공식 |
| ORC | Mark price 실시간 갱신 | Mark price+갱신, Mark price+실시간 | 실시간 정확성 검증 |
| ORC | Δ% 산출 정확성 | Δ%, Δ %, delta %, 차이율 | Limit 주문의 가격 차이 검증 |
| ORC | 잔고 비율 80% 경고 | 잔고+80%, 잔고 비율+경고, 80%+경고 배너 | 비즈니스 위험 — 별도 TC |
| ORC | 더블 탭 방지 | 더블 탭, 연속 탭, double tap, 중복 클릭 방지 | UI 가드 (중복 주문 Modal 과 다른 차원) |
| ORC | iOS swipe back | iOS+스와이프, iOS+swipe, Safari+뒤로가기 | 플랫폼별 trigger 분리 |
| ORC | Android back button | Android+뒤로가기, Android+back, Chrome+back | 플랫폼별 trigger 분리 |
| ORC | 3G 5초 이내 로딩 | 3G+5초, 저사양+로딩, 성능+5초 | 성능 임계값 (일반 Loading 과 다름) |

## OAuth Connect (OAC) — SCR-801

| ScreenCode | Pattern Name | Keywords | Why |
|------------|-------------|----------|-----|
| OAC | 권한 목록 표시 | 권한 목록, Read account, Read balances, Place trades | 정확한 권한 항목 검증 |
| OAC | Withdrawals 비활성 | Withdrawals+비활성, Withdrawals+disabled | 보안상 핵심 검증 |
| OAC | Connect 버튼 동작 | Connect+탭, Connect+버튼+동작 | 핵심 진입 |

## OKX OAuth Webview (OKX) — SCR-808

| ScreenCode | Pattern Name | Keywords | Why |
|------------|-------------|----------|-----|
| OKX | URL 바 정보 검증 | URL 바, www.okx.com, OKX 도메인 | 보안 — 피싱 방지 |
| OKX | 인증 취소 동작 | 취소+SCR-801, 취소+복귀, Cancel+OAuth | 사용자 중단 흐름 |

## Reconnect (ERC) — SCR-805

| ScreenCode | Pattern Name | Keywords | Why |
|------------|-------------|----------|-----|
| ERC | OAuth 재인증 시작 | Reconnect+OKX+탭, OAuth+재인증, OAuth+재오픈 | 핵심 동작 |
| ERC | API Key 경로 분기 | API Key+분기, Or update API Keys | 대체 경로 검증 |

## Exchange Detail (EXD) — SCR-806

| ScreenCode | Pattern Name | Keywords | Why |
|------------|-------------|----------|-----|
| EXD | Connected 상태 표시 | Connected+상태, Connected+badge | 정상 상태 |
| EXD | Expired 상태 표시 | Expired+상태, Expired+badge | 만료 상태 |
| EXD | 재연결 후 상태 전환 | Reconnect+후+Connected, Expired+후+Connected | 상태 전환 검증 |

## Disconnect Confirm (EDC) — SCR-804

| ScreenCode | Pattern Name | Keywords | Why |
|------------|-------------|----------|-----|
| EDC | destructive 가드 | destructive+빨강, 빨강+버튼, Disconnect+빨강 | UX 가드 (실수 방지) |
| EDC | Cancel 복귀 | Cancel+SCR-806, Cancel+복귀+상세 | 취소 경로 |

## 전 화면 공통 (`*`)

| ScreenCode | Pattern Name | Keywords | Why |
|------------|-------------|----------|-----|
| * | 네트워크 끊김 처리 | 네트워크+끊김, 네트워크+오프라인, 네트워크 오류 | 비기능 — 모든 화면 |
| * | 빈 상태 표시 | 빈 상태, Empty 상태, empty state | UI/UX — 데이터 없을 때 |

---

## 운영 가이드

- **추가 방법**: 위 표에 행 추가. ScreenCode 는 screen_code_map.md 참고.
- **파싱 규칙**:
  - 콤마(`,`) = OR (하나라도 매칭되면 통과)
  - 플러스(`+`) = AND (모두 등장해야 통과 — 동일 TC 안에서)
  - 공백 무시, 대소문자 무시
- **검출 실패 시**: `obligatory_tc_check` 시트에 표시. 자동 추가 안 함 — 사람이 검토 후 spec 보강하거나 TC 재생성.
