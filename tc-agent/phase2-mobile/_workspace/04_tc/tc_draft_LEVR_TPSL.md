# TC 초안 — LEVR / TPSL 도메인 (F-022~F-041)

> 작성 일시: 2026-04-02
> 적용 규칙: common/tc-rules.md + phase2-mobile/tc-rules-override.md
> 담당 기능: F-022~F-041 (20개)
> 작성 TC 수: 32개

---

## [LEVR] 레버리지 도메인 — F-022~F-030

---

### ★ LEVR-CNST-001 — 레버리지 슬라이더 최대값 2배 제한 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- 온보딩이 완료된 상태이다
- TradingPage(`/trade`)에 접속해 있다
- LeverageNotice 팝업을 이미 확인한 상태이다

**테스트 단계**
1. OrderForm 상단의 레버리지 버튼을 탭한다
2. AdjustLeverage 모달이 열리면 슬라이더의 최대값을 확인한다
3. 슬라이더를 오른쪽 끝까지 드래그한다

**예상 결과**
- AdjustLeverage 모달의 슬라이더 최대값이 2x로 표시된다
- 슬라이더를 오른쪽 끝까지 이동해도 2x를 초과하지 않는다
- 레버리지 입력값이 2 이상으로 설정되지 않는다

---

### ★ LEVR-CNST-002 — 레버리지 슬라이더 최솟값 1배 제한 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- TradingPage(`/trade`)에 접속해 있다
- AdjustLeverage 모달이 열려 있는 상태이다

**테스트 단계**
1. 슬라이더를 왼쪽 끝까지 드래그한다
2. 슬라이더의 최솟값을 확인한다

**예상 결과**
- 슬라이더를 왼쪽 끝까지 이동해도 1x 미만으로 내려가지 않는다
- 레버리지 입력값이 1 미만으로 설정되지 않는다

---

### ★ LEVR-CNST-003 — 신규 계정 기본 레버리지 2배 설정 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 신규 계정으로 온보딩을 방금 완료한 상태이다
- TradingPage(`/trade`)에 처음 진입한 상태이다
- LeverageNotice 팝업을 확인한 직후이다

**테스트 단계**
1. OrderForm 상단의 레버리지 버튼을 탭한다
2. AdjustLeverage 모달이 열리면 현재 설정된 레버리지 값을 확인한다

**예상 결과**
- AdjustLeverage 모달에 현재 레버리지 값이 2x로 표시된다

---

### ★ LEVR-POPUP-001 — LeverageNotice 팝업 최초 1회 노출 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정이다
- TradingPage에 최초 진입하는 상태이다 (LeverageNotice를 한 번도 확인하지 않은 상태)
- 온보딩이 완료된 상태이다

**테스트 단계**
1. 온보딩 완료 후 `Start Trading` 버튼을 탭하여 TradingPage에 진입한다
2. 화면에 팝업이 자동으로 표시되는지 확인한다
3. 팝업 내 문구와 버튼을 확인한다

**예상 결과**
- LeverageNotice 팝업이 자동으로 표시된다
- 팝업 제목에 "Leverage Policy Notice"가 표시된다
- "This account has a maximum leverage limit of 2x under the user protection policy." 문구가 표시된다
- `I Understand` 버튼이 표시된다

**비고**
- [미결] 팝업 내 표시 언어(한국어/영어) 미확정 — 정책 확정 후 문구 검증 필요

---

### ★ LEVR-POPUP-002 — LeverageNotice 팝업 배경 클릭 시 닫힘 불가 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- TradingPage에 최초 진입하여 LeverageNotice 팝업이 표시된 상태이다

**테스트 단계**
1. LeverageNotice 팝업 바깥 영역(배경)을 탭한다
2. 팝업의 표시 상태를 확인한다

**예상 결과**
- 배경 탭 후에도 LeverageNotice 팝업이 닫히지 않고 계속 표시된다
- `I Understand` 버튼 외의 방법으로는 팝업을 닫을 수 없다

---

### ★ LEVR-IUND-001 — "I Understand" 버튼 탭 후 팝업 닫힘 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- TradingPage에 최초 진입하여 LeverageNotice 팝업이 표시된 상태이다

