# Supercycl TC 생성 핵심 규칙 (최우선)

> 이 파일은 `load_project_policies()` 정렬 상 맨 앞에 오므로 프롬프트에 가장 확실히 포함된다.
> `common/tc-rules.md` 섹션 1-1, 1-2의 Supercycl 프로젝트 적용판 요약.

---

## 1. TC ID 발번 규칙 (강제)

### 형식

| Project | ProjectCode | 스킴 | 예시 |
|---------|-------------|------|------|
| PC Web | `SC` | **Suite-based** (기능 단위) | `SC-GNBF-001`, `SC-TRD-ORDR-012` |
| Mobile Web | `SM` | **Screen-based** (화면 단위) | `SM-SPL-001`, `SM-VCD-008` |
| Mobile App (향후) | `SA` | Screen-based | `SA-SPL-001` |

### Mobile (SM) — Screen-based 스킴

- **SuiteCode 자리에 ScreenCode를 사용**한다.
- ScreenCode는 `screen_code_map.md`에 정의된 3~4자 대문자 코드.
- 맵에 없는 중분류는 자동 파생 (영문자 3자 uppercase).
- **NNN은 화면별 001부터 시작**. 각 화면은 독립된 번호 네임스페이스를 가진다.

### ⚠️ 과거 버그와 비교

| ❌ 과거 중복 버그 | ✅ Screen-based 적용 |
|------------------|---------------------|
| `SM-ONBD-001` (Splash) | `SM-SPL-001` (Splash 1번) |
| `SM-ONBD-001` (Login, 중복!) | `SM-LGI-001` (Login Options 1번) |
| `SM-ONBD-001` (Email, 중복!) | `SM-EML-001` (Email Input 1번) |
| `SM-ONBD-001` (Verify, 중복!) | `SM-VCD-001` (Verification Code 1번) |

- 화면코드가 다르므로 **NNN이 리셋되어도 전역 유니크 보장**.
- TC ID만 봐도 어느 화면인지 즉시 식별 가능 (`SPL`, `LGI`, `EML`, `VCD`).
- 스펙의 SCR-ID(SCR-001 Splash 등)와 1:1 대응.

### Screen Code 조회 우선순위

1. `projects/supercycl/screen_code_map.md`의 매핑 테이블 검색 (정확 일치)
2. 없으면 자동 파생: 영문자 3자 uppercase
3. 한글만 있는 경우 해시 기반 `MID###`

생성기는 프롬프트에 해당 화면의 `ScreenCode`와 `starting_seq=1`을 전달하고,
호출 후 `renumber_tc_ids()`가 화면 내 001~NNN 연속 증가를 강제한다.

---

## 2. 스펙 기반 생성 4원칙 (추측 금지)

### 원칙 A. 스펙에 없는 시나리오 TC 생성 금지

| 금지 유형 | 처리 |
|---------|------|
| 오프라인/네트워크 끊김 (스펙에 언급 없을 때) | `[미결]` 태그로 비고에만 기록, TC 생성 X |
| 성능 임계치 ("3초 이내" 등 스펙에 없는 수치) | TC 생성 X |
| 로그인 상태에서 특정 URL 접근 리다이렉트 (라우팅 정책 미명시) | `[미결]` |

### 원칙 B. 에러 케이스 테이블 → Negative TC 1:1

기획서의 `에러 케이스` 표 한 행 = 정확히 1개 Negative TC. 메시지 텍스트는 원문 그대로.

- 스펙에 에러 테이블이 **없는 화면**은 Negative TC를 생성하지 않는다.
- 테이블이 5행이면 → 정확히 5개의 Negative TC.

### 원칙 C. Deferred / Archived 화면 제외

스펙의 화면 목록 `상태 (status)` 컬럼이 `deferred` 또는 `archived`면 TC 생성 대상에서 완전 제외.

- `deferred`: 다른 화면의 상태 변형 (별도 목업 없음) — 원본 화면 TC에 흡수
- `archived`: 폐기된 화면

### 원칙 D. Visual 속성 통합 (1 TC per screen)

색·폰트·radius·여백은 화면당 **1개의 "UI Spec Compliance" TC**로 묶는다. 분할 금지.

```
❌ TC-001: 배경색 #000000 / TC-002: 슬로건 텍스트 / TC-003: 버튼 radius
✅ TC-001: 디자인 토큰 준수 — 배경/슬로건/버튼 스타일 일괄 확인
```

### 원칙 E. 비기능 TC는 화면 성격 기반 조건부 생성

`screen_code_map.md`의 **"성격"** 컬럼 기준으로 필수 비기능 TC를 추가한다.

