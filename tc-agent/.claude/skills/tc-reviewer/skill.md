---
name: tc-reviewer
description: "TC 초안을 검토하여 품질을 검증하는 스킬. TC 검토, 테스트 케이스 리뷰, 커버리지 확인, 중복 TC 탐지, 최소 TC 세트 선별 요청 시 반드시 이 스킬을 사용할 것."
---

# TC Reviewer

TC 초안의 품질을 검증하고 review_report.md를 작성한다. "존재 확인"이 아니라 "올바른 것을 검증하는지" 판단하는 것이 목표다.

> ⚠️ **역할 분리 원칙**
> - tc-reviewer: 품질 검토 → `05_review/review_report.md` 만 생성
> - tc_final.md 생성: bash `cat` 병합으로 처리 (오케스트레이터가 직접 실행)
> - Excel 빌드: `build_excel.py` 스크립트로 처리 (output-builder 또는 오케스트레이터)
>
> tc-reviewer는 **절대 tc_final.md를 직접 생성하지 않는다.** 파일 병합은 LLM이 아닌 bash가 처리한다.

## 검토 항목 체크리스트

### 0. 분류표 일관성 검사 (신규)

`classification_v1_APPROVED.md`가 있으면 반드시 읽고 다음을 확인한다:

1. **TC ID 형식** — 모든 TC가 `SC-{대분류코드}-{중분류코드}-{NNN}` 형식인지 확인
2. **대분류/중분류 필드** — 각 TC의 대분류/중분류/소분류 값이 분류표와 일치하는지 확인
3. **중분류 코드 일관성** — 동일 중분류에 속한 TC들이 같은 코드를 사용하는지 확인
4. **미분류 TC** — 분류표에 없는 대분류/중분류가 있으면 분류표 추가 또는 TC 수정 필요

분류 불일치 발견 시 이슈 목록에 `분류 불일치` 유형으로 기록한다.

### 1. 커버리지 검증
기능 목록 (`feature_list.md`)의 각 기능 ID가 적어도 1개 이상의 TC로 커버되는지 확인한다.

```
커버리지 매트릭스:
| 기능 ID | 기능명 | TC 수 | 상태 |
|---------|--------|-------|------|
| F-001   | ...    | 3     | ✅   |
| F-002   | ...    | 0     | ❌ 누락 |
```

커버리지 95% 미만 → tc-writer에게 보강 요청 후 재검토. 최대 3회 반복.

### 2. 중복 탐지
GIVEN + WHEN + THEN이 실질적으로 동일한 TC를 찾는다. 표현이 달라도 검증 목적이 같으면 중복이다.

### 2-1. [미결] 태그 검증
비고란에 `[미결]` 태그가 없는데 정책 미확정 내용이 있으면 태그를 추가한다.
`[미결]` TC는 커버리지 계산에는 포함하되, review_report의 미결 목록 테이블에 별도 집계한다.

### 3. THEN 품질 검사
- 측정 불가능한 표현 탐지 ("제대로", "정상적으로", "올바르게")
- 기대값이 없는 THEN 탐지
- 여러 기대 결과를 한 TC에 섞은 경우 분리 제안

### 4. Edge 케이스 비율
Edge 케이스가 전체의 20% 미만이면 경계값 시나리오 추가를 tc-writer에게 요청한다.

### 5. N/A 조건 판단
플랫폼별·환경별 제약이 있으면 TC에 명시한다.
예: "Hyperliquid는 Auto TP/SL 미지원 → 해당 TC에 N/A 조건 추가"

## 최소 TC 세트 선별 기준

다음 기준으로 최소 TC 세트를 선별한다:

1. **우선순위 High** TC 전체
2. **Happy Path** — 각 도메인의 대표 정상 흐름 1개
3. **환경별 차이** — 플랫폼/거래소/역할에 따라 동작이 다른 TC
4. 목표: 전체의 35~50% 수준

## 검토 보고서 형식

출력: `{phaseDir}/_workspace/05_review/review_report.md` **만** 생성한다.

```markdown
# TC 검토 보고서

## 요약
- 총 TC: {N}개
- 커버리지: {N}% ({커버된 기능}/{전체 기능})
- 발견된 이슈: {N}개
- 최소 TC 세트: {N}개

## 발견된 이슈

| 번호 | TC ID | 이슈 유형 | 내용 | 수정 제안 |
|------|-------|----------|------|----------|
| 1    | ...   | 중복     | ... | ... |
| 2    | ...   | THEN 불명확 | ... | ... |

## 최소 TC 세트
{TC ID 목록}

## 커버리지 매트릭스
{표}
```

## tc_final.md 생성 (bash — LLM 불필요)

검토 완료 후 오케스트레이터가 다음 bash 명령으로 tc_final.md를 생성한다:

```bash
# 헤더 작성
cat > {phaseDir}/_workspace/05_review/tc_final.md << EOF
# Phase N TC 최종본

## 메타 정보
- 생성일: {날짜}
- 총 TC: {N}개
- 최소 TC: {N}개
- 커버리지: {N}%
---
EOF

# 도메인별 draft 병합
for domain in AUTH LEVR TPSL TRAD SGNL FUND MOBL SETG; do
  cat {phaseDir}/_workspace/04_tc/tc_draft_${domain}.md >> {phaseDir}/_workspace/05_review/tc_final.md
  echo -e "\n---\n" >> {phaseDir}/_workspace/05_review/tc_final.md
done
```

이 단순 파일 병합 작업에 LLM 에이전트를 사용하지 않는다.