**테스트 단계**
1. LeverageNotice 팝업에서 `I Understand` 버튼을 탭한다
2. 팝업이 닫히는지 확인한다

**예상 결과**
- `I Understand` 버튼 탭 시 팝업이 닫힌다
- TradingPage 메인 화면이 표시된다

---

### LEVR-RPOP-001 — 재방문 시 LeverageNotice 팝업 미표시 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- 이전 세션에서 LeverageNotice 팝업의 `I Understand`를 탭한 계정이다
- TradingPage를 나갔다가 다시 진입하는 상태이다

**테스트 단계**
1. TradingPage(`/trade`)에 재진입한다
2. 화면에 LeverageNotice 팝업이 표시되는지 확인한다

**예상 결과**
- LeverageNotice 팝업이 표시되지 않는다
- TradingPage 메인 화면이 바로 표시된다

**비고**
- [신규] 코드 근거: AppContext의 hasSeenLeverageNotice 상태 유지 여부 (화면 동작 기준으로 검증)

---

### ★ LEVR-NTXT-001 — LeverageNotice 팝업 문구 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정이다
- TradingPage에 최초 진입하여 LeverageNotice 팝업이 표시된 상태이다

**테스트 단계**
1. LeverageNotice 팝업의 본문 텍스트를 확인한다

**예상 결과**
- "This account has a maximum leverage limit of 2x under the user protection policy." 문구가 팝업에 표시된다

**비고**
- [미결] 팝업 문구 언어(한국어/영어) 미확정 — 정책 확정 후 정확한 텍스트 재검증 필요

---

### ★ LEVR-ORDR-001 — LeverageNotice 팝업과 AdjustLeverage 모달 노출 순서 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정이다
- TradingPage에 최초 진입하는 상태이다 (LeverageNotice 미확인 상태)

**테스트 단계**
1. TradingPage에 진입한다
2. 화면에 어떤 UI가 먼저 표시되는지 확인한다
3. LeverageNotice 팝업에서 `I Understand`를 탭한다
4. AdjustLeverage 모달이 표시되는지 확인한다

**예상 결과**
- TradingPage 진입 시 LeverageNotice 팝업이 AdjustLeverage 모달보다 먼저 표시된다
- `I Understand` 탭 후 AdjustLeverage 모달이 표시된다 (또는 TradingPage 메인 화면이 표시되어 레버리지 버튼을 탭해야 모달 진입 가능)

---

### ★ LEVR-SLDR-001 — AdjustLeverage 모달 슬라이더 1~2 범위 제한 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- LeverageNotice 팝업을 이미 확인한 상태이다
- AdjustLeverage 모달이 열려 있는 상태이다

**테스트 단계**
1. AdjustLeverage 모달의 슬라이더를 확인한다
2. 슬라이더를 왼쪽 끝까지 드래그하여 최솟값을 확인한다
3. 슬라이더를 오른쪽 끝까지 드래그하여 최댓값을 확인한다

**예상 결과**
- 슬라이더의 최솟값이 1x이다
- 슬라이더의 최댓값이 2x이다
- 슬라이더 단계가 1x, 2x 두 가지만 선택 가능하다 (step=1)
- 3x 이상 선택이 불가하다

---

### ★ LEVR-SLDR-002 — AdjustLeverage 모달 3배 초과 입력 불가 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- AdjustLeverage 모달이 열려 있고 레버리지 수동 입력 필드가 표시된 상태이다

**테스트 단계**
1. AdjustLeverage 모달의 레버리지 입력 필드에 "3"을 입력한다
2. 입력 결과 및 적용 가능 여부를 확인한다

**예상 결과**
- 레버리지 값이 3으로 설정되지 않는다
- 입력이 차단되거나 자동으로 2로 리셋된다

---

### ★ LEVR-BNNER-001 — AdjustLeverage 모달 경고 배너 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- AdjustLeverage 모달이 열려 있는 상태이다

**테스트 단계**
1. AdjustLeverage 모달 상단의 경고 배너를 확인한다
2. 배너 문구와 색상을 확인한다

