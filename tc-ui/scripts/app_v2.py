#!/usr/bin/env python3
"""
TC 자동화 v2 — Flask + SSE + Claude AI
PDF/GitHub URL/텍스트 → 실시간 TC 생성 → Excel 출력
실행: python3 scripts/app_v2.py
접속: http://localhost:5001
"""

import os
import sys
import json
import uuid
import queue
import threading
import subprocess
import re
import time
from pathlib import Path
from datetime import datetime

# ── .env 로딩 ──────────────────────────────────────────────────────────────────
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding='utf-8').splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            key, val = k.strip(), v.strip()
            if not os.environ.get(key):   # 빈 값이면 .env 값으로 채움
                os.environ[key] = val

from flask import Flask, request, jsonify, render_template_string, send_file, Response

# ── 경로 설정 ──────────────────────────────────────────────────────────────────
BASE_DIR       = Path(__file__).parent.parent   # /tc-ui/
AGENT_DIR      = BASE_DIR.parent / "tc-agent"
RULES_FILE     = AGENT_DIR / "common" / "tc-rules.md"
BUILD_EXCEL    = AGENT_DIR / "scripts" / "build_excel.py"
WORKSPACE_ROOT   = BASE_DIR / "workspace"
OUTPUTS_DIR      = BASE_DIR / "outputs"
SPECS_DIR        = BASE_DIR / "specs"
TC_FILES_DIR     = BASE_DIR / "tc_files"    # 저장된 TC 마크다운
PROJECTS_FILE    = BASE_DIR / "projects.json"  # 프로젝트 레지스트리
CONFIG_FILE      = BASE_DIR / "config.json"
DRIVE_CREDS_FILE = BASE_DIR / "credentials.json"
DRIVE_TOKEN_FILE = BASE_DIR / ".drive_token.json"
PORT             = int(os.environ.get("PORT", 5001))
MODEL          = "claude-opus-4-5"

WORKSPACE_ROOT.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
SPECS_DIR.mkdir(exist_ok=True)
TC_FILES_DIR.mkdir(exist_ok=True)

# ── 샘플 기획서 ────────────────────────────────────────────────────────────────
SAMPLE_DOC_FILENAME = "sample_planning_쇼핑몰앱.md"
SAMPLE_DOC_CONTENT = """\
# 샘플 기획서 — 온라인 쇼핑몰 앱 v1.0
> 이 문서는 TC 자동화 시스템 점검용 샘플 기획서입니다.

---

## 대분류: 회원 관리 (AUTH)

### 중분류: 회원가입
- 이메일 + 비밀번호 조합으로 회원가입
- 이메일 중복 확인 (실시간 API 검증)
- 비밀번호 규칙: 8자 이상, 영문+숫자+특수문자 조합
- 가입 완료 시 인증 이메일 발송, 24시간 내 미인증 시 계정 비활성화
- 소셜 로그인 지원: 카카오, 네이버, 구글 (OAuth 2.0)

### 중분류: 로그인 / 로그아웃
- 이메일·비밀번호 로그인, 5회 오류 시 계정 30분 잠금
- JWT 토큰 발급 (Access: 1h, Refresh: 30d)
- 자동 로그인 설정 (기기당 Refresh 토큰 저장)
- 로그아웃 시 Refresh 토큰 무효화

### 중분류: 비밀번호 관리
- 비밀번호 찾기: 이메일로 재설정 링크 발송 (유효 10분)
- 로그인 상태에서 비밀번호 변경 (현재 PW 확인 후 변경)
- 재설정 완료 시 모든 기기 세션 만료

### 중분류: 마이페이지
- 회원 정보 수정 (닉네임, 연락처, 배송지)
- 회원 탈퇴 (즉시 개인정보 익명화, 30일 후 완전 삭제)
- 알림 수신 설정 (마케팅 이메일, 앱 푸시, SMS)

---

## 대분류: 상품 탐색 (PROD)

### 중분류: 상품 목록
- 카테고리별 상품 목록 조회 (대분류 → 소분류 depth 3단계)
- 정렬: 인기순, 최신순, 낮은 가격순, 높은 가격순, 리뷰 많은 순
- 필터: 가격 범위, 브랜드, 평점, 배송 유형(일반/당일/새벽)
- 무한 스크롤 (페이지당 20개 로드)
- 품절 상품은 목록 하단 배치, 구매 불가 표시

### 중분류: 상품 검색
- 키워드 검색 (Elasticsearch 기반, 오타 교정 지원)
- 최근 검색어 저장 (최대 20개, 개별/전체 삭제)
- 자동 완성 추천 (입력 2자 이상 시 최대 10개 노출)
- 검색 결과 없을 시 연관 상품 추천

### 중분류: 상품 상세
- 상품명, 가격(정가/할인가), 할인율, 재고 수량 표시
- 이미지 갤러리 (최대 10장, 확대/슬라이드)
- 상품 옵션 선택 (색상, 사이즈 등 조합별 재고 연동)
- 배송 예정일 표시 (재고·배송 유형에 따라 실시간 계산)
- 판매자 정보, 교환/반품 정책 노출

### 중분류: 찜 목록
- 상품 찜 추가/해제 (하트 아이콘 토글)
- 찜 목록 페이지 (가격 변동 표시, 품절 여부 실시간 반영)
- 최대 500개 저장, 초과 시 경고

---

## 대분류: 장바구니 및 주문 (ORDER)

### 중분류: 장바구니
- 상품 추가 (옵션 포함), 수량 변경 (최소 1, 최대 99)
- 개별 항목 삭제 / 전체 삭제
- 품절·판매종료 항목 자동 비활성화 및 안내
- 비로그인 장바구니 지원 (로컬 스토리지, 로그인 시 병합)
- 선택한 항목만 주문하기

### 중분류: 주문서 작성
- 배송지 입력/수정 (기본 배송지 자동 불러오기)
- 배송 메모 선택 (사전 정의 옵션 + 직접 입력)
- 쿠폰 적용 (1회 주문당 1개, 중복 불가)
- 포인트 사용 (100P 이상, 10P 단위 입력)
- 최종 결제 금액 실시간 계산 (상품가 + 배송비 - 할인)

### 중분류: 주문 내역
- 주문 목록: 최근 3개월 기본, 기간 필터 가능
- 주문 상세: 상품 정보, 배송 현황, 결제 정보
- 주문 취소 (결제 완료 후 배송 전까지 가능)
- 구매 확정 (배송 완료 후 자동 14일 or 수동 확정)

---

## 대분류: 결제 (PAY)

### 중분류: 결제 수단
- 신용·체크카드 (국내 주요 8개사 간편 결제)
- 카카오페이, 네이버페이, 토스페이
- 무통장 입금 (가상계좌 발급, 24시간 내 입금 확인)
- 결제 수단 저장 및 기본 결제수단 설정

### 중분류: 결제 처리
- PG사 연동 (토스페이먼츠) — 실결제 / 테스트 모드 전환 가능
- 결제 완료 시 주문 확인 SMS·이메일 즉시 발송
- 결제 실패 시 실패 사유 표시 및 재시도 안내
- 금액 불일치(위변조) 서버 사이드 검증

### 중분류: 환불
- 취소 승인 시 원결제 수단으로 자동 환불 (3~5 영업일)
- 부분 취소 지원 (다품목 주문 중 일부만 취소)
- 가상계좌 환불은 고객 환불 계좌 입력 후 처리
- 포인트·쿠폰 사용분 취소 시 원복 처리 규칙 명시

---

## 대분류: 배송 관리 (DELIV)

### 중분류: 배송 조회
- 운송장 번호 자동 연동 (출고 시 등록)
- 배송 단계: 상품 준비중 → 배송중 → 배송 완료
- 택배사별 배송 조회 페이지 연결 (CJ, 한진, 롯데, 우체국)
- 배송 지연 시 알림 발송 (출고 예정일 +1일 초과)

### 중분류: 교환 / 반품
- 구매 확정 전까지 교환·반품 신청 가능
- 반품 사유 입력 (고객 귀책 / 판매자 귀책 선택)
- 반품 회수 택배사 자동 배정, 회수 운송장 발급
- 교환 상품 재배송 일정 안내

### 중분류: 리뷰
- 구매 확정 후 리뷰 작성 가능 (텍스트 + 이미지 최대 5장)
- 평점 1~5점, 옵션 정보 함께 저장
- 리뷰 수정·삭제 (작성자 본인만)
- 판매자 리뷰 답변 기능
- 신고 기능 (욕설, 광고성 등 — 관리자 검토 후 블라인드)
"""

SAMPLE_PDF_FILENAME = "sample_planning_쇼핑몰앱.pdf"
STATIC_DIR = BASE_DIR / "static"
SAMPLE_PDF_PATH = STATIC_DIR / SAMPLE_PDF_FILENAME


def _find_korean_font():
    """OS별 한글 TTF/TTC 폰트 경로를 반환한다. 없으면 None."""
    import platform
    sys_name = platform.system()
    candidates = []
    if sys_name == "Darwin":
        candidates = [
            "/Library/Fonts/NanumGothic.ttf",
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/Library/Fonts/AppleGothic.ttf",
        ]
    elif sys_name == "Windows":
        candidates = [
            r"C:\Windows\Fonts\malgun.ttf",
            r"C:\Windows\Fonts\gulim.ttc",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
    for p in candidates:
        if Path(p).exists():
            return p
    return None


def _find_korean_bold_font():
    """한글 Bold 폰트 경로. 없으면 일반 폰트로 대체."""
    import platform
    sys_name = platform.system()
    if sys_name == "Darwin":
        for p in ["/Library/Fonts/NanumGothicBold.ttf"]:
            if Path(p).exists():
                return p
    elif sys_name == "Windows":
        for p in [r"C:\Windows\Fonts\malgunbd.ttf"]:
            if Path(p).exists():
                return p
    else:
        for p in ["/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"]:
            if Path(p).exists():
                return p
    return None


def build_sample_pdf(force: bool = False) -> Path:
    """샘플 기획서 PDF를 생성(또는 캐시)하여 경로를 반환한다."""
    STATIC_DIR.mkdir(exist_ok=True)
    if SAMPLE_PDF_PATH.exists() and not force:
        return SAMPLE_PDF_PATH

    try:
        from fpdf import FPDF

        font_path = _find_korean_font()
        bold_path = _find_korean_bold_font() or font_path
        has_kr = font_path is not None

        class SamplePDF(FPDF):
            pass

        pdf = SamplePDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.set_margins(20, 20, 20)
        pdf.add_page()

        if has_kr:
            pdf.add_font("KR",  "",  font_path)
            pdf.add_font("KR",  "B", bold_path)

        L = pdf.l_margin           # 왼쪽 여백
        W = pdf.w - L - pdf.r_margin  # 유효 너비

        def kr(size, bold=False):
            if has_kr:
                pdf.set_font("KR", "B" if bold else "", size)
            else:
                pdf.set_font("Helvetica", "B" if bold else "", size)

        def put(text, w, h, indent=0):
            """x를 항상 왼쪽 여백+indent로 고정한 뒤 multi_cell 출력"""
            pdf.set_x(L + indent)
            pdf.multi_cell(w - indent, h, text)
            pdf.set_x(L)  # 출력 후 x 리셋

        for raw_line in SAMPLE_DOC_CONTENT.split("\n"):
            s = raw_line.strip()
            pdf.set_x(L)  # 매 줄 시작 전 x 리셋 (핵심 수정)

            if s.startswith("# "):          # H1 제목
                kr(16, bold=True)
                pdf.set_text_color(20, 20, 70)
                put(s[2:], W, 9)
                pdf.ln(1)

            elif s.startswith("## "):       # H2 대분류
                pdf.ln(3)
                kr(12, bold=True)
                pdf.set_text_color(0, 95, 125)
                put(s[3:], W, 8)
                pdf.set_x(L)
                pdf.set_draw_color(0, 95, 125)
                pdf.set_line_width(0.4)
                pdf.line(L, pdf.get_y(), L + W, pdf.get_y())
                pdf.ln(2)

            elif s.startswith("### "):      # H3 중분류
                pdf.ln(2)
                kr(11, bold=True)
                pdf.set_text_color(50, 50, 50)
                put(s[4:], W, 7)

            elif s.startswith("- "):        # 불릿 항목
                kr(10)
                pdf.set_text_color(60, 60, 60)
                put("\u2022  " + s[2:], W, 6, indent=4)

            elif s.startswith(">"):         # 인용 (부제)
                kr(9)
                pdf.set_text_color(130, 130, 130)
                put(s.lstrip("> ").strip(), W, 6, indent=2)

            elif s.startswith("---"):       # 수평선
                pdf.ln(2)
                pdf.set_draw_color(200, 200, 200)
                pdf.set_line_width(0.3)
                pdf.line(L, pdf.get_y(), L + W, pdf.get_y())
                pdf.ln(4)

            elif s == "":
                pdf.ln(2)

            else:
                kr(10)
                pdf.set_text_color(50, 50, 50)
                put(s, W, 6)

        pdf.output(str(SAMPLE_PDF_PATH))
        return SAMPLE_PDF_PATH

    except Exception as e:
        print(f"[WARN] PDF 생성 실패: {e}")
        return None


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

# ── 세션 저장소 ────────────────────────────────────────────────────────────────
SESSIONS: dict[str, dict] = {}

def new_session() -> dict:
    sid = str(uuid.uuid4())[:8]
    ws  = WORKSPACE_ROOT / sid
    ws.mkdir(exist_ok=True)
    sess = {
        "id":               sid,
        "workspace":        ws,
        "events":           queue.Queue(),
        "gate_event":       threading.Event(),
        "approved":         None,
        "selected_domains": None,  # None=전체, list=선택된 도메인 코드
        "status":           "idle",
        "result":           None,
        "thread":           None,
        "project_name":     "",
        "stop_requested":   False,
    }
    SESSIONS[sid] = sess
    return sess


class PipelineStopError(Exception):
    """사용자가 중단 버튼을 눌렀을 때 발생"""
    pass


def check_stop(sess: dict):
    """중단 요청 시 PipelineStopError 를 발생시킨다."""
    if sess.get("stop_requested"):
        raise PipelineStopError("사용자가 파이프라인을 중단했습니다.")

# ── 프로젝트 레지스트리 ────────────────────────────────────────────────────────
def load_projects() -> list:
    if PROJECTS_FILE.exists():
        try:
            return json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_project(project_name: str, tc_file: str = "", excel_file: str = "", **extra):
    projects = load_projects()
    existing = next((p for p in projects if p["name"] == project_name), None)
    entry = {
        "name":       project_name,
        "tc_file":    tc_file or (existing or {}).get("tc_file", ""),
        "excel_file": excel_file or (existing or {}).get("excel_file", ""),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    # 기존 필드 보존 (pipeline_state 등)
    if existing:
        for k, v in existing.items():
            if k not in entry:
                entry[k] = v
    # extra 필드 병합
    entry.update(extra)
    if existing:
        projects = [entry if p["name"] == project_name else p for p in projects]
    else:
        projects.insert(0, entry)
    PROJECTS_FILE.write_text(json.dumps(projects, ensure_ascii=False, indent=2), encoding="utf-8")


# ── 프로젝트별 파이프라인 상태 저장 (이어서 작업용) ─────────────────────────────
PIPELINE_STATES_DIR = BASE_DIR / "pipeline_states"
PIPELINE_STATES_DIR.mkdir(exist_ok=True)

def save_pipeline_state(project_name: str, stage: str, data: dict):
    """파이프라인 중간 상태를 프로젝트별 JSON으로 저장"""
    safe = re.sub(r"[^\w\-_]", "_", project_name)[:40]
    state_file = PIPELINE_STATES_DIR / f"{safe}.json"
    state = {
        "project_name": project_name,
        "stage":        stage,
        "saved_at":     datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data":         data,
    }
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    # 프로젝트 레지스트리에도 상태 요약 기록
    save_project(project_name, pipeline_stage=stage, pipeline_saved_at=state["saved_at"])

def load_pipeline_state(project_name: str) -> dict | None:
    """저장된 파이프라인 상태 로드"""
    safe = re.sub(r"[^\w\-_]", "_", project_name)[:40]
    state_file = PIPELINE_STATES_DIR / f"{safe}.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None

def clear_pipeline_state(project_name: str):
    """완료 시 파이프라인 상태 파일 삭제"""
    safe = re.sub(r"[^\w\-_]", "_", project_name)[:40]
    state_file = PIPELINE_STATES_DIR / f"{safe}.json"
    if state_file.exists():
        state_file.unlink()
    # 프로젝트 레지스트리에서 상태 필드 제거
    projects = load_projects()
    for p in projects:
        if p["name"] == project_name:
            p.pop("pipeline_stage", None)
            p.pop("pipeline_saved_at", None)
            break
    PROJECTS_FILE.write_text(json.dumps(projects, ensure_ascii=False, indent=2), encoding="utf-8")


CHECKPOINT_FILE = BASE_DIR / ".bkit" / "state" / "modify_checkpoint.json"
CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)

def save_checkpoint(project_name: str, change_desc: str, stage: str, partial: dict = None):
    """TC 수정 파이프라인 체크포인트 저장"""
    data = {
        "project_name": project_name,
        "change_desc": change_desc,
        "stage": stage,
        "partial": partial or {},
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    CHECKPOINT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_checkpoint() -> dict:
    if CHECKPOINT_FILE.exists():
        try:
            return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def clear_checkpoint():
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()


def push(sess: dict, etype: str, data: dict):
    sess["events"].put({"type": etype, "data": data})

def push_stage(sess, stage: int, label: str, pct: int):
    push(sess, "stage", {"stage": stage, "label": label, "pct": pct})

def push_log(sess, msg: str):
    push(sess, "log", {"msg": msg})

def push_error(sess, msg: str):
    sess["status"] = "error"
    push(sess, "error", {"msg": msg})

# ── Claude API 헬퍼 ────────────────────────────────────────────────────────────
def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 8192) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
        msg = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return msg.content[0].text
    except Exception as e:
        raise RuntimeError(f"Claude API 오류: {e}")

# ── TC 규칙 로딩 ───────────────────────────────────────────────────────────────
FEWSHOT_FILE = AGENT_DIR / "common" / "tc-sample-fewshot.md"

def load_tc_rules() -> str:
    if RULES_FILE.exists():
        return RULES_FILE.read_text(encoding="utf-8")
    return ""

def load_fewshot_examples() -> str:
    if FEWSHOT_FILE.exists():
        return FEWSHOT_FILE.read_text(encoding="utf-8")
    return ""

# ── 프로젝트별 정책 파일 로딩 ──────────────────────────────────────────────────
PROJECTS_RULES_DIR = AGENT_DIR / "projects"

def load_project_policies(project_name: str) -> str:
    """프로젝트명으로 매칭되는 정책 파일들을 로드.
    projects/ 하위 폴더명과 프로젝트명을 대소문자 무시로 매칭."""
    if not PROJECTS_RULES_DIR.exists():
        return ""
    # 프로젝트명 → 폴더명 매칭 (supercycl, tc-manager 등)
    pname_lower = project_name.lower().replace(" ", "").replace("-", "").replace("_", "")
    for folder in PROJECTS_RULES_DIR.iterdir():
        if not folder.is_dir():
            continue
        fname_lower = folder.name.lower().replace(" ", "").replace("-", "").replace("_", "")
        if fname_lower in pname_lower or pname_lower in fname_lower:
            # 해당 폴더의 .md 파일 모두 읽기
            texts = []
            for md_file in sorted(folder.glob("*.md")):
                texts.append(f"### 📋 {md_file.stem}\n\n{md_file.read_text(encoding='utf-8')[:5000]}")
            if texts:
                return "\n\n---\n\n".join(texts)
    return ""

# ── 1단계: 문서 파싱 ──────────────────────────────────────────────────────────
def step_parse(sess: dict, input_type: str, content: str) -> str:
    """단일 소스 파싱 (하위 호환용)"""
    return step_parse_sources(sess, [{"type": input_type, "content": content}])


def step_parse_sources(sess: dict, sources: list) -> str:
    """복수 소스를 각각 파싱한 뒤 하나의 텍스트로 합친다."""
    parts = []
    total = len(sources)
    for i, src in enumerate(sources, 1):
        src_type = src.get("type", "text")
        content  = src.get("content", "").strip()
        push_log(sess, f"[파싱] 소스 {i}/{total} — {src_type}")

        if src_type == "pdf":
            pdf_path = SPECS_DIR / content
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF 파일 없음: {pdf_path}")
            text = extract_pdf_text(pdf_path)
            label = f"📄 PDF: {content}"
            push_log(sess, f"[파싱] PDF 추출 완료 ({len(text):,}자)")
        elif src_type == "url":
            selected_files = src.get("selected_files") or None
            text  = fetch_url_content(sess, content, selected_files=selected_files)
            label = f"🔗 URL: {content}"
            push_log(sess, f"[파싱] URL 추출 완료 ({len(text):,}자)")
        elif src_type == "web":
            text  = fetch_web_page(sess, content)
            label = f"🌐 웹: {content}"
            push_log(sess, f"[파싱] 웹 크롤링 완료 ({len(text):,}자)")
        elif src_type == "md":
            md_path = SPECS_DIR / content
            if not md_path.exists():
                raise FileNotFoundError(f"마크다운 파일 없음: {md_path}")
            text = md_path.read_text(encoding="utf-8")
            label = f"📝 마크다운: {content}"
            push_log(sess, f"[파싱] 마크다운 읽기 완료 ({len(text):,}자)")
        else:
            text  = content
            label = "✏️ 텍스트 입력"
            push_log(sess, f"[파싱] 텍스트 입력 ({len(text):,}자)")

        parts.append(f"===== 소스 {i}/{total} — {label} =====\n\n{text}")

    raw_text = "\n\n".join(parts)
    parsed_path = sess["workspace"] / "01_parsed.md"
    parsed_path.write_text(f"# 파싱 결과\n\n{raw_text}", encoding="utf-8")
    return raw_text


def extract_pdf_text(pdf_path: Path) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        texts = []
        for i, page in enumerate(reader.pages):
            t = page.extract_text()
            if t:
                texts.append(f"--- 페이지 {i+1} ---\n{t}")
        return "\n\n".join(texts)
    except Exception as e:
        raise RuntimeError(f"PDF 파싱 실패: {e}")


def fetch_url_content(sess: dict, url: str, selected_files: list = None) -> str:
    try:
        import requests
    except ImportError:
        raise RuntimeError("requests 패키지가 필요합니다: pip install requests")

    push_log(sess, f"[파싱] URL 접속 중: {url}")

    # GitHub 리포지토리 URL 감지
    gh_match = re.match(r"https?://github\.com/([^/]+)/([^/\s]+?)(?:\.git)?/?$", url)
    if gh_match:
        owner, repo = gh_match.group(1), gh_match.group(2)
        return fetch_github_repo(sess, owner, repo, selected_files=selected_files)

    # github.io 또는 일반 URL
    try:
        headers = {"User-Agent": "Mozilla/5.0 (TC-Automation/2.0)"}
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")

        if "html" in content_type:
            return html_to_text(resp.text)
        else:
            return resp.text
    except Exception as e:
        raise RuntimeError(f"URL 접속 실패: {e}")


def fetch_github_repo(sess: dict, owner: str, repo: str, selected_files: list = None) -> str:
    """GitHub 리포지토리에서 파일 내용을 가져온다.
    selected_files: 경로 문자열 리스트. None이면 .md 파일 최대 10개 자동 선택.
    """
    try:
        import requests
    except ImportError:
        raise RuntimeError("requests 패키지가 필요합니다")

    texts = []
    headers = {"User-Agent": "TC-Automation/2.0"}
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"token {token}"

    # 기본 브랜치 확인
    branch = "main"
    try:
        r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=10)
        if r.status_code == 200:
            branch = r.json().get("default_branch", "main")
    except Exception:
        pass

    if selected_files:
        # 사용자가 선택한 파일만 로드
        push_log(sess, f"[파싱] 선택된 파일 {len(selected_files)}개 로드 중...")
        for fpath in selected_files:
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{fpath}"
            try:
                r = requests.get(raw_url, headers=headers, timeout=15)
                if r.status_code == 200:
                    texts.append(f"## {fpath}\n\n{r.text}")
                    push_log(sess, f"[파싱] ✅ {fpath}")
                else:
                    push_log(sess, f"[파싱] ⚠️ {fpath} 로드 실패 (status {r.status_code})")
            except Exception as e:
                push_log(sess, f"[파싱] ⚠️ {fpath} 오류: {e}")
    else:
        # 선택 없으면 README + .md 최대 10개 자동
        for br in [branch, "main", "master"]:
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{br}/README.md"
            try:
                resp = requests.get(readme_url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    texts.append(f"## README.md\n\n{resp.text}")
                    push_log(sess, f"[파싱] README.md 로드 완료 (branch: {br})")
                    break
            except Exception:
                pass

        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            resp = requests.get(api_url, headers=headers, timeout=15)
            if resp.status_code == 200:
                tree = resp.json().get("tree", [])
                md_files = [f["path"] for f in tree if f["path"].endswith(".md") and f["path"] != "README.md"][:10]
                push_log(sess, f"[파싱] GitHub 파일 트리: MD 파일 {len(md_files)}개 자동 선택")
                for fpath in md_files:
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{fpath}"
                    try:
                        r = requests.get(raw_url, headers=headers, timeout=10)
                        if r.status_code == 200:
                            texts.append(f"## {fpath}\n\n{r.text}")
                    except Exception:
                        pass
        except Exception as e:
            push_log(sess, f"[파싱] GitHub API 오류 (무시): {e}")

    if not texts:
        raise RuntimeError(f"GitHub 리포지토리에서 콘텐츠를 가져올 수 없습니다: {owner}/{repo}")

    return "\n\n---\n\n".join(texts)


def fetch_web_page(sess: dict, url: str) -> str:
    """일반 웹 URL을 크롤링하여 텍스트 추출"""
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except ImportError:
        raise RuntimeError("requests 패키지가 필요합니다: pip install requests")
    push_log(sess, f"[파싱] 웹 크롤링 중: {url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (TC-Automation/2.0)"}
        resp = requests.get(url, headers=headers, timeout=30, verify=False)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "html" in content_type:
            return html_to_text(resp.text)
        else:
            return resp.text
    except Exception as e:
        raise RuntimeError(f"웹 크롤링 실패: {e}")


def html_to_text(html: str) -> str:
    # script/style 제거
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    # 태그 제거
    text = re.sub(r"<[^>]+>", " ", html)
    # 연속 공백 정리
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)
    return text.strip()


