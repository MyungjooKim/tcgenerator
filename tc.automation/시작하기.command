#!/bin/bash
# TC 자동화 시스템 런처
# 이 파일을 더블클릭하면 서버가 시작되고 브라우저가 자동으로 열립니다.

# 이 스크립트가 있는 폴더로 이동
cd "$(dirname "$0")"

PORT=5001

# 이미 실행 중인지 확인
if lsof -i :$PORT -t &>/dev/null; then
  echo "✅ 서버가 이미 실행 중입니다. 브라우저를 엽니다..."
  open "http://localhost:$PORT"
  exit 0
fi

# Python3 경로 확인 — 전용 venv 우선 사용
if [ -f ".venv/bin/python3" ]; then
  PYTHON=".venv/bin/python3"
else
  PYTHON=$(which python3)
fi

if [ -z "$PYTHON" ]; then
  echo "❌ python3 를 찾을 수 없습니다. Python 설치를 확인해주세요."
  echo "   https://www.python.org/downloads/ 에서 설치 후 다시 실행해주세요."
  read -p "엔터를 누르면 종료됩니다..."
  exit 1
fi

# ── 패키지 자동 설치 ───────────────────────────────────────────
echo "📦 필요한 패키지를 확인합니다..."

# flask 확인
if ! "$PYTHON" -c "import flask" &>/dev/null; then
  echo "   → flask 설치 중..."
  "$PYTHON" -m pip install flask --quiet
fi

# google-genai 확인
if ! "$PYTHON" -c "from google import genai" &>/dev/null; then
  echo "   → google-genai 설치 중... (최초 1회, 1~2분 소요)"
  "$PYTHON" -m pip install google-genai --quiet
fi

# openpyxl 확인
if ! "$PYTHON" -c "import openpyxl" &>/dev/null; then
  echo "   → openpyxl 설치 중..."
  "$PYTHON" -m pip install openpyxl --quiet
fi

# google-api-python-client 확인 (Google Drive 업로드용)
if ! "$PYTHON" -c "from googleapiclient.discovery import build" &>/dev/null; then
  echo "   → google-api-python-client 설치 중..."
  "$PYTHON" -m pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib --quiet
fi

echo "✅ 패키지 준비 완료"
echo ""
# ──────────────────────────────────────────────────────────────

echo "🚀 TC 자동화 서버를 시작합니다..."
echo "   브라우저: http://localhost:$PORT"
echo ""
echo "   종료하려면 웹 페이지의 [서버 종료] 버튼을 누르세요."
echo "─────────────────────────────────────────"

# 3초 후 브라우저 오픈 (패키지 설치 완료 후 서버 준비 시간)
(sleep 3 && open "http://localhost:$PORT") &

# 서버 실행
"$PYTHON" scripts/upload_server.py