**예상 결과**
- AdjustLeverage 모달 상단에 경고 배너가 표시된다
- 배너에 "Max leverage limited to 2x (User Protection)" 문구가 표시된다
- 배너가 노란색 계열 색상으로 표시된다

---

## [TPSL] Auto TP/SL 도메인 — F-031~F-041

---

### ★ TPSL-DFLT-001 — 신규 계정 Auto TP/SL 기본 상태 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 신규 계정으로 온보딩을 방금 완료한 상태이다
- Settings 탭 → Trading Preferences 섹션에 접속해 있다

**테스트 단계**
1. Settings 탭을 탭한다
2. Trading Preferences 섹션을 확인한다
3. Auto TP/SL 토글의 초기 상태를 확인한다
4. TP/SL 수치 표시를 확인한다

**예상 결과**
- Auto TP/SL 토글이 OFF 상태로 표시된다
- TP 수치 표시란에 `--%`가 표시된다
- SL 수치 표시란에 `--%`가 표시된다

**비고**
- [미결] 초기 ON/OFF 여부 미확정 — 정책 확정 후 검증 필요 (F-041)
- [미결] TP 기본값(`DEFAULT_TP_PERCENT=1.8`) 최종 확정 여부 확인 필요 (F-031)
- [미결] SL 기본값(`DEFAULT_SL_PERCENT=5.0`) 최종 확정 여부 확인 필요 (F-032)

---

### ★ TPSL-STAT-001 — Auto TP/SL 전역 상태 관리 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Settings 탭 → Trading Preferences 섹션에서 Auto TP/SL을 ON으로 설정하고 저장한 상태이다

**테스트 단계**
1. Settings 탭에서 Auto TP/SL 토글 상태를 확인한다
2. BottomNav에서 Trade 탭을 탭하여 TradingPage로 이동한다
3. OrderForm에서 Auto TP/SL 관련 인디케이터가 표시되는지 확인한다
4. 다시 Settings 탭으로 이동하여 Auto TP/SL 토글 상태를 확인한다

**예상 결과**
- Trade 탭 이동 후 OrderForm에 TP%/SL% 값과 Edit 버튼이 표시된다
- Settings 탭으로 돌아와도 Auto TP/SL이 ON 상태로 유지된다

**비고**
- [신규] 코드 근거: AppContext의 autoTpSlEnabled 전역 상태 관리 (화면 동작 기준으로 검증)

---

### ★ TPSL-MODL-001 — AutoTpSlModal 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Settings 탭 → Trading Preferences 섹션에 접속해 있다

**테스트 단계**
1. Trading Preferences 섹션의 Auto TP/SL `Edit` 버튼을 탭한다
2. 모달이 표시되는지 확인한다
3. 모달 내 구성 요소를 확인한다

**예상 결과**
- AutoTpSlModal이 화면에 표시된다
- TP 입력 필드가 표시된다
- SL 입력 필드가 표시된다
- 확인(저장) 버튼이 표시된다

---

### ★ TPSL-MODL-002 — AutoTpSlModal 확인 버튼 활성화 조건 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 표시된 상태이다
- TP 입력 필드와 SL 입력 필드가 모두 0 또는 빈칸 상태이다

**테스트 단계**
1. TP 입력 필드에 `1.8`을 입력한다
2. 확인 버튼의 활성화 상태를 확인한다

**예상 결과**
- TP 값(`1.8`) 입력 후 확인 버튼이 활성화된다

---

### ★ TPSL-MODL-003 — AutoTpSlModal 확인 버튼 비활성화 조건 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 표시된 상태이다

**테스트 단계**
1. TP 입력 필드를 비워 두거나 0으로 설정한다
2. SL 입력 필드를 비워 두거나 0으로 설정한다
3. 확인 버튼의 활성화 상태를 확인한다

**예상 결과**
- TP와 SL 모두 0 또는 빈칸인 경우 확인 버튼이 비활성화(disabled) 상태이다
- 버튼을 탭해도 저장 동작이 발생하지 않는다

---