# ── 2단계: 정책 분석 ──────────────────────────────────────────────────────────
def step_policy(sess: dict, raw_text: str, project_name: str, focus_area: str = "") -> str:
    push_log(sess, "[정책] Claude AI로 정책 분석 중...")
    system = """당신은 소프트웨어 QA 전문가입니다.
주어진 문서에서 테스트 가능한 정책과 비즈니스 규칙을 추출합니다.
다음 형식으로 출력하세요:

# 정책 분석 결과

## 도메인별 정책
(각 도메인별로 테스트 가능한 정책을 구체적으로 나열)

## 핵심 비즈니스 규칙
(서비스의 핵심 로직과 검증 포인트)

## 예외 처리 정책
(오류 케이스, 엣지 케이스, 유효성 검증 규칙)
"""
    focus_instruction = ""
    if focus_area:
        focus_instruction = f"""

⚠️ 중요: 사용자가 다음 기능에 대한 TC만 생성하려고 합니다. 해당 기능과 관련된 정책/규칙에 집중하세요:
→ {focus_area}

관련 없는 도메인이나 기능의 정책은 간략하게만 다루고, 위 범위의 정책을 상세하게 분석하세요."""
    user = f"""프로젝트: {project_name}

다음 문서에서 TC 작성에 필요한 모든 정책과 규칙을 추출해주세요:

---
{raw_text[:15000]}
---

각 정책은 구체적이고 테스트 가능한 형태로 서술해주세요.{focus_instruction}
"""
    result = call_claude(system, user, max_tokens=4096)
    policy_path = sess["workspace"] / "02_policy.md"
    policy_path.write_text(result, encoding="utf-8")
    push_log(sess, f"[정책] 분석 완료 → {len(result):,}자")
    return result


# ── 3단계: 기능 목록 ──────────────────────────────────────────────────────────
def step_features(sess: dict, policy_text: str, project_name: str, focus_area: str = "") -> str:
    push_log(sess, "[기능] 기능 목록 생성 중...")
    system = """당신은 QA 엔지니어입니다. 정책 분석 결과를 바탕으로 테스트 가능한 기능 목록을 생성합니다.

다음 형식으로 feature_list.md를 작성하세요:

# Feature List — {프로젝트명}

## 도메인코드 — 도메인명

### FT-001 기능명
- 설명: (기능 설명)
- 테스트 포인트: (주요 검증 항목)
- 우선순위: High/Medium/Low

각 도메인의 모든 기능을 빠짐없이 나열하세요.
"""
    focus_instruction = ""
    if focus_area:
        focus_instruction = f"""

⚠️ 중요: 다음 기능 범위에 해당하는 기능을 중심으로 목록을 작성하세요:
→ {focus_area}

해당 범위의 기능은 세부적으로 나열하고, 범위 밖의 기능은 포함하지 마세요."""
    user = f"""프로젝트: {project_name}

다음 정책 분석을 바탕으로 테스트해야 할 기능 목록을 작성해주세요:

---
{policy_text}
---

모든 주요 기능을 도메인별로 분류하여 나열하고, 각 기능의 테스트 포인트를 구체적으로 서술하세요.{focus_instruction}
"""
    result = call_claude(system, user, max_tokens=4096)
    features_path = sess["workspace"] / "03_features.md"
    features_path.write_text(result, encoding="utf-8")
    push_log(sess, f"[기능] 기능 목록 완료 → {len(result):,}자")
    return result


# ── 4단계: 분류표 생성 ────────────────────────────────────────────────────────
def step_classify(sess: dict, features_text: str, project_name: str, focus_area: str = "") -> str:
    push_log(sess, "[분류] 계층 분류표 생성 중...")
    system = """당신은 TC 분류 전문가입니다. 기능 목록을 바탕으로 대분류/중분류/소분류 계층 분류표를 생성합니다.

다음 형식으로 출력하세요:

# TC 분류표 — {프로젝트명}

## 대분류: {대분류명} ({대분류코드})
- 대분류코드: 영문 대문자 4~6자 (예: AUTH, TRAD, FUND)

### 중분류: {중분류명} ({중분류코드})
- 중분류코드: 영문 대문자 4~6자 (예: LOGN, ORDR, BLNC)

#### 소분류
- {소분류명}: {설명}
- {소분류명}: {설명}

규칙:
- 대분류는 도메인 단위
- 중분류는 주요 기능 단위
- 소분류는 세부 케이스 단위
- 코드는 의미를 반영하는 영문 대문자
- ⛔ TC ID를 생성하지 마세요. TC ID는 이후 단계에서 검토자가 결정합니다.
- ⛔ TC ID 생성 규칙, TC ID 예시표, 기능-TC 매핑표를 포함하지 마세요.
- 분류표에는 대분류/중분류/소분류 구조만 출력하세요.
"""
    focus_instruction = ""
    if focus_area:
        focus_instruction = f"""

⚠️ 중요: 다음 범위에 해당하는 기능의 분류표만 생성하세요:
→ {focus_area}

범위 밖의 기능은 분류표에 포함하지 마세요."""
    # 프로젝트별 카테고리 참조 데이터 로드
    project_policies = load_project_policies(project_name)
    category_ref = ""
    if project_policies:
        category_ref = f"""

⚠️ 기존 프로젝트 카테고리 참조: 아래 기존 대분류/중분류 이름과 동일한 용어를 사용하세요.
{project_policies[:4000]}"""
    user = f"""프로젝트: {project_name}

다음 기능 목록을 대분류/중분류/소분류 계층으로 분류해주세요:

---
{features_text}
---

분류 결과는 TC ID 생성의 기반이 되므로, 명확하고 일관성 있는 코드를 사용하세요.{focus_instruction}{category_ref}
"""
    result = call_claude(system, user, max_tokens=4096)
    classify_path = sess["workspace"] / "04_classification_draft.md"
    classify_path.write_text(result, encoding="utf-8")
    push_log(sess, f"[분류] 분류표 생성 완료 → {len(result):,}자")
    return result


# ── 5단계: Human Gate (블로킹) ────────────────────────────────────────────────
def step_gate(sess: dict, classification: str):
    push_log(sess, "[GATE] 분류표 검토 대기 중... 사용자 승인 필요")
    sess["status"] = "gate_waiting"
    push(sess, "gate", {"content": classification})
    # 사용자 승인까지 블로킹
    sess["gate_event"].wait()
    approved_content = sess["approved"]
    push_log(sess, "[GATE] 분류표 승인됨. TC 작성 시작.")
    # 승인된 분류표 저장
    approved_path = sess["workspace"] / "classification_v1_APPROVED.md"
    approved_path.write_text(approved_content, encoding="utf-8")
    return approved_content


# ── 6단계: TC 작성 ────────────────────────────────────────────────────────────
def step_write_tc(sess: dict, approved_classification: str, features_text: str,
                  policy_text: str, project_name: str,
                  selected_domain_codes=None) -> tuple:
    push_log(sess, "[TC 작성] TC 초안 작성 시작...")
    tc_rules = load_tc_rules()
    fewshot = load_fewshot_examples()
    project_policies = load_project_policies(project_name)
    if project_policies:
        push_log(sess, f"[TC 작성] 프로젝트 정책 로드됨: {project_name}")
    if fewshot:
        push_log(sess, f"[TC 작성] Few-shot 예시 로드됨")

    # 도메인 목록 추출
    all_domains = extract_domains(approved_classification)

    # 범위 필터 적용
    if selected_domain_codes:
        domains = [d for d in all_domains if d["code"] in selected_domain_codes]
        skipped = [d["code"] for d in all_domains if d["code"] not in selected_domain_codes]
        if skipped:
            push_log(sess, f"[TC 작성] 범위 제외 도메인: {', '.join(skipped)}")
    else:
        domains = all_domains

    if not domains:
        raise RuntimeError("선택된 도메인이 없습니다. 범위를 다시 확인하세요.")

    # SuiteCode 매핑 (Human Gate에서 검토자가 입력한 코드)
    suite_codes = sess.get("suite_codes", [])
    for i, domain in enumerate(domains):
        if i < len(suite_codes) and suite_codes[i]:
            domain["suite_code"] = suite_codes[i]
    if suite_codes:
        push_log(sess, f"[TC 작성] SuiteCode 매핑: {', '.join(d.get('suite_code', '?') for d in domains)}")

    push_log(sess, f"[TC 작성] 생성 대상 도메인 {len(domains)}개: {', '.join(d['code'] for d in domains)}")

    all_tc_parts = []
    total_tc = 0

    for i, domain in enumerate(domains):
        domain_code = domain["code"]
        domain_name = domain["name"]
        push_log(sess, f"[TC 작성] [{i+1}/{len(domains)}] {domain_code} — {domain_name} 작성 중...")
        push(sess, "stage", {
            "stage": 4,
            "label": f"TC 작성: {domain_code} ({i+1}/{len(domains)})",
            "pct":   55 + int(25 * (i / max(len(domains), 1)))
        })

        system = build_tc_system_prompt(tc_rules, approved_classification, project_policies, fewshot)
        user = build_tc_user_prompt(domain, features_text, policy_text, project_name, approved_classification)

        try:
            tc_draft = call_claude(system, user, max_tokens=8192)
        except Exception as e:
            push_log(sess, f"[TC 작성] {domain_code} 오류: {e}, 재시도...")
            time.sleep(2)
            try:
                tc_draft = call_claude(system, user, max_tokens=8192)
            except Exception as e2:
                push_log(sess, f"[TC 작성] {domain_code} 실패 (건너뜀): {e2}")
                continue

        # 잘림 감지: 마지막 TC에 **테스트 단계** 또는 **예상 결과**가 없으면 이어서 생성
        last_tc_match = list(re.finditer(r"^###\s", tc_draft, re.MULTILINE))
        if last_tc_match:
            last_tc_block = tc_draft[last_tc_match[-1].start():]
            has_steps = "**테스트 단계**" in last_tc_block
            has_expected = "**예상 결과**" in last_tc_block
            if not has_steps or not has_expected:
                push_log(sess, f"[TC 작성] {domain_code} 마지막 TC 불완전 — 이어서 생성 중...")
                continue_prompt = f"이전 응답이 중간에 잘렸습니다. 아래 TC를 이어서 완성해주세요. **테스트 단계**와 **예상 결과**를 반드시 포함하세요.\\n\\n---\\n{last_tc_block}"
                try:
                    continuation = call_claude(system, continue_prompt, max_tokens=4096)
                    # 잘린 마지막 TC를 교체
                    tc_draft = tc_draft[:last_tc_match[-1].start()] + continuation
                    push_log(sess, f"[TC 작성] {domain_code} 보완 완료")
                except Exception:
                    push_log(sess, f"[TC 작성] {domain_code} 보완 실패 — 불완전한 TC 포함")

        # 도메인별 파일 저장
        draft_path = sess["workspace"] / f"tc_draft_{domain_code}.md"
        draft_path.write_text(tc_draft, encoding="utf-8")

        # TC 수 카운트
        tc_count = len(re.findall(r"^###\s", tc_draft, re.MULTILINE))
        total_tc += tc_count
        all_tc_parts.append(tc_draft)
        push_log(sess, f"[TC 작성] {domain_code} 완료 — TC {tc_count}개")
        check_stop(sess)  # 도메인 완료 후 중단 체크

    if not all_tc_parts:
        raise RuntimeError("TC 작성 결과가 없습니다.")

    min_tc = max(1, round(total_tc * 0.35))
    return "\n\n---\n\n".join(all_tc_parts), total_tc, min_tc


def extract_domains(classification: str) -> list[dict]:
    domains = []
    # "## 대분류: {이름} ({코드})" 패턴 추출
    pattern = re.compile(
        r"##\s+대분류[:\s]+([^\(\n]+?)\s*[\(\（]([A-Z]{2,8})[\)\）]",
        re.MULTILINE
    )
    for m in pattern.finditer(classification):
        domains.append({"name": m.group(1).strip(), "code": m.group(2).strip()})

    # 패턴이 없으면 섹션 헤딩 기반 폴백
    if not domains:
        for line in classification.splitlines():
            line = line.strip()
            if line.startswith("## "):
                text = line[3:].strip()
                # 코드 추출 시도
                cm = re.search(r"[\(\（]([A-Z]{2,8})[\)\）]", text)
                if cm:
                    code = cm.group(1)
                    name = re.sub(r"\s*[\(\（][A-Z]{2,8}[\)\）]", "", text).strip()
                    domains.append({"name": name, "code": code})

    # 최소 1개 보장
    if not domains:
        domains = [{"name": "전체 기능", "code": "FUNC"}]

    return domains


def build_tc_system_prompt(tc_rules: str, classification: str, project_policies: str = "", fewshot: str = "") -> str:
    policy_section = ""
    if project_policies:
        policy_section = f"""

## 프로젝트별 정책 (반드시 준수)

{project_policies[:6000]}
"""
    fewshot_section = ""
    if fewshot:
        fewshot_section = f"""

## 참고 예시 (⚠️ 이 형식과 수준을 따라 작성하세요)

아래는 실제 사용 중인 TC 예시입니다. 형식, 상세도, 어투를 동일하게 따르세요.

{fewshot[:5000]}
"""
    return f"""당신은 전문 소프트웨어 QA 엔지니어입니다. 주어진 도메인의 테스트 케이스를 작성합니다.

## TC 작성 규칙

{tc_rules[:8000] if tc_rules else "표준 TC 형식을 따릅니다."}
{policy_section}{fewshot_section}
## 분류표
{classification[:3000]}

## TC 생성 카테고리 (4가지 — 순서대로 작성, 비율 준수)

각 도메인(중분류)에 대해 아래 4가지 카테고리 순서로 TC를 작성하세요.
해당 카테고리에 만들 TC가 없으면 skip 합니다.
⚠️ 카테고리 3(예외)과 4(에러)를 반드시 포함하세요. Positive만으로 구성하지 마세요.

### 카테고리 1: UI/UX 체크 (분류: Positive, 우선순위: Medium~High) — 약 20%
- 화면 레이아웃, 요소 배치, 텍스트 표시가 올바른지 확인
- 초기 진입 시 기본 상태 (기본값, placeholder, 비활성 버튼 등)
- 반응형 / 해상도별 레이아웃 깨짐 여부
- 로딩 상태, 빈 데이터 표시, 툴팁/안내 문구

### 카테고리 2: 주요 기능 (분류: Positive, 우선순위: High) — 약 35%
- 핵심 비즈니스 흐름 (Happy Path)
- 사용자가 가장 자주 수행하는 동작
- 데이터 입력 → 처리 → 결과 확인의 정상 흐름
- CRUD 동작, 상태 전환, 네비게이션

### 카테고리 3: 예외 기능 — 비즈니스 위험 중심 (분류: Negative, 우선순위: High~Medium) — 약 25%
- 잘못된 입력, 경계값, 허용 범위 초과
- 권한 없는 접근, 인증 만료 상태에서의 동작
- 동시 접근, 중복 요청 (더블 클릭 등)
- 데이터 정합성 위험 (잔고 부족, 수량 초과 등)
- 미연동 상태에서의 기능 접근

### 카테고리 4: 에러 처리 및 비기능 (분류: Edge, 우선순위: Medium~Low) — 약 20%
- 네트워크 오류, 서버 타임아웃 시 에러 메시지 표시
- 빈 응답, 잘못된 응답 형식에 대한 방어
- 성능 관련 (로딩 시간, 대량 데이터 표시)
- 접근성 (키보드 조작, 포커스 이동)

## Smoke TC 선별
- 카테고리 1, 2에서 High 우선순위 TC를 bold 처리 (### **...**)
- 카테고리 3에서 High Negative TC도 bold 처리

## 형식 규칙

### TC ID 규칙 (⚠️ 반드시 준수)
- 형식: `{{ProjectCode}}-{{SuiteCode}}-{{NNN}}`
- ProjectCode: `SC` (PC Web) 또는 `SM` (Mobile Web) — 프로젝트명에서 판별
- SuiteCode: 시트명의 약어 (대문자 영문, 하이픈 허용). 예: GNB&Footer→GNBF, Trade-Order→TRD-ORDR
- NNN: 001부터 순차 번호 (3자리 zero-padding)
- ⛔ `TC-`로 시작하면 안 됨. 반드시 ProjectCode(`SC` 또는 `SM`)로 시작
- 예시: SC-GNBF-001, SC-TRD-ACCT-001, SM-LITE-001, SM-TRD-ORDR-001

### TC 헤딩
- Smoke TC: `### **{{ProjectCode}}-{{SuiteCode}}-{{NNN}}** — {{제목}}`  (bold)
- 일반 TC: `### {{ProjectCode}}-{{SuiteCode}}-{{NNN}} — {{제목}}`  (plain)
- [★] 기호 사용 금지

### 사전 조건
- 번호 개조식: `1. 조건A / 2. 조건B`
- 어미: `~인 상태 / ~된 상태 / ~한 상태`
- 불릿(-) 금지

### TC 출력 형식
```
### {{ProjectCode}}-{{SuiteCode}}-{{NNN}} — [제목]

| 항목 | 내용 |
|------|------|
| 대분류 | {{대분류명}} ({{대분류코드}}) |
| 중분류 | {{중분류명}} |
| 소분류 | {{소분류명}} |
| 분류 | Positive/Negative/Edge |
| 우선순위 | High/Medium/Low |
| 플랫폼 | Web(Mobile) |
| 연관 화면 | /경로 또는 화면명 |

**사전 조건**
1. 조건A인 상태
2. 조건B된 상태

**테스트 단계**
1. 단계 1
2. 단계 2

**예상 결과**
- 결과 1

**비고**
- (없으면 생략)
```

비개발자도 이해할 수 있도록 구체적으로 작성하세요. 모호한 표현("정상적으로", "제대로") 금지.
"""


def _detect_project_code(project_name: str) -> str:
    """프로젝트명에서 ProjectCode 추출"""
    name_lower = project_name.lower()
    if "mobile" in name_lower or "모바일" in name_lower:
        return "SM"
    return "SC"

def build_tc_user_prompt(domain: dict, features_text: str, policy_text: str,
                          project_name: str, classification: str) -> str:
    # 해당 도메인의 분류 섹션 추출
    domain_section = extract_domain_section(classification, domain["code"])
    project_code = _detect_project_code(project_name)

    suite_code = domain.get("suite_code", "")
    if suite_code:
        tc_id_instruction = f"⚠️ TC ID: `{project_code}-{suite_code}-NNN` (예: {project_code}-{suite_code}-001, {project_code}-{suite_code}-002). 이 SuiteCode를 반드시 사용하세요."
    else:
        tc_id_instruction = f"⚠️ TC ID의 ProjectCode: `{project_code}` (예: {project_code}-XXXX-001). `TC-`로 시작하면 안 됩니다."

    return f"""프로젝트: {project_name}
도메인: {domain['name']} ({domain['code']})
{tc_id_instruction}

## 이 도메인의 분류 구조
{domain_section}

## 전체 기능 목록 (참고)
{features_text[:3000]}

## 관련 정책
{policy_text[:3000]}

위 도메인({domain['name']})에 속하는 TC를 아래 4가지 카테고리 순서로 작성해주세요.
해당 카테고리에 만들 TC가 없으면 skip합니다.

1. UI/UX 체크: 화면 표시, 초기 상태, 레이아웃 (Positive, Medium~High) — 전체의 약 20%
2. 주요 기능: 핵심 정상 흐름 (Positive, High) — bold 처리 — 전체의 약 35%
3. 예외 기능: 잘못된 입력, 권한 오류, 잔고 부족, 중복 요청 등 (Negative, High~Medium) — High는 bold — 전체의 약 25%
4. 에러 처리 및 비기능: 네트워크 오류, 타임아웃, 빈 응답, 성능 (Edge, Medium~Low) — 전체의 약 20%

⚠️ 카테고리 3(예외)과 4(에러)를 반드시 포함하세요. Positive만으로 구성하지 마세요.
- 사전 조건은 반드시 번호 개조식으로 작성
- 각 소분류별로 적절한 수의 TC 작성 (무의미한 TC 양산 금지)
"""


def extract_domain_section(classification: str, domain_code: str) -> str:
    lines = classification.splitlines()
    result = []
    in_section = False
    for line in lines:
        if re.search(rf"[\(\（]{domain_code}[\)\）]", line):
            in_section = True
        elif in_section and re.match(r"^##\s+대분류", line) and domain_code not in line:
            break
        if in_section:
            result.append(line)
    return "\n".join(result) if result else classification[:1000]


# ── 7단계: TC 검토 ────────────────────────────────────────────────────────────
def step_review(sess: dict, tc_content: str, project_name: str) -> str:
    push_log(sess, "[검토] TC 품질 검토 중...")
    system = """당신은 시니어 QA 리뷰어입니다. TC 초안을 검토하고 개선 리포트를 작성합니다."""
    user = f"""프로젝트: {project_name}

다음 TC 초안을 검토하고 review_report.md를 작성해주세요:

검토 항목:
1. TC ID 일관성 및 중복 여부
2. 사전 조건 작성 규칙 준수 여부
3. Positive/Negative/Edge 비율
4. 최소 TC 세트 선별 적절성
5. 예상 결과 측정 가능성
6. 누락된 케이스

TC 초안 (처음 5000자):
---
{tc_content[:5000]}
---

리포트 형식:
# TC 검토 보고서
## 전체 요약
## 발견된 이슈
## 개선 권장 사항
## 최소 TC 세트 검증
"""
    result = call_claude(system, user, max_tokens=3000)
    review_path = sess["workspace"] / "07_review_report.md"
    review_path.write_text(result, encoding="utf-8")
    push_log(sess, "[검토] 검토 완료")
    return result


