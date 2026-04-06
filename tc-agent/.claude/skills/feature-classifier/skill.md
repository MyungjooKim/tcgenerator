---
name: feature-classifier
description: "기능 목록(feature_list.md)을 읽고 대분류/중분류/소분류 계층 구조로 분류표 초안을 자동 생성하는 스킬. TC 파이프라인의 Human Gate 전 단계. 'TC 분류표 만들어줘', '기능 분류 초안', '대분류/중분류/소분류 정리', '분류표 생성' 요청 시 반드시 이 스킬을 사용할 것."
---

# Feature Classifier

feature_list.md를 읽고 기능들을 대분류/중분류/소분류 3단계 계층으로 분류한 초안(classification_draft.md)을 생성한다.
이 초안은 **반드시 사람이 검토/승인(Human Gate)**해야 tc-writer에 전달된다.

## 목적

기획서에 분류 기준이 일관되지 않은 경우에도, AI가 최선의 초안을 만들고
불확실한 항목을 명시적으로 표시하여 사람이 한 번만 정리하면
이후 모든 TC가 일관된 분류 체계를 따를 수 있도록 한다.

## 입력

| 파일 | 내용 |
|------|------|
| `{phaseDir}/_workspace/03_features/feature_list.md` | feature-mapper 출력물 |
| `{phaseDir}/tc-rules-override.md` | 도메인 코드 목록 |
| `common/tc-rules.md` | 공통 규칙 |

## 출력

`{phaseDir}/_workspace/03_features/classification_draft.md`

## 분류 기준

### 대분류 (서비스 메뉴/섹션 단위)
- 사용자가 앱에서 보는 최상위 메뉴나 페이지 단위
- 예: `AUTH` (인증/온보딩), `TRAD` (거래), `SGNL` (시그널), `SETG` (설정)
- tc-rules-override.md 또는 tc-rules.md의 도메인 코드 목록을 그대로 사용

### 중분류 (화면/컴포넌트 단위)
- 대분류 내에서 구분되는 화면, 모달, 주요 컴포넌트
- 예: `Login`, `Terms`, `Onboarding`, `Order Form`, `Position Card`
- 4~8자의 영문 코드로 축약 (ORDF, PSTN, LEVMOD 등)

### 소분류 (개별 기능/검증 포인트)
- 중분류 내에서 TC 하나로 커버하는 세부 기능
- 예: OAuth 로그인, 경계값 입력 제한, 배지 표시

## TC ID 형식

```
SC-{대분류코드}-{중분류코드}-{NNN}
예: SC-AUTH-LOGN-001, SC-TPSL-MODL-002
```

- `SC` = Supercycl (프로젝트 고정 접두사)
- `{대분류코드}` = tc-rules.md 도메인 코드 (AUTH, TRAD 등)
- `{중분류코드}` = 4~6자 영문 대문자
- `{NNN}` = 001부터 시작

## 출력 형식 (classification_draft.md)

```markdown
# 기능 분류표 초안 — {프로젝트명}

> 작성 일시: {YYYY-MM-DD}
> 상태: ⏳ STEP 3 — 검토 대기 (승인 전)
> 기준: feature_list.md

---

## 대분류 코드 정의

| 대분류 | 코드 | 설명 |
|--------|------|------|
| {이름} | {코드} | {설명} |
...

---

## 기능 분류표

### {대분류명} — {코드}

| No. | 대분류 | 중분류 | 소분류 | TC ID 프리픽스 | 기능 ID | 비고 |
|-----|--------|--------|--------|--------------|---------|------|
| 1   | AUTH   | Login  | OAuth 로그인 | SC-AUTH-LOGN | F-001, F-002 | |
| 2   | AUTH   | Terms  | 약관 동의 | SC-AUTH-TERM | F-003, F-004 | ⚠️ 불확실: ... |
...

---

## ⚠️ 불확실 항목 목록

| No. | 항목 | 쟁점 | 선택지 |
|-----|------|------|--------|
| 1   | ... | ... | A) ... / B) ... |
...

---

## Human Gate 안내

이 파일을 검토하여:
1. 분류가 잘못된 항목 수정
2. ⚠️ 불확실 항목 결정
3. 검토 완료 후 파일명을 `classification_v1_APPROVED.md`로 저장
4. 오케스트레이터에게 승인 완료를 알림
```

## 불확실 항목 처리 기준

다음 상황에서 `⚠️ 불확실` 표시:
- 동일 기능이 두 중분류에 걸쳐 있을 때
- 기획서에 화면 구조가 명시되지 않은 기능
- 기존 도메인 코드와 매핑이 불명확한 기능
- 중분류 코드가 충돌할 가능성이 있을 때

## 실행 규칙

1. feature_list.md의 **모든 기능 ID**가 분류표에 매핑되어야 한다. 누락 금지.
2. 기존 Phase가 있으면 `classification_v1_APPROVED.md`를 참조하여 일관성 유지
3. 불확실 항목이 0개여도 사람 승인 없이 진행하지 않는다
4. 분류표 작성 완료 후 오케스트레이터에게 `⏸️ HUMAN GATE 대기` 알림을 보낸다
