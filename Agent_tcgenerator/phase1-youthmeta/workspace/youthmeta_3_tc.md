# 테스트 케이스 목록

> 기반 문서: youthmeta_2_features.md | 작성일: 2026-03-12
> 서비스: Supercycl × Youthmeta 파트너 버전 (v1.0)

---

## 도메인 코드 정의

| 코드 | 설명 |
|------|------|
| TPSL | 자동 TP/SL 설정 및 관리 |
| ORDER | 주문 처리 및 자동 TP/SL 생성 |
| LEVER | 2배 레버리지 고정 |
| UI | UI 인디케이터 및 토스트 표시 |

---

## [TPSL] 자동 TP/SL 설정 관리

### TPSL-SET-001 Settings 화면에서 TP/SL 값 입력 후 저장 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Settings > Trading Preferences |

**사전 조건**
- 로그인 상태이다
- Settings > Trading Preferences 화면에 접속해 있다
- Auto TP/SL 설정값이 비어 있다

**테스트 단계**
1. `Edit` 버튼을 클릭하여 Auto TP/SL 설정 모달을 연다
2. Take Profit(%) 입력 필드에 `1.8`을 입력한다
3. Stop Loss(%) 입력 필드에 `5.0`을 입력한다
4. `Confirm` 버튼을 클릭한다

**예상 결과**
- 모달이 닫힌다
- Settings 화면에 `TP: +1.8% | SL: -5.0%`로 설정값이 표시된다
- 성공 토스트 `Auto TP/SL settings saved. TP: +1.8% / SL: -5.0%`가 노출된다

---

### TPSL-SET-002 TP만 입력해도 Confirm 버튼 활성화 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Auto TP/SL 설정 모달 |

**사전 조건**
- Auto TP/SL 설정 모달이 열려 있다
- 입력 필드가 모두 비어 있다

**테스트 단계**
1. Take Profit(%) 필드에 `2.0`을 입력한다
2. Stop Loss(%) 필드는 비워 둔다
3. `Confirm` 버튼 활성화 여부를 확인한다

**예상 결과**
- `Confirm` 버튼이 활성화된다
- `Confirm` 클릭 시 설정이 저장되고 모달이 닫힌다

---

### TPSL-SET-003 TP/SL 값 미입력 상태에서 Confirm 버튼 비활성화 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Auto TP/SL 설정 모달 |

**사전 조건**
- Auto TP/SL 설정 모달이 열려 있다
- 두 입력 필드 모두 비어 있다

**테스트 단계**
1. Take Profit(%) 필드와 Stop Loss(%) 필드를 모두 빈 상태로 유지한다
2. `Confirm` 버튼 상태를 확인한다

**예상 결과**
- `Confirm` 버튼이 비활성화(disabled) 상태이다
- 버튼 클릭이 되지 않는다

---

### TPSL-SET-004 TP 입력 필드에 + 접두사 자동 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Auto TP/SL 설정 모달 |

**사전 조건**
- Auto TP/SL 설정 모달이 열려 있다

**테스트 단계**
1. Take Profit(%) 필드에 `1.8`을 입력한다

**예상 결과**
- 입력 필드에 `+1.8`로 + 접두사가 자동 표시된다

---

### TPSL-SET-005 SL 입력 필드에 양수 입력 시 자동으로 음수 변환 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Auto TP/SL 설정 모달 |

**사전 조건**
- Auto TP/SL 설정 모달이 열려 있다

**테스트 단계**
1. Stop Loss(%) 필드에 `5.0`(양수)을 입력한다

**예상 결과**
- 입력 필드에 `-5.0`으로 자동 변환되어 표시된다

---

### TPSL-SET-006 TP 유효성 최솟값(0.1%) 미만 입력 시 오류 처리 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Auto TP/SL 설정 모달 |

**사전 조건**
- Auto TP/SL 설정 모달이 열려 있다