# ── 8단계: tc_final.md 생성 및 Excel 빌드 ─────────────────────────────────────
def step_build_excel(sess: dict, tc_content: str, project_name: str,
                     total_tc: int, min_tc: int) -> Path:
    push_log(sess, "[빌드] tc_final.md 생성 중...")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"""# TC 최종본 — {project_name}

## 메타 정보
- 생성일: {now}
- Phase: P_WebApp
- 총 TC: {total_tc}개 / 최소 TC: {min_tc}개

---

"""
    tc_final_content = header + tc_content
    tc_final_path = sess["workspace"] / "tc_final.md"
    tc_final_path.write_text(tc_final_content, encoding="utf-8")
    push_log(sess, f"[빌드] tc_final.md 저장 완료 ({len(tc_final_content):,}자)")

    # 출력 디렉토리
    out_dir = OUTPUTS_DIR

    # build_excel.py 호출
    if BUILD_EXCEL.exists():
        push_log(sess, f"[빌드] build_excel.py 호출 중...")
        try:
            proc = subprocess.run(
                [sys.executable, str(BUILD_EXCEL),
                 "--phase", "P_WebApp",
                 "--tc",    str(tc_final_path),
                 "--output", str(out_dir)],
                capture_output=True, text=True, timeout=120
            )
            if proc.returncode == 0:
                push_log(sess, "[빌드] build_excel.py 성공")
                # 가장 최근 Excel 파일 찾기
                excel_files = sorted(out_dir.glob("*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
                if excel_files:
                    return excel_files[0]
            else:
                push_log(sess, f"[빌드] build_excel.py 오류: {proc.stderr[:500]}")
        except subprocess.TimeoutExpired:
            push_log(sess, "[빌드] build_excel.py 타임아웃, fallback으로 직접 생성")
        except Exception as e:
            push_log(sess, f"[빌드] build_excel.py 예외: {e}")

    # Fallback: 직접 Excel 생성
    push_log(sess, "[빌드] fallback: openpyxl로 직접 Excel 생성 중...")
    return build_excel_fallback(tc_final_content, out_dir, project_name, total_tc, min_tc)


def build_excel_fallback(tc_content: str, out_dir: Path, project_name: str,
                          total_tc: int, min_tc: int) -> Path:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise RuntimeError("openpyxl 미설치: pip install openpyxl")

    NAVY, BLUE, TEAL = "1E2761", "3557A0", "028090"
    LIGHT, WHITE = "EEF1F8", "FFFFFF"

    def fill(c): return PatternFill("solid", fgColor=c)
    def hfont(bold=True, size=10, color=WHITE):
        return Font(name="Calibri", bold=bold, size=size, color=color)
    def bdr():
        s = Side(style="thin", color="D0D7DE")
        return Border(left=s, right=s, top=s, bottom=s)
    def center(w=False): return Alignment(horizontal="center", vertical="center", wrap_text=w)
    def left_align(w=True): return Alignment(horizontal="left", vertical="center", wrap_text=w)

    wb = Workbook()
    wb.remove(wb.active)

    # 표지 시트
    cov = wb.create_sheet("표지")
    cov.sheet_view.showGridLines = False
    cov.merge_cells("A1:J3")
    c = cov["A1"]
    c.value = f"TC Checklist — {project_name}"
    c.font = hfont(size=18)
    c.fill = fill(NAVY)
    c.alignment = center()
    cov.row_dimensions[1].height = 60

    meta = [
        ("작성일", datetime.now().strftime("%Y-%m-%d")),
        ("프로젝트", project_name),
        ("Phase", "P_WebApp"),
        ("총 TC 수", str(total_tc)),
        ("최소 TC 수", str(min_tc)),
        ("생성 도구", "TC 자동화 v2 (Claude AI)"),
    ]
    for ri, (lbl, val) in enumerate(meta, 5):
        c = cov.cell(ri, 1, lbl)
        c.font = hfont(); c.fill = fill(BLUE); c.alignment = center(); c.border = bdr()
        cov.merge_cells(f"A{ri}:C{ri}")
        c = cov.cell(ri, 4, val)
        c.font = hfont(bold=False, color=NAVY)
        c.fill = fill(LIGHT); c.alignment = left_align(w=False); c.border = bdr()
        cov.merge_cells(f"D{ri}:J{ri}")
        cov.row_dimensions[ri].height = 24
    for i in range(1, 11):
        cov.column_dimensions[get_column_letter(i)].width = 12
    cov.column_dimensions["A"].width = 16
    cov.column_dimensions["D"].width = 40

    # TC 전체목록 시트
    ws = wb.create_sheet("TC 전체목록")
    ws.freeze_panes = "A3"

    HEADERS = ["Smoke", "TC ID", "우선순위", "거래소", "대분류", "중분류", "소분류", "사전 조건", "스텝", "기대 결과"]
    COL_W   = [8,           18,     10,       10,      14,     14,     16,      50,       50,     50]

    def _priority_kr(p):
        return {"High": "높음", "Medium": "보통", "Low": "낮음"}.get(p, p or "보통")

    for ci, (h, w) in enumerate(zip(HEADERS, COL_W), 1):
        c = ws.cell(1, ci, h)
        c.font = hfont(); c.fill = fill(NAVY); c.alignment = center(); c.border = bdr()
        ws.column_dimensions[get_column_letter(ci)].width = w
    ws.row_dimensions[1].height = 22

    # TC 파싱 및 행 삽입
    tcs = parse_tc_markdown(tc_content)

    # Smoke 마킹: 중분류별 대표 Positive 1개 + High Negative 1개 + 대분류별 최소 1개
    from collections import defaultdict
    mid_groups = defaultdict(list)
    for tc in tcs:
        mid_groups[(tc.get("major",""), tc.get("middle",""))].append(tc)
    for key, group in mid_groups.items():
        pos_done = False
        for pri_t in [("high","높음"),("medium","보통"),("low","낮음")]:
            if pos_done: break
            for tc in group:
                if tc.get("priority","").lower() in pri_t and tc.get("type","").lower() == "positive":
                    tc["_smoke"] = True; pos_done = True; break
        neg_done = False
        for tc in group:
            if neg_done: break
            if tc.get("priority","").lower() in ("high","높음") and tc.get("type","").lower() == "negative":
                tc["_smoke"] = True; neg_done = True
    domain_has = {}
    for tc in tcs:
        if tc.get("_smoke"): domain_has[tc.get("major","")] = True
    for tc in tcs:
        d = tc.get("major","")
        if d not in domain_has: tc["_smoke"] = True; domain_has[d] = True

    FILL_MIN  = PatternFill("solid", fgColor="FFF9C4")
    FILL_NORM = PatternFill("solid", fgColor="FFFFFF")

    for ri, tc in enumerate(tcs, 2):
        is_min = tc.get("is_min", False)
        row_fill = FILL_MIN if is_min else FILL_NORM
        row_data = [
            "Y" if tc.get("_smoke") else "",
            tc.get("id", ""),
            _priority_kr(tc.get("priority", "")),
            "",  # 거래소
            tc.get("major", ""),
            tc.get("middle", ""),
            tc.get("minor", ""),
            tc.get("precondition", ""),
            tc.get("steps", ""),
            tc.get("expected", ""),
        ]
        for ci, val in enumerate(row_data, 1):
            c = ws.cell(ri, ci, val)
            c.fill = row_fill
            c.alignment = left_align() if ci >= 9 else center()
            c.border = bdr()
            c.font = Font(name="Calibri", size=9,
                          bold=(ci == 2 and is_min), color="1E2761" if is_min else "222222")
        ws.row_dimensions[ri].height = max(30, min(120, len(str(row_data[8])) // 3 + 20))

    # 통계 시트
    stat = wb.create_sheet("통계")
    stat.sheet_view.showGridLines = False
    stat.merge_cells("A1:E1")
    c = stat["A1"]
    c.value = "TC 통계 요약"
    c.font = hfont(size=14); c.fill = fill(NAVY); c.alignment = center()
    stat.row_dimensions[1].height = 36

    type_counts = {}
    priority_counts = {}
    for tc in tcs:
        t = tc.get("type", "Unknown")
        p = tc.get("priority", "Unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
        priority_counts[p] = priority_counts.get(p, 0) + 1

    stat_data = [
        ("총 TC 수", total_tc),
        ("최소 TC 수", min_tc),
        ("Positive", type_counts.get("Positive", 0)),
        ("Negative", type_counts.get("Negative", 0)),
        ("Edge", type_counts.get("Edge", 0)),
        ("High 우선순위", priority_counts.get("High", 0)),
        ("Medium 우선순위", priority_counts.get("Medium", 0)),
        ("Low 우선순위", priority_counts.get("Low", 0)),
    ]
    for ri, (lbl, val) in enumerate(stat_data, 3):
        c = stat.cell(ri, 1, lbl)
        c.font = hfont(); c.fill = fill(BLUE); c.alignment = center(); c.border = bdr()
        stat.merge_cells(f"A{ri}:C{ri}")
        c = stat.cell(ri, 4, val)
        c.font = hfont(bold=False, color=NAVY)
        c.fill = fill(LIGHT); c.alignment = center(); c.border = bdr()
        stat.column_dimensions["A"].width = 20
        stat.column_dimensions["D"].width = 15

    # 파일 저장
    today = datetime.now().strftime("%Y%m%d")
    safe_name = re.sub(r"[^\w\-_]", "_", project_name)[:20]
    version = 1
    while True:
        fname = f"SPCY_TC_P_WebApp_{safe_name}_{today}_v{version}.xlsx"
        fpath = out_dir / fname
        if not fpath.exists():
            break
        version += 1

    wb.save(str(fpath))
    return fpath


def parse_tc_markdown(content: str) -> list[dict]:
    """TC Markdown을 파싱하여 딕셔너리 리스트로 변환"""
    tcs = []
    # TC 블록 분할
    blocks = re.split(r"\n(?=###\s)", content)

    for block in blocks:
        if not block.strip().startswith("###"):
            continue
        # 카테고리 구분 헤더 스킵
        first_line = block.strip().split("\n")[0]
        if re.match(r"###\s*카테고리\s*\d", first_line):
            continue
        tc = parse_single_tc(block)
        if tc.get("id"):
            tcs.append(tc)
    return tcs


def parse_single_tc(block: str) -> dict:
    tc = {}
    lines = block.strip().splitlines()
    if not lines:
        return tc

    # 제목 줄 파싱
    heading = lines[0]
    is_min = bool(re.search(r"###\s+\*\*", heading))
    tc["is_min"] = is_min

    # TC ID 추출
    id_match = re.search(r"(SC-[A-Z]+-[A-Z]+-\d+|[A-Z]+-[A-Z]+-\d+)", heading)
    tc["id"] = id_match.group(1) if id_match else ""

    # 제목 추출
    title_match = re.search(r"—\s+(.+?)(?:\s*\*\*)?$", heading)
    if title_match:
        title = title_match.group(1).strip()
        title = re.sub(r"\*+", "", title).strip()
        tc["title"] = title
    else:
        tc["title"] = re.sub(r"^###\s+\*?\*?[A-Z\-0-9]+\*?\*?\s*—?\s*", "", heading).strip()

    # 테이블 파싱
    for line in lines:
        line = line.strip()
        if "|" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                key, val = parts[0], parts[1]
                if "대분류" in key: tc["major"] = val
                elif "중분류" in key: tc["middle"] = val
                elif "소분류" in key: tc["minor"] = val
                elif "분류" in key and "대" not in key and "중" not in key and "소" not in key:
                    tc["type"] = val
                elif "우선순위" in key: tc["priority"] = val
                elif "플랫폼" in key: tc["platform"] = val
                elif "연관 화면" in key or "화면" in key: tc["screen"] = val

    # 섹션 파싱
    tc["precondition"] = extract_section(block, "사전 조건")
    tc["steps"]        = extract_section(block, "테스트 단계")
    tc["expected"]     = extract_section(block, "예상 결과")
    tc["note"]         = extract_section(block, "비고")

    # 기본값
    tc.setdefault("major", "")
    tc.setdefault("middle", "")
    tc.setdefault("minor", "")
    tc.setdefault("type", "Positive")
    tc.setdefault("priority", "Medium")
    tc.setdefault("platform", "")
    tc.setdefault("screen", "")

    return tc


def extract_section(block: str, section_name: str) -> str:
    pattern = re.compile(
        rf"\*\*{re.escape(section_name)}\*\*\n(.*?)(?=\n\*\*[가-힣\s]+\*\*|\Z)",
        re.DOTALL
    )
    m = pattern.search(block)
    if not m:
        return ""
    text = m.group(1).strip()
    # 사전 조건: 불릿(-) 형식이면 번호 개조식으로 변환
    if section_name == "사전 조건":
        lines = text.splitlines()
        # 불릿 라인이 하나라도 있으면 전체를 번호로 변환
        has_bullet = any(re.match(r"^[-*]\s+", l) for l in lines)
        if has_bullet:
            numbered, n = [], 1
            for l in lines:
                l = l.strip()
                if not l:
                    continue
                # 이미 번호가 있으면 그대로, 불릿이면 번호 부여
                if re.match(r"^\d+\.", l):
                    numbered.append(l)
                else:
                    body = re.sub(r"^[-*]\s+", "", l)
                    numbered.append(f"{n}. {body}")
                    n += 1
            text = "\n".join(numbered)
    return text


# ── 메인 파이프라인 ────────────────────────────────────────────────────────────
def run_pipeline(sess: dict, sources: list, project_name: str):
    focus_area = sess.get("focus_area", "")
    # 이어서 작업인지 확인
    resumed = sess.get("_resumed_state")
    # 소스 정보 보존 (이어서 작업 시에는 이전 상태에서 가져옴)
    if sources:
        _sources_info = [{"type": s.get("type",""), "content": s.get("content",""), "selected_files": s.get("selected_files")} for s in sources]
    elif resumed:
        _sources_info = resumed.get("data", {}).get("sources_info", [])
    else:
        _sources_info = []
    try:
        # ── 파싱 ──
        if resumed and resumed.get("stage") in ("policy", "features", "classifying", "gate_waiting", "tc_writing"):
            raw_text = resumed["data"].get("raw_text", "")
            push_log(sess, f"[이어서] 파싱 결과 복원됨 ({len(raw_text):,}자)")
        else:
            sess["status"] = "parsing"
            push_stage(sess, 1, "문서 파싱", 5)
            raw_text = step_parse_sources(sess, sources)
            check_stop(sess)
            sources_info = [{"type": s.get("type",""), "content": s.get("content",""), "selected_files": s.get("selected_files")} for s in sources]
            save_pipeline_state(project_name, "parsed", {"raw_text": raw_text[:20000], "focus_area": focus_area, "sources_info": sources_info})
            save_project(project_name, last_sources=sources_info, last_focus_area=focus_area)

        if focus_area:
            push_log(sess, f"[포커스] TC 생성 범위: {focus_area}")

        # ── 정책 분석 ──
        if resumed and resumed.get("stage") in ("features", "classifying", "gate_waiting", "tc_writing"):
            policy_text = resumed["data"].get("policy_text", "")
            push_log(sess, f"[이어서] 정책 분석 복원됨 ({len(policy_text):,}자)")
        else:
            sess["status"] = "policy"
            push_stage(sess, 2, "정책 분석", 15)
            policy_text = step_policy(sess, raw_text, project_name, focus_area)
            check_stop(sess)
            save_pipeline_state(project_name, "policy", {"raw_text": raw_text[:20000], "policy_text": policy_text, "focus_area": focus_area, "sources_info": _sources_info})

        # ── 기능 목록 ──
        if resumed and resumed.get("stage") in ("classifying", "gate_waiting", "tc_writing"):
            features_text = resumed["data"].get("features_text", "")
            push_log(sess, f"[이어서] 기능 목록 복원됨 ({len(features_text):,}자)")
        else:
            sess["status"] = "features"
            push_stage(sess, 2, "기능 목록 생성", 25)
            features_text = step_features(sess, policy_text, project_name, focus_area)
            check_stop(sess)
            save_pipeline_state(project_name, "features", {"raw_text": raw_text[:20000], "policy_text": policy_text, "features_text": features_text, "focus_area": focus_area, "sources_info": _sources_info})

        # ── 분류표 ──
        if resumed and resumed.get("stage") in ("gate_waiting", "tc_writing"):
            classification = resumed["data"].get("classification", "")
            push_log(sess, f"[이어서] 분류표 복원됨 ({len(classification):,}자)")
        else:
            sess["status"] = "classifying"
            push_stage(sess, 2, "분류표 생성", 38)
            classification = step_classify(sess, features_text, project_name, focus_area)
            check_stop(sess)
            save_pipeline_state(project_name, "gate_waiting", {"raw_text": raw_text[:20000], "policy_text": policy_text, "features_text": features_text, "classification": classification, "focus_area": focus_area, "sources_info": _sources_info})

        # Human Gate
        push_stage(sess, 3, "분류표 검토 대기", 45)
        approved = step_gate(sess, classification)
        check_stop(sess)

        # TC 작성
        sess["status"] = "tc_writing"
        push_stage(sess, 4, "TC 작성 시작", 50)
        tc_content, total_tc, min_tc = step_write_tc(
            sess, approved, features_text, policy_text, project_name,
            selected_domain_codes=sess.get("selected_domains")
        )
        check_stop(sess)

        # TC 검토
        sess["status"] = "reviewing"
        push_stage(sess, 4, "TC 품질 검토", 82)
        step_review(sess, tc_content, project_name)
        check_stop(sess)

        # Excel 빌드
        sess["status"] = "building"
        push_stage(sess, 5, "Excel 빌드", 90)
        excel_path = step_build_excel(sess, tc_content, project_name, total_tc, min_tc)

        # TC 마크다운을 tc_files/에 저장 (수정 모드에서 재사용)
        today = datetime.now().strftime("%Y%m%d")
        safe_name = re.sub(r"[^\w\-_]", "_", project_name)[:30]
        tc_md_path = TC_FILES_DIR / f"{safe_name}_{today}.md"
        tc_md_path.write_text(tc_content, encoding="utf-8")
        save_project(project_name, str(tc_md_path), str(excel_path))
        clear_pipeline_state(project_name)  # 완료 시 상태 파일 정리
        push_log(sess, f"[저장] TC 파일 저장: {tc_md_path.name}")

        sess["result"] = excel_path
        sess["status"] = "done"
        push_stage(sess, 5, "완료", 100)
        push(sess, "done", {
            "filename":  excel_path.name,
            "size":      excel_path.stat().st_size,
            "sid":       sess["id"],
            "total_tc":  total_tc,
            "min_tc":    min_tc,
        })
        push_log(sess, f"[완료] Excel 파일 생성: {excel_path.name} ({excel_path.stat().st_size:,} bytes)")

        # 1시간 후 workspace 정리 (선택적)
        def cleanup():
            time.sleep(3600)
            import shutil
            ws = sess.get("workspace")
            if ws and Path(ws).exists():
                shutil.rmtree(ws, ignore_errors=True)
        threading.Thread(target=cleanup, daemon=True).start()

    except PipelineStopError:
        sess["status"] = "stopped"
        push_log(sess, "[중단] 사용자가 파이프라인을 중단했습니다.")
        push(sess, "stopped", {"msg": "파이프라인이 중단되었습니다.", "stage": sess.get("status", "")})

    except Exception as e:
        import traceback
        push_log(sess, f"[오류] {e}")
        push_log(sess, traceback.format_exc()[:1000])
        push_error(sess, str(e))


# ── 수정 파이프라인 ────────────────────────────────────────────────────────────
def run_modify_pipeline(sess: dict, project_name: str, existing_tc: str, change_desc: str, resume_stage: str = None):
    try:
        tc_rules = load_tc_rules()
        save_checkpoint(project_name, change_desc, "analyzing", {"existing_tc": existing_tc[:5000]})

        # Step M1: 영향도 분석
        sess["status"] = "analyzing"
        push_stage(sess, 2, "변경 영향 분석 중", 20)
        push_log(sess, "[영향 분석] 기존 TC와 변경사항을 비교 중...")

        tc_count_before = len(re.findall(r"^###\s", existing_tc, re.MULTILINE))

        system_impact = f"""당신은 QA 엔지니어입니다. 기존 TC 목록과 변경사항을 비교하여 영향받는 TC를 정확히 식별하세요.

TC 형식 규칙:
- bold heading (### **SC-XXX-YYY-NNN**) = 최소 TC
- plain heading (### SC-XXX-YYY-NNN) = 일반 TC

{tc_rules[:4000] if tc_rules else ""}"""

        user_impact = f"""## 기존 TC ({tc_count_before}개)

{existing_tc[:12000]}

## 변경사항

{change_desc}

위 변경사항을 분석하여 다음 형식으로 영향도를 출력하세요.
각 항목에 TC ID와 구체적인 이유를 반드시 포함하세요.

## 삭제할 TC
| TC ID | 삭제 이유 |
|-------|---------|
| SC-XXX-YYY-001 | 해당 기능이 제거됨 |

## 수정할 TC
| TC ID | 변경 내용 |
|-------|---------|
| SC-XXX-YYY-002 | When 단계에서 OTP 인증 추가 |

## 새로 추가할 TC
| 기능/시나리오 | TC 개수 (예상) |
|------------|------------|
| OTP 인증 실패 처리 | 3 |

## 영향 요약
- 삭제: N개
- 수정: N개
- 신규 추가: N개
- 변경 후 예상 TC 수: N개"""

        impact_analysis = call_claude(system_impact, user_impact, max_tokens=4096)
        check_stop(sess)

        impact_path = sess["workspace"] / "impact_analysis.md"
        impact_path.write_text(impact_analysis, encoding="utf-8")
        push_log(sess, f"[영향 분석] 완료 — 결과 {len(impact_analysis):,}자")
        save_checkpoint(project_name, change_desc, "gate_waiting", {"impact_analysis": impact_analysis, "existing_tc": existing_tc[:5000]})

        # Step M2: Human Gate (영향도 검토)
        push_stage(sess, 3, "영향도 검토 대기", 40)
        push_log(sess, "[GATE] 영향도 분석 결과를 검토해주세요.")
        sess["status"] = "gate_waiting"
        push(sess, "gate", {"content": impact_analysis, "mode": "modify"})
        sess["gate_event"].wait()
        approved_plan = sess["approved"]
        check_stop(sess)

        approved_path = sess["workspace"] / "impact_APPROVED.md"
        approved_path.write_text(approved_plan, encoding="utf-8")
        push_log(sess, "[GATE] 영향도 승인됨. TC 수정 시작.")

        # Step M3: TC 수정 적용
        sess["status"] = "tc_writing"
        push_stage(sess, 4, "TC 수정 적용 중", 55)
        push_log(sess, "[TC 수정] 승인된 계획에 따라 TC를 수정 중...")

        system_modify = f"""당신은 QA 엔지니어입니다. 기존 TC를 수정 계획에 따라 정확히 수정하세요.

TC 형식 규칙:
- bold heading (### **SC-XXX-YYY-NNN**) = 최소 TC (smoke test 대상)
- plain heading (### SC-XXX-YYY-NNN) = 일반 TC
- Given(사전 조건)은 번호 매긴 목록
- 전체 TC의 약 35%가 최소 TC여야 함

{tc_rules[:4000] if tc_rules else ""}"""

        user_modify = f"""## 수정 지시사항

{approved_plan}

## 변경 배경

{change_desc}

## 기존 TC 전체

{existing_tc[:15000]}

---

위 수정 계획을 정확히 적용하여 **수정된 TC 전체**를 출력하세요.
- 삭제 대상 TC는 완전히 제거
- 수정 대상 TC는 내용 업데이트 (TC ID 유지)
- 신규 TC는 기존 ID 체계에 맞춰 추가 (마지막 번호 이어서)
- 변경되지 않은 TC는 그대로 유지
- 기존 TC 형식(### heading, Given/When/Then)을 반드시 유지"""

        modified_tc = call_claude(system_modify, user_modify, max_tokens=16000)
        check_stop(sess)

        modified_path = sess["workspace"] / "tc_modified.md"
        modified_path.write_text(modified_tc, encoding="utf-8")

        total_tc = len(re.findall(r"^###\s", modified_tc, re.MULTILINE))
        min_tc   = max(1, round(total_tc * 0.35))
        push_log(sess, f"[TC 수정] 완료 — 총 {total_tc}개 TC (최소 TC: {min_tc}개)")

        # Step M4: TC 검토
        sess["status"] = "reviewing"
        push_stage(sess, 4, "TC 품질 검토", 80)
        step_review(sess, modified_tc, project_name)
        check_stop(sess)

        # Step M5: Excel 빌드
        sess["status"] = "building"
        push_stage(sess, 5, "Excel 빌드", 90)
        excel_path = step_build_excel(sess, modified_tc, project_name, total_tc, min_tc)

        # TC 파일 저장 (수정본으로 덮어쓰기)
        today = datetime.now().strftime("%Y%m%d")
        safe_name = re.sub(r"[^\w\-_]", "_", project_name)[:30]
        tc_md_path = TC_FILES_DIR / f"{safe_name}_{today}.md"
        tc_md_path.write_text(modified_tc, encoding="utf-8")
        save_project(project_name, str(tc_md_path), str(excel_path))

        sess["result"] = excel_path
        sess["status"] = "done"
        clear_checkpoint()
        push_stage(sess, 5, "완료", 100)
        push(sess, "done", {
            "filename":  excel_path.name,
            "size":      excel_path.stat().st_size,
            "sid":       sess["id"],
            "total_tc":  total_tc,
            "min_tc":    min_tc,
        })
        push_log(sess, f"[완료] 수정 Excel 저장: {excel_path.name}")

    except PipelineStopError:
        sess["status"] = "stopped"
        push_log(sess, "[중단] 사용자가 수정 파이프라인을 중단했습니다.")
        push(sess, "stopped", {"msg": "수정 파이프라인이 중단되었습니다."})

    except Exception as e:
        import traceback
        push_log(sess, f"[오류] {e}")
        push_log(sess, traceback.format_exc()[:1000])
        sess["status"] = "error"
        # 체크포인트가 있으면 복구 옵션 이벤트 발송
        cp = load_checkpoint()
        push(sess, "error_recovery", {
            "error": str(e),
            "has_checkpoint": bool(cp),
            "checkpoint_stage": cp.get("stage", ""),
            "checkpoint_project": cp.get("project_name", ""),
            "checkpoint_saved_at": cp.get("saved_at", ""),
        })
        push_error(sess, str(e))


# ── Flask 라우트 ───────────────────────────────────────────────────────────────

@app.route("/")
def index():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    api_warning = not api_key or api_key == "sk-ant-..."
    return render_template_string(HTML_TEMPLATE, api_warning=api_warning)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "파일 없음"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"ok": False, "error": "파일명 없음"}), 400
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"ok": False, "error": "PDF 파일만 허용"}), 400
    save_path = SPECS_DIR / f.filename
    f.save(str(save_path))
    return jsonify({"ok": True, "filename": f.filename})


@app.route("/upload-md", methods=["POST"])
def upload_md():
    """마크다운 파일 업로드"""
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "파일 없음"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"ok": False, "error": "파일명 없음"}), 400
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ("md", "markdown", "txt"):
        return jsonify({"ok": False, "error": ".md / .txt 파일만 허용"}), 400
    save_path = SPECS_DIR / f.filename
    f.save(str(save_path))
    return jsonify({"ok": True, "filename": f.filename})


@app.route("/start", methods=["POST"])
def start():
    data = request.get_json(force=True) or {}
    project_name = data.get("project_name", "프로젝트").strip() or "프로젝트"
    focus_area   = (data.get("focus_area") or "").strip()
    resume       = data.get("resume", False)  # 이어서 작업 여부

    # 이어서 작업 모드
    if resume:
        state = load_pipeline_state(project_name)
        if not state:
            return jsonify({"ok": False, "error": "저장된 작업 상태가 없습니다."}), 400
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY가 설정되지 않았습니다."}), 500
        sess = new_session()
        sess["project_name"] = project_name
        sess["focus_area"] = state["data"].get("focus_area", "")
        sess["_resumed_state"] = state
        # 이어서 작업 시 소스는 빈 배열 (이미 파싱 결과가 state에 있음)
        t = threading.Thread(
            target=run_pipeline,
            args=(sess, [], project_name),
            daemon=True
        )
        sess["thread"] = t
        t.start()
        return jsonify({"ok": True, "sid": sess["id"], "resumed_stage": state["stage"]})

    # 새 형식: sources 배열 / 구버전 호환: input_type + content
    sources = data.get("sources")
    if not sources:
        input_type = data.get("input_type", "text")
        content    = data.get("content", "").strip()
        sources    = [{"type": input_type, "content": content}]

    if not sources:
        return jsonify({"ok": False, "error": "소스가 없습니다."}), 400
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY가 설정되지 않았습니다."}), 500

    for src in sources:
        t = src.get("type", "text")
        c = src.get("content", "").strip()
        if not c:
            return jsonify({"ok": False, "error": f"{t} 소스의 내용이 비어 있습니다."}), 400
        if t not in ("pdf", "url", "web", "md", "text"):
            return jsonify({"ok": False, "error": f"소스 유형 오류: {t}"}), 400
        if t == "pdf" and not (SPECS_DIR / c).exists():
            return jsonify({"ok": False, "error": f"PDF 파일 없음: {c}"}), 400
        if t == "md" and not (SPECS_DIR / c).exists():
            return jsonify({"ok": False, "error": f"마크다운 파일 없음: {c}"}), 400

    sess = new_session()
    sess["project_name"] = project_name
    sess["focus_area"] = focus_area
    # 소스 정보를 프로젝트에 저장 (다음에 불러오기용)
    sources_to_save = []
    for src in sources:
        sources_to_save.append({
            "type": src.get("type", "text"),
            "content": src.get("content", ""),
            "selected_files": src.get("selected_files"),
        })
    save_project(project_name, last_sources=sources_to_save, last_focus_area=focus_area)
    t = threading.Thread(
        target=run_pipeline,
        args=(sess, sources, project_name),
        daemon=True
    )
    sess["thread"] = t
    t.start()
    return jsonify({"ok": True, "sid": sess["id"]})


@app.route("/projects/<name>/sources")
def get_project_sources(name):
    """프로젝트에 저장된 이전 소스 정보 반환"""
    projects = load_projects()
    proj = next((p for p in projects if p["name"] == name), None)
    if not proj:
        return jsonify({"ok": True, "has_sources": False})
    last_sources = proj.get("last_sources")
    last_focus = proj.get("last_focus_area", "")
    # last_sources가 없으면 pipeline_state에서 가져옴
    if not last_sources:
        state = load_pipeline_state(name)
        if state and state.get("data", {}).get("sources_info"):
            last_sources = state["data"]["sources_info"]
            last_focus = state["data"].get("focus_area", "")
    if not last_sources:
        return jsonify({"ok": True, "has_sources": False})
    return jsonify({
        "ok": True,
        "has_sources": True,
        "sources": last_sources,
        "focus_area": last_focus,
    })


@app.route("/projects/<name>/state")
def get_project_state(name):
    """프로젝트의 저장된 파이프라인 상태 조회"""
    state = load_pipeline_state(name)
    if not state:
        return jsonify({"ok": True, "has_state": False})
    return jsonify({
        "ok": True,
        "has_state": True,
        "stage": state["stage"],
        "saved_at": state["saved_at"],
        "focus_area": state["data"].get("focus_area", ""),
    })


@app.route("/stream/<sid>")
def stream(sid):
    sess = SESSIONS.get(sid)
    if not sess:
        return jsonify({"error": "세션 없음"}), 404

    def generate():
        while True:
            try:
                evt = sess["events"].get(timeout=30)
                payload = json.dumps(evt, ensure_ascii=False)
                yield f"data: {payload}\n\n"
                if evt["type"] in ("done", "error"):
                    break
            except queue.Empty:
                # heartbeat
                yield "data: {\"type\":\"ping\"}\n\n"
                # 세션이 완료/오류면 종료
                if sess["status"] in ("done", "error"):
                    break

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )


@app.route("/projects", methods=["GET"])
def list_projects():
    projects = load_projects()
    return jsonify(projects)


@app.route("/projects", methods=["POST"])
def create_project():
    """새 프로젝트 생성 (빈 TC로 등록)"""
    data = request.get_json(force=True) or {}
    project_name = data.get("name", "").strip()
    if not project_name:
        return jsonify({"ok": False, "error": "프로젝트명을 입력하세요."}), 400
    projects = load_projects()
    if any(p["name"] == project_name for p in projects):
        return jsonify({"ok": False, "error": "이미 존재하는 프로젝트명입니다."}), 400
    save_project(project_name, "", "")
    return jsonify({"ok": True, "project_name": project_name})


@app.route("/projects/<path:project_name>", methods=["DELETE"])
def delete_project(project_name):
    """프로젝트 삭제"""
    projects = load_projects()
    projects = [p for p in projects if p["name"] != project_name]
    PROJECTS_FILE.write_text(json.dumps(projects, ensure_ascii=False, indent=2), encoding="utf-8")
    return jsonify({"ok": True})