### ★ TPSL-ORDF-001 — Auto TP/SL ON 시 OrderForm 인디케이터 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Auto TP/SL이 ON 상태이고 TP: 1.8%, SL: 5.0%로 설정된 상태이다
- TradingPage(`/trade`)의 OrderForm이 표시된 상태이다

**테스트 단계**
1. OrderForm 하단의 Auto TP/SL 인디케이터 영역을 확인한다
2. 표시된 TP%, SL% 값과 Edit 버튼을 확인한다

**예상 결과**
- OrderForm에 `TP: +1.8%` 또는 해당 TP 비율이 표시된다
- OrderForm에 `SL: -5.0%` 또는 해당 SL 비율이 표시된다
- `Edit` 버튼이 함께 표시된다

**비고**
- [미결] TP 기본값(`DEFAULT_TP_PERCENT=1.8`) 최종 확정 여부 확인 필요 (F-031)
- [미결] SL 기본값(`DEFAULT_SL_PERCENT=5.0`) 최종 확정 여부 확인 필요 (F-032)

---

### ★ TPSL-ORDF-002 — Auto TP/SL OFF 시 OrderForm 인디케이터 미표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Auto TP/SL이 OFF 상태이다
- TradingPage(`/trade`)의 OrderForm이 표시된 상태이다

**테스트 단계**
1. OrderForm 하단의 Auto TP/SL 인디케이터 영역을 확인한다

**예상 결과**
- OrderForm에 TP%/SL% 인디케이터가 표시되지 않는다 (빈칸 또는 해당 영역 미표시)

---

### ★ TPSL-PSTN-001 — Auto 포지션에 녹색 Auto 배지 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Auto TP/SL이 ON 상태에서 주문을 체결하여 포지션이 생성된 상태이다
- Dashboard 탭의 Positions 목록에 해당 포지션이 표시된 상태이다

**테스트 단계**
1. Dashboard 탭을 탭한다
2. Positions 목록에서 Auto TP/SL이 적용된 포지션 카드를 확인한다
3. 포지션 카드의 배지를 확인한다

**예상 결과**
- Auto TP/SL이 적용된 포지션 카드에 녹색 "Auto" 배지가 표시된다

---

### ★ TPSL-PSTN-002 — PositionCard TP/SL 조건부 렌더링 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Auto TP/SL이 ON 상태에서 주문을 체결하여 TP와 SL이 설정된 포지션이 존재하는 상태이다
- Dashboard 탭의 Positions 목록에 해당 포지션이 표시된 상태이다

**테스트 단계**
1. Dashboard 탭 → Positions 목록에서 Auto TP/SL이 적용된 포지션 카드를 확인한다
2. 포지션 카드에 TP, SL 값이 표시되는지 확인한다

**예상 결과**
- TP 값이 설정된 포지션 카드에 TP 정보가 표시된다
- SL 값이 설정된 포지션 카드에 SL 정보가 표시된다

---

### TPSL-PSTN-003 — TP/SL 미설정 포지션 카드에서 TP/SL 미표시 확인 [신규]

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Dashboard 탭) |

**사전 조건**
- Auto TP/SL이 OFF 상태에서 주문을 체결하여 TP/SL이 없는 포지션이 존재하는 상태이다
- Dashboard 탭의 Positions 목록에 해당 포지션이 표시된 상태이다

**테스트 단계**
1. Dashboard 탭 → Positions 목록에서 TP/SL이 설정되지 않은 포지션 카드를 확인한다
2. 포지션 카드에 TP, SL 영역이 표시되는지 확인한다

**예상 결과**
- TP/SL이 설정되지 않은 포지션 카드에 TP/SL 정보가 표시되지 않는다

**비고**
- [신규] 코드 근거: PositionCard의 position.tp / position.sl 값 존재 여부에 따른 조건부 렌더링 (화면 동작 기준으로 검증)

---

### ★ TPSL-TOGL-001 — SettingsPage Auto TP/SL 토글 ON 전환 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Settings 탭 → Trading Preferences 섹션에 접속해 있다
- Auto TP/SL 토글이 현재 OFF 상태이다

**테스트 단계**
1. Auto TP/SL 토글을 탭하여 ON으로 전환한다
2. 토글 색상 변화를 확인한다

