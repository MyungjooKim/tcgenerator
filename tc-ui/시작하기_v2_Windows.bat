@echo off
chcp 65001 > NUL
title TC 자동화 시스템 v2
cd /d "%~dp0"
set PORT=5001

REM Python 경로 설정
if exist ".venv\Scripts\python.exe" (
  set PYTHON=.venv\Scripts\python.exe
) else (
  set PYTHON=python
)

REM .env 파일 확인
if not exist ".env" (
  echo [오류] .env 파일이 없습니다.
  echo.
  echo 1. copy .env.example .env
  echo 2. .env 파일을 열어 ANTHROPIC_API_KEY=sk-ant-... 입력
  echo.
  pause
  exit /b 1
)

REM 패키지 설치
echo [패키지 확인 중...]
%PYTHON% -m pip install -r requirements.txt --quiet
echo [준비 완료]
echo.
echo [TC 자동화 v2 시작] http://localhost:%PORT%

REM 브라우저 오픈 (3초 후)
timeout /t 3 /nobreak > NUL
start "" "http://localhost:%PORT%"

REM .env 로드는 app_v2.py 내부에서 처리됨 (cross-platform)

REM 서버 실행
%PYTHON% scripts\app_v2.py
pause