def excel_to_md(file_path: Path) -> str:
    """Excel TC 파일을 md 텍스트로 변환 (헤더 행 기준 자동 파싱)"""
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise RuntimeError("openpyxl 패키지가 필요합니다: pip install openpyxl")
    wb = load_workbook(str(file_path), data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        raise RuntimeError("Excel 파일이 비어 있습니다.")

    # 헤더 행 찾기 (TC ID 또는 ID 컬럼 포함)
    header_row, header_idx = None, 0
    for i, row in enumerate(rows):
        cells = [str(c).strip() if c else "" for c in row]
        if any(k in " ".join(cells) for k in ["TC ID", "tc_id", "ID", "제목", "Title"]):
            header_row = cells
            header_idx = i
            break
    if header_row is None:
        header_row = [str(c) if c else f"col{j}" for j, c in enumerate(rows[0])]

    lines = []
    for row in rows[header_idx + 1:]:
        if not any(c for c in row):
            continue
        vals = {header_row[j]: (str(row[j]).strip() if row[j] is not None else "") for j in range(min(len(header_row), len(row)))}
        tc_id    = vals.get("TC ID") or vals.get("ID") or vals.get("tc_id") or ""
        title    = vals.get("제목") or vals.get("Title") or vals.get("title") or ""
        major    = vals.get("대분류") or ""
        middle   = vals.get("중분류") or ""
        minor    = vals.get("소분류") or ""
        tc_type  = vals.get("분류") or vals.get("Type") or "Positive"
        priority = vals.get("우선순위") or vals.get("Priority") or "Medium"
        platform = vals.get("플랫폼") or vals.get("Platform") or ""
        screen   = vals.get("연관 화면") or vals.get("화면") or vals.get("Screen") or ""
        precond  = vals.get("사전 조건") or vals.get("Precondition") or vals.get("Given") or ""
        steps    = vals.get("테스트 단계") or vals.get("Steps") or vals.get("When") or ""
        expected = vals.get("예상 결과") or vals.get("Expected") or vals.get("Then") or ""
        note     = vals.get("비고") or vals.get("Note") or ""
        is_min   = vals.get("최소TC") or vals.get("최소 TC") or ""

        heading = f"### {'**' + tc_id + '**' if is_min and is_min.upper() == 'Y' else tc_id} — {title}"
        lines.append(heading)
        lines.append(f"\n| 항목 | 내용 |\n|------|------|")
        if major:    lines.append(f"| 대분류 | {major} |")
        if middle:   lines.append(f"| 중분류 | {middle} |")
        if minor:    lines.append(f"| 소분류 | {minor} |")
        lines.append(f"| 분류 | {tc_type} |")
        lines.append(f"| 우선순위 | {priority} |")
        if platform: lines.append(f"| 플랫폼 | {platform} |")
        if screen:   lines.append(f"| 연관 화면 | {screen} |")
        lines.append(f"\n**사전 조건**\n{precond}")
        lines.append(f"\n**테스트 단계**\n{steps}")
        lines.append(f"\n**예상 결과**\n{expected}")
        if note:     lines.append(f"\n**비고**\n{note}")
        lines.append("")
    return "\n".join(lines)


@app.route("/upload-tc", methods=["POST"])
def upload_tc():
    """TC 파일 업로드 — .md / .xlsx / .xls 지원"""
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "파일 없음"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"ok": False, "error": "파일명 없음"}), 400

    ext = Path(f.filename).suffix.lower()
    if ext not in (".md", ".xlsx", ".xls"):
        return jsonify({"ok": False, "error": ".md / .xlsx / .xls 파일만 허용"}), 400

    project_name = request.form.get("project_name", Path(f.filename).stem)
    safe_name = re.sub(r"[^\w\-_]", "_", project_name)[:30]
    today = datetime.now().strftime("%Y%m%d")

    if ext == ".md":
        save_path = TC_FILES_DIR / f"{safe_name}_{today}_upload.md"
        f.save(str(save_path))
    else:
        # Excel → 임시 저장 후 md 변환
        tmp_path = TC_FILES_DIR / f"{safe_name}_{today}_tmp{ext}"
        f.save(str(tmp_path))
        try:
            md_text = excel_to_md(tmp_path)
        except Exception as e:
            tmp_path.unlink(missing_ok=True)
            return jsonify({"ok": False, "error": f"Excel 변환 실패: {e}"}), 400
        tmp_path.unlink(missing_ok=True)
        save_path = TC_FILES_DIR / f"{safe_name}_{today}_upload.md"
        save_path.write_text(md_text, encoding="utf-8")

    save_project(project_name, str(save_path), "")
    return jsonify({"ok": True, "project_name": project_name, "tc_file": save_path.name})


@app.route("/import-sheets", methods=["POST"])
def import_sheets():
    """Google Sheets URL에서 TC 데이터를 가져와 md로 변환"""
    try:
        import requests as req_lib
    except ImportError:
        return jsonify({"ok": False, "error": "requests 패키지가 필요합니다"}), 500

    data = request.get_json(force=True) or {}
    url = data.get("url", "").strip()
    project_name = data.get("project_name", "").strip()

    if not url:
        return jsonify({"ok": False, "error": "URL을 입력하세요."}), 400
    if not project_name:
        return jsonify({"ok": False, "error": "프로젝트명을 입력하세요."}), 400

    # Google Sheets ID 추출 및 CSV export URL 생성
    sheets_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
    if not sheets_match:
        return jsonify({"ok": False, "error": "Google Sheets URL 형식이 올바르지 않습니다."}), 400

    sheet_id = sheets_match.group(1)
    # gid(시트 탭 ID) 추출
    gid_match = re.search(r"[#&?]gid=(\d+)", url)
    gid = gid_match.group(1) if gid_match else "0"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    try:
        resp = req_lib.get(csv_url, timeout=20)
        if resp.status_code == 403:
            return jsonify({"ok": False, "error": "Sheets 접근 권한이 없습니다. '링크가 있는 사용자 공개' 설정 필요"}), 403
        resp.raise_for_status()
        csv_text = resp.text
    except Exception as e:
        return jsonify({"ok": False, "error": f"Sheets 다운로드 실패: {e}"}), 400

    # CSV → md 변환
    import csv, io
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)
    if not rows:
        return jsonify({"ok": False, "error": "시트가 비어 있습니다."}), 400

    # 헤더 탐색
    header_row, header_idx = None, 0
    for i, row in enumerate(rows):
        if any(k in " ".join(row) for k in ["TC ID", "ID", "제목", "Title"]):
            header_row = row
            header_idx = i
            break
    if header_row is None:
        header_row = rows[0]

    lines = []
    for row in rows[header_idx + 1:]:
        if not any(c.strip() for c in row):
            continue
        vals = {header_row[j]: row[j].strip() if j < len(row) else "" for j in range(len(header_row))}
        tc_id    = vals.get("TC ID") or vals.get("ID") or ""
        title    = vals.get("제목") or vals.get("Title") or ""
        tc_type  = vals.get("분류") or vals.get("Type") or "Positive"
        priority = vals.get("우선순위") or vals.get("Priority") or "Medium"
        precond  = vals.get("사전 조건") or vals.get("Precondition") or ""
        steps    = vals.get("테스트 단계") or vals.get("Steps") or ""
        expected = vals.get("예상 결과") or vals.get("Expected") or ""
        is_min   = vals.get("최소TC") or vals.get("최소 TC") or ""
        heading  = f"### {'**' + tc_id + '**' if is_min.upper() == 'Y' else tc_id} — {title}"
        lines += [heading, f"\n| 항목 | 내용 |\n|------|------|",
                  f"| 분류 | {tc_type} |", f"| 우선순위 | {priority} |",
                  f"\n**사전 조건**\n{precond}", f"\n**테스트 단계**\n{steps}",
                  f"\n**예상 결과**\n{expected}", ""]

    md_text = "\n".join(lines)
    safe_name = re.sub(r"[^\w\-_]", "_", project_name)[:30]
    today = datetime.now().strftime("%Y%m%d")
    save_path = TC_FILES_DIR / f"{safe_name}_{today}_sheets.md"
    save_path.write_text(md_text, encoding="utf-8")
    save_project(project_name, str(save_path), "")
    return jsonify({"ok": True, "project_name": project_name, "tc_file": save_path.name, "tc_count": len(lines) // 8})


@app.route("/start-modify", methods=["POST"])
def start_modify():
    data = request.get_json(force=True) or {}
    project_name  = data.get("project_name", "").strip()
    change_desc   = data.get("change_desc", "").strip()

    if not project_name:
        return jsonify({"ok": False, "error": "프로젝트명이 없습니다."}), 400
    if not change_desc:
        return jsonify({"ok": False, "error": "변경사항 내용이 없습니다."}), 400
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY가 설정되지 않았습니다."}), 500

    # 기존 TC 파일 로드
    projects = load_projects()
    proj = next((p for p in projects if p["name"] == project_name), None)
    if not proj or not Path(proj["tc_file"]).exists():
        return jsonify({"ok": False, "error": f"'{project_name}' 프로젝트의 TC 파일을 찾을 수 없습니다."}), 404

    existing_tc = Path(proj["tc_file"]).read_text(encoding="utf-8")

    sess = new_session()
    sess["project_name"] = project_name
    sess["mode"] = "modify"
    t = threading.Thread(
        target=run_modify_pipeline,
        args=(sess, project_name, existing_tc, change_desc),
        daemon=True
    )
    sess["thread"] = t
    t.start()
    return jsonify({"ok": True, "sid": sess["id"]})


@app.route("/checkpoint", methods=["GET"])
def get_checkpoint():
    cp = load_checkpoint()
    return jsonify({"ok": True, "checkpoint": cp})

@app.route("/checkpoint", methods=["DELETE"])
def del_checkpoint():
    clear_checkpoint()
    return jsonify({"ok": True})

@app.route("/restart-modify", methods=["POST"])
def restart_modify():
    """체크포인트 기반 재시작 또는 처음부터 재시작"""
    data = request.get_json(force=True) or {}
    mode = data.get("mode", "fresh")  # "resume" | "fresh"

    cp = load_checkpoint()
    if mode == "resume" and not cp:
        return jsonify({"ok": False, "error": "저장된 체크포인트가 없습니다."}), 400

    project_name = cp.get("project_name") if mode == "resume" else data.get("project_name", "")
    change_desc  = cp.get("change_desc")  if mode == "resume" else data.get("change_desc", "")

    if not project_name:
        return jsonify({"ok": False, "error": "프로젝트명이 없습니다."}), 400

    projects = load_projects()
    proj = next((p for p in projects if p["name"] == project_name), None)
    if not proj or not proj.get("tc_file") or not Path(proj["tc_file"]).exists():
        return jsonify({"ok": False, "error": f"'{project_name}' TC 파일을 찾을 수 없습니다."}), 404

    existing_tc = Path(proj["tc_file"]).read_text(encoding="utf-8")
    sess = new_session()
    sess["project_name"] = project_name
    sess["mode"] = "modify"
    resume_stage = cp.get("stage") if mode == "resume" else None
    t = threading.Thread(
        target=run_modify_pipeline,
        args=(sess, project_name, existing_tc, change_desc, resume_stage),
        daemon=True
    )
    sess["thread"] = t
    t.start()
    return jsonify({"ok": True, "sid": sess["id"], "mode": mode})


@app.route("/stop/<sid>", methods=["POST"])
def stop_pipeline(sid):
    sess = SESSIONS.get(sid)
    if not sess:
        return jsonify({"ok": False, "error": "세션 없음"}), 404
    sess["stop_requested"] = True
    # Human Gate에서 대기 중이면 즉시 해제 후 중단
    if sess["status"] == "gate_waiting":
        sess["approved"] = ""
        sess["gate_event"].set()
    return jsonify({"ok": True})


@app.route("/regenerate-classification", methods=["POST"])
def regenerate_classification():
    """분류표 재생성 — 정책/기능 목록은 유지하고 분류표부터 다시 생성"""
    data = request.get_json(force=True) or {}
    project_name = (data.get("project_name") or "").strip() or "프로젝트"
    focus_area   = (data.get("focus_area") or "").strip()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY가 설정되지 않았습니다."}), 500

    # 저장된 파이프라인 상태에서 이전 결과 로드
    state = load_pipeline_state(project_name)
    if not state or not state["data"].get("features_text"):
        return jsonify({"ok": False, "error": "이전 분석 결과가 없습니다. 처음부터 시작해주세요."}), 400

    sess = new_session()
    sess["project_name"] = project_name
    sess["focus_area"] = focus_area
    # 분류표 직전 단계(features)에서 재시작하도록 상태 설정
    sess["_resumed_state"] = {
        "stage": "features",
        "data": {
            "raw_text": state["data"].get("raw_text", ""),
            "policy_text": state["data"].get("policy_text", ""),
            "features_text": state["data"].get("features_text", ""),
            "focus_area": focus_area,
        }
    }
    t = threading.Thread(
        target=run_pipeline,
        args=(sess, [], project_name),
        daemon=True
    )
    sess["thread"] = t
    t.start()
    return jsonify({"ok": True, "sid": sess["id"]})


@app.route("/approve/<sid>", methods=["POST"])
def approve(sid):
    sess = SESSIONS.get(sid)
    if not sess:
        return jsonify({"ok": False, "error": "세션 없음"}), 404
    data = request.get_json(force=True) or {}
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"ok": False, "error": "승인할 내용이 없습니다."}), 400
    # 선택된 도메인 코드 저장 (None이면 전체 생성)
    selected = data.get("selected_domains")  # list of codes or null
    sess["selected_domains"] = selected if selected else None
    # SuiteCode 저장 (검토자가 Human Gate에서 입력)
    suite_codes = data.get("suite_codes")  # list of codes
    sess["suite_codes"] = suite_codes if suite_codes else []
    sess["approved"] = content
    sess["gate_event"].set()
    return jsonify({"ok": True})