**예상 결과**
- Auto TP/SL 토글이 ON 상태로 전환된다
- 토글 색상이 녹색으로 변경된다

---

### ★ TPSL-TOGL-002 — SettingsPage Auto TP/SL 토글 OFF 전환 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- Auto TP/SL 토글이 현재 ON 상태(녹색)이다
- Settings 탭 → Trading Preferences 섹션에 접속해 있다

**테스트 단계**
1. Auto TP/SL 토글을 탭하여 OFF로 전환한다
2. 토글 색상 변화를 확인한다

**예상 결과**
- Auto TP/SL 토글이 OFF 상태로 전환된다
- 토글 색상이 기본 배경 색상으로 변경된다

---

### ★ TPSL-PATH-001 — Settings → Trading Preferences → Auto TP/SL Edit 진입 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- TradingPage에 접속해 있다

**테스트 단계**
1. BottomNav에서 Settings 탭을 탭한다
2. Trading Preferences 섹션을 확인한다
3. Auto TP/SL 항목 옆의 `Edit` 버튼을 탭한다
4. AutoTpSlModal이 표시되는지 확인한다

**예상 결과**
- Settings 탭 → Trading Preferences 섹션이 표시된다
- Auto TP/SL `Edit` 버튼이 표시된다
- `Edit` 버튼 탭 시 AutoTpSlModal이 표시된다

---

### ★ TPSL-INIT-001 — 신규 계정 Auto TP/SL 초기 ON/OFF 상태 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 신규 계정으로 온보딩을 방금 완료한 상태이다

**테스트 단계**
1. Settings 탭 → Trading Preferences 섹션을 확인한다
2. Auto TP/SL 토글의 초기 상태를 확인한다

**예상 결과**
- Auto TP/SL 토글의 초기 상태가 명확하게 ON 또는 OFF 중 하나로 표시된다

**비고**
- [미결] 초기 ON/OFF 여부 미확정 — 정책 확정 후 예상 결과의 초기값 지정 필요 (F-041)

---

### TPSL-SAVE-001 — Auto TP/SL 설정값 저장 성공 Toast 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있는 상태이다
- TP에 `1.8`, SL에 `5.0`이 입력된 상태이다

**테스트 단계**
1. AutoTpSlModal에서 확인(저장) 버튼을 탭한다
2. Toast 메시지가 표시되는지 확인한다

**예상 결과**
- `Auto TP/SL settings saved.` Toast 메시지가 표시된다
- AutoTpSlModal이 닫힌다
- Settings → Trading Preferences에서 TP: 1.8%, SL: 5.0%로 표시된다

---

### TPSL-BDRY-001 — TP 입력 최솟값 0.1% 미만 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있는 상태이다

**테스트 단계**
1. TP 입력 필드에 `0`을 입력한다
2. 확인 버튼의 활성화 상태를 확인한다
3. 저장 시 동작을 확인한다

**예상 결과**
- TP 값 0 입력 시 입력이 차단되거나 저장이 불가하다
- 확인 버튼이 비활성화 상태이거나 오류 메시지가 표시된다

---

### TPSL-BDRY-002 — SL 입력 최댓값 99.9% 초과 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있는 상태이다

**테스트 단계**
1. SL 입력 필드에 `100`을 입력한다
2. 입력 결과 및 저장 가능 여부를 확인한다

**예상 결과**
- SL 값이 99.9%를 초과하여 저장되지 않는다
- 입력이 차단되거나 자동으로 99.9 이하로 리셋된다

---

### TPSL-BDRY-003 — TP/SL 음수 입력 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있는 상태이다

**테스트 단계**
1. TP 입력 필드에 `-1`을 입력한다
2. 입력 결과를 확인한다

**예상 결과**
- 음수 입력이 차단되어 필드에 `-1`이 입력되지 않는다

---

### TPSL-BDRY-004 — TP/SL 소수점 2자리 이상 입력 제한 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있는 상태이다

**테스트 단계**
1. TP 입력 필드에 `1.85`를 입력한다
2. 입력 결과를 확인한다