**테스트 단계**
1. Take Profit(%) 필드에 `0`을 입력한다
2. `Confirm` 버튼 상태를 확인한다

**예상 결과**
- `Confirm` 버튼이 비활성화 상태이다 (0 입력 시 활성화되지 않음)

---

### TPSL-SET-007 TP 최댓값(999.9%) 입력 후 저장 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web |
| 연관 화면 | Auto TP/SL 설정 모달 |

**사전 조건**
- Auto TP/SL 설정 모달이 열려 있다

**테스트 단계**
1. Take Profit(%) 필드에 `999.9`를 입력한다
2. Stop Loss(%) 필드에 `1.0`을 입력한다
3. `Confirm` 버튼을 클릭한다

**예상 결과**
- 설정이 정상 저장되고 모달이 닫힌다
- Settings 화면에 `TP: +999.9% | SL: -1.0%`로 표시된다

---

### TPSL-SET-008 SL 최댓값(99.9%) 초과 입력 시 처리 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Auto TP/SL 설정 모달 |

**사전 조건**
- Auto TP/SL 설정 모달이 열려 있다

**테스트 단계**
1. Stop Loss(%) 필드에 `100`을 입력한다
2. `Confirm` 버튼 상태를 확인한다

**예상 결과**
- `Confirm` 버튼이 비활성화되거나 유효성 오류가 표시된다 (99.9% 초과 불가)

---

### TPSL-SET-009 설정값 없는 상태에서 토글 ON 시도 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Settings > Trading Preferences |

**사전 조건**
- 로그인 상태이다
- Auto TP/SL 설정값(TP/SL %)이 없는 상태이다
- Auto TP/SL 토글이 OFF 상태이다

**테스트 단계**
1. Settings > Trading Preferences에서 Auto TP/SL 토글을 ON으로 변경하려 클릭한다

**예상 결과**
- 토글이 ON으로 전환되지 않는다
- Edit 모달이 자동으로 열리거나 설정값 입력을 유도하는 안내가 표시된다

---

### TPSL-SET-010 모달 저장 시 토글 OFF 상태였다면 자동으로 ON 전환 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Auto TP/SL 설정 모달 |

**사전 조건**
- Auto TP/SL 토글이 OFF 상태이다
- Auto TP/SL 설정 모달이 열려 있다

**테스트 단계**
1. Take Profit(%) 필드에 `2.0`을 입력한다
2. Stop Loss(%) 필드에 `3.0`을 입력한다
3. `Confirm` 버튼을 클릭한다

**예상 결과**
- 모달이 닫힌다
- Settings 화면의 Auto TP/SL 토글이 자동으로 ON 상태가 된다

---

### TPSL-SET-011 Cancel 버튼 클릭 시 변경사항 미저장 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Auto TP/SL 설정 모달 |

**사전 조건**
- Auto TP/SL 설정 모달이 열려 있다
- 기존 설정값: TP +1.8%, SL -5.0%

**테스트 단계**
1. Take Profit(%) 필드 값을 `3.0`으로 변경한다
2. `Cancel` 버튼을 클릭한다

**예상 결과**
- 모달이 닫힌다
- Settings 화면에 기존 값 `TP: +1.8% | SL: -5.0%`가 유지된다

---

## [TPSL] 자동 TP/SL — Order Form 연동

### TPSL-FORM-001 Order Form에서 Auto TP/SL 인디케이터 상시 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Order Form |

**사전 조건**
- 로그인 상태이다
- Order Form이 열려 있다
- Auto TP/SL 설정값이 저장되어 있다 (TP +1.8%, SL -5.0%)

**테스트 단계**
1. Order Form의 TP/SL 영역을 확인한다
2. Auto TP/SL 토글 상태와 설정값 표시 여부를 확인한다

**예상 결과**
- "Auto TP/SL ON/OFF" 인디케이터가 TP/SL 영역에 표시된다
- 현재 설정값 `TP: +1.8% | SL: -5.0%`가 함께 표시된다

