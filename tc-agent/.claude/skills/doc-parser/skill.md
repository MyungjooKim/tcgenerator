---
name: doc-parser
description: "기획 관련 모든 입력을 파싱하여 구조화된 텍스트로 추출하는 스킬. PDF/PPTX/텍스트/슬라이드/서비스 시나리오/GitHub 목업 리포지토리 등 어떤 형식이든 TC 생성의 원재료가 될 수 있으면 반드시 이 스킬을 사용할 것."
---

# Doc Parser

기획 관련 모든 입력을 파싱하여 `_workspace/01_parsed/parsed_content.md`에 정규화된 텍스트로 저장한다.
정식 기획서가 없어도 서비스 시나리오, 목업 코드, GitHub 리포지토리로부터 동등한 품질의 입력을 생성할 수 있다.

## 입력 처리 방식

입력 유형을 먼저 판별하고 적합한 파서를 선택한다:

| 입력 유형 | 파서 | 비고 |
|----------|------|------|
| `.pdf` | anthropic Files API | PDF 업로드 후 텍스트 추출 |
| `.pptx` | python-pptx | 슬라이드별 텍스트 + 노트 추출 |
| `.txt` / `.md` | 직접 읽기 | 인코딩 UTF-8 우선 |
| 구글 슬라이드 URL | PDF 다운로드 후 처리 | 공유 설정 확인 필요 |
| **서비스 시나리오 (텍스트)** | 시나리오 구조 분석 | 아래 섹션 참조 |
| **GitHub/로컬 목업 리포** | 코드 구조 탐색 | 아래 섹션 참조 |

## 출력 형식

```markdown
## [파일명 또는 슬라이드 제목]

[추출된 원문 내용 — 요약하지 않고 그대로]

---
```

여러 파일이 있으면 파일별로 `##` 섹션으로 구분하여 하나의 파일에 합친다.

## 파싱 실행 순서

1. `_workspace/00_input/` 디렉토리의 파일 목록 확인
2. 각 파일을 유형에 따라 파싱
3. `_workspace/01_parsed/` 디렉토리 생성
4. `parsed_content.md`에 저장
5. 파싱 통계 출력 (성공/실패 파일 수)

## PPTX 파싱 상세

```python
from pptx import Presentation

prs = Presentation(file_path)
for i, slide in enumerate(prs.slides, 1):
    # 슬라이드 제목
    if slide.shapes.title:
        print(f"# {slide.shapes.title.text}")
    # 본문 텍스트
    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text.strip():
            print(shape.text.strip())
    # 화자 노트
    if slide.has_notes_slide:
        notes = slide.notes_slide.notes_text_frame.text.strip()
        if notes:
            print(f"[노트] {notes}")
```

python-pptx가 없으면 `pip install python-pptx`를 실행한다.

## 서비스 시나리오 파싱

"정식 기획서"가 없는 경우 서비스 시나리오(자연어로 쓴 사용자 흐름 묘사)를 입력으로 받는다.

**인식 패턴:** 아래와 같은 자연어 입력은 서비스 시나리오로 처리한다.
- "사용자가 로그인 후 대시보드에 진입하면..."
- "A가 B를 누르면 C가 표시된다"
- 번호 붙은 사용자 행동 목록
- 역할(사용자/관리자/시스템)이 등장하는 서술

**파싱 방법:**

1. **액터 추출** — 시나리오에 등장하는 역할을 식별한다 (예: 일반 사용자, 관리자, 외부 시스템)
2. **화면/기능 단위 분리** — 시나리오를 화면 또는 기능 단위로 분절한다
3. **흐름 재구성** — 각 단위를 다음 형식으로 정규화한다:

```markdown
## [화면/기능명]

**액터:** {역할}
**진입 조건:** {이 화면/기능에 도달하는 조건}
**주요 행동:**
- 행동 1
- 행동 2
**예외/분기:**
- 조건 A이면 → B로 이동
- 조건 C이면 → 에러 표시
**데이터/상태:**
- {관련 데이터나 상태 변화}
```

4. 정규화된 내용을 `parsed_content.md`에 저장

**policy-analyst에게 전달할 메타데이터:** "입력 유형: 서비스 시나리오 / 식별된 액터 수: N / 화면 단위 수: M"

---

## GitHub / 로컬 목업 리포지토리 파싱

HTML/CSS/React 등 목업 코드가 담긴 Git 리포를 입력으로 받는다.
목업은 "무엇을 만들려는가"의 가장 구체적인 증거다 — 화면 구조, 컴포넌트, 라우트, 데이터 흐름을 코드에서 직접 읽는다.

**입력 형태:**
- GitHub URL (예: `https://github.com/owner/repo`)
- 로컬 디렉토리 경로 (예: `/path/to/mockup-project`)

**탐색 전략:**

### Step 1: 구조 파악
```bash
# 로컬 리포
find {path} -type f \( -name "*.html" -o -name "*.tsx" -o -name "*.jsx" -o -name "*.vue" \) \
  | grep -v node_modules | grep -v .git | head -50

# GitHub (gh CLI 사용 가능한 경우)
gh api repos/{owner}/{repo}/git/trees/HEAD?recursive=1 | jq '.tree[].path' | grep -E '\.(html|tsx|jsx|vue)$'
```

### Step 2: 라우트/페이지 목록 추출
프레임워크별 라우트 파일을 탐색한다:

| 프레임워크 | 탐색 대상 |
|-----------|----------|
| Next.js | `app/` 또는 `pages/` 디렉토리 구조 |
| React (CRA/Vite) | `src/App.tsx`, 라우터 설정 파일 |
| Vue | `router/index.js`, `views/` 디렉토리 |
| 순수 HTML | `*.html` 파일 목록 + `<a href>` 링크 |

### Step 3: 각 화면별 정보 추출
각 페이지/컴포넌트 파일에서 다음을 읽는다:
- **화면 제목:** `<title>`, `<h1>`, 컴포넌트명
- **UI 요소:** 버튼, 폼 필드, 테이블, 모달 — 사용자가 조작할 수 있는 모든 요소
- **API 호출:** `fetch`, `axios`, `useQuery` 등 — 어떤 데이터를 다루는지
- **상태/조건:** `if`, `isLoading`, `isLoggedIn` 등 — 화면 분기 조건
- **주석:** 개발자 주석은 정책 힌트일 수 있으므로 보존

### Step 4: 정규화 출력
```markdown
## [화면명 / 라우트 경로]

**파일 경로:** {소스 파일}
**UI 요소:**
- {버튼/폼/테이블 목록}
**API 호출:**
- {엔드포인트 또는 함수명}
**상태/분기:**
- {조건 목록}
**주석:**
- {개발자 주석}
```

**policy-analyst에게 전달할 메타데이터:** "입력 유형: 목업 리포 / 식별된 화면 수: N / 프레임워크: X / API 호출 수: M"

---

## 에러 처리

- 파일 없음 → 경고 메시지 출력, 다른 파일 계속 처리
- PDF 이미지 기반 → "이미지 기반 PDF 파싱 불가" 경고 후 계속
- 구글 슬라이드 403 → "링크가 있는 모든 사용자" 공유 설정 안내
- GitHub 리포 접근 불가 → gh CLI 또는 git clone 시도, 실패 시 리더에게 알림
- 목업 코드에 텍스트가 거의 없는 경우 → "코드 기반 목업으로 UI 요소 위주 분석" 메모 추가