**예상 결과**
- 소수점 2자리 이상 입력이 차단되거나 소수점 1자리로 자동 반올림된다

---

### ★ TPSL-STNG-001 — Settings Trading Preferences Auto TP/SL 현재 설정값 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | High |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 로그인한 상태이다
- Auto TP/SL이 ON이고 TP: 1.8%, SL: 5.0%로 설정 저장된 상태이다
- Settings 탭 → Trading Preferences 섹션에 접속해 있다

**테스트 단계**
1. Trading Preferences 섹션의 Auto TP/SL 항목을 확인한다
2. 현재 설정된 TP와 SL 수치가 표시되는지 확인한다

**예상 결과**
- Auto TP/SL 항목에 현재 설정된 TP 비율(예: `1.8%`)이 표시된다
- Auto TP/SL 항목에 현재 설정된 SL 비율(예: `5.0%`)이 표시된다
- `Edit` 버튼이 함께 표시된다

---

### LEVR-COIN-001 — 코인 변경 시 레버리지 2배 자동 변경 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- Open Orders 및 Position이 없는 상태이다
- 현재 선택된 코인의 레버리지가 1x로 설정된 상태이다

**테스트 단계**
1. CoinSelector에서 다른 코인을 선택한다 (예: BTC → ETH)
2. OrderForm 상단의 레버리지 표시값을 확인한다

**예상 결과**
- 코인 변경 후 레버리지가 2x로 자동 변경된다
- OrderForm 상단에 2x 레버리지가 표시된다

---

### LEVR-COIN-002 — 포지션 보유 중 코인 변경 시 기존 레버리지 유지 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- 1x 레버리지로 포지션 또는 Open Orders를 보유한 상태이다

**테스트 단계**
1. CoinSelector에서 다른 코인을 선택한다
2. OrderForm 상단의 레버리지 표시값을 확인한다

**예상 결과**
- 포지션/Open Orders 보유 중에는 코인 변경 시 레버리지가 강제로 2x로 변경되지 않는다
- 기존 설정된 레버리지 값이 유지된다

---

### LEVR-MRGIN-001 — 기존 포지션 레버리지 낮추기 성공 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- YOUTHMETA 파트너코드로 가입한 계정으로 TradingPage에 접속해 있다
- 2x 레버리지 포지션이 존재하고 Margin이 충분한 상태이다
- AdjustLeverage 모달이 열려 있는 상태이다

**테스트 단계**
1. AdjustLeverage 모달에서 슬라이더를 1x로 변경한다
2. 확인 버튼을 탭한다
3. 변경 결과를 확인한다

**예상 결과**
- 레버리지가 1x로 성공적으로 변경된다
- OrderForm 상단에 1x 레버리지가 표시된다

---

### TPSL-ORDF-003 — Auto TP/SL ON 상태에서 주문 시 OrderForm TP/SL 자동 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- Auto TP/SL이 ON 상태이고 TP: 1.8%, SL: 5.0%로 설정된 상태이다
- TradingPage OrderForm이 표시된 상태이다

**테스트 단계**
1. OrderForm에서 코인을 선택하고 주문 유형을 Market으로 설정한다
2. OrderForm 하단의 TP/SL 표시 영역을 확인한다

**예상 결과**
- OrderForm 하단 TP/SL 항목에 Settings에서 설정한 값이 자동으로 표시된다
- 표시 형식이 `TP: +1.8% / SL: -5.0%` 또는 유사한 형태로 표시된다

---

### TPSL-PRTY-001 — Auto TP/SL ON 상태에서 수동 TP/SL 입력 시 수동값 우선 적용 확인

| 항목 | 내용 |
|------|------|
| 분류 | Positive |
| 우선순위 | Medium |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- Auto TP/SL이 ON 상태이고 TP: 1.8%, SL: 5.0%로 설정된 상태이다
- TradingPage OrderForm에서 주문 설정 중인 상태이다

**테스트 단계**
1. OrderForm의 TP/SL Edit 버튼을 탭하여 AutoTpSlModal을 연다
2. TP 값을 `3.0`으로 수정하고 확인한다
3. 주문을 체결한다
4. Dashboard Positions 탭에서 생성된 포지션의 TP 값을 확인한다