---

### TPSL-FORM-002 Order Form에서 토글 OFF 전환 후 설정값 표시 유지 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Order Form |

**사전 조건**
- Auto TP/SL이 ON 상태이며 설정값(TP +1.8%, SL -5.0%)이 있다
- Order Form이 열려 있다

**테스트 단계**
1. Order Form 내 Auto TP/SL 토글을 OFF로 변경한다

**예상 결과**
- 인디케이터가 "Auto TP/SL OFF" 상태로 변경된다
- 설정값 표시는 유지된다
- 토스트 `Auto TP/SL disabled. Existing TP/SL orders are not affected.`가 노출된다

---

### TPSL-FORM-003 Order Form과 Settings 토글 상태 동기화 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Order Form / Settings |

**사전 조건**
- Auto TP/SL이 Settings에서 ON 상태이다
- Order Form이 열려 있다

**테스트 단계**
1. Settings > Trading Preferences에서 Auto TP/SL 토글을 OFF로 변경한다
2. Order Form 화면으로 돌아온다

**예상 결과**
- Order Form의 Auto TP/SL 토글도 OFF 상태로 동기화되어 있다

---

### TPSL-FORM-004 Order Form에서 수동 TP/SL 입력 시 수동값 우선 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Order Form |

**사전 조건**
- Auto TP/SL이 ON 상태이다 (TP +1.8%, SL -5.0%)
- Order Form이 열려 있다

**테스트 단계**
1. Order Form의 TP/SL 입력 필드에 TP: `$2,100`, SL: `$1,800`을 수동으로 입력한다
2. Buy/Long 주문을 실행한다

**예상 결과**
- 수동으로 입력한 TP $2,100, SL $1,800이 적용된 TP/SL 주문이 생성된다
- Auto TP/SL 인디케이터는 여전히 표시된다 (설정 자체는 유지)

---

## [ORDER] 자동 TP/SL 주문 처리

### ORDER-MKTFILL-001 시장가 롱 주문 체결 시 자동 TP/SL 생성 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Order Form / Positions 탭 |

**사전 조건**
- Auto TP/SL이 ON 상태이다 (TP +1.8%, SL -5.0%)
- 잔고가 충분하다
- ETH-PERP 시장이 열려 있다

**테스트 단계**
1. Order Form에서 ETH-PERP를 선택한다
2. 주문 유형을 `Market`으로 설정한다
3. 수량을 입력하고 `Buy / Long` 버튼을 클릭한다
4. Positions 탭에서 생성된 포지션을 확인한다

**예상 결과**
- 주문이 시장가로 체결된다
- Positions 탭에 해당 포지션의 TP/SL이 진입가 기준 +1.8% / -5.0%로 자동 설정되어 있다
- 성공 토스트 `Order filled. Auto TP/SL applied. TP: $X / SL: $Y`가 노출된다

---

### ORDER-MKTFILL-002 Auto TP/SL OFF 상태에서 시장가 주문 체결 시 TP/SL 미생성 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Order Form / Positions 탭 |

**사전 조건**
- Auto TP/SL이 OFF 상태이다
- 잔고가 충분하다

**테스트 단계**
1. Order Form에서 시장가 롱 주문을 실행한다
2. Positions 탭에서 해당 포지션의 TP/SL을 확인한다

**예상 결과**
- 주문이 체결된다
- 해당 포지션에 자동 TP/SL이 생성되지 않는다 (TP/SL 항목이 빈 상태 또는 미표시)

---

### ORDER-LIMIT-001 지정가 주문 시 지정가 기준 TP/SL 즉시 생성 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Order Form / Open Orders 탭 |

**사전 조건**
- Auto TP/SL이 ON 상태이다 (TP +1.8%, SL -5.0%)
- 잔고가 충분하다

