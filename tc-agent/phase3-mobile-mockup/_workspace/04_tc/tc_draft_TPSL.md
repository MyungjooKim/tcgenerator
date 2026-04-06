# TC 초안 — TPSL 도메인 (TP/SL 설정)

**생성일:** 2026-04-03
**도메인:** TPSL — TP/SL 설정
**중분류:** MODL (AutoTpSl 모달), TOGL (Auto TP/SL 토글)
**기준 소스:** classification_v1_APPROVED.md / feature_list.md / policy_doc.md / 03_TC_Policy_AutoTPSL.md

---

## 요약

| 항목 | 내용 |
|------|------|
| 전체 TC 수 | 14개 |
| ★ TC 수 | 5개 (36%) |
| 중분류 MODL | 11개 |
| 중분류 TOGL | 3개 |

---

## TPSL-MODL — AutoTpSl 모달

---

### **SC-TPSL-MODL-001** — AutoTpSlModal 오픈 및 기본값 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | AutoTpSlModal 오픈 (설정 화면) |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- `/trade` Settings 탭에 접속해 있다

**테스트 단계**
1. Settings 탭의 Auto TP/SL 섹션에서 `Edit` 버튼을 탭한다
2. AutoTpSlModal이 화면에 표시되는지 확인한다
3. TP 입력 필드의 기본값을 확인한다
4. SL 입력 필드의 기본값을 확인한다

**예상 결과**
- AutoTpSlModal이 오픈된다
- TP 입력 필드에 기본값 `1.8`(%)이 표시된다
- SL 입력 필드에 기본값 `5.0`(%)이 표시된다

---

### **SC-TPSL-MODL-002** — AutoTpSlModal Confirm 후 설정값 저장 및 설정 화면 반영 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | AutoTpSlModal Confirm — 설정 저장 |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings), AutoTpSlModal |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Settings 탭의 Edit 버튼을 탭하여 AutoTpSlModal이 열린 상태이다
- TP 및 SL 중 하나 이상의 값이 0보다 크다

**테스트 단계**
1. AutoTpSlModal에서 TP 입력 필드에 `2.5`를 입력한다
2. SL 입력 필드에 `3.0`을 입력한다
3. `Confirm` 버튼을 탭한다
4. 모달이 닫히는지 확인한다
5. Settings 탭의 Auto TP/SL 표시 영역을 확인한다

**예상 결과**
- `Confirm` 버튼 탭 후 모달이 닫힌다
- Settings 화면의 Auto TP/SL 표시가 `TP: +2.5% | SL: -3.0%`로 업데이트된다

---

### SC-TPSL-MODL-003 — AutoTpSlModal Confirm 후 안내 문구 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | AutoTpSlModal Confirm — 설정 저장 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
- AutoTpSlModal이 열린 상태이다
- TP 입력 필드와 SL 입력 필드에 유효한 값(0 초과)이 입력되어 있다

**테스트 단계**
1. AutoTpSlModal 하단 안내 문구를 확인한다

**예상 결과**
- 모달 내에 "Settings apply to new orders only. Existing positions will not be affected." 안내 문구가 표시된다

---

### **SC-TPSL-MODL-004** — TP/SL 모두 0일 때 Confirm 버튼 비활성화 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
- AutoTpSlModal이 열린 상태이다

**테스트 단계**
1. TP 입력 필드를 `0`으로 변경한다
2. SL 입력 필드를 `0`으로 변경한다
3. `Confirm` 버튼의 상태를 확인한다
4. `Confirm` 버튼을 탭한다

**예상 결과**
- TP + SL 모두 0인 상태에서 `Confirm` 버튼이 비활성화(disabled) 상태이다
- 버튼을 탭해도 모달이 닫히지 않는다

---

### SC-TPSL-MODL-005 — TP 입력값 최댓값(999.9%) 초과 시 입력 제한 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
- AutoTpSlModal이 열린 상태이다

**테스트 단계**
1. TP 입력 필드에 `1000`을 입력한다
2. 입력 필드의 값을 확인한다

**예상 결과**
- TP 입력값이 `999.9`(%)를 초과하지 않도록 입력이 제한되거나 자동으로 리셋된다

---

### SC-TPSL-MODL-006 — SL 입력값 최댓값(99.9%) 초과 시 입력 제한 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
- AutoTpSlModal이 열린 상태이다

**테스트 단계**
1. SL 입력 필드에 `100`을 입력한다
2. 입력 필드의 값을 확인한다

**예상 결과**
- SL 입력값이 `99.9`(%)를 초과하지 않도록 입력이 제한되거나 자동으로 리셋된다

---

### SC-TPSL-MODL-007 — TP/SL 입력 필드 음수 입력 불가 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
- AutoTpSlModal이 열린 상태이다

**테스트 단계**
1. SL 입력 필드에 `-5`를 입력 시도한다
2. 입력 필드의 값을 확인한다

**예상 결과**
- 음수 값이 입력되지 않는다 (입력 필드가 음수를 허용하지 않거나 자동으로 제거된다)

**비고**
- SL은 UI 상 양수로 입력받으며 내부적으로 손실 비율로 처리됨

---

### SC-TPSL-MODL-008 — TP/SL 소수점 2자리 이상 입력 불가 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
- AutoTpSlModal이 열린 상태이다

**테스트 단계**
1. TP 입력 필드에 `1.23`을 입력 시도한다
2. 입력 필드의 값을 확인한다

**예상 결과**
- 소수점 2자리 이상이 입력되지 않는다 (소수점 1자리까지만 허용되거나 자동으로 반올림된다)

---

