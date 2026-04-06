#!/bin/bash
# TC 자동화 시스템 v2 런처 (Mac)
# 이 파일을 더블클릭하면 서버가 시작되고 브라우저가 자동으로 열립니다.

cd "$(dirname "$0")"
PORT=5001

if lsof -i :$PORT -t &>/dev/null; then
  echo "✅ 서버가 이미 실행 중입니다."
  open "http://localhost:$PORT"
  exit 0
fi

if [ -f ".venv/bin/python3" ]; then
  PYTHON=".venv/bin/python3"
else
  PYTHON=$(which python3)
fi

if [ -z "$PYTHON" ]; then
  echo "❌ python3를 찾을 수 없습니다."
  echo "   https://www.python.org/downloads/ 에서 설치 후 재시도하세요."
  read -p "엔터를 누르면 종료됩니다..."
  exit 1
fi

if [ ! -f ".env" ]; then
  echo "⚠️  .env 파일이 없습니다. ANTHROPIC_API_KEY 설정이 필요합니다."
  echo ""
  echo "   1. cp .env.example .env"
  echo "   2. .env 파일을 열어 ANTHROPIC_API_KEY=sk-ant-... 입력"
  echo ""
  read -p "엔터를 누르면 종료됩니다..."
  exit 1
fi

echo "📦 패키지 확인 중..."
"$PYTHON" -m pip install -r requirements.txt --quiet 2>&1 | grep -E "Installed|already"
echo "✅ 준비 완료"
echo ""
echo "🚀 TC 자동화 v2 시작 중... → http://localhost:$PORT"
echo "─────────────────────────────────"

(sleep 3 && open "http://localhost:$PORT") &
set -a; source .env; set +a
"$PYTHON" scripts/app_v2.py