**테스트 단계**
1. Order Form에서 ETH-PERP를 선택한다
2. 주문 유형을 `Limit`으로 설정하고 지정가를 `$1,950`으로 입력한다
3. 수량을 입력하고 `Buy / Long` 버튼을 클릭한다
4. Open Orders(미체결 주문) 목록에서 해당 주문을 확인한다

**예상 결과**
- 미체결 주문 목록에 해당 주문이 표시된다
- 해당 주문의 TP/SL이 지정가 $1,950 기준으로 계산된 값 (TP: $1,985.10 / SL: $1,852.50)으로 표시된다

---

### ORDER-LIMIT-002 지정가 주문 체결 시 포지션 TP/SL로 전환 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Positions 탭 |

**사전 조건**
- Auto TP/SL ON 상태이며 $1,950 지정가 롱 주문이 미체결 대기 중이다

**테스트 단계**
1. 시장가가 $1,950에 도달하여 주문이 체결된다
2. Positions 탭에서 해당 포지션을 확인한다

**예상 결과**
- 포지션 탭에 해당 포지션이 표시된다
- TP/SL이 체결 진입가 $1,950 기준으로 TP: $1,985.10 / SL: $1,852.50로 설정되어 있다

---

### ORDER-LIMIT-003 미체결 지정가 주문의 TP/SL 수정 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Open Orders 탭 |

**사전 조건**
- Auto TP/SL ON 상태이며 미체결 지정가 주문이 존재한다
- 해당 주문의 TP/SL이 자동 생성되어 있다

**테스트 단계**
1. Open Orders 탭에서 미체결 주문의 TP/SL 값을 클릭한다
2. TP 값을 `$2,000`으로 수동 변경한다
3. 저장 버튼을 클릭한다

**예상 결과**
- 미체결 주문의 TP 값이 $2,000으로 변경된다
- SL 값은 기존 자동 설정값이 유지된다

---

### ORDER-AVG-001 추가 진입(물타기) 시 각 주문별 개별 TP/SL 생성 확인 (3월 빌드)

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Order Form / Positions 탭 |

**사전 조건**
- Auto TP/SL ON 상태이다 (TP +1.8%, SL -5.0%)
- ETH-PERP $2,000에 1차 진입 포지션이 이미 열려 있다 (TP: $2,036 / SL: $1,900)

**테스트 단계**
1. 동일 포지션(ETH-PERP 롱)에 $1,900 시장가로 추가 주문을 실행한다
2. Positions 탭에서 TP/SL 상태를 확인한다

**예상 결과**
- 2차 주문에 대해 별도의 TP/SL이 생성된다 (TP: $1,934.20 / SL: $1,805.00)
- 1차 진입의 TP/SL은 기존값(TP: $2,036 / SL: $1,900)이 유지된다

---

### ORDER-OVR-001 자동 생성된 TP/SL을 수동으로 변경 후 유지 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Positions 탭 |

**사전 조건**
- Auto TP/SL ON 상태이며 포지션의 TP/SL이 자동 생성되어 있다 (TP: $2,036 / SL: $1,900)

**테스트 단계**
1. Positions 탭에서 해당 포지션의 TP 값을 클릭한다
2. TP를 `$2,100`으로 수동 변경한다
3. 저장 버튼을 클릭한다

**예상 결과**
- TP가 $2,100으로 변경된다
- 변경 후 Dashboard의 "Auto" 배지가 제거된다

---

### ORDER-OVR-002 수동 변경 후 추가 진입 시 수동값 유지 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Positions 탭 |

**사전 조건**
- 포지션의 TP가 수동으로 $2,100으로 변경된 상태이다
- Auto TP/SL이 ON 상태이다

**테스트 단계**
1. 동일 방향(롱)으로 추가 시장가 주문을 실행한다
2. Positions 탭에서 기존 포지션의 TP/SL을 확인한다