### SC-TPSL-MODL-009 — AutoTpSlModal Cancel 후 변경값 미저장 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | AutoTpSlModal Cancel — 변경 불저장 |
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
- AutoTpSlModal이 열린 상태이다
- 현재 TP 설정값은 `1.8`(%), SL 설정값은 `5.0`(%)이다

**테스트 단계**
1. TP 입력 필드를 `9.9`로 변경한다
2. `Cancel` 버튼을 탭한다
3. 모달이 닫히는지 확인한다
4. Settings 탭의 Auto TP/SL 표시 영역을 확인한다

**예상 결과**
- `Cancel` 버튼 탭 후 모달이 닫힌다
- Settings 화면의 Auto TP/SL 표시가 기존 값(`TP: +1.8% | SL: -5.0%`)으로 유지된다 (변경 미저장)

---

### SC-TPSL-MODL-010 — TP만 0이고 SL > 0인 경우 Confirm 버튼 활성 여부 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | TP/SL 퍼센트 입력 및 범위 검증 |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | AutoTpSlModal |

**사전 조건**
- AutoTpSlModal이 열린 상태이다

**테스트 단계**
1. TP 입력 필드를 `0`으로 변경한다
2. SL 입력 필드에 `5.0`을 입력한다
3. `Confirm` 버튼의 상태를 확인한다

**예상 결과**
- TP = 0이고 SL > 0인 상태에서 `Confirm` 버튼의 활성화 여부를 확인한다

**비고**
- [미결] PEND-SETS-002: TP=0이고 SL>0인 경우 Confirm 버튼 활성 여부 미확정 — 현재 정책은 "TP+SL 모두 0이면 비활성"이므로 이 경우 활성화 예상, 정책 확정 후 예상 결과 수정 필요

---

### SC-TPSL-MODL-011 — Auto TP/SL OFF 상태에서 Edit 버튼 탭 시 모달 오픈 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | AutoTpSl 모달 |
| 소분류 | AutoTpSlModal 오픈 (설정 화면) |
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
- Settings 탭에 접속해 있다
- Auto TP/SL 토글이 OFF 상태이다

**테스트 단계**
1. Auto TP/SL 섹션의 `Edit` 버튼을 탭한다
2. AutoTpSlModal 오픈 여부를 확인한다

**예상 결과**
- AutoTpSlModal이 오픈된다

**비고**
- [미결] PEND-SETS-001: OFF 상태에서 Edit → Confirm 시 Auto TP/SL이 ON으로 자동 전환되는지 여부 미확정

---

## TPSL-TOGL — Auto TP/SL 토글

---

### **SC-TPSL-TOGL-001** — Auto TP/SL 토글 ON 전환 및 상태 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | Auto TP/SL 토글 |
| 소분류 | Auto TP/SL 토글 ON/OFF |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- `/trade` Settings 탭에 접속해 있다
- Auto TP/SL 토글이 OFF 상태이다

**테스트 단계**
1. Auto TP/SL 섹션의 토글 스위치를 탭하여 ON으로 전환한다
2. 토글 상태를 확인한다
3. Settings 화면의 Auto TP/SL 표시 영역을 확인한다

**예상 결과**
- 토글이 ON 상태로 전환된다 (시각적으로 활성화 상태가 표시된다)
- Settings 화면에 현재 TP/SL 설정값(`TP: +X.X% | SL: -X.X%`)이 표시된다

---

### **SC-TPSL-TOGL-002** — Auto TP/SL ON 상태에서 주문 시 Order Form TP/SL 자동 표시 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | Auto TP/SL 토글 |
| 소분류 | Auto TP/SL 토글 ON/OFF |
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: trade, settings) |

**사전 조건**
- Settings 탭에서 Auto TP/SL 토글이 ON 상태이다
- TP: 1.8%, SL: 5.0%로 설정되어 있다
- Trade 탭에 접속해 있다

**테스트 단계**
1. Trade 탭의 OrderForm 영역을 확인한다
2. OrderForm 하단의 TP/SL 표시 항목을 확인한다

**예상 결과**
- OrderForm 하단에 `TP: +1.8% / SL: -5.0%` 가 표시된다

---

### SC-TPSL-TOGL-003 — Auto TP/SL 토글 OFF 전환 확인

| 항목 | 내용 |
|------|------|
| 대분류 | TP/SL 설정 (TPSL) |
| 중분류 | Auto TP/SL 토글 |
| 소분류 | Auto TP/SL 토글 ON/OFF |
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (탭: settings) |

**사전 조건**
- Settings 탭에 접속해 있다
- Auto TP/SL 토글이 ON 상태이다

**테스트 단계**
1. Auto TP/SL 섹션의 토글 스위치를 탭하여 OFF로 전환한다
2. 토글 상태를 확인한다

**예상 결과**
- 토글이 OFF 상태로 전환된다 (시각적으로 비활성화 상태가 표시된다)

---

## ★ TC 선별 근거

| TC ID | 선별 이유 |
|-------|-----------|
| SC-TPSL-MODL-001 | 모달 오픈 진입점 — 이후 전체 TPSL 기능의 전제 조건 |
| SC-TPSL-MODL-002 | 핵심 Positive — 설정 저장 및 UI 반영 검증 |
| SC-TPSL-MODL-004 | 핵심 Negative — 0 입력 시 저장 차단 검증 (서비스 진입 차단 조건) |
| SC-TPSL-TOGL-001 | 핵심 Positive — 토글 ON 전환, 가장 기본적인 사용 흐름 |
| SC-TPSL-TOGL-002 | 핵심 Positive — 토글 ON 상태의 실제 주문 연동 동작 검증 |
