---
name: tc-orchestrator
description: "범용 TC 자동화 에이전트 팀을 조율하는 오케스트레이터. 기획 문서(PDF/PPTX/텍스트/구글슬라이드)뿐 아니라 서비스 시나리오, GitHub 목업 리포지토리, 자연어 설명만으로도 BDD 형식 테스트 케이스를 자동 생성하고 Excel로 출력한다. '테스트 케이스 만들어줘', 'TC 자동화', 'TC 생성', '테스트 케이스 자동화', '시나리오로 TC', '목업으로 TC' 요청 시 반드시 이 스킬을 사용할 것."
---

# TC Orchestrator

기획 문서 → BDD TC → Excel 전 과정을 6개 전문 에이전트 팀으로 자동화한다.
**v2 신규:** feature-classifier 단계 + Human Gate(사람 승인) 추가.

## 실행 모드: 에이전트 팀 (파이프라인 패턴)

## 에이전트 구성

| 팀원 | 역할 | 스킬 | 출력 |
|------|------|------|------|
| doc-parser | 문서 파싱 | doc-parser | `_workspace/01_parsed/parsed_content.md` |
| policy-analyst | 정책 정리 | policy-analyst | `_workspace/02_policy/policy_doc.md` |
| feature-mapper | 기능 목록 추출 | feature-mapper | `_workspace/03_features/feature_list.md` |
| **feature-classifier** | **대/중/소 분류표 초안 생성** | **feature-classifier** | **`_workspace/03_features/classification_draft.md`** |
| tc-writer | TC 초안 작성 (도메인별 순차) | tc-writer | `_workspace/04_tc/tc_draft_{도메인}.md` × N개 |
| tc-reviewer | TC 품질 검증 | tc-reviewer | `_workspace/05_review/tc_final.md` |
| output-builder | 산출물 생성 | output-builder | `outputs/{프로젝트명}_TC_{날짜}.{md,xlsx}` |

> **⛔ Human Gate**: feature-classifier 완료 후 반드시 사람이 분류표를 검토·승인해야 tc-writer가 시작된다.

## 워크플로우

### Phase 1: 준비

1. 사용자로부터 다음 정보를 확인한다:
   - **입력:** 아래 중 하나 이상 (혼합 가능)
     - 문서 파일: PDF, PPTX, `.txt`, `.md`
     - URL: 구글 슬라이드, GitHub 리포지토리, Figma
     - 자연어: 서비스 시나리오 직접 입력
   - **Phase 코드:** P1_Youthmeta / P2_Mobile / 신규 Phase
   - **Phase 디렉토리:** `phase{N}-{name}/` (tc-rules-override.md 위치)

2. 규칙 파일 경로 확인:
   - 공통: `common/tc-rules.md`
   - Phase 전용: `phase{N}-{name}/tc-rules-override.md`
   - 스타일 샘플: `common/tc-sample.md`
   - 정책 문서: `common/policy/`

   > 정식 기획서가 없어도 괜찮다. 서비스 시나리오나 GitHub 목업 URL만 있어도 파이프라인을 실행할 수 있다.

2. 디렉토리 구조 생성 (`{phaseDir}` = `phase{N}-{name}/`):
   ```
   {phaseDir}/
   ├── _workspace/
   │   ├── 00_input/     ← 입력 파일 복사 또는 링크
   │   ├── 01_parsed/
   │   ├── 02_policy/
   │   ├── 03_features/
   │   ├── 04_tc/
   │   └── 05_review/
   └── outputs/
   ```

3. 입력 파일을 `{phaseDir}/_workspace/00_input/`에 복사
4. 구글 슬라이드 URL이 있으면 `{phaseDir}/_workspace/00_input/input_sources.txt`에 저장

### Phase 2: 팀 구성

```
TeamCreate(
  team_name: "tc-automation-team",
  members: [
    { name: "doc-parser",           agent_type: "general-purpose", model: "opus" },
    { name: "policy-analyst",       agent_type: "general-purpose", model: "opus" },
    { name: "feature-mapper",       agent_type: "general-purpose", model: "opus" },
    { name: "feature-classifier",   agent_type: "general-purpose", model: "opus" },
    { name: "tc-writer",            agent_type: "general-purpose", model: "opus" },
    { name: "tc-reviewer",          agent_type: "general-purpose", model: "opus" },
    { name: "output-builder",       agent_type: "general-purpose", model: "opus" }
  ]
)
```

