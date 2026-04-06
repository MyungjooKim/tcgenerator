---
name: output-builder
description: "최종 TC를 Markdown과 Excel 파일로 변환·저장하는 스킬. TC 결과물 생성, Excel 내보내기, TC 파일 패키징 요청 시 반드시 이 스킬을 사용할 것."
---

# Output Builder

최종 TC를 Markdown과 Excel 두 가지 형식으로 패키징하여 Phase별 `outputs/` 디렉토리에 저장한다.

## 출력 파일 경로

| 파일 | 경로 |
|------|------|
| Markdown | `phase{N}-{name}/outputs/SPCY_TC_{PhaseCode}_{YYYYMMDD}_v{N}.md` |
| Excel | `phase{N}-{name}/outputs/SPCY_TC_{PhaseCode}_{YYYYMMDD}_v{N}.xlsx` |

**파일명 규칙 (버전 자동 증가):**
- 같은 날짜·Phase 파일이 이미 있으면 v{N}을 1씩 증가
- 날짜가 바뀌면 v1부터 시작
- 예: `SPCY_TC_P2_Mobile_20260402_v1.xlsx`, `SPCY_TC_P2_Mobile_20260402_v2.xlsx`

## Excel 생성 명령

통합 Excel 빌더를 사용한다:

```bash
# venv 활성화 후 실행
source .venv/bin/activate

# Phase 2 (단일 거래소)
python3 scripts/build_excel.py \
  --phase P2_Mobile \
  --tc phase2-mobile/_workspace/05_review/tc_final.md \
  --output phase2-mobile/outputs

# Phase 1 (다중 거래소)
python3 scripts/build_excel.py \
  --phase P1_Youthmeta \
  --tc phase1-youthmeta/workspace/youthmeta_3_tc.md \
  --output phase1-youthmeta/outputs
```

## Excel 시트 구성

### 시트 1: 표지 (📋)
- 프로젝트명, Phase, 생성일, 버전, 테스트 환경, 플랫폼
- TC 통계 (총 TC, High, Positive/Negative/Edge, 최소 TC 세트)
- 판정 코드 범례 (Pass/Fail/N/T/N/A)

### 시트 2: TC 전체목록 (🧪)
- 고정 컬럼: TC ID / 도메인 / 제목 / 분류 / 우선순위 / 플랫폼 / 연관 화면 / 사전 조건 / 테스트 단계 / 예상 결과 / 실제 결과
- **거래소 컬럼 (Phase 1만):** Gate / OKX / Bybit / Bitget / Hyperliquid
  - N/A 셀: 회색 (#E0E0E0)
  - 기본값: N/T
- **Row 2 (Phase 1만):** 테스터 배정 서브헤더 (Tester 1=초록, Tester 2=네이비)
- 최소 TC 행: 노란색 강조 (bold heading — `### **SC-XXX**` 형식)

### 시트 3: TC 통계 (📊)
- 도메인별 TC 수 (총/High/Positive/Negative/Edge/최소TC)

### 시트 4: 최소 TC 세트 (🎯)
- bold heading(`### **SC-XXX**`) TC만 선별 (전체의 30~40%)

## Markdown 출력

> ⚠️ tc_final.md 생성은 오케스트레이터가 bash `cat` 병합으로 처리한다.
> output-builder는 이미 만들어진 tc_final.md를 outputs/에 복사만 한다.

tc_final.md를 복사하여 파일명 규칙으로 저장한다:

```bash
cp {phaseDir}/_workspace/05_review/tc_final.md \
   {phaseDir}/outputs/SPCY_TC_{PhaseCode}_{YYYYMMDD}_v{N}.md
```

## 에러 처리

- Excel 생성 실패 → Markdown만 출력 후 리더에게 알림
- `scripts/build_excel.py` 없으면 리더에게 알림 (스크립트 없이 진행 불가)
- Phase 출력 디렉토리 없으면 자동 생성

## 완료 보고 형식

완료 시 리더에게 SendMessage:
```
산출물 생성 완료.
- Markdown: phase2-mobile/outputs/SPCY_TC_P2_Mobile_{날짜}_v{N}.md
- Excel: phase2-mobile/outputs/SPCY_TC_P2_Mobile_{날짜}_v{N}.xlsx
- 총 TC: {N}개 | High: {N}개 | 최소TC: {N}개 | 버전: v{N}
```
