# 정책 정리

> 원문: [Supercycl] Yothmeta 버전 기획.pptx | 작성일: 2026-03-12

---

## [자동 TP/SL 기능]

### 정책 목표
- 유저가 사전에 TP/SL 비율(%)을 설정해두면, 주문 체결 시 자동으로 TP/SL 주문이 생성되어 매 포지션마다 수동으로 입력하는 부담을 해소하고 리스크 관리를 습관화한다.

### 핵심 정책 규칙

**TP/SL 기준**
- TP/SL은 진입가 대비 퍼센트(%) 기준만 지원 (고정가격/금액 미지원)
- 롱/숏 동일한 TP/SL % 적용 (별도 설정 불가)

**설정 범위**
- Take Profit: 0.1% ~ 999.9% (양수 입력, + 접두사 자동 표시)
- Stop Loss: 0.1% ~ 99.9% (양수 입력 시 자동으로 - 변환)
- 소수점 첫째 자리까지 허용
- TP 또는 SL 중 하나만 입력해도 저장 가능

**ON/OFF 제어**
- Settings Page > Trading Preferences 섹션에 ON/OFF 토글 제공
- Order Form 내에서도 ON/OFF 토글 상시 노출 (설정값 표시 포함)
- 토글 OFF 시: 신규 주문은 자동 TP/SL 미적용, 기존 포지션의 TP/SL은 유지
- 설정값(TP/SL %)이 없으면 토글 ON 불가, Edit 모달로 유도

**주문 유형별 적용**
- 시장가 주문: 체결 즉시 진입가 기준 TP/SL 생성
- 지정가 주문: 주문 시점에 지정가 기준 TP/SL 생성 → 체결 시점에 포지션 TP/SL로 변환
  - 미체결 대기 중 TP/SL 확인 및 수정 가능

**추가 진입(물타기) 처리**
- 3월 말 빌드: 주문별 개별 TP/SL 생성 (Partial TP/SL)
  - 각 주문량과 주문 가격 기준으로 개별 TP/SL 추가
- 5월 말 빌드: 평균 진입가 기준 TP/SL 재계산 (Full TP/SL)

**수동 오버라이드**
- 유저가 개별 포지션에서 TP/SL 수동 수정/삭제 가능
- 수동 변경 후 추가 진입 시: 수동 변경값 유지 (자동 변경 없음)
- Order Form에서 수동 TP/SL 입력 시: 해당 주문은 수동값 우선 적용, 자동 TP/SL 인디케이터는 유지

**설정값 변경 소급 적용 없음**
- 설정 변경은 신규 주문에만 적용
- 기존 포지션의 TP/SL에는 소급 적용하지 않음

**Dashboard 표시**
- 자동으로 생성된 TP/SL에는 "Auto" 배지 표시
- 유저가 수동 변경 시 "Auto" 배지 제거

**토스트 팝업 (Toast)**
- 주문 체결 + 자동 TP/SL 생성 성공: "Order filled. Auto TP/SL applied. TP: $X / SL: $Y" (Green)
- 자동 TP/SL 설정 저장: "Auto TP/SL settings saved. TP: +X% / SL: -Y%" (Green)
- 토글 ON: "Auto TP/SL enabled." (Green)
- 토글 OFF: "Auto TP/SL disabled. Existing TP/SL orders are not affected." (Green)
- 물타기 재계산(5월 빌드): "Position averaged. Auto TP/SL recalculated. TP: $X / SL: $Y" (Green)
- 자동 TP/SL 생성 실패: "Auto TP/SL failed to apply. Please set TP/SL manually." (Red)

### 예외/제한 사항
- Gate 거래소는 Basic TP/SL 미지원으로 별도 대응 방안 검토 필요
- 자동 TP/SL 기본 상태: OFF (설정값 없음) — 유스메타 측 확인 필요 (기본 ON일 경우 default 수치도 필요)

### 미결 사항
- TP/SL 기준을 % 외 고정가격/금액도 지원할지 여부 (현재 % only로 가정)
- Gate 거래소 대응 시점 및 방식
- 파트너/개인 계정별 TP/SL 기본값 수치 확정
- Partial TP/SL 누적 시 최대 허용 개수 또는 병합 정책 (5월 빌드로 이관)
- 자동 TP/SL 기본 상태 (ON/OFF) 및 기본 수치 확정

---

## [2배 레버리지 고정]

### 정책 목표
- 유스메타(YOUTHMETA) 파트너 레퍼럴 링크를 통해 유입된 유저에 한해 최대 레버리지를 2배로 제한하여 과도한 리스크를 방지한다.

### 핵심 정책 규칙

**대상 유저 식별**
- 유스메타 전용 레퍼럴 링크를 통해 가입 시 `partner_code = YOUTHMETA` 자동 태깅
- 태깅된 계정에 "레버리지 2배 고정 정책" 플래그 자동 적용

