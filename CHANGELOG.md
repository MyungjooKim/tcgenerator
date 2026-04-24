# TC 자동화 도구 — 변경 이력 (Release Notes)

릴리즈 간 주요 변경사항을 기록합니다. 동료가 `git pull` 받은 후 이 파일을 먼저 읽으면 변경 내용을 빠르게 파악할 수 있습니다.

---

## v0.9.7a — 2026-04-24 (마크다운 다중·폴더 업로드)

> **요약**: 쪽대본 묶음 업로드 지원. 파일 여러 개 또는 폴더 통째로 선택 가능. Windows 호환성 수정(v0.9.7) 포함.

### ✨ 신규 기능

- **📄 다중 파일 업로드**: 「마크다운 파일 추가」 카드에서 여러 .md 파일을 한 번에 선택 가능 (Ctrl/Cmd 다중 선택 또는 Shift 범위 선택)
- **📁 폴더 선택 업로드** (신규 버튼): md 카드에 "폴더 선택" 버튼 추가
  - `webkitdirectory` 활용, 네이티브 폴더 선택창
  - 내부 `.md / .markdown / .txt`만 자동 필터 (숨김 파일 제외)
  - **파일명 순 자동 정렬** (쪽대본 01_ → 02_ 순서 보존)
  - **50개 초과 시 confirm 경고** — 대규모 실수 방지
- **중복 파일명 자동 보존**: 같은 이름의 파일을 연속 업로드하면 서버가 `_1`, `_2` 자동 접미사 부여 (덮어쓰기 방지)
- **소스 자동 분할**: 업로드한 파일마다 독립된 md 소스 카드로 자동 생성 → 개별 삭제·관리 가능