**예상 결과**
- 기존 포지션의 TP 값 $2,100이 변경되지 않고 유지된다
- 추가 주문에 대해 새로운 개별 TP/SL이 자동 생성된다

---

### ORDER-SETCHANGE-001 설정값 변경 후 신규 주문에만 새 설정값 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Settings / Positions 탭 |

**사전 조건**
- 포지션 A가 TP +1.8%, SL -5.0% 기준으로 이미 생성되어 있다
- Auto TP/SL이 ON 상태이다

**테스트 단계**
1. Settings > Trading Preferences에서 TP를 `+3.0%`, SL을 `-2.0%`로 변경하고 저장한다
2. 신규 주문을 실행한다
3. 포지션 A와 신규 포지션의 TP/SL을 각각 확인한다

**예상 결과**
- 기존 포지션 A의 TP/SL은 변경 전 값(TP +1.8%, SL -5.0%)으로 유지된다
- 신규 포지션의 TP/SL은 새 설정값(TP +3.0%, SL -2.0%)으로 생성된다

---

### ORDER-FAIL-001 자동 TP/SL 생성 실패 시 에러 토스트 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Order Form / Toast |

**사전 조건**
- Auto TP/SL이 ON 상태이다
- 거래소 API 오류 상황이 재현 가능한 환경이다 (테스트용 mock 또는 staging)

**테스트 단계**
1. 시장가 주문을 실행한다
2. 주문은 체결되었으나 TP/SL 생성이 거래소 오류로 실패한 경우를 확인한다

**예상 결과**
- 에러 토스트 `Auto TP/SL failed to apply. Please set TP/SL manually.`가 빨간색으로 노출된다
- 포지션은 정상 체결 상태이다 (TP/SL 없이)

---

## [LEVER] 2배 레버리지 고정

### LEVER-TAG-001 유스메타 레퍼럴 링크 통해 가입 시 파트너 코드 태깅 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | 회원가입 화면 / 관리자 조회 |

**사전 조건**
- 유스메타 전용 레퍼럴 링크가 발급되어 있다
- 신규 가입 계정이 없는 이메일이다

**테스트 단계**
1. 유스메타 레퍼럴 링크를 클릭하여 회원가입 페이지로 진입한다
2. 필수 정보를 입력하고 가입을 완료한다
3. 관리자 화면 또는 DB에서 해당 계정의 `partner_code` 값을 조회한다

**예상 결과**
- `partner_code = YOUTHMETA`가 자동으로 태깅되어 있다
- 레버리지 2배 고정 플래그가 활성화되어 있다

---

### LEVER-TAG-002 일반 경로 가입 시 파트너 코드 미태깅 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | 회원가입 화면 |

**사전 조건**
- 유스메타 레퍼럴 링크 없이 일반 가입 경로로 접근 가능하다
- 신규 가입 계정이 없는 이메일이다

**테스트 단계**
1. 유스메타 링크 없이 일반 가입 경로로 회원가입을 완료한다
2. 관리자 화면에서 해당 계정의 `partner_code` 값을 확인한다

**예상 결과**
- `partner_code`가 `YOUTHMETA`로 태깅되지 않는다
- 레버리지 2배 고정 플래그가 적용되지 않는다

---

### LEVER-POPUP-001 YOUTHMETA 계정 최초 로그인 시 안내 팝업 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | 로그인 후 메인 화면 |

**사전 조건**
- `partner_code = YOUTHMETA`로 태깅된 계정이 있다
- 해당 계정으로 최초 로그인 이력이 없다

**테스트 단계**
1. YOUTHMETA 계정으로 로그인한다

**예상 결과**
- "Leverage Policy Notice" 안내 팝업이 자동으로 노출된다
- 팝업 내 문구: `This account has a maximum leverage limit of 2x under the user protection policy.`가 표시된다
- 배경 클릭으로 팝업이 닫히지 않는다

---