**최초 로그인 안내 팝업**
- 노출 대상: `partner_code = YOUTHMETA` 태깅 계정
- 노출 시점: 최초 로그인 1회만 노출 (이후 재접속/재로그인 시 미노출)
- 모달 타입: 확인 필수 모달 (배경 클릭으로 닫기 불가)
- 확인 이력: 로컬 저장
- 안내 문구(영문): "This account has a maximum leverage limit of 2x under the user protection policy."
- 버튼: "I Understand"

**Adjust Leverage 모달 변경 (YOUTHMETA 유저 전용)**
- 경고 배너: 모달 상단 노란색 배너로 2배 제한 안내 (항상 노출)
- 슬라이더 범위: 1x ~ 2x로 제한 (기존 최대 레버리지 무시)
- 인풋 입력 제한: 3 이상 숫자 입력 불가
- 일반 유저: 기존 모달 그대로 유지

**Order Form 레버리지 표시 변경 (YOUTHMETA 유저 전용)**
- 레버리지 값 옆에 "(Max)" 텍스트 추가 표시
- 예: `Isolated  2x /2x (Max)`
- 클릭 시 제한된 Adjust Leverage 모달 출력

**기존 고레버리지 포지션 처리**
- 정책 적용 전 또는 별도 앱에서 2배 초과 포지션 보유 중인 경우
  - 기존 포지션은 강제 청산하지 않고 유지
  - 기존 포지션 레버리지 표시는 실제 설정값 그대로 표시
  - 신규 주문부터 2배 제한 적용
  - 기존 포지션 레버리지 변경 시도 시: 2배 이하로만 변경 가능

**롱/숏 별도 레버리지**
- 롱/숏 각각 최대 2x로 제한
- 동일 UI 구조, 범위만 변경

### 예외/제한 사항
- 일반 유저(비 YOUTHMETA 계정)에게는 기존 레버리지 정책 그대로 적용
- 기존 고레버리지 포지션은 강제 청산 없이 유지

### 미결 사항
- 기존 고레버리지 포지션 보유 유저의 UI 표시 방안 (예: 3배 포지션을 어떻게 표시할지)

---

## [UI/UX 화면 변경]

### 정책 목표
- 자동 TP/SL 및 2배 레버리지 고정 기능을 사용자가 직관적으로 제어할 수 있도록 기존 화면을 수정하고 신규 UI 컴포넌트를 추가한다.

### 핵심 정책 규칙

**신규 화면/컴포넌트**
1. Settings Page > Trading Preferences 섹션 (신규): Auto TP/SL 설정 진입점
2. 자동 TP/SL 설정 모달 (신규): Settings 및 Order Form에서 동일 모달 사용
3. 레버리지 2배 고정 최초 로그인 안내 팝업 (신규)
4. 자동 TP/SL 토스트 팝업 (기존 컴포넌트 재사용)

**기존 화면 변경**
1. Order Form: 자동 TP/SL 활성화 상태 인디케이터 추가 (TP/SL 영역 하단)
2. Dashboard (Positions 탭): 자동 생성된 TP/SL에 "Auto" 배지 추가
3. Adjust Leverage 모달: YOUTHMETA 유저 대상 슬라이더/인풋 범위 제한 + 경고 배너
4. Order Form 레버리지 버튼: YOUTHMETA 유저 대상 "(Max)" 텍스트 추가

### 예외/제한 사항
- Dashboard의 "Auto" 배지 표시는 3월 말 스코프에서 제외 (슬라이드 21 기준)

### 미결 사항
- 자동 TP/SL 인디케이터 위치 (Order Form 내 TP/SL 영역 하단으로 가정, 디자인 작업 시 변경 가능성 있음)

---

## [빌드 및 버전 로드맵]

### 정책 목표
- 유스메타 파트너 버전을 단계적으로 출시하여 서비스 안정성을 확보하고 협업 성과에 따라 기능을 확장한다.

### 핵심 정책 규칙

| 버전 | 시기 | 대상 CEX | 주요 기능 |
|------|------|----------|-----------|
| 1.0 | 3월 말 | GATE, OKX | 2배 레버리지 제한, Auto TP/SL |
| 1.1 | 5월 말 | + Binance | Binance 추가, 모바일 Push 알림, 평균진입가 기준 TP/SL 재계산 |
| 1.2 | 6~7월 | + BingX | BingX 거래소 연동 |

### 예외/제한 사항
- 5월 이후 추가 기능은 3월 오픈 성과(유저 유입률 등)에 따라 진행 여부 결정

### 미결 사항
- 모바일 Push 알림 구현 방식 (API Key 저장 방식)
- 시드 제한 매매 기능 상세 설계 (예: $1,000 중 $500만 운용)