**예상 결과**
- 체결된 포지션의 TP 값이 Auto 기본값(1.8%)이 아닌 수동 입력값(3.0%)으로 적용된다

---

### TPSL-ERRL-001 — Auto TP/SL 설정 저장 실패 시 오류 Toast 표시 확인

| 항목 | 내용 |
|------|------|
| 분류 | Negative |
| 우선순위 | Medium |
| 플랫폼 | 공통 |
| 연관 화면 | /trade (Settings 탭) |

**사전 조건**
- AutoTpSlModal이 열려 있고 유효한 TP/SL 값이 입력된 상태이다
- 네트워크 오류 또는 서버 오류 상황이 시뮬레이션된 상태이다

**테스트 단계**
1. 확인(저장) 버튼을 탭한다
2. Toast 메시지가 표시되는지 확인한다

**예상 결과**
- 오류 Toast 메시지가 표시된다
- 기존에 저장된 TP/SL 값이 Settings 화면에서 유지된다

**비고**
- [미결] 저장 실패 시 정확한 Toast 오류 문구 미확정 — 정책 확정 필요

---

### LEVR-INPT-001 — AdjustLeverage 소수점 입력 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- AdjustLeverage 모달이 열려 있고 레버리지 수동 입력 필드가 표시된 상태이다

**테스트 단계**
1. 레버리지 입력 필드에 `1.5`를 입력한다
2. 입력 결과를 확인한다

**예상 결과**
- 소수점 입력이 차단되어 `1.5`가 입력되지 않는다
- 정수(1 또는 2)만 입력 가능하다

---

### LEVR-INPT-002 — AdjustLeverage 0 입력 차단 확인

| 항목 | 내용 |
|------|------|
| 분류 | Edge |
| 우선순위 | Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /trade |

**사전 조건**
- AdjustLeverage 모달이 열려 있고 레버리지 수동 입력 필드가 표시된 상태이다

**테스트 단계**
1. 레버리지 입력 필드에 `0`을 입력한다
2. 입력 결과 및 저장 가능 여부를 확인한다

**예상 결과**
- 0 입력이 차단되거나 저장이 불가하다

---

## TC 커버리지 요약

| 기능 ID | 기능명 | 담당 TC |
|---------|--------|---------|
| F-022 | MAX_LEVERAGE=2 상수 적용 | LEVR-CNST-001, LEVR-SLDR-001, LEVR-SLDR-002 |
| F-023 | MIN_LEVERAGE=1 상수 적용 | LEVR-CNST-002, LEVR-SLDR-001 |
| F-024 | DEFAULT_LEVERAGE=2 기본값 적용 | LEVR-CNST-003 |
| F-025 | LeverageNotice 팝업 최초 1회 표시 | LEVR-POPUP-001, LEVR-RPOP-001 |
| F-026 | LeverageNotice 팝업 문구 표시 | LEVR-NTXT-001 |
| F-027 | LeverageNotice "I Understand" 버튼 동작 | LEVR-POPUP-002, LEVR-IUND-001 |
| F-028 | LeverageNotice와 AdjustLeverage 노출 순서 | LEVR-ORDR-001 |
| F-029 | AdjustLeverage 슬라이더 범위 제한 | LEVR-SLDR-001, LEVR-SLDR-002, LEVR-INPT-001, LEVR-INPT-002 |
| F-030 | AdjustLeverage 모달 경고 배너 표시 | LEVR-BNNER-001 |
| F-031 | DEFAULT_TP_PERCENT=1.8 상수 적용 | TPSL-DFLT-001, TPSL-ORDF-001 |
| F-032 | DEFAULT_SL_PERCENT=5.0 상수 적용 | TPSL-DFLT-001, TPSL-ORDF-001 |
| F-033 | autoTpSlEnabled 전역 상태 관리 | TPSL-STAT-001 |
| F-034 | AutoTpSlModal 표시 | TPSL-MODL-001, TPSL-PATH-001 |
| F-035 | AutoTpSlModal 확인 버튼 활성화 조건 | TPSL-MODL-002, TPSL-MODL-003 |
| F-036 | OrderForm Auto TP/SL 인디케이터 표시 | TPSL-ORDF-001, TPSL-ORDF-002 |
| F-037 | PositionCard Auto 배지 표시 | TPSL-PSTN-001 |
| F-038 | PositionCard TP/SL 조건부 렌더링 | TPSL-PSTN-002, TPSL-PSTN-003 |
| F-039 | SettingsPage Auto TP/SL 토글 스위치 | TPSL-TOGL-001, TPSL-TOGL-002 |
| F-040 | Settings → Auto TP/SL Edit 접근 | TPSL-PATH-001 |
| F-041 | Auto TP/SL 초기 기본 상태 | TPSL-INIT-001, TPSL-DFLT-001 |