### LEVER-POPUP-002 팝업에서 "I Understand" 클릭 후 팝업 닫힘 및 재노출 없음 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | 로그인 후 메인 화면 |

**사전 조건**
- YOUTHMETA 계정 최초 로그인 시 안내 팝업이 노출된 상태이다

**테스트 단계**
1. 팝업에서 `I Understand` 버튼을 클릭한다
2. 로그아웃 후 다시 로그인한다

**예상 결과**
- 버튼 클릭 시 팝업이 닫힌다
- 재로그인 시 안내 팝업이 다시 노출되지 않는다

---

### LEVER-POPUP-003 일반 계정 로그인 시 안내 팝업 미노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | 로그인 후 메인 화면 |

**사전 조건**
- 일반 계정(partner_code 미태깅)으로 최초 로그인하는 상황이다

**테스트 단계**
1. 일반 계정으로 로그인한다

**예상 결과**
- 레버리지 안내 팝업이 노출되지 않는다

---

### LEVER-ADJ-001 YOUTHMETA 계정의 Adjust Leverage 모달에서 2배 초과 선택 불가 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Adjust Leverage 모달 |

**사전 조건**
- YOUTHMETA 계정으로 로그인되어 있다
- Order Form에서 레버리지 버튼을 클릭하여 Adjust Leverage 모달이 열려 있다

**테스트 단계**
1. 모달 내 슬라이더를 최대로 이동시킨다
2. 인풋 필드에 현재 설정 가능한 최댓값을 확인한다

**예상 결과**
- 슬라이더 범위가 1x ~ 2x로 제한되어 있다
- 슬라이더를 최대로 이동해도 2x를 넘지 않는다
- 모달 상단에 노란색 경고 배너 `Max leverage limited to 2x (User Protection Policy)`가 표시된다

---

### LEVER-ADJ-002 YOUTHMETA 계정의 레버리지 인풋 필드에 3 이상 입력 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Adjust Leverage 모달 |

**사전 조건**
- YOUTHMETA 계정으로 로그인되어 있다
- Adjust Leverage 모달이 열려 있다

**테스트 단계**
1. 인풋 필드에 `3`을 입력한다

**예상 결과**
- 입력이 차단되거나 자동으로 2 이하로 리셋된다
- 3x 레버리지 설정이 적용되지 않는다

---

### LEVER-ADJ-003 일반 계정의 Adjust Leverage 모달은 기존과 동일 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Adjust Leverage 모달 |

**사전 조건**
- 일반 계정(partner_code 미태깅)으로 로그인되어 있다
- Adjust Leverage 모달이 열려 있다

**테스트 단계**
1. 슬라이더 범위를 확인한다
2. 인풋 필드에 `10`을 입력한다

**예상 결과**
- 슬라이더가 기존 최대 레버리지 범위(10x 이상)까지 정상 표시된다
- 10x 입력 및 설정이 정상 작동한다
- 경고 배너가 표시되지 않는다

---

### LEVER-FORM-001 YOUTHMETA 계정의 Order Form 레버리지 버튼에 "(Max)" 텍스트 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Order Form |

**사전 조건**
- YOUTHMETA 계정으로 로그인되어 있다
- Order Form이 열려 있다

**테스트 단계**
1. Order Form 상단의 레버리지 표시 영역을 확인한다

**예상 결과**
- 레버리지 버튼에 `2x /2x (Max)` 형태로 "(Max)" 텍스트가 추가 표시된다
- 일반 유저의 `Isolated 10x` 표시와 다르게 보인다

---

### LEVER-EXIST-001 정책 적용 전 고레버리지 포지션 보유 시 기존 포지션 유지 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Positions 탭 |

**사전 조건**
- 정책 적용 전 또는 별도 앱에서 5배 레버리지 포지션이 열려 있는 YOUTHMETA 계정이 있다