| 성격 | Supercycl 예시 | 필수 비기능 TC |
|------|---------------|--------------|
| entry | Splash, Login Options | 로딩 시간 3초 (Google RAIL) |
| data-fetch | Markets, Portfolio, Order History, PnL | 초기 로딩 5초 + 빈 상태 + 새로고침 |
| realtime | Trade Lite, Positions | WebSocket 끊김 복원 + 지연 배너 |
| form | Email Input, Amount 입력 | 입력 반응 100ms (선택) |
| overlay | Coin Selector, Margin Mode Sheet | 외부 탭 닫힘 + 애니메이션 |
| static | Terms of Use, Privacy, Guide | 비기능 TC 없음 |

**중요**: 임계치 수치(3초, 5초 등)는 업계 표준이므로 TC 생성 시 반드시 `[미결]` 태그로 "임계치 PM 확정 필요" 비고 추가.

**Splash 화면 예상 TC 수**: 3개 → **4개** (로딩 시간 TC 1개 추가)

### 원칙 F. 네비게이션 동작은 화면 분류 기반 조건부 TC 생성

`screen_code_map.md`의 **"네비" 컬럼** 기준으로 뒤로가기/스와이프 TC 추가. 성격과 **직교** — Splash/Login Complete 모두 `entry`지만 네비는 다름.

| 네비 | Supercycl 예시 | 필수 TC |
|------|---------------|--------|
| `tab-root` | Splash, Markets, Trade Lite, Portfolio, Profile | 뒤로가기 시 앱 종료 확인 또는 Splash |
| `one-way` | **Login Complete**, Verifying Code, Order Success/Failed, QR Scan Complete, Connection Result | **뒤로가기/스와이프 차단** (이전 화면 복귀 금지) |
| `sequential` | Email Input, Verification Code, Terms Consent, OAuth Connect | 이전 단계 복귀 + 입력값 유지 |
| `overlay` | Coin Selector, Margin Mode Sheet, Cancel Order Modal | 뒤로가기/외부 탭 → 모달만 닫힘 |
| `detail` | Order History, PnL Analysis, Exchange Detail, Notifications | 리스트 복귀 + 스크롤 위치 유지 |
| `static` | Terms of Use, Privacy, Guide | 자연스러운 상위 복귀 (별도 TC 불필요) |

**사용자 지적 케이스 (one-way) — Login Complete 뒤로가기**:
- 로그인 완료 후 뒤로가기 → Verification Code/Email Input으로 돌아가면 **안 됨**
- 기대 동작: 홈 이동, 차단, 또는 로그아웃 확인 모달 중 하나
- 임계치/구현 방식은 `[미결]` PM 확정 필요

**Login Complete 화면 예상 TC 수**: 2~3개 → **4~5개** (네비 TC 1~2개 추가)

---

## 3. 화면별 TC 수량 쿼터 (리스크 기반)

```
Impact 가중치:
  자산/거래 (Trade/Order)      = 5
  보안/인증 (Login/OAuth)      = 4
  데이터 (Portfolio/History)   = 3
  설정 (Settings/Profile)      = 2
  브랜딩 (Splash/Guide)        = 1

화면당 권장 TC 수:
  Impact 1 + 에러 0~1건  →  3~4개 (Splash 등)
  Impact 2 + 에러 1~3건  →  5~8개
  Impact 3 + 에러 2~5건  →  7~12개
  Impact 4 + 에러 3~7건  →  10~15개
  Impact 5 + 에러 5+건   →  15~20개
```

**강제**: Splash/Guide 같은 단순 화면에 10개 이상 TC 생성 금지. 대부분 3~4개로 충분.

---

## 4. TC 생성 Pre-flight 체크리스트

각 화면 TC 작성 전 반드시 확인:

- [ ] 화면 `status`가 `active`인가? (`deferred`/`archived` 제외)
- [ ] Impact 수준 판정 → 권장 TC 수 범위 확인
- [ ] 스펙의 `에러 케이스` 테이블 존재 여부 확인 → Negative TC 개수 결정
- [ ] 시각 속성은 1개 "UI Spec Compliance" TC로 통합했는가?
- [ ] 오프라인/타임아웃/성능 TC는 스펙 명시가 있을 때만 생성했는가?
- [ ] 카테고리 1(UI/UX) TC가 화면당 1개로 제한되는가? (분할 금지)

---

## 5. Mobile Web 전용 추가 사항

- ProjectCode: `SM`
- 사전 조건에 "모바일 브라우저(iOS Safari / Android Chrome)에서 접속한 상태" 포함
- SuiteCode는 PC Web(`SC`)과 동일 이름 사용 (LOGN, TRD-ORDR 등) — 플랫폼 간 통일
- 소분류만 모바일 UI 용어(바텀시트, 스와이프 등)로 자유 작성 허용