작업 등록 (`{phaseDir}` 실제 값으로 치환, 예: `phase2-mobile`):
```
TaskCreate(tasks: [
  { title: "문서 파싱",
    assignee: "doc-parser",
    description: "{phaseDir}/_workspace/00_input/ 파일 파싱 → {phaseDir}/_workspace/01_parsed/parsed_content.md" },

  { title: "정책 정리",
    assignee: "policy-analyst",
    description: "parsed_content.md → {phaseDir}/_workspace/02_policy/policy_doc.md",
    depends_on: ["문서 파싱"] },

  { title: "기능 목록 추출",
    assignee: "feature-mapper",
    description: "policy_doc.md → {phaseDir}/_workspace/03_features/feature_list.md. 규칙: common/tc-rules.md + {phaseDir}/tc-rules-override.md",
    depends_on: ["정책 정리"] },

  { title: "분류표 초안 생성",
    assignee: "feature-classifier",
    description: "feature_list.md → {phaseDir}/_workspace/03_features/classification_draft.md. 대분류/중분류/소분류 계층 구조. 완료 후 오케스트레이터에게 HUMAN GATE 대기 알림",
    depends_on: ["기능 목록 추출"] },

  ⛔ --- HUMAN GATE (자동 진행 불가) ---
  feature-classifier 완료 후 오케스트레이터는 사용자에게 아래 메시지 전달:
    "분류표 초안이 준비됐습니다: {phaseDir}/_workspace/03_features/classification_draft.md
     검토 후 수정하시고, 승인 완료 시 파일을 {phaseDir}/_workspace/03_features/classification_v1_APPROVED.md 로 저장 후 '승인됐어' 라고 알려주세요."
  사용자 승인 메시지를 받을 때까지 다음 단계를 시작하지 않는다.
  --------------------------------------

  { title: "TC 초안 작성 (도메인 분할)",
    assignee: "tc-writer",
    description: "classification_v1_APPROVED.md + feature_list.md 읽기 → 도메인별 순차 TC 작성 → {phaseDir}/_workspace/04_tc/tc_draft_{도메인}.md. 각 TC에 대분류/중분류/소분류 필드 포함. TC ID는 SC-{대분류코드}-{중분류코드}-{NNN} 형식. 규칙: common/tc-rules.md + {phaseDir}/tc-rules-override.md + common/tc-sample.md",
    depends_on: ["분류표 초안 생성 + 사람 승인"] },

  { title: "TC 품질 검증",
    assignee: "tc-reviewer",
    description: "{phaseDir}/_workspace/04_tc/tc_draft_*.md 전체 + classification_v1_APPROVED.md → {phaseDir}/_workspace/05_review/review_report.md 만 생성. tc_final.md는 생성하지 않음 (bash 병합으로 처리). 분류 일관성 검사 포함",
    depends_on: ["TC 초안 작성 (도메인 분할)"] },

  { title: "산출물 생성",
    assignee: "output-builder",
    description: "tc_final.md → {phaseDir}/outputs/. 스크립트: python3 scripts/build_excel.py --phase {PhaseCode} --tc {phaseDir}/_workspace/05_review/tc_final.md --output {phaseDir}/outputs",
    depends_on: ["TC 품질 검증"] }
])
```

### Phase 3: 파이프라인 실행

팀원들이 순차적으로 자체 조율하며 파이프라인을 진행한다.

**통신 흐름:**
```
doc-parser → policy-analyst → feature-mapper → feature-classifier
  ⛔ HUMAN GATE (사용자 분류표 검토·승인 대기)
→ tc-writer(도메인1) → tc-writer(도메인2) → ... → tc-reviewer → output-builder → 리더
```

각 팀원은 작업 완료 시 다음 팀원에게 SendMessage로 알린다. 리더는 진행 상황을 모니터링하며 이슈 발생 시 개입한다.

**tc-writer 도메인 분할 실행 (핵심):**

Rate limit 및 토큰 효율을 위해 tc-writer는 도메인별로 순차 실행한다.

1. feature_list.md에서 도메인 목록 추출 (예: AUTH, TRADE, SIGNAL, FUND, UI ...)
2. 도메인별로 tc-writer를 순서대로 1개씩 호출:
   - `{phaseDir}/_workspace/04_tc/tc_draft_AUTH.md`
   - `{phaseDir}/_workspace/04_tc/tc_draft_TRADE.md`
   - ... (도메인 수만큼 반복)
3. 각 호출마다 **해당 도메인의 기능 목록만** 전달 (다른 도메인 내용 제외)
4. 도메인 1개 완료 → 즉시 파일 저장 → 다음 도메인 시작
5. 전체 완료 후 tc-reviewer에게 `{phaseDir}/_workspace/04_tc/` 경로 전달

> 이 방식으로 한 번의 tc-writer 실행이 처리하는 기능 수를 5~10개로 제한하여
> 토큰 사용량과 Rate limit 위험을 줄인다.

**tc-reviewer 재작업 루프:**
tc-reviewer가 커버리지 95% 미만을 발견하면:
1. tc-writer에게 미커버 기능 ID 목록과 함께 보강 요청
2. tc-writer가 해당 도메인 tc_draft_v{N}.md 작성 (누락 기능만 처리)
3. tc-reviewer가 재검토
4. 최대 3회 반복

**tc_final.md 생성 (bash — LLM 불필요):**

tc-reviewer 완료 후 오케스트레이터가 직접 bash로 병합한다. **에이전트 사용 금지.**