---

## ★ TC 목록 (최소 TC 세트)

총 32개 중 ★ 표시 TC: 19개 (59.4% — High+Positive 전체 및 핵심 Negative 포함)

| TC ID | 제목 요약 | 분류 | 우선순위 |
|-------|-----------|------|----------|
| LEVR-CNST-001 | 레버리지 슬라이더 최대값 2배 제한 확인 | Positive | High |
| LEVR-CNST-002 | 레버리지 슬라이더 최솟값 1배 제한 확인 | Positive | High |
| LEVR-CNST-003 | 신규 계정 기본 레버리지 2배 설정 확인 | Positive | High |
| LEVR-POPUP-001 | LeverageNotice 팝업 최초 1회 노출 확인 | Positive | High |
| LEVR-POPUP-002 | LeverageNotice 팝업 배경 클릭 시 닫힘 불가 확인 | Negative | High |
| LEVR-IUND-001 | "I Understand" 버튼 탭 후 팝업 닫힘 확인 | Positive | High |
| LEVR-NTXT-001 | LeverageNotice 팝업 문구 표시 확인 | Positive | High |
| LEVR-ORDR-001 | LeverageNotice와 AdjustLeverage 모달 노출 순서 확인 | Positive | High |
| LEVR-SLDR-001 | AdjustLeverage 모달 슬라이더 1~2 범위 제한 확인 | Positive | High |
| LEVR-SLDR-002 | AdjustLeverage 모달 3배 초과 입력 불가 확인 | Negative | High |
| LEVR-BNNER-001 | AdjustLeverage 모달 경고 배너 표시 확인 | Positive | High |
| TPSL-DFLT-001 | 신규 계정 Auto TP/SL 기본 상태 확인 | Positive | High |
| TPSL-STAT-001 | Auto TP/SL 전역 상태 관리 확인 | Positive | High |
| TPSL-MODL-001 | AutoTpSlModal 표시 확인 | Positive | High |
| TPSL-MODL-002 | AutoTpSlModal 확인 버튼 활성화 조건 확인 | Positive | High |
| TPSL-MODL-003 | AutoTpSlModal 확인 버튼 비활성화 조건 확인 | Negative | High |
| TPSL-ORDF-001 | Auto TP/SL ON 시 OrderForm 인디케이터 표시 확인 | Positive | High |
| TPSL-ORDF-002 | Auto TP/SL OFF 시 OrderForm 인디케이터 미표시 확인 | Positive | High |
| TPSL-PSTN-001 | Auto 포지션에 녹색 Auto 배지 표시 확인 | Positive | High |
| TPSL-PSTN-002 | PositionCard TP/SL 조건부 렌더링 확인 | Positive | High |
| TPSL-TOGL-001 | SettingsPage Auto TP/SL 토글 ON 전환 확인 | Positive | High |
| TPSL-TOGL-002 | SettingsPage Auto TP/SL 토글 OFF 전환 확인 | Positive | High |
| TPSL-PATH-001 | Settings → Trading Preferences → Auto TP/SL Edit 진입 확인 | Positive | High |
| TPSL-INIT-001 | 신규 계정 Auto TP/SL 초기 ON/OFF 상태 확인 | Positive | High |
| TPSL-STNG-001 | Settings Trading Preferences Auto TP/SL 현재 설정값 표시 확인 | Positive | High |