@app.route("/gate-chat/<sid>", methods=["POST"])
def gate_chat(sid):
    """Human Gate 채팅 — AI와 대화하며 분류표/영향도 문서를 수정"""
    import anthropic
    sess = SESSIONS.get(sid)
    if not sess:
        return jsonify({"ok": False, "error": "세션 없음"}), 404
    if sess.get("status") != "gate_waiting":
        return jsonify({"ok": False, "error": "Gate 대기 상태가 아닙니다."}), 400

    data = request.get_json(force=True) or {}
    user_msg = data.get("message", "").strip()
    current_doc = data.get("current_doc", "").strip()
    gate_mode = data.get("gate_mode", "new")   # "new" | "modify"
    history = data.get("history", [])           # [{role, content}, ...]

    if not user_msg:
        return jsonify({"ok": False, "error": "메시지를 입력해주세요."}), 400

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY 미설정"}), 500

    client = anthropic.Anthropic(api_key=api_key)

    if gate_mode == "modify":
        system_prompt = """당신은 TC(Test Case) 수정 전문가입니다.
현재 AI가 생성한 '변경 영향도 분석' 문서를 사용자의 요청에 따라 수정합니다.

규칙:
- 사용자의 수정 요청을 정확히 반영하여 문서를 업데이트하세요.
- 응답은 반드시 두 부분으로 구성하세요:
  1. [REPLY] 태그: 수정 내용에 대한 간단한 설명 (1-3문장)
  2. [DOCUMENT] 태그: 수정된 전체 문서 내용 (마크다운 형식 유지)
- 수정 요청이 없거나 질문인 경우, [DOCUMENT] 태그에는 기존 문서를 그대로 포함하세요.
- 문서 형식(마크다운, 헤딩, 목록 등)을 유지하세요."""
    else:
        system_prompt = """당신은 TC(Test Case) 분류 전문가입니다.
현재 AI가 생성한 '분류표' 문서를 사용자의 요청에 따라 수정합니다.

규칙:
- 사용자의 수정 요청을 정확히 반영하여 분류표를 업데이트하세요.
- 응답은 반드시 두 부분으로 구성하세요:
  1. [REPLY] 태그: 수정 내용에 대한 간단한 설명 (1-3문장)
  2. [DOCUMENT] 태그: 수정된 전체 문서 내용 (마크다운 형식 유지)
- 수정 요청이 없거나 질문인 경우, [DOCUMENT] 태그에는 기존 문서를 그대로 포함하세요.
- 분류표 형식(## 대분류, ### 중분류, TC ID 패턴 등)을 유지하세요."""

    # 메시지 구성 — 히스토리 + 현재 문서 컨텍스트 + 사용자 메시지
    messages = []
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})

    # 현재 문서를 컨텍스트로 포함
    full_user_msg = f"""현재 문서:\n```\n{current_doc}\n```\n\n사용자 요청: {user_msg}"""
    messages.append({"role": "user", "content": full_user_msg})

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            temperature=0,
            system=system_prompt,
            messages=messages
        )
        ai_text = resp.content[0].text

        # [REPLY]와 [DOCUMENT] 파싱
        reply_text = ""
        updated_doc = current_doc  # 기본값: 변경 없음

        reply_match = re.search(r'\[REPLY\](.*?)(?=\[DOCUMENT\]|$)', ai_text, re.DOTALL)
        doc_match   = re.search(r'\[DOCUMENT\](.*?)$', ai_text, re.DOTALL)

        if reply_match:
            reply_text = reply_match.group(1).strip()
        if doc_match:
            updated_doc = doc_match.group(1).strip()
            # 코드블록 래핑 제거
            if updated_doc.startswith("```"):
                lines = updated_doc.split("\n")
                updated_doc = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()

        if not reply_text:
            reply_text = ai_text.strip()

        return jsonify({
            "ok": True,
            "reply": reply_text,
            "updated_doc": updated_doc
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/export-gate", methods=["POST"])
def export_gate():
    """Human Gate 분류표를 Excel로 내보내기 (범위 선택 포함)"""
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    data = request.get_json() or {}
    content = data.get("content", "")
    mode    = data.get("mode", "new")   # "new" | "modify"
    domains = extract_domains(content)

    wb = Workbook()

    # ── Sheet 1: 범위 선택 ─────────────────────────────────────────────────────
    ws1 = wb.active
    ws1.title = "TC 생성 범위 선택"
    ws1.sheet_view.showGridLines = False

    NAVY  = "1E2761"; TEAL  = "028090"; LIGHT = "EBF5FB"; YELLOW = "FFF9C4"
    def hfont(bold=True, color="FFFFFF", size=10):
        return Font(name="Calibri", bold=bold, color=color, size=size)
    def fill(c): return PatternFill("solid", fgColor=c)
    def center(): return Alignment(horizontal="center", vertical="center", wrap_text=True)
    def left(): return Alignment(horizontal="left", vertical="center", wrap_text=True)
    def bdr():
        s = Side(style="thin", color="CCCCCC")
        return Border(left=s, right=s, top=s, bottom=s)

    headers = ["도메인 코드", "도메인명", "TC 생성 포함 (Y/N)", "비고"]
    col_w   = [16, 30, 20, 40]
    for ci, (h, w) in enumerate(zip(headers, col_w), 1):
        c = ws1.cell(1, ci, h)
        c.font = hfont(); c.fill = fill(NAVY); c.alignment = center(); c.border = bdr()
        ws1.column_dimensions[get_column_letter(ci)].width = w
    ws1.row_dimensions[1].height = 28

    # 안내 메모 행
    ws1.merge_cells("A2:D2")
    note = ws1["A2"]
    msg = "TC 생성 포함 열에 Y(포함) 또는 N(제외)를 입력하세요. 기본값은 Y(전체 생성)입니다."
    if mode == "modify":
        msg = "수정 영향도 분석 결과입니다. 실제 TC를 수정할 범위에 Y를 표시하세요."
    note.value = msg
    note.font = Font(name="Calibri", size=9, italic=True, color="555555")
    note.alignment = left()
    note.fill = fill("FFF3CD")
    ws1.row_dimensions[2].height = 20

    for ri, d in enumerate(domains, 3):
        ws1.cell(ri, 1, d["code"]).alignment = center()
        ws1.cell(ri, 2, d["name"]).alignment = left()
        c = ws1.cell(ri, 3, "Y")
        c.alignment = center()
        c.fill = fill(YELLOW)
        c.font = Font(name="Calibri", bold=True, color="1E6F50")
        ws1.cell(ri, 4, "").alignment = left()
        for ci in range(1, 5):
            ws1.cell(ri, ci).border = bdr()
        ws1.row_dimensions[ri].height = 22

    # ── Sheet 2: 원문 (분류표 마크다운) ───────────────────────────────────────
    ws2 = wb.create_sheet("분류표 원문")
    ws2.sheet_view.showGridLines = False
    ws2.column_dimensions["A"].width = 120
    title_cell = ws2["A1"]
    title_cell.value = "분류표 / 영향도 분석 원문"
    title_cell.font = hfont(size=12)
    title_cell.fill = fill(TEAL)
    title_cell.alignment = left()
    ws2.row_dimensions[1].height = 26

    for ri, line in enumerate(content.splitlines(), 2):
        c = ws2.cell(ri, 1, line)
        c.font = Font(name="Consolas", size=9)
        c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=False)
        ws2.row_dimensions[ri].height = 15

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    fname = "gate_review.xlsx"
    return Response(
        buf.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={fname}"}
    )


# ── Google Drive 헬퍼 ─────────────────────────────────────────────────────────
def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return {}


def get_drive_service():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    if not DRIVE_CREDS_FILE.exists():
        raise FileNotFoundError(
            "credentials.json이 없습니다.\n"
            "Google Cloud Console → API 및 서비스 → 사용자 인증 정보 →\n"
            "OAuth 2.0 클라이언트 ID (데스크톱 앱)를 만들고\n"
            f"다운로드한 파일을 '{DRIVE_CREDS_FILE}' 으로 저장하세요."
        )
    creds = None
    if DRIVE_TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(DRIVE_TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(DRIVE_CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        DRIVE_TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return build("drive", "v3", credentials=creds)


@app.route("/open-folder", methods=["POST"])
def open_folder():
    import subprocess as _sp
    import platform
    folder = str(OUTPUTS_DIR)
    if platform.system() == "Windows":
        _sp.Popen(["explorer", folder])
    elif platform.system() == "Darwin":
        _sp.Popen(["open", folder])
    else:
        _sp.Popen(["xdg-open", folder])
    return jsonify({"ok": True})


@app.route("/upload-to-drive", methods=["POST"])
def upload_to_drive():
    data = request.get_json() or {}
    filename = data.get("filename", "")
    sid = data.get("sid", "")

    # 세션에서 결과 파일 경로 확인, 없으면 outputs 폴더에서 탐색
    file_path = None
    sess = SESSIONS.get(sid)
    if sess and sess.get("result") and Path(sess["result"]).exists():
        file_path = Path(sess["result"])
    else:
        candidate = (OUTPUTS_DIR / filename).resolve()
        if str(candidate).startswith(str(OUTPUTS_DIR.resolve())) and candidate.exists():
            file_path = candidate

    if not file_path:
        return jsonify({"ok": False, "error": "파일을 찾을 수 없습니다."})

    config = load_config()
    folder_id = config.get("google_drive", {}).get("upload_folder_id")
    if not folder_id:
        return jsonify({"ok": False, "error": "config.json에 google_drive.upload_folder_id가 없습니다."})

    try:
        from googleapiclient.http import MediaFileUpload
        service = get_drive_service()
        file_metadata = {"name": filename, "parents": [folder_id]}
        media = MediaFileUpload(
            str(file_path),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        uploaded = service.files().create(
            body=file_metadata, media_body=media, fields="id,webViewLink"
        ).execute()
        folder_url = config.get("google_drive", {}).get("folder_url", "")
        return jsonify({
            "ok": True,
            "file_id": uploaded.get("id"),
            "link": folder_url or uploaded.get("webViewLink"),
        })
    except FileNotFoundError as e:
        return jsonify({"ok": False, "error": str(e), "need_credentials": True})
    except Exception as e:
        err_str = str(e)
        # OAuth 권한 부족 또는 Drive API 미활성화
        if any(k in err_str for k in ["insufficient_scope", "accessNotConfigured",
                                       "forbidden", "403", "Request had insufficient"]):
            return jsonify({"ok": False, "error": "Google Drive 접근 권한이 없습니다. Drive API가 활성화된 계정인지 확인해주세요.", "need_credentials": True})
        return jsonify({"ok": False, "error": err_str})


@app.route("/download/<sid>/<filename>")
def download(sid, filename):
    sess = SESSIONS.get(sid)
    if not sess:
        return jsonify({"error": "세션 없음"}), 404
    result = sess.get("result")
    if not result or not Path(result).exists():
        # outputs 폴더에서 파일명으로 검색
        fpath = OUTPUTS_DIR / filename
        if not fpath.exists():
            return jsonify({"error": "파일 없음"}), 404
        result = fpath
    return send_file(str(result), as_attachment=True, download_name=filename)


@app.route("/sample-download")
def sample_download():
    """샘플 기획서 PDF 다운로드 (없으면 즉석 생성)"""
    pdf_path = build_sample_pdf()
    if pdf_path is None or not pdf_path.exists():
        return jsonify({"error": "PDF 생성 실패. fpdf2 패키지 설치 여부를 확인하세요."}), 500
    return send_file(
        str(pdf_path),
        as_attachment=True,
        download_name=SAMPLE_PDF_FILENAME,
        mimetype="application/pdf",
    )


@app.route("/sample-content")
def sample_content():
    """샘플 기획서 텍스트 반환 (JS에서 직접 채우기용)"""
    return jsonify({"content": SAMPLE_DOC_CONTENT, "filename": SAMPLE_PDF_FILENAME})


@app.route("/github-tree", methods=["POST"])
def github_tree():
    """GitHub 리포지토리 파일 트리를 반환 (파일 선택 미리보기용)"""
    try:
        import requests as req_lib
    except ImportError:
        return jsonify({"ok": False, "error": "requests 패키지가 필요합니다"})

    data = request.get_json(force=True)
    url = (data.get("url") or "").strip()

    gh_match = re.match(r"https?://github\.com/([^/]+)/([^/\s]+?)(?:\.git)?/?$", url)
    if not gh_match:
        return jsonify({"ok": False, "error": "GitHub 리포지토리 URL이 아닙니다"})

    owner, repo = gh_match.group(1), gh_match.group(2)
    headers = {"User-Agent": "TC-Automation/2.0"}
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"token {token}"

    # 기본 브랜치 확인
    branch = "main"
    try:
        r = req_lib.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=10)
        if r.status_code == 200:
            branch = r.json().get("default_branch", "main")
        elif r.status_code == 404:
            return jsonify({"ok": False, "error": f"리포지토리를 찾을 수 없습니다: {owner}/{repo} (private이면 GITHUB_TOKEN 필요)"})
        elif r.status_code == 401:
            return jsonify({"ok": False, "error": "GitHub 인증 실패: GITHUB_TOKEN을 확인해주세요"})
    except Exception as e:
        return jsonify({"ok": False, "error": f"GitHub API 오류: {e}"})

    # 파일 트리 가져오기
    try:
        r = req_lib.get(f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1", headers=headers, timeout=15)
        if r.status_code != 200:
            return jsonify({"ok": False, "error": f"파일 트리 로드 실패 (status {r.status_code})"})
        tree = r.json().get("tree", [])
    except Exception as e:
        return jsonify({"ok": False, "error": f"파일 트리 오류: {e}"})

    # 파일 목록 (blob만, 디렉토리 제외)
    files = [
        {"path": f["path"], "size": f.get("size", 0)}
        for f in tree
        if f["type"] == "blob"
    ]

    return jsonify({"ok": True, "owner": owner, "repo": repo, "branch": branch, "files": files})


@app.route("/shutdown", methods=["POST"])
def shutdown():
    func = request.environ.get("werkzeug.server.shutdown")
    if func:
        func()
    else:
        os._exit(0)
    return jsonify({"ok": True})


# ── HTML 템플릿 ────────────────────────────────────────────────────────────────
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TC 자동화 v2</title>
<style>
  :root {
    --bg: #EEF1F8;
    --navy: #1E2761;
    --blue: #3557A0;
    --teal: #028090;
    --white: #FFFFFF;
    --text: #222222;
    --muted: #6B7A99;
    --border: #D0D7DE;
    --success: #1C6E38;
    --warn: #B45309;
    --danger: #B91C1C;
    --radius: 12px;
    --shadow: 0 2px 12px rgba(30,39,97,0.10);
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; }

  /* 경고 배너 */
  .api-warning {
    background: #FEF3C7; border-bottom: 2px solid #D97706;
    color: #92400E; padding: 10px 24px; font-size: 14px; text-align: center;
    font-weight: 500;
  }

  /* 헤더 */
  header {
    background: var(--navy); color: var(--white);
    padding: 20px 32px; display: flex; align-items: center; gap: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.18);
  }
  header > div { display: flex; flex-direction: column; gap: 2px; }
  header h1 { font-size: 22px; font-weight: 700; letter-spacing: -0.3px; }
  header .header-sub { font-size: 13px; opacity: 0.7; margin-left: auto; }
  .version-badge { font-size: 11px; font-weight: 600; color: #FF8C00; letter-spacing: 0.3px; }

  /* 진행 스텝 바 */
  .steps-bar {
    background: var(--white); border-bottom: 1px solid var(--border);
    padding: 14px 32px; display: flex; gap: 0; overflow-x: auto;
  }
  .step-item {
    display: flex; align-items: center; gap: 8px;
    font-size: 13px; color: var(--muted); white-space: nowrap; flex: 1;
  }
  .step-item.active { color: var(--blue); font-weight: 600; }
  .step-item.done   { color: var(--success); }
  .step-num {
    width: 26px; height: 26px; border-radius: 50%;
    background: var(--border); color: var(--muted);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; flex-shrink: 0;
  }
  .step-item.active .step-num { background: var(--blue); color: var(--white); }
  .step-item.done   .step-num { background: var(--success); color: var(--white); }
  .step-arrow { color: var(--border); margin: 0 4px; font-size: 16px; }

  /* 메인 */
  main { max-width: 860px; margin: 32px auto; padding: 0 20px 60px; }

  /* 카드 */
  .card {
    background: var(--white); border-radius: var(--radius);
    box-shadow: var(--shadow); padding: 28px 32px; margin-bottom: 20px;
  }
  .card-title {
    font-size: 17px; font-weight: 700; color: var(--navy);
    margin-bottom: 18px; display: flex; align-items: center; gap: 8px;
  }
  .card-title .badge {
    font-size: 11px; font-weight: 600; padding: 2px 8px;
    border-radius: 99px; background: var(--bg); color: var(--muted);
  }

  /* 폼 */
  .form-label { font-size: 13px; font-weight: 600; color: var(--navy); margin-bottom: 6px; display: block; }
  .form-input {
    width: 100%; padding: 10px 14px; border: 1.5px solid var(--border);
    border-radius: 8px; font-size: 14px; color: var(--text); background: var(--bg);
    transition: border-color 0.15s;
  }
  .form-input:focus { outline: none; border-color: var(--blue); background: var(--white); }
  textarea.form-input { resize: vertical; min-height: 120px; }
  .form-group { margin-bottom: 16px; }

  /* 프로젝트 드롭다운 */
  .project-select-row {
    display: flex; gap: 8px; align-items: center; margin-bottom: 16px;
  }
  .project-select-row label {
    font-size: 13px; font-weight: 600; color: var(--navy); white-space: nowrap;
  }
  .project-dropdown {
    flex: 1; padding: 8px 12px; border: 1.5px solid var(--border);
    border-radius: 8px; font-size: 13px; color: var(--text);
    background: #fff; cursor: pointer; appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23666'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 12px center;
    padding-right: 30px;
  }
  .project-dropdown:focus { border-color: var(--blue); outline: none; }
  .btn-new-project {
    padding: 7px 14px; background: var(--teal); color: #fff;
    border: none; border-radius: 8px; font-size: 12px; font-weight: 600;
    cursor: pointer; white-space: nowrap;
  }
  .btn-new-project:hover { background: #026D75; }
  .project-new-inline {
    display: none; gap: 8px; align-items: center; margin-bottom: 12px;
  }
  .project-new-inline input {
    flex: 1; padding: 7px 10px; border: 1.5px solid var(--border);
    border-radius: 8px; font-size: 13px;
  }
  .project-new-inline input:focus { border-color: var(--blue); outline: none; }
  .project-resume-bar {
    padding: 10px 12px; margin-bottom: 16px;
    border: 1.5px solid #60A5FA; border-radius: 8px;
    background: #EFF6FF; display: none; align-items: center; gap: 10px;
    font-size: 12px; color: #1E40AF;
  }
  .project-resume-bar strong { font-weight: 700; }
  .btn-resume-pipeline {
    padding: 5px 14px; background: #2563EB; color: #fff; border: none;
    border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;
    white-space: nowrap;
  }
  .btn-resume-pipeline:hover { background: #1D4ED8; }
  .pj-status-tag {
    font-size: 10px; padding: 1px 6px; border-radius: 8px;
    font-weight: 600; margin-left: 4px; vertical-align: middle;
  }
  .pj-status-tag.in-progress { background: #FEF3C7; color: #92400E; }
  .pj-status-tag.completed { background: #D1FAE5; color: #065F46; }
  .pj-status-tag.sample { background: #E5E7EB; color: #6B7280; }

  /* 모드 스위처 */
  .mode-switcher {
    display: flex; background: var(--bg); border-radius: 10px;
    padding: 4px; gap: 4px; margin-bottom: 20px;
  }
  .mode-btn {
    flex: 1; padding: 10px 16px; border: none; border-radius: 8px;
    font-size: 14px; font-weight: 600; cursor: pointer;
    background: none; color: var(--muted); transition: all 0.2s;
  }
  .mode-btn.active {
    background: var(--white); color: var(--navy);
    box-shadow: 0 1px 4px rgba(0,0,0,.12);
  }

  /* 입력 유형 탭 버튼 */
  .radio-group { display: flex; gap: 10px; flex-wrap: wrap; }
  .type-btn {
    display: flex; align-items: center; gap: 6px; cursor: pointer;
    padding: 8px 16px; border: 1.5px solid var(--border); border-radius: 8px;
    font-size: 13px; font-weight: 500; transition: all 0.15s;
    background: var(--white); color: var(--text);
  }
  .type-btn:hover { border-color: var(--blue); color: var(--blue); }
  .type-btn.active { border-color: var(--blue); background: #EBF2FF; color: var(--blue); }

  /* 프로젝트 선택 드롭다운 */
  .project-select {
    width: 100%; padding: 11px 14px; border: 1.5px solid var(--border);
    border-radius: 8px; font-size: 14px; color: var(--text);
    background: var(--bg); cursor: pointer; appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23888' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
    background-repeat: no-repeat; background-position: right 14px center;
  }
  .project-select:focus { outline: none; border-color: var(--blue); }

  /* 프로젝트 카드 (선택된 프로젝트 정보) */
  .project-card {
    background: #F0FBF8; border: 1.5px solid #B2E8DC; border-radius: 10px;
    padding: 14px 16px; margin-top: 10px; display: none;
  }
  .project-card.visible { display: block; }
  .project-card-name { font-size: 15px; font-weight: 700; color: var(--navy); }
  .project-card-meta { font-size: 12px; color: var(--muted); margin-top: 3px; }

  /* TC 파일 업로드 영역 */
  .tc-upload-area {
    border: 2px dashed #B2E8DC; border-radius: 10px; padding: 20px;
    text-align: center; cursor: pointer; color: var(--muted); font-size: 13px;
    transition: all 0.2s; margin-top: 10px;
  }
  .tc-upload-area:hover { border-color: var(--teal); color: var(--teal); }

  /* 직접 입력 textarea */
  .text-input-area {
    min-height: 260px; resize: vertical; font-family: inherit;
    line-height: 1.7; font-size: 14px;
  }
  .input-hint {
    font-size: 12px; color: var(--muted); margin-top: 6px;
  }

  /* 드롭존 */
  .dropzone {
    border: 2px dashed var(--border); border-radius: 10px;
    padding: 32px; text-align: center; cursor: pointer;
    transition: all 0.2s; color: var(--muted); font-size: 14px;
  }
  .dropzone:hover, .dropzone.drag-over { border-color: var(--blue); background: #EBF2FF; color: var(--blue); }
  .dropzone .icon { font-size: 36px; margin-bottom: 8px; }
  .dropzone .hint { font-size: 12px; margin-top: 4px; }
  #fileInput { display: none; }

  /* 버튼 */
  .btn {
    padding: 11px 24px; border-radius: 8px; font-size: 14px; font-weight: 600;
    cursor: pointer; border: none; transition: all 0.15s; display: inline-flex;
    align-items: center; gap: 8px;
  }
  .btn-primary { background: var(--blue); color: var(--white); }
  .btn-primary:hover { background: var(--navy); }
  .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-success { background: var(--success); color: var(--white); }
  .btn-success:hover { background: #155228; }
  .btn-teal { background: var(--teal); color: var(--white); }
  .btn-teal:hover { background: #016070; }
  .btn-stop {
    background: none; color: #e53e3e; border: 1.5px solid #e53e3e;
    padding: 7px 18px; border-radius: 8px; font-size: 13px; font-weight: 600;
    cursor: pointer; transition: all 0.15s; display: inline-flex; align-items: center; gap: 6px;
  }
  .btn-stop:hover { background: #fff5f5; }
  .btn-stop:disabled { opacity: 0.4; cursor: not-allowed; }

  /* 중단 배너 */
  .stopped-banner {
    background: #FFF5F5; border: 1.5px solid #FEB2B2; border-radius: 10px;
    padding: 18px 22px; margin-top: 16px; display: flex; align-items: center; gap: 12px;
  }
  .stopped-banner .stopped-icon { font-size: 28px; flex-shrink: 0; }
  .stopped-banner .stopped-msg  { font-size: 14px; font-weight: 600; color: #c53030; }
  .stopped-banner .stopped-sub  { font-size: 12px; color: #888; margin-top: 2px; }

  /* 다중 소스 입력 */
  .source-add-bar { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
  .btn-add-source {
    padding: 7px 14px; border-radius: 8px; font-size: 12px; font-weight: 600;
    background: var(--white); color: var(--text); border: 1.5px solid var(--border);
    cursor: pointer; transition: all 0.15s;
  }
  .btn-add-source:hover { border-color: var(--blue); color: var(--blue); background: #EBF2FF; }
  .source-card {
    border: 1.5px solid var(--border); border-radius: 10px;
    margin-bottom: 10px; overflow: hidden; background: var(--white);
  }
  .source-card-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 12px; background: var(--bg); border-bottom: 1px solid var(--border);
  }
  .source-type-badge {
    font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 12px;
  }
  .source-type-badge.pdf  { background: #FEE2E2; color: #C53030; }
  .source-type-badge.url  { background: #EBF2FF; color: var(--blue); }
  .source-type-badge.text { background: #D1FAE5; color: #276749; }
  .btn-remove-source {
    background: none; border: none; cursor: pointer; font-size: 14px;
    color: var(--muted); padding: 2px 8px; border-radius: 4px;
  }
  .btn-remove-source:hover { background: #FEE2E2; color: #C53030; }
  .source-card-body { padding: 12px; }
  .src-dropzone {
    border: 2px dashed var(--border); border-radius: 8px; padding: 18px;
    text-align: center; cursor: pointer; font-size: 13px; color: var(--muted);
    transition: all 0.15s;
  }
  .src-dropzone:hover { border-color: var(--blue); color: var(--blue); }
  .src-file-name { font-size: 13px; font-weight: 600; color: var(--success); padding: 4px 0; }
  .source-empty {
    border: 2px dashed var(--border); border-radius: 10px; padding: 28px 16px;
    text-align: center; font-size: 13px; color: var(--muted); line-height: 1.8;
  }

  /* TC 가져오기 탭 */
  .tc-import-tabs { display: flex; gap: 4px; margin-bottom: 10px; }
  .tc-import-tab { flex: 1; padding: 7px; font-size: 12px; font-weight: 600; border: 1px solid var(--border); border-radius: 6px; background: var(--surface); cursor: pointer; color: var(--muted); }
  .tc-import-tab.active { background: var(--navy); color: #fff; border-color: var(--navy); }

  /* 새 프로젝트 생성 */
  .btn-new-project { font-size: 11px; padding: 3px 10px; border: 1px solid var(--teal); color: var(--teal); background: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
  .btn-new-project:hover { background: var(--teal); color: #fff; }
  .new-project-form { margin-top: 10px; padding: 12px; background: var(--surface); border: 1px solid var(--border); border-radius: 8px; }
  .btn-delete-project { margin-top: 6px; font-size: 11px; padding: 2px 8px; border: 1px solid #e53e3e; color: #e53e3e; background: none; border-radius: 6px; cursor: pointer; }
  .btn-delete-project:hover { background: #e53e3e; color: #fff; }

  /* 샘플 기획서 푸터 */
  .sample-footer { display: flex; align-items: center; gap: 10px; padding: 10px 32px; background: var(--surface); border-top: 1px solid var(--border); font-size: 12px; color: var(--muted); }
  .sample-footer-label { color: var(--muted); }

  /* 샘플 기획서 배너 (구) */
  .sample-banner {
    display: flex; align-items: center; justify-content: space-between; gap: 14px;
    background: linear-gradient(135deg, #F0FFF4, #EBF2FF);
    border: 1.5px solid #9AE6B4; border-radius: 12px;
    padding: 14px 18px; margin-bottom: 20px; flex-wrap: wrap;
  }
  .sample-banner-left { display: flex; align-items: center; gap: 12px; }
  .sample-icon { font-size: 28px; flex-shrink: 0; }
  .sample-title { font-size: 13px; font-weight: 700; color: var(--text); }
  .sample-desc  { font-size: 11px; color: var(--muted); margin-top: 2px; }
  .sample-banner-right { display: flex; gap: 8px; flex-wrap: wrap; }
  .btn-sample-dl {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 7px 14px; border-radius: 8px; font-size: 12px; font-weight: 600;
    background: var(--white); color: var(--blue); border: 1.5px solid var(--blue);
    cursor: pointer; text-decoration: none; transition: background 0.15s;
  }
  .btn-sample-dl:hover { background: #EBF2FF; }
  .btn-sample-fill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 7px 14px; border-radius: 8px; font-size: 12px; font-weight: 600;
    background: var(--teal); color: var(--white); border: none;
    cursor: pointer; transition: opacity 0.15s;
  }
  .btn-sample-fill:hover { opacity: 0.88; }

  /* 진행률 바 */
  .progress-wrap { background: var(--bg); border-radius: 99px; height: 10px; overflow: hidden; margin: 12px 0; }
  .progress-bar  { height: 100%; border-radius: 99px; background: linear-gradient(90deg, var(--blue), var(--teal)); transition: width 0.4s ease; }

  /* 로그 박스 */
  .log-box {
    background: #1a1d2e; color: #a8d8a8; font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12px; padding: 14px 16px; border-radius: 8px; height: 200px;
    overflow-y: auto; line-height: 1.6; margin-top: 12px;
  }
  .log-box .log-line { padding: 1px 0; }
  .log-box .log-line.error { color: #f87171; }

  /* 서브스텝 아이콘 */
  .substeps { display: flex; gap: 12px; margin: 14px 0; flex-wrap: wrap; }
  .substep {
    display: flex; align-items: center; gap: 6px;
    padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
    background: var(--bg); color: var(--muted); transition: all 0.3s;
  }
  .substep.active { background: #EBF2FF; color: var(--blue); }
  .substep.done   { background: #D1FAE5; color: var(--success); }

  /* 도메인 체크박스 */
  .domain-chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600;
    cursor: pointer; border: 2px solid var(--border); background: var(--white);
    color: var(--text); transition: all 0.15s; user-select: none;
  }
  .domain-chip.checked {
    border-color: var(--teal); background: #E6F7F7; color: var(--teal);
  }
  .domain-chip input[type=checkbox] { display: none; }
  .domain-chip .chip-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--border); transition: background 0.15s; flex-shrink: 0;
  }
  .domain-chip.checked .chip-dot { background: var(--teal); }

  /* Gate 채팅 UI */
  .gate-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    min-height: 480px;
  }
  @media (max-width: 860px) {
    .gate-layout { grid-template-columns: 1fr; }
  }
  .gate-chat-panel {
    display: flex; flex-direction: column;
    border: 1.5px solid var(--border); border-radius: 10px; overflow: hidden;
    background: #fff;
  }
  .gate-chat-header {
    padding: 10px 14px; background: var(--navy); color: #fff;
    font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px;
  }
  .gate-chat-messages {
    flex: 1; overflow-y: auto; padding: 12px; display: flex;
    flex-direction: column; gap: 10px; min-height: 320px; max-height: 420px;
    background: #F8FAFC;
  }
  .gate-msg { max-width: 88%; padding: 9px 13px; border-radius: 10px; font-size: 13px; line-height: 1.55; }
  .gate-msg.assistant {
    align-self: flex-start; background: #EDF2FF; color: var(--navy);
    border-bottom-left-radius: 3px;
  }
  .gate-msg.user {
    align-self: flex-end; background: var(--teal); color: #fff;
    border-bottom-right-radius: 3px;
  }
  .gate-msg.system {
    align-self: center; background: #F0FDF4; color: #166534;
    font-size: 12px; border: 1px solid #BBF7D0; border-radius: 8px; max-width: 96%;
  }
  .gate-chat-input-row {
    display: flex; gap: 8px; padding: 10px;
    border-top: 1px solid var(--border); background: #fff;
  }
  .gate-chat-input {
    flex: 1; border: 1.5px solid var(--border); border-radius: 8px;
    padding: 8px 12px; font-size: 13px; resize: none; outline: none;
    font-family: inherit; min-height: 40px; max-height: 100px;
    line-height: 1.5; color: var(--text);
  }
  .gate-chat-input:focus { border-color: var(--blue); }
  .gate-chat-send {
    padding: 8px 16px; background: var(--teal); color: #fff;
    border: none; border-radius: 8px; font-size: 13px; font-weight: 600;
    cursor: pointer; white-space: nowrap; align-self: flex-end;
  }
  .gate-chat-send:disabled { opacity: 0.5; cursor: not-allowed; }
  .gate-viewer-panel {
    display: flex; flex-direction: column;
    border: 1.5px solid var(--border); border-radius: 10px; overflow: hidden;
    background: #fff;
  }
  .gate-viewer-header {
    padding: 10px 14px; background: #2D3748; color: #fff;
    font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px;
  }
  .gate-viewer-content {
    flex: 1; overflow-y: auto; padding: 16px;
    font-size: 13px; line-height: 1.75; color: var(--text);
    min-height: 320px; max-height: 420px; background: #fff;
  }
  .gate-viewer-content h2 { font-size: 15px; font-weight: 700; color: var(--navy); margin: 14px 0 6px; border-bottom: 1.5px solid #E2E8F0; padding-bottom: 4px; }
  .gate-viewer-content h3 { font-size: 13px; font-weight: 600; color: var(--blue); margin: 10px 0 4px; }
  .gate-viewer-content ul, .gate-viewer-content ol { padding-left: 18px; margin: 4px 0; }
  .gate-viewer-content li { margin: 2px 0; }
  .gate-viewer-content strong { color: var(--navy); }
  .gate-viewer-content code { background: #EDF2FF; padding: 1px 5px; border-radius: 3px; font-size: 12px; }
  .gate-viewer-content blockquote { border-left: 3px solid var(--teal); padding-left: 10px; color: var(--muted); margin: 6px 0; }
  .gate-doc-updated { animation: flashUpdate 0.6s ease; }
  @keyframes flashUpdate { 0%,100%{background:#fff} 50%{background:#E0F2FE} }
  /* 기존 textarea (숨김) */
  .gate-textarea { display: none; }

  /* 완료 카드 */
  .result-box {
    background: linear-gradient(135deg, #EBF2FF, #D1FAE5);
    border: 1.5px solid #A7F3D0; border-radius: 10px;
    padding: 20px 24px; margin-bottom: 16px;
  }
  .result-filename { font-size: 18px; font-weight: 700; color: var(--navy); }
  .result-meta { font-size: 13px; color: var(--muted); margin-top: 4px; }
  .tc-stats { display: flex; gap: 24px; margin-top: 14px; }
  .tc-stat { text-align: center; }
  .tc-stat-num { font-size: 28px; font-weight: 800; color: var(--blue); }
  .tc-stat-label { font-size: 12px; color: var(--muted); }

  /* 숨김 */
  .hidden { display: none !important; }

  /* 안내 */
  .info-box {
    background: #EBF2FF; border-left: 4px solid var(--blue);
    padding: 10px 14px; border-radius: 0 6px 6px 0; font-size: 13px; color: var(--navy);
    margin-bottom: 14px;
  }

  /* 완료 카드 - 파일 행 */
  .result-file {
    display: flex; align-items: center; gap: 14px;
    padding: 16px; background: #F0FBF8; border: 1px solid #B2E8DC;
    border-radius: 12px; margin-bottom: 16px;
  }
  .ricon { font-size: 32px; flex-shrink: 0; }
  .rinfo { flex: 1; overflow: hidden; }
  .rname { font-size: 14px; font-weight: 700; color: var(--navy);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .rsize { font-size: 12px; color: var(--muted); margin-top: 2px; }

  /* 액션 버튼 행 */
  .action-row { display: flex; gap: 12px; }
  .btn-dl {
    flex: 1; padding: 12px; background: var(--teal); color: #fff; border: none;
    border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer;
    transition: background .2s; display: flex; align-items: center;
    justify-content: center; gap: 6px;
  }
  .btn-dl:hover { background: #016570; }
  .btn-drive {
    flex: 1; padding: 12px; background: #fff; color: var(--navy);
    border: 2px solid #D1D9EE; border-radius: 10px; font-size: 14px;
    font-weight: 600; cursor: pointer; transition: all .2s;
    display: flex; align-items: center; justify-content: center; gap: 6px;
  }
  .btn-drive:hover { border-color: #3557A0; background: #F7F9FF; }

  /* Drive 모달 */
  .modal-bg {
    position: fixed; inset: 0; background: rgba(0,0,0,.45);
    display: none; align-items: center; justify-content: center; z-index: 999;
  }
  .modal-bg.open { display: flex; }
  .modal {
    background: #fff; border-radius: 16px; padding: 32px;
    max-width: 440px; width: 90%; box-shadow: 0 8px 32px rgba(0,0,0,.18);
  }
  .modal h2 { font-size: 17px; font-weight: 700; color: var(--navy); margin-bottom: 16px; }
  .modal ol { padding-left: 20px; color: #444; font-size: 13px; line-height: 2.2; }
  .modal-btns { display: flex; gap: 10px; margin-top: 22px; }
  .btn-open-drive {
    flex: 1; padding: 11px; background: #4285F4; color: #fff; border: none;
    border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
  }
  .btn-modal-close {
    flex: 1; padding: 11px; background: #F4F6FB; color: #444; border: none;
    border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer;
  }

  /* 토스트 */
  #toast {
    position: fixed; bottom: 28px; left: 50%; transform: translateX(-50%);
    padding: 12px 24px; border-radius: 10px; font-size: 14px; font-weight: 600;
    display: none; z-index: 1000; box-shadow: 0 4px 16px rgba(0,0,0,.2); white-space: nowrap;
  }
  #toast.success { background: var(--teal); color: #fff; }
  #toast.error   { background: #e53e3e; color: #fff; }

  @media (max-width: 480px) { .action-row { flex-direction: column; } }

  /* GitHub 파일 트리 */
  .btn-preview-tree { margin-top: 8px; padding: 5px 12px; font-size: 12px; border: 1px solid var(--border); border-radius: 6px; background: var(--surface); cursor: pointer; }
  .btn-preview-tree:hover { background: var(--hover); }
  .tree-panel { margin-top: 10px; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; max-height: 360px; overflow-y: auto; font-size: 12px; }
  .tree-loading, .tree-error { padding: 16px; color: var(--muted); }
  .tree-error { color: #e53e3e; }
  .tree-header { padding: 10px 14px; background: var(--surface); border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; position: sticky; top: 0; z-index: 1; }
  .tree-actions button { padding: 3px 8px; font-size: 11px; border: 1px solid var(--border); border-radius: 4px; background: var(--surface); cursor: pointer; margin-left: 4px; }
  .btn-apply-tree { background: var(--surface); font-weight: 600; }
  .tree-list { padding: 8px 0; }
  .tree-folder { padding: 4px 14px; }
  .tree-folder-label { display: block; font-weight: 600; color: var(--text); padding: 3px 0; cursor: pointer; }
  .tree-file-label { display: block; padding: 2px 0 2px 20px; color: var(--muted); cursor: pointer; }
  .tree-file-label:hover, .tree-folder-label:hover { color: var(--text); }
  .file-size { color: var(--muted); font-size: 10px; }
</style>
</head>
<body>

{% if api_warning %}
<div class="api-warning">
  ⚠️ <strong>ANTHROPIC_API_KEY 미설정</strong> — .env 파일에 API 키를 설정해주세요.
  예: <code>ANTHROPIC_API_KEY=sk-ant-...</code>
</div>
{% endif %}

<header>
  <div>
    <h1>🤖 TC 자동화 v2</h1>
    <span class="version-badge">v0.9.5</span>
  </div>
  <span class="header-sub">Claude AI · PDF / URL / 텍스트 → Excel</span>
</header>

<!-- 진행 스텝 바 -->
<div class="steps-bar">
  <div class="step-item active" id="stepBar1">
    <div class="step-num">1</div>📥 입력
  </div>
  <span class="step-arrow">›</span>
  <div class="step-item" id="stepBar2">
    <div class="step-num">2</div>⚙️ 분석
  </div>
  <span class="step-arrow">›</span>
  <div class="step-item" id="stepBar3">
    <div class="step-num">3</div>🔍 검토
  </div>
  <span class="step-arrow">›</span>
  <div class="step-item" id="stepBar4">
    <div class="step-num">4</div>✍️ TC 생성
  </div>
  <span class="step-arrow">›</span>
  <div class="step-item" id="stepBar5">
    <div class="step-num">5</div>📊 완료
  </div>
</div>

<main>

  <!-- Step 1: 입력 카드 -->
  <div class="card" id="card1">
    <div class="card-title">📥 입력 설정 <span class="badge">Step 1</span></div>

    <!-- 프로젝트 선택 -->
    <div class="project-select-row">
      <label>📁 프로젝트</label>
      <select class="project-dropdown" id="projectDropdown" onchange="onProjectDropdownChange()">
        <option value="">— 프로젝트를 선택하세요 —</option>
      </select>
      <button class="btn-new-project" onclick="toggleNewProjectInline()">+ 새 프로젝트</button>
      <button id="btnDeleteProject" style="display:none;padding:7px 10px;background:none;border:1px solid #E5E7EB;border-radius:8px;font-size:12px;cursor:pointer;color:#DC2626;" onclick="deleteDashProject()">삭제</button>
    </div>
    <div class="project-new-inline" id="newProjectInline">
      <input type="text" id="newDashProjectName" placeholder="새 프로젝트명 입력"
        onkeydown="if(event.key==='Enter')createDashProject();">
      <button class="btn-new-project" onclick="createDashProject()">생성</button>
      <button style="padding:7px 10px;background:none;border:1px solid var(--border);border-radius:8px;font-size:12px;cursor:pointer;" onclick="toggleNewProjectInline()">취소</button>
    </div>
    <div class="project-resume-bar" id="resumeBar">
      <span>💾 이전 작업이 있습니다 — <strong id="resumeStage"></strong> 단계까지 완료</span>
      <span id="resumeSavedAt" style="font-size:11px;opacity:0.7;margin-left:auto;"></span>
      <button class="btn-resume-pipeline" onclick="resumePipeline()">이어서 작업</button>
      <button style="padding:5px 10px;background:none;border:1px solid #93C5FD;border-radius:6px;font-size:11px;cursor:pointer;color:#1E40AF;" onclick="discardResume()">처음부터</button>
    </div>

    <!-- 모드 스위처 -->
    <div class="mode-switcher">
      <button type="button" class="mode-btn active" id="modeNew" onclick="switchMode('new')">
        🆕 신규 TC 생성
      </button>
      <button type="button" class="mode-btn" id="modeModify" onclick="switchMode('modify')">
        ✏️ 기존 TC 수정
      </button>
    </div>

    <!-- ── 신규 생성 모드 ── -->
    <div id="panelNew">


      <div class="form-group">
        <label class="form-label">프로젝트명</label>
        <input type="text" id="projectName" class="form-input"
               placeholder="예: Supercycl 모바일" value="">
      </div>

      <div class="form-group">
        <label class="form-label" style="display:flex;align-items:center;justify-content:space-between">
          <span>입력 소스</span>
          <span style="font-size:11px;color:var(--muted);font-weight:400">여러 소스를 자유롭게 조합하세요</span>
        </label>
        <div class="source-add-bar">
          <button type="button" class="btn-add-source" onclick="addSource('pdf')">📄 PDF 추가</button>
          <button type="button" class="btn-add-source" onclick="addSource('url')">🔗 GitHub URL 추가</button>
          <button type="button" class="btn-add-source" onclick="addSource('web')">🌐 웹 URL 추가</button>
          <button type="button" class="btn-add-source" onclick="addSource('md')">📝 마크다운 파일 추가</button>
          <button type="button" class="btn-add-source" onclick="addSource('text')">✏️ 텍스트 추가</button>
        </div>
        <div id="sourceList"></div>
        <div id="sourceEmpty" class="source-empty">
          소스를 추가하세요.<br>
          <span style="font-size:12px">PDF · GitHub URL · 웹페이지 · 마크다운 파일 · 텍스트 등을 자유롭게 조합할 수 있습니다.</span>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label" style="display:flex;align-items:center;justify-content:space-between">
          <span>TC 생성 범위</span>
          <span style="font-size:11px;color:var(--muted);font-weight:400">선택 — 비우면 전체 TC 생성</span>
        </label>
        <textarea id="focusArea" class="form-input" rows="2"
          style="resize:vertical; min-height:48px; font-size:13px; line-height:1.5;"
          placeholder="특정 기능에 대해서만 TC를 만들려면 여기에 입력하세요.&#10;예) import 기능 / 로그인 및 회원가입 / 결제 모듈의 환불 처리"></textarea>
        <div style="font-size:11px; color:var(--muted); margin-top:3px;">
          입력하면 해당 기능에 집중하여 TC를 생성합니다. 여러 기능은 쉼표 또는 줄바꿈으로 구분하세요.
        </div>
      </div>

      <button class="btn btn-primary" id="startBtn" onclick="startPipeline()">
        🚀 파이프라인 시작
      </button>
    </div>

    <!-- ── 수정 모드 ── -->
    <div id="panelModify" class="hidden">

      <!-- 프로젝트 선택 -->
      <div class="form-group">
        <label class="form-label" style="display:flex;align-items:center;justify-content:space-between">
          <span>수정할 프로젝트 선택</span>
          <button type="button" class="btn-new-project" onclick="toggleNewProjectForm()">＋ 새 프로젝트</button>
        </label>
        <select class="project-select" id="projectSelect" onchange="onProjectSelect()">
          <option value="">— 프로젝트를 선택하세요 —</option>
        </select>
        <div class="project-card" id="projectCard">
          <div class="project-card-name" id="projectCardName"></div>
          <div class="project-card-meta" id="projectCardMeta"></div>
          <button type="button" class="btn-delete-project" id="btnDeleteProject" onclick="deleteProject()" style="display:none">🗑 삭제</button>
        </div>
        <!-- 새 프로젝트 생성 폼 -->
        <div id="newProjectForm" class="new-project-form hidden">
          <input type="text" id="newProjectName" class="form-input" placeholder="새 프로젝트명 입력 (예: Supercycl iOS v2)">
          <div style="display:flex;gap:8px;margin-top:8px">
            <button type="button" class="btn btn-primary" style="flex:1" onclick="createProject()">✅ 생성</button>
            <button type="button" class="btn" style="flex:1" onclick="toggleNewProjectForm()">취소</button>
          </div>
        </div>
      </div>

      <!-- TC 파일 가져오기 -->
      <div class="form-group">
        <label class="form-label" style="display:flex;align-items:center;justify-content:space-between">
          <span>TC 파일 가져오기</span>
          <span style="font-size:11px;color:var(--muted);font-weight:400">Excel 업로드 또는 Google Sheets 연동</span>
        </label>
        <!-- 탭 선택 -->
        <div class="tc-import-tabs">
          <button type="button" class="tc-import-tab active" id="tabExcel" onclick="switchImportTab('excel')">📊 Excel 업로드</button>
          <button type="button" class="tc-import-tab" id="tabSheets" onclick="switchImportTab('sheets')">🔗 Google Sheets</button>
        </div>
        <!-- Excel 업로드 -->
        <div id="panelExcel">
          <div class="tc-upload-area" id="tcDropzone" onclick="document.getElementById('tcFileInput').click()">
            📎 Excel(.xlsx/.xls) 또는 .md 파일을 드래그하거나 클릭하여 업로드
          </div>
          <input type="file" id="tcFileInput" accept=".xlsx,.xls,.md" style="display:none">
        </div>
        <!-- Google Sheets -->
        <div id="panelSheets" class="hidden">
          <input type="text" id="sheetsUrl" class="form-input"
                 placeholder="https://docs.google.com/spreadsheets/d/...">
          <div class="input-hint">⚠️ 시트가 <strong>링크가 있는 사용자에게 공개</strong> 설정이어야 합니다.</div>
          <button type="button" class="btn btn-primary" style="margin-top:8px;width:100%" onclick="importSheets()">🔗 Sheets 가져오기</button>
        </div>
        <div id="tcUploadStatus" class="hidden" style="margin-top:8px;font-size:13px;color:var(--success);font-weight:600;"></div>
      </div>

      <!-- 프로젝트명 (업로드 시) -->
      <div class="form-group" id="uploadProjectNameGroup" style="display:none">
        <label class="form-label">업로드 파일의 프로젝트명</label>
        <input type="text" id="uploadProjectName" class="form-input"
               placeholder="예: Supercycl 모바일 v2">
        <div class="input-hint">저장 후 다음번에 드롭다운에서 선택할 수 있습니다.</div>
      </div>

      <!-- 변경사항 입력 -->
      <div class="form-group">
        <label class="form-label">변경사항 설명</label>
        <div class="info-box" style="margin-bottom:8px">
          ✏️ <strong>무엇이 변경되었는지 구체적으로 작성하세요.</strong><br>
          기능 추가/삭제/변경, 정책 변경, 화면 수정 등 모든 변경사항을 포함할수록 정확합니다.
        </div>
        <textarea id="changeDesc" class="form-input text-input-area"
                  placeholder="예: 출금 한도가 1일 500만원에서 1000만원으로 변경됨. OTP 인증 단계가 추가됨. 단, 10만원 미만 소액 출금은 OTP 생략 가능."></textarea>
      </div>

      <button class="btn btn-primary" id="startModifyBtn" onclick="startModify()">
        ✏️ TC 수정 시작
      </button>
    </div>
  </div>

  <!-- Step 2: 파이프라인 실행 카드 -->
  <div class="card hidden" id="card2">
    <div class="card-title">⚙️ 파이프라인 실행 <span class="badge">Step 2</span></div>

    <div class="substeps">
      <div class="substep" id="sub1">📄 파싱</div>
      <div class="substep" id="sub2">🔎 정책</div>
      <div class="substep" id="sub3">📋 기능</div>
      <div class="substep" id="sub4">🗂 분류</div>
    </div>

    <div style="font-size:14px; font-weight:600; color:var(--blue); margin-bottom:6px;">
      <span id="stageLabel">시작 중...</span><span id="countdownLabel" style="font-weight:400; font-size:12px; color:var(--muted);"></span>
    </div>
    <div class="progress-wrap">
      <div class="progress-bar" id="progressBar" style="width:0%"></div>
    </div>

    <div class="log-box" id="logBox"></div>
    <div style="margin-top:12px; text-align:right;">
      <button class="btn-stop" id="stopBtn2" onclick="stopPipeline()">⏹ 파이프라인 중단</button>
    </div>
  </div>

  <!-- Step 3: Human Gate 카드 -->
  <div class="card hidden" id="card3">
    <div class="card-title" id="gateTitle">🔍 분류표 검토 <span class="badge">Step 3 · Human Gate</span></div>
    <div class="info-box" id="gateInfoBox">
      AI가 생성한 분류표입니다. 채팅으로 수정을 요청하고, 우측 Viewer에서 결과를 확인한 뒤 승인하세요.
    </div>

    <!-- 채팅 + Viewer 2-column 레이아웃 -->
    <div class="gate-layout">

      <!-- 왼쪽: AI 채팅 패널 -->
      <div class="gate-chat-panel">
        <div class="gate-chat-header">
          💬 AI와 대화하여 수정
        </div>
        <div class="gate-chat-messages" id="gateChatMessages">
          <!-- 메시지가 여기에 추가됨 -->
        </div>
        <div class="gate-chat-input-row">
          <textarea class="gate-chat-input" id="gateChatInput"
            placeholder="수정 요청을 입력하세요. 예) AUTH 도메인 케이스 3번 삭제해줘"
            onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendGateChat();}"></textarea>
          <button class="gate-chat-send" id="gateChatSend" onclick="sendGateChat()">전송</button>
        </div>
      </div>

      <!-- 오른쪽: 문서 Viewer -->
      <div class="gate-viewer-panel">
        <div class="gate-viewer-header">
          📄 문서 Viewer <span id="gateViewerBadge" style="margin-left:auto; font-size:11px; opacity:0.8;"></span>
        </div>
        <div class="gate-viewer-content" id="gateViewer">
          <!-- 마크다운 렌더링 결과 -->
        </div>
      </div>
    </div>

    <!-- 숨겨진 원본 데이터 저장용 -->
    <textarea class="gate-textarea" id="gateContent"></textarea>

    <!-- TC 생성 범위 선택 -->
    <div style="margin-top:18px; margin-bottom:8px; font-size:13px; font-weight:600; color:var(--navy);">
      📌 TC 생성 범위 선택
      <span style="font-weight:400; color:var(--muted); font-size:12px; margin-left:8px;">체크된 도메인만 TC를 생성합니다</span>
    </div>
    <div id="domainChecklist" style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:14px;">
      <!-- JS로 동적 생성 -->
    </div>
    <div style="display:flex; gap:8px; margin-bottom:16px; align-items:center;">
      <button type="button" onclick="selectAllDomains(true)"
        style="font-size:12px; padding:4px 12px; border:1px solid var(--border);
          border-radius:6px; background:none; cursor:pointer; color:var(--text);">
        전체 선택
      </button>
      <button type="button" onclick="selectAllDomains(false)"
        style="font-size:12px; padding:4px 12px; border:1px solid var(--border);
          border-radius:6px; background:none; cursor:pointer; color:var(--text);">
        전체 해제
      </button>
      <button type="button" onclick="exportGateExcel()"
        style="font-size:12px; padding:4px 14px; border:1.5px solid var(--teal);
          border-radius:6px; background:none; cursor:pointer; color:var(--teal);
          font-weight:600; margin-left:auto; display:flex; align-items:center; gap:5px;">
        📥 Excel로 내보내기
      </button>
    </div>

    <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
      <button class="btn btn-success" onclick="approveGate()">
        ✅ 승인 및 TC 생성 시작
      </button>
      <button style="padding:8px 16px;background:#EFF6FF;color:#1D4ED8;border:1.5px solid #93C5FD;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;" onclick="regenerateClassification()">
        🔄 분류표 다시 생성
      </button>
      <button class="btn-stop" id="stopBtn3" onclick="stopPipeline()">⏹ 여기서 중단</button>
    </div>
  </div>

  <!-- Step 4: TC 생성 카드 -->
  <div class="card hidden" id="card4">
    <div class="card-title">✍️ TC 생성 중 <span class="badge">Step 4</span></div>
    <div id="tcStageLabel" style="font-size:14px; font-weight:600; color:var(--blue); margin-bottom:6px;">
      TC 작성 중...
    </div>
    <div class="progress-wrap">
      <div class="progress-bar" id="tcProgressBar" style="width:50%"></div>
    </div>
    <div class="log-box" id="tcLogBox"></div>
    <div style="margin-top:12px; text-align:right;">
      <button class="btn-stop" id="stopBtn4" onclick="stopPipeline()">⏹ TC 생성 중단</button>
    </div>
  </div>

  <!-- Step 5: 완료 카드 -->
  <div class="card hidden" id="card5">
    <div class="card-title">📊 완료 <span class="badge">Step 5</span></div>

    <!-- 파일 정보 행 -->
    <div class="result-file">
      <span class="ricon">📊</span>
      <div class="rinfo">
        <div class="rname" id="resultFilename">—</div>
        <div class="rsize" id="resultMeta">—</div>
      </div>
      <button onclick="openFolder()"
        style="margin-left:auto;background:none;border:1px solid #CBD5E0;
          color:#555;font-size:12px;padding:5px 12px;border-radius:8px;
          cursor:pointer;white-space:nowrap">
        📁 폴더 열기
      </button>
    </div>

    <!-- TC 통계 -->
    <div class="tc-stats" style="margin-bottom:16px">
      <div class="tc-stat">
        <div class="tc-stat-num" id="statTotal">—</div>
        <div class="tc-stat-label">총 TC</div>
      </div>
      <div class="tc-stat">
        <div class="tc-stat-num" id="statMin">—</div>
        <div class="tc-stat-label">최소 TC (≈35%)</div>
      </div>
    </div>

    <!-- 액션 버튼 행 -->
    <div class="action-row">
      <button class="btn-drive" id="driveBtn" onclick="uploadToDrive()">
        <svg width="16" height="16" viewBox="0 0 87.3 78" xmlns="http://www.w3.org/2000/svg">
          <path d="m6.6 66.85 3.85 6.65c.8 1.4 1.95 2.5 3.3 3.3l13.75-23.8h-27.5c0 1.55.4 3.1 1.2 4.5z" fill="#0066da"/>
          <path d="m43.65 25-13.75-23.8c-1.35.8-2.5 1.9-3.3 3.3l-25.4 44a9.06 9.06 0 0 0-1.2 4.5h27.5z" fill="#00ac47"/>
          <path d="m73.55 76.8c1.35-.8 2.5-1.9 3.3-3.3l1.6-2.75 7.65-13.25c.8-1.4 1.2-2.95 1.2-4.5h-27.502l5.852 11.5z" fill="#ea4335"/>
          <path d="m43.65 25 13.75-23.8c-1.35-.8-2.9-1.2-4.5-1.2h-18.5c-1.6 0-3.15.45-4.5 1.2z" fill="#00832d"/>
          <path d="m59.8 53h-32.3l-13.75 23.8c1.35.8 2.9 1.2 4.5 1.2h50.8c1.6 0 3.15-.45 4.5-1.2z" fill="#2684fc"/>
          <path d="m73.4 26.5-12.7-22c-.8-1.4-1.95-2.5-3.3-3.3l-13.75 23.8 16.15 27h27.45c0-1.55-.4-3.1-1.2-4.5z" fill="#ffba00"/>
        </svg>
        Google Drive에 올리기
      </button>
    </div>
  </div>

</main>

<!-- 시스템 점검용 샘플 기획서 (푸터) -->
<footer class="sample-footer">
  <span class="sample-footer-label">🧪 시스템 점검용 샘플:</span>
  <a href="/sample-download" class="btn-sample-dl" download>⬇ 샘플 PDF</a>
  <button type="button" class="btn-sample-fill" onclick="loadSampleDoc()">✏️ 직접입력으로 채우기</button>
</footer>

<!-- 오류 복구 모달 -->
<div class="modal-bg" id="recovery-modal">
  <div class="modal">
    <h2>⚠️ 파이프라인 오류 발생</h2>
    <p id="recoveryErrorMsg" style="font-size:13px;color:#e53e3e;margin-bottom:12px"></p>
    <div id="recoveryCheckpointInfo" class="hidden" style="font-size:12px;color:#555;background:#f7f7f7;padding:10px;border-radius:8px;margin-bottom:14px"></div>
    <div style="display:flex;flex-direction:column;gap:8px">
      <button class="btn btn-primary" id="btnResume" onclick="restartModify('resume')" style="display:none">
        🔄 이어서 재시작 (체크포인트 복원)
      </button>
      <button class="btn btn-primary" onclick="restartModify('fresh')">
        ▶ 처음부터 재시작
      </button>
      <button class="btn" onclick="closeRecoveryModal()">
        ✕ 종료
      </button>
    </div>
  </div>
</div>

<!-- Google Drive 연동 안내 모달 -->
<div class="modal-bg" id="drive-modal">
  <div class="modal">
    <h2>🔑 Google Drive 연동 설정</h2>
    <p style="font-size:13px;color:#444;margin-bottom:14px">
      최초 1회 <strong>credentials.json</strong> 파일 설정이 필요합니다.
    </p>
    <ol>
      <li><a href="https://console.cloud.google.com/apis/credentials" target="_blank"
          style="color:#3557A0">Google Cloud Console</a> 접속</li>
      <li><strong>+ 사용자 인증 정보 만들기 → OAuth 클라이언트 ID</strong></li>
      <li>애플리케이션 유형: <strong>데스크톱 앱</strong> 선택 후 만들기</li>
      <li>JSON 다운로드 → <strong>tc-ui 폴더에 <code>credentials.json</code>으로 저장</strong></li>
      <li>저장 후 다시 <strong>Drive에 올리기</strong> 클릭 → 브라우저에서 Google 계정 인증</li>
    </ol>
    <p style="font-size:12px;color:#888;margin-top:10px">
      또한 <code>config.json</code>에 <code>google_drive.upload_folder_id</code>를 설정해야 합니다.
    </p>
    <div class="modal-btns">
      <button class="btn-open-drive"
        onclick="window.open('https://console.cloud.google.com/apis/credentials','_blank')">
        Cloud Console 열기
      </button>
      <button class="btn-modal-close" onclick="closeDriveModal()">닫기</button>
    </div>
  </div>
</div>

<div id="toast"></div>

<script>
let currentSid = null;
let currentFilename = null;
let eventSource = null;
let currentMode = 'new';          // 'new' | 'modify'
let projects = [];                // 프로젝트 목록 캐시
let selectedTcFile = null;        // 업로드된 TC 파일명

// ── 프로젝트 드롭다운 ─────────────────────────────────────────────────────────
let selectedProject = null;
let projectResumeState = null;

async function loadDashProjects() {
  try {
    const r = await fetch('/projects');
    const list = await r.json();
    projects = list;
    const dd = document.getElementById('projectDropdown');
    dd.innerHTML = '<option value="">-- 프로젝트를 선택하세요 --</option>';
    // 샘플(is_sample)은 하단에 배치
    const normal = list.filter(p => !p.is_sample);
    const samples = list.filter(p => p.is_sample);
    const sorted = [...normal, ...samples];
    sorted.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.name;
      let label = p.name + '  [진행 중]';
      if (p.is_sample) label += '  (샘플)';
      opt.textContent = label;
      dd.appendChild(opt);
    });
    if (selectedProject) dd.value = selectedProject;
  } catch(e) {
    console.error('프로젝트 로드 실패', e);
  }
}

async function onProjectDropdownChange() {
  const name = document.getElementById('projectDropdown').value;
  projectResumeState = null;

  // ── UI 전체 초기화 ──
  // SSE 연결 종료
  if (eventSource) { eventSource.close(); eventSource = null; }
  currentSid = null;
  currentFilename = null;
  stopCountdown();
  // 카드 숨김 (card2~card5)
  ['card2','card3','card4','card5'].forEach(function(id) {
    var card = document.getElementById(id);
    if (card) card.classList.add('hidden');
  });
  // 중단/오류 배너 제거
  document.querySelectorAll('.stopped-banner, .error-banner').forEach(function(el) { el.remove(); });
  // 버튼 상태 복원
  document.getElementById('startBtn').disabled = false;
  var startModifyBtn = document.getElementById('startModifyBtn');
  if (startModifyBtn) startModifyBtn.disabled = false;
  setStepBar(1);
  // 상단 card2 내부 요소 복원 (TC 단계에서 숨겼던 것들)
  var logBox = document.getElementById('logBox');
  if (logBox) { logBox.style.display = ''; logBox.innerHTML = ''; }
  var stopBtn2 = document.getElementById('stopBtn2');
  if (stopBtn2) stopBtn2.style.display = '';
  var progressWrap = document.getElementById('progressBar');
  if (progressWrap && progressWrap.parentElement) progressWrap.parentElement.style.display = '';
  var substeps = document.querySelector('#card2 .substeps');
  if (substeps) substeps.style.display = '';
  document.getElementById('stageLabel').textContent = '시작 중...';
  // 소스/포커스 초기화
  sources = [];
  sourceCounter = 0;
  renderSources();
  document.getElementById('focusArea').value = '';
  // 이어서 작업 바 / 삭제 버튼
  document.getElementById('resumeBar').style.display = 'none';
  document.getElementById('btnDeleteProject').style.display = name ? 'inline-block' : 'none';

  if (!name) { selectedProject = null; document.getElementById('projectName').value = ''; return; }
  selectedProject = name;
  document.getElementById('projectName').value = name;
  // 수정 모드 드롭다운도 연동
  var sel = document.getElementById('projectSelect');
  if (sel) {
    for (var i = 0; i < sel.options.length; i++) {
      if (sel.options[i].value === name) { sel.selectedIndex = i; break; }
    }
  }

  // ── 해당 프로젝트 데이터 로드 ──
  // 이전 작업 상태 확인
  try {
    var r = await fetch('/projects/' + encodeURIComponent(name) + '/state');
    var d = await r.json();
    if (d.ok && d.has_state) {
      projectResumeState = d;
      var stageNames = {parsed:'문서 파싱', policy:'정책 분석', features:'기능 목록', classifying:'분류표 생성', gate_waiting:'분류표 검토 대기', tc_writing:'TC 작성'};
      document.getElementById('resumeStage').textContent = stageNames[d.stage] || d.stage;
      document.getElementById('resumeSavedAt').textContent = d.saved_at || '';
      document.getElementById('resumeBar').style.display = 'flex';
      if (d.focus_area) document.getElementById('focusArea').value = d.focus_area;
    }
  } catch(e) {}
  // 이전 소스 복원
  try {
    var r2 = await fetch('/projects/' + encodeURIComponent(name) + '/sources');
    var d2 = await r2.json();
    if (d2.ok && d2.has_sources && d2.sources.length > 0) {
      sources = [];
      sourceCounter = 0;
      d2.sources.forEach(function(s) {
        var id = ++sourceCounter;
        sources.push({ id: id, type: s.type, content: s.content || '', selected_files: s.selected_files || null });
      });
      renderSources();
      if (d2.focus_area) document.getElementById('focusArea').value = d2.focus_area;
      showToast('이전 소스 ' + d2.sources.length + '개를 불러왔습니다.');
    }
  } catch(e) {}
}

function toggleNewProjectInline() {
  const row = document.getElementById('newProjectInline');
  const visible = row.style.display === 'flex';
  row.style.display = visible ? 'none' : 'flex';
  if (!visible) document.getElementById('newDashProjectName').focus();
}

async function retryPipeline() {
  // 오류 배너 제거
  document.querySelectorAll('.error-banner').forEach(el => el.remove());
  var name = selectedProject || document.getElementById('projectName').value.trim();
  if (!name) { alert('프로젝트를 선택해주세요.'); return; }
  document.getElementById('startBtn').disabled = true;
  document.getElementById('stageLabel').textContent = '이어서 재시작 중...';
  try {
    var r = await fetch('/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_name: name, resume: true })
    });
    var d = await r.json();
    if (!d.ok) { alert(d.error); document.getElementById('startBtn').disabled = false; return; }
    currentSid = d.sid;
    showToast('이전 단계에서 이어서 재시작합니다.');
    connectStream(d.sid);
  } catch(e) {
    alert('오류: ' + e.message);
    document.getElementById('startBtn').disabled = false;
  }
}

function restartFromScratch() {
  document.querySelectorAll('.error-banner').forEach(el => el.remove());
  document.getElementById('card2').classList.add('hidden');
  document.getElementById('startBtn').disabled = false;
  setStepBar(1);
  showToast('소스를 확인하고 파이프라인을 다시 시작하세요.');
}

async function resumePipeline() {
  if (!selectedProject) return;
  document.getElementById('startBtn').disabled = true;
  document.getElementById('card2').classList.remove('hidden');
  setStepBar(2);
  document.getElementById('card2').scrollIntoView({ behavior: 'smooth', block: 'start' });
  try {
    const r = await fetch('/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_name: selectedProject, resume: true })
    });
    const d = await r.json();
    if (!d.ok) { alert(d.error); document.getElementById('startBtn').disabled = false; return; }
    currentSid = d.sid;
    showToast('이전 작업에서 이어서 진행합니다.');
    connectStream(d.sid);
  } catch(e) {
    alert('오류: ' + e.message);
    document.getElementById('startBtn').disabled = false;
  }
}

function discardResume() {
  document.getElementById('resumeBar').style.display = 'none';
  projectResumeState = null;
  showToast('처음부터 새로 시작합니다.');
}

async function deleteDashProject() {
  if (!selectedProject) return;
  if (!confirm(selectedProject + ' 프로젝트를 목록에서 숨길까요?')) return;
  try {
    const r = await fetch('/projects/' + encodeURIComponent(selectedProject), { method: 'DELETE' });
    const d = await r.json();
    if (!d.ok) { alert(d.error); return; }
    selectedProject = null;
    document.getElementById('projectName').value = '';
    document.getElementById('resumeBar').style.display = 'none';
    document.getElementById('btnDeleteProject').style.display = 'none';
    await loadDashProjects();
    showToast('프로젝트가 목록에서 제거되었습니다.');
  } catch(e) {
    alert('오류: ' + e.message);
  }
}

async function createDashProject() {
  const input = document.getElementById('newDashProjectName');
  const name = input.value.trim();
  if (!name) { input.focus(); return; }
  try {
    const r = await fetch('/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    const d = await r.json();
    if (!d.ok) { alert(d.error); return; }
    input.value = '';
    document.getElementById('newProjectInline').style.display = 'none';
    await loadDashProjects();
    document.getElementById('projectDropdown').value = name;
    onProjectDropdownChange();
    showToast('프로젝트 생성: ' + name);
  } catch(e) {
    alert('오류: ' + e.message);
  }
}

// 페이지 로드 시 프로젝트 목록 불러오기
setTimeout(loadDashProjects, 100);

// ── 모드 전환 ──────────────────────────────────────────────────────────────────
function switchMode(mode) {
  currentMode = mode;
  document.getElementById('modeNew').classList.toggle('active', mode === 'new');
  document.getElementById('modeModify').classList.toggle('active', mode === 'modify');
  document.getElementById('panelNew').classList.toggle('hidden', mode !== 'new');
  document.getElementById('panelModify').classList.toggle('hidden', mode !== 'modify');
  if (mode === 'modify') {
    loadProjects();
    initTcDropzone();
  }
}

// 샘플 기획서 불러오기 — 직접 입력 모드로 전환 후 textarea 채우기
async function loadSampleDoc() {
  try {
    const r = await fetch('/sample-content');
    const data = await r.json();
    // 텍스트 소스로 추가
    const id = ++sourceCounter;
    sources.push({ id, type: 'text', content: data.content });
    renderSources();
    const pn = document.getElementById('projectName');
    if (!pn.value.trim()) pn.value = '샘플_쇼핑몰앱';
    showToast('샘플 기획서가 소스로 추가됐습니다. 파이프라인을 시작하세요!');
  } catch(e) {
    alert('샘플 불러오기 실패: ' + e.message);
  }
}

// 간단한 토스트 메시지
function showToast(msg) {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    t.style.cssText = 'position:fixed;bottom:28px;left:50%;transform:translateX(-50%);' +
      'background:#2D3748;color:#fff;padding:10px 22px;border-radius:24px;' +
      'font-size:13px;font-weight:600;z-index:9999;opacity:0;transition:opacity 0.3s;pointer-events:none;';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.style.opacity = '1';
  setTimeout(() => { t.style.opacity = '0'; }, 3000);
}

// 프로젝트 목록 불러오기
async function loadProjects() {
  try {
    const r = await fetch('/projects');
    projects = await r.json();
    const sel = document.getElementById('projectSelect');
    sel.innerHTML = '<option value="">— 프로젝트를 선택하세요 —</option>';
    projects.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.name;
      opt.textContent = p.name + ' (' + (p.updated_at || '신규') + ')';
      sel.appendChild(opt);
    });
    if (projects.length === 0) {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = '저장된 프로젝트 없음 — 새 프로젝트를 만드세요';
      opt.disabled = true;
      sel.appendChild(opt);
    }
  } catch(e) {
    console.error('프로젝트 목록 로드 실패', e);
  }
}

function onProjectSelect() {
  const name = document.getElementById('projectSelect').value;
  const card = document.getElementById('projectCard');
  const deleteBtn = document.getElementById('btnDeleteProject');
  if (!name) { card.classList.remove('visible'); deleteBtn.style.display = 'none'; return; }
  const proj = projects.find(p => p.name === name);
  if (!proj) return;
  document.getElementById('projectCardName').textContent = proj.name;
  document.getElementById('projectCardMeta').textContent =
    '최근 업데이트: ' + (proj.updated_at || '—') + (proj.excel_file ? '  |  Excel: ' + proj.excel_file.split('/').pop() : '');
  card.classList.add('visible');
  deleteBtn.style.display = 'inline-block';
  selectedTcFile = null;
  document.getElementById('tcUploadStatus').classList.add('hidden');
  document.getElementById('uploadProjectNameGroup').style.display = 'none';
}

function toggleNewProjectForm() {
  const form = document.getElementById('newProjectForm');
  form.classList.toggle('hidden');
  if (!form.classList.contains('hidden')) document.getElementById('newProjectName').focus();
}

async function createProject() {
  const name = document.getElementById('newProjectName').value.trim();
  if (!name) { alert('프로젝트명을 입력해주세요.'); return; }
  try {
    const r = await fetch('/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    const d = await r.json();
    if (!d.ok) { alert('❌ ' + d.error); return; }
    document.getElementById('newProjectName').value = '';
    document.getElementById('newProjectForm').classList.add('hidden');
    await loadProjects();
    // 방금 만든 프로젝트 자동 선택
    document.getElementById('projectSelect').value = name;
    onProjectSelect();
    showToast('✅ 프로젝트 생성 완료: ' + name);
  } catch(e) {
    alert('오류: ' + e.message);
  }
}

async function deleteProject() {
  const name = document.getElementById('projectSelect').value;
  if (!name) return;
  if (!confirm('"' + name + '" 프로젝트를 삭제할까요?\\n(TC 파일은 삭제되지 않습니다)')) return;
  try {
    const r = await fetch('/projects/' + encodeURIComponent(name), { method: 'DELETE' });
    const d = await r.json();
    if (!d.ok) { alert('❌ ' + d.error); return; }
    await loadProjects();
    document.getElementById('projectCard').classList.remove('visible');
    document.getElementById('btnDeleteProject').style.display = 'none';
    showToast('🗑 프로젝트 삭제 완료');
  } catch(e) {
    alert('오류: ' + e.message);
  }
}

// TC 가져오기 탭 전환
function switchImportTab(tab) {
  document.getElementById('tabExcel').classList.toggle('active', tab === 'excel');
  document.getElementById('tabSheets').classList.toggle('active', tab === 'sheets');
  document.getElementById('panelExcel').classList.toggle('hidden', tab !== 'excel');
  document.getElementById('panelSheets').classList.toggle('hidden', tab !== 'sheets');
}

// Excel / md 파일 업로드 — 이벤트는 switchMode('modify') 이후 패널 표시 시점에 등록
function initTcDropzone() {
  const tcDropzone = document.getElementById('tcDropzone');
  const tcFileInput = document.getElementById('tcFileInput');
  if (!tcDropzone || tcDropzone._initialized) return;
  tcDropzone._initialized = true;
  tcDropzone.addEventListener('dragover', e => { e.preventDefault(); tcDropzone.style.borderColor = 'var(--teal)'; });
  tcDropzone.addEventListener('dragleave', () => { tcDropzone.style.borderColor = ''; });
  tcDropzone.addEventListener('drop', e => {
    e.preventDefault(); tcDropzone.style.borderColor = '';
    if (e.dataTransfer.files.length > 0) uploadTcFile(e.dataTransfer.files[0]);
  });
  if (tcFileInput) {
    tcFileInput.addEventListener('change', () => {
      if (tcFileInput.files.length > 0) uploadTcFile(tcFileInput.files[0]);
    });
  }
}

async function uploadTcFile(file) {
  const ext = file.name.split('.').pop().toLowerCase();
  if (!['md', 'xlsx', 'xls'].includes(ext)) {
    alert('.xlsx / .xls / .md 파일만 업로드 가능합니다.'); return;
  }
  document.getElementById('uploadProjectNameGroup').style.display = 'block';
  const stem = file.name.replace(/\.[^.]+$/, '');
  const projName = document.getElementById('uploadProjectName').value.trim() ||
                   document.getElementById('projectSelect').value || stem;

  tcDropzone.textContent = '⏳ 변환 중...';
  const fd = new FormData();
  fd.append('file', file);
  fd.append('project_name', projName);
  try {
    const r = await fetch('/upload-tc', { method: 'POST', body: fd });
    const d = await r.json();
    if (d.ok) {
      selectedTcFile = d.tc_file;
      tcDropzone.textContent = '✅ ' + file.name + ' 업로드 완료';
      const status = document.getElementById('tcUploadStatus');
      status.textContent = '✅ ' + file.name + ' 등록됨 (프로젝트: ' + d.project_name + ')';
      status.classList.remove('hidden');
      await loadProjects();
      document.getElementById('projectSelect').value = d.project_name;
      onProjectSelect();
      showToast('✅ TC 파일 등록 완료');
    } else {
      tcDropzone.textContent = '❌ ' + d.error;
    }
  } catch(e) {
    tcDropzone.textContent = '❌ 업로드 실패: ' + e.message;
  }
}

// Google Sheets 가져오기
async function importSheets() {
  const url = document.getElementById('sheetsUrl').value.trim();
  const projName = document.getElementById('uploadProjectName').value.trim() ||
                   document.getElementById('projectSelect').value;
  if (!url) { alert('Sheets URL을 입력해주세요.'); return; }
  if (!projName) {
    document.getElementById('uploadProjectNameGroup').style.display = 'block';
    document.getElementById('uploadProjectName').focus();
    alert('프로젝트명을 입력해주세요.'); return;
  }
  document.getElementById('uploadProjectNameGroup').style.display = 'block';
  const status = document.getElementById('tcUploadStatus');
  status.textContent = '⏳ Sheets 가져오는 중...';
  status.classList.remove('hidden');
  try {
    const r = await fetch('/import-sheets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, project_name: projName })
    });
    const d = await r.json();
    if (d.ok) {
      selectedTcFile = d.tc_file;
      status.textContent = '✅ Sheets 가져오기 완료 (TC ' + (d.tc_count || '?') + '개, 프로젝트: ' + d.project_name + ')';
      await loadProjects();
      document.getElementById('projectSelect').value = d.project_name;
      onProjectSelect();
      showToast('✅ Google Sheets 연동 완료');
    } else {
      status.textContent = '❌ ' + d.error;
    }
  } catch(e) {
    status.textContent = '❌ 오류: ' + e.message;
  }
}

// TC 수정 시작
async function startModify() {
  const projectName = document.getElementById('projectSelect').value;
  const changeDesc  = document.getElementById('changeDesc').value.trim();

  if (!projectName) { alert('수정할 프로젝트를 선택하세요.'); return; }
  if (!changeDesc)   { alert('변경사항 내용을 입력하세요.'); return; }

  document.getElementById('startModifyBtn').disabled = true;
  document.getElementById('card2').classList.remove('hidden');
  setStepBar(2);
  document.getElementById('card2').scrollIntoView({ behavior: 'smooth', block: 'start' });
  document.getElementById('stageLabel').textContent = '수정 파이프라인 시작 중...';

  try {
    const r = await fetch('/start-modify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_name: projectName, change_desc: changeDesc })
    });
    const d = await r.json();
    if (!d.ok) {
      alert('오류: ' + d.error);
      document.getElementById('startModifyBtn').disabled = false;
      return;
    }
    currentSid = d.sid;
    connectStream(d.sid);
  } catch(e) {
    alert('오류: ' + e.message);
    document.getElementById('startModifyBtn').disabled = false;
  }
}

// ── 입력 유형 전환 ──────────────────────────────────────────────────────────────
// ── GitHub 파일 트리 미리보기 ─────────────────────────────────────────────────
async function previewGithubTree(srcId) {
  const urlInput = document.getElementById('srcUrl_' + srcId);
  const panel = document.getElementById('treePanel_' + srcId);
  const url = urlInput ? urlInput.value.trim() : '';
  if (!url) { alert('GitHub URL을 먼저 입력해주세요.'); return; }

  panel.classList.remove('hidden');
  panel.innerHTML = '<div class="tree-loading">⏳ 파일 목록 불러오는 중...</div>';

  try {
    const resp = await fetch('/github-tree', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const data = await resp.json();
    if (!data.ok) {
      panel.innerHTML = '<div class="tree-error">❌ ' + data.error + '</div>';
      return;
    }

    const files = data.files;
    // 폴더별 그룹핑
    const groups = {};
    files.forEach(f => {
      const parts = f.path.split('/');
      const folder = parts.length > 1 ? parts[0] : '(루트)';
      if (!groups[folder]) groups[folder] = [];
      groups[folder].push(f);
    });

    let html = '<div class="tree-header">';
    html += '<strong>' + data.owner + '/' + data.repo + '</strong> (branch: ' + data.branch + ') — 총 ' + files.length + '개 파일';
    html += '<div class="tree-actions">';
    html += '<button type="button" onclick="selectAllTree(' + srcId + ', true)">전체 선택</button> ';
    html += '<button type="button" onclick="selectAllTree(' + srcId + ', false)">전체 해제</button> ';
    html += '<button type="button" class="btn-apply-tree" onclick="applyTreeSelection(' + srcId + ')">✅ 선택 적용</button>';
    html += '</div></div>';
    html += '<div class="tree-list">';

    Object.entries(groups).sort().forEach(([folder, flist]) => {
      html += '<div class="tree-folder">';
      html += '<label class="tree-folder-label"><input type="checkbox" class="folder-cb" data-srcid="' + srcId + '" data-folder="' + folder + '" onchange="toggleFolder(this)"> 📁 ' + folder + ' (' + flist.length + ')</label>';
      flist.forEach(f => {
        const sizeKb = f.size > 0 ? ' <span class="file-size">(' + Math.ceil(f.size/1024) + 'KB)</span>' : '';
        const ext = f.path.split('.').pop().toLowerCase();
        const icon = ext === 'md' ? '📝' : ext === 'pdf' ? '📄' : ext === 'json' ? '{}' : '📄';
        html += '<label class="tree-file-label"><input type="checkbox" class="file-cb" data-srcid="' + srcId + '" data-folder="' + folder + '" value="' + f.path + '"> ' + icon + ' ' + f.path.split('/').pop() + sizeKb + '</label>';
      });
      html += '</div>';
    });

    html += '</div>';
    panel.innerHTML = html;
  } catch(e) {
    panel.innerHTML = '<div class="tree-error">❌ 오류: ' + e.message + '</div>';
  }
}

function toggleFolder(cb) {
  const srcId = cb.dataset.srcid;
  const folder = cb.dataset.folder;
  document.querySelectorAll('.file-cb[data-srcid="' + srcId + '"][data-folder="' + folder + '"]')
    .forEach(fc => fc.checked = cb.checked);
}

function selectAllTree(srcId, checked) {
  document.querySelectorAll('.file-cb[data-srcid="' + srcId + '"], .folder-cb[data-srcid="' + srcId + '"]')
    .forEach(cb => cb.checked = checked);
}

function applyTreeSelection(srcId) {
  const selected = [];
  document.querySelectorAll('.file-cb[data-srcid="' + srcId + '"]:checked')
    .forEach(cb => selected.push(cb.value));

  if (selected.length === 0) { alert('최소 1개 파일을 선택해주세요.'); return; }

  const src = sources.find(s => s.id === srcId);
  if (src) src.selected_files = selected;

  const panel = document.getElementById('treePanel_' + srcId);
  const applyBtn = panel.querySelector('.btn-apply-tree');
  if (applyBtn) applyBtn.textContent = '✅ ' + selected.length + '개 파일 선택됨';
  applyBtn.style.background = 'var(--teal)';
  applyBtn.style.color = '#fff';
}

// ── 다중 소스 관리 ──────────────────────────────────────────────────────────
let sources = [];
let sourceCounter = 0;

function addSource(type) {
  const id = ++sourceCounter;
  sources.push({ id, type, content: '' });
  renderSources();
  if (type === 'url' || type === 'web') {
    setTimeout(() => document.getElementById('srcUrl_' + id)?.focus(), 50);
  } else if (type === 'text') {
    setTimeout(() => document.getElementById('srcText_' + id)?.focus(), 50);
  } else if (type === 'pdf' || type === 'md') {
    setTimeout(() => {
      const zone = document.getElementById('srcZone_' + id);
      if (zone) zone.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 50);
  }
}

function removeSource(id) {
  sources = sources.filter(s => s.id !== id);
  renderSources();
}

function updateSourceContent(id, value) {
  const s = sources.find(s => s.id === id);
  if (s) s.content = value;
}

async function onSrcFileChange(id, input) {
  if (!input.files.length) return;
  const file = input.files[0];
  if (!file.name.toLowerCase().endsWith('.pdf')) { alert('PDF 파일만 허용됩니다.'); return; }
  const zone = document.getElementById('srcZone_' + id);
  if (zone) zone.innerHTML = '⏳ 업로드 중...';
  const fd = new FormData();
  fd.append('file', file);
  try {
    const resp = await fetch('/upload', { method: 'POST', body: fd });
    const data = await resp.json();
    if (data.ok) {
      const s = sources.find(s => s.id === id);
      if (s) s.content = data.filename;
      if (zone) zone.innerHTML = '<span class="src-file-name">✅ ' + data.filename + '</span>';
    } else {
      if (zone) zone.innerHTML = '❌ ' + data.error;
    }
  } catch(e) {
    if (zone) zone.innerHTML = '❌ 업로드 실패';
  }
}

async function onMdFileChange(id, input) {
  if (!input.files.length) return;
  const file = input.files[0];
  const zone = document.getElementById('srcZone_' + id);
  if (zone) zone.innerHTML = '⏳ 업로드 중...';
  const fd = new FormData();
  fd.append('file', file);
  try {
    const resp = await fetch('/upload-md', { method: 'POST', body: fd });
    const data = await resp.json();
    if (data.ok) {
      const s = sources.find(s => s.id === id);
      if (s) s.content = data.filename;
      if (zone) zone.innerHTML = '<span class="src-file-name">✅ ' + data.filename + '</span>';
    } else {
      if (zone) zone.innerHTML = '❌ ' + data.error;
    }
  } catch(e) {
    if (zone) zone.innerHTML = '❌ 업로드 실패';
  }
}

function renderSources() {
  const list  = document.getElementById('sourceList');
  const empty = document.getElementById('sourceEmpty');
  if (!list) return;
  if (sources.length === 0) {
    list.innerHTML = '';
    empty && empty.classList.remove('hidden');
    return;
  }
  empty && empty.classList.add('hidden');
  list.innerHTML = sources.map(src => {
    const badgeClass = src.type;
    const badges = { pdf: '📄 PDF', url: '🔗 GitHub URL', web: '🌐 웹 URL', md: '📝 마크다운', text: '✏️ 텍스트' };
    let body = '';
    if (src.type === 'pdf') {
      body = src.content
        ? '<span class="src-file-name">✅ ' + src.content + '</span>'
        : '<div class="src-dropzone" id="srcZone_' + src.id + '" onclick="document.getElementById(&#39;srcFile_' + src.id + '&#39;).click()">클릭하여 PDF 파일 선택<br><span style="font-size:11px;color:var(--muted)">최대 50MB · PDF만 허용</span></div>';
      body += '<input type="file" id="srcFile_' + src.id + '" accept=".pdf" style="display:none" onchange="onSrcFileChange(' + src.id + ', this)">';
    } else if (src.type === 'url') {
      body = '<input type="text" id="srcUrl_' + src.id + '" class="form-input" placeholder="https://github.com/user/repo" value="' + src.content + '" oninput="updateSourceContent(' + src.id + ', this.value)">';
      body += '<div class="input-hint">GitHub 저장소 URL (private repo는 GITHUB_TOKEN 필요)</div>';
      body += '<button type="button" class="btn-preview-tree" onclick="previewGithubTree(' + src.id + ')">🗂 파일 목록 보기</button>';
      body += '<div id="treePanel_' + src.id + '" class="tree-panel hidden"></div>';
    } else if (src.type === 'web') {
      body = '<input type="text" id="srcUrl_' + src.id + '" class="form-input" placeholder="https://example.com 또는 https://app.vercel.app" value="' + src.content + '" oninput="updateSourceContent(' + src.id + ', this.value)">';
      body += '<div class="input-hint">웹 서비스, 랜딩 페이지, Vercel 배포 URL 등 — HTML을 크롤링하여 분석합니다</div>';
    } else if (src.type === 'md') {
      body = src.content
        ? '<span class="src-file-name">✅ ' + src.content + '</span>'
        : '<div class="src-dropzone" id="srcZone_' + src.id + '" onclick="document.getElementById(&#39;srcFile_' + src.id + '&#39;).click()">클릭하여 마크다운 파일 선택<br><span style="font-size:11px;color:var(--muted)">.md 파일</span></div>';
      body += '<input type="file" id="srcFile_' + src.id + '" accept=".md,.markdown,.txt" style="display:none" onchange="onMdFileChange(' + src.id + ', this)">';
    } else {
      body = '<textarea id="srcText_' + src.id + '" class="form-input text-input-area" placeholder="기획서 내용, 슬랙 메시지 등 자유롭게 붙여넣으세요..." oninput="updateSourceContent(' + src.id + ', this.value)">' + src.content + '</textarea>';
    }
    return '<div class="source-card">' +
      '<div class="source-card-header">' +
        '<span class="source-type-badge ' + badgeClass + '">' + badges[src.type] + '</span>' +
        '<button type="button" class="btn-remove-source" onclick="removeSource(' + src.id + ')">✕ 삭제</button>' +
      '</div>' +
      '<div class="source-card-body">' + body + '</div>' +
      '</div>';
  }).join('');
}

async function startPipeline() {
  const projectName = document.getElementById('projectName').value.trim() || '프로젝트';
  const focusArea = document.getElementById('focusArea').value.trim();

  if (sources.length === 0) { alert('소스를 하나 이상 추가해주세요.'); return; }

  const typeNames = { pdf: 'PDF', url: 'GitHub URL', web: '웹 URL', md: '마크다운', text: '텍스트' };
  for (const s of sources) {
    if (!s.content.trim()) {
      alert(typeNames[s.type] + ' 소스의 내용을 입력해주세요.');
      return;
    }
  }

  const payload = sources.map(s => ({ type: s.type, content: s.content, selected_files: s.selected_files || null }));

  document.getElementById('startBtn').disabled = true;
  document.getElementById('card2').classList.remove('hidden');
  setStepBar(2);
  document.getElementById('card2').scrollIntoView({ behavior: 'smooth', block: 'start' });

  try {
    const resp = await fetch('/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sources: payload, project_name: projectName, focus_area: focusArea || null })
    });
    const data = await resp.json();
    if (!data.ok) {
      alert('오류: ' + data.error);
      document.getElementById('startBtn').disabled = false;
      return;
    }
    currentSid = data.sid;
    connectStream(data.sid);
  } catch(e) {
    alert('서버 오류: ' + e.message);
    document.getElementById('startBtn').disabled = false;
  }
}

function connectStream(sid) {
  // 이전 중단 배너 제거
  document.querySelectorAll('.stopped-banner').forEach(el => el.remove());
  eventSource = new EventSource('/stream/' + sid);
  eventSource.onmessage = (e) => {
    try {
      const evt = JSON.parse(e.data);
      handleEvent(evt);
    } catch(err) {}
  };
  eventSource.onerror = () => {
    addLog('⚠️ SSE 연결 오류. 재연결 시도...', true);
  };
}

function handleEvent(evt) {
  if (evt.type === 'ping') return;

  if (evt.type === 'stage') {
    const { stage, label, pct } = evt.data;
    updateProgress(label, pct);
    updateSubsteps(stage);
    if (stage >= 4) {
      document.getElementById('tcStageLabel').textContent = label;
      document.getElementById('tcProgressBar').style.width = pct + '%';
      // TC 단계 진입 시 상단 카드 간략화 — 프로그레스바+로그+버튼 숨김
      document.getElementById('logBox').style.display = 'none';
      document.getElementById('stopBtn2').style.display = 'none';
      document.getElementById('progressBar').parentElement.style.display = 'none';
      document.querySelector('#card2 .substeps').style.display = 'none';
    }
    setStepBar(stage);
  }

  if (evt.type === 'log') {
    // TC 생성 단계(card4 보이면)에서는 하단에만 로그 표시
    const card4 = document.getElementById('card4');
    if (!card4.classList.contains('hidden')) {
      addTcLog(evt.data.msg);
    } else {
      addLog(evt.data.msg);
    }
  }

  if (evt.type === 'gate') {
    const isModify = evt.data.mode === 'modify';
    window._gateMode = isModify ? 'modify' : 'new';
    // 제목/안내문 전환
    document.getElementById('gateTitle').innerHTML = isModify
      ? '📋 영향도 검토 <span class="badge">Step 3 · Human Gate</span>'
      : '🔍 분류표 검토 <span class="badge">Step 3 · Human Gate</span>';
    document.getElementById('gateInfoBox').innerHTML = isModify
      ? 'AI가 분석한 변경 영향도입니다. 채팅으로 수정을 요청하고, 우측 Viewer에서 확인한 뒤 승인하세요.'
      : 'AI가 생성한 분류표입니다. 채팅으로 수정을 요청하고, 우측 Viewer에서 확인한 뒤 승인하세요.';
    initGateChat(evt.data.content);
    renderDomainChecklist(evt.data.content);
    document.getElementById('card3').classList.remove('hidden');
    setStepBar(3);
    document.getElementById('card3').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  if (evt.type === 'done') {
    stopCountdown();
    const { filename, size, sid, total_tc, min_tc } = evt.data;
    currentFilename = filename;
    document.getElementById('card4').classList.add('hidden');
    document.getElementById('card5').classList.remove('hidden');
    document.getElementById('resultFilename').textContent = filename;
    document.getElementById('resultMeta').textContent =
      `${(size / 1024).toFixed(1)} KB`;
    document.getElementById('statTotal').textContent = total_tc;
    document.getElementById('statMin').textContent = min_tc;
    setStepBar(5);
    setStopButtonsDisabled(true);
    document.getElementById('card5').scrollIntoView({ behavior: 'smooth', block: 'start' });
    showToast('🎉 TC 생성 완료!');
    if (eventSource) eventSource.close();
  }

  if (evt.type === 'stopped') {
    stopCountdown();
    setStopButtonsDisabled(true);
    ['card2', 'card3', 'card4'].forEach(id => {
      const card = document.getElementById(id);
      if (!card.classList.contains('hidden')) {
        const banner = document.createElement('div');
        banner.className = 'stopped-banner';
        banner.innerHTML = '<div class="stopped-icon">⏹</div><div><div class="stopped-msg">파이프라인이 중단되었습니다.</div><div class="stopped-sub">새 작업을 시작하려면 위 버튼을 눌러주세요.</div></div>';
        card.appendChild(banner);
      }
    });
    document.getElementById('startBtn').disabled = false;
    document.getElementById('startModifyBtn').disabled = false;
    setStepBar(1);
    showToast('⏹ 파이프라인이 중단되었습니다.', 'error');
    if (eventSource) eventSource.close();
  }

  if (evt.type === 'error') {
    stopCountdown();
    setStopButtonsDisabled(true);
    addLog('❌ 오류: ' + evt.data.msg, true);
    document.getElementById('stageLabel').textContent = '오류 발생';
    document.getElementById('startBtn').disabled = false;
    if (eventSource) eventSource.close();
    // 오류 배너 + 재시작 버튼
    var card2 = document.getElementById('card2');
    var existing = card2.querySelector('.error-banner');
    if (existing) existing.remove();
    var banner = document.createElement('div');
    banner.className = 'error-banner';
    banner.style.cssText = 'background:#FEF2F2;border:1.5px solid #FECACA;border-radius:10px;padding:14px 18px;margin-top:14px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;';
    banner.innerHTML = '<div style="font-size:24px;">⚠️</div>' +
      '<div style="flex:1;"><div style="font-size:13px;font-weight:600;color:#991B1B;">오류가 발생했습니다</div>' +
      '<div style="font-size:12px;color:#666;margin-top:2px;">' + (evt.data.msg || '').substring(0, 100) + '</div></div>' +
      '<button onclick="retryPipeline()" style="padding:8px 16px;background:#2563EB;color:#fff;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;white-space:nowrap;">🔄 이어서 재시작</button>' +
      '<button onclick="restartFromScratch()" style="padding:8px 14px;background:#fff;color:#1D4ED8;border:1.5px solid #93C5FD;border-radius:8px;font-size:12px;cursor:pointer;white-space:nowrap;">처음부터 시작</button>';
    card2.appendChild(banner);
  }

  if (evt.type === 'error_recovery') {
    setStopButtonsDisabled(true);
    if (eventSource) eventSource.close();
    const d = evt.data;
    document.getElementById('recoveryErrorMsg').textContent = '오류: ' + d.error;
    const resumeBtn = document.getElementById('btnResume');
    const cpInfo = document.getElementById('recoveryCheckpointInfo');
    if (d.has_checkpoint) {
      resumeBtn.style.display = 'block';
      cpInfo.classList.remove('hidden');
      cpInfo.innerHTML = '💾 저장된 체크포인트<br>프로젝트: <strong>' + d.checkpoint_project +
        '</strong><br>단계: ' + d.checkpoint_stage + '<br>저장 시각: ' + d.checkpoint_saved_at;
    } else {
      resumeBtn.style.display = 'none';
      cpInfo.classList.add('hidden');
    }
    document.getElementById('recovery-modal').classList.add('open');
  }
}

let _countdownTimer = null;
let _countdownSec = 0;

function stopCountdown() {
  if (_countdownTimer) { clearInterval(_countdownTimer); _countdownTimer = null; }
  var el = document.getElementById('countdownLabel');
  if (el) el.textContent = '';
}

function startCountdown(seconds) {
  if (_countdownTimer) clearInterval(_countdownTimer);
  _countdownSec = seconds;
  _countdownTimer = setInterval(function() {
    _countdownSec--;
    if (_countdownSec <= 0) {
      clearInterval(_countdownTimer);
      _countdownTimer = null;
      var el = document.getElementById('countdownLabel');
      if (el) el.textContent = '';
      return;
    }
    var min = Math.floor(_countdownSec / 60);
    var sec = _countdownSec % 60;
    var text = min > 0 ? min + '분 ' + sec + '초' : sec + '초';
    var el = document.getElementById('countdownLabel');
    if (el) el.textContent = '  (약 ' + text + ' 후 완료)';
  }, 1000);
}

function updateProgress(label, pct) {
  document.getElementById('stageLabel').textContent = label + ' (' + pct + '%)';
  document.getElementById('progressBar').style.width = pct + '%';
  // 단계별 예상 시간 카운트다운
  var estimates = {5: 20, 15: 30, 25: 50, 38: 30, 50: 90, 82: 20, 90: 15};
  var estSec = estimates[pct];
  if (estSec) startCountdown(estSec);
}

function updateSubsteps(stage) {
  const map = {1: 'sub1', 2: 'sub2', 3: 'sub2', 4: 'sub3'};
  ['sub1','sub2','sub3','sub4'].forEach(id => {
    const el = document.getElementById(id);
    el.classList.remove('active','done');
  });
  // 파싱=1→sub1, 정책/기능/분류=2→sub2/sub3/sub4
  if (stage >= 1) document.getElementById('sub1').classList.add('done');
  if (stage >= 2) document.getElementById('sub2').classList.add('active');
}

function addLog(msg, isError=false) {
  const box = document.getElementById('logBox');
  const line = document.createElement('div');
  line.className = 'log-line' + (isError ? ' error' : '');
  line.textContent = '[' + new Date().toLocaleTimeString() + '] ' + msg;
  box.appendChild(line);
  box.scrollTop = box.scrollHeight;
}

function addTcLog(msg) {
  const box = document.getElementById('tcLogBox');
  const line = document.createElement('div');
  line.className = 'log-line';
  line.textContent = '[' + new Date().toLocaleTimeString() + '] ' + msg;
  box.appendChild(line);
  box.scrollTop = box.scrollHeight;
}

// ── 도메인 체크리스트 ─────────────────────────────────────────────────────────
function parseDomains(text) {
  const domains = [];
  // "## 대분류: 이름 (코드)" 패턴
  const re = /##\s+대분류[:\s]+([^\(]+?)\s*[\(\（]([A-Z]{2,8})[\)\）]/gm;
  let m;
  while ((m = re.exec(text)) !== null) {
    domains.push({ name: m[1].trim(), code: m[2].trim() });
  }
  // 패턴 없으면 "## " 헤딩에서 코드 추출
  if (domains.length === 0) {
    const re2 = /^##\s+(.+)/gm;
    while ((m = re2.exec(text)) !== null) {
      const cm = m[1].match(/[\(\（]([A-Z]{2,8})[\)\）]/);
      if (cm) {
        const name = m[1].replace(/\s*[\(\（][A-Z]{2,8}[\)\）]/, '').trim();
        domains.push({ name, code: cm[1] });
      }
    }
  }
  return domains;
}

function renderDomainChecklist(content) {
  const domains = parseDomains(content);
  const container = document.getElementById('domainChecklist');
  container.innerHTML = '';
  if (domains.length === 0) {
    container.innerHTML = '<span style="font-size:12px;color:var(--muted)">도메인을 자동으로 인식하지 못했습니다. 전체 생성됩니다.</span>';
    return;
  }
  domains.forEach(d => {
    const label = document.createElement('label');
    label.className = 'domain-chip checked';
    label.innerHTML = '<input type="checkbox" checked value="' + d.code + '"><span class="chip-dot"></span>' + d.code + ' · ' + d.name;
    label.querySelector('input').addEventListener('change', function() {
      label.classList.toggle('checked', this.checked);
    });
    container.appendChild(label);
  });
}

function selectAllDomains(checked) {
  document.querySelectorAll('#domainChecklist input[type=checkbox]').forEach(cb => {
    cb.checked = checked;
    cb.closest('.domain-chip').classList.toggle('checked', checked);
  });
}

function getSelectedDomains() {
  const checked = [...document.querySelectorAll('#domainChecklist input[type=checkbox]:checked')];
  if (checked.length === 0) return null; // 아무것도 없으면 null → 전체로 처리
  const all = document.querySelectorAll('#domainChecklist input[type=checkbox]');
  if (checked.length === all.length) return null; // 전체 선택이면 null (필터 없음)
  return checked.map(cb => cb.value);
}

async function exportGateExcel() {
  const content = document.getElementById('gateContent').value.trim();
  if (!content) { alert('분류표 내용이 없습니다.'); return; }
  showToast('📥 Excel 생성 중...');
  try {
    const r = await fetch('/export-gate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, mode: window._gateMode || 'new' })
    });
    if (!r.ok) { showToast('❌ Excel 생성 실패', 'error'); return; }
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'gate_review.xlsx';
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('✅ Excel 다운로드 완료!');
  } catch(e) {
    showToast('❌ 오류: ' + e.message, 'error');
  }
}

// ── Human Gate 채팅 ──────────────────────────────────────────────────────────
let gateChatHistory = [];  // [{role, content}, ...]

function initGateChat(docContent) {
  // 문서 저장
  document.getElementById('gateContent').value = docContent;
  // Viewer 렌더링
  renderGateViewer(docContent);
  // 채팅 초기화
  gateChatHistory = [];
  const msgs = document.getElementById('gateChatMessages');
  msgs.innerHTML = '';
  addGateChatMsg('assistant',
    'AI가 문서를 준비했습니다. 수정이 필요한 부분을 채팅으로 알려주세요. ' +
    '예) "AUTH 도메인의 비밀번호 변경 케이스 삭제해줘" / "PROD 도메인 이름을 상품관리로 바꿔줘"');
  document.getElementById('gateChatInput').focus();
}

function mdToHtml(md) {
  // 라인 단위 마크다운 → HTML (Python 문자열 호환 — 백슬래시 최소화)
  const lines = md.split('\\n');
  let out = [];
  let inList = false;
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i]
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    // 헤딩
    if (line.startsWith('#### ')) {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push('<h4 style="font-size:13px;font-weight:600;margin:8px 0 3px;">' + line.slice(5) + '</h4>');
    } else if (line.startsWith('### ')) {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push('<h3>' + line.slice(4) + '</h3>');
    } else if (line.startsWith('## ')) {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push('<h2>' + line.slice(3) + '</h2>');
    } else if (line.startsWith('# ')) {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push('<h2 style="font-size:16px;">' + line.slice(2) + '</h2>');
    } else if (line.startsWith('> ')) {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push('<blockquote>' + line.slice(2) + '</blockquote>');
    } else if (line.match(/^[-*] /) || line.match(/^\d+\. /)) {
      if (!inList) { out.push('<ul>'); inList = true; }
      const txt = line.replace(/^[-*] /, '').replace(/^\d+\. /, '');
      out.push('<li>' + txt + '</li>');
    } else if (line.trim() === '') {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push('<br>');
    } else {
      if (inList) { out.push('</ul>'); inList = false; }
      out.push('<p style="margin:3px 0;">' + line + '</p>');
    }
  }
  if (inList) out.push('</ul>');
  // 인라인: **bold**, `code`
  let html = out.join('');
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  return html;
}

function extractCategorySummary(mdText) {
  // 분류표에서 대분류/중분류/소분류 구조 추출
  var lines = mdText.split('\\n');
  var suites = [];
  var curMajor = '';
  var curMiddles = [];
  var curMinors = [];
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (line.startsWith('## ') && !line.startsWith('### ')) {
      if (curMajor) suites.push({ major: curMajor, middles: curMiddles, minors: curMinors });
      curMajor = line.replace(/^##\s+/, '').replace(/\*\*/g, '');
      curMiddles = [];
      curMinors = [];
    } else if (line.startsWith('### ')) {
      curMiddles.push(line.replace(/^###\s+/, '').replace(/\*\*/g, ''));
    } else if (line.startsWith('#### ')) {
      curMinors.push(line.replace(/^####\s+/, '').replace(/\*\*/g, ''));
    } else if ((line.startsWith('- ') || line.startsWith('* ')) && curMinors.length === 0 && curMiddles.length > 0) {
      var txt = line.replace(/^[-*]\s+/, '');
      if (txt.length < 40) curMinors.push(txt);
    }
  }
  if (curMajor) suites.push({ major: curMajor, middles: curMiddles, minors: curMinors });
  return suites;
}

function updateTcIdPreview(input) {
  var code = input.value.trim().toUpperCase();
  var pcode = input.dataset.pcode || 'SC';
  var idx = input.dataset.domain;
  var preview = document.getElementById('tcIdPreview_' + idx);
  if (preview) {
    preview.textContent = code ? pcode + '-' + code + '-001' : '-';
  }
}

function renderGateViewer(mdText) {
  var viewer = document.getElementById('gateViewer');
  // 분류 요약 카드
  var cats = extractCategorySummary(mdText);
  var summaryHtml = '';
  if (cats.length > 0) {
    var _pcode = (document.getElementById('projectName').value || '').toLowerCase().indexOf('mobile') >= 0 ? 'SM' : 'SC';
    summaryHtml = '<div style="background:#F0F9FF;border:1.5px solid #93C5FD;border-radius:10px;padding:14px 16px;margin-bottom:16px;">';
    summaryHtml += '<div style="font-size:14px;font-weight:700;color:#1E3A5F;margin-bottom:4px;">TC 분류 요약</div>';
    summaryHtml += '<div style="font-size:12px;color:#4B5563;margin-bottom:10px;">각 도메인의 <strong>SuiteCode</strong>를 입력하세요. 순번(001, 002...)은 자동 생성됩니다.<br>예: SuiteCode에 <code style="background:#DBEAFE;padding:1px 4px;border-radius:3px;">GNBF</code> 입력 → TC ID: <code style="background:#DBEAFE;padding:1px 4px;border-radius:3px;">' + _pcode + '-GNBF-001</code>, <code style="background:#DBEAFE;padding:1px 4px;border-radius:3px;">' + _pcode + '-GNBF-002</code> ...</div>';
    summaryHtml += '<table style="width:100%;border-collapse:collapse;font-size:12px;">';
    summaryHtml += '<tr style="background:#DBEAFE;"><th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;">시트명</th><th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;">SuiteCode</th><th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;">TC ID 미리보기</th><th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;">대분류</th><th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;">중분류</th><th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;">소분류</th></tr>';
    for (var ci = 0; ci < cats.length; ci++) {
      var c = cats[ci];
      var majorClean = c.major.replace(/대분류[:\s]*/g, '').replace(/\(.*?\)/g, '').trim();
      var firstMid = c.middles.length > 0 ? c.middles[0].replace(/중분류[:\s]*/g, '').replace(/\(.*?\)/g, '').trim() : '';
      var sheetName = firstMid ? majorClean + '-' + firstMid : majorClean;
      var autoCode = majorClean.replace(/[^A-Za-z]/g, '').toUpperCase().substring(0, 4);
      if (firstMid) autoCode += '-' + firstMid.replace(/[^A-Za-z]/g, '').toUpperCase().substring(0, 4);
      var midText = c.middles.length > 0 ? c.middles.join(', ') : '-';
      var minText = c.minors.length > 0 ? c.minors.join(', ') : '-';
      var bg = ci % 2 === 0 ? '#F8FAFC' : '#FFFFFF';
      var previewId = _pcode + '-' + autoCode + '-001';
      summaryHtml += '<tr style="background:' + bg + ';">';
      summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;font-weight:600;">' + sheetName + '</td>';
      summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;"><input type="text" class="suite-code-input" data-domain="' + ci + '" data-pcode="' + _pcode + '" value="' + autoCode + '" placeholder="예: GNBF" oninput="updateTcIdPreview(this)" style="width:80px;padding:4px 6px;border:1.5px solid #93C5FD;border-radius:4px;font-size:12px;font-weight:700;text-transform:uppercase;font-family:monospace;"></td>';
      summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;font-family:monospace;font-size:11px;color:#1D4ED8;" id="tcIdPreview_' + ci + '">' + previewId + '</td>';
      summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;">' + majorClean + '</td>';
      summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;">' + midText + '</td>';
      summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;color:#666;">' + minText + '</td>';
      summaryHtml += '</tr>';
    }
    summaryHtml += '</table>';
    summaryHtml += '</div>';
  }
  viewer.innerHTML = summaryHtml + mdToHtml(mdText);
  viewer.classList.add('gate-doc-updated');
  setTimeout(() => viewer.classList.remove('gate-doc-updated'), 700);
  var badge = document.getElementById('gateViewerBadge');
  if (badge) {
    badge.textContent = '최근 업데이트: ' + new Date().toLocaleTimeString();
  }
}

function addGateChatMsg(role, text) {
  const msgs = document.getElementById('gateChatMessages');
  const div = document.createElement('div');
  div.className = 'gate-msg ' + role;
  div.textContent = text;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

async function sendGateChat() {
  const input = document.getElementById('gateChatInput');
  const sendBtn = document.getElementById('gateChatSend');
  const msg = input.value.trim();
  if (!msg || !currentSid) return;

  input.value = '';
  sendBtn.disabled = true;
  addGateChatMsg('user', msg);

  // 로딩 메시지
  const loadingDiv = document.createElement('div');
  loadingDiv.className = 'gate-msg assistant';
  loadingDiv.textContent = '⏳ 분석 중...';
  loadingDiv.id = 'gateLoadingMsg';
  document.getElementById('gateChatMessages').appendChild(loadingDiv);
  document.getElementById('gateChatMessages').scrollTop = 999999;

  const currentDoc = document.getElementById('gateContent').value;

  try {
    const r = await fetch('/gate-chat/' + currentSid, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: msg,
        current_doc: currentDoc,
        gate_mode: window._gateMode || 'new',
        history: gateChatHistory.slice(-6)  // 최근 6턴만 전송
      })
    });
    const d = await r.json();

    // 로딩 제거
    document.getElementById('gateLoadingMsg')?.remove();

    if (d.ok) {
      addGateChatMsg('assistant', d.reply);
      // 문서 업데이트
      document.getElementById('gateContent').value = d.updated_doc;
      renderGateViewer(d.updated_doc);
      renderDomainChecklist(d.updated_doc);
      // 히스토리 추가 (컨텍스트 유지용 — 축약 버전)
      gateChatHistory.push({ role: 'user', content: '요청: ' + msg });
      gateChatHistory.push({ role: 'assistant', content: d.reply });
      // 변경 알림
      addGateChatMsg('system', '✅ 문서가 업데이트되었습니다. 우측 Viewer에서 확인하세요.');
    } else {
      document.getElementById('gateLoadingMsg')?.remove();
      addGateChatMsg('system', '❌ 오류: ' + d.error);
    }
  } catch(e) {
    document.getElementById('gateLoadingMsg')?.remove();
    addGateChatMsg('system', '❌ 네트워크 오류: ' + e.message);
  }
  sendBtn.disabled = false;
  input.focus();
}

async function regenerateClassification() {
  if (!currentSid) return;
  if (!confirm('분류표를 처음부터 다시 생성합니다. 현재 분류표는 삭제됩니다. 계속할까요?')) return;
  try {
    // 현재 파이프라인 중단
    await fetch('/stop/' + currentSid, { method: 'POST' });
    if (eventSource) eventSource.close();
    // 분류표 재생성 요청
    const projectName = document.getElementById('projectName').value.trim() || selectedProject || '';
    const focusArea = document.getElementById('focusArea').value.trim();
    document.getElementById('card3').classList.add('hidden');
    document.getElementById('card2').classList.remove('hidden');
    setStepBar(2);
    document.getElementById('card2').scrollIntoView({ behavior: 'smooth', block: 'start' });
    document.getElementById('stageLabel').textContent = '분류표 재생성 중...';
    const r = await fetch('/regenerate-classification', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_name: projectName, focus_area: focusArea || null })
    });
    const d = await r.json();
    if (!d.ok) { alert(d.error); return; }
    currentSid = d.sid;
    showToast('분류표를 다시 생성합니다.');
    connectStream(d.sid);
  } catch(e) {
    alert('오류: ' + e.message);
  }
}

async function approveGate() {
  if (!currentSid) return;
  const content = document.getElementById('gateContent').value.trim();
  if (!content) { alert('내용이 비어있습니다.'); return; }

  // SuiteCode 수집
  var suiteCodeInputs = document.querySelectorAll('.suite-code-input');
  var suiteCodes = {};
  var hasEmpty = false;
  suiteCodeInputs.forEach(function(input) {
    var code = input.value.trim().toUpperCase();
    if (!code) hasEmpty = true;
    suiteCodes[input.dataset.domain] = code;
  });
  if (suiteCodeInputs.length > 0 && hasEmpty) {
    alert('모든 도메인의 SuiteCode를 입력해주세요.'); return;
  }
  // SuiteCode 목록 (순서대로)
  var suiteCodeList = [];
  for (var i = 0; i < suiteCodeInputs.length; i++) {
    suiteCodeList.push(suiteCodeInputs[i].value.trim().toUpperCase());
  }

  // 선택된 도메인 수집
  const selectedDomains = getSelectedDomains();
  const allCount = document.querySelectorAll('#domainChecklist input[type=checkbox]').length;
  const selCount = selectedDomains ? selectedDomains.length : allCount;

  if (selectedDomains && selectedDomains.length === 0) {
    alert('TC를 생성할 도메인을 하나 이상 선택하세요.'); return;
  }

  const approveBtn = document.querySelector('#card3 .btn-success');
  approveBtn.disabled = true;
  approveBtn.textContent = '⏳ 처리 중...';

  var codeMsg = suiteCodeList.length > 0 ? ' (SuiteCode: ' + suiteCodeList.join(', ') + ')' : '';
  const scopeMsg = selectedDomains
    ? selCount + '개 도메인 범위로 TC를 생성합니다.' + codeMsg + ' 계속할까요?'
    : '전체 도메인(' + allCount + '개)으로 TC를 생성합니다.' + codeMsg + ' 계속할까요?';
  if (!confirm(scopeMsg)) {
    approveBtn.disabled = false;
    approveBtn.textContent = '✅ 승인 및 TC 생성 시작';
    return;
  }

  try {
    const resp = await fetch('/approve/' + currentSid, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, selected_domains: selectedDomains, suite_codes: suiteCodeList })
    });
    const data = await resp.json();
    if (data.ok) {
      document.getElementById('card3').classList.add('hidden');
      document.getElementById('card4').classList.remove('hidden');
      const label = selectedDomains ? selCount + '개 도메인 TC 작성 중...' : 'TC 작성 중...';
      document.getElementById('tcStageLabel').textContent = label;
      setStepBar(4);
      document.getElementById('card4').scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      alert('승인 오류: ' + data.error);
      approveBtn.disabled = false;
      approveBtn.textContent = '✅ 승인 및 TC 생성 시작';
    }
  } catch(e) {
    alert('오류: ' + e.message);
    approveBtn.disabled = false;
    approveBtn.textContent = '✅ 승인 및 TC 생성 시작';
  }
}

function setStepBar(active) {
  for (let i = 1; i <= 5; i++) {
    const el = document.getElementById('stepBar' + i);
    el.classList.remove('active', 'done');
    if (i < active) el.classList.add('done');
    else if (i === active) el.classList.add('active');
  }
}

async function stopPipeline() {
  if (!currentSid) return;
  if (!confirm('파이프라인을 중단할까요? 현재 단계가 끝난 직후 멈춥니다.')) return;
  setStopButtonsDisabled(true);
  try {
    await fetch('/stop/' + currentSid, { method: 'POST' });
    showToast('⏹ 중단 요청을 보냈습니다...', 'error');
  } catch(e) {
    showToast('❌ 중단 요청 실패: ' + e.message, 'error');
    setStopButtonsDisabled(false);
  }
}

function setStopButtonsDisabled(disabled) {
  ['stopBtn2', 'stopBtn3', 'stopBtn4'].forEach(id => {
    const btn = document.getElementById(id);
    if (btn) btn.disabled = disabled;
  });
}

function downloadFile() {
  if (!currentSid || !currentFilename) return;
  window.location.href = '/download/' + currentSid + '/' + encodeURIComponent(currentFilename);
  showToast('⬇ 다운로드 시작!');
}

async function openFolder() {
  await fetch('/open-folder', { method: 'POST' });
  showToast('📁 폴더를 열었습니다');
}

const DRIVE_SVG = `<svg width="16" height="16" viewBox="0 0 87.3 78" xmlns="http://www.w3.org/2000/svg"><path d="m6.6 66.85 3.85 6.65c.8 1.4 1.95 2.5 3.3 3.3l13.75-23.8h-27.5c0 1.55.4 3.1 1.2 4.5z" fill="#0066da"/><path d="m43.65 25-13.75-23.8c-1.35.8-2.5 1.9-3.3 3.3l-25.4 44a9.06 9.06 0 0 0-1.2 4.5h27.5z" fill="#00ac47"/><path d="m73.55 76.8c1.35-.8 2.5-1.9 3.3-3.3l1.6-2.75 7.65-13.25c.8-1.4 1.2-2.95 1.2-4.5h-27.502l5.852 11.5z" fill="#ea4335"/><path d="m43.65 25 13.75-23.8c-1.35-.8-2.9-1.2-4.5-1.2h-18.5c-1.6 0-3.15.45-4.5 1.2z" fill="#00832d"/><path d="m59.8 53h-32.3l-13.75 23.8c1.35.8 2.9 1.2 4.5 1.2h50.8c1.6 0 3.15-.45 4.5-1.2z" fill="#2684fc"/><path d="m73.4 26.5-12.7-22c-.8-1.4-1.95-2.5-3.3-3.3l-13.75 23.8 16.15 27h27.45c0-1.55-.4-3.1-1.2-4.5z" fill="#ffba00"/></svg>`;

async function uploadToDrive() {
  if (!currentFilename) return;
  const btn = document.getElementById('driveBtn');
  btn.disabled = true;
  btn.innerHTML = '⏳ 업로드 중...';
  showToast('☁️ Google Drive에 업로드 중...');
  try {
    const r = await fetch('/upload-to-drive', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sid: currentSid, filename: currentFilename })
    });
    const d = await r.json();
    if (d.ok) {
      showToast('✅ Google Drive 업로드 완료!');
      btn.innerHTML = DRIVE_SVG + ' Drive 업로드 완료';
      btn.style.borderColor = '#34a853';
      if (d.link) window.open(d.link, '_blank');
      return;
    } else if (d.need_credentials) {
      openDriveModal();
      showToast('🔑 Drive 연동 설정이 필요합니다', 'error');
      btn.innerHTML = '⚠️ Drive 연동 설정 필요';
      btn.style.borderColor = '#e53e3e';
      btn.style.color = '#e53e3e';
    } else {
      showToast('❌ ' + d.error, 'error');
      btn.innerHTML = DRIVE_SVG + ' Google Drive에 올리기';
    }
  } catch(e) {
    showToast('❌ 오류: ' + e.message, 'error');
    btn.innerHTML = DRIVE_SVG + ' Google Drive에 올리기';
  }
  btn.disabled = false;
}

function openDriveModal() { document.getElementById('drive-modal').classList.add('open'); }
function closeDriveModal() { document.getElementById('drive-modal').classList.remove('open'); }
function closeRecoveryModal() {
  document.getElementById('recovery-modal').classList.remove('open');
  fetch('/checkpoint', { method: 'DELETE' });  // 종료 선택 시 체크포인트 삭제
}

async function restartModify(mode) {
  document.getElementById('recovery-modal').classList.remove('open');
  const projectName = document.getElementById('projectSelect').value;
  const changeDesc  = document.getElementById('changeDesc')?.value?.trim() || '';
  document.getElementById('card2').classList.remove('hidden');
  setStepBar(2);
  document.getElementById('card2').scrollIntoView({ behavior: 'smooth', block: 'start' });
  try {
    const r = await fetch('/restart-modify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode, project_name: projectName, change_desc: changeDesc })
    });
    const d = await r.json();
    if (!d.ok) { alert('❌ ' + d.error); return; }
    currentSid = d.sid;
    showToast(mode === 'resume' ? '🔄 체크포인트에서 재시작합니다.' : '▶ 처음부터 재시작합니다.');
    connectStream(d.sid);
  } catch(e) {
    alert('재시작 오류: ' + e.message);
  }
}
document.getElementById('drive-modal').addEventListener('click', e => {
  if (e.target === e.currentTarget) closeDriveModal();
});

function showToast(msg, type = 'success') {
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = type; t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 3000);
}
</script>
</body>
</html>
"""


# ── 진입점 ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print(f"🚀 TC 자동화 v2 시작: http://localhost:{PORT}")
    print(f"   BASE_DIR   : {BASE_DIR}")
    print(f"   AGENT_DIR  : {AGENT_DIR}")
    print(f"   BUILD_EXCEL: {BUILD_EXCEL} {'✓' if BUILD_EXCEL.exists() else '✗ (없음)'}")
    print(f"   RULES_FILE : {RULES_FILE} {'✓' if RULES_FILE.exists() else '✗ (없음)'}")
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        print(f"   API KEY    : sk-ant-...{api_key[-6:]} (설정됨)")
    else:
        print("   API KEY    : ⚠️  미설정 — .env 파일을 확인하세요")
    # 샘플 PDF 사전 생성 (없을 때만)
    try:
        sp = build_sample_pdf()
        if sp:
            print(f"   SAMPLE PDF : {sp.name} ✓")
        else:
            print("   SAMPLE PDF : ⚠️  생성 실패 (fpdf2 확인)")
    except Exception as _e:
        print(f"   SAMPLE PDF : ⚠️  {_e}")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
