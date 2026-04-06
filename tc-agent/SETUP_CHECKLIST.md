# 동료 PC 세팅 체크리스트

> 이 폴더를 받은 후 처음 한 번만 실행한다.
> **Mac**: 터미널(Terminal) 사용 / **Windows**: PowerShell 사용 (Windows Terminal 권장)

---

## Step 1. 필수 소프트웨어 설치

### 1-1. Python

| 환경 | 방법 |
|------|------|
| **Mac** | 터미널에서 `python3 --version` 확인. 없으면 https://www.python.org/downloads/ 설치 |
| **Windows** | https://www.python.org/downloads/ 설치. ⚠️ 설치 시 **"Add Python to PATH"** 반드시 체크 |

설치 확인:

**Mac:**
```bash
python3 --version
# 출력 예: Python 3.12.x
```

**Windows (PowerShell):**
```powershell
python --version
# 출력 예: Python 3.12.x
```

---

### 1-2. Claude Code

https://claude.ai/download 에서 본인 OS에 맞는 버전 다운로드 후 설치.

설치 확인:
```
claude --version
```
*(Mac/Windows 동일)*

---

### 1-3. VSCode (md 파일 편집용, 권장)

https://code.visualstudio.com/ 에서 설치.
설치 후 Extensions에서 `Markdown Preview Enhanced` 설치 (선택).

---

## Step 2. 폴더 확인

받은 폴더를 원하는 위치에 놓는다.

**Mac 예시 경로**: `/Users/사용자명/tc-agent`
**Windows 예시 경로**: `C:\Users\사용자명\tc-agent`

다음 항목이 있는지 확인:
- [ ] `HANDOVER.md`
- [ ] `SETUP_CHECKLIST.md`
- [ ] `common/tc-rules.md`
- [ ] `common/tc-sample.md`
- [ ] `scripts/build_excel.py`
- [ ] `.claude/skills/` (하위 스킬 폴더들)
- [ ] `phase3-mobile-mockup/`

---

## Step 3. [Windows 전용] PowerShell 실행 정책 설정

Mac은 이 단계 건너뜀.

PowerShell을 **관리자 권한**으로 실행 후:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
`Y` 입력 후 엔터.

---

## Step 4. Python 가상환경 및 의존성 설치

**Mac (터미널):**
```bash
cd /Users/사용자명/tc-agent
python3 -m venv .venv
source .venv/bin/activate
pip install openpyxl
```

**Windows (PowerShell):**
```powershell
cd "C:\Users\사용자명\tc-agent"
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install openpyxl
```

설치 확인 (공통):
```
python -c "import openpyxl; print('OK')"
# 출력: OK
```
*(Mac은 `python3`, Windows는 `python`)*

---

## Step 5. Claude Code 실행

**Mac:**
```bash
cd /Users/사용자명/tc-agent
claude
```

**Windows (PowerShell):**
```powershell
cd "C:\Users\사용자명\tc-agent"
claude
```

---

## Step 6. 첫 번째 지시

Claude Code 실행 후 본인 경로에 맞게 입력:

**Mac:**
```
이 폴더(/Users/사용자명/tc-agent)에서 TC 자동화 파이프라인을 운영 중이야.
HANDOVER.md를 먼저 읽고, 이후 작업 요청에 따라 진행해줘.
```

**Windows:**
```
이 폴더(C:\Users\사용자명\tc-agent)에서 TC 자동화 파이프라인을 운영 중이야.
HANDOVER.md를 먼저 읽고, 이후 작업 요청에 따라 진행해줘.
```

---

## Step 7. Excel 빌드 동작 확인 (선택)

기존 tc_final.md로 Excel 빌드가 정상 동작하는지 테스트.

**Mac:**
```bash
cd /Users/사용자명/tc-agent
source .venv/bin/activate
python3 scripts/build_excel.py \
  --phase P3_MobileMockup \
  --tc phase3-mobile-mockup/_workspace/05_review/tc_final.md \
  --output phase3-mobile-mockup/outputs
```

**Windows (PowerShell):**
```powershell
cd "C:\Users\사용자명\tc-agent"
.venv\Scripts\Activate.ps1
python scripts\build_excel.py `
  --phase P3_MobileMockup `
  --tc "phase3-mobile-mockup\_workspace\05_review\tc_final.md" `
  --output "phase3-mobile-mockup\outputs"
```

`phase3-mobile-mockup/outputs/` 에 `.xlsx` 파일이 생성되면 성공.

---

## Step 8. TC 웹앱 설치 및 실행 (tc.automation)

TC를 **웹 UI**에서 생성하려면 `tc.automation` 폴더를 별도로 설정해야 합니다.
Git을 클론하면 `tc-agent`과 **같은 부모 폴더**에 `tc.automation`이 있어야 합니다.

### 8-1. Anthropic API 키 설정

**Mac:**
```bash
cd ../tc.automation
cp .env.example .env
# .env 파일을 열어 본인의 API 키 입력
open -e .env
```

**Windows (PowerShell):**
```powershell
cd ..\tc.automation
Copy-Item .env.example .env
# .env 파일을 열어 본인의 API 키 입력
notepad .env
```

`.env` 파일 안에 아래 형식으로 **본인의 키**를 입력:
```
ANTHROPIC_API_KEY=sk-ant-api03-여기에-본인-키-입력
```

> ⚠️ API 키는 각자 개인 키를 사용합니다. https://console.anthropic.com/settings/keys 에서 발급.

---

### 8-2. 패키지 설치

**Mac:**
```bash
cd ../tc.automation
pip3 install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
cd ..\tc.automation
pip install -r requirements.txt
```

---

### 8-3. 웹앱 실행

**Mac — 더블클릭으로 실행:**
- `시작하기_v2.command` 더블클릭

**Mac — 터미널에서 직접:**
```bash
cd ../tc.automation
python3 scripts/app_v2.py
```

**Windows (PowerShell):**
```powershell
cd ..\tc.automation
python scripts\app_v2.py
```

브라우저에서 http://localhost:5001 접속

---

### 8-4. (선택) Google Drive 연동 설정

Google Drive 업로드 기능을 사용할 경우:

1. `config.example.json`을 복사해 `config.json`으로 저장
2. 본인의 Google Drive 폴더 ID 입력
3. Google Cloud Console에서 `credentials.json` 발급 후 `tc.automation/` 폴더에 저장

**Mac:**
```bash
cp config.example.json config.json
# config.json을 열어 upload_folder_id 입력
```

**Windows:**
```powershell
Copy-Item config.example.json config.json
notepad config.json
```

---

## 명령어 대조표

| 목적 | Mac (bash) | Windows (PowerShell) |
|------|-----------|---------------------|
| Python 버전 확인 | `python3 --version` | `python --version` |
| 가상환경 활성화 | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |
| 가상환경 비활성화 | `deactivate` | `deactivate` |
| 폴더 내용 확인 | `ls` 또는 `dir` | `dir` 또는 `ls` |
| 파일 복사 | `cp 원본 대상` | `Copy-Item 원본 대상` |
| 파일 내용 보기 | `cat 파일` | `Get-Content 파일` |
| 텍스트 검색 | `grep "패턴" 파일` | `Select-String "패턴" 파일` |
| 파일 존재 확인 | `[ -f 파일 ]` | `Test-Path 파일` |
