# TC 자동화 Suite

BDD 형식 테스트 케이스(TC)를 자동 생성하는 도구 모음.

```
repo/
├── tc-agent/   Claude Code 기반 TC 파이프라인
└── tc-ui/              웹 UI (Flask + Claude AI)
```

---

## 처음 설치하는 경우

→ `tc-agent/SETUP_CHECKLIST.md` 를 순서대로 따라 하세요.

---

## API 키 설정 (각자 필수)

```bash
# 웹앱 API 키
cp tc-ui/.env.example tc-ui/.env
# .env 파일에 본인의 Anthropic API 키 입력

# Google Drive 연동 (선택)
cp tc-ui/config.example.json tc-ui/config.json
# config.json에 본인의 Drive 폴더 ID 입력
```

> 🔑 API 키는 각자 https://console.anthropic.com/settings/keys 에서 발급합니다.
> `.env`, `config.json`, `credentials.json` 은 Git에 포함되지 않습니다.

---

## Git 저장소 최초 설정 (첫 번째 사람만)

```bash
cd /path/to/this/folder
git init
git add tc-agent tc-ui .gitignore README.md
git commit -m "initial commit"
git remote add origin https://github.com/YOUR_ORG/tc-suite.git
git push -u origin main
```

## 동료가 클론하는 경우

```bash
git clone https://github.com/YOUR_ORG/tc-suite.git
cd tc-suite

# API 키 설정
cp tc-ui/.env.example tc-ui/.env
# → .env 파일에 본인 키 입력

# 패키지 설치
pip3 install -r tc-ui/requirements.txt          # Mac
pip  install -r tc-ui\requirements.txt          # Windows

# Agent 파이프라인 패키지 설치
cd tc-agent
python3 -m venv .venv && source .venv/bin/activate      # Mac
python  -m venv .venv; .venv\Scripts\Activate.ps1       # Windows
pip install openpyxl
```
