@echo off
chcp 65001 > nul
title TC 자동화 시스템

cd /d "%~dp0"

set PORT=5001

:: 이미 실행 중인지 확인
netstat -an 2>nul | find ":%PORT% " | find "LISTENING" > nul 2>&1
if %errorlevel% == 0 (
  echo ✅ 서버가 이미 실행 중입니다. 브라우저를 엽니다...
  start http://localhost:%PORT%
  exit /b 0
)

:: Python 경로 확인
where python > nul 2>&1
if %errorlevel% neq 0 (
  echo ❌ Python 을 찾을 수 없습니다.
  echo    https://www.python.org/downloads/ 에서 설치 후 다시 실행해주세요.
  echo    설치 시 "Add Python to PATH" 체크 필수!
  pause
  exit /b 1
)

:: ── 패키지 자동 설치 ────────────────────────────────────────────
echo 📦 필요한 패키지를 확인합니다...

python -c "import flask" > nul 2>&1
if %errorlevel% neq 0 (
  echo    → flask 설치 중...
  python -m pip install flask --quiet
)

python -c "import openpyxl" > nul 2>&1
if %errorlevel% neq 0 (
  echo    → openpyxl 설치 중...
  python -m pip install openpyxl --quiet
)

python -c "from googleapiclient.discovery import build" > nul 2>&1
if %errorlevel% neq 0 (
  echo    → google-api-python-client 설치 중...
  python -m pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib --quiet
)

echo ✅ 패키지 준비 완료
echo.
:: ────────────────────────────────────────────────────────────────

echo 🚀 TC 자동화 서버를 시작합니다...
echo    브라우저: http://localhost:%PORT%
echo.
echo    종료하려면 웹 페이지의 [서버 종료] 버튼을 누르세요.
echo ─────────────────────────────────────────

:: 3초 후 브라우저 오픈
start /b cmd /c "timeout /t 3 > nul && start http://localhost:%PORT%"

:: 서버 실행
python scripts\upload_server.py

pause
