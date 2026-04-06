# TC Policy — Youthmeta Leverage 2x 제한 정책
**문서 버전:** v1.0
**기준 날짜:** 2026-03-18
**적용 범위:** Youthmeta 파트너 계정 레버리지 제한 기능

---

## 1. 기능 개요

Supercycl에서 Youthmeta 파트너 코드로 회원가입한 계정은 **레버리지가 최대 2배로 제한**된다.
일반 계정은 이 제한이 적용되지 않는다.

---

## 2. 계정 조건

| 조건 | 적용 여부 |
|------|-----------|
| `partner_code=YOUTHMETA`로 가입한 계정 | ✅ 레버리지 2x 제한 |
| 일반 계정 (파트너 코드 없음) | ❌ 미적용 (기존 거래소 최대 레버리지 사용) |

---

## 3. 레버리지 제한 동작 규칙

### 3.1 코인 페어 변경 시
- 다른 coin pair 선택 시 → 해당 코인의 레버리지가 **자동으로 2x로 변경**
- 조건: Position, Open Orders가 없는 상태

### 3.2 포지션/오더 보유 상태
- **Position 또는 Open Orders를 보유한 경우** → 기존 설정된 레버리지 유지
- 강제 변경 없음

### 3.3 Position Mode별 동작

| Position Mode | 동작 |
|---------------|------|
| One-Way Mode | 레버리지 2x로 자동 변경 |
| Hedge Mode + Cross | Long / Short 공통 2x로 자동 변경 |
| Hedge Mode + Isolated | Long 2x / Short 2x 각각 변경 |

### 3.4 레버리지 직접 입력 제한
- **슬라이더 범위:** 1x ~ 2x (이 범위 밖으로 이동 불가)
- **숫자 입력:** 정수(1, 2)만 허용 / 소수점 불가 / 0 입력 불가
- **3 이상 입력:** 입력 불가 또는 자동으로 2로 리셋

### 3.5 거래소 외부에서 3x 이상 설정 후 복귀
- 거래소 앱/웹에서 3x 이상으로 레버리지 설정 후 Supercycl 접속
- Order Form 상단: 현재 설정된 레버리지로 표시
- Adjust Leverage 모달: 현재 레버리지로 표시
- **Confirm 클릭 시:** 레버리지가 2x로 변경됨

### 3.6 기존 포지션 레버리지 수정 시
- 기존 고레버리지 포지션의 레버리지를 낮출 수 있음
- Margin이 충분하면: 변경 성공
- **Margin 부족 시:** 에러 토스트 팝업 표시, 기존 레버리지 유지

---

## 4. UI 요소 상세

### 4.1 Adjust Leverage 모달 진입
- **트리거:** Order Form 상단 레버리지 버튼 클릭
- **경고 배너:** `Max leverage limited to 2x` (노란색, 모달 상단 항상 표시)

### 4.2 최초 로그인 팝업 (Leverage Policy Notice)
```
Leverage Policy Notice

This account has a maximum leverage
limit of 2x under the user protection policy.

[I Understand] 버튼
```

**팝업 동작 규칙:**
- 최초 1회만 표시
- 배경 클릭으로 닫기 불가 (필수 확인 모달)
- `[I Understand]` 클릭 후 닫힘
- 이후 재로그인 / 새로고침 시 재표시 안 됨

### 4.3 최초 로그인 팝업 노출 순서
로그인 방식에 따라 모달 노출 순서:
- **구글/이메일:** 약관 동의 → 2배 레버리지 안내
- **지갑:** 지갑 서명 → 약관 동의 → 2배 레버리지 안내

---

## 5. API 확인 방법

### 5.1 파트너 코드 등록 확인
브라우저 개발자 도구 > Network 탭 > `info` API 응답:

```json
// Youthmeta 계정 (등록됨)
"partner": {
  "no": 1,
  "name": "Youthmeta",
  "code": "Youthmeta"
}

// 일반 계정 (미등록)
"partner": null
```

---

## 6. TC 작성 시 전제 조건 패턴

### 6.1 표준 전제 조건 (Leverage)

```
GIVEN:
1. Youthmeta 파트너 코드로 회원가입한 계정으로 로그인한 상태
2. Trade 메뉴인 상태
3. [추가 조건 — 아래 중 해당하는 것 선택]
   - Open Orders, Position이 없는 상태
   - 기존 {nx} 레버리지 포지션 보유 상태
   - Adjust Leverage 모달 진입 상태
   - Hedge Mode + Cross 상태
   - Hedge Mode + Isolated 상태
```

---

## 7. TC 범위 및 카테고리

| 카테고리 | 세부 항목 | Phase |
|----------|-----------|-------|
| 로그인 | 비대상자 확인, 파트너 계정 최초 로그인, 팝업 동작 | Phase 01~02 |
| Leverage 제한 UI | 거래소 리스트, 경고 배너, 슬라이더 제한 | Phase 04 |
| Leverage 동작 | 코인 변경, 포지션 모드별, 레버리지 직접 입력 | Phase 04 |
| 기존 포지션 | 5x 포지션 유지, 수정, 추가 주문 | Phase 14 |
| 경계값 | 1x/2x 최소최대, 소수점 불가, 0 불가 | Phase 15 |

---

## 8. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| v1.0 | 2026-03-18 | 최초 작성 |