### 🔒 안전 / 보안
- 파일명에서 경로 조작 문자 제거 (`<>:"/\|?*`)
- 확장자 화이트리스트: `.md / .markdown / .txt`만 허용
- webkitRelativePath 경로 분리자 제거 (폴더 업로드 시 서버 측 하위폴더 접근 방지)

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-ui/scripts/app_v2.py` | 프론트: `<input webkitdirectory>` + 폴더 선택 버튼 + `onMdFolderChange` 추가 · 서버: `/upload-md` 중복 파일명 접미사 처리 |

### 🧪 테스트 현황 (투명 공개)
- ✅ Python 구문 검사 · 서버 기동 검증
- ✅ 서버 API 중복 파일명 접미사 동작 (3회 업로드 → `_1`/`_2` 확인)
- ✅ UI 렌더 (`webkitdirectory` 속성, 폴더 선택 버튼 노출)
- ⏳ 브라우저에서 실제 폴더 선택 E2E 테스트는 사용자 확인 예정

### 💡 포함되는 이전 버전 수정
- v0.9.7의 Windows cp949 인코딩 / Excel 빌더 모듈화 등 모두 포함

---

## v0.9.7 — 2026-04-23 (Windows 호환성 패치)

> **요약**: Windows 환경에서 Excel 빌드가 fallback으로 빠져 **대분류별 시트 분할·Smoke Test 시트가 누락**되던 문제 해결. Excel 빌더를 모듈 import 방식으로 전환.

### 🐛 버그 수정 (Windows PC 환경)

- **Excel 대분류별 시트 분할 누락 & 🔥 Smoke Test 시트 누락**
  - 원인: Windows 기본 콘솔 인코딩(cp949)에서 `subprocess.run(text=True)`가 이모지(🔥) 디코드 실패 → `UnicodeDecodeError` → fallback 경로 진입
  - fallback은 `TC 전체목록` 한 시트에 모든 TC를 몰아 넣고 Smoke Test 시트도 생성 안 함 → 결과적으로 동료 Windows 환경에서만 Excel 구조 붕괴
  - **해결**: `build_excel.py`의 로직을 `run_build()` 함수로 추출 + `app_v2.py`가 subprocess 대신 **모듈 import로 직접 호출**. cp949 경로 자체를 제거.

- **cp949 인코딩 오류 추가 방어**
  - `build_excel.py` 시작부에 `sys.stdout/stderr.reconfigure(encoding="utf-8", errors="replace")` 추가
  - subprocess 폴백 경로에도 `PYTHONIOENCODING=utf-8`, `PYTHONUTF8=1` 환경변수 주입
  - stdout/stderr를 bytes로 받아 `errors='replace'`로 수동 디코드

- **fallback에도 🔥 Smoke Test 시트 생성 추가**
  - 모든 폴백 경로가 실패해서 내부 간이 빌더를 쓰더라도 Smoke Test는 보장

### ✨ 구조 개선

- **Excel 빌더 모듈화**: `build_excel.py`의 `main()` → `run_build(phase, tc_path, output_dir, verbose)` 함수로 분리
- **3단계 폴백 체인**:
  1. **모듈 import** → `run_build()` 호출 (기본 · Windows 호환)
  2. subprocess 호출 (모듈 import 실패 시)
  3. 내부 간이 빌더 (최후 수단 · 시트 분할/Traceability 없음)
- **속도 향상**: 모듈 호출 경로는 subprocess 생성 오버헤드 제거 (~1초 절감)

### 📁 파일 변경

| 파일 | 변경 내용 |
|---|---|
| `tc-agent/scripts/build_excel.py` | `run_build()` 함수 추출, stdout/stderr UTF-8 강제 |
| `tc-ui/scripts/app_v2.py` | `step_build_excel` 모듈 import 우선 + 3단계 폴백, fallback에 Smoke 시트 추가 |

### 💡 동료 Windows PC 환경 확인 방법

`git pull` 후 재실행 → Excel 빌드 후 시트 목록에 다음이 모두 있어야 정상:
```
📋 표지 / 📊 TC 통계 / 🔥 Smoke Test / 🔗 Traceability / 📑 대분류명 (N개)
```
Flask 터미널 로그에 `[빌드] 모듈 호출 성공 — 총 N TC / Smoke M / 대분류 K시트` 메시지가 나오면 1순위 경로가 정상 동작 중입니다.

---

## v0.9.6 — 2026-04-23

> **요약**: 「기존 TC 수정」 탭 전면 개편 (기획서 diff 기반), 파이프라인 최적화, SCR Traceability, 다수 버그 수정

### ✨ 신규 기능

#### 1. 「기존 TC 수정」 탭 전면 개편 — 기획서 변경 기반 TC 갱신
기존의 "변경사항을 텍스트로 설명" 방식에서 **두 기획서 파일을 비교**하는 방식으로 전환.

- **3-슬롯 입력 UI**: 이전 기획서 · 새 기획서 · 기존 TC 파일 (모두 드래그앤드롭)
- **프로젝트 선택 없이 단발성 작업 가능** — 쪽대본 방식 지원
- **구조 기반 diff**: 기획서를 `SCR-001`, `SCREEN-xxx`, `PAGE-xxx` 단위로 분할 후 신규/수정/삭제/유지 자동 분류
- **GitHub 스타일 unified diff 뷰어**: +/- 라인 하이라이트로 무엇이 바뀌었는지 한눈에
- **체크박스 선택**: 각 변경 항목을 개별 승인 가능, 섹션별 + 전체 "전체 선택/해제"
- **TC ID 유지한 채 AI로 재작성**: 수정 사유 자동 추출
- **기존 TC 파일 지원**: 우리가 생성한 MD / Excel 역파싱 (외부 Spreadsheet는 추후 지원)
- **자동 스냅샷**: 갱신 전 `tc_history/{project}/snapshot_{timestamp}.md`에 백업 저장

#### 2. SCR Traceability — 화면 ↔ TC 양방향 추적성
- **"화면 코드" 컬럼 추가** (TC ID 바로 옆): 각 TC가 검증하는 SCR/SCREEN/PAGE 코드 기록
- **`🔗 Traceability` 시트 신규**: 화면 코드별 TC 개수 · Smoke 개수 · TC ID 목록 역참조
- AI가 중분류 이름 주변에서 화면 코드를 자동 탐지하여 TC 메타에 삽입

#### 3. 파이프라인 생성 모드 선택 UI
- Step 1 입력 설정에 **생성 모드 라디오** 추가
  - **정책 반영 모드 (기본)**: policy·features·분류 3단계 분석 (대용량 문서 적합)
  - **Quick 모드**: 원문을 직접 분류 (200KB 이하 권장, 정확도↑)
- 소스 크기 실시간 표시 + 200KB 초과 시 Quick 자동 비활성

#### 4. 파이프라인 효율 최적화
- **정책 반영 모드**: policy + features 2회 호출 → **1회 통합 호출** (토큰 ~40% 감소)
- **Quick 모드 3단계 재설계**: 인벤토리 → 분류 → 섹션 발췌 TC (누락 방지 구조)
- **TC 작성 시 원문 섹션 발췌**: 중분류당 컨텍스트 44KB → 6KB (**~87% 감소**)
- **Review 단계 누락 보강**: 분류표 vs 초안 비교하여 빠진 중분류의 TC 자동 추가 생성

#### 5. Excel 출력 구조 개선
- **대분류별 시트 분할**: `🧪 TC 전체목록` 제거 → `📑 대분류명` 시트 N개로 분리 (가독성↑)
- **컬럼 재배치** (팀원 의견 반영): `Smoke | TC ID | 화면 코드 | 우선순위 | 거래소 | 대분류 | 중분류 | 소분류 | 사전조건 | 스텝 | 기대결과`
- **변경 이력 컬럼/시트**: 상태(🆕/🔄/🗑️/빈값) + 수정 사유 컬럼 + `🔄 변경 이력` 시트
- **상태별 행 배경색**: 🆕신규(연초록) / 🔄수정(연노랑) / 🗑️Deprecated(회색)
- **TC ID 기반 중복 제거 dedup** 최종 방어선 내장

#### 6. UX 개선
- 📊 결과 화면: "최소 TC" → **"🔥 Smoke TC"** 라벨 교체 (실제 Smoke 개수 표시)
- 진행도 stage 세분화: 82→88→92→98→100 + 서버 전송 `eta_sec` 기반 정확한 카운트다운
- 파이프라인 stop 버튼, 재개(resume) 로직 개선

### 🐛 버그 수정

- **TC 카운트 웹/Excel 불일치**: 웹 102개 vs Excel 81개 → 유니크 TC ID 기반으로 통일
- **ScreenCode 충돌**: 같은 ScreenCode(예: CON)를 여러 중분류가 공유해 TC ID 21개 손실되던 문제 → `CON / CON2 / CON3 ...` 자동 접미사로 회피
- **프로젝트 빈 이름 유령 레코드**: 드롭다운에 삭제된 프로젝트가 `[진행 중]`으로 남는 현상 → 3중 방어 (저장 차단 + 로드 필터 + 렌더 필터)
- **Review 누락 보강 중복 생성**: 마크다운 테이블 형식 TC를 인식 못해 이미 있는 TC를 재생성 → 테이블 패턴까지 인식하도록 파서 강화
- **fetch_web_page TLS 검증 비활성**: `verify=False` 하드코딩 → 기본 활성, `TC_WEB_INSECURE=1` env로만 명시적 opt-out

### 🔐 안전 / 호환성

- **Windows PC 호환성 강화**: `.env` 로더 `utf-8-sig` BOM 처리, 따옴표 자동 제거, `시작하기_v2_Windows.bat` 단순화
- **Excel 빌드 하위 호환**: 상태/수정사유 필드 없는 기존 TC 파일도 정상 처리

### 📁 파일 변경

| 파일 | 용도 |
|---|---|
| `tc-ui/scripts/app_v2.py` | Flask + SSE 웹앱 메인 (신규 엔드포인트 3개, 함수 15개+ 추가) |
| `tc-agent/scripts/build_excel.py` | Excel 빌더 (컬럼 재정의, Traceability / 변경 이력 시트) |
| `tc-ui/시작하기_v2_Windows.bat` | Windows 실행 스크립트 단순화 |
| `tc-ui/.gitignore` | `tc_history/` 제외 추가 |
| `CHANGELOG.md` | 이 파일 (신규) |
| `tc-agent/projects/supercycl/` | 프로젝트별 규칙 파일 추가 |

### 🆕 신규 API 엔드포인트

- `POST /upload-existing-tc` — MD/xlsx 업로드 (TC 개수 미리보기)
- `POST /analyze-diff` — 3-슬롯 분석 → 변경사항 리포트 반환
- `POST /update-tc` — 승인된 변경사항 기반 TC 갱신 실행

### 💻 개발자를 위한 참고

**실행 방법 (변경 없음)**:
```bash
# macOS
./시작하기_v2.command
# Windows
시작하기_v2_Windows.bat
```

**테스트 권장 시나리오**:
1. 「새 TC 생성」 탭에서 Quick 모드로 작은 기획서 처리 → 새 Excel 구조 확인 (📑 대분류별 시트, 🔗 Traceability)
2. 「기존 TC 수정」 탭에서 이전/새 기획서 + 기존 TC MD 업로드 → unified diff 뷰어 + 체크박스 승인 흐름
3. Excel 열어서 `🔄 변경 이력` 시트 확인

**알려진 제약**:
- 기존 TC 파일의 외부 Google Spreadsheet 직접 입력은 미지원 (MD/Excel만)
- SCR 코드가 전혀 없는 기획서는 구조 diff 불가 (화면 코드 체계 필요)

---

## v0.9.5 — 2026-04-21 (이전 릴리즈)

- TC ID 이중 하이픈 버그 수정 (`SC-GNB--006` → `SC-GNB-006`)
- TC 수량 조정
- TC 카테고리 비율 강화 및 Few-shot Negative/Edge 예시 추가
- Human Gate SuiteCode 입력 UX 개선
- 프로젝트 전환 초기화