**테스트 단계**
1. 해당 계정으로 로그인한다
2. Positions 탭에서 기존 포지션의 레버리지를 확인한다
3. 신규 주문을 시도할 때 레버리지 제한이 적용되는지 확인한다

**예상 결과**
- 기존 5배 포지션은 강제 청산되지 않고 유지된다
- 기존 포지션의 레버리지 표시는 실제 설정값(5x)으로 표시된다
- 신규 주문 시도 시 레버리지는 최대 2x로 제한된다

---

### LEVER-EXIST-002 기존 고레버리지 포지션의 레버리지 변경 시 2배 이하로만 변경 가능 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | High |
| 플랫폼 | Web |
| 연관 화면 | Adjust Leverage 모달 |

**사전 조건**
- YOUTHMETA 계정에 5배 레버리지 기존 포지션이 있다
- 해당 포지션의 레버리지를 변경하려 한다

**테스트 단계**
1. 기존 5배 포지션의 레버리지 버튼을 클릭한다
2. Adjust Leverage 모달에서 레버리지 변경을 시도한다
3. 1x 또는 2x로 변경하고 `Confirm`을 클릭한다
4. 다시 3x 이상으로 변경을 시도한다

**예상 결과**
- 1x, 2x로의 변경은 정상 적용된다
- 3x 이상으로의 변경은 차단된다
- 슬라이더 및 인풋 모두 2x 이하로 제한된다

---

## [UI] 인디케이터 및 토스트

### UI-TOAST-001 Auto TP/SL 토글 ON 시 성공 토스트 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Settings / Order Form |

**사전 조건**
- Auto TP/SL 설정값이 저장되어 있다 (TP +1.8%, SL -5.0%)
- Auto TP/SL 토글이 OFF 상태이다

**테스트 단계**
1. Settings 또는 Order Form에서 Auto TP/SL 토글을 ON으로 변경한다

**예상 결과**
- 토스트 `Auto TP/SL enabled.`가 초록색으로 노출된다

---

### UI-TOAST-002 Auto TP/SL 토글 OFF 시 토스트 및 안내 메시지 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Settings / Order Form |

**사전 조건**
- Auto TP/SL 토글이 ON 상태이다

**테스트 단계**
1. Auto TP/SL 토글을 OFF로 변경한다

**예상 결과**
- 토스트 `Auto TP/SL disabled. Existing TP/SL orders are not affected.`가 초록색으로 노출된다

---

### UI-TOAST-003 설정 저장 성공 시 설정값 포함 토스트 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Auto TP/SL 설정 모달 |

**사전 조건**
- Auto TP/SL 설정 모달이 열려 있다

**테스트 단계**
1. TP `1.8`, SL `5.0`을 입력하고 `Confirm`을 클릭한다

**예상 결과**
- 토스트 `Auto TP/SL settings saved. TP: +1.8% / SL: -5.0%`가 초록색으로 노출된다

---

### UI-BADGE-001 자동 생성된 TP/SL에 "Auto" 배지 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Dashboard > Positions 탭 |

**사전 조건**
- Auto TP/SL이 ON 상태에서 시장가 주문이 체결되어 TP/SL이 자동 생성된 포지션이 있다

**테스트 단계**
1. Dashboard의 Positions 탭에서 해당 포지션의 TP/SL 영역을 확인한다

**예상 결과**
- TP/SL 값 옆에 `Auto` 배지가 표시된다

---

### UI-BADGE-002 TP/SL 수동 변경 후 "Auto" 배지 제거 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web |
| 연관 화면 | Dashboard > Positions 탭 |

**사전 조건**
- Positions 탭에 Auto 배지가 표시된 포지션이 있다

**테스트 단계**
1. 해당 포지션의 TP/SL 값을 클릭하여 수동으로 TP 값을 변경한다
2. 변경을 저장한다

**예상 결과**
- `Auto` 배지가 제거된다
- 수동 변경된 TP/SL 값이 표시된다