```bash
# 1. 헤더 생성
cat > {phaseDir}/_workspace/05_review/tc_final.md << 'EOF'
# Phase N TC 최종본
## 메타 정보
- 생성일: {날짜}
- Phase: {PhaseCode}
- 총 TC: N개 / 최소 TC: N개 / 커버리지: N%
---
EOF

# 2. 도메인 순서대로 병합 (도메인 목록은 feature_list.md 기준으로 조정)
for domain in AUTH LEVR TPSL TRAD SGNL FUND MOBL SETG; do
  f="{phaseDir}/_workspace/04_tc/tc_draft_${domain}.md"
  [ -f "$f" ] && cat "$f" >> {phaseDir}/_workspace/05_review/tc_final.md && echo -e "\n---\n" >> {phaseDir}/_workspace/05_review/tc_final.md
done
```

**Excel 빌드 (bash 직접 실행):**

```bash
cd {프로젝트 루트}
source .venv/bin/activate
python3 scripts/build_excel.py \
  --phase {PhaseCode} \
  --tc {phaseDir}/_workspace/05_review/tc_final.md \
  --output {phaseDir}/outputs
```

### Phase 4: 결과 수집

output-builder의 완료 보고를 받으면:
1. `{phaseDir}/outputs/` 디렉토리 확인
2. 사용자에게 최종 결과 요약:
   - 생성된 파일 경로
   - TC 총 개수 및 분포
   - 최소 TC 세트 개수
   - 발견된 주요 이슈

## 데이터 전달 규칙

| 전달 방식 | 용도 |
|----------|------|
| 파일 기반 (`{phaseDir}/_workspace/`) | 단계별 중간 산출물 |
| SendMessage | 작업 완료 알림, clarification 요청 |
| TaskUpdate | 작업 상태 업데이트 |

## 에러 핸들링

| 상황 | 처리 방법 |
|------|----------|
| 문서 파싱 실패 | 실패 파일 목록 기록 후 계속 진행 |
| 정책 분석 불충분 | 사용자에게 추가 문서 요청 |
| TC 커버리지 95% 미만 | tc-writer 보강 요청 (최대 3회) |
| Excel 생성 실패 | Markdown만 출력 후 완료 보고 |
| 팀원 무응답 | 5분 후 리더가 직접 해당 작업 수행 |

## ⚠️ Rate Limit 대응 전략

에이전트가 `total_tokens: 0` 또는 "You've hit your limit"으로 종료되면 rate limit이다.

### 원인별 대응

| 원인 | 증상 | 대응 |
|------|------|------|
| 에이전트 입력 과다 | 8개 파일 동시 읽기 → 토큰 폭발 | 파일을 분할하여 전달 |
| tc-reviewer 과부하 | draft 파일 전체 + tc_final 생성 동시 | tc_final은 bash로, 검토만 담당 |
| 연속 에이전트 실행 | 여러 에이전트 연속 호출 후 한도 초과 | 에이전트 수 줄이고 직접 처리 |

### Rate Limit 발생 시 오케스트레이터 행동

1. **tc-writer 단계에서 걸린 경우**: 완료된 `tc_draft_*.md` 파일 확인 → 누락 도메인만 재실행
2. **tc-reviewer에서 걸린 경우**: `review_report.md` 존재 여부 확인
   - 있으면 → bash로 tc_final.md 병합 → Excel 빌드로 바로 진행
   - 없으면 → tc-reviewer 재실행 (이번엔 tc_final 생성 제외)
3. **tc_final.md 생성은 항상 bash**: LLM 에이전트에게 절대 맡기지 않는다
4. **Excel 빌드는 항상 bash**: `python3 scripts/build_excel.py` 직접 실행

### 작업 재개 체크리스트

```
□ 04_tc/tc_draft_*.md — 완료된 도메인 확인
□ 05_review/review_report.md — 검토 완료 여부
□ 05_review/tc_final.md — bash로 직접 생성
□ outputs/*.xlsx — bash로 직접 빌드
```

## 테스트 시나리오

### 정상 흐름
```
입력: planning.txt (기획 메모 텍스트)
→ doc-parser: 텍스트 읽어 parsed_content.md 생성
→ policy-analyst: 정책 영역 3개 식별, policy_doc.md 생성
→ feature-mapper: 기능 15개 추출 (High: 8, Medium: 5, Low: 2)
→ tc-writer: TC 40개 작성 (Positive 20, Negative 12, Edge 8)
→ tc-reviewer: 커버리지 93%, 이슈 3개 발견, 최소 TC 세트 18개
→ output-builder: Project_TC_20260401.md / .xlsx 생성
결과: outputs/ 아래 2개 파일
```

### 에러 흐름 — 커버리지 부족
```
tc-reviewer가 커버리지 55% 발견
→ tc-writer에게 보강 요청 (Edge 케이스 위주)
→ tc-writer: tc_draft_v2.md 작성 (12개 TC 추가)
→ tc-reviewer: 재검토 → 커버리지 88%로 통과
→ output-builder: 파이프라인 계속
```

## 빠른 시작

```
이 기획서 기반으로 TC 만들어줘: [파일 경로 또는 내용]
```

또는:

```
TC 자동화 실행해줘. 입력 파일: specs/기획서.pdf, 프로젝트명: MyProject
```
