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
# Windows 메모장 저장 시 BOM이 붙을 수 있어 utf-8-sig 사용 (없으면 무해).
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        key, val = k.strip(), v.strip()
        # 값이 "..." 또는 '...'로 감싸져 있으면 벗겨내기 (Windows 사용자 흔한 실수 방어)
        if len(val) >= 2 and ((val[0] == val[-1] == '"') or (val[0] == val[-1] == "'")):
            val = val[1:-1]
        if key and not os.environ.get(key):
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

# ── 앱 버전 (단일 소스 — 여기 한 곳만 수정하면 UI 배지/배너/모달/JS 상수 모두 자동 반영) ──
APP_VERSION         = "v0.10.0"
APP_VERSION_DATE    = "2026-05-07"
APP_VERSION_TAGLINE = "구조화 spec 폴더 모드 + UI 정식화 + 화면별 정밀 TC"
# 릴리즈 요약 — UI 배너/모달용 (4~5줄 권장)
APP_VERSION_HIGHLIGHTS = [
    "📁 구조화 spec 폴더 모드 — overview/policy/design/scr 분리 폴더 1개로 화면별 정밀 TC (분류 LLM 호출 0회)",
    "🔄 버전 diff 모드 — 이전 폴더 대비 변경/추가 SCR 만 재생성 (비용 76% 절감 가능)",
    "🎯 분류표 계층 정상화 — 대분류>중분류(화면)>소분류(세부 시나리오) + SCR md 본문에서 자동 추출",
    "✨ Step 1 UI 정식화 — 구조화 spec 우선 / 개별 소스는 임시 작업용 아코디언으로 분리 + 최근 사용 폴더 드롭다운",
    "🛠 다수 안정화 — TC 갯수 정상화, focus_area SCR 일괄/범위 인식, Excel 너비 1.4배·구분 행·줄바꿈 정리",
]

WORKSPACE_ROOT.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
SPECS_DIR.mkdir(exist_ok=True)
TC_FILES_DIR.mkdir(exist_ok=True)

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
        "selected_domains": None,  # None=전체, list=선택된 대분류 코드
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
            data = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
        # 이름이 비어있는 유령 레코드 자동 필터 (과거 버그로 남은 데이터 방어)
        return [p for p in data if isinstance(p, dict) and (p.get("name") or "").strip()]
    return []

def save_project(project_name: str, tc_file: str = "", excel_file: str = "", **extra):
    # 빈 이름 저장 방지 — "단발성 작업"이나 프로젝트 미선택 케이스는 레코드를 남기지 않음
    project_name = (project_name or "").strip()
    if not project_name:
        return
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

    # 최근 사용 spec 폴더 이력 누적 (last_sources 에서 spec_folder 타입 추출)
    if "last_sources" in extra:
        recent = list(entry.get("recent_spec_folders") or [])
        for src in extra["last_sources"]:
            if src.get("type") in ("spec_folder", "spec_folder_prev") and src.get("content"):
                path = src["content"]
                if path in recent:
                    recent.remove(path)
                recent.insert(0, path)  # 최신을 맨 앞에
        # 최대 10개
        entry["recent_spec_folders"] = recent[:10]

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

def push_stage(sess, stage: int, label: str, pct: int, eta_sec: int | None = None):
    data = {"stage": stage, "label": label, "pct": pct}
    if eta_sec is not None:
        data["eta_sec"] = eta_sec
    push(sess, "stage", data)

def push_log(sess, msg: str):
    push(sess, "log", {"msg": msg})

def push_error(sess, msg: str):
    sess["status"] = "error"
    push(sess, "error", {"msg": msg})


def count_unique_tc_ids(tc_content: str) -> int:
    """tc_content에서 유니크 TC ID 개수를 반환.
    build_excel의 parse_tc_markdown이 TC ID 기반 dedup을 수행하므로,
    웹에 표시하는 값도 동일한 유니크 기준으로 맞춘다.
    """
    if not tc_content:
        return 0
    ids = re.findall(r"^###\s+\*?\*?([A-Z]{2,}-[A-Z0-9]+-\d+)", tc_content, re.MULTILINE)
    return len(set(ids)) if ids else 0


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


def call_claude_cached(system_blocks: list, user_prompt: str, max_tokens: int = 8192) -> str:
    """system_blocks: list of {"type":"text","text":..., "cache_control":{"type":"ephemeral"} 선택}.
    첫 호출은 캐시 미스(오버헤드 ~25%), 이후 5분 내 동일 블록 호출은 캐시 히트(약 90% 비용↓).
    화면별 1:1 호출처럼 system 부분이 동일하고 user만 바뀔 때 효과 큼.
    """
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
        msg = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0,
            system=system_blocks,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return msg.content[0].text
    except Exception as e:
        raise RuntimeError(f"Claude API 오류 (cached): {e}")

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


def extract_scr_from_source(filename: str, content: str) -> str:
    """입력 소스에서 화면 식별자(SCR-NNN[A]) 추출 — Phase 1 단순 패턴.

    우선순위:
      1) 파일명 매칭: SCR-003.md → 'SCR-003'
      2) 본문 H1 첫 줄: '# SCR-003: ...' → 'SCR-003'
      3) 본문 첫 번째 패턴 등장
      4) 위 모두 실패 → '' (빈 문자열, AI 환각/추측 금지)
    """
    pattern = re.compile(r'SCR-\d+[A-Z]?')

    # 1) 파일명
    if filename:
        m = pattern.search(filename)
        if m:
            return m.group(0)

    if not content:
        return ''

    # 2) H1 첫 줄
    first_line = content.lstrip().split('\n', 1)[0] if content.lstrip() else ''
    if first_line.startswith('#'):
        m = pattern.search(first_line)
        if m:
            return m.group(0)

    # 3) 본문 첫 번째 등장
    m = pattern.search(content)
    if m:
        return m.group(0)

    # 4) 폴백
    return ''


def strip_appendix_tables(filename: str, content: str, primary_scr: str) -> tuple[str, list]:
    """입력 소스 본문에서 다른 SCR 화면의 부록 표를 자동 감지하여 제거 — v0.9.26.

    동료 보고 케이스: SCR-810.md 본문 끝에 SCR-403/SCR-221/SCR-410 의 에러 케이스
    부록 표가 붙어있어 AI 가 무관한 분류를 만드는 문제.

    감지 패턴:
      1. 부록 헤더: '**에러 케이스 (...)**:' 또는 '## 부록' 또는 '---' 다음에
         '| 화면 |' 컬럼이 있는 표
      2. 표 안의 '화면' 컬럼이 입력 파일의 primary_scr 와 다른 SCR 코드
      3. '---' 구분자 + 별도 SCR 코드들이 연이어 등장

    안전장치 (제거 안 함):
      - primary_scr 가 비어있으면 (식별자 없는 임의 마크다운) 부록 감지 시도 안 함
      - 표 안에 primary_scr 가 다수 등장하면 본문 핵심으로 판단해 보존

    Returns:
        (정제된 content, [{"reason": str, "scr_codes": [...]}, ...] 제거 정보)
    """
    if not content or not primary_scr:
        return content, []

    pattern_scr = re.compile(r'SCR-\d+[A-Z]?')

    # 줄 단위로 쪼개서 부록 후보 찾기
    lines = content.split('\n')
    removed_segments = []  # 제거된 정보 (사용자 안내용)
    keep_lines = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # 부록 헤더 패턴 — 본문 끝에서 자주 발견되는 형식
        is_appendix_header = (
            re.match(r'^\*\*에러\s*케이스\s*\(.+?\)\*\*\s*:?\s*$', line.strip()) or
            re.match(r'^\*\*부록.+?\*\*\s*:?\s*$', line.strip()) or
            re.match(r'^##\s+부록', line.strip()) or
            re.match(r'^##\s+다른\s*화면.+', line.strip())
        )

        # 부록 헤더 발견 → 다음 표의 SCR 들이 primary_scr 와 다른지 검사
        if is_appendix_header:
            # 헤더부터 표 끝까지 (또는 다음 ---) 의 영역 미리보기
            preview_end = min(n, i + 50)
            preview_block = '\n'.join(lines[i:preview_end])
            scrs_in_block = set(pattern_scr.findall(preview_block))
            other_scrs = [s for s in scrs_in_block if s != primary_scr]
            if other_scrs and primary_scr not in scrs_in_block:
                # 부록 영역이 다른 화면만 다룸 → 제거
                removed_segments.append({
                    "reason": "부록 표 — 다른 화면의 정보",
                    "scr_codes": sorted(other_scrs),
                    "header": line.strip(),
                })
                # 다음 빈 줄 + '---' 까지 또는 다음 H1/H2 까지 skip
                j = i + 1
                while j < n:
                    nxt = lines[j].strip()
                    # 다음 ---  / 다음 H1 / 다음 H2 / 다음 부록 헤더 만나면 종료 (그 줄은 keep 로 진입)
                    if nxt == '---':
                        # --- 자체는 보존하지 말고 skip (부록 마무리 구분선)
                        j += 1
                        break
                    if re.match(r'^#{1,2}\s+', nxt) and not re.match(r'^##\s+부록', nxt):
                        break  # 다음 일반 섹션 — keep 시작
                    j += 1
                i = j
                continue

        # 일반 라인 — 보존
        keep_lines.append(line)
        i += 1

    cleaned = '\n'.join(keep_lines)
    # 연속 빈 줄 정리 (3개 이상 → 2개)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned, removed_segments


def step_parse_sources(sess: dict, sources: list) -> str:
    """복수 소스를 각각 파싱한 뒤 하나의 텍스트로 합친다."""
    parts = []
    total = len(sources)
    # 입력 소스의 SCR 식별자 매핑 — TC 작성 단계에서 AI 에게 전달됨
    sess["_source_scr_map"] = {}  # {filename: scr_id}
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
            # SCR 식별자 추출 (마크다운 입력만 우선 적용)
            scr_id = extract_scr_from_source(content, text)
            if scr_id:
                sess["_source_scr_map"][content] = scr_id
                push_log(sess, f"[파싱] 화면 식별자 발견: {content} → {scr_id}")
                # v0.9.26: 부록 표 자동 감지 + 제거 — 다른 화면의 무관한 정보 차단
                cleaned_text, removed = strip_appendix_tables(content, text, scr_id)
                if removed:
                    text = cleaned_text
                    sess.setdefault("_appendix_removed", []).append({
                        "filename": content,
                        "primary_scr": scr_id,
                        "removed": removed,
                    })
                    for r in removed:
                        push_log(sess, f"[파싱] 부록 자동 제거 — {content} 의 '{r['header']}' (다른 화면: {', '.join(r['scr_codes'])})")
        else:
            text  = content
            label = "✏️ 텍스트 입력"
            push_log(sess, f"[파싱] 텍스트 입력 ({len(text):,}자)")

        parts.append(f"===== 소스 {i}/{total} — {label} =====\n\n{text}")

    raw_text = "\n\n".join(parts)
    parsed_path = sess["workspace"] / "01_parsed.md"
    parsed_path.write_text(f"# 파싱 결과\n\n{raw_text}", encoding="utf-8")
    # SCR 매핑 요약 로그
    if sess["_source_scr_map"]:
        push_log(sess, f"[파싱] 입력 소스 화면 식별자 매핑: {len(sess['_source_scr_map'])}개")
    else:
        push_log(sess, "[파싱] 입력 소스에서 화면 식별자(SCR-NNN) 미발견 — 화면 코드 컬럼은 빈 칸으로 출력됩니다")
    return raw_text


# ── 구조화 spec 폴더 처리 (v0.10.0+) ─────────────────────────────────────────
# 새 기획서 형식: 폴더 1개에 overview/policy/design/scr/*.md 가 역할별로 분리됨.
# 기존 "raw_text concat" 모드와 병행. 사용자가 폴더 경로로 입력하면 이 흐름을 탄다.

def classify_spec_files(folder: Path) -> dict:
    """spec 폴더 안의 md 파일들을 역할별로 자동 분류.
    반환: {"overview": Path|None, "policy": [Path...], "design": [Path...], "screens": [Path...]}
    분류 규칙(파일명/경로 우선순위):
      - scr/ 또는 SCR-* 패턴 → screens
      - *error*, *policy*, *biz*, *rule* → policy
      - *design*, *ux*, *theme*, *token* → design
      - 01_*, *spec*, *overview* → overview (첫 매칭 1개)
      - 그 외 .md → overview 폴백 (있으면 policy 으로)
    """
    out = {"overview": None, "policy": [], "design": [], "screens": []}
    if not folder.exists() or not folder.is_dir():
        return out

    # 1) screens — scr/ 하위 또는 파일명이 SCR-* 패턴
    scr_dir = folder / "scr"
    if scr_dir.exists() and scr_dir.is_dir():
        out["screens"] = sorted([p for p in scr_dir.glob("*.md") if p.is_file()])
    # 루트에 SCR-XXX.md 가 직접 있는 경우도 수용
    for p in sorted(folder.glob("SCR-*.md")):
        if p.is_file() and p not in out["screens"]:
            out["screens"].append(p)

    # 2) 루트 md 분류 (scr/ 안의 파일은 위에서 처리됨)
    for p in sorted(folder.glob("*.md")):
        if not p.is_file():
            continue
        name = p.name.lower()
        # 생성물(generated) 은 참고용으로만 — design 으로 분류
        if "error" in name or "policy" in name or "biz-rule" in name or "business-rule" in name:
            out["policy"].append(p)
        elif "design" in name or name.startswith("02_ux") or "theme" in name or "token" in name or "ux_design" in name:
            out["design"].append(p)
        elif name.startswith("01_") or "spec" in name or "overview" in name:
            if out["overview"] is None:
                out["overview"] = p
            else:
                out["policy"].append(p)
        else:
            # 미상 → policy 폴백 (overview 가 없으면 overview 로)
            if out["overview"] is None:
                out["overview"] = p
            else:
                out["policy"].append(p)
    return out


def parse_screen_list_table(overview_md_text: str) -> list[dict]:
    """01_spec.md 의 '화면 목록' 표를 파싱해 분류표 시드를 만든다.
    헤더 형식: | ID | 화면명 | 대분류 | 중분류 | 상태 | 설명 | 진입 경로 |
    상태(status) 컬럼이 'deprecated'/'미사용' 같으면 제외.
    반환: [{"id":"SCR-001","name":"Login","major":"Onboarding","middle":"Login","status":"active","desc":"...","entry":"..."}]
    """
    rows = []
    in_table = False
    headers: list[str] = []
    for line in overview_md_text.splitlines():
        line = line.rstrip()
        # 표 시작 감지: ID/화면명/대분류 같은 헤더가 있어야 함
        if line.startswith("|") and "ID" in line and ("대분류" in line or "Major" in line):
            cells = [c.strip() for c in line.strip("|").split("|")]
            headers = [c.lower() for c in cells]
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table:
            if not line.startswith("|"):
                in_table = False
                headers = []
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 4:
                continue
            row = {}
            for i, h in enumerate(headers):
                if i >= len(cells):
                    break
                row[h] = cells[i]
            # 키 정규화
            sid = row.get("id") or row.get("화면id") or ""
            name = row.get("화면명") or row.get("name") or ""
            major = row.get("대분류") or row.get("major") or ""
            middle = row.get("중분류") or row.get("middle") or ""
            status = row.get("상태") or row.get("status") or "active"
            desc = row.get("설명") or row.get("description") or ""
            entry = row.get("진입 경로") or row.get("진입경로") or row.get("entry") or ""
            if not sid or not re.match(r"^SCR[-_]?\w+", sid, re.IGNORECASE):
                continue
            if status.lower() in ("deprecated", "미사용", "obsolete", "삭제"):
                continue
            rows.append({
                "id": sid.upper().replace("_", "-"),
                "name": name,
                "major": major,
                "middle": middle,
                "status": status,
                "desc": desc,
                "entry": entry,
            })
    return rows


def extract_minors_from_screen_md(md_text: str, max_minors: int = 12) -> list[str]:
    """SCR-XXX.md 본문에서 소분류(세부 시나리오) 시드를 규칙 기반으로 추출.
    LLM 호출 없음. 우선순위:
      1. 상태(Status) 표 케이스 — 가장 구조화된 시나리오
      2. 에러 케이스 표
      3. [dev] 인터랙션 항목
      4. 비고의 [정책]/[제약]/[접근성]/[세션] 마커
    너무 많아지면 max_minors 까지 자른다.
    각 항목은 짧은 한국어 라벨(35자 이내)로 정규화.
    """
    minors: list[str] = []
    seen_keys: set[str] = set()  # 중복 제거용 (소문자 정규화 비교)

    def add(label: str):
        label = label.strip().rstrip(".·")
        if not label:
            return
        if len(label) > 50:
            label = label[:50].rstrip() + "…"
        key = re.sub(r"\s+", "", label.lower())
        if key in seen_keys:
            return
        seen_keys.add(key)
        minors.append(label)

    # 1) 상태 표 — | 케이스 | 조건 | 설명/동작 |
    in_status = False
    for line in md_text.splitlines():
        if not in_status:
            if re.search(r"상태\s*\(\s*Status\s*\)|^##+\s*상태", line):
                in_status = "header_pending"
            continue
        if in_status == "header_pending":
            if line.strip().startswith("|") and "케이스" in line:
                in_status = "rows"
            continue
        if in_status == "rows":
            if line.strip().startswith("|---"):
                continue
            if not line.strip().startswith("|"):
                in_status = False
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 1 and cells[0]:
                # 케이스 라벨 (Normal, Error.network) 을 소분류 시드로
                add(f"{cells[0]} 상태 표시 및 동작")

    # 2) 에러 케이스 표 — | 에러 케이스 | 표시 패턴 | 메시지 | 동작 |
    in_err = False
    err_headers: list[str] = []
    for line in md_text.splitlines():
        if not in_err:
            if re.search(r"에러\s*케이스|^##+\s*에러", line):
                in_err = "header_pending"
            continue
        if in_err == "header_pending":
            if line.strip().startswith("|") and ("에러" in line or "케이스" in line):
                err_headers = [c.strip().lower() for c in line.strip("|").split("|")]
                in_err = "rows"
            continue
        if in_err == "rows":
            if line.strip().startswith("|---"):
                continue
            if not line.strip().startswith("|"):
                in_err = False
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 1 and cells[0]:
                add(f"에러 처리 — {cells[0]}")

    # 3) [dev] 인터랙션 항목 — bullet list (- xxx → yyy)
    in_inter = False
    for line in md_text.splitlines():
        if not in_inter:
            if re.search(r"\[dev\]\s*인터랙션|^##+\s*인터랙션|\*\*인터랙션\*\*", line, re.IGNORECASE):
                in_inter = True
            continue
        if not line.strip():
            continue
        # bullet 끝났음을 다음 굵은 헤더(**) 또는 다음 ## 으로 판단
        if line.startswith("**") or line.startswith("##") or line.startswith("---"):
            in_inter = False
            continue
        # bullet 추출
        m = re.match(r"^[\-\*]\s+(.+)", line)
        if m:
            body = m.group(1)
            # "<요소> <이벤트> → <결과>" 형식이 흔함. 화살표 앞부분만 사용
            label = body.split("→")[0]
            # 백틱·HTML 코드 제거
            label = re.sub(r"`[^`]+`", "", label)
            label = re.sub(r"<[^>]+>", "", label)
            label = re.sub(r"\s+", " ", label).strip(" .·:")
            if label and len(label) >= 3:
                add(label)

    # 4) 비고의 [정책]/[제약]/[접근성]/[세션]/[타이밍] 마커
    for m in re.finditer(r"\[(정책|제약|접근성|세션|타이밍|보안|성능)\]\s*([^\n]{5,80})", md_text):
        marker, body = m.group(1), m.group(2)
        # 첫 문장만
        body = re.split(r"[.。]", body)[0].strip(" ·-")
        if body:
            add(f"[{marker}] {body}")

    # 한도 잘라내기 — 가장 중요한 것 먼저 (위에서 이미 우선순위 순)
    if len(minors) > max_minors:
        minors = minors[:max_minors]
    return minors


def build_classification_from_screen_list(screen_rows: list[dict], project_name: str,
                                            screens_meta: list[dict] | None = None) -> str:
    """parse_screen_list_table() 의 결과를 분류표 마크다운(extract_domains() 가 읽는 형식)으로 변환.
    LLM 호출 없이 바로 Human Gate 로 갈 수 있는 분류표를 생성한다.

    구조: 대분류(영역) > 중분류(화면) > 소분류(세부 시나리오)
      - 중분류 = 화면 (SCR-XXX) — 사용자가 자주 단위로 인식하는 레벨
      - 소분류 = SCR md 본문에서 규칙 기반 추출한 시나리오 (extract_minors_from_screen_md)

    Args:
        screen_rows: parse_screen_list_table() 결과 (id/name/major/middle 등)
        screens_meta: parse_screen_md() 결과 list — 있으면 본문에서 소분류 추출.
                      없으면 폴백(소분류 = '기본 동작 검증'만).
    """
    # 화면 ID → meta 매핑
    meta_by_id = {sc["id"]: sc for sc in (screens_meta or [])}

    # 대분류 → [화면 행 list]  (중분류는 화면 자체로 매핑)
    from collections import defaultdict
    tree: dict[str, list[dict]] = defaultdict(list)
    for r in screen_rows:
        major = r["major"] or "공통"
        tree[major].append(r)

    lines = [f"# TC 분류표 — {project_name}", ""]
    for major, screens in tree.items():
        lines.append(f"## 대분류: {major}")
        lines.append("")
        for s in screens:
            # 중분류 = 화면명만 (화면 코드는 별도 '화면 코드' 컬럼에서 보여짐 → 중복 제거).
            # 화면명이 비어있는 폴백 케이스에서만 ID 를 사용.
            screen_label = (s["name"] or s["id"]).strip()
            lines.append(f"### 중분류: {screen_label}")
            lines.append("")
            lines.append("#### 소분류")

            # 소분류 = SCR md 본문에서 추출 (규칙 기반)
            sc_meta = meta_by_id.get(s["id"])
            minors = []
            if sc_meta and sc_meta.get("raw"):
                minors = extract_minors_from_screen_md(sc_meta["raw"])

            if minors:
                for label in minors:
                    lines.append(f"- {label}")
            else:
                # 폴백 — 본문이 없거나 파싱 실패. 최소 1개라도 시드.
                desc_short = (s.get("desc") or "")[:60]
                lines.append(f"- 기본 UI 표시 및 동작 검증{(': ' + desc_short) if desc_short else ''}")

            lines.append("")
    return "\n".join(lines)


def parse_screen_md(md_path: Path) -> dict:
    """SCR-XXX.md 한 파일을 파싱해 메타 정보 추출.
    반환: {
      "id": "SCR-001",
      "title": "Login",
      "group": "로그인_공통",
      "description": "...",
      "states": [{"case":"Normal","cond":"...","desc":"..."}, ...],
      "ref_keywords": ["error.network", ...],   # cross-ref 감지용
      "raw": <원문 전체>
    }
    """
    text = md_path.read_text(encoding="utf-8")
    # ID — 파일명 우선, 본문 H1 보조
    m = re.match(r"^(SCR[-_]?\w+)", md_path.stem, re.IGNORECASE)
    sid = m.group(1).upper().replace("_", "-") if m else md_path.stem.upper()

    # H1 제목
    title = ""
    h1 = re.search(r"^#\s+([^\n]+)", text, re.MULTILINE)
    if h1:
        # "SCR-001: Login" → "Login"
        t = h1.group(1).strip()
        t = re.sub(r"^SCR[-_]?\w+\s*[:\-]\s*", "", t, flags=re.IGNORECASE)
        title = t.strip()

    # 그룹/설명 — **그룹**: xxx, **설명**: xxx 패턴
    group = ""
    g = re.search(r"\*\*그룹\*\*\s*[:：]\s*([^\n]+)", text)
    if g:
        group = g.group(1).strip()
    desc = ""
    d = re.search(r"\*\*설명\*\*\s*[:：]\s*([^\n]+(?:\n(?![*#\-|]).+)*)", text)
    if d:
        desc = d.group(1).strip()[:300]

    # 상태(Status) 표 — | 케이스 | 조건 | 설명 / 동작 |
    states: list[dict] = []
    in_status_tbl = False
    status_headers: list[str] = []
    for line in text.splitlines():
        if not in_status_tbl:
            # "**상태 (Status)**" 또는 "## 상태" 등 키워드 뒤의 첫 표
            if re.search(r"상태\s*\(\s*Status\s*\)|^##+\s*상태", line):
                in_status_tbl = "header_pending"
            continue
        if in_status_tbl == "header_pending":
            if line.strip().startswith("|") and ("케이스" in line or "case" in line.lower()):
                cells = [c.strip().lower() for c in line.strip("|").split("|")]
                status_headers = cells
                in_status_tbl = "rows"
            continue
        if in_status_tbl == "rows":
            if line.strip().startswith("|---"):
                continue
            if not line.strip().startswith("|"):
                in_status_tbl = False
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            row = {}
            for i, h in enumerate(status_headers):
                if i < len(cells):
                    row[h] = cells[i]
            states.append({
                "case": row.get("케이스") or row.get("case") or "",
                "cond": row.get("조건") or row.get("condition") or "",
                "desc": (row.get("설명 / 동작") or row.get("설명") or row.get("동작")
                         or row.get("description") or ""),
            })

    # cross-ref 키워드 감지 (정책/디자인 자동 inject 용)
    ref_kw = []
    if re.search(r"error\.\w+|에러|네트워크|타임아웃|세션", text, re.IGNORECASE):
        ref_kw.append("error")
    if re.search(r"세션|토큰|로그아웃|만료", text):
        ref_kw.append("session")
    if re.search(r"toast|modal|alert|inline error|full-?screen error", text, re.IGNORECASE):
        ref_kw.append("error_ui")
    if re.search(r"empty\s*state|빈\s*상태", text, re.IGNORECASE):
        ref_kw.append("empty_state")
    if re.search(r"loading|로딩|skeleton", text, re.IGNORECASE):
        ref_kw.append("loading")

    return {
        "id": sid,
        "title": title,
        "group": group,
        "description": desc,
        "states": states,
        "ref_keywords": ref_kw,
        "raw": text,
    }


def _split_checklist_report(tc_md: str) -> tuple[str, str]:
    """AI 응답의 말미에서 '### 체크리스트 처리 결과' 섹션을 분리.
    반환: (TC 본문, 체크리스트 보고 텍스트)
    못 찾으면 (원본, "") 반환.
    """
    # ### 체크리스트 처리 결과 헤더 찾기 (대소문자/이모지 변형 허용)
    m = re.search(r"\n#{1,4}\s*(?:체크리스트\s*처리\s*결과|체크리스트\s*검증|Checklist\s*(?:Verification|Result))\s*\n",
                  tc_md, re.IGNORECASE)
    if not m:
        return tc_md, ""
    body = tc_md[:m.start()].rstrip()
    report = tc_md[m.start():].strip()
    return body, report


def _extract_screen_classification_section(classification: str, screen_id: str, screen_name: str) -> str:
    """전체 분류표 마크다운에서 해당 SCR 의 중분류 섹션만 추출 (A-1 분류표 동적 축소).

    build_classification_from_screen_list() 결과는 다음 구조:
      ## 대분류: Trade
      ### 중분류: Order Confirm     ← 화면명 = screen_name
      #### 소분류
      - ...

    찾기 우선순위: screen_name 일치 → screen_id 일치.
    못 찾으면 빈 문자열 반환 (호출부에서 폴백 처리).
    """
    lines = classification.splitlines()
    out: list[str] = []
    in_target = False
    current_major = ""
    for line in lines:
        if line.startswith("## 대분류:"):
            current_major = line
            in_target = False
            continue
        if line.startswith("### 중분류:"):
            label = line[len("### 중분류:"):].strip()
            # 화면명 또는 ID 매칭
            if screen_name and label == screen_name.strip():
                in_target = True
                if current_major:
                    out.append(current_major)
                out.append(line)
                continue
            if screen_id and screen_id in label:
                in_target = True
                if current_major:
                    out.append(current_major)
                out.append(line)
                continue
            in_target = False
            continue
        if line.startswith("## ") or line.startswith("### "):
            in_target = False
            continue
        if in_target:
            out.append(line)
    return "\n".join(out).strip()


def _build_checklist_from_screen_meta(screen_meta: dict) -> str:
    """C-2 체크리스트 강제 — 화면 본문의 모든 상태/인터랙션/비고 마커에 ID 부여.
    AI 가 응답 끝에 각 항목별 [✓ 처리 / ✗ 누락 + 사유] 보고하도록 함.
    """
    items: list[str] = []
    counter_s = 0
    counter_i = 0
    counter_r = 0

    # 상태 케이스 — S1, S2, ...
    for st in screen_meta.get("states", []):
        counter_s += 1
        case = st.get("case", "").strip() or f"상태{counter_s}"
        items.append(f"S{counter_s}. {case} 상태")

    # 인터랙션 — I1, I2, ... — raw 에서 [dev] 인터랙션 bullet 발췌 (extract_minors 와 같은 패턴)
    in_inter = False
    for line in screen_meta.get("raw", "").splitlines():
        if not in_inter:
            if re.search(r"\[dev\]\s*인터랙션|\*\*인터랙션\*\*", line, re.IGNORECASE):
                in_inter = True
            continue
        if line.startswith("**") or line.startswith("##") or line.startswith("---"):
            in_inter = False
            continue
        m = re.match(r"^[\-\*]\s+(.+)", line)
        if m:
            body = m.group(1).split("→")[0]
            body = re.sub(r"`[^`]+`", "", body)
            body = re.sub(r"<[^>]+>", "", body)
            body = re.sub(r"\s+", " ", body).strip(" .·:")
            if body and len(body) >= 3:
                counter_i += 1
                items.append(f"I{counter_i}. {body[:50]}")
                if counter_i >= 10:  # 너무 많으면 자름
                    break

    # 비고 마커 — R1, R2, ...
    for m in re.finditer(r"\[(정책|제약|접근성|세션|타이밍|보안|성능)\]\s*([^\n]{5,80})",
                         screen_meta.get("raw", "")):
        marker, body = m.group(1), m.group(2)
        body = re.split(r"[.。]", body)[0].strip(" ·-")
        if body:
            counter_r += 1
            items.append(f"R{counter_r}. [{marker}] {body[:45]}")
            if counter_r >= 6:
                break

    if not items:
        return ""
    return "\n".join(items)


def build_screen_user_prompt(screen_meta: dict, project_name: str, project_code: str,
                              suite_code: str, starting_seq: int,
                              policy_excerpts: list[str] = None,
                              design_excerpts: list[str] = None,
                              screen_classification_section: str = "") -> str:
    """화면별 1:1 호출용 user prompt.

    v0.10.x 변경:
    - A-1: 전체 분류표 대신 해당 SCR 의 중분류 섹션만 주입 (다른 화면 정보 격리)
    - C-2: 화면 본문에서 추출한 체크리스트 + 응답 말미 자체 검증 강제
    """
    seq_str = f"{starting_seq:03d}"
    next_str = f"{starting_seq+1:03d}"
    example_id = f"{project_code}-{suite_code}-{seq_str}"

    # A-1: 분류표 — 해당 화면 섹션만
    classification_block = ""
    if screen_classification_section:
        classification_block = (
            f"## 분류표 (이 화면만 — 사용자 승인된 최종 진실 소스)\n"
            f"{screen_classification_section}\n"
        )

    states_block = ""
    if screen_meta["states"]:
        lines = ["## 이 화면의 상태 케이스 (각각 TC 후보)"]
        for st in screen_meta["states"]:
            lines.append(f"- **{st['case']}**: 조건={st['cond']} / 동작={st['desc']}")
        states_block = "\n".join(lines) + "\n"

    refs_block = ""
    if policy_excerpts or design_excerpts:
        parts = ["## 이 화면에 적용되는 정책·디자인 발췌 (자동 cross-ref)"]
        if policy_excerpts:
            parts.append("### 관련 정책")
            for x in policy_excerpts:
                parts.append(x)
        if design_excerpts:
            parts.append("### 관련 디자인")
            for x in design_excerpts:
                parts.append(x)
        refs_block = "\n".join(parts) + "\n"

    # C-2: 체크리스트
    checklist = _build_checklist_from_screen_meta(screen_meta)
    checklist_block = ""
    if checklist:
        checklist_block = (
            "\n## 체크리스트 — 반드시 모두 처리 (누락 시 응답 끝에 사유 명시)\n\n"
            "다음 항목 각각에 대해 최소 1개의 TC 를 작성하세요. 항목은 화면 명세에서 자동 추출됨.\n\n"
            f"{checklist}\n"
        )

    selfcheck = (
        "\n## 응답 말미 자체 검증 (필수)\n\n"
        "TC 작성 완료 후, 응답 마지막에 아래 형식으로 체크리스트 처리 결과를 반드시 명시하세요:\n\n"
        "```\n"
        "### 체크리스트 처리 결과\n"
        "- S1: ✓ TC SC-LIT-001, SC-LIT-005\n"
        "- S2: ✓ TC SC-LIT-002\n"
        "- I1: ✗ 누락 / 사유: 화면 명세에 충분한 정보 없음\n"
        "- ...\n"
        "```\n"
        "이 자체 검증 표는 후처리에서 분리되며 TC 본문에 영향 없습니다. 누락이 발견되면 솔직히 명시하세요.\n"
    )

    return f"""프로젝트: {project_name}
화면: {screen_meta['id']} — {screen_meta['title']}
그룹: {screen_meta['group']}

⚠️ TC ID 형식: `{example_id}`, `{project_code}-{suite_code}-{next_str}`, ... (시작 번호 `{seq_str}`부터 연속 증가)
⚠️ 시스템 프롬프트의 'TC 생성 카테고리 4가지(UI/주요/예외/에러)'와 비율(20/35/25/20)을 반드시 따르세요.
   카테고리 3(예외)·4(에러)는 반드시 포함합니다 (Positive 만으로 구성 금지).

{classification_block}
## 화면 명세 (전문 — 이 문서의 내용에서만 TC 작성)

{screen_meta['raw']}

{states_block}
{refs_block}
{checklist_block}
{selfcheck}

위 화면의 모든 상태 케이스·인터랙션·비고 마커를 빠짐없이 TC 로 변환하세요.
- Normal 상태 → 카테고리 1 (UI/UX) + 카테고리 2 (주요 기능) Positive TC
- Error.* 상태 → 카테고리 3 (예외) Negative + 카테고리 4 (에러) Edge TC
- 비고의 [정책]/[제약]/[접근성]/[세션]/[타이밍]/[dev] 마커는 각각 별도 TC 후보
- 인터랙션의 모든 진입 경로/탭 동작/네비게이션 → 각각 별도 TC
- 누락 없이 가능한 모든 시나리오를 작성. 응답이 길어지더라도 끝까지 작성하세요.

## ⚠️ 중복 통합 원칙 (반드시 준수)

**같은 화면 안에서 동일한 검증 결과를 갖는 트리거가 여러 개라면 1개의 TC 로 통합** 하세요.
대표 예시:
- "Cancel 버튼 탭" 과 "배경 오버레이 탭" 둘 다 → "시트 닫힘 + SCR-102 복귀"
  → ❌ 별도 TC 2개로 만들지 말고, ✅ TC 1개로 통합 + 테스트 단계에 두 동작 모두 명시

통합 형식 예시:
```
### {{ID}} — Order Confirm 시트 닫기 (Cancel 버튼 또는 배경 오버레이 탭)

**테스트 단계**
다음 중 하나를 수행한다:
1. Cancel 버튼을 탭한다
2. 시트 외부 배경 오버레이를 탭한다

**예상 결과**
- 시트가 닫히고 SCR-102 Lite Trade 화면으로 복귀한다
- 두 진입 모두 동일한 결과 (AppState 변경 없음)
```

판단 기준:
- 검증 결과(예상 결과)가 100% 동일 → 통합 권장
- 검증 결과가 일부 다르거나 부수 효과(로그·이벤트 등)가 다름 → 별도 TC 유지
- 사전 조건이 다른 경우 → 별도 TC 유지 (사전 조건이 다르면 같은 결과여도 별도 검증 필요)

이 통합 원칙은 양을 줄이는 것이 목적이 아니라 **테스터 가독성과 유지보수성** 을 위한 것입니다.
의미 있는 검증이 사라지면 안 되고, 단지 "동일 검증의 트리거 중복" 만 합치는 것입니다.
"""


def extract_policy_excerpts(policy_full_text: str, ref_keywords: list[str]) -> list[str]:
    """정책 전문에서 화면이 참조할 섹션만 발췌. 키워드별 최대 800자.
    너무 길면 화면별 호출이 무거워지므로 압축해서 user prompt 에 넣는다.
    """
    if not ref_keywords or not policy_full_text:
        return []

    excerpts = []
    sections = re.split(r"\n(?=#{1,3}\s)", policy_full_text)
    seen_titles = set()
    for kw in ref_keywords:
        kw_pat = {
            "error": r"error|에러|패턴",
            "session": r"세션|토큰|만료|로그아웃",
            "error_ui": r"toast|modal|alert|inline|full-?screen",
            "empty_state": r"empty|빈\s*상태",
            "loading": r"loading|로딩|skeleton",
        }.get(kw, kw)
        for sec in sections:
            head = sec.split("\n", 1)[0]
            if head in seen_titles:
                continue
            if re.search(kw_pat, sec, re.IGNORECASE):
                excerpt = sec.strip()[:800]
                excerpts.append(excerpt)
                seen_titles.add(head)
                if len(excerpts) >= 4:  # 너무 많으면 잘라냄
                    return excerpts
    return excerpts


def parse_scr_filter_from_focus(focus_area: str, available_scrs: set[str] | None = None) -> set[str] | None:
    """focus_area 텍스트에서 SCR ID 패턴을 관대하게 추출해 필터로 사용.

    지원 입력 형식:
      - 명시: "SCR-104", "scr-104", "scr_104", "SCR104", "SCR 104"
      - 일괄 (앵커 모드): "SCR-102, 104, 106, 116" → 첫 SCR 발견 후 따라오는 숫자도 SCR ID 로
      - 범위: "SCR-102~116", "SCR-102 to 116", "SCR-102 - 116"
        → available_scrs 가 주어지면 그 범위 내 실제 존재 SCR 만 매칭
      - 영문 접미: "SCR-007A" 그대로 인식
      - 자연어 섞임: "주문 확인 화면 (SCR-104) 만 만들어줘" OK

    Args:
        focus_area:      사용자 입력 텍스트
        available_scrs:  폴더에서 실제 발견된 SCR ID 집합 (예: {"SCR-001","SCR-102",...})
                         주어지면 범위 표기·숫자 흡수의 유효성 검증에 사용.
                         None 이면 명시적으로 보인 ID 만 신뢰.

    Returns:
        - set[str]: 매칭된 SCR ID 들 (예: {"SCR-102","SCR-104"})
        - None:     SCR 패턴이 하나도 없으면 (필터 미적용 = 전체 처리)
    """
    if not focus_area or not focus_area.strip():
        return None

    text = focus_area
    # 1) 명시적 SCR-XXX 매칭 (영문 접미 가능)
    explicit = re.findall(r"SCR[\s\-_]*([0-9]+[A-Z]?)", text, re.IGNORECASE)
    explicit_norm = {f"SCR-{m.upper()}" for m in explicit}

    # 앵커가 하나도 없으면 SCR 모드 아님 → None
    if not explicit_norm:
        return None

    # available_scrs 가 주어지면 명시 ID 도 폴더 검증 (잘못 입력한 ID 흡수 방지)
    if available_scrs:
        result = explicit_norm & available_scrs
    else:
        result = set(explicit_norm)

    # 2) 범위 표기 지원: "SCR-102~116", "102-116", "102 to 116"
    #    숫자~숫자 / 숫자-숫자 / 숫자 to 숫자 패턴
    range_matches = re.findall(
        r"(?:SCR[\s\-_]*)?([0-9]{2,4})\s*(?:~|to|\-\-|—|–)\s*([0-9]{2,4})",
        text, re.IGNORECASE
    )
    if range_matches and available_scrs:
        for start_s, end_s in range_matches:
            start, end = int(start_s), int(end_s)
            if start > end:
                start, end = end, start
            # available_scrs 안에서 숫자 부분이 [start, end] 범위에 들어가는 것 추가
            for sid in available_scrs:
                m = re.match(r"^SCR-([0-9]+)([A-Z]?)$", sid)
                if not m:
                    continue
                num = int(m.group(1))
                if start <= num <= end:
                    result.add(sid)

    # 3) 앵커 모드 — 텍스트에 SCR 가 보였으니 뒤따르는 "그냥 숫자"도 SCR ID 후보로
    #    예: "SCR-102, 104, 106, 116" → 102, 104, 106, 116 모두
    #    단, available_scrs 가 주어진 경우에만 (미지의 숫자 흡수 방지).
    if available_scrs:
        # 텍스트 안의 모든 2~4자리 숫자 토큰 (앞뒤가 단어 경계)
        # 단, 범위 표기에서 이미 처리한 숫자는 흡수해도 무방 (set 이라 중복 제거됨)
        all_nums = re.findall(r"\b([0-9]{2,4})([A-Z]?)\b", text)
        for num_s, suffix in all_nums:
            num = int(num_s)
            # SCR ID 와 매칭되는 형식으로 후보 생성
            # available_scrs 에는 보통 "SCR-001", "SCR-102", "SCR-007A" 형식
            candidate_plain = f"SCR-{num_s}{suffix.upper()}"
            # zero-padding 변형: 102 → 102, 1 → 001 / 12 → 012 도 시도
            candidate_padded = f"SCR-{num_s.zfill(3)}{suffix.upper()}"
            for cand in (candidate_plain, candidate_padded):
                if cand in available_scrs:
                    result.add(cand)
                    break

    return result


def step_parse_structured_spec(sess: dict, folder_path: str) -> dict:
    """구조화 spec 폴더 1개를 받아 overview/policy/design/screens 로 분리하고 메타 추출.
    반환: {
      "overview_text": str,
      "policy_text":   str,    # 모든 정책 md concat
      "design_text":   str,    # 모든 디자인 md concat
      "screens":       [parse_screen_md() 결과 ...],
      "screen_rows":   [parse_screen_list_table() 결과 ...],
    }
    LLM 호출은 0회 — 순수 파싱만.
    """
    folder = Path(folder_path).expanduser()
    if not folder.exists():
        raise FileNotFoundError(f"폴더 없음: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"폴더가 아님: {folder}")

    push_log(sess, f"[구조화 spec] 폴더 스캔 중: {folder}")
    cls = classify_spec_files(folder)

    overview_text = cls["overview"].read_text(encoding="utf-8") if cls["overview"] else ""
    policy_text = "\n\n".join(p.read_text(encoding="utf-8") for p in cls["policy"])
    design_text = "\n\n".join(p.read_text(encoding="utf-8") for p in cls["design"])

    screens = [parse_screen_md(p) for p in cls["screens"]]
    screen_rows = parse_screen_list_table(overview_text) if overview_text else []

    push_log(sess,
        f"[구조화 spec] 분류 완료 — overview={'있음' if cls['overview'] else '없음'} / "
        f"policy={len(cls['policy'])}개 / design={len(cls['design'])}개 / "
        f"화면 md={len(cls['screens'])}개 / 화면 목록 표={len(screen_rows)}행")

    return {
        "overview_text": overview_text,
        "policy_text":   policy_text,
        "design_text":   design_text,
        "screens":       screens,
        "screen_rows":   screen_rows,
        "_files":        cls,  # 디버깅용
    }


def diff_spec_folders(prev_folder: Path, new_folder: Path) -> dict:
    """이전 spec 폴더와 신규 spec 폴더를 비교해 SCR 단위로 변경분 분류.

    반환: {
      "added":     [SCR-ID, ...],   # 신규 추가된 화면
      "modified":  [SCR-ID, ...],   # 본문이 바뀐 화면
      "removed":   [SCR-ID, ...],   # 신규에서 사라진 화면
      "unchanged": [SCR-ID, ...],   # 동일 (재생성 불필요)
      "common_changed": bool,       # 정책/디자인/overview 가 바뀌었는지
    }
    """
    import hashlib

    def _hash_file(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    def _scr_map(folder: Path) -> dict[str, Path]:
        cls = classify_spec_files(folder)
        out: dict[str, Path] = {}
        for p in cls["screens"]:
            m = re.match(r"^(SCR[-_]?\w+)", p.stem, re.IGNORECASE)
            if m:
                sid = m.group(1).upper().replace("_", "-")
                out[sid] = p
        return out

    prev_scr = _scr_map(prev_folder)
    new_scr = _scr_map(new_folder)

    added = sorted(set(new_scr) - set(prev_scr))
    removed = sorted(set(prev_scr) - set(new_scr))
    modified = []
    unchanged = []
    for sid in sorted(set(new_scr) & set(prev_scr)):
        if _hash_file(prev_scr[sid]) != _hash_file(new_scr[sid]):
            modified.append(sid)
        else:
            unchanged.append(sid)

    # 공통 문서(overview/policy/design) 변경 여부
    prev_cls = classify_spec_files(prev_folder)
    new_cls = classify_spec_files(new_folder)
    common_changed = False
    for key in ("overview",):
        a = prev_cls.get(key)
        b = new_cls.get(key)
        if (a is None) != (b is None) or (a and b and _hash_file(a) != _hash_file(b)):
            common_changed = True
            break
    if not common_changed:
        prev_common = sorted([p.name for p in prev_cls["policy"] + prev_cls["design"]])
        new_common = sorted([p.name for p in new_cls["policy"] + new_cls["design"]])
        if prev_common != new_common:
            common_changed = True
        else:
            for plist_a, plist_b in [
                (sorted(prev_cls["policy"], key=lambda p: p.name),
                 sorted(new_cls["policy"], key=lambda p: p.name)),
                (sorted(prev_cls["design"], key=lambda p: p.name),
                 sorted(new_cls["design"], key=lambda p: p.name)),
            ]:
                for a, b in zip(plist_a, plist_b):
                    if _hash_file(a) != _hash_file(b):
                        common_changed = True
                        break
                if common_changed:
                    break

    return {
        "added": added,
        "modified": modified,
        "removed": removed,
        "unchanged": unchanged,
        "common_changed": common_changed,
    }


def step_parse_structured_spec_with_diff(sess: dict, new_folder_path: str,
                                           prev_folder_path: str,
                                           include_unchanged: bool = False) -> dict:
    """diff 모드 — 신규 폴더를 파싱하되 변경된/추가된 화면만 screens 에 남기고
    unchanged 는 따로 표기. step_parse_structured_spec 의 결과 + diff 정보를 반환.
    include_unchanged=True 이면 모든 화면 포함(분류표 일관성 유지용).
    """
    new_folder = Path(new_folder_path).expanduser()
    prev_folder = Path(prev_folder_path).expanduser()
    if not prev_folder.exists():
        raise FileNotFoundError(f"이전 폴더 없음: {prev_folder}")

    push_log(sess, f"[diff] 비교 — 이전={prev_folder.name} / 신규={new_folder.name}")
    diff = diff_spec_folders(prev_folder, new_folder)
    push_log(sess,
        f"[diff] 추가 {len(diff['added'])}개 / 수정 {len(diff['modified'])}개 / "
        f"삭제 {len(diff['removed'])}개 / 동일 {len(diff['unchanged'])}개 / "
        f"공통 문서 변경={diff['common_changed']}")

    # 신규 폴더 정상 파싱
    spec = step_parse_structured_spec(sess, str(new_folder))

    # diff 결과를 screens 필터링에 반영 (재생성 대상만 남김)
    target_scrs = set(diff["added"]) | set(diff["modified"])
    if diff["common_changed"]:
        push_log(sess, "[diff] ⚠️ 공통 문서(정책/디자인/overview) 변경됨 — 모든 화면 재생성 권장")
    if include_unchanged or diff["common_changed"]:
        # 전체 유지 (분류표 일관성 + 공통 변경 시 안전 재생성)
        pass
    else:
        before_n = len(spec["screens"])
        spec["screens"] = [sc for sc in spec["screens"] if sc["id"] in target_scrs]
        push_log(sess, f"[diff] 재생성 대상으로 화면 필터링: {before_n}개 → {len(spec['screens'])}개")

    spec["_diff"] = diff
    spec["_prev_folder"] = str(prev_folder)
    return spec


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
    except ImportError:
        raise RuntimeError("requests 패키지가 필요합니다: pip install requests")
    push_log(sess, f"[파싱] 웹 크롤링 중: {url}")
    # TLS 검증: 기본 활성화. 사내 테스트 등 자가서명 인증서가 필요한 경우에만
    # TC_WEB_INSECURE=1 환경변수로 명시적으로 비활성화 가능.
    verify_tls = os.environ.get("TC_WEB_INSECURE", "").strip() not in ("1", "true", "yes")
    if not verify_tls:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        push_log(sess, f"[파싱] ⚠️ TLS 검증 비활성화됨 (TC_WEB_INSECURE=1)")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (TC-Automation/2.0)"}
        resp = requests.get(url, headers=headers, timeout=30, verify=verify_tls)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "html" in content_type:
            return html_to_text(resp.text)
        else:
            return resp.text
    except requests.exceptions.SSLError as e:
        raise RuntimeError(
            f"TLS 인증서 검증 실패: {e}. "
            f"자가서명 인증서 환경이라면 TC_WEB_INSECURE=1 환경변수를 설정하세요."
        )
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

## 화면/페이지 인벤토리 (필수)
(문서에 등장하는 모든 화면/페이지를 빠짐없이 나열 — ID·이름·간단 설명)
(Splash, 진입 화면, 정적 화면, 브랜딩 화면, 빈 상태 화면 등 단순 화면도 반드시 포함)
(SCR-xxx, SCREEN-xxx 같은 코드가 있으면 그대로 사용)

## 대분류별 정책
(각 대분류별로 테스트 가능한 정책을 구체적으로 나열)

## 핵심 비즈니스 규칙
(서비스의 핵심 로직과 검증 포인트)

## 예외 처리 정책
(오류 케이스, 엣지 케이스, 유효성 검증 규칙)

⛔ 다음을 절대 드롭하지 마세요:
- 단순 UI 진입 화면 (Splash, 브랜딩 화면, Welcome, Landing)
- 정적 정보 화면 (About, Help, Empty State)
- 짧은 설명의 화면도 화면 인벤토리에 반드시 ID와 이름을 기록
- "테스트할 게 단순해 보여도" 생략하지 말 것 — UI 체크 TC 대상
"""
    focus_instruction = ""
    if focus_area:
        focus_instruction = f"""

⚠️ 중요: 사용자가 다음 기능에 대한 TC만 생성하려고 합니다. 해당 기능과 관련된 정책/규칙에 집중하세요:
→ {focus_area}

관련 없는 대분류나 기능의 정책은 간략하게만 다루고, 위 범위의 정책을 상세하게 분석하세요."""
    user = f"""프로젝트: {project_name}

다음 문서에서 TC 작성에 필요한 모든 정책과 규칙을 추출해주세요:

---
{raw_text[:200000]}
---

각 정책은 구체적이고 테스트 가능한 형태로 서술해주세요.{focus_instruction}

⚠️ 문서에 등장하는 모든 화면/기능/섹션을 빠짐없이 정리하세요. 주요한 것만 선별하지 말고 전체를 포괄하세요.
"""
    result = call_claude(system, user, max_tokens=16000)
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

## 대분류코드 — 대분류명

### FT-001 기능명
- 설명: (기능 설명)
- 테스트 포인트: (주요 검증 항목)
- 우선순위: High/Medium/Low

각 대분류의 모든 기능을 빠짐없이 나열하세요.

⛔ 필수: 정책 분석의 "화면/페이지 인벤토리"에 나열된 모든 화면을 각각 별도 기능으로 반드시 포함하세요.
- Splash 같은 단순 진입 화면도 "화면 진입/표시/버튼 동작" 같은 테스트 포인트로 기능화
- 정적 화면, Empty State, Welcome 화면도 모두 개별 기능으로 등록
- "테스트할 게 적어 보인다"는 이유로 생략 금지 — UI/UX 체크 TC 대상
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

모든 주요 기능을 대분류별로 분류하여 나열하고, 각 기능의 테스트 포인트를 구체적으로 서술하세요.{focus_instruction}

⚠️ 정책 분석에 등장한 모든 화면/기능을 빠짐없이 나열하세요. 선별하지 말고 전체를 다루세요.
"""
    result = call_claude(system, user, max_tokens=16000)
    features_path = sess["workspace"] / "03_features.md"
    features_path.write_text(result, encoding="utf-8")
    push_log(sess, f"[기능] 기능 목록 완료 → {len(result):,}자")
    return result


def step_policy_features_combined(sess: dict, raw_text: str, project_name: str,
                                    focus_area: str = "") -> tuple[str, str]:
    """정책 반영 모드 최적화 — policy + features를 1회 호출로 통합 추출.
    반환: (policy_text, features_text).
    출력 형식은 기존 policy/features의 합집합 구조를 그대로 유지해 기존 코드 호환.
    """
    push_log(sess, "[정책+기능] 통합 추출 중... (1회 호출로 정책·기능 동시 생성)")
    system = """당신은 소프트웨어 QA 전문가입니다. 주어진 원문에서 테스트 준비에 필요한
정책·규칙과 기능 인벤토리를 **한 번에 통합 문서로** 추출합니다.

다음 정확한 형식으로 출력하세요:

# 통합 분석 결과 — {프로젝트명}

## [SECTION: POLICY] 화면/페이지 인벤토리 (필수)
(원문에 등장하는 모든 화면/페이지를 빠짐없이 나열 — ID · 이름 · 간단 설명 한 줄)
(Splash, 진입 화면, 정적 화면, 브랜딩 화면, 빈 상태 화면 등 단순 화면도 반드시 포함)
(SCR-xxx, SCREEN-xxx 같은 코드가 있으면 그대로 사용)

## [SECTION: POLICY] 대분류별 정책
(각 대분류별로 테스트 가능한 정책을 구체적으로 나열)

## [SECTION: POLICY] 핵심 비즈니스 규칙
(서비스의 핵심 로직과 검증 포인트)

## [SECTION: POLICY] 예외 처리 정책
(오류 케이스, 엣지 케이스, 유효성 검증 규칙)

---

# Feature List — {프로젝트명}

## [SECTION: FEATURES] 대분류코드 — 대분류명

### FT-001 기능명
- 설명: (기능 설명)
- 테스트 포인트: (주요 검증 항목)
- 우선순위: High/Medium/Low

(각 대분류·화면의 모든 기능을 빠짐없이 나열)

⛔ 다음을 절대 드롭하지 마세요:
- 단순 UI 진입 화면 (Splash, Welcome, Landing, 브랜딩)
- 정적 정보 화면 (About, Help, Empty State)
- 각 화면의 "진입·표시·버튼 동작" 같은 단순해 보이는 케이스
- 화면 인벤토리에 등록된 모든 화면은 Feature List에도 최소 1개 기능으로 반드시 등록
"""
    focus_instruction = ""
    if focus_area:
        focus_instruction = f"""

⚠️ 포커스 범위: 아래 범위에 해당하는 화면/기능만 포함하세요.
→ {focus_area}"""
    user = f"""프로젝트: {project_name}

아래 원문에서 (1) 정책·규칙 분석 + (2) 기능 인벤토리를 **한 문서로 통합** 추출하세요.

---
{raw_text[:200000]}
---
{focus_instruction}

⚠️ 문서에 등장하는 모든 화면/기능/섹션을 빠짐없이 다루세요. 선별하지 마세요.
⚠️ 반드시 위의 출력 형식(SECTION 마커 포함)을 정확히 따르세요. 후처리가 의존합니다.
"""
    result = call_claude(system, user, max_tokens=16000)

    # 결과를 policy_text / features_text 로 분리
    # `---` 또는 `# Feature List` 기준으로 나눔. 실패 시 전체를 둘 다에 넣어 안전하게 처리.
    policy_text = result
    features_text = result
    # 분리 마커: "# Feature List" (독립 # 헤더)
    m = re.search(r"^# Feature List\b", result, re.MULTILINE)
    if m:
        policy_text = result[:m.start()].rstrip()
        features_text = result[m.start():].strip()

    # 저장 (디버깅용)
    combined_path = sess["workspace"] / "02_combined.md"
    combined_path.write_text(result, encoding="utf-8")
    (sess["workspace"] / "02_policy.md").write_text(policy_text, encoding="utf-8")
    (sess["workspace"] / "03_features.md").write_text(features_text, encoding="utf-8")

    push_log(sess, f"[정책+기능] 통합 추출 완료 → 정책 {len(policy_text):,}자 · 기능 {len(features_text):,}자")
    return policy_text, features_text


# ── 4단계: 분류표 생성 ────────────────────────────────────────────────────────
def step_classify(sess: dict, features_text: str, project_name: str, focus_area: str = "") -> str:
    push_log(sess, "[분류] 계층 분류표 생성 중...")
    system = """당신은 TC 분류 전문가입니다. 기능 목록을 바탕으로 대분류/중분류/소분류 계층 분류표를 생성합니다.

다음 형식으로 출력하세요:

# TC 분류표 — {프로젝트명}

## 대분류: {대분류명}

### 중분류: {중분류명}

#### 소분류
- {소분류명}: {설명}

규칙:
- 대분류는 비즈니스 영역 단위 (예: Onboarding, Authentication, Trading)
- 중분류는 주요 기능 단위
- 소분류는 세부 케이스 단위
- ⛔ 대분류/중분류/소분류 이름에 괄호 코드를 붙이지 마세요. 예: "FOOTER (FOOT)" ❌ → "Footer" ✅
- ⛔ TC ID를 생성하지 마세요. TC ID는 이후 단계에서 검토자가 결정합니다.
- ⛔ TC ID 생성 규칙, TC ID 예시표, 기능-TC 매핑표를 포함하지 마세요.
- 분류표에는 대분류/중분류/소분류 구조만 출력하세요.

⛔ 필수 완전성:
- 기능 목록에 등장하는 모든 화면을 중분류로 반드시 포함하세요.
- Splash, Login Options, Welcome, Landing, Empty State 같은 단순 UI 진입 화면도 반드시 중분류로 포함
- 온보딩 흐름의 모든 화면(SCR-xxx 등 코드가 있으면 해당 화면명)을 누락 없이 분류
- "단순해 보여서 생략"은 금지 — UI/UX 체크 TC 대상이므로 반드시 분류표에 등록
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

⚠️ 문서 전체를 빠짐없이 분석하여 모든 대분류와 중분류를 포함하세요.
"""
    result = call_claude(system, user, max_tokens=16000)
    classify_path = sess["workspace"] / "04_classification_draft.md"
    classify_path.write_text(result, encoding="utf-8")
    push_log(sess, f"[분류] 분류표 생성 완료 → {len(result):,}자")
    return result


# ── Quick 모드 전용 3단계: 인벤토리 → 분류 → 섹션발췌 ──────────────────────
# 원문을 요약하지 않고 "항목 목록만" 먼저 추출한 뒤, 항목별로 원문의 해당 섹션만
# 발췌해 TC 작성에 전달한다. 총 토큰은 기존 Quick과 비슷하거나 적고, 누락이 줄어든다.

def step_quick_inventory(sess: dict, raw_text: str, project_name: str,
                          focus_area: str = "") -> str:
    """Quick 모드 1단계 — 원문에서 모든 화면/기능 인벤토리만 추출.
    요약이 아니라 '목록'이어서 AI가 축약할 여지가 적다."""
    push_log(sess, "[Quick 1/3] 인벤토리 추출 중...")
    system = """당신은 기획 문서 스캐너입니다. 주어진 원문에서 테스트 가능한 모든 항목(화면/페이지/기능)의 인벤토리만 추출합니다.

출력 형식 (정확히 이 형식만):
# 인벤토리

## 화면 목록
- {ID} | {이름} | {한 줄 설명}
- ...

## 독립 기능 목록 (화면에 속하지 않는 기능)
- {이름} | {한 줄 설명}
- ...

규칙:
- 화면 ID(SCR-xxx, SCREEN-xxx 등)가 원문에 있으면 그대로 쓰세요. 없으면 비워 두세요.
- 각 항목은 한 줄로 간결하게. 상세 설명·정책·절차는 절대 포함하지 마세요.
- ⛔ Splash, Empty State, Landing, Welcome, 진입 화면, 정적 화면도 **반드시** 포함하세요.
- ⛔ 원문에 등장하는 모든 화면을 빠짐없이 수집하세요. "단순해 보인다"고 생략 금지.
- ⛔ 요약·정리·설명 문구를 추가하지 마세요. 항목 목록만 출력.
- 일반적으로 원문 기획서 1개당 30~100개의 항목이 나옵니다. 10개 미만이면 뭔가 놓친 것입니다.
"""
    focus_instruction = ""
    if focus_area:
        focus_instruction = f"""

⚠️ 포커스 범위: 아래 범위에 해당하는 항목만 인벤토리에 포함하세요.
→ {focus_area}"""
    user = f"""프로젝트: {project_name}

아래 원문에서 화면/기능 인벤토리를 추출하세요.

---
{raw_text[:200000]}
---
{focus_instruction}

⚠️ 빠짐없이 모든 화면을 수집하세요. Splash, Login Options, 각 Onboarding 단계 화면, Empty State 등 **단순 화면도 반드시** 포함.
"""
    result = call_claude(system, user, max_tokens=8000)
    inv_path = sess["workspace"] / "02_inventory.md"
    inv_path.write_text(result, encoding="utf-8")
    # 간단한 카운트 로그
    item_count = len(re.findall(r"^-\s+", result, re.MULTILINE))
    push_log(sess, f"[Quick 1/3] 인벤토리 완료 — 항목 {item_count}개, {len(result):,}자")
    return result


def step_classify_from_inventory(sess: dict, inventory_text: str,
                                  project_name: str, focus_area: str = "") -> str:
    """Quick 모드 2단계 — 인벤토리 → 분류표.
    원문을 입력하지 않으므로 AI가 축약하지 않고 모든 항목을 분류한다."""
    push_log(sess, "[Quick 2/3] 분류표 생성 중...")
    system = """당신은 TC 분류 전문가입니다. 주어진 인벤토리의 모든 항목을 대분류/중분류/소분류 계층으로 분류합니다.

다음 형식으로 출력하세요:

# TC 분류표 — {프로젝트명}

## 대분류: {대분류명}

### 중분류: {중분류명}

#### 소분류
- {소분류명}: {설명}

규칙:
- 대분류는 비즈니스 영역 단위 (예: Onboarding, Authentication, Trading)
- 중분류는 화면/주요 기능 단위 (인벤토리의 각 화면/기능이 중분류가 됨)
- 소분류는 해당 중분류의 테스트 가능한 세부 케이스
- ⛔ 대분류/중분류/소분류 이름에 괄호 코드를 붙이지 마세요. 예: "FOOTER (FOOT)" ❌ → "Footer" ✅
- ⛔ TC ID를 생성하지 마세요.
- ⛔ TC ID 생성 규칙, TC ID 예시표, 기능-TC 매핑표를 포함하지 마세요.
- 분류표에는 대분류/중분류/소분류 구조만 출력하세요.

⛔ 필수 완전성 (매우 중요):
- 인벤토리의 **모든 항목을 반드시 중분류로** 포함하세요. 하나도 생략하지 마세요.
- Splash, Login Options, Welcome, Landing, Empty State 등 단순 화면도 반드시 중분류로 등록
- 인벤토리 항목 수 ≒ 중분류 수 (통상)
- 중분류가 10개 미만이면 뭔가 빠뜨린 것입니다.
"""
    focus_instruction = ""
    if focus_area:
        focus_instruction = f"""

⚠️ 포커스 범위: 인벤토리 중 아래 범위에 해당하는 항목만 분류하세요.
→ {focus_area}"""
    project_policies = load_project_policies(project_name)
    category_ref = ""
    if project_policies:
        category_ref = f"""

⚠️ 기존 프로젝트 카테고리 참조: 아래 기존 대분류/중분류 이름과 동일한 용어를 사용하세요.
{project_policies[:4000]}"""
    user = f"""프로젝트: {project_name}

아래 인벤토리의 모든 항목을 대분류/중분류/소분류 계층으로 분류해주세요:

---
{inventory_text}
---
{focus_instruction}{category_ref}

⚠️ 인벤토리의 **모든 항목**을 반드시 포함하세요. 빠뜨리면 안 됩니다.
"""
    result = call_claude(system, user, max_tokens=16000)
    classify_path = sess["workspace"] / "04_classification_draft.md"
    classify_path.write_text(result, encoding="utf-8")
    push_log(sess, f"[Quick 2/3] 분류표 생성 완료 → {len(result):,}자")
    return result


def extract_section_from_raw(raw_text: str, middle_name: str,
                              major_name: str = "", max_chars: int = 8000) -> str:
    """Quick 모드 3단계용 — 원문에서 middle_name과 관련된 섹션만 발췌한다.
    매칭 우선순위:
      1. 정확한 middle_name을 포함한 헤더(###/##)
      2. middle_name의 단어들을 포함한 헤더
      3. major_name 매칭 (백업)
    찾으면 해당 헤더부터 다음 같은 레벨 헤더까지 반환.
    못 찾으면 middle_name이 언급된 주변 ±500자 컨텍스트 반환.
    """
    if not raw_text or not middle_name:
        return ""
    lines = raw_text.splitlines()

    def header_level(line: str) -> int:
        m = re.match(r"^(#+)\s", line)
        return len(m.group(1)) if m else 0

    # 후보 검색어: 원문 middle_name + 공백 대체 + 단어 분할
    candidates = [middle_name.strip()]
    if "/" in middle_name:
        candidates.extend(p.strip() for p in middle_name.split("/") if p.strip())
    # 영단어 3자 이상만 개별 매칭 (너무 일반적인 단어 방어)
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z0-9]{2,}", middle_name) if len(w) > 2]
    candidates.extend(words)

    best_span = None
    best_score = 0
    for i, line in enumerate(lines):
        lvl = header_level(line)
        if lvl == 0:
            continue
        # 헤더 텍스트 추출
        header_text = re.sub(r"^#+\s+", "", line).strip()
        # 점수 산정: middle_name 완전 매칭 > 부분 매칭 > 단어 매칭
        score = 0
        if middle_name.lower() in header_text.lower():
            score = 100
        else:
            for w in candidates:
                if w and w.lower() in header_text.lower():
                    score = max(score, 50)
        if score == 0 and major_name and major_name.lower() in header_text.lower():
            score = 10

        if score > best_score:
            # 같은 레벨 다음 헤더까지 발췌
            end = len(lines)
            for j in range(i + 1, len(lines)):
                jlvl = header_level(lines[j])
                if jlvl > 0 and jlvl <= lvl:
                    end = j
                    break
            best_span = (i, end)
            best_score = score
            if score >= 100:
                # 완전 매칭이면 더 찾지 않음
                break

    if best_span:
        i, end = best_span
        section = "\n".join(lines[i:end])
        return section[:max_chars]

    # Fallback: middle_name 언급 위치 ±500자
    pat = re.escape(middle_name)
    m = re.search(pat, raw_text, re.IGNORECASE)
    if m:
        start = max(0, m.start() - 500)
        end = min(len(raw_text), m.end() + 2000)
        return raw_text[start:end][:max_chars]
    return ""


# ── 5단계: Human Gate (블로킹) ────────────────────────────────────────────────
def step_gate(sess: dict, classification: str):
    push_log(sess, "[GATE] 분류표 검토 대기 중... 사용자 승인 필요")
    sess["status"] = "gate_waiting"
    # 입력 소스 SCR 매핑도 함께 전달 — 프론트의 Gate UI에서 안내문 노출
    _scr_map = sess.get("_source_scr_map") or {}
    # v0.9.22: Stage 1 분류표 중복 가능성 예측
    try:
        prediction = predict_classification_duplicates(classification)
    except Exception as _e:
        push_log(sess, f"[GATE] 중복 예측 스킵: {_e}")
        prediction = {"predictions": [], "high_risk_count": 0}
    if prediction.get("high_risk_count"):
        push_log(sess, f"[GATE] 분류표 중복 가능성 {prediction['high_risk_count']}개 그룹 탐지")
    push(sess, "gate", {
        "content": classification,
        "source_scr_map": _scr_map,
        "duplicate_prediction": prediction,
    })
    # 사용자 승인까지 블로킹
    sess["gate_event"].wait()
    approved_content = sess["approved"]
    push_log(sess, "[GATE] 분류표 승인됨. TC 작성 시작.")
    # 승인된 분류표 저장
    approved_path = sess["workspace"] / "classification_v1_APPROVED.md"
    approved_path.write_text(approved_content, encoding="utf-8")
    return approved_content


# ── 6단계: TC 작성 ────────────────────────────────────────────────────────────
def step_write_tc_per_screen(sess: dict, approved_classification: str,
                              spec_data: dict, project_name: str,
                              selected_domain_codes=None) -> tuple:
    """구조화 spec 모드 전용 — 화면(SCR) 1개당 LLM 1회 호출.

    Args:
        approved_classification: Human Gate 통과한 분류표 (build_classification_from_screen_list 결과).
        spec_data:               step_parse_structured_spec() 반환값.
        selected_domain_codes:   대분류 필터 (None=전체).
    Returns: (merged_tc_md, total_tc_count)

    핵심 차이점 (vs step_write_tc):
      - 정책/디자인을 시스템 프롬프트에 cache_control 로 1회만 전송 → 화면 N개 호출에 캐시 히트
      - 화면별 user prompt 는 해당 SCR 본문 전문 + 자동 추출한 cross-ref 인용만 포함
      - 화면 단위 매핑이 정확 (휴리스틱 발췌 X)
    """
    push_log(sess, "[화면별 TC 작성] 시작 — 구조화 spec 모드")
    tc_rules = load_tc_rules()
    fewshot = load_fewshot_examples()
    project_policies = load_project_policies(project_name)

    # 1) 시스템 프롬프트 블록 구성 — cache_control 적용 + 화면 격리 강화 (v0.10.x)
    #
    # 변경: 분류표는 시스템 블록에서 제거하고 user prompt 에서 화면별 축소 버전으로 주입.
    #       이유: SCR 단독 호출 vs 일괄 호출의 결과 갯수 편차 줄이기 (다른 화면 정보가
    #       AI 의 분배·중복 회피 동기를 만들어 갯수가 줄어드는 현상).
    #
    # ⚠️ Anthropic 제약: cache_control 블록은 최대 4개.
    #    캐시 #1: tc_rules + 카테고리 가이드 + 형식 규칙 (build_tc_system_prompt 의 분류표 제외 부분)
    #    캐시 #2: spec policy_text (전문)
    #    캐시 #3: spec design_text (전문)
    #    캐시 #4: 화면별 호출 모드 안내 (B-1 단독 호출 명시)
    sys_blocks = []
    # 분류표 자리에 placeholder 만 남기고 build_tc_system_prompt() 호출 → 화면별 축소 버전은 user 로 이동.
    base_system_prompt = build_tc_system_prompt(
        tc_rules=tc_rules,
        classification="(분류표는 user 메시지에 화면별 축소 버전으로 제공됩니다 — 그 화면만 처리하세요)",
        project_policies=project_policies,
        fewshot=fewshot,
    )
    sys_blocks.append({
        "type": "text",
        "text": base_system_prompt,
        "cache_control": {"type": "ephemeral"},  # 캐시 #1
    })
    if spec_data.get("policy_text"):
        sys_blocks.append({
            "type": "text",
            "text": f"\n## 공통 정책 문서 (구조화 spec 의 policy md 전문)\n{spec_data['policy_text'][:20000]}\n",
            "cache_control": {"type": "ephemeral"},  # 캐시 #2
        })
    if spec_data.get("design_text"):
        sys_blocks.append({
            "type": "text",
            "text": f"\n## 디자인 시스템 문서 (구조화 spec 의 design md 전문 — 토큰/컴포넌트 참조)\n{spec_data['design_text'][:20000]}\n",
            "cache_control": {"type": "ephemeral"},  # 캐시 #3
        })
    # B-1 단독 호출 명시 + 격리 강화 — AI 자기검열 차단
    sys_blocks.append({
        "type": "text",
        "text": (
            "\n## 화면별 단독 호출 모드 안내 (반드시 준수)\n\n"
            "**핵심 원칙**: 이 호출은 **하나의 화면(SCR)에 대한 단독 작업** 입니다. "
            "프로젝트에 다른 화면이 존재하더라도 이 호출에서는 **존재하지 않는 것처럼** 처리하세요. "
            "당신은 이 화면 전담 QA 엔지니어이고, 다른 화면은 다른 사람이 담당합니다.\n\n"
            "**금지 행동**:\n"
            "- 다른 화면에 만들 TC 와의 중복 회피를 의식하지 마세요 (중복은 후처리에서 자동 제거됨)\n"
            "- TC 갯수를 다른 화면들과 분배해서 줄이지 마세요\n"
            "- 'A 도 B 도 비슷하니 하나로 묶자' 같은 통합 시도 금지\n\n"
            "**지향**: user 메시지의 화면 명세에 등장하는 **모든** 상태/인터랙션/비고 마커를 "
            "각각 독립적인 TC 로 변환하세요. 카테고리 4가지(20/35/25/20%)와 카테고리 3·4 의무 포함은 그대로 유지.\n"
        ),
        "cache_control": {"type": "ephemeral"},  # 캐시 #4
    })

    # 2) 처리 대상 화면 필터링 (selected_domain_codes)
    all_domains = extract_domains(approved_classification)
    if selected_domain_codes:
        domain_codes_set = set(selected_domain_codes)
        # 분류표의 대분류명 → 화면 매핑
    else:
        domain_codes_set = None

    # screen_rows 의 major(대분류) 와 domain 의 name 매칭으로 SuiteCode 결정 (대분류 단위 폴백용)
    suite_codes = sess.get("suite_codes", [])
    domain_to_suite: dict[str, str] = {}
    for i, dom in enumerate(all_domains):
        if i < len(suite_codes) and suite_codes[i]:
            domain_to_suite[dom["name"]] = suite_codes[i].strip().strip("-")
        else:
            domain_to_suite[dom["name"]] = dom["code"]

    # ── v0.10.x: 화면(SCR)별 고유 SuiteCode 결정 — 기존 인프라 재사용 ─────────
    # tc-rules.md §2-1 유형 B (Screen-based) 규칙 적용.
    # SM/SA 프로젝트는 SuiteCode 자리에 ScreenCode 를 사용하고 NNN 은 화면 내 001~.
    # 우선순위:
    #   1) projects/{project}/screen_code_map.md 에 등록된 ScreenCode (사용자 합의)
    #   2) 미등록 화면은 resolve_screen_code() 자동 파생 (기존 함수 재사용)
    # 두 단계 모두 used_codes 충돌 회피 내장.
    project_code_for_id = _detect_project_code(project_name)
    is_screen_mode = _is_screen_based(project_code_for_id)
    screen_map = load_screen_code_map(project_name) if is_screen_mode else {}

    rows_by_id_pre = {r["id"]: r for r in spec_data.get("screen_rows", [])}
    screen_to_suite: dict[str, str] = {}
    used_screen_codes: set[str] = set()
    # resume 시 같은 결과가 나오도록 ID 정렬 보장
    sorted_screens = sorted(spec_data["screens"], key=lambda sc: sc["id"])
    for sc in sorted_screens:
        meta_row = rows_by_id_pre.get(sc["id"], {})
        # screen_code_map.md 는 'Middle Name' 키로 매핑 — 화면명(title) 또는 중분류 사용.
        # 우선 title 로 시도 (Login, Email Input 등) → 없으면 SCR-ID 자체로 시도.
        middle_name = (sc.get("title") or meta_row.get("name") or sc["id"]).strip()
        if is_screen_mode:
            # 기존 resolve_screen_code() 가 1) screen_map 정확 일치 2) 자동 파생
            #   3) used_codes 충돌 회피 모두 처리
            code = resolve_screen_code(middle_name, screen_map, used_screen_codes)
        else:
            # Suite-based 프로젝트(SC, PC Web)는 대분류 단위 SuiteCode 사용
            major = meta_row.get("major", "")
            code = domain_to_suite.get(major, "FUNC") or "FUNC"
        used_screen_codes.add(code)
        screen_to_suite[sc["id"]] = code

    # screens 와 screen_rows 를 ID 로 조인
    rows_by_id = {r["id"]: r for r in spec_data.get("screen_rows", [])}
    target_screens = []
    for sc in spec_data["screens"]:
        check_stop(sess)
        meta_row = rows_by_id.get(sc["id"], {})
        major = meta_row.get("major") or ""
        if domain_codes_set is not None:
            # selected_domain_codes 는 코드 기반이므로 코드/이름 매칭 모두 시도
            matched_dom = next((d for d in all_domains if d["name"] == major or d["code"] == major), None)
            if not matched_dom or matched_dom["code"] not in domain_codes_set:
                continue
        target_screens.append((sc, meta_row, major))

    if not target_screens:
        raise RuntimeError("처리할 화면이 없습니다. 분류표/필터를 확인하세요.")

    push_log(sess, f"[화면별 TC 작성] 대상 화면 {len(target_screens)}개")
    project_code = _detect_project_code(project_name)

    # resume 지원 — 이미 처리된 화면은 건너뛴다.
    # 화면별 결과는 sess["workspace"]/per_screen/<SCR-ID>.md 에 저장된다.
    per_screen_dir = sess["workspace"] / "per_screen"
    per_screen_dir.mkdir(exist_ok=True)
    completed_ids = {p.stem for p in per_screen_dir.glob("SCR-*.md")}
    if completed_ids:
        push_log(sess, f"[화면별 TC 작성] resume — 이미 완료된 화면 {len(completed_ids)}개 건너뜀: {sorted(completed_ids)[:5]}{'...' if len(completed_ids) > 5 else ''}")

    tc_parts: list[str] = []
    seq_per_suite: dict[str, int] = {}
    total_tc = 0

    # 이미 완료된 화면의 결과를 먼저 메모리에 적재
    # 유형 B (Screen-based): 각 화면이 고유 SuiteCode + 001~ 라 누적 의미 없음. 그래도
    # 다음 화면 호출에서 seq_per_suite 가 의도치 않게 사용될 가능성 차단을 위해
    # 화면 단위로는 +1 만 표기하고 실제 starting 결정은 위쪽에서 is_screen_mode 분기.
    # 유형 A (Suite-based): 같은 SuiteCode 화면들이 누적되도록 + scr_tc_count.
    for sc, meta_row, major in target_screens:
        if sc["id"] not in completed_ids:
            continue
        existing_path = per_screen_dir / f"{sc['id']}.md"
        existing_text = existing_path.read_text(encoding="utf-8")
        suite_code = screen_to_suite.get(sc["id"]) or domain_to_suite.get(major, "FUNC") or "FUNC"
        scr_tc_count = count_unique_tc_ids(existing_text)
        if is_screen_mode:
            seq_per_suite[suite_code] = scr_tc_count + 1  # 참고용 (실제 reuse X)
        else:
            seq_per_suite[suite_code] = seq_per_suite.get(suite_code, 1) + scr_tc_count
        total_tc += scr_tc_count
        tc_parts.append(f"<!-- {sc['id']} — {sc['title']} (resumed) -->\n\n{existing_text.strip()}")

    pending = [(sc, mr, mj) for (sc, mr, mj) in target_screens if sc["id"] not in completed_ids]
    push_log(sess, f"[화면별 TC 작성] 대기 화면 {len(pending)}개 (총 {len(target_screens)}개 중)")

    for idx_pending, (sc, meta_row, major) in enumerate(pending, 1):
        check_stop(sess)
        idx = len(completed_ids) + idx_pending  # 전체 진행 인덱스
        suite_code = screen_to_suite.get(sc["id"]) or domain_to_suite.get(major, "FUNC") or "FUNC"
        # tc-rules.md §2-1:
        #   - 유형 B (Screen-based, SM/SA): NNN 은 화면 내 유니크 → 항상 1 부터
        #   - 유형 A (Suite-based, SC):     NNN 은 Suite 내 전역 유니크 → seq_per_suite 누적
        if is_screen_mode:
            starting = 1
        else:
            starting = seq_per_suite.get(suite_code, 1)

        # cross-ref 인용 추출
        policy_excerpts = extract_policy_excerpts(spec_data.get("policy_text", ""), sc["ref_keywords"])

        # A-1: 분류표 — 해당 화면 섹션만 추출. 못 찾으면 폴백으로 짧은 헤더만.
        screen_section = _extract_screen_classification_section(
            approved_classification, sc["id"], sc.get("title", "")
        )
        if not screen_section:
            screen_section = f"## 대분류: {major}\n### 중분류: {sc.get('title', sc['id'])}\n"

        user = build_screen_user_prompt(
            screen_meta=sc,
            project_name=project_name,
            project_code=project_code,
            suite_code=suite_code,
            starting_seq=starting,
            policy_excerpts=policy_excerpts,
            design_excerpts=None,  # 디자인은 system 캐시에 들어가 있어서 별도 발췌 불필요
            screen_classification_section=screen_section,
        )

        push(sess, "stage", {
            "stage": 4, "label": f"[{idx}/{len(target_screens)}] {sc['id']} TC 작성 중...",
            "pct": 55 + int(25 * (idx / max(len(target_screens), 1))),
        })

        # max_tokens=20000 — Anthropic SDK 의 'Streaming required >10min' 임계 회피.
        # 32000 까지 올렸더니 SDK 가 streaming 강제 → 21333 (≈ 8K tps × 약 9분) 이하로 유지.
        # 안전 마진 + 미래 모델 속도 변화 고려해 20000.
        # 현재 사용량: TC 56개 시 ~14K 토큰 → 20K 한도로도 충분히 여유.
        tc_draft = call_claude_cached(sys_blocks, user, max_tokens=20000)

        # 잘림 감지 + 자동 보충 호출 (기존 step_write_tc 와 동등 처리).
        # 증상 예시: 마지막 TC 가 '| 플랫' 같이 표 중간에서 끊기면 사전조건/스텝/기대결과
        # 컬럼이 빈 채로 Excel 에 들어감. 마지막 ### 이후 본문에 필수 섹션 없으면 보충.
        last_tc_match = list(re.finditer(r"^###\s", tc_draft, re.MULTILINE))
        if last_tc_match:
            last_tc_block = tc_draft[last_tc_match[-1].start():]
            if "**테스트 단계**" not in last_tc_block or "**예상 결과**" not in last_tc_block:
                push_log(sess, f"[화면별 TC 작성] {sc['id']} 마지막 TC 불완전 — 이어서 생성 중...")
                try:
                    continuation = call_claude_cached(
                        sys_blocks,
                        f"이전 응답이 max_tokens 한도로 잘렸습니다. 아래 미완성 TC 를 그대로 이어서 완성하세요. "
                        f"새 TC 추가 금지, 표/사전조건/테스트 단계/예상 결과/비고 누락 없이.\n\n---\n{last_tc_block}",
                        max_tokens=8000,  # 미완성 TC 1~2개 완성용 — 충분
                    )
                    tc_draft = tc_draft[:last_tc_match[-1].start()] + continuation
                    push_log(sess, f"[화면별 TC 작성] {sc['id']} 보충 완료")
                except Exception as e:
                    push_log(sess, f"[화면별 TC 작성] {sc['id']} 보충 실패: {e} — 잘린 채 진행")

        # C-2: 응답 말미의 '체크리스트 처리 결과' 섹션 분리 (TC 본문 영향 차단)
        tc_clean, checklist_report = _split_checklist_report(tc_draft)
        if checklist_report:
            (per_screen_dir / f"{sc['id']}_checklist.md").write_text(checklist_report, encoding="utf-8")

        # 화면별 즉시 저장 — resume 시 여기서 다시 시작
        (per_screen_dir / f"{sc['id']}.md").write_text(tc_clean, encoding="utf-8")

        # TC 개수 카운트 — 유형별 seq 누적 정책
        scr_tc_count = count_unique_tc_ids(tc_clean)
        if is_screen_mode:
            # 화면 단위 리셋 — 누적 의미 없으므로 참고용으로만
            seq_per_suite[suite_code] = scr_tc_count + 1
        else:
            # Suite-based: 같은 SuiteCode 끼리 NNN 전역 유니크 → 다음 화면 starting 누적
            seq_per_suite[suite_code] = starting + scr_tc_count
        total_tc += scr_tc_count

        # 화면 헤더 + 본문
        tc_parts.append(f"<!-- {sc['id']} — {sc['title']} -->\n\n{tc_clean.strip()}")
        # 체크리스트 처리 보고 요약 — 누락 항목 카운트
        if checklist_report:
            n_done = checklist_report.count("✓")
            n_miss = checklist_report.count("✗")
            push_log(sess,
                f"[화면별 TC 작성] [{idx}/{len(target_screens)}] {sc['id']} ({suite_code}) 완료 — "
                f"TC {scr_tc_count}개 (체크리스트 {n_done}✓ / {n_miss}✗, 누적 {total_tc})")
        else:
            push_log(sess,
                f"[화면별 TC 작성] [{idx}/{len(target_screens)}] {sc['id']} ({suite_code}) 완료 — "
                f"TC {scr_tc_count}개 (누적 {total_tc})")

    merged = "\n\n---\n\n".join(tc_parts)
    draft_path = sess["workspace"] / "tc_draft_per_screen.md"
    draft_path.write_text(merged, encoding="utf-8")
    push_log(sess, f"[화면별 TC 작성] 전체 완료 — 화면 {len(target_screens)}개, TC {total_tc}개")

    # 정책 A 후처리 검증: 같은 화면 안에서 예상 결과가 동일한 TC 의심 그룹 검출.
    # 자동 병합은 하지 않고 리포트로만 알림 (false positive 위험).
    try:
        dup_report = detect_same_result_duplicates(merged)
        if dup_report["total_suspect"] > 0:
            report_path = sess["workspace"] / "duplicate_suspects.md"
            lines = ["# 중복 의심 TC 그룹 (검토 필요)\n"]
            lines.append(f"동일 화면 내 같은 검증 결과를 갖는 TC 그룹 {len(dup_report['groups'])}개 / 통합 가능 TC {dup_report['total_suspect']}개\n")
            for i, g in enumerate(dup_report["groups"], 1):
                lines.append(f"\n## 그룹 {i} — {g['middle']}\n")
                lines.append(f"**공통 예상 결과**: {g['common_result']}\n")
                lines.append("**해당 TC**:")
                for tc in g["tcs"]:
                    lines.append(f"- `{tc['id']}` — {tc['title']}")
                lines.append("\n→ 검토 후 1개로 통합하고 테스트 단계에 다른 트리거를 추가하는 것을 권장")
            report_path.write_text("\n".join(lines), encoding="utf-8")
            push_log(sess,
                f"⚠️ [중복 의심] 같은 화면 내 동일 결과 TC {dup_report['total_suspect']}개 검출 — "
                f"{report_path.name} 참고")
        # 세션에 저장 — UI 알림용
        sess["_dup_same_result_report"] = dup_report
    except Exception as e:
        push_log(sess, f"[중복 검증] 스킵: {e}")

    return merged, total_tc


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

    # 대분류 목록 추출
    all_domains = extract_domains(approved_classification)

    # 범위 필터 적용
    if selected_domain_codes:
        domains = [d for d in all_domains if d["code"] in selected_domain_codes]
        skipped = [d["code"] for d in all_domains if d["code"] not in selected_domain_codes]
        if skipped:
            push_log(sess, f"[TC 작성] 범위 제외 대분류: {', '.join(skipped)}")
    else:
        domains = all_domains

    if not domains:
        raise RuntimeError("선택된 대분류가 없습니다. 범위를 다시 확인하세요.")

    # SuiteCode 매핑 (Human Gate에서 검토자가 입력한 코드)
    suite_codes = sess.get("suite_codes", [])
    for i, domain in enumerate(domains):
        if i < len(suite_codes) and suite_codes[i]:
            domain["suite_code"] = suite_codes[i]
    if suite_codes:
        push_log(sess, f"[TC 작성] SuiteCode 매핑: {', '.join(d.get('suite_code', '?') for d in domains)}")

    push_log(sess, f"[TC 작성] 생성 대상 대분류 {len(domains)}개: {', '.join(d['code'] for d in domains)}")

    all_tc_parts = []
    total_tc = 0

    # 중분류 목록 추출 (분류표에서)
    def extract_middles_from_classification(classification_text: str, domain_code: str) -> list[str]:
        domain_section = extract_domain_section(classification_text, domain_code)
        middles = []
        for line in domain_section.splitlines():
            line = line.strip()
            if line.startswith("### "):
                mid_name = re.sub(r"^###\s+", "", line).strip()
                mid_name = re.sub(r"^중분류[:\s]*", "", mid_name).strip()
                mid_name = re.sub(r"\s*[\(\（][A-Z]{2,8}[\)\）]", "", mid_name).strip()
                if mid_name:
                    middles.append(mid_name)
        return middles

    for i, domain in enumerate(domains):
        domain_code = domain["code"]
        domain_name = domain["name"]

        # 중분류별 분할 호출
        middles = extract_middles_from_classification(approved_classification, domain_code)
        if not middles:
            middles = ["전체"]  # 중분류 추출 실패 시 전체로 1회 호출

        push_log(sess, f"[TC 작성] [{i+1}/{len(domains)}] {domain_code} — {domain_name} ({len(middles)}개 중분류)")

        domain_tc_parts = []
        # TC ID 스킴 분기 (tc-rules.md 섹션 2-1):
        #   - Suite-based (PC Web, SC): 중분류 전체에 걸쳐 cumulative seq
        #   - Screen-based (Mobile, SM): 화면(중분류)별 독립 seq, SuiteCode 자리에 ScreenCode 사용
        project_code = _detect_project_code(project_name)
        domain_suite_code = domain.get("suite_code", "").strip().strip("-")
        # 사용자 명시적 선택(auto_screen_code)이 있으면 우선, 없으면 프로젝트 코드 자동 판별
        user_auto_flag = sess.get("auto_screen_code")
        if user_auto_flag is True:
            screen_based = True
            scheme_reason = "사용자 선택: 시스템 규칙 자동 적용"
        elif user_auto_flag is False:
            screen_based = False
            scheme_reason = "사용자 선택: 수동 SuiteCode 입력"
        else:
            screen_based = _is_screen_based(project_code)
            scheme_reason = f"자동 판별 (project_code={project_code})"
        screen_map = load_screen_code_map(project_name) if screen_based else {}
        if screen_based:
            push_log(sess, f"[TC 작성] {domain_code} — Screen-based 스킴 ({scheme_reason}, map {len(screen_map)}개)")
        else:
            push_log(sess, f"[TC 작성] {domain_code} — Suite-based 스킴 ({scheme_reason})")

        cumulative_seq = 1  # Suite-based 전용 (Screen-based는 매 중분류마다 1로 리셋)
        # Screen-based 스킴: 이미 사용한 ScreenCode 추적 — 같은 코드가 여러 중분류에 매핑되면
        # 두 번째부터 접미사를 붙여 TC ID 충돌(SC-CON-001 3회 생성 등)을 방지한다.
        used_screen_codes = set()

        for mi, middle in enumerate(middles):
            label = f"{domain_code}/{middle}" if middle != "전체" else domain_code

            # 스킴별 effective code & starting seq 결정
            screen_character = ""
            screen_navigation = ""
            if screen_based and middle != "전체":
                # resolve_screen_code가 used_screen_codes를 참조해 충돌 시 마지막 단어를 1자씩 확장
                # 예: GOWE 충돌 → GOWEB → GOWEBV → 그래도 충돌이면 GOWE2 숫자 폴백
                effective_code = resolve_screen_code(middle, screen_map, used_screen_codes)
                # 이론적으로 resolve_screen_code가 유일한 코드를 반환하지만, 매핑 파일이 중복된 극단 케이스를 방어
                if effective_code in used_screen_codes:
                    for suffix in range(2, 100):
                        cand = f"{effective_code}{suffix}"
                        if cand not in used_screen_codes:
                            push_log(sess, f"[TC 작성] ⚠️ ScreenCode 최종 충돌 — {effective_code} → {cand} ({middle})")
                            effective_code = cand
                            break
                used_screen_codes.add(effective_code)

                screen_character = resolve_screen_character(middle, screen_map)
                screen_navigation = resolve_screen_navigation(middle, screen_map)
                starting_seq = 1  # 화면 단위 독립 네임스페이스
                id_scope_label = f"{effective_code} (screen)"
            else:
                effective_code = domain_suite_code
                starting_seq = cumulative_seq
                id_scope_label = f"{effective_code} (suite)" if effective_code else "(no-code)"

            meta_msg = ""
            if screen_character:
                meta_msg += f" [성격: {screen_character}]"
            if screen_navigation:
                meta_msg += f" [네비: {screen_navigation}]"
            push_log(sess, f"[TC 작성] [{i+1}/{len(domains)}] {label} 작성 중... "
                            f"→ SM-{effective_code}-{starting_seq:03d}~ [{id_scope_label}]{meta_msg}")
            push(sess, "stage", {
                "stage": 4,
                "label": f"TC 작성: {label} ({mi+1}/{len(middles)})",
                "pct": 55 + int(25 * ((i * len(middles) + mi) / max(len(domains) * len(middles), 1)))
            })

            system = build_tc_system_prompt(tc_rules, approved_classification, project_policies, fewshot)

            # 섹션 발췌 모드: Quick 모드 또는 정책 반영 모드(최적화) 모두에서 원문 발췌 활성
            # (`_section_extract` = 정책 반영 모드 TC 최적화, `_quick_mode` = Quick 전용 플래그)
            effective_features = features_text
            effective_policy = policy_text
            use_section = (sess.get("_quick_mode") or sess.get("_section_extract"))
            if use_section and middle != "전체":
                raw_full = sess.get("_raw_text", "")
                section = extract_section_from_raw(raw_full, middle, major_name=domain_name)
                if section:
                    effective_features = section
                    if sess.get("_quick_mode"):
                        effective_policy = section  # Quick은 원문 근거만
                        push_log(sess, f"[Quick 3/3] {label} — 원문 섹션 발췌 ({len(section):,}자)")
                    else:
                        # 정책 반영 모드: 원문 섹션 + 정책 요약 앞부분(≤4KB) 병행
                        effective_policy = (policy_text[:4000] + "\n\n---\n\n원문 섹션:\n" + section) if policy_text else section
                        push_log(sess, f"[정책+섹션] {label} — 원문 섹션 발췌 ({len(section):,}자)")
                # 섹션을 못 찾으면 features_text로 폴백

            # 중분류 단위 프롬프트 — 해당 중분류에 집중, effective_code & starting_seq & 성격 & 네비 전달
            # 입력 소스 SCR 매핑 (v0.9.13~) — AI 가 화면 코드 환각 안 하도록 명시적 주입
            _scr_map = sess.get("_source_scr_map") or {}
            if middle != "전체":
                domain_with_middle = dict(domain)
                domain_with_middle["_focus_middle"] = middle
                domain_with_middle["suite_code"] = effective_code  # screen-based면 ScreenCode로 교체
                user = build_tc_user_prompt(domain_with_middle, effective_features, effective_policy,
                                            project_name, approved_classification,
                                            starting_seq=starting_seq,
                                            screen_character=screen_character,
                                            screen_navigation=screen_navigation,
                                            source_scr_map=_scr_map)
            else:
                domain_copy = dict(domain)
                domain_copy["suite_code"] = effective_code
                user = build_tc_user_prompt(domain_copy, features_text, policy_text,
                                            project_name, approved_classification,
                                            starting_seq=starting_seq,
                                            screen_character=screen_character,
                                            screen_navigation=screen_navigation,
                                            source_scr_map=_scr_map)

            try:
                tc_draft = call_claude(system, user, max_tokens=16000)
            except Exception as e:
                push_log(sess, f"[TC 작성] {label} 오류: {e}, 재시도...")
                time.sleep(2)
                try:
                    tc_draft = call_claude(system, user, max_tokens=16000)
                except Exception as e2:
                    push_log(sess, f"[TC 작성] {label} 실패 (건너뜀): {e2}")
                    continue

            # 잘림 감지
            last_tc_match = list(re.finditer(r"^###\s", tc_draft, re.MULTILINE))
            if last_tc_match:
                last_tc_block = tc_draft[last_tc_match[-1].start():]
                if "**테스트 단계**" not in last_tc_block or "**예상 결과**" not in last_tc_block:
                    push_log(sess, f"[TC 작성] {label} 마지막 TC 불완전 — 이어서 생성 중...")
                    try:
                        continuation = call_claude(system, f"이전 응답이 잘렸습니다. 아래 TC를 완성하세요.\\n\\n---\\n{last_tc_block}", max_tokens=4096)
                        tc_draft = tc_draft[:last_tc_match[-1].start()] + continuation
                    except Exception:
                        pass

            # Post-processing: TC ID 재번호링 (유니크 강제)
            if effective_code:
                tc_draft, next_seq = renumber_tc_ids(tc_draft, project_code, effective_code, starting_seq)
                renumbered_count = next_seq - starting_seq
                if screen_based:
                    # 화면별 독립 카운트 — cumulative_seq는 건드리지 않음
                    push_log(sess, f"[TC 작성] {label} 완료 — TC {renumbered_count}개 "
                                    f"(SM-{effective_code}-001~{next_seq-1:03d})")
                else:
                    cumulative_seq = next_seq
                    push_log(sess, f"[TC 작성] {label} 완료 — TC {renumbered_count}개 (seq ~{cumulative_seq-1:03d})")
                total_tc += renumbered_count
            else:
                tc_count = len(re.findall(r"^###\s", tc_draft, re.MULTILINE))
                tc_count -= len(re.findall(r"^###\s*카테고리\s*\d", tc_draft, re.MULTILINE))
                push_log(sess, f"[TC 작성] {label} 완료 — TC {tc_count}개")
                total_tc += tc_count

            domain_tc_parts.append(tc_draft)
            check_stop(sess)

        # 대분류별 병합 저장
        merged = "\n\n---\n\n".join(domain_tc_parts)
        draft_path = sess["workspace"] / f"tc_draft_{domain_code}.md"
        draft_path.write_text(merged, encoding="utf-8")
        all_tc_parts.append(merged)
        push_log(sess, f"[TC 작성] {domain_code} 전체 완료 — TC {total_tc}개 (누적)")
        check_stop(sess)

    if not all_tc_parts:
        raise RuntimeError("TC 작성 결과가 없습니다.")

    min_tc = max(1, round(total_tc * 0.35))
    return "\n\n---\n\n".join(all_tc_parts), total_tc, min_tc


def extract_domains(classification: str) -> list[dict]:
    domains = []
    for line in classification.splitlines():
        line = line.strip()
        if not line.startswith("## "):
            continue
        text = line[3:].strip()
        # "대분류:" 접두사 제거
        text = re.sub(r"^대분류[:\s]*", "", text).strip()
        if not text or text.startswith("#"):
            continue
        # 괄호 코드 있으면 추출, 없으면 이름을 코드로 사용
        cm = re.search(r"[\(\（]([A-Z]{2,8})[\)\）]", text)
        if cm:
            code = cm.group(1)
            name = re.sub(r"\s*[\(\（][A-Z]{2,8}[\)\）]", "", text).strip()
        else:
            name = text
            # 이름에서 코드 자동 생성 (영문 대문자 약어)
            code = re.sub(r"[^A-Za-z]", "", name).upper()[:6] or "FUNC"
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
    return f"""당신은 전문 소프트웨어 QA 엔지니어입니다. 주어진 대분류의 테스트 케이스를 작성합니다.

## TC 작성 규칙

{tc_rules if tc_rules else "표준 TC 형식을 따릅니다."}
{policy_section}{fewshot_section}
## 분류표
{classification[:10000]}

## TC 생성 카테고리 (4가지 — 순서대로 작성, 비율 준수)

각 중분류에 대해 아래 4가지 카테고리 순서로 TC를 작성하세요.
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
| 대분류 | {{대분류명}} |
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


def _is_screen_based(project_code: str) -> bool:
    """Screen-based TC ID 스킴을 사용하는 프로젝트 판정.

    - SM (Mobile Web), SA (Mobile App) → Screen-based (화면별 001~)
    - SC (PC Web) 등 → Suite-based (Suite 내 전역 001~)
    """
    return project_code.upper() in ("SM", "SA")


# Screen Code Map 로더 (프로젝트별 projects/{name}/screen_code_map.md 파싱)
# 매핑 구조: { middle_name: { "code": "SPL", "character": "entry" } }
_SCREEN_CODE_CACHE: dict[str, dict[str, dict[str, str]]] = {}

# 성격(character) → 필수 비기능 TC 가이드 (원칙 E, tc-rules.md §1-1)
SCREEN_CHARACTER_NFR_GUIDE = {
    "entry": "로딩 시간 3초 이내 (Google RAIL 기준). [미결] 임계치 PM 확정 필요.",
    "data-fetch": "초기 로딩 5초 이내 + 빈 상태 표시 + Pull-to-refresh. [미결] 임계치 확정 필요.",
    "realtime": "WebSocket 끊김 시 자동 재연결 + 지연 표시 인라인 배너. 재연결 10초 이내.",
    "form": "입력 반응 100ms 이내 (RAIL First-Input-Delay, 선택적).",
    "overlay": "외부 영역 탭 시 자동 닫힘 + 진입/퇴장 애니메이션 부드러움.",
    "static": "비기능 TC 불필요 (정적 컨텐츠, 스크롤만).",
}

# 네비게이션(navigation) → 필수 뒤로가기/스와이프 TC 가이드 (원칙 F, tc-rules.md §1-1)
SCREEN_NAVIGATION_TC_GUIDE = {
    "tab-root": "탭바 최상위 — 뒤로가기 시 앱 종료 확인 모달 또는 Splash 복귀. 브라우저 뒤로가기 특수 처리 확인.",
    "one-way": "⚠️ **이전 화면 복귀 금지** — 뒤로가기/iOS 스와이프 백 제스처 시 이전 화면(인증·주문 플로우)으로 돌아가면 안 됨. 차단 또는 홈 이동 또는 확인 모달. 재실행 방지 검증.",
    "sequential": "뒤로가기 → 이전 단계 화면 복귀 + 입력값(이메일·코드·약관 체크) 유지 확인.",
    "overlay": "뒤로가기 / 외부 영역 탭 / Escape → 오버레이만 닫힘, 배경 화면 상태 그대로 유지.",
    "detail": "뒤로가기 → 리스트 화면 복귀 + 이전 스크롤 위치 유지.",
    "static": "뒤로가기 → 상위 화면 자연 복귀 (depth 2+ 에서만 확인 TC 추가).",
}


def load_screen_code_map(project_name: str) -> dict[str, dict[str, str]]:
    """projects/{project}/screen_code_map.md를 파싱.

    Returns:
        {middle_name: {"code": str, "character": str, "navigation": str}}
    파일 테이블 형식:
        `| Middle | Code | 성격 | 네비 | SCR-ID | 설명 |`
        성격/네비 컬럼은 선택. 없으면 빈 문자열.
    """
    cache_key = project_name.lower()
    if cache_key in _SCREEN_CODE_CACHE:
        return _SCREEN_CODE_CACHE[cache_key]

    if not PROJECTS_RULES_DIR.exists():
        _SCREEN_CODE_CACHE[cache_key] = {}
        return {}

    pname_lower = project_name.lower().replace(" ", "").replace("-", "").replace("_", "")
    mapping: dict[str, dict[str, str]] = {}
    valid_chars = {"entry", "data-fetch", "realtime", "form", "overlay", "static"}
    valid_navs  = {"tab-root", "one-way", "sequential", "overlay", "detail", "static"}
    for folder in PROJECTS_RULES_DIR.iterdir():
        if not folder.is_dir():
            continue
        fname_lower = folder.name.lower().replace(" ", "").replace("-", "").replace("_", "")
        if fname_lower not in pname_lower and pname_lower not in fname_lower:
            continue
        map_file = folder / "screen_code_map.md"
        if not map_file.exists():
            continue
        text = map_file.read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("|") or not line.endswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            middle, code = cells[0], cells[1]
            if not middle or not code:
                continue
            if re.match(r"^-+$", middle) or middle.lower() in ("middle name", "이름"):
                continue
            if not re.fullmatch(r"[A-Z]{2,5}", code):
                continue
            # 3번째 셀: 성격 (선택)
            character = ""
            if len(cells) >= 3:
                cand = cells[2].lower().strip()
                if cand in valid_chars:
                    character = cand
            # 4번째 셀: 네비게이션 (선택)
            navigation = ""
            if len(cells) >= 4:
                cand = cells[3].lower().strip()
                if cand in valid_navs:
                    navigation = cand
            # navigation이 비어있으면 character 기반 기본 추론
            if not navigation:
                if character == "overlay":
                    navigation = "overlay"
                elif character == "static":
                    navigation = "static"
                else:
                    navigation = "sequential"  # 안전한 기본값
            if middle not in mapping:
                mapping[middle] = {
                    "code": code,
                    "character": character,
                    "navigation": navigation,
                }
        break

    _SCREEN_CODE_CACHE[cache_key] = mapping
    return mapping


def resolve_screen_code(middle_name: str, screen_map: dict,
                         used_codes: set | None = None) -> str:
    """중분류 이름을 ScreenCode로 변환 (v0.9.7b 규칙).

    ┌─ 규칙 ────────────────────────────────────────────────────
    │ 1. screen_map에 명시적 매핑이 있으면 그대로 사용 (최우선)
    │ 2. 없으면 자동 파생:
    │    - 1단어     → 앞 3자         (예: Splash → SPL)
    │    - 2단어     → 각 단어 앞 2자  (예: Email Input → EMIN)
    │    - 3단어 이상 → 앞 단어들 2자 + 마지막 단어 1자
    │                  (예: Google OAuth Start → GOOAS)
    │ 3. 최대 8자로 절단, 대문자화
    │ 4. used_codes와 충돌하면 마지막 단어를 1자씩 확장
    │    (예: GOOAC 충돌 → GOOACO → GOOACOM ...)
    │ 5. 그래도 충돌하면 숫자 접미사 폴백 (GOOAC2)
    │ 6. 영문자가 전혀 없으면 해시 기반 MID### 폴백
    └────────────────────────────────────────────────────────────
    """
    if not middle_name:
        return "SCR"

    # 1단계: screen_map 정확 일치
    if middle_name in screen_map:
        entry = screen_map[middle_name]
        if isinstance(entry, dict):
            return entry.get("code") or "SCR"
        return entry

    # 2단계: 단어 분해 — 공백/하이픈/언더스코어 단위 + 영문자만 추출
    words = [re.sub(r"[^A-Za-z]", "", w) for w in re.split(r"[\s\-_]+", middle_name) if w]
    words = [w for w in words if w]
    if not words:
        return f"MID{abs(hash(middle_name)) % 1000:03d}"

    # 2단계 계속: 단어 수별 기본 파생
    if len(words) == 1:
        base = words[0][:3].upper()
    elif len(words) == 2:
        base = (words[0][:2] + words[1][:2]).upper()
    else:  # 3단어 이상
        head = "".join(w[:2] for w in words[:-1])
        tail = words[-1][:1]
        base = (head + tail).upper()

    # 3단계: 최대 8자 절단
    base = base[:8]
    if not base:
        return f"MID{abs(hash(middle_name)) % 1000:03d}"

    # 4단계: 충돌 없으면 반환
    if used_codes is None or base not in used_codes:
        return base

    # 4단계 계속: 마지막 단어를 1자씩 확장 시도
    # base는 "앞 단어들의 앞 N자" + "마지막 단어의 앞 1~2자" 구조
    if len(words) >= 2:
        last = words[-1]
        # 마지막 단어 사용 자수: 2단어면 2자, 3단어 이상이면 1자
        last_used_n = 2 if len(words) == 2 else 1
        head_part = base[:-last_used_n]
        # extra_len을 키우며 시도
        for extra_len in range(last_used_n + 1, len(last) + 1):
            cand = (head_part + last[:extra_len]).upper()[:8]
            if cand not in used_codes:
                return cand
    else:
        # 단일 단어: 글자 수 늘려가며 시도
        w = words[0]
        for extra_len in range(4, len(w) + 1):
            cand = w[:extra_len].upper()[:8]
            if cand not in used_codes:
                return cand

    # 5단계: 숫자 접미사 폴백
    for n in range(2, 100):
        cand = f"{base}{n}"[:8]
        if cand not in used_codes:
            return cand
    return base  # 극단 케이스 — 호출부에서 추가 처리


def resolve_screen_character(middle_name: str, screen_map: dict) -> str:
    """Middle 이름의 성격(character) 반환. 맵에 없으면 빈 문자열.

    비기능 TC 조건부 생성 (원칙 E)에서 프롬프트 힌트로 사용.
    """
    if not middle_name or middle_name not in screen_map:
        return ""
    entry = screen_map[middle_name]
    if isinstance(entry, dict):
        return entry.get("character", "")
    return ""


def resolve_screen_navigation(middle_name: str, screen_map: dict) -> str:
    """Middle 이름의 네비게이션 분류 반환. 맵에 없으면 빈 문자열.

    뒤로가기/스와이프 TC 조건부 생성 (원칙 F)에서 프롬프트 힌트로 사용.
    """
    if not middle_name or middle_name not in screen_map:
        return ""
    entry = screen_map[middle_name]
    if isinstance(entry, dict):
        return entry.get("navigation", "")
    return ""


def detect_same_result_duplicates(tc_md: str) -> dict:
    """같은 화면 안에서 '예상 결과' 가 거의 동일한 TC 그룹을 검출.

    정책 A 의 후처리 안전망: AI 가 통합을 안 했을 경우 검토자가 확인할 수 있도록
    의심 그룹을 리포트로 만든다. 자동 병합은 하지 않음 (false positive 위험).

    매칭 기준:
      - 같은 대분류 + 같은 중분류 (= 같은 화면)
      - 사전 조건의 핵심 줄 1~3 개가 같음 (마지막 줄 "...상태" 정규화 비교)
      - 예상 결과의 핵심 결과 1~2개가 같음 (불릿 정규화 후 80% 이상 일치)

    Returns:
        {
          "groups": [
            {
              "middle": "Order Confirm",
              "common_result": "시트가 닫히고 SCR-102 로 복귀한다",
              "tcs": [
                {"id": "SM-TRAD-012", "title": "Cancel 버튼 탭으로 시트 닫기"},
                {"id": "SM-TRAD-013", "title": "배경 오버레이 탭으로 시트 닫기"},
              ],
            },
            ...
          ],
          "total_suspect": 4,    # 통합 대상이 될 수 있는 TC 수
        }
    """
    from collections import defaultdict

    # TC 블록 파싱 — 각 TC 의 (대분류, 중분류, 예상 결과 정규화) 추출
    tc_blocks = re.split(r"\n(?=###\s)", tc_md)
    tcs_by_screen: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for block in tc_blocks:
        if not block.strip().startswith("### "):
            continue
        # TC ID 추출
        m_id = re.search(r"###\s+\*?\*?([A-Z]+-[A-Z]+-\d+)", block)
        if not m_id:
            continue
        tc_id = m_id.group(1)
        # 제목
        m_title = re.search(r"###\s+\*?\*?[A-Z]+-[A-Z]+-\d+\*?\*?\s*[—\-]\s*(.+)", block)
        title = m_title.group(1).strip() if m_title else ""
        # 대/중분류
        m_major = re.search(r"\|\s*대분류\s*\|\s*([^|]+?)\s*\|", block)
        m_middle = re.search(r"\|\s*중분류\s*\|\s*([^|]+?)\s*\|", block)
        major = m_major.group(1).strip() if m_major else ""
        middle = m_middle.group(1).strip() if m_middle else ""
        # 예상 결과 — 첫 2줄만 (핵심 검증 지표)
        m_then = re.search(r"\*\*예상\s*결과\*\*\s*\n((?:[^\n]+\n){1,5})", block)
        then_lines = []
        if m_then:
            for line in m_then.group(1).split("\n"):
                norm = re.sub(r"^[\-\*\d.\s]+", "", line).strip()
                norm = re.sub(r"\s+", " ", norm)
                # 의미 없는 짧은 줄 제외
                if len(norm) >= 8:
                    then_lines.append(norm)
        # 핵심 결과 키 (앞 2줄)
        result_key = " | ".join(sorted(then_lines[:2])) if then_lines else ""
        if not result_key or not middle:
            continue

        tcs_by_screen[(major, middle, result_key)].append({
            "id": tc_id, "title": title,
        })

    # 같은 키에 2개 이상 → 의심 그룹
    groups = []
    total_suspect = 0
    for (major, middle, result_key), tcs in tcs_by_screen.items():
        if len(tcs) >= 2:
            groups.append({
                "middle": middle,
                "common_result": result_key[:120] + ("..." if len(result_key) > 120 else ""),
                "tcs": tcs,
            })
            total_suspect += len(tcs) - 1  # 통합 시 줄어들 수

    return {"groups": groups, "total_suspect": total_suspect}


def detect_duplicate_error_tcs(tc_md: str) -> dict:
    """원칙 G — 같은 그룹 내 동일 비기능 패턴 TC 가 여러 화면에 반복되는 경우 검출.

    탐지 패턴 (제목 + 분류 기반):
      - 네트워크 끊김 / 연결 실패
      - 타임아웃
      - 3G / 저사양 / 로딩 시간
      - 백그라운드 / 포그라운드
      - 화면 회전
      - 메모리 부족 / 강제 종료

    Returns:
        {
          "patterns": [
            {
              "pattern": "네트워크 끊김",
              "major": "01.로그인_Gmail",
              "tcs": [
                {"id": "SM-LGI-007", "title": "...", "middle": "Google Sign-in"},
                {"id": "SM-LGI-013", "title": "...", "middle": "OAuth Confirm"},
              ],
              "count": 2,
            },
            ...
          ],
          "total_duplicates": 12,    # 통합 시 줄어들 TC 수
          "suggested_keep": [...],    # 유지 권장 TC IDs (대표 화면)
          "suggested_remove": [...],  # 제거 권장 TC IDs
        }

    중복 패턴이 없으면 patterns=[], total_duplicates=0.
    """
    # 패턴 키워드 — 한글/영문 모두 매칭
    patterns_def = [
        ("네트워크 끊김", [r"네트워크\s*(끊김|차단|단절|장애|불안정)", r"연결\s*실패", r"오프라인", r"network\s*(disconnect|fail)", r"connection\s*(lost|fail)"]),
        ("타임아웃", [r"타임\s*아웃", r"응답\s*지연", r"timeout"]),
        ("3G/저사양 로딩 시간", [r"3G\s*(환경|네트워크)?", r"저사양", r"로딩\s*시간", r"loading\s*time"]),
        ("백그라운드/포그라운드", [r"백그라운드", r"포그라운드", r"background", r"foreground"]),
        ("화면 회전", [r"화면\s*회전", r"orientation\s*change"]),
        ("메모리/강제 종료", [r"메모리\s*부족", r"앱\s*(강제\s*)?종료", r"out\s*of\s*memory", r"force\s*(close|quit|kill)"]),
    ]

    if not tc_md:
        return {"patterns": [], "total_duplicates": 0, "suggested_keep": [], "suggested_remove": []}

    # TC 블록 분할 — `### ` 또는 `### **` 헤더 기준
    blocks = re.split(r'(?=^###\s)', tc_md, flags=re.MULTILINE)

    detected = {}  # {(pattern, major): [tc_info, ...]}

    for block in blocks:
        if not block.strip().startswith("###"):
            continue
        # TC ID 추출
        m_id = re.match(r'###\s+\*?\*?([A-Z0-9-]+(?:-\d+)+)\*?\*?\s*(?:—|-)?\s*(.*?)(?:\n|$)', block)
        if not m_id:
            continue
        tc_id = m_id.group(1).strip()
        title = m_id.group(2).strip().rstrip('*').strip()
        # 대분류 / 중분류 추출 (테이블 형식)
        m_major = re.search(r'\|\s*대분류\s*\|\s*([^|]+?)\s*\|', block)
        m_middle = re.search(r'\|\s*중분류\s*\|\s*([^|]+?)\s*\|', block)
        major = m_major.group(1).strip() if m_major else ""
        middle = m_middle.group(1).strip() if m_middle else ""
        if not major:
            continue

        # 패턴 매칭 (title + middle 텍스트 합쳐서 검색)
        search_text = f"{title}\n{middle}".lower()
        for pattern_label, regexes in patterns_def:
            matched = any(re.search(rgx, search_text, re.IGNORECASE) for rgx in regexes)
            if matched:
                key = (pattern_label, major)
                detected.setdefault(key, []).append({
                    "id": tc_id,
                    "title": title,
                    "middle": middle,
                })
                break  # 한 TC 가 여러 패턴 매칭돼도 가장 먼저 잡힌 것만

    # 결과 가공: 같은 (패턴, 대분류) 에 2개 이상 있으면 중복으로 간주
    patterns_out = []
    suggested_keep = []
    suggested_remove = []
    total_duplicates = 0
    for (pattern_label, major), tcs in detected.items():
        if len(tcs) < 2:
            continue
        # TC ID 의 가장 작은 번호를 대표(유지) 로 — 일반적으로 entry 화면이 먼저 등장
        tcs_sorted = sorted(tcs, key=lambda t: t["id"])
        keep = tcs_sorted[0]
        remove_list = tcs_sorted[1:]
        suggested_keep.append(keep["id"])
        suggested_remove.extend([t["id"] for t in remove_list])
        total_duplicates += len(remove_list)
        patterns_out.append({
            "pattern": pattern_label,
            "major": major,
            "tcs": tcs_sorted,
            "count": len(tcs_sorted),
            "keep": keep["id"],
            "remove": [t["id"] for t in remove_list],
        })

    return {
        "patterns": patterns_out,
        "total_duplicates": total_duplicates,
        "suggested_keep": suggested_keep,
        "suggested_remove": suggested_remove,
    }


def predict_classification_duplicates(classification_md: str) -> dict:
    """분류표(TC 작성 전) 단계에서 중복 가능성 예측 — Stage 1.

    TC ID 가 아직 없으므로 휴리스틱 기반:
      1. 같은 대분류 내 중분류 5개 이상 → AI 가 비기능 TC 반복 작성 가능성 높음
      2. 같은 대분류 내 여러 중분류에 같은 소분류 키워드 등장 (예: 모두에 "로딩") → 통합 후보

    Returns:
      {
        "predictions": [
          {
            "type": "group_size" | "shared_minor",
            "major": "01.로그인_Gmail",
            "middle_count": 5,
            "middles": [...],
            "shared_keyword": "로딩 시간" (shared_minor 일 때만),
            "predicted_pattern": "비기능 TC (네트워크/타임아웃/로딩) 가 반복될 가능성 높음",
            "recommendation": "그룹 entry 화면 1개에만 비기능 TC 작성 권장"
          },
          ...
        ],
        "high_risk_count": int,
      }
    """
    if not classification_md:
        return {"predictions": [], "high_risk_count": 0}

    # 분류표 파싱: ## 대분류 / ### 중분류 / 소분류 불릿
    majors = {}  # {major_name: {middle_name: [minor1, minor2, ...]}}
    cur_major = None
    cur_middle = None
    for line in classification_md.split('\n'):
        line = line.rstrip()
        # 대분류 헤더: ## 또는 ## 대분류:
        m_major = re.match(r'^##\s+(?:대분류[:\s]*)?(.+?)\s*$', line)
        m_middle = re.match(r'^###\s+(?:중분류[:\s]*)?(.+?)\s*$', line)
        if m_major and not line.startswith('###') and not line.startswith('####'):
            name = m_major.group(1).strip()
            # '소분류' 이런 건 대분류가 아님
            if name and name not in ('소분류', '중분류'):
                cur_major = name
                cur_middle = None
                majors.setdefault(cur_major, {})
        elif m_middle and cur_major:
            mid_name = m_middle.group(1).strip()
            if mid_name and mid_name != '소분류':
                cur_middle = mid_name
                majors[cur_major].setdefault(cur_middle, [])
        elif cur_major and cur_middle:
            # 소분류 불릿: - 또는 *
            m_minor = re.match(r'^\s*[-*]\s+(.+?)\s*$', line)
            if m_minor:
                minor_text = m_minor.group(1).strip()
                # 콜론 앞부분만 추출 (예: "로딩 시간: 3G 환경..." → "로딩 시간")
                minor_label = minor_text.split(':', 1)[0].split('—', 1)[0].strip()
                if minor_label and minor_label != '소분류':
                    majors[cur_major][cur_middle].append(minor_label)

    predictions = []

    # 휴리스틱 1: 그룹 크기 (중분류 5개 이상)
    SIZE_THRESHOLD = 5
    for major_name, middles in majors.items():
        if len(middles) >= SIZE_THRESHOLD:
            predictions.append({
                "type": "group_size",
                "major": major_name,
                "middle_count": len(middles),
                "middles": list(middles.keys()),
                "predicted_pattern": "비기능 TC (네트워크/타임아웃/로딩 시간 등) 가 여러 화면에 반복 작성될 가능성 높음",
                "recommendation": "그룹의 entry 성격 화면 1개에만 비기능 TC 작성 권장 (원칙 G)"
            })

    # 휴리스틱 2: 같은 대분류 내 여러 중분류에 동일 소분류 키워드 등장
    DUPLICATE_KEYWORDS = [
        '로딩 시간', '네트워크', '타임아웃', '백그라운드', '포그라운드',
        '화면 회전', '메모리', '강제 종료', '오프라인',
    ]
    for major_name, middles in majors.items():
        # 각 키워드가 몇 개 중분류에 등장하는지 카운트
        keyword_hits = {kw: [] for kw in DUPLICATE_KEYWORDS}
        for mid_name, minors in middles.items():
            for minor_label in minors:
                for kw in DUPLICATE_KEYWORDS:
                    if kw in minor_label:
                        keyword_hits[kw].append(mid_name)
                        break
        for kw, mids_with_kw in keyword_hits.items():
            if len(mids_with_kw) >= 2:
                # 그룹 크기 휴리스틱과 중복 안 되게 — 같은 major 가 이미 group_size 로 들어가 있으면 키워드만 추가
                existing = next((p for p in predictions if p["major"] == major_name and p["type"] == "group_size"), None)
                if existing:
                    existing.setdefault("shared_keywords", []).append({"keyword": kw, "middles": mids_with_kw})
                else:
                    predictions.append({
                        "type": "shared_minor",
                        "major": major_name,
                        "middle_count": len(middles),
                        "middles": list(middles.keys()),
                        "shared_keyword": kw,
                        "shared_in_middles": mids_with_kw,
                        "predicted_pattern": f'"{kw}" 관련 소분류가 여러 중분류에 등장 — 통합 후보',
                        "recommendation": f'"{kw}" 검증은 그룹 대표 화면 1개에서만 권장'
                    })

    return {
        "predictions": predictions,
        "high_risk_count": len(predictions),
    }


def disambiguate_duplicate_minors(tc_md: str) -> str:
    """같은 (대분류, 중분류) 안에서 동일한 소분류 이름이 여러 TC에 쓰인 경우,
    각 TC의 제목(### 헤더 뒤 — 이후 부분)에서 핵심 키워드를 추출하여
    소분류 뒤에 ` — {키워드}` 형태로 자동 부여한다.

    예: 같은 중분류 'Splash'에 소분류 'Splash 화면 진입' × 4개
        TC들의 제목이 'UI 요소 표시', 'Get Started 버튼 탭', '뒤로가기 동작', '로딩 시간' 이라면
        → 각각 'Splash 화면 진입 — UI 요소 표시', '... — Get Started 버튼 탭' ...

    원칙:
    - 같은 (대,중,소) 그룹의 TC가 1개뿐이면 변경하지 않음 (불필요한 변형 회피)
    - 이미 다른 소분류 이름이면 변경하지 않음
    - 변형 결과의 길이는 60자 이내로 제한 (Excel 가독성)
    - title이 비어있거나 추출 실패 시 (1), (2) 같은 일련번호 fallback
    """
    if not tc_md:
        return tc_md

    # 1단계: TC 블록 단위로 분리 + 각 블록에서 (major, middle, minor, title) 추출
    blocks = re.split(r"(?m)^(?=###\s)", tc_md)
    parsed = []  # [(idx, block_text, major, middle, minor, title), ...]
    for idx, block in enumerate(blocks):
        if not block.lstrip().startswith("###"):
            parsed.append((idx, block, None, None, None, None))
            continue
        first_line = block.split("\n", 1)[0]
        # 카테고리/대중소분류 헤더 등 제외
        if re.match(r"^###\s*(카테고리|대분류|중분류|소분류|Category)\s*[:：\d]", first_line, re.IGNORECASE):
            parsed.append((idx, block, None, None, None, None))
            continue
        # 제목 추출 (— 뒤)
        cleaned = re.sub(r"\*\*", "", first_line)
        m = re.match(r"^###\s+\S+\s+—\s+(.+?)\s*$", cleaned)
        title = m.group(1).strip() if m else ""
        # 메타 테이블 필드
        major = _extract_md_field(block, "대분류")
        middle = _extract_md_field(block, "중분류")
        minor = _extract_md_field(block, "소분류")
        parsed.append((idx, block, major, middle, minor, title))

    # 2단계: (major, middle, minor) 그룹별 등장 인덱스 수집
    from collections import defaultdict as _dd
    groups = _dd(list)
    for idx, block, major, middle, minor, title in parsed:
        if major and middle and minor:
            groups[(major, middle, minor)].append((idx, title))

    # 3단계: 그룹 크기 >= 2인 경우만 변형 적용
    new_minors_per_idx: dict[int, str] = {}
    for (major, middle, minor), entries in groups.items():
        if len(entries) < 2:
            continue
        # 각 TC의 차별화 키워드 추출
        used_variants: set[str] = set()
        for ord_n, (idx, title) in enumerate(entries, 1):
            variant = _extract_minor_variant(title, minor)
            if not variant:
                # title에서 추출 불가 → 일련번호 폴백
                variant = f"({ord_n})"
            # 길이 제한 (소분류 + " — " + variant 합계 60자 이내)
            max_var_len = max(8, 60 - len(minor) - 3)
            if len(variant) > max_var_len:
                variant = variant[:max_var_len].rstrip()
            # 같은 그룹 내 variant 충돌 방지
            base_variant = variant
            n = 2
            while variant in used_variants:
                variant = f"{base_variant} ({n})"
                n += 1
            used_variants.add(variant)
            new_minors_per_idx[idx] = f"{minor} — {variant}"

    if not new_minors_per_idx:
        return tc_md  # 변형 없음

    # 4단계: 각 블록의 `| 소분류 | ... |` 라인을 새 값으로 치환
    out_blocks = []
    for idx, block, major, middle, minor, title in parsed:
        if idx in new_minors_per_idx and minor:
            new_minor = new_minors_per_idx[idx]
            # `| 소분류 | <기존> |` 첫 번째 매칭만 치환
            block = re.sub(
                r"(\|\s*소분류\s*\|\s*)" + re.escape(minor) + r"(\s*\|)",
                r"\g<1>" + new_minor.replace("\\", "\\\\") + r"\g<2>",
                block, count=1
            )
        out_blocks.append(block)
    return "".join(out_blocks)


def _extract_md_field(block: str, field: str) -> str:
    """TC 블록의 마크다운 테이블에서 특정 필드 값 추출."""
    m = re.search(rf"\|\s*{re.escape(field)}\s*\|\s*([^|]+?)\s*\|", block)
    return m.group(1).strip() if m else ""


def _extract_minor_variant(title: str, minor: str) -> str:
    """TC title에서 소분류와 차별화되는 키워드 추출.

    전략:
    1. title이 minor를 prefix/suffix로 이미 포함하면 그 부분만 잘라낸 나머지 사용
    2. minor의 핵심 단어와 겹치는 부분 제거 후 남은 핵심 부분
    3. 결과가 너무 짧거나 어색하면 title 그대로 사용 (단, 길이 제한)
    """
    if not title:
        return ""
    cleaned = re.sub(r"\s+", " ", title).strip()
    norm_title = cleaned
    norm_minor = minor.strip()

    # 1) prefix/suffix 일치 — minor가 그대로 포함되면 잘라내기
    if norm_minor and norm_title.startswith(norm_minor):
        leftover = norm_title[len(norm_minor):].strip(" -—:")
        if len(leftover) >= 4:
            return _trim_leading_function_words(leftover)[:40]
    if norm_minor and norm_title.endswith(norm_minor):
        leftover = norm_title[:-len(norm_minor)].strip(" -—:")
        if len(leftover) >= 4:
            return _trim_leading_function_words(leftover)[:40]

    # 2) minor의 단어와 title이 부분 일치 — title 자체가 더 구체적인 표현이면 그대로 사용
    minor_set = set(re.split(r"[\s\-—:_/()]+", norm_minor))
    title_words = re.split(r"[\s\-—:_/()]+", norm_title)
    # title 단어가 minor 단어보다 많으면 (= 더 구체적) title 사용
    if len([w for w in title_words if w not in minor_set and len(w) >= 2]) >= 2:
        return norm_title[:40]

    # 3) 마지막 폴백 — title 앞부분
    return norm_title[:40]


def _trim_leading_function_words(s: str) -> str:
    """문장 시작의 어색한 조사/접속어 제거 (예: '시 키보드 표시' → '키보드 표시')."""
    # 한국어 조사/접속어 + 영어 의미 없는 시작 단어
    pattern = r"^(시|에|의|에서|으로|로|가|이|는|은|을|를|와|과|the|a|an)\s+"
    while True:
        new_s = re.sub(pattern, "", s, flags=re.IGNORECASE)
        if new_s == s:
            break
        s = new_s
    return s.strip(" -—:")


def renumber_tc_ids(tc_md: str, project_code: str, suite_code: str, starting_seq: int) -> tuple[str, int]:
    """Markdown 내 TC ID(`{PC}-{SC}-NNN`)를 starting_seq부터 연속 재번호.

    같은 TC 블록(### ...) 안에서 여러 번 나오는 동일 ID는 하나로 취급.
    Suite 내 SeqNumber 전역 유니크 규칙 (tc-rules.md 섹션 2-1) 강제.

    Returns:
        (renumbered_md, next_seq_after_last)
    """
    if not suite_code:
        return tc_md, starting_seq

    pattern = re.compile(
        rf"({re.escape(project_code)}-{re.escape(suite_code)}-)(\d{{3,}})",
        re.IGNORECASE,
    )

    # 블록 분할: "### " 헤더 기준
    blocks = re.split(r"(?m)(?=^### )", tc_md)
    next_seq = starting_seq
    id_remap: dict[str, str] = {}

    for i, block in enumerate(blocks):
        header_match = re.match(r"^### .*", block)
        if not header_match:
            continue
        header = header_match.group(0)
        first = pattern.search(header)
        if not first:
            continue
        old_id = first.group(0)
        if old_id not in id_remap:
            new_id = f"{first.group(1)}{next_seq:03d}"
            id_remap[old_id] = new_id
            next_seq += 1

    # 모든 TC ID 치환 (블록 헤더 + 본문 참조 모두)
    def _sub(m: re.Match) -> str:
        old = m.group(0)
        return id_remap.get(old, old)

    return pattern.sub(_sub, tc_md), next_seq


def build_tc_user_prompt(domain: dict, features_text: str, policy_text: str,
                          project_name: str, classification: str,
                          starting_seq: int = 1,
                          screen_character: str = "",
                          screen_navigation: str = "",
                          source_scr_map: dict | None = None) -> str:
    # 해당 대분류의 분류 섹션 추출
    domain_section = extract_domain_section(classification, domain["code"])
    project_code = _detect_project_code(project_name)

    suite_code = domain.get("suite_code", "").strip().strip("-")  # trailing 하이픈 제거
    if suite_code:
        seq_str = f"{starting_seq:03d}"
        next_str = f"{starting_seq+1:03d}"
        example_id = f"{project_code}-{suite_code}-{seq_str}"
        tc_id_instruction = (
            f"⚠️ TC ID 형식: `{example_id}`, `{project_code}-{suite_code}-{next_str}`, ... "
            f"하이픈은 정확히 이 위치에만. `{project_code}-{suite_code}--001` 처럼 하이픈이 연속되면 안 됩니다.\n"
            f"⚠️ **Suite 내 SeqNumber 전역 유니크**: 이 호출의 시작 번호는 `{seq_str}`. "
            f"중분류가 바뀌어도 001로 리셋하지 말고 {seq_str}부터 연속 증가. "
            f"(tc-rules.md 섹션 2-1 SeqNumber 전역 유니크 규칙)"
        )
    else:
        tc_id_instruction = f"⚠️ TC ID의 ProjectCode: `{project_code}` (예: {project_code}-XXXX-001). `TC-`로 시작하면 안 됩니다."

    focus_middle = domain.get("_focus_middle", "")

    # 화면 성격별 비기능 TC 힌트 (tc-rules.md 원칙 E)
    nfr_instruction = ""
    if screen_character and screen_character != "static":
        guide = SCREEN_CHARACTER_NFR_GUIDE.get(screen_character, "")
        if guide:
            screen_label = focus_middle or "화면"
            nfr_instruction = (
                f"\n## ⚙️ 비기능 TC 필수 포함 (원칙 E — 화면 성격: `{screen_character}`)\n\n"
                f"이 화면은 `{screen_character}` 성격이므로 아래 비기능 TC를 **반드시 1개 이상** 포함하세요:\n"
                f"- {guide}\n\n"
                f"TC 작성 예시 (entry 성격 화면):\n"
                f"```\n"
                f"### {project_code}-{suite_code}-XXX — {screen_label} 로딩 시간\n"
                f"| 분류 | Edge |\n| 우선순위 | Medium |\n\n"
                f"**사전 조건**\n1. 3G 또는 저사양 기기 환경인 상태\n\n"
                f"**테스트 단계**\n화면 완전 표시까지의 시간을 측정한다.\n\n"
                f"**예상 결과**\n- (업계 표준 임계치) 이내에 표시된다\n\n"
                f"**비고**\n- [미결] 임계치는 업계 표준 기반 추정. PM 확정 필요.\n"
                f"```\n"
            )
    elif screen_character == "static":
        nfr_instruction = (
            f"\n## ⚙️ 비기능 TC (원칙 E — 화면 성격: `static`)\n\n"
            f"이 화면은 정적 컨텐츠이므로 **비기능 TC는 생성하지 마세요** (로딩·성능·실시간 TC 불필요).\n"
        )

    # 네비게이션 분류별 뒤로가기/스와이프 TC 힌트 (tc-rules.md 원칙 F)
    nav_instruction = ""
    if screen_navigation:
        nav_guide = SCREEN_NAVIGATION_TC_GUIDE.get(screen_navigation, "")
        screen_label = focus_middle or "화면"
        if screen_navigation == "one-way":
            nav_instruction = (
                f"\n## ⚠️ 뒤로가기/스와이프 TC 필수 (원칙 F — 네비게이션: `one-way`)\n\n"
                f"이 화면은 **완료 화면**이므로 뒤로가기 시 이전 화면 복귀를 차단해야 합니다:\n"
                f"- {nav_guide}\n\n"
                f"**반드시 아래 Negative TC를 1개 포함하세요** (우선순위 High):\n"
                f"```\n"
                f"### {project_code}-{suite_code}-XXX — {screen_label} 후 뒤로가기/스와이프 차단\n"
                f"| 분류 | Negative |\n| 우선순위 | High |\n\n"
                f"**사전 조건**\n1. 모바일 브라우저에서 접속한 상태\n"
                f"2. {screen_label} 화면에 진입 완료한 상태\n\n"
                f"**테스트 단계**\n브라우저 뒤로가기 버튼 또는 iOS 스와이프 백 제스처를 실행한다.\n\n"
                f"**예상 결과**\n- 이전 화면(인증·주문 등)으로 돌아가지 않는다\n"
                f"- 홈 이동 / 뒤로가기 차단 / 확인 모달 중 하나가 발생한다\n"
                f"- 이미 완료된 플로우를 재실행할 수 없는 상태가 유지된다\n\n"
                f"**비고**\n- [미결] 구체적 차단 방식은 PM 확정 필요\n"
                f"```\n"
            )
        elif screen_navigation in ("tab-root", "sequential", "overlay", "detail"):
            nav_instruction = (
                f"\n## ⚙️ 뒤로가기/스와이프 TC 포함 (원칙 F — 네비게이션: `{screen_navigation}`)\n\n"
                f"이 화면의 뒤로가기 동작을 검증하는 TC를 1개 포함하세요:\n"
                f"- {nav_guide}\n"
            )
        # static은 TC 불필요 (별도 instruction 없음)

    middle_instruction = ""
    if focus_middle:
        middle_instruction = f"""
⚠️ 이 호출에서는 중분류 "{focus_middle}"에 해당하는 TC만 상세하게 작성하세요.
다른 중분류의 TC는 작성하지 마세요. "{focus_middle}" 중분류의 모든 소분류에 대해 빠짐없이 작성하세요.
"""

    # 화면 코드는 입력 소스 자체에서 추출 (v0.9.13~)
    # 우선순위:
    #   1) source_scr_map: step_parse_sources 가 파일명/H1/본문에서 미리 뽑은 매핑 — 가장 정확
    #   2) _detect_screen_codes_for_middle: features_text 에서 중분류 이름 근처 SCR 패턴 탐색 (보조)
    #   3) 둘 다 없으면 → 빈 칸 명시 (AI 환각 금지)
    screen_code_hint = ""
    if focus_middle:
        # source_scr_map 에서 입력 파일별 매핑이 있으면 모두 안내 — AI 가 본문 컨텍스트로 해당 TC 의 SCR 결정
        scr_table_lines = []
        if source_scr_map:
            for fn, scr in source_scr_map.items():
                scr_table_lines.append(f"| {fn} | {scr} |")

        detected = _detect_screen_codes_for_middle(focus_middle, features_text)

        if scr_table_lines:
            scr_table = "\n".join(scr_table_lines)
            primary_example = list(source_scr_map.values())[0]
            allowed_scrs = list(source_scr_map.values())
            allowed_scrs_str = ", ".join(f"`{s}`" for s in allowed_scrs)
            screen_code_hint = f"""
## 📱 화면 코드 매핑 (입력 소스 기반 — 반드시 준수)

이 분류표는 다음 입력 소스에서 추출되었습니다. 각 TC 의 `| 연관 화면 |` 필드에는 **해당 TC 가 어느 입력 소스에서 나왔는지 기준으로** 아래 매핑 표의 화면 코드를 정확히 사용하세요:

| 입력 소스 파일 | 화면 코드 |
|---|---|
{scr_table}

## 🚨 입력 소스 범위 엄격 준수 (v0.9.26~ 절대 규칙)

**이 작업의 입력 화면 코드 = {allowed_scrs_str} — 이 외에는 절대 다루지 마세요.**

⚠️ 다음과 같은 상황에 주의하세요:

- 입력 파일 본문에 다른 SCR 코드(예: SCR-403, SCR-221, SCR-410)가 표/참고/링크로 언급될 수 있습니다
- 본문 끝의 부록 표("**에러 케이스 (프로필/알림/PnL)**" 같은 형식) 에 다른 화면들의 정보가 있을 수 있습니다
- 인터랙션 설명에서 navigateTo('scr-XXX') 같은 다른 화면 참조가 있을 수 있습니다

**위 모든 경우에 다른 화면들의 분류/TC 는 만들지 마세요.**

✅ **올바른 행동**:
- 위 매핑 표의 SCR 코드만 분류표/TC ID 에 사용
- 다른 SCR 이 본문에 등장해도 무시
- "Notifications", "PnL", "Profile" 등 무관한 키워드는 명시적으로 입력 파일에 없으면 분류 금지

❌ **금지 행동**:
- 본문 부록에 SCR-221 (알림) 정보가 있다고 "Notifications" 중분류 추가 금지
- navigateTo('scr-403') 참조 봤다고 "Profile" 분류 추가 금지
- 매핑 표에 없는 SCR 코드를 임의로 만들기 금지

규칙:
1. 각 TC 메타 테이블에 `| 연관 화면 | SCR-NNN |` 형식 정확히 사용 (예: `| 연관 화면 | {primary_example} |`)
2. 화면명 없이 코드만: "SCR-001" ✅ / "Splash (SCR-001)" ❌
3. 한 TC 가 여러 화면에 걸치면 쉼표 구분: `SCR-001, SCR-003` (단, 둘 다 위 매핑 표에 있어야 함)
4. **임의 코드 생성 금지**: 위 매핑 표에 없는 화면 코드(SCR-999, LGI, ABC, 또는 입력 외 다른 SCR)는 절대 만들지 마세요
5. 출처 입력 소스에 매핑이 없으면 `| 연관 화면 |  |` 빈 칸으로 두세요
"""
        elif detected:
            # source_scr_map 은 비어있지만 features_text 에서 SCR 패턴 발견 (예: 본문에 SCR-NNN 언급)
            codes_str = ", ".join(detected[:5])
            screen_code_hint = f"""
## 📱 연관 화면 코드 (입력 본문에서 탐지)

이 중분류 "{focus_middle}" 와 관련해 입력 본문에서 다음 화면 코드를 발견했습니다: **{codes_str}**

⚠️ **규칙**:
1. 각 TC 메타 테이블에 `| 연관 화면 | {detected[0]} |` 형식 사용
2. 위에 나열된 코드만 사용 — **임의 코드(LGI, ABC, SCR-999 등) 생성 금지**
3. 본문에 SCR 코드가 명시되지 않은 TC 는 `| 연관 화면 |  |` 필드를 비워두세요
"""
        else:
            # 입력 소스에 화면 식별자가 전혀 없음 — 빈 칸 명시
            screen_code_hint = f"""
## 📱 연관 화면 (입력 소스에 화면 식별자 없음)

⚠️ 이 입력 소스에서 화면 코드(SCR-NNN 형식)가 발견되지 않았습니다.

**규칙**: 각 TC 메타 테이블의 `| 연관 화면 |` 필드를 **반드시 빈 칸**으로 두세요:
```
| 연관 화면 |  |
```
- 임의 코드(SCR-001, LGI 등) 생성 금지
- 중분류 이름을 화면 코드 자리에 넣지 마세요
- 빈 칸이 정상입니다. 입력 소스에 식별자가 추가되면 다음 실행에서 자동 채워집니다.
"""

    # 분류표 우선 원칙 (Gate 검토 후 사용자 수정사항이 본문/features 보다 우선)
    classification_priority_hint = """
## 🎯 분류표 우선 원칙 (절대 규칙 — 반드시 준수)

⚠️ **사용자가 검토·승인한 분류표가 최종 진실 소스입니다.**

분류표는 단순 목차가 아닙니다. 사용자가 Gate 검토 단계에서 다음과 같은 수정을 했을 수 있습니다:
- 불필요한 기능 (예: 체크박스, 광고 영역 등) 제거
- 중분류/소분류 통합 또는 분리
- 시나리오 우선순위 조정
- 범위 외 항목 제외

**그러므로**:

1. **분류표에 있는 중분류/소분류만 TC 로 작성하세요.**
2. **본문(features_text, 정책)에 추가 기능이 보여도, 분류표에 없으면 TC 만들지 마세요.**
3. **분류표 ⊃ 본문이 아닙니다.** 본문이 더 자세할 수 있지만 분류표가 우선입니다.
4. 본문은 TC **상세 시나리오 작성을 위한 참고**일 뿐 (입력값/조건/결과 등). **항목 자체의 포함 여부 결정에는 사용 금지.**
5. 만약 본문에는 있는데 분류표에는 없는 기능이 있다면: **사용자가 의도적으로 제외한 것** — TC 만들지 마세요.

예시:
- 분류표에 "이메일 입력" 만 있고 본문에 "체크박스 동의" 가 있을 때
  → 체크박스 동의 TC 만들지 않음 (사용자가 의도적으로 제거한 것)
- 분류표에 "로그인" 이 있을 때
  → 본문의 로그인 관련 상세 시나리오를 참고하여 TC 작성 (정상)
"""

    # 그룹 단위 에러 패턴 통합 안내 (tc-rules.md 원칙 G 보강)
    dedup_hint = """
## 🔁 에러/예외 패턴 통합 규칙 (tc-rules.md 원칙 G — 반드시 준수)

⚠️ **같은 그룹/대분류의 여러 화면에 동일 패턴 비기능 TC 를 반복 작성하지 마세요.**

### 보존 (스펙 명시)
- 기획서의 "에러 케이스" 표에 **명시된** 에러 → 해당 화면 TC 로 보존
  (예: SCR-013 의 "권한 거부 Modal", "토큰 수신 실패 Modal")

### 통합 (AI 추가)
다음 패턴은 **그룹당 1개 대표 화면에만** 작성:
- 네트워크 끊김 / 연결 실패
- 타임아웃 처리
- 3G/저사양 환경 로딩 시간
- 백그라운드 → 포그라운드 복귀
- 화면 회전 / 메모리 부족

### 대표 화면 선택
1. entry 성격 화면 우선 (그룹의 진입 지점)
2. entry 가 없으면 그룹의 첫 번째 화면
3. 사용자가 입력한 화면 중에서만 선택

### 통합 TC 형식
```
**비고**
- [통합] 그룹 단위 비기능 검증 — 같은 패턴을 다른 화면별로 반복 작성하지 않음 (원칙 G).
```

### ❌ 금지 예시
같은 그룹 SCR-010, 011, 012, 013, 014 모두에 "네트워크 끊김" TC 5개 작성 → 1개로 통합 필수
"""

    # 마침표 종결 강화 안내 (tc-rules.md 9-2 절 보강)
    period_hint = """
## ✍️ 문장 종결 규칙 (tc-rules.md 9-2 — 반드시 준수)

**테스트 단계** 와 **예상 결과** 의 **모든 항목은 마침표(`.`)로 끝**나야 합니다.

✅ 올바른 예:
```
**테스트 단계**
1. Continue 버튼을 탭한다.

**예상 결과**
- 인증 코드 입력 화면으로 이동한다.
- AppState 의 email 값이 갱신된다.
```

❌ 잘못된 예:
```
**예상 결과**
- 인증 코드 입력 화면으로 이동한다  ← 마침표 누락
- email 값 갱신                     ← 단어형 + 마침표 누락
```

사전 조건은 명사형 (`~인 상태`, `~된 상태`) 이므로 마침표 불필요.
"""

    return f"""프로젝트: {project_name}
대분류: {domain['name']} ({domain['code']})
{tc_id_instruction}
{middle_instruction}
{nfr_instruction}
{nav_instruction}
{screen_code_hint}
{classification_priority_hint}
{dedup_hint}
{period_hint}
## 이 대분류의 분류 구조 (사용자 승인 — 최종 진실 소스)
{domain_section}

## 전체 기능 목록 (참고용 — 분류표가 우선)
⚠️ 아래 정보는 **TC 상세 작성을 위한 참고**입니다. 항목 포함 여부는 위 분류표 기준으로 결정하세요.
{features_text[:15000]}

## 관련 정책 (참고용 — 분류표가 우선)
⚠️ 아래 정책은 **TC 의 사전조건/예상결과 작성에 참고**합니다. 분류표에 없는 기능은 정책이 있어도 TC 만들지 마세요.
{policy_text[:15000]}

위 대분류({domain['name']}){' 중 "' + focus_middle + '" 중분류' if focus_middle else ''}에 속하는 TC를 아래 4가지 카테고리 순서로 상세하게 작성해주세요.
해당 카테고리에 만들 TC가 없으면 skip합니다.

1. UI/UX 체크: 화면 표시, 초기 상태, 레이아웃 (Positive, Medium~High) — 약 20%
2. 주요 기능: 핵심 정상 흐름 (Positive, High) — bold 처리 — 약 35%
3. 예외 기능: 잘못된 입력, 권한 오류, 잔고 부족, 중복 요청 등 (Negative, High~Medium) — High는 bold — 약 25%
4. 에러 처리 및 비기능: 네트워크 오류, 타임아웃, 빈 응답, 성능 (Edge, Medium~Low) — 약 20%

⚠️ 카테고리 3(예외)과 4(에러)를 반드시 포함하세요. Positive만으로 구성하지 마세요.
⚠️ 이미 다른 TC에서 검증되는 내용은 중복 작성하지 마세요.
⚠️ 중분류당 TC는 5~15개가 적정합니다. 유의미한 TC만 작성하고 양을 채우기 위한 TC는 만들지 마세요.

⚠️ **소분류 이름 유일성** (테스터 가독성 핵심):
- 같은 중분류 안에서 **여러 TC의 소분류 이름이 동일하면 안 됩니다**.
- 테스터는 TC ID보다 소분류 이름으로 케이스를 구분하므로, 소분류는 **그 자체로 무엇을 검증하는지 명확히** 표현해야 합니다.
- 같은 화면의 다른 시나리오라면 소분류에 **차별화 키워드**를 포함하세요.
  예시 ❌: "Splash 화면 진입" × 4개 (UI 표시/버튼 탭/뒤로가기/로딩)
  예시 ✅: "Splash 화면 UI 표시", "Splash Get Started 버튼 탭", "Splash 뒤로가기 차단", "Splash 로딩 시간"
- 소분류 길이는 30자 이내로 짧고 구체적으로.
- 사전 조건은 반드시 번호 개조식으로 작성
- **각 TC의 메타 테이블에 `| 연관 화면 |` 필드를 반드시 포함**하세요 (위 📱 섹션 참고)

⛔ **출력 형식 절대 규칙**:
- 모든 `### ...` 헤더는 반드시 TC ID로 시작해야 합니다 (예: `### SC-XXX-001 — 제목`)
- **TC가 아닌 설명·분석·메모·원칙 적용 결과**를 `### 헤더`로 작성하지 마세요.
- 이 중분류가 원칙 C(deferred/archived) 등에 의해 **TC 생성 제외 대상**이면, 아무것도 작성하지 말고 **완전히 빈 응답**을 반환하세요. 제외 이유 설명도 작성 금지.
- 부가 설명이 꼭 필요하면 TC 블록 안의 `**비고**` 섹션 또는 `---` 구분선 앞의 본문에만 쓰세요. `### 헤더`로는 절대 금지.
"""


def _detect_screen_codes_for_middle(middle: str, text: str) -> list[str]:
    """중분류 이름이 언급된 부근에서 화면 코드(SCR-NNN / SCREEN-NNN / PAGE-NNN)를 추출.
    우선순위:
      1. `| SCR-xxx | {middle} | ...` 인벤토리 표 행 (정확 매칭)
      2. middle 이름 주변 ±300자에 등장하는 SCR/SCREEN/PAGE 코드
    반환: 등장 순서 · 중복 제거한 코드 리스트
    """
    if not middle or not text:
        return []
    codes = []
    seen = set()

    # 패턴 1: 인벤토리 표 행 — `| CODE | NAME | ...`
    row_pat = re.compile(r"\|\s*((?:SCR|SCREEN|PAGE)-[A-Z0-9]+)\s*\|\s*([^|]+?)\s*\|")
    for m in row_pat.finditer(text):
        code, name = m.group(1), m.group(2).strip()
        if middle.lower() in name.lower() or name.lower() in middle.lower():
            if code not in seen:
                codes.append(code)
                seen.add(code)

    if codes:
        return codes

    # 패턴 2: middle 이름 주변에 등장하는 코드 (±300자 윈도우)
    code_pat = re.compile(r"(?:SCR|SCREEN|PAGE)-[A-Z0-9]+")
    for m in re.finditer(re.escape(middle), text, re.IGNORECASE):
        start = max(0, m.start() - 300)
        end = min(len(text), m.end() + 300)
        window = text[start:end]
        for c in code_pat.findall(window):
            if c not in seen:
                codes.append(c)
                seen.add(c)
    return codes


def extract_domain_section(classification: str, domain_code: str) -> str:
    """분류표에서 특정 대분류 섹션 추출.
    괄호 코드(`## 대분류: 이름 (CODE)`) 형식과 코드 없는 형식(`## 대분류: 이름`) 모두 지원.
    domain_code는 extract_domains에서 자동 생성된 코드(이름의 영문자 대문자 약어)."""
    lines = classification.splitlines()
    result = []
    in_section = False
    for line in lines:
        # 새 섹션 시작 감지
        m = re.match(r"^##\s+(.+)", line)
        if m and not line.startswith("###"):
            text = m.group(1).strip()
            text = re.sub(r"^대분류[:\s]*", "", text).strip()
            # 괄호 코드가 있으면 그걸로 매칭
            cm = re.search(r"[\(\（]([A-Z]{2,8})[\)\）]", text)
            if cm:
                matched = (cm.group(1) == domain_code)
            else:
                # 괄호 없음 → 이름에서 코드 자동 생성하여 매칭
                name_only = re.sub(r"\s*[\(\（][^\)\）]*[\)\）]", "", text).strip()
                auto_code = re.sub(r"[^A-Za-z]", "", name_only).upper()[:6] or "FUNC"
                matched = (auto_code == domain_code)
            if matched:
                in_section = True
                result.append(line)
                continue
            elif in_section:
                break
        if in_section:
            result.append(line)
    return "\n".join(result) if result else classification[:1000]


# ── 7단계: TC 검토 ────────────────────────────────────────────────────────────
def _extract_covered_middles(tc_content: str) -> set:
    """TC 초안에서 실제로 다뤄진 (대분류, 중분류) 페어 추출.
    세 가지 패턴 지원:
      1. `**대분류**: X` / `**중분류**: Y` 라인 (bold 라인 스타일)
      2. `## 대분류 / ### 중분류` 섹션 헤더 스타일
      3. `| 대분류 | X |` / `| 중분류 | Y |` 마크다운 테이블 스타일 (현재 TC 형식)
    """
    covered = set()

    # 패턴 1: bold 라인 스타일
    major = None
    middle = None
    for line in tc_content.splitlines():
        m_major = re.search(r"\*\*대분류\*\*\s*[:：]\s*(.+)", line)
        m_middle = re.search(r"\*\*중분류\*\*\s*[:：]\s*(.+)", line)
        if m_major:
            major = m_major.group(1).strip()
        if m_middle:
            middle = m_middle.group(1).strip()
            if major and middle:
                covered.add((major, middle))

    # 패턴 2: 섹션 헤더 스타일
    cur_major = None
    for line in tc_content.splitlines():
        line_s = line.strip()
        if line_s.startswith("## ") and not line_s.startswith("### "):
            txt = re.sub(r"^##\s+", "", line_s).strip()
            txt = re.sub(r"^대분류[:\s]*", "", txt).strip()
            txt = re.sub(r"\s*[\(\（][A-Z]{2,8}[\)\）]", "", txt).strip()
            if txt and not txt.startswith("카테고리"):
                cur_major = txt
        elif line_s.startswith("### ") and cur_major:
            txt = re.sub(r"^###\s+", "", line_s).strip()
            txt = re.sub(r"^중분류[:\s]*", "", txt).strip()
            txt = re.sub(r"\s*[\(\（][A-Z]{2,8}[\)\）]", "", txt).strip()
            if txt and not txt.lower().startswith("tc") and not txt.startswith("카테고리"):
                covered.add((cur_major, txt))

    # 패턴 3: 마크다운 테이블 — TC 블록별로 대분류/중분류 짝맞춤
    # 각 `### TC-ID` 블록 안에서 `| 대분류 | X |`과 `| 중분류 | Y |`를 찾는다
    blocks = re.split(r"\n(?=###\s)", tc_content)
    for block in blocks:
        if not block.strip().startswith("###"):
            continue
        major_match = re.search(r"\|\s*대분류\s*\|\s*([^|]+?)\s*\|", block)
        middle_match = re.search(r"\|\s*중분류\s*\|\s*([^|]+?)\s*\|", block)
        if major_match and middle_match:
            maj = major_match.group(1).strip()
            mid = middle_match.group(1).strip()
            # 괄호 코드 제거
            maj = re.sub(r"\s*[\(\（][A-Z]{2,8}[\)\）]", "", maj).strip()
            mid = re.sub(r"\s*[\(\（][A-Z]{2,8}[\)\）]", "", mid).strip()
            if maj and mid:
                covered.add((maj, mid))

    return covered


def _extract_classification_middles(classification: str) -> list:
    """분류표에서 (대분류, 중분류) 순서 리스트 반환."""
    pairs = []
    cur_major = None
    for line in classification.splitlines():
        line_s = line.strip()
        if line_s.startswith("## ") and not line_s.startswith("### "):
            txt = re.sub(r"^##\s+", "", line_s).strip()
            txt = re.sub(r"^대분류[:\s]*", "", txt).strip()
            txt = re.sub(r"\s*[\(\（][A-Z]{2,8}[\)\）]", "", txt).strip()
            if txt:
                cur_major = txt
        elif line_s.startswith("### ") and cur_major:
            txt = re.sub(r"^###\s+", "", line_s).strip()
            txt = re.sub(r"^중분류[:\s]*", "", txt).strip()
            txt = re.sub(r"\s*[\(\（][A-Z]{2,8}[\)\）]", "", txt).strip()
            if txt:
                pairs.append((cur_major, txt))
    return pairs


def _generate_missing_tc_for_middle(sess: dict, major: str, middle: str,
                                    classification: str, features_text: str,
                                    policy_text: str, project_name: str,
                                    tc_rules: str, fewshot: str,
                                    project_policies: str,
                                    screen_based: bool, screen_map: dict,
                                    project_code: str) -> str:
    """누락된 (대분류, 중분류) 하나에 대해 TC를 생성해 돌려준다."""
    # 대분류 코드 복원 (extract_domains 규칙과 동일)
    cm = re.search(r"[\(\（]([A-Z]{2,8})[\)\）]", major)
    if cm:
        domain_code = cm.group(1)
        domain_name = re.sub(r"\s*[\(\（][A-Z]{2,8}[\)\）]", "", major).strip()
    else:
        domain_name = major
        domain_code = re.sub(r"[^A-Za-z]", "", domain_name).upper()[:6] or "FUNC"

    # Screen-based면 screen code 매핑
    if screen_based:
        effective_code = resolve_screen_code(middle, screen_map)
        screen_character = resolve_screen_character(middle, screen_map)
        screen_navigation = resolve_screen_navigation(middle, screen_map)
        starting_seq = 1
    else:
        effective_code = domain_code
        screen_character = ""
        screen_navigation = ""
        starting_seq = 1

    domain_with_middle = {
        "name": domain_name,
        "code": domain_code,
        "suite_code": effective_code,
        "_focus_middle": middle,
    }
    # 섹션 발췌 (Quick / 정책 반영 최적화 공통)
    effective_features = features_text
    effective_policy = policy_text
    if sess.get("_quick_mode") or sess.get("_section_extract"):
        raw_full = sess.get("_raw_text", "")
        section = extract_section_from_raw(raw_full, middle, major_name=domain_name)
        if section:
            effective_features = section
            if sess.get("_quick_mode"):
                effective_policy = section
            else:
                effective_policy = (policy_text[:4000] + "\n\n---\n\n원문 섹션:\n" + section) if policy_text else section
    system = build_tc_system_prompt(tc_rules, classification, project_policies, fewshot)
    _scr_map = sess.get("_source_scr_map") or {}
    user = build_tc_user_prompt(domain_with_middle, effective_features, effective_policy,
                                project_name, classification,
                                starting_seq=starting_seq,
                                screen_character=screen_character,
                                screen_navigation=screen_navigation,
                                source_scr_map=_scr_map)
    try:
        tc_draft = call_claude(system, user, max_tokens=16000)
    except Exception as e:
        push_log(sess, f"[검토-보강] {domain_code}/{middle} 생성 실패: {e}")
        return ""

    # TC ID 재번호링
    if effective_code:
        tc_draft, _ = renumber_tc_ids(tc_draft, project_code, effective_code, starting_seq)
    return tc_draft


def step_review(sess: dict, tc_content: str, project_name: str,
                approved_classification: str = "",
                features_text: str = "", policy_text: str = "") -> str:
    """TC 품질 검토 + 누락 중분류 자동 보강.
    approved_classification이 주어지면 분류표 vs TC 초안 비교하여 누락 중분류의 TC를 자동 생성하고 tc_content에 추가한다.
    sess["_augmented_tc"]에 보강된 tc_content를 저장한다."""
    push_log(sess, "[검토] TC 품질 검토 중...")

    # ── 1) 누락 탐지 ─────────────────────────────────────────────
    augmented = tc_content
    missing_pairs = []
    if approved_classification:
        expected = _extract_classification_middles(approved_classification)
        covered = _extract_covered_middles(tc_content)
        # 대소문자·공백 관용 매칭
        def norm(s): return re.sub(r"\s+", "", s).lower()
        covered_norm = {(norm(a), norm(b)) for a, b in covered}
        for (maj, mid) in expected:
            if (norm(maj), norm(mid)) not in covered_norm:
                missing_pairs.append((maj, mid))
        if missing_pairs:
            push_log(sess, f"[검토] 누락된 중분류 {len(missing_pairs)}개 탐지: "
                             + ", ".join(f"{m}/{n}" for m, n in missing_pairs[:5])
                             + (" ..." if len(missing_pairs) > 5 else ""))
        else:
            push_log(sess, "[검토] 누락된 중분류 없음 (분류표 전체 커버)")

    # ── 2) 누락 보강 ─────────────────────────────────────────────
    if missing_pairs and features_text and policy_text:
        tc_rules = load_tc_rules()
        fewshot = load_fewshot_examples()
        project_policies = load_project_policies(project_name)
        project_code = _detect_project_code(project_name)
        user_auto_flag = sess.get("auto_screen_code")
        if user_auto_flag is True:
            screen_based = True
        elif user_auto_flag is False:
            screen_based = False
        else:
            screen_based = _is_screen_based(project_code)
        screen_map = load_screen_code_map(project_name) if screen_based else {}

        added_parts = []
        total_missing = len(missing_pairs)
        # 보강 단계: 82 → 87 구간을 누락 개수로 분할 + ETA 동적 갱신
        for idx, (maj, mid) in enumerate(missing_pairs):
            push_log(sess, f"[검토-보강] [{idx+1}/{total_missing}] {maj}/{mid} TC 생성 중...")
            remaining = total_missing - idx
            pct = 82 + int(5 * (idx / max(total_missing, 1)))
            push_stage(sess, 4, f"TC 보강 {idx+1}/{total_missing} — {mid}", pct,
                       eta_sec=remaining * 30 + 10)
            part = _generate_missing_tc_for_middle(
                sess, maj, mid, approved_classification, features_text, policy_text,
                project_name, tc_rules, fewshot, project_policies,
                screen_based, screen_map, project_code
            )
            if part.strip():
                added_parts.append(part)
            check_stop(sess)
        if added_parts:
            augmented = tc_content + "\n\n---\n\n## 검토 단계 보강 TC\n\n" + "\n\n---\n\n".join(added_parts)
            push_log(sess, f"[검토-보강] 보강 완료 — {len(added_parts)}개 중분류 TC 추가")

    sess["_augmented_tc"] = augmented

    # ── 3) 리포트 작성 ──────────────────────────────────────────
    system = """당신은 시니어 QA 리뷰어입니다. TC 초안을 검토하고 개선 리포트를 작성합니다."""
    missing_section = ""
    if missing_pairs:
        missing_section = "\n누락 중분류 (자동 보강됨):\n" + "\n".join(f"- {m}/{n}" for m, n in missing_pairs[:30])
    user = f"""프로젝트: {project_name}

다음 TC 초안을 검토하고 review_report.md를 작성해주세요:

검토 항목:
1. TC ID 일관성 및 중복 여부
2. 사전 조건 작성 규칙 준수 여부
3. Positive/Negative/Edge 비율
4. 최소 TC 세트 선별 적절성
5. 예상 결과 측정 가능성
6. 누락된 케이스
{missing_section}

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
## 누락 중분류 보강 결과
"""
    try:
        result = call_claude(system, user, max_tokens=3000)
    except Exception as e:
        result = f"# TC 검토 보고서\n\n검토 실행 중 오류: {e}\n"
    review_path = sess["workspace"] / "07_review_report.md"
    review_path.write_text(result, encoding="utf-8")
    push_log(sess, "[검토] 검토 완료")
    return result


# ── 8단계: tc_final.md 생성 및 Excel 빌드 ─────────────────────────────────────
def step_build_excel(sess: dict, tc_content: str, project_name: str,
                     total_tc: int, min_tc: int) -> Path:
    # 후처리: 같은 (대,중,소) 그룹에 TC가 여러 개면 소분류에 차별화 키워드 자동 부여
    # MD ↔ Excel 일관성을 위해 tc_content 자체를 갱신 (이후 tc_files에도 변형 적용된 형태로 저장됨)
    sess.pop("_tc_content_disambiguated", None)  # 이전 호출 잔여 제거
    try:
        new_content = disambiguate_duplicate_minors(tc_content)
        if new_content != tc_content:
            tc_content = new_content
            # 세션에도 보관 — 호출부에서 tc_files에 저장 시 이 변형본 사용
            sess["_tc_content_disambiguated"] = tc_content
            push_log(sess, "[빌드] 소분류 중복 자동 구분 적용 — 같은 화면의 다른 시나리오에 차별화 키워드 부여")
    except Exception as e:
        push_log(sess, f"[빌드] 소분류 후처리 스킵: {e}")

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

    # ── 1순위: build_excel 모듈을 직접 import해서 run_build() 호출 ──
    # subprocess 우회 시 장점:
    #   - Windows cp949 인코딩 이슈 완전 제거 (stdout/stderr 디코드 경로 없음)
    #   - 가상환경 activation 의존성 없음 (Flask가 쓰는 같은 인터프리터)
    #   - 속도 ~1초 절감 (프로세스 생성/teardown 불필요)
    # 실패 시에만 subprocess → fallback 으로 강등
    if BUILD_EXCEL.exists():
        push_log(sess, f"[빌드] build_excel 모듈 호출 중... (대분류별 시트 생성 · 60초 내외)")
        try:
            build_excel_dir = str(BUILD_EXCEL.parent)
            if build_excel_dir not in sys.path:
                sys.path.insert(0, build_excel_dir)
            # 매 호출 시 fresh import (코드 수정 반영)
            import importlib
            import build_excel as _be
            importlib.reload(_be)
            # 상태/수정 사유 컬럼 + 🔄 변경 이력 시트는 「기존 TC 수정」 플로우(update-tc)에서만 포함.
            # 신규 TC 생성 시에는 깨끗한 Excel을 위해 생략.
            include_change = bool(sess.get("_include_change_columns"))
            # 사용자가 Human Gate에서 선택한 Excel 시트 옵션 (없으면 None=Full Set)
            excel_sheets = sess.get("_excel_sheets")
            result = _be.run_build("P_WebApp", str(tc_final_path), str(out_dir),
                                   verbose=False, include_change_columns=include_change,
                                   sheets=excel_sheets)
            if result and result.get("ok"):
                push_log(sess, f"[빌드] 모듈 호출 성공 — 총 {result['total_tc']} TC / Smoke {result['smoke_tc']} / 대분류 {result['major_count']}시트")
                sess["smoke_tc"] = result["smoke_tc"]
                out_path = result["out_path"]
                # v0.9.22: 통합 빌드인 경우 파일명에 _merged suffix 추가
                fname_suffix = sess.get("_excel_filename_suffix", "")
                if fname_suffix and out_path and out_path.exists():
                    new_name = out_path.stem + fname_suffix + out_path.suffix
                    new_path = out_path.parent / new_name
                    try:
                        out_path.rename(new_path)
                        out_path = new_path
                        push_log(sess, f"[빌드] 통합 결과 파일명 → {new_path.name}")
                    except Exception as _re:
                        push_log(sess, f"[빌드] 파일명 rename 실패 (원본 유지): {_re}")
                return out_path
        except Exception as e:
            push_log(sess, f"[빌드] 모듈 호출 실패 ({type(e).__name__}: {e}) — subprocess 폴백")

        # ── 2순위: subprocess (모듈 import 실패 시) ──
        try:
            child_env = os.environ.copy()
            child_env["PYTHONIOENCODING"] = "utf-8"
            child_env["PYTHONUTF8"] = "1"
            proc = subprocess.run(
                [sys.executable, str(BUILD_EXCEL),
                 "--phase", "P_WebApp",
                 "--tc",    str(tc_final_path),
                 "--output", str(out_dir)],
                capture_output=True, timeout=120, env=child_env,
            )
            stdout_str = (proc.stdout or b"").decode("utf-8", errors="replace")
            stderr_str = (proc.stderr or b"").decode("utf-8", errors="replace")
            if proc.returncode == 0:
                push_log(sess, "[빌드] subprocess 성공")
                m = re.search(r"Smoke Test\s*:\s*(\d+)개", stdout_str)
                if m:
                    sess["smoke_tc"] = int(m.group(1))
                excel_files = sorted(out_dir.glob("*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
                if excel_files:
                    return excel_files[0]
                push_log(sess, "[빌드] ⚠️ subprocess 성공했지만 xlsx 파일 없음 — fallback")
            else:
                err_msg = (stderr_str or stdout_str or "").strip()[:500]
                push_log(sess, f"[빌드] subprocess 오류 (returncode={proc.returncode}): {err_msg}")
        except subprocess.TimeoutExpired:
            push_log(sess, "[빌드] subprocess 타임아웃, fallback으로 직접 생성")
        except FileNotFoundError as e:
            push_log(sess, f"[빌드] ❌ Python 실행 파일 못 찾음: {e} — 가상환경(.venv) activation 확인 필요")
        except Exception as e:
            push_log(sess, f"[빌드] subprocess 예외 ({type(e).__name__}): {e}")

    # ── 3순위(최후): 내부 간이 빌더 (구형 포맷, 시트 분할 없음 — 아무것도 못 만드는 것보다 낫다) ──
    push_log(sess, "[빌드] ⚠️ 최후 fallback: 내부 간이 빌더 — 대분류별 시트 분할/Traceability 없음")
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

    # Smoke Test 시트 — Smoke 마킹된 TC만 모아 동일 구조로 렌더
    smoke_tcs = [t for t in tcs if t.get("_smoke")]
    ws_sm = wb.create_sheet("Smoke Test")
    ws_sm.freeze_panes = "A3"
    for ci, (h, w) in enumerate(zip(HEADERS, COL_W), 1):
        c = ws_sm.cell(1, ci, h)
        c.font = hfont(); c.fill = fill(NAVY); c.alignment = center(); c.border = bdr()
        ws_sm.column_dimensions[get_column_letter(ci)].width = w
    ws_sm.row_dimensions[1].height = 22
    for ri, tc in enumerate(smoke_tcs, 2):
        row_data = [
            "Y",
            tc.get("id", ""),
            _priority_kr(tc.get("priority", "")),
            "",
            tc.get("major", ""),
            tc.get("middle", ""),
            tc.get("minor", ""),
            tc.get("precondition", ""),
            tc.get("steps", ""),
            tc.get("expected", ""),
        ]
        for ci, val in enumerate(row_data, 1):
            c = ws_sm.cell(ri, ci, val)
            c.fill = PatternFill("solid", fgColor="E8F5E9")
            c.alignment = left_align() if ci >= 9 else center()
            c.border = bdr()
            c.font = Font(name="Calibri", size=9)
        ws_sm.row_dimensions[ri].height = max(30, min(120, len(str(row_data[8])) // 3 + 20))

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


def parse_tc_excel(path: Path) -> list[dict]:
    """우리가 생성한 Excel 포맷의 TC를 파싱하여 딕셔너리 리스트로 변환.
    대분류별 시트(📑 prefix)를 순회하며 TC ID가 있는 행을 수집.
    헤더 컬럼명으로 매핑 (컬럼 순서 변경에 강건).
    """
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise RuntimeError("openpyxl 패키지가 필요합니다")

    wb = load_workbook(path, data_only=True)
    tcs = []
    seen_ids = set()

    # 한글 → 내부 키 매핑 (구·신 컬럼명 모두 인식 — 하위 호환)
    KEY_MAP = {
        "TC ID": "id",
        "Smoke": "smoke",
        # 신규 컬럼명 (v0.9.7b)
        "중요도": "priority",
        "대상 거래소": "exchange",
        "사전조건": "precondition",
        "테스트 스텝": "steps",
        "기대결과": "expected",
        # 구 컬럼명 (하위 호환)
        "우선순위": "priority",
        "관련 거래소": "exchange",
        "거래소": "exchange",
        "사전 조건": "precondition",
        "스텝": "steps",
        "기대 결과": "expected",
        # 공통
        "대분류": "major",
        "중분류": "middle",
        "소분류": "minor",
        "화면 코드": "screen_code",
        "연관 화면": "screen",
        "상태": "status",
        "수정 사유": "change_reason",
    }

    for sheet_name in wb.sheetnames:
        # 공통 시트는 제외 (📑로 시작하는 대분류 시트만 순회)
        if not sheet_name.startswith("📑"):
            continue
        ws = wb[sheet_name]
        if ws.max_row < 2:
            continue
        # 헤더 읽기 (1행)
        header_row = [c.value for c in ws[1]]
        col_idx = {}
        for i, h in enumerate(header_row):
            if not h:
                continue
            h_str = str(h).strip()
            key = KEY_MAP.get(h_str)
            if key:
                col_idx[key] = i

        if "id" not in col_idx:
            continue

        for row in ws.iter_rows(min_row=2, values_only=True):
            raw_id = row[col_idx["id"]] if col_idx["id"] < len(row) else None
            if not raw_id or not re.match(r"^[A-Z]{2,}-[A-Z0-9]+-\d+", str(raw_id).strip()):
                continue
            tid = str(raw_id).strip()
            if tid in seen_ids:
                continue
            seen_ids.add(tid)

            tc = {"id": tid, "title": ""}
            for key, idx in col_idx.items():
                if idx < len(row) and row[idx] is not None:
                    tc[key] = str(row[idx]).strip()

            # smoke은 "Y" 여부를 bool로
            tc["is_min"] = (tc.get("smoke", "").upper() == "Y")
            # 우선순위 한글 → 영문 역변환 (Medium 기본)
            pri_map = {"높음": "High", "보통": "Medium", "낮음": "Low"}
            if tc.get("priority") in pri_map:
                tc["priority"] = pri_map[tc["priority"]]
            tc.setdefault("major", "")
            tc.setdefault("middle", "")
            tc.setdefault("minor", "")
            tc.setdefault("priority", "Medium")
            tc.setdefault("screen", tc.get("screen_code", ""))
            tcs.append(tc)
    return tcs


def _extract_spec_sections(md_text: str) -> dict[str, dict]:
    """기획서 MD를 화면(SCR/SCREEN/PAGE) 단위로 분할하여
    {code: {"name": ..., "body": ..., "raw_header": ...}} 딕셔너리 반환.

    매칭 패턴 (우선순위):
      1. `### SCR-001: Splash` (또는 `SCREEN-001`, `PAGE-001`)
      2. `### SCR-001` (이름 없음)
      3. 인벤토리 표 행 `| SCR-001 | Splash | 설명 |` — 이것은 헤더가 아니지만
         화면 코드가 없는 헤더 아래에서 소속 화면을 식별할 때 보조로 사용

    헤더가 없으면 빈 dict 반환 (상위 레벨에서 fallback 처리).
    """
    sections = {}
    if not md_text:
        return sections

    lines = md_text.splitlines()
    current_code = None
    current_name = ""
    current_header = ""
    buffer = []

    # `### CODE: Name` 또는 `### CODE` 형식
    header_pat = re.compile(
        r"^(#{2,4})\s+((?:SCR|SCREEN|PAGE)-[A-Z0-9]+[A-Z]?)\s*[:\-]?\s*(.*?)\s*$"
    )

    def flush():
        if current_code:
            sections[current_code] = {
                "name": current_name,
                "body": "\n".join(buffer).strip(),
                "raw_header": current_header,
            }

    for line in lines:
        m = header_pat.match(line)
        if m:
            flush()
            current_code = m.group(2).strip()
            current_name = m.group(3).strip() or ""
            current_header = line
            buffer = []
        elif current_code is not None:
            buffer.append(line)
    flush()
    return sections


def _normalize_body(body: str) -> str:
    """비교용 정규화 — 공백/빈 줄 정리, 가독성 변경(줄바꿈 등)에 둔감하게."""
    if not body:
        return ""
    # 연속 공백 하나로, 줄 끝 공백 제거, 빈 줄 제거
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in body.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def diff_specs(old_md: str, new_md: str) -> dict:
    """두 기획서 MD를 화면 코드 단위로 비교하여 변경사항 리포트 생성.

    반환 구조:
    {
        "added":   [{"code": "SCR-020", "name": "...", "body": "..."}],
        "removed": [{"code": "SCR-008", "name": "...", "body": "..."}],
        "modified":[{"code": "SCR-001", "name": "...",
                     "old_body": "...", "new_body": "...",
                     "diff_summary": "(옵션)"}],
        "unchanged_codes": ["SCR-002", ...],
        "has_spec_codes": True/False,  # 화면 코드 체계 사용 여부
    }
    """
    old_sections = _extract_spec_sections(old_md)
    new_sections = _extract_spec_sections(new_md)
    has_codes = bool(old_sections or new_sections)

    result = {
        "added": [],
        "removed": [],
        "modified": [],
        "unchanged_codes": [],
        "has_spec_codes": has_codes,
    }

    if not has_codes:
        # 화면 코드 체계 없음 — fallback은 상위에서 처리 (예: 전체 raw diff)
        return result

    old_codes = set(old_sections.keys())
    new_codes = set(new_sections.keys())

    for code in sorted(new_codes - old_codes):
        s = new_sections[code]
        result["added"].append({
            "code": code, "name": s["name"], "body": s["body"][:2000]
        })

    for code in sorted(old_codes - new_codes):
        s = old_sections[code]
        result["removed"].append({
            "code": code, "name": s["name"], "body": s["body"][:2000]
        })

    for code in sorted(old_codes & new_codes):
        old_raw = old_sections[code]["body"]
        new_raw = new_sections[code]["body"]
        old_body = _normalize_body(old_raw)
        new_body = _normalize_body(new_raw)
        if old_body != new_body:
            # 라인 단위 diff — 변경된 라인만 시각적으로 표시 가능하게 함
            line_diff = _compute_line_diff(old_raw, new_raw)
            result["modified"].append({
                "code": code,
                "name": new_sections[code]["name"] or old_sections[code]["name"],
                "old_body": old_raw[:4000],
                "new_body": new_raw[:4000],
                "line_diff": line_diff,
            })
        else:
            result["unchanged_codes"].append(code)

    return result


def _compute_line_diff(old_text: str, new_text: str,
                       max_lines: int = 400) -> list[dict]:
    """difflib 기반 라인 단위 diff 계산.
    반환: [{"tag": "equal"|"insert"|"delete"|"replace",
            "old_lines": [...], "new_lines": [...]}] 형태의 블록 리스트.
    너무 크면 max_lines에서 잘라낸다.
    """
    import difflib
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    # 공백만 다른 경우 노이즈 줄이기 — 동일하게 취급할지 여부는 difflib에 맡김
    matcher = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    blocks = []
    total_lines = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        olines = old_lines[i1:i2]
        nlines = new_lines[j1:j2]
        # equal 블록이 너무 길면 앞뒤 2줄만 남겨 컨텍스트 제공
        if tag == "equal" and (i2 - i1) > 4:
            olines = old_lines[i1:i1+2] + ["... (중략)"] + old_lines[i2-2:i2]
            nlines = new_lines[j1:j1+2] + ["... (중략)"] + new_lines[j2-2:j2]
        blocks.append({"tag": tag, "old_lines": olines, "new_lines": nlines})
        total_lines += max(len(olines), len(nlines))
        if total_lines >= max_lines:
            blocks.append({"tag": "truncated", "old_lines": [], "new_lines": []})
            break
    return blocks


def group_tcs_by_scr(tcs: list[dict]) -> dict[str, list[dict]]:
    """TC 리스트를 화면 코드(SCR-xxx) 기준으로 그룹핑.
    화면 코드가 없거나 여러 개인 경우:
      - 여러 개면 각 코드에 중복 등록
      - 없으면 "(화면 코드 없음)" 그룹으로
    """
    groups = defaultdict(list) if False else {}  # noqa
    from collections import defaultdict as _dd
    groups = _dd(list)
    for tc in tcs:
        screen_field = tc.get("screen_code") or tc.get("screen") or ""
        codes = re.findall(r"(?:SCR|SCREEN|PAGE)-[A-Za-z0-9]+", screen_field)
        if not codes:
            groups["(화면 코드 없음)"].append(tc)
            continue
        for c in dict.fromkeys(codes):  # 중복 제거 · 순서 유지
            groups[c].append(tc)
    return dict(groups)


def next_tc_id(existing_tcs: list[dict], project_code: str, suite_code: str) -> int:
    """주어진 프로젝트/스위트 코드의 기존 TC 번호 중 최대값 + 1 반환."""
    max_seq = 0
    pat = re.compile(rf"^{re.escape(project_code)}-{re.escape(suite_code)}-(\d+)$")
    for tc in existing_tcs:
        m = pat.match(tc.get("id", ""))
        if m:
            seq = int(m.group(1))
            if seq > max_seq:
                max_seq = seq
    return max_seq + 1


def build_diff_report(old_md: str, new_md: str,
                       existing_tcs: list[dict]) -> dict:
    """기획서 diff + 기존 TC 매핑을 결합한 리포트 생성.

    반환 구조 (프론트엔드에 바로 사용 가능):
    {
      "has_spec_codes": bool,
      "added":   [{"code", "name", "body", "estimated_tc_count"}],
      "modified":[{"code", "name", "old_body", "new_body",
                   "affected_tc_ids": [...], "affected_count"}],
      "removed": [{"code", "name", "affected_tc_ids": [...]}],
      "summary": {"added_n", "modified_n", "removed_n", "unchanged_n"}
    }
    """
    base = diff_specs(old_md, new_md)
    tc_groups = group_tcs_by_scr(existing_tcs)

    report = {
        "has_spec_codes": base["has_spec_codes"],
        "added": [],
        "modified": [],
        "removed": [],
        "summary": {},
    }

    for a in base["added"]:
        report["added"].append({
            "code": a["code"],
            "name": a["name"],
            "body": a["body"],
            "estimated_tc_count": 8,  # 경험적 기본값 (5~15 중 중앙)
        })

    for m in base["modified"]:
        affected = tc_groups.get(m["code"], [])
        report["modified"].append({
            "code": m["code"],
            "name": m["name"],
            "old_body": m["old_body"],
            "new_body": m["new_body"],
            "line_diff": m.get("line_diff", []),
            "affected_tc_ids": [t.get("id", "") for t in affected if t.get("id")],
            "affected_count": len(affected),
        })

    for r in base["removed"]:
        affected = tc_groups.get(r["code"], [])
        report["removed"].append({
            "code": r["code"],
            "name": r["name"],
            "affected_tc_ids": [t.get("id", "") for t in affected if t.get("id")],
            "affected_count": len(affected),
        })

    report["summary"] = {
        "added_n":     len(report["added"]),
        "modified_n":  len(report["modified"]),
        "removed_n":   len(report["removed"]),
        "unchanged_n": len(base["unchanged_codes"]),
    }
    return report


def load_existing_tcs(file_path: str | Path) -> list[dict]:
    """기존 TC 파일(MD 또는 Excel)을 자동 판별하여 파싱."""
    p = Path(file_path)
    if not p.exists():
        raise RuntimeError(f"파일 없음: {file_path}")
    suf = p.suffix.lower()
    if suf in (".md", ".markdown", ".txt"):
        content = p.read_text(encoding="utf-8")
        return parse_tc_markdown(content)
    if suf in (".xlsx", ".xls"):
        return parse_tc_excel(p)
    raise RuntimeError(f"지원하지 않는 파일 형식: {suf} (.md, .xlsx만 지원)")


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
            # v0.9.19: 입력 소스 SCR 매핑 복원 (체크포인트에 있으면 그것을, 없으면 raw_text 에서 자동 재추출)
            saved_scr_map = resumed["data"].get("source_scr_map") or {}
            if saved_scr_map:
                sess["_source_scr_map"] = dict(saved_scr_map)
                push_log(sess, f"[이어서] 화면 식별자 매핑 복원됨 ({len(saved_scr_map)}개)")
            else:
                # 폴백 — raw_text 에서 자동 재추출 (체크포인트가 v0.9.18 이하 버전이면 매핑 없음)
                fallback_map = {}
                # 입력 소스 정보가 있으면 파일별로 SCR 추출
                for src_info in (_sources_info or []):
                    if src_info.get("type") == "md":
                        fname = src_info.get("content", "")
                        if fname and raw_text:
                            # raw_text 안에서 해당 파일 섹션 찾기 — 헤더 패턴 사용
                            scr_id = extract_scr_from_source(fname, raw_text)
                            if scr_id:
                                fallback_map[fname] = scr_id
                # raw_text 전체에서 SCR 패턴 모두 수집 (파일 매핑 안 되도 표시)
                if not fallback_map and raw_text:
                    found = re.findall(r'SCR-\d+[A-Z]?', raw_text)
                    if found:
                        # unique 보존, 순서 유지
                        unique_scrs = list(dict.fromkeys(found))
                        # 가상 키로 보관 — UI 안내용
                        fallback_map = {f"(소스 #{i+1})": scr for i, scr in enumerate(unique_scrs[:10])}
                if fallback_map:
                    sess["_source_scr_map"] = fallback_map
                    push_log(sess, f"[이어서] 화면 식별자 자동 재추출 ({len(fallback_map)}개) — 옛 체크포인트 보강")
                else:
                    sess["_source_scr_map"] = {}
                    push_log(sess, "[이어서] 화면 식별자 매핑 없음 — Excel 화면 코드 컬럼 빈 칸 출력 (정상)")
        else:
            sess["status"] = "parsing"
            push_stage(sess, 1, "문서 파싱", 5)
            raw_text = step_parse_sources(sess, sources)
            check_stop(sess)
            sources_info = [{"type": s.get("type",""), "content": s.get("content",""), "selected_files": s.get("selected_files")} for s in sources]
            save_pipeline_state(project_name, "parsed", {"raw_text": raw_text[:20000], "focus_area": focus_area, "sources_info": sources_info, "source_scr_map": sess.get("_source_scr_map") or {}})
            save_project(project_name, last_sources=sources_info, last_focus_area=focus_area)

        if focus_area:
            push_log(sess, f"[포커스] TC 생성 범위: {focus_area}")

        # 생성 모드 결정 (resume 시에도 동일 로직 사용)
        gen_mode = sess.get("generation_mode", "summary")
        if gen_mode == "direct":
            push_log(sess, f"[모드] Quick 모드 — 3단계 (인벤토리 → 분류 → 섹션 발췌 TC)")
        else:
            push_log(sess, f"[모드] 정책 반영 모드 — 3단계 (통합 추출 → 분류 → 섹션 발췌 TC)")

        if gen_mode == "direct":
            # ── Quick 모드 3단계: 인벤토리 → 분류표 → 섹션발췌(TC 작성 시) ──
            # policy_text는 원문 전체 유지 (TC 작성 시 일반 정책 참조용으로도 사용됨)
            policy_text = raw_text
            if resumed and resumed.get("stage") in ("gate_waiting", "tc_writing"):
                # 복원 시 inventory도 복원 (있으면)
                inventory_text = resumed["data"].get("inventory_text", "") or resumed["data"].get("features_text", "")
                features_text = inventory_text or raw_text
                classification = resumed["data"].get("classification", "")
                push_log(sess, f"[이어서] 분류표 복원됨 ({len(classification):,}자)")
            else:
                # 1단계: 인벤토리 추출
                sess["status"] = "inventory"
                push_stage(sess, 2, "인벤토리 추출 (Quick 1/3)", 18)
                inventory_text = step_quick_inventory(sess, raw_text, project_name, focus_area)
                check_stop(sess)
                save_pipeline_state(project_name, "features", {"raw_text": raw_text[:20000], "policy_text": raw_text[:20000], "features_text": inventory_text, "inventory_text": inventory_text, "focus_area": focus_area, "sources_info": _sources_info, "source_scr_map": sess.get("_source_scr_map") or {}})

                # 2단계: 인벤토리 → 분류표
                sess["status"] = "classifying"
                push_stage(sess, 2, "분류표 생성 (Quick 2/3)", 35)
                classification = step_classify_from_inventory(sess, inventory_text, project_name, focus_area)
                check_stop(sess)
                # features_text 자리에 inventory_text를 세팅 — TC 작성 시 참고 목록으로 사용
                features_text = inventory_text
                save_pipeline_state(project_name, "gate_waiting", {"raw_text": raw_text[:20000], "policy_text": raw_text[:20000], "features_text": inventory_text, "inventory_text": inventory_text, "classification": classification, "focus_area": focus_area, "sources_info": _sources_info, "source_scr_map": sess.get("_source_scr_map") or {}})
            # sess에 flag 저장 — step_write_tc가 섹션 발췌 모드로 동작하도록
            sess["_quick_mode"] = True
            sess["_raw_text"] = raw_text
        else:
            # ── 정책 반영 모드 (최적화: 정책+기능 통합 1회 호출 + TC 작성 섹션 발췌) ──
            # 정책+기능 통합 추출 (기존 policy→features 2회 호출을 1회로)
            if resumed and resumed.get("stage") in ("classifying", "gate_waiting", "tc_writing"):
                policy_text = resumed["data"].get("policy_text", "")
                features_text = resumed["data"].get("features_text", "")
                push_log(sess, f"[이어서] 정책·기능 복원됨 (정책 {len(policy_text):,}자, 기능 {len(features_text):,}자)")
            else:
                sess["status"] = "policy_features"
                push_stage(sess, 2, "정책·기능 통합 추출", 22, eta_sec=90)
                policy_text, features_text = step_policy_features_combined(sess, raw_text, project_name, focus_area)
                check_stop(sess)
                save_pipeline_state(project_name, "features", {"raw_text": raw_text[:20000], "policy_text": policy_text, "features_text": features_text, "focus_area": focus_area, "sources_info": _sources_info, "source_scr_map": sess.get("_source_scr_map") or {}})

            # 분류표
            if resumed and resumed.get("stage") in ("gate_waiting", "tc_writing"):
                classification = resumed["data"].get("classification", "")
                push_log(sess, f"[이어서] 분류표 복원됨 ({len(classification):,}자)")
            else:
                sess["status"] = "classifying"
                push_stage(sess, 2, "분류표 생성", 38)
                classification = step_classify(sess, features_text, project_name, focus_area)
                check_stop(sess)
                save_pipeline_state(project_name, "gate_waiting", {"raw_text": raw_text[:20000], "policy_text": policy_text, "features_text": features_text, "classification": classification, "focus_area": focus_area, "sources_info": _sources_info, "source_scr_map": sess.get("_source_scr_map") or {}})

            # 정책 반영 모드도 TC 작성 시 원문 섹션 발췌 적용 (Quick 모드와 동일)
            sess["_raw_text"] = raw_text
            sess["_section_extract"] = True

        # Gate 단계에서 features/policy 도 sess 에 노출 — gate_chat 이 수정 시 함께 동기화하기 위함 (v0.9.15~)
        sess["_features_text"] = features_text
        sess["_policy_text"] = policy_text

        # Human Gate
        push_stage(sess, 3, "분류표 검토 대기", 45)
        approved = step_gate(sess, classification)
        check_stop(sess)

        # Gate 채팅에서 features/policy 도 수정됐을 수 있음 — 갱신본 사용 (v0.9.15~)
        synced_features = sess.get("_features_text", features_text)
        synced_policy = sess.get("_policy_text", policy_text)

        # TC 작성
        sess["status"] = "tc_writing"
        push_stage(sess, 4, "TC 작성 시작", 50)
        tc_content, total_tc, min_tc = step_write_tc(
            sess, approved, synced_features, synced_policy, project_name,
            selected_domain_codes=sess.get("selected_domains")
        )
        check_stop(sess)

        # TC 검토 (누락 중분류 자동 보강 포함)
        sess["status"] = "reviewing"
        # 검토 시작 — 누락 탐지 약 10초 + 보강(중분류당 ~30초) 가변
        push_stage(sess, 4, "TC 품질 검토 — 누락 탐지 중", 82, eta_sec=20)
        step_review(sess, tc_content, project_name,
                    approved_classification=approved,
                    features_text=synced_features,
                    policy_text=synced_policy)
        check_stop(sess)
        # 보강된 TC가 있으면 채택
        augmented_tc = sess.get("_augmented_tc")
        if augmented_tc and augmented_tc != tc_content:
            tc_content = augmented_tc
            # 보강된 TC의 개수 재계산
            new_tc_count = len(re.findall(r"^###\s+(?!카테고리)", tc_content, re.MULTILINE))
            if new_tc_count > total_tc:
                added = new_tc_count - total_tc
                push_log(sess, f"[검토-보강] TC 총 {new_tc_count}개 (원본 {total_tc} + 보강 {added})")
                total_tc = new_tc_count
                min_tc = max(1, round(total_tc * 0.35))

        push_stage(sess, 4, "TC 검토 완료 · Excel 준비", 88, eta_sec=10)

        # 원칙 G — 그룹 단위 에러 패턴 중복 탐지 (v0.9.17~)
        try:
            dup_report = detect_duplicate_error_tcs(tc_content)
            if dup_report["total_duplicates"] > 0:
                push_log(sess, f"[원칙 G] 중복 의심 패턴 {len(dup_report['patterns'])}개, 통합 시 약 {dup_report['total_duplicates']}개 TC 감소 예상")
                # SSE 로 프론트에 알림 — 사용자가 검토할 수 있게
                push(sess, "duplicate_warning", dup_report)
        except Exception as _e:
            push_log(sess, f"[원칙 G] 중복 탐지 스킵: {_e}")

        # Excel 빌드 — tc_final.md 생성(즉시) + build_excel.py 호출(60초 내외)
        sess["status"] = "building"
        push_stage(sess, 5, "Excel 빌드 — 시트 구성 중", 92, eta_sec=60)
        excel_path = step_build_excel(sess, tc_content, project_name, total_tc, min_tc)
        push_stage(sess, 5, "Excel 빌드 완료 · 마무리 중", 98, eta_sec=3)

        # 후처리(소분류 중복 차별화)가 적용된 tc_content를 마스터로 채택 (MD ↔ Excel 일치)
        tc_content = sess.get("_tc_content_disambiguated", tc_content)

        # TC 마크다운을 tc_files/에 저장 (수정 모드에서 재사용)
        today = datetime.now().strftime("%Y%m%d")
        safe_name = re.sub(r"[^\w\-_]", "_", project_name)[:30]
        tc_md_path = TC_FILES_DIR / f"{safe_name}_{today}.md"
        tc_md_path.write_text(tc_content, encoding="utf-8")
        save_project(project_name, str(tc_md_path), str(excel_path))
        clear_pipeline_state(project_name)  # 완료 시 상태 파일 정리
        push_log(sess, f"[저장] TC 파일 저장: {tc_md_path.name}")

        # 유니크 TC ID 수 — Excel 빌드 후 dedup 결과와 일치하도록 재계산
        unique_tc = count_unique_tc_ids(tc_content)
        if unique_tc and unique_tc != total_tc:
            push_log(sess, f"[완료] TC ID 중복 제거 — {total_tc}개 헤더 중 유니크 {unique_tc}개")
            total_tc = unique_tc
            min_tc = max(1, round(total_tc * 0.35))

        sess["result"] = excel_path
        sess["status"] = "done"
        push_stage(sess, 5, "완료", 100)
        push(sess, "done", {
            "filename":  excel_path.name,
            "size":      excel_path.stat().st_size,
            "sid":       sess["id"],
            "total_tc":  total_tc,
            "min_tc":    min_tc,
            "smoke_tc":  sess.get("smoke_tc"),
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

{tc_rules if tc_rules else ""}"""

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

## 🎯 영향도 분석 우선 원칙 (절대 규칙 — 반드시 준수)

⚠️ **사용자가 검토·승인한 영향도 분석(approved_plan)이 최종 진실 소스입니다.**

영향도 분석은 단순 참고가 아닙니다. 사용자가 Gate 검토 단계에서 다음과 같은 수정을 했을 수 있습니다:
- 삭제 대상에서 일부 TC 제외 (보존)
- 수정 대상에 추가 TC 포함 또는 제외
- 신규 추가 항목 변경
- 변경 범위 조정

**그러므로**:

1. **approved_plan 에 명시된 변경(삭제/수정/추가)만 정확히 적용하세요.**
2. **approved_plan 에 없는 TC 는 변경하지 마세요** — 기존 TC 그대로 유지.
3. **기존 TC (existing_tc) 의 내용을 보고 영향이 있어 보여도, approved_plan 에 없으면 건드리지 마세요.**
4. **임의로 추가 TC 를 생성하지 마세요** — 영향도 분석의 "신규 추가" 항목만 추가.
5. 만약 approved_plan 의 지시가 모호하면 보수적으로 판단 (변경 최소화 우선).

예시:
- approved_plan: "SCR-003-001 삭제, SCR-005-002 수정 (Given 단계에 OTP 추가)"
- → 정확히 그 두 TC 만 변경, 나머지 모든 TC 는 그대로 유지
- 사용자가 "SCR-007-003 도 비슷해 보이니까 같이 수정" 식의 환상 금지

## TC 형식 규칙
- bold heading (### **SC-XXX-YYY-NNN**) = 최소 TC (smoke test 대상)
- plain heading (### SC-XXX-YYY-NNN) = 일반 TC
- Given(사전 조건)은 번호 매긴 목록
- 전체 TC의 약 35%가 최소 TC여야 함

{tc_rules if tc_rules else ""}"""

        user_modify = f"""## 수정 지시사항 (사용자 승인 — 최종 진실 소스)

{approved_plan}

## 변경 배경 (참고)

{change_desc}

## 기존 TC 전체 (참고용 — 승인된 수정 지시사항이 우선)

⚠️ 아래 기존 TC 들은 **참고용**입니다. 위 수정 지시사항에 명시된 변경만 적용하세요.
지시사항에 없는 TC 는 임의로 변경하지 마세요.

{existing_tc[:15000]}

---

위 수정 계획을 정확히 적용하여 **수정된 TC 전체**를 출력하세요.
- 삭제 대상 TC는 완전히 제거
- 수정 대상 TC는 내용 업데이트 (TC ID 유지)
- 신규 TC는 기존 ID 체계에 맞춰 추가 (마지막 번호 이어서)
- **수정 지시사항에 없는 TC는 그대로 유지** (임의 변경 금지)
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
        # 후처리 적용본 채택 (MD ↔ Excel 일치)
        modified_tc = sess.get("_tc_content_disambiguated", modified_tc)

        # TC 파일 저장 (수정본으로 덮어쓰기)
        today = datetime.now().strftime("%Y%m%d")
        safe_name = re.sub(r"[^\w\-_]", "_", project_name)[:30]
        tc_md_path = TC_FILES_DIR / f"{safe_name}_{today}.md"
        tc_md_path.write_text(modified_tc, encoding="utf-8")
        save_project(project_name, str(tc_md_path), str(excel_path))

        # 유니크 TC ID 수 — Excel dedup 결과와 일치하도록 재계산
        unique_tc = count_unique_tc_ids(modified_tc)
        if unique_tc and unique_tc != total_tc:
            push_log(sess, f"[완료] TC ID 중복 제거 — {total_tc}개 헤더 중 유니크 {unique_tc}개")
            total_tc = unique_tc
            min_tc = max(1, round(total_tc * 0.35))

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
            "smoke_tc":  sess.get("smoke_tc"),
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
    return render_template_string(
        HTML_TEMPLATE,
        api_warning=api_warning,
        app_version=APP_VERSION,
        app_version_date=APP_VERSION_DATE,
        app_version_tagline=APP_VERSION_TAGLINE,
        app_version_highlights=APP_VERSION_HIGHLIGHTS,
    )


# ── 관리자 엔드포인트 ─────────────────────────────────────────────────────────
# 활성 세션으로 간주되는 status (이 외에는 종료/대기 상태로 봄)
# v0.9.18: gate_waiting 도 활성 세션 — 사용자가 분류표 검토 중인데 재시작하면
#          승인 시점에 sid 가 사라져 "세션 없음" 404 발생함
_ACTIVE_STATUSES = {
    "parsing", "inventory", "classifying", "policy_features",
    "gate_waiting",  # ← v0.9.18 추가: 분류표 검토 대기 중인 사용자 보호
    "tc_writing", "reviewing", "building", "analyzing",
}

def _count_active_sessions() -> int:
    return sum(1 for s in SESSIONS.values() if s.get("status") in _ACTIVE_STATUSES)

def _is_localhost_request() -> bool:
    """요청이 로컬호스트(127.0.0.1 / ::1)에서 왔는지 검사."""
    addr = request.remote_addr or ""
    return addr in ("127.0.0.1", "::1", "localhost")


@app.route("/admin/status", methods=["GET"])
def admin_status():
    """서버 살아있음 + 버전 + 활성 세션 수 (재시작 폴링용)."""
    return jsonify({
        "ok": True,
        "version": APP_VERSION,
        "active_sessions": _count_active_sessions(),
        "localhost": _is_localhost_request(),
    })


@app.route("/admin/restart", methods=["POST"])
def admin_restart():
    """서버 자기 자신을 재시작 (os.execv).
    보안:
      - localhost 요청만 허용
      - 활성 세션 있으면 ?force=1 로 강제 가능
    """
    # 1) localhost 가드 (LAN 다른 PC 차단)
    if not _is_localhost_request():
        return jsonify({"ok": False, "error": "재시작은 로컬에서만 허용됩니다."}), 403

    # 2) 활성 세션 가드
    force = (request.args.get("force", "0") == "1") or \
            (request.get_json(silent=True) or {}).get("force") is True
    active = _count_active_sessions()
    if active > 0 and not force:
        return jsonify({
            "ok": False,
            "error": "active_sessions",
            "active_sessions": active,
            "message": f"진행 중인 세션이 {active}개 있습니다. 정말 재시작하려면 force=1 로 다시 요청하세요.",
        }), 409

    # 3) 응답을 먼저 보내고 백그라운드에서 실제 재시작 (1.5초 후 os.execv)
    def _do_restart():
        try:
            time.sleep(1.5)  # 응답 도달 시간 확보
        finally:
            # listen socket 명시적 close — 새 프로세스만 incoming connection 처리하도록
            try:
                sk = getattr(app, "_listen_sock", None)
                if sk is not None:
                    sk.close()
            except Exception:
                pass
            # 현재 인터프리터 + 동일 인자로 자기 자신 재실행
            # SO_REUSEADDR 가 활성화되어 있어 새 프로세스도 즉시 bind 가능
            os.execv(sys.executable, [sys.executable] + sys.argv)

    threading.Thread(target=_do_restart, daemon=True).start()
    return jsonify({
        "ok": True,
        "message": "서버 재시작 중... 약 3~5초 후 자동 재연결됩니다.",
        "delay_sec": 1.5,
    })


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
    """마크다운 파일 업로드. 같은 이름 파일이 이미 있으면 _1/_2... 접미사로 구분 보존."""
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "파일 없음"}), 400
    f = request.files["file"]
    raw_name = (f.filename or "").strip()
    if not raw_name:
        return jsonify({"ok": False, "error": "파일명 없음"}), 400
    # webkitdirectory로 업로드 시 webkitRelativePath로 들어오는 경로 분리자 제거
    raw_name = raw_name.replace("\\", "/").split("/")[-1]
    # 안전한 파일명 (경로 조작 방지)
    safe_name = re.sub(r'[<>:"/\\|?*]', "_", raw_name).strip(". ")
    if not safe_name:
        return jsonify({"ok": False, "error": "유효하지 않은 파일명"}), 400
    ext = safe_name.rsplit(".", 1)[-1].lower() if "." in safe_name else ""
    if ext not in ("md", "markdown", "txt"):
        return jsonify({"ok": False, "error": ".md / .markdown / .txt 파일만 허용"}), 400

    # 중복 처리: 기존 파일 있으면 _1, _2 ... 접미사 자동 부여
    stem, suffix = safe_name.rsplit(".", 1)
    final_name = safe_name
    counter = 1
    while (SPECS_DIR / final_name).exists():
        final_name = f"{stem}_{counter}.{suffix}"
        counter += 1
        if counter > 999:
            return jsonify({"ok": False, "error": "같은 이름의 파일이 너무 많습니다"}), 400

    save_path = SPECS_DIR / final_name
    f.save(str(save_path))
    return jsonify({
        "ok": True,
        "filename": final_name,
        "original_filename": raw_name,
        "renamed": final_name != safe_name,
    })


def run_pipeline_structured(sess: dict, folder_path: str, project_name: str,
                              prev_folder_path: str = "",
                              include_unchanged: bool = False):
    """구조화 spec 폴더 파이프라인 — LLM 분류 단계 스킵, 화면별 1:1 호출.

    Args:
        prev_folder_path: 비어있지 않으면 diff 모드 — 이전 폴더 대비 추가/수정 SCR 만 재생성.
        include_unchanged: True면 diff 가 있어도 모든 화면 처리 (분류표 일관성용).
    """
    focus_area = sess.get("focus_area", "")
    diff_mode = bool(prev_folder_path)
    try:
        # ── 1) 폴더 파싱 (LLM 호출 없음) ──
        sess["status"] = "parsing"
        if diff_mode:
            push_stage(sess, 1, "구조화 spec 폴더 + diff 비교", 8)
            spec_data = step_parse_structured_spec_with_diff(
                sess, folder_path, prev_folder_path, include_unchanged=include_unchanged
            )
        else:
            push_stage(sess, 1, "구조화 spec 폴더 파싱", 8)
            spec_data = step_parse_structured_spec(sess, folder_path)
        check_stop(sess)

        if not spec_data["screens"]:
            if diff_mode and not spec_data.get("_diff", {}).get("common_changed"):
                # diff 모드에서 변경된 화면이 0개면 정상 종료
                push_log(sess, "[diff] 변경된 화면이 없습니다. 재생성할 TC 없음 — 종료.")
                sess["status"] = "done"
                push_stage(sess, 7, "완료 (변경 없음)", 100)
                push(sess, "done", {"result": None, "tc_count": 0, "diff": spec_data.get("_diff")})
                clear_pipeline_state(project_name)
                return
            raise RuntimeError(f"화면 md 가 없습니다: {folder_path}/scr/")
        if not spec_data["screen_rows"]:
            push_log(sess, "[경고] overview 의 화면 목록 표를 찾지 못함 — 화면 파일명/H1만으로 분류표 생성")
            # screen_rows fallback
            for sc in spec_data["screens"]:
                spec_data["screen_rows"].append({
                    "id": sc["id"], "name": sc["title"], "major": "공통",
                    "middle": sc["title"], "status": "active",
                    "desc": sc["description"], "entry": "",
                })

        # ── focus_area 에서 SCR ID 필터 추출 → 화면 한정 처리 ──
        # available_scrs 를 함께 넘겨야 "SCR-102, 104, 106" 같은 일괄 표기,
        # "SCR-102~116" 같은 범위 표기를 정확히 인식할 수 있다.
        available_scrs = {sc["id"] for sc in spec_data["screens"]}
        scr_filter = parse_scr_filter_from_focus(focus_area, available_scrs=available_scrs)
        if scr_filter:
            before_screens = len(spec_data["screens"])
            before_rows = len(spec_data["screen_rows"])
            spec_data["screens"] = [sc for sc in spec_data["screens"] if sc["id"] in scr_filter]
            spec_data["screen_rows"] = [r for r in spec_data["screen_rows"] if r["id"] in scr_filter]
            if not spec_data["screens"]:
                raise RuntimeError(
                    f"focus_area 에서 추출한 SCR ID({sorted(scr_filter)}) 가 폴더에서 매칭되지 않습니다. "
                    f"폴더에 있는 화면 md를 확인하세요."
                )
            push_log(sess,
                f"[focus] SCR 필터 적용 — {sorted(scr_filter)} → "
                f"화면 {before_screens}→{len(spec_data['screens'])}개, 행 {before_rows}→{len(spec_data['screen_rows'])}개")

        # raw_text 호환용 (resume/체크포인트용 — 전체 텍스트)
        raw_text = "\n\n".join([
            spec_data["overview_text"],
            spec_data["policy_text"],
            spec_data["design_text"],
        ])
        # SCR 매핑 — 화면 파일에서 ID 그대로
        sess["_source_scr_map"] = {sc["id"]: sc["id"] for sc in spec_data["screens"]}

        # ── 2) 분류표 자동 생성 (LLM 호출 없음) ──
        sess["status"] = "classifying"
        push_stage(sess, 2, "분류표 자동 생성 (LLM 호출 없음)", 25)
        # 필터링된 화면 기준으로 분류표 생성 (focus_area 가 있으면 그 화면들만).
        # screens 메타까지 넘겨야 SCR md 본문에서 소분류(세부 시나리오)를 자동 추출 가능.
        all_rows = spec_data["screen_rows"]
        classification = build_classification_from_screen_list(
            all_rows, project_name, screens_meta=spec_data.get("screens"),
        )
        classify_path = sess["workspace"] / "04_classification_draft.md"
        classify_path.write_text(classification, encoding="utf-8")
        push_log(sess, f"[분류] 화면 목록 표에서 분류표 자동 생성 — {len(classification):,}자")

        # 체크포인트 저장
        sources_info = [{"type": "spec_folder", "content": folder_path}]
        if diff_mode:
            sources_info.append({"type": "spec_folder_prev", "content": prev_folder_path})
        save_pipeline_state(project_name, "gate_waiting", {
            "raw_text": raw_text[:20000],
            "classification": classification,
            "focus_area": focus_area,
            "sources_info": sources_info,
            "source_scr_map": sess["_source_scr_map"],
            "structured_spec_folder": folder_path,
            "prev_folder": prev_folder_path,
            "include_unchanged": include_unchanged,
            "workspace": str(sess["workspace"]),
        })
        save_project(project_name, last_sources=sources_info, last_focus_area=focus_area)

        # spec_data 보관 — Human Gate 통과 후 step_write_tc_per_screen 에서 사용
        sess["_structured_spec_data"] = spec_data

        # ── 3) Human Gate ──
        sess["status"] = "gate_waiting"
        push_stage(sess, 3, "분류표 검토 대기 (Human Gate)", 50)
        approved = step_gate(sess, classification)
        check_stop(sess)

        # ── 4) 화면별 1:1 TC 작성 ──
        sess["status"] = "tc_writing"
        push_stage(sess, 4, "화면별 TC 작성 (cache 활용)", 55)
        # tc_writing 단계 진입 전 체크포인트 갱신 — resume 시 여기로 복귀
        save_pipeline_state(project_name, "tc_writing", {
            "raw_text": raw_text[:20000],
            "classification": classification,
            "approved_classification": approved,
            "focus_area": focus_area,
            "sources_info": sources_info,
            "source_scr_map": sess["_source_scr_map"],
            "structured_spec_folder": folder_path,
            "prev_folder": prev_folder_path,
            "include_unchanged": include_unchanged,
            "workspace": str(sess["workspace"]),
            "selected_domains": sess.get("selected_domains"),
            "suite_codes": sess.get("suite_codes"),
        })
        selected = sess.get("selected_domains")
        merged_tc, total_tc = step_write_tc_per_screen(
            sess, approved, spec_data, project_name,
            selected_domain_codes=selected,
        )

        # ── 5) Review (선택) — step_review 는 검토 보고서를 별도 파일로 저장.
        #    반환값은 검토 보고서 텍스트이므로 TC 본문 자리에 쓰면 안 된다.
        sess["status"] = "reviewing"
        push_stage(sess, 5, "TC 검토 / 정리", 82)
        try:
            step_review(sess, merged_tc, project_name)
        except Exception as e:
            push_log(sess, f"[검토] 스킵 — {e}")

        # ── 6) Excel 빌드 — step_build_excel 이 내부에서 tc_final.md 도 직접 생성한다.
        sess["status"] = "building_excel"
        push_stage(sess, 6, "Excel 빌드", 92)
        # total_tc 는 step_write_tc_per_screen 에서 받은 값이 정확. min_tc 는 표준 35% 공식.
        min_tc = max(1, round(total_tc * 0.35))
        result_file = step_build_excel(sess, merged_tc, project_name, total_tc, min_tc)
        excel_path = Path(result_file)
        sess["result"] = str(excel_path)

        sess["status"] = "done"
        push_stage(sess, 7, "완료", 100)
        # 기존 파이프라인과 동일한 페이로드 — 프론트가 filename/size/total_tc/min_tc/smoke_tc 를 사용
        push(sess, "done", {
            "filename":  excel_path.name,
            "size":      excel_path.stat().st_size if excel_path.exists() else 0,
            "sid":       sess["id"],
            "total_tc":  total_tc,
            "min_tc":    min_tc,
            "smoke_tc":  sess.get("smoke_tc"),
        })
        push_log(sess, f"[완료] 화면 {len(spec_data['screens'])}개 → TC {total_tc}개 → {excel_path.name}")

        # 체크포인트 정리
        clear_pipeline_state(project_name)
    except Exception as e:
        sess["status"] = "error"
        push_error(sess, f"구조화 spec 파이프라인 오류: {e}")


@app.route("/start-spec-folder", methods=["POST"])
def start_spec_folder():
    """구조화 spec 폴더 1개를 받아 파이프라인 실행.
    POST body: {project_name, folder_path, focus_area?, prev_folder_path?, include_unchanged?, resume?}
    - prev_folder_path 가 있으면 diff 모드 (변경/추가 SCR 만 재생성)
    - resume=true 면 이전 체크포인트(workspace/per_screen/*.md)로부터 이어서 작업
    """
    data = request.get_json(force=True) or {}
    project_name = data.get("project_name", "프로젝트").strip() or "프로젝트"
    focus_area   = (data.get("focus_area") or "").strip()
    folder_path  = (data.get("folder_path") or "").strip()
    prev_folder  = (data.get("prev_folder_path") or "").strip()
    include_unchanged = bool(data.get("include_unchanged"))
    resume       = bool(data.get("resume"))

    # resume 모드 — 저장된 체크포인트 복원
    if resume:
        state = load_pipeline_state(project_name)
        if not state:
            return jsonify({"ok": False, "error": "저장된 체크포인트가 없습니다."}), 400
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY가 설정되지 않았습니다."}), 500
        ckpt = state["data"]
        ckpt_folder = ckpt.get("structured_spec_folder")
        if not ckpt_folder:
            return jsonify({"ok": False, "error": "체크포인트에 spec 폴더 정보가 없습니다 (구조화 spec 모드 체크포인트가 아님)."}), 400

        sess = new_session()
        sess["project_name"] = project_name
        sess["focus_area"] = ckpt.get("focus_area", "")
        sess["generation_mode"] = "structured_spec"
        # workspace 복원 — per_screen/*.md 가 여기 있어야 resume 효력
        prev_workspace = ckpt.get("workspace")
        if prev_workspace and Path(prev_workspace).exists():
            sess["workspace"] = Path(prev_workspace)
            push_log(sess, f"[resume] workspace 복원: {prev_workspace}")
        sess["selected_domains"] = ckpt.get("selected_domains")
        sess["suite_codes"]      = ckpt.get("suite_codes") or []
        sess["_resumed_state"]   = state

        t = threading.Thread(
            target=run_pipeline_structured,
            args=(sess, ckpt_folder, project_name,
                  ckpt.get("prev_folder", ""),
                  bool(ckpt.get("include_unchanged"))),
            daemon=True,
        )
        sess["thread"] = t
        t.start()
        return jsonify({"ok": True, "sid": sess["id"], "resumed_stage": state["stage"]})

    if not folder_path:
        return jsonify({"ok": False, "error": "folder_path 가 비어 있습니다."}), 400
    folder = Path(folder_path).expanduser()
    if not folder.exists() or not folder.is_dir():
        return jsonify({"ok": False, "error": f"폴더가 없거나 디렉토리가 아닙니다: {folder}"}), 400
    if prev_folder:
        prev_p = Path(prev_folder).expanduser()
        if not prev_p.exists() or not prev_p.is_dir():
            return jsonify({"ok": False, "error": f"이전 폴더가 없거나 디렉토리가 아닙니다: {prev_p}"}), 400
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY가 설정되지 않았습니다."}), 500

    # 사전 검증 — 화면 md 가 있어야 함
    cls_check = classify_spec_files(folder)
    if not cls_check["screens"]:
        return jsonify({
            "ok": False,
            "error": f"화면 md 를 찾지 못했습니다. {folder}/scr/SCR-*.md 형식이 필요합니다.",
            "detail": {
                "overview": cls_check["overview"].name if cls_check["overview"] else None,
                "policy": [p.name for p in cls_check["policy"]],
                "design": [p.name for p in cls_check["design"]],
                "screens_count": 0,
            },
        }), 400

    sess = new_session()
    sess["project_name"] = project_name
    sess["focus_area"] = focus_area
    sess["generation_mode"] = "structured_spec"

    sources_to_save = [{"type": "spec_folder", "content": str(folder)}]
    if prev_folder:
        sources_to_save.append({"type": "spec_folder_prev", "content": str(Path(prev_folder).expanduser())})
    save_project(project_name, last_sources=sources_to_save, last_focus_area=focus_area)

    t = threading.Thread(
        target=run_pipeline_structured,
        args=(sess, str(folder), project_name,
              str(Path(prev_folder).expanduser()) if prev_folder else "",
              include_unchanged),
        daemon=True,
    )
    sess["thread"] = t
    t.start()
    return jsonify({
        "ok": True,
        "sid": sess["id"],
        "summary": {
            "overview": cls_check["overview"].name if cls_check["overview"] else None,
            "policy_count": len(cls_check["policy"]),
            "design_count": len(cls_check["design"]),
            "screens_count": len(cls_check["screens"]),
        },
    })


@app.route("/recent-spec-folders", methods=["GET"])
def recent_spec_folders():
    """프로젝트별 최근 사용 spec 폴더 목록 반환.
    Query: project_name=... (없으면 전체 프로젝트의 최근 폴더 합집합)
    Returns: {ok, folders: [path, ...]} — 존재하는 경로만, 최신 순.
    """
    project_name = request.args.get("project_name", "").strip()
    projects = load_projects()
    candidates: list[str] = []
    if project_name:
        proj = next((p for p in projects if p["name"] == project_name), None)
        if proj:
            candidates = list(proj.get("recent_spec_folders") or [])
        # 폴백 — 프로젝트의 last_sources 에서 spec_folder 추출
        if not candidates and proj:
            for src in (proj.get("last_sources") or []):
                if src.get("type") in ("spec_folder", "spec_folder_prev") and src.get("content"):
                    if src["content"] not in candidates:
                        candidates.append(src["content"])
    else:
        # 프로젝트 미지정 — 모든 프로젝트의 recent_spec_folders 합집합 (최신 5개)
        seen = set()
        for p in projects:
            for f in (p.get("recent_spec_folders") or []):
                if f not in seen:
                    seen.add(f)
                    candidates.append(f)
                if len(candidates) >= 10:
                    break
            if len(candidates) >= 10:
                break

    # 실제 존재하는 폴더만 필터
    folders = [f for f in candidates if Path(f).expanduser().is_dir()]
    return jsonify({"ok": True, "folders": folders[:10]})


@app.route("/preview-spec-folder", methods=["POST"])
def preview_spec_folder():
    """폴더 경로만 받아 미리 분류 결과 반환 (시작 전 검증용)."""
    data = request.get_json(force=True) or {}
    folder_path = (data.get("folder_path") or "").strip()
    if not folder_path:
        return jsonify({"ok": False, "error": "folder_path 가 비어 있습니다."}), 400
    folder = Path(folder_path).expanduser()
    if not folder.exists() or not folder.is_dir():
        return jsonify({"ok": False, "error": f"폴더 없음: {folder}"}), 400

    cls = classify_spec_files(folder)
    overview_text = cls["overview"].read_text(encoding="utf-8") if cls["overview"] else ""
    rows = parse_screen_list_table(overview_text) if overview_text else []
    return jsonify({
        "ok": True,
        "folder": str(folder),
        "overview": cls["overview"].name if cls["overview"] else None,
        "policy": [p.name for p in cls["policy"]],
        "design": [p.name for p in cls["design"]],
        "screens": [p.name for p in cls["screens"]],
        "screen_rows_count": len(rows),
        "majors": sorted(set(r["major"] for r in rows if r["major"])),
    })


@app.route("/diff-spec-folders", methods=["POST"])
def diff_spec_folders_route():
    """두 폴더 비교 미리보기 — 변경 SCR 목록 반환."""
    data = request.get_json(force=True) or {}
    new_path = (data.get("folder_path") or "").strip()
    prev_path = (data.get("prev_folder_path") or "").strip()
    if not new_path or not prev_path:
        return jsonify({"ok": False, "error": "folder_path 와 prev_folder_path 모두 필요합니다."}), 400
    new_p = Path(new_path).expanduser()
    prev_p = Path(prev_path).expanduser()
    if not new_p.exists() or not new_p.is_dir():
        return jsonify({"ok": False, "error": f"신규 폴더 없음: {new_p}"}), 400
    if not prev_p.exists() or not prev_p.is_dir():
        return jsonify({"ok": False, "error": f"이전 폴더 없음: {prev_p}"}), 400
    try:
        diff = diff_spec_folders(prev_p, new_p)
    except Exception as e:
        return jsonify({"ok": False, "error": f"diff 실패: {e}"}), 500
    return jsonify({
        "ok": True,
        "new_folder": str(new_p),
        "prev_folder": str(prev_p),
        "added": diff["added"],
        "modified": diff["modified"],
        "removed": diff["removed"],
        "unchanged_count": len(diff["unchanged"]),
        "common_changed": diff["common_changed"],
        "regenerate_count": len(diff["added"]) + len(diff["modified"]),
    })


@app.route("/check-resume-spec", methods=["GET"])
def check_resume_spec():
    """프로젝트의 구조화 spec 모드 체크포인트가 있는지 확인.
    Query: project_name=...
    Returns: {ok, resumable, stage, completed_screens, total_screens, ...}
    """
    project_name = request.args.get("project_name", "").strip()
    if not project_name:
        return jsonify({"ok": False, "error": "project_name 필요"}), 400
    state = load_pipeline_state(project_name)
    if not state:
        return jsonify({"ok": True, "resumable": False})
    ckpt = state["data"]
    folder = ckpt.get("structured_spec_folder")
    if not folder:
        return jsonify({"ok": True, "resumable": False, "reason": "구조화 spec 모드 체크포인트 아님"})
    workspace = ckpt.get("workspace")
    completed = []
    if workspace and Path(workspace).exists():
        per_screen_dir = Path(workspace) / "per_screen"
        if per_screen_dir.exists():
            completed = sorted([p.stem for p in per_screen_dir.glob("SCR-*.md")])
    # 신규 폴더에서 화면 개수 다시 계산 (참고용)
    folder_p = Path(folder)
    total = 0
    if folder_p.exists():
        cls = classify_spec_files(folder_p)
        total = len(cls["screens"])
    return jsonify({
        "ok": True,
        "resumable": True,
        "stage": state["stage"],
        "folder": folder,
        "prev_folder": ckpt.get("prev_folder", ""),
        "completed_screens": completed,
        "completed_count": len(completed),
        "total_screens": total,
        "remaining": max(total - len(completed), 0) if total else None,
    })


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
    # 생성 모드: "summary" (기본, policy/features/classify 3단계) / "direct" (원문 직접 분류)
    gen_mode = (data.get("generation_mode") or "summary").strip().lower()
    if gen_mode not in ("summary", "direct"):
        gen_mode = "summary"
    sess["generation_mode"] = gen_mode
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
    """프로젝트 삭제. 빈 이름 유령 레코드도 함께 정리."""
    # 유령 레코드(name=빈값)를 포함한 잘못된 레코드까지 정리
    raw = []
    if PROJECTS_FILE.exists():
        try:
            raw = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            raw = []
    target = (project_name or "").strip()
    cleaned = [
        p for p in raw
        if isinstance(p, dict) and (p.get("name") or "").strip() and p.get("name") != target
    ]
    PROJECTS_FILE.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
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


@app.route("/upload-existing-tc", methods=["POST"])
def upload_existing_tc():
    """기존 TC 파일(MD/Excel)을 업로드하여 specs 또는 tc_files에 저장.
    반환: 저장 경로 + 감지된 TC 개수.
    """
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "파일 없음"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"ok": False, "error": "파일명 없음"}), 400
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ("md", "markdown", "xlsx", "xls"):
        return jsonify({"ok": False, "error": ".md / .xlsx 파일만 허용"}), 400
    # 업로드 저장 — tc_files 디렉토리 (Excel 포함)
    save_path = TC_FILES_DIR / f.filename
    f.save(str(save_path))
    try:
        tcs = load_existing_tcs(save_path)
    except Exception as e:
        return jsonify({"ok": False, "error": f"TC 파일 파싱 실패: {e}"}), 400
    return jsonify({
        "ok": True,
        "filename": f.filename,
        "tc_count": len(tcs),
        "tc_ids_sample": [t["id"] for t in tcs[:5]],
    })


def _tc_to_markdown_block(tc: dict) -> str:
    """파싱된 TC dict를 markdown TC 블록 형식으로 직렬화 (build_excel가 파싱 가능한 포맷).
    이미 raw_text가 있으면 그걸 사용 (업데이트 전 원본 보존용)."""
    if tc.get("raw_block"):
        return tc["raw_block"]
    tid = tc.get("id", "")
    title = tc.get("title", "") or tid
    bold = "**" if tc.get("is_min") else ""
    header = f"### {bold}{tid}{bold} — {title}"
    table = [
        f"| 대분류 | {tc.get('major', '')} |",
        f"| 중분류 | {tc.get('middle', '')} |",
        f"| 소분류 | {tc.get('minor', '')} |",
        f"| 분류 | {tc.get('type', 'Positive')} |",
        f"| 우선순위 | {tc.get('priority', 'Medium')} |",
    ]
    if tc.get("screen") or tc.get("screen_code"):
        table.append(f"| 연관 화면 | {tc.get('screen') or tc.get('screen_code')} |")
    sections = [
        f"**사전 조건**\n{tc.get('precondition', '')}",
        f"**테스트 단계**\n{tc.get('steps', '')}",
        f"**예상 결과**\n{tc.get('expected', '')}",
    ]
    if tc.get("note"):
        sections.append(f"**비고**\n{tc['note']}")
    return "\n".join([header, "", "| 항목 | 내용 |", "|------|------|", *table, "", *sections])


def _save_tc_history_snapshot(project_name: str, existing_tcs: list[dict]) -> Path:
    """업데이트 실행 직전의 TC 상태를 tc_history/에 스냅샷 저장."""
    history_dir = BASE_DIR / "tc_history" / (re.sub(r"[^\w\-_]", "_", project_name or "unnamed")[:30])
    history_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    snap_path = history_dir / f"snapshot_{ts}.md"
    parts = [f"# TC 스냅샷 — {project_name or '(unnamed)'}\n\n생성: {datetime.now().isoformat()}\n\n---\n"]
    for tc in existing_tcs:
        parts.append(_tc_to_markdown_block(tc))
        parts.append("\n")
    snap_path.write_text("\n\n".join(parts), encoding="utf-8")
    return snap_path


def _update_tc_for_modified_scr(tc: dict, new_section: str,
                                  tc_rules: str) -> tuple[dict, str]:
    """수정된 SCR에 대해 기존 TC 하나를 새 사양 기반으로 재작성.
    반환: (업데이트된 TC dict, AI가 서술한 수정 사유)
    """
    system = """당신은 시니어 QA 엔지니어입니다. 기존 TC를 새 기획서 섹션 기반으로 **업데이트**합니다.

규칙:
- TC ID는 **절대 변경하지 마세요** — 그대로 유지
- 사전 조건 / 테스트 단계 / 예상 결과를 새 사양에 맞게 재작성
- 기존 대분류/중분류/소분류 유지 (사양에서 변경된 경우만 수정)
- 이미 존재하는 Given/When/Then 구조와 어투를 따르세요
- 수정 사유를 한 문장(50자 이내)으로 요약하여 마지막에 `수정 사유: ...` 형식으로 포함
"""
    user = f"""기존 TC (업데이트 대상):
---
{_tc_to_markdown_block(tc)[:3000]}
---

새 기획서 섹션 (이 TC가 커버하는 화면의 변경된 내용):
---
{new_section[:4000]}
---

위 기존 TC를 새 기획서에 맞게 업데이트해주세요. TC ID는 그대로 유지.
출력 형식: 기존 TC와 동일한 markdown 블록 + 마지막에 `수정 사유: ...` 한 줄 추가.
"""
    try:
        result = call_claude(system, user, max_tokens=3000)
    except Exception as e:
        return tc, f"AI 오류로 원본 유지: {e}"

    # 수정 사유 추출
    reason = ""
    m = re.search(r"수정\s*사유\s*[:：]\s*(.+)", result)
    if m:
        reason = m.group(1).strip().split("\n")[0][:200]
        result = re.sub(r"수정\s*사유\s*[:：].*$", "", result, flags=re.MULTILINE).rstrip()

    # 결과 파싱하여 새 TC dict 생성
    try:
        parsed = parse_tc_markdown(result)
        if parsed:
            updated = parsed[0]
            updated["id"] = tc["id"]  # ID 강제 유지
            updated["status"] = "🔄 수정됨"
            updated["change_reason"] = reason
            updated["raw_block"] = result.strip()
            # 기존에 있던 필드 중 새 파싱에 없는 것 보존 (screen_code 등)
            for k, v in tc.items():
                if k not in updated and v:
                    updated[k] = v
            return updated, reason
    except Exception as e:
        return tc, f"파싱 실패로 원본 유지: {e}"
    return tc, reason


@app.route("/analyze-diff", methods=["POST"])
def analyze_diff():
    """기획서 변경 기반 TC 수정 — 1단계: 두 기획서 + 기존 TC 파일 분석.

    입력 JSON:
      {
        "project_name": (optional) — 저장된 프로젝트 이름. 로그/저장용.
        "old_spec_path":  (필수) SPECS_DIR 내 파일명
        "new_spec_path":  (필수) SPECS_DIR 내 파일명
        "existing_tc_path": (선택) TC_FILES_DIR 내 파일명. 없으면 "diff만 분석".
      }

    반환: build_diff_report() 결과 + 추가 메타.
    """
    data = request.get_json(force=True) or {}
    project_name = (data.get("project_name") or "").strip()
    old_path_name = (data.get("old_spec_path") or "").strip()
    new_path_name = (data.get("new_spec_path") or "").strip()
    tc_path_name = (data.get("existing_tc_path") or "").strip()

    if not new_path_name:
        return jsonify({"ok": False, "error": "새 기획서가 필요합니다."}), 400
    if not old_path_name:
        return jsonify({"ok": False, "error": "이전 기획서가 필요합니다."}), 400

    old_path = SPECS_DIR / old_path_name
    new_path = SPECS_DIR / new_path_name
    if not old_path.exists():
        return jsonify({"ok": False, "error": f"이전 기획서 파일 없음: {old_path_name}"}), 400
    if not new_path.exists():
        return jsonify({"ok": False, "error": f"새 기획서 파일 없음: {new_path_name}"}), 400

    try:
        old_md = old_path.read_text(encoding="utf-8")
        new_md = new_path.read_text(encoding="utf-8")
    except Exception as e:
        return jsonify({"ok": False, "error": f"기획서 읽기 실패: {e}"}), 400

    # 기존 TC 로드 (선택)
    existing_tcs = []
    tc_load_error = None
    if tc_path_name:
        tc_path = TC_FILES_DIR / tc_path_name
        if not tc_path.exists():
            # SPECS_DIR도 확인 (업로드 경로가 달랐을 경우 대비)
            alt = SPECS_DIR / tc_path_name
            if alt.exists():
                tc_path = alt
            else:
                return jsonify({"ok": False, "error": f"기존 TC 파일 없음: {tc_path_name}"}), 400
        try:
            existing_tcs = load_existing_tcs(tc_path)
        except Exception as e:
            tc_load_error = str(e)

    # 리포트 생성
    report = build_diff_report(old_md, new_md, existing_tcs)

    # 변경 없음 확인
    summary = report["summary"]
    no_changes = (summary["added_n"] == 0 and summary["modified_n"] == 0
                  and summary["removed_n"] == 0)

    # 세션 생성 (이후 /update-tc 호출 시 재사용)
    sess = new_session()
    sess["project_name"] = project_name
    sess["_diff_context"] = {
        "old_md": old_md,
        "new_md": new_md,
        "existing_tcs": existing_tcs,
        "report": report,
        "old_spec_name": old_path_name,
        "new_spec_name": new_path_name,
        "tc_path_name": tc_path_name,
    }

    return jsonify({
        "ok": True,
        "sid": sess["id"],
        "report": report,
        "no_changes": no_changes,
        "existing_tc_count": len(existing_tcs),
        "tc_load_error": tc_load_error,
        "has_spec_codes": report.get("has_spec_codes", False),
    })


@app.route("/update-tc", methods=["POST"])
def update_tc():
    """analyze-diff로 생성된 리포트 승인 후 실제 TC 갱신 실행.

    입력 JSON:
      {
        "sid": (필수) — analyze-diff에서 받은 세션 ID
        "approved": {
          "added":   ["SCR-020", "SCR-021"],      # 승인된 신규 SCR 코드 목록
          "modified":["SCR-001"],                 # 승인된 수정 SCR 코드 목록
          "removed": ["SCR-008"],                 # 승인된 삭제 SCR 코드 목록 (Deprecated 처리)
        }
      }

    흐름:
      1. 스냅샷 저장 (tc_history/)
      2. 승인된 신규 SCR → 신규 TC 생성 (새 파이프라인 트리거)
      3. 승인된 수정 SCR → 기존 TC 재작성 (ID 유지)
      4. 승인된 삭제 SCR → 해당 TC에 status=Deprecated
      5. 영향 없는 TC → 상태 빈 값 (유지)
      6. 결과 TC 리스트 → Excel 빌드
    """
    data = request.get_json(force=True) or {}
    sid = (data.get("sid") or "").strip()
    approved = data.get("approved") or {}

    sess = SESSIONS.get(sid)
    if not sess:
        return jsonify({"ok": False, "error": "세션 없음 — /analyze-diff를 먼저 호출하세요."}), 404
    ctx = sess.get("_diff_context")
    if not ctx:
        return jsonify({"ok": False, "error": "diff 컨텍스트 없음"}), 400
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY 미설정"}), 500

    approved_added    = set(approved.get("added") or [])
    approved_modified = set(approved.get("modified") or [])
    approved_removed  = set(approved.get("removed") or [])

    # 백엔드 가드 — 승인 항목이 하나도 없으면 빈 Excel 생성 방지
    if not (approved_added or approved_modified or approved_removed):
        return jsonify({
            "ok": False,
            "error": "승인된 변경사항이 없습니다. 최소 1개 이상의 항목을 체크한 뒤 승인하세요."
        }), 400

    def worker():
        try:
            existing_tcs = list(ctx["existing_tcs"])  # copy
            project_name = sess.get("project_name", "")

            # 1. 스냅샷
            push_log(sess, "[갱신] TC 스냅샷 저장 중...")
            snap = _save_tc_history_snapshot(project_name, existing_tcs)
            push_log(sess, f"[갱신] 스냅샷 저장됨: {snap.name}")
            push_stage(sess, 2, "기존 TC 스냅샷 저장 완료", 10)

            # 2. 새 기획서의 SCR별 섹션 추출 (TC 재작성용 근거)
            new_sections = _extract_spec_sections(ctx["new_md"])
            report = ctx["report"]

            # 공통: tc_rules / fewshot 로드
            tc_rules = load_tc_rules()
            fewshot = load_fewshot_examples()
            project_policies = load_project_policies(project_name)
            project_code = _detect_project_code(project_name)

            # 3. 수정된 SCR별 TC 재작성
            tc_by_scr = group_tcs_by_scr(existing_tcs)
            modified_count = 0
            total_modified_tcs = sum(
                len(tc_by_scr.get(code, []))
                for code in approved_modified
            )
            done_mod_tcs = 0
            for code in approved_modified:
                affected = tc_by_scr.get(code, [])
                new_section = new_sections.get(code, {}).get("body", "")
                if not new_section:
                    push_log(sess, f"[갱신] ⚠️ {code} 새 섹션 없음 — 건너뜀")
                    continue
                for tc in affected:
                    push_log(sess, f"[갱신] 수정 ({code}) → {tc.get('id')}")
                    updated_tc, reason = _update_tc_for_modified_scr(tc, new_section, tc_rules)
                    # existing_tcs에서 ID로 찾아 교체
                    for i, t in enumerate(existing_tcs):
                        if t.get("id") == updated_tc.get("id"):
                            existing_tcs[i] = updated_tc
                            break
                    modified_count += 1
                    done_mod_tcs += 1
                    pct = 10 + int(40 * done_mod_tcs / max(total_modified_tcs, 1))
                    push_stage(sess, 2, f"수정 TC 재작성 {done_mod_tcs}/{total_modified_tcs}", pct, eta_sec=(total_modified_tcs - done_mod_tcs) * 30)

            # 4. 삭제된 SCR → Deprecated 태그
            deprecated_count = 0
            for code in approved_removed:
                affected = tc_by_scr.get(code, [])
                for tc in affected:
                    for i, t in enumerate(existing_tcs):
                        if t.get("id") == tc.get("id"):
                            existing_tcs[i]["status"] = "🗑️ Deprecated"
                            existing_tcs[i]["change_reason"] = f"{code} 삭제로 폐기"
                            deprecated_count += 1
                            break
            push_log(sess, f"[갱신] Deprecated 처리 {deprecated_count}건")

            # 5. 신규 SCR → 신규 TC 생성
            added_tc_count = 0
            if approved_added:
                push_stage(sess, 3, f"신규 SCR {len(approved_added)}개 TC 생성 중", 55, eta_sec=len(approved_added) * 40)
                # 분류표 임시 생성 — 각 신규 SCR을 별도 중분류로
                temp_classification_parts = [f"# TC 분류표 — 신규 추가"]
                for code in approved_added:
                    new_s = new_sections.get(code, {})
                    name = new_s.get("name") or code
                    temp_classification_parts.append(f"\n## 대분류: 신규 화면\n\n### 중분류: {name}\n\n#### 소분류\n- 화면 진입/표시/동작: {code} 기본 TC")
                temp_classification = "\n".join(temp_classification_parts)

                # 각 신규 SCR마다 단일 호출로 TC 생성
                for idx, code in enumerate(approved_added):
                    new_s = new_sections.get(code, {})
                    name = new_s.get("name") or code
                    body = new_s.get("body", "")
                    # build_tc_user_prompt 사용을 위한 domain 객체 구성
                    domain = {"name": "신규 화면", "code": "NEWSCR",
                              "suite_code": re.sub(r"[^A-Za-z]", "", name).upper()[:6] or "NEW",
                              "_focus_middle": name}
                    # 연관 화면 코드 hint 주입을 위해 body에 code 포함
                    prompt_context = f"{code}: {name}\n\n{body}"
                    starting_seq = next_tc_id(existing_tcs, project_code, domain["suite_code"])
                    user_prompt = build_tc_user_prompt(
                        domain, prompt_context, prompt_context, project_name,
                        temp_classification, starting_seq=starting_seq,
                        source_scr_map=(sess.get("_source_scr_map") or {}),
                    )
                    system_prompt = build_tc_system_prompt(
                        tc_rules, temp_classification, project_policies, fewshot
                    )
                    push_log(sess, f"[갱신] 신규 ({code}) TC 생성 중...")
                    try:
                        tc_md = call_claude(system_prompt, user_prompt, max_tokens=8000)
                    except Exception as e:
                        push_log(sess, f"[갱신] {code} 생성 실패: {e}")
                        continue
                    # TC ID 재번호
                    tc_md, _ = renumber_tc_ids(tc_md, project_code, domain["suite_code"], starting_seq)
                    new_tcs = parse_tc_markdown(tc_md)
                    for nt in new_tcs:
                        nt["status"] = "🆕 신규"
                        nt["change_reason"] = f"{code} 추가로 신규 생성"
                        nt["screen_code"] = code
                        nt["screen"] = code
                        existing_tcs.append(nt)
                        added_tc_count += 1

            # 6. 결과 마크다운 생성 → Excel 빌드
            push_stage(sess, 4, "tc_final.md 저장 중", 85, eta_sec=5)
            final_md = "\n\n---\n\n".join(_tc_to_markdown_block(t) for t in existing_tcs)
            workspace = sess["workspace"]
            tc_final_path = workspace / "tc_final.md"
            tc_final_path.write_text(final_md, encoding="utf-8")

            # Excel 빌드 — 기존 TC 수정 플로우이므로 상태/수정 사유 컬럼 + 🔄 변경 이력 시트 포함
            sess["_include_change_columns"] = True
            push_stage(sess, 5, "Excel 빌드 중", 92, eta_sec=60)
            excel_path = step_build_excel(sess, final_md, project_name,
                                           total_tc=len(existing_tcs),
                                           min_tc=max(1, round(len(existing_tcs) * 0.35)))
            # 후처리 적용본 채택 (MD ↔ Excel 일치)
            final_md = sess.get("_tc_content_disambiguated", final_md)

            # tc_files에 저장
            today = datetime.now().strftime("%Y%m%d")
            safe_name = re.sub(r"[^\w\-_]", "_", project_name or "Updated")[:30]
            tc_md_path = TC_FILES_DIR / f"{safe_name}_{today}.md"
            tc_md_path.write_text(final_md, encoding="utf-8")
            save_project(project_name, str(tc_md_path), str(excel_path))

            # 변경 이력 요약 저장
            change_log_path = workspace / "change_log.md"
            change_log_path.write_text(
                f"# 변경 이력\n\n"
                f"- 수정된 TC: {modified_count}건\n"
                f"- Deprecated TC: {deprecated_count}건\n"
                f"- 신규 TC: {added_tc_count}건\n"
                f"- 스냅샷: {snap}\n",
                encoding="utf-8"
            )

            # 유니크 TC ID 수 — Excel dedup 결과와 일치하도록 재계산
            unique_tc = count_unique_tc_ids(final_md) or len(existing_tcs)

            sess["result"] = excel_path
            sess["status"] = "done"
            push_stage(sess, 5, "완료", 100)
            push(sess, "done", {
                "filename": excel_path.name,
                "size": excel_path.stat().st_size,
                "sid": sess["id"],
                "total_tc": unique_tc,
                "smoke_tc": sess.get("smoke_tc"),
                "min_tc": max(1, round(unique_tc * 0.35)),
                "update_summary": {
                    "modified": modified_count,
                    "deprecated": deprecated_count,
                    "added": added_tc_count,
                },
            })
            push_log(sess, f"[완료] 업데이트 반영 — 수정 {modified_count} / 추가 {added_tc_count} / Deprecated {deprecated_count}")
        except Exception as e:
            push_log(sess, f"[오류] {e}")
            push_error(sess, str(e))

    t = threading.Thread(target=worker, daemon=True)
    sess["thread"] = t
    t.start()
    return jsonify({"ok": True, "sid": sess["id"]})


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


@app.route("/screen-code-map", methods=["GET"])
def get_screen_code_map():
    """프로젝트별 Screen Code 매핑 테이블 조회.

    프론트엔드의 Human Gate에서 "시스템 규칙 자동 적용" 모드 ON 시,
    각 중분류가 어떤 ScreenCode로 매핑될지 미리보기하는 데 사용.
    """
    project_name = request.args.get("project", "").strip()
    project_code = _detect_project_code(project_name)
    screen_based_default = _is_screen_based(project_code)
    mapping = load_screen_code_map(project_name) if project_name else {}
    return jsonify({
        "ok": True,
        "project_code": project_code,
        "screen_based_default": screen_based_default,
        "map": mapping,
    })


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
        # v0.9.18: 사용자 친화적 메시지 — 서버 재시작 등으로 세션 소실 시
        return jsonify({
            "ok": False,
            "error": "세션이 만료되었습니다. 서버가 재시작됐을 수 있어요.\n페이지를 새로고침하고 '이어서 작업'을 클릭하면 분류표 검토 단계부터 복원됩니다."
        }), 404
    data = request.get_json(force=True) or {}
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"ok": False, "error": "승인할 내용이 없습니다."}), 400
    # 선택된 대분류 코드 저장 (None이면 전체 생성)
    selected = data.get("selected_domains")  # list of codes or null
    sess["selected_domains"] = selected if selected else None
    # SuiteCode 저장 (검토자가 Human Gate에서 입력)
    suite_codes = data.get("suite_codes")  # list of codes
    sess["suite_codes"] = suite_codes if suite_codes else []
    # 시스템 규칙 자동 적용 (screen_code_map 기반 Screen-based 스킴) 여부.
    # None이면 프로젝트 코드 기반 자동 판별 (_is_screen_based).
    # True/False면 사용자 명시적 선택 우선.
    auto_flag = data.get("auto_screen_code")
    sess["auto_screen_code"] = auto_flag  # None / True / False
    # ── Excel 시트 옵션 (Full/Light/Custom 프리셋 → 시트별 dict) ──
    # 프론트가 보내는 형식:
    #   {"cover": bool, "stats": bool, "smoke": bool,
    #    "traceability": bool, "tc_list": bool, "change_history": bool}
    # 누락/None 이면 step_build_excel 에서 Full Set 으로 폴백
    excel_sheets = data.get("excel_sheets")
    if isinstance(excel_sheets, dict):
        sess["_excel_sheets"] = {k: bool(v) for k, v in excel_sheets.items()}
    sess["approved"] = content
    sess["gate_event"].set()
    return jsonify({"ok": True})


@app.route("/gate-chat/<sid>", methods=["POST"])
def gate_chat(sid):
    """Human Gate 채팅 — AI와 대화하며 분류표/영향도 문서를 수정"""
    import anthropic
    sess = SESSIONS.get(sid)
    if not sess:
        # v0.9.18: 사용자 친화적 메시지
        return jsonify({
            "ok": False,
            "error": "세션이 만료되었습니다. 서버가 재시작됐을 수 있어요.\n페이지를 새로고침하고 '이어서 작업'을 클릭하면 분류표 검토 단계부터 복원됩니다."
        }), 404
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
현재 AI가 생성한 '분류표' 문서를 사용자의 요청에 따라 적극적으로 수정합니다.

## 절대 규칙

1. **짧은 명령형 요청도 명확한 수정 의도로 해석하세요** (한국어 특성).
   - "splash 케이스 삭제" → Splash 관련 중분류/소분류를 모두 제거
   - "이메일 입력 빼줘" → Email Input 중분류 제거
   - "AUTH 대분류 3번 지워" → AUTH 대분류의 3번째 항목 제거
   - "체크박스 기능 빼" → 체크박스 관련 항목 모두 제거

2. **삭제 요청을 절대 거부하지 마세요**. 사용자가 "X 삭제/제거/빼줘" 라고 하면 X 와 관련된 항목을 분류표에서 모두 찾아 제거하세요.

3. **모호한 경우에도 일단 수정 시도하고, [REPLY] 에 어떤 해석을 했는지 명시**하세요. 거부 대신 "Splash 관련 항목을 모두 제거했습니다. 다른 의도였으면 알려주세요." 식으로.

4. **수정이 필요 없는 진짜 질문(단순 문의)** 일 때만 기존 문서 그대로 반환:
   - "Splash 가 뭐야?" — 질문이므로 [DOCUMENT] 그대로
   - "이 분류표 잘 만든 거 같아?" — 평가 질문이므로 그대로
   - "splash 삭제" — 명령이므로 반드시 수정

## 응답 형식 (반드시 준수)

응답은 정확히 두 부분으로 구성:
1. [REPLY] 태그: 수정 내용 명확히 (예: "Onboarding 대분류의 Splash 중분류 1개를 제거했습니다.")
2. [DOCUMENT] 태그: 수정된 **전체** 분류표 (마크다운 형식 유지, 잘리지 않게 끝까지)

분류표 형식(## 대분류, ### 중분류, 표 컬럼, TC ID 패턴) 유지."""

    # 메시지 구성 — 히스토리 + 현재 문서 컨텍스트 + 사용자 메시지
    messages = []
    for h in history:
        messages.append({"role": h["role"], "content": h["content"]})

    # 현재 문서를 컨텍스트로 포함
    full_user_msg = f"""현재 문서:\n```\n{current_doc}\n```\n\n사용자 요청: {user_msg}"""
    messages.append({"role": "user", "content": full_user_msg})

    # v0.9.20: max_tokens 4096 → 16384 (긴 분류표 출력 잘림 방지)
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=16384,
            temperature=0,
            system=system_prompt,
            messages=messages
        )
        ai_text = resp.content[0].text
        stop_reason = getattr(resp, "stop_reason", None)

        # [REPLY]와 [DOCUMENT] 파싱
        reply_text = ""
        updated_doc = current_doc  # 기본값: 변경 없음
        truncated = False

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
            # 잘림 감지: stop_reason == "max_tokens" 또는 출력이 비정상적으로 짧음
            if stop_reason == "max_tokens":
                truncated = True
                push_log(sess, "[Gate] AI 응답이 max_tokens 도달 — 분류표가 잘렸을 수 있음")

        if not reply_text:
            reply_text = ai_text.strip()

        # 잘림 감지 시 사용자 알림 + 원본 유지 (잘린 문서로 덮어쓰기 방지)
        if truncated:
            updated_doc = current_doc
            reply_text = "⚠️ 응답이 너무 길어 잘렸습니다. 더 작은 단위로 나눠서 요청해 주세요. (예: 'Splash 한 번에' 대신 'Splash 중분류 1개만 삭제')\n\n" + reply_text

        # ── v0.9.15: 분류표 모드에서 변경이 감지되면 features/policy 도 동기화 ──
        # 사용자가 "체크박스 기능 제거" 등 의미 있는 수정을 했을 때, 본문(features/policy)에서도
        # 해당 항목을 제거하여 TC 작성 시 일관된 컨텍스트가 전달되도록 함.
        sync_status = None  # 'synced' | 'unchanged' | 'failed'
        if gate_mode == "new" and updated_doc and updated_doc != current_doc:
            try:
                sync_status = _sync_features_policy_with_classification(
                    sess, client, updated_doc, current_doc, user_msg
                )
                if sync_status == "synced":
                    reply_text += "\n\n📌 본문 정책·기능 정보도 분류표와 일관되도록 자동 동기화했습니다."
            except Exception as _sync_e:
                sync_status = "failed"
                # 동기화 실패해도 분류표 수정은 그대로 반영 (최소 보장)
                push_log(sess, f"[Gate] features/policy 동기화 실패 (분류표만 반영): {_sync_e}")

        return jsonify({
            "ok": True,
            "reply": reply_text,
            "updated_doc": updated_doc,
            "sync_status": sync_status,
            "changed": updated_doc != current_doc,  # v0.9.20: 변경 여부 명시
            "truncated": truncated,                  # v0.9.20: 잘림 여부
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


def _sync_features_policy_with_classification(sess, client, new_classification, old_classification, user_msg):
    """v0.9.15: Gate 채팅에서 분류표가 수정되면 features/policy 도 함께 동기화.

    사용자의 의도(예: "체크박스 기능 제거")를 본문 문서에도 반영하여
    TC 작성 시 분류표·본문 사이의 모순을 제거.

    Returns:
        "synced" — 동기화 성공
        "unchanged" — features/policy 가 sess 에 없거나 변경 사항이 사소함
        "failed" — AI 호출 실패 (예외 raise 됨)
    """
    features_text = sess.get("_features_text", "")
    policy_text = sess.get("_policy_text", "")
    if not features_text and not policy_text:
        return "unchanged"  # gate 단계 진입 전이거나 복원 케이스 — 동기화 불가

    sync_system = """당신은 TC 분류 전문가입니다. 사용자가 분류표를 수정했을 때, 본문 정책·기능 문서를 분류표와 일관되게 동기화합니다.

규칙:
- 사용자의 분류표 변경(추가/제거/수정)을 본문 문서에 반영하세요.
- 분류표에서 **제거된 항목** 은 본문 정책·기능 문서에서도 제거하세요.
- 분류표에서 **수정된 항목** 은 본문 문서에서도 동일하게 수정하세요.
- 분류표에 그대로 있는 항목은 본문 문서에서도 유지하세요.
- 분류표 변경과 무관한 본문 내용은 절대 변경하지 마세요.
- 응답은 반드시 다음 두 부분으로 구성:
  1. [POLICY] 태그: 동기화된 정책 문서 전체
  2. [FEATURES] 태그: 동기화된 기능 문서 전체
- 변경할 내용이 없으면 두 태그 안에 원본을 그대로 포함하세요."""

    sync_user = f"""## 사용자 요청
{user_msg}

## 변경 전 분류표
```
{old_classification[:8000]}
```

## 변경 후 분류표 (사용자 승인 — 최종)
```
{new_classification[:8000]}
```

## 현재 정책 문서 (동기화 대상)
```
{policy_text[:10000]}
```

## 현재 기능 문서 (동기화 대상)
```
{features_text[:10000]}
```

위 분류표 변경에 맞춰 정책·기능 문서를 동기화한 결과를 [POLICY] 와 [FEATURES] 태그로 반환하세요."""

    resp = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        temperature=0,
        system=sync_system,
        messages=[{"role": "user", "content": sync_user}],
    )
    sync_text = resp.content[0].text

    # [POLICY] / [FEATURES] 파싱
    policy_match = re.search(r'\[POLICY\](.*?)(?=\[FEATURES\]|$)', sync_text, re.DOTALL)
    features_match = re.search(r'\[FEATURES\](.*?)$', sync_text, re.DOTALL)

    new_policy = policy_text
    new_features = features_text

    if policy_match:
        candidate = policy_match.group(1).strip()
        # 코드블록 래핑 제거
        if candidate.startswith("```"):
            lines = candidate.split("\n")
            candidate = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()
        if candidate:
            new_policy = candidate

    if features_match:
        candidate = features_match.group(1).strip()
        if candidate.startswith("```"):
            lines = candidate.split("\n")
            candidate = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()
        if candidate:
            new_features = candidate

    # 세션 갱신
    sess["_policy_text"] = new_policy
    sess["_features_text"] = new_features
    return "synced"


@app.route("/merge-classification/<sid>", methods=["POST"])
def merge_classification(sid):
    """Stage 1 — 분류표 자동 정리 (TC 작성 전).

    예측된 중복 가능성에 따라 AI 가 분류표 재구성:
    - 같은 그룹 내 비기능 TC 후보를 entry 화면에 통합 (비고에 [통합] 명시)
    - 중분류 자체는 보존 (사용자 의도 명시 없으면 함부로 통합 X)

    응답: { "ok": true, "updated_doc": str, "predictions_resolved": int }
    """
    import anthropic
    sess = SESSIONS.get(sid)
    if not sess:
        return jsonify({
            "ok": False,
            "error": "세션이 만료되었습니다. 페이지를 새로고침하고 '이어서 작업'을 클릭하세요."
        }), 404
    if sess.get("status") != "gate_waiting":
        return jsonify({"ok": False, "error": "Gate 대기 상태가 아닙니다."}), 400

    data = request.get_json(force=True) or {}
    current_doc = (data.get("current_doc") or "").strip()
    predictions = data.get("predictions") or []
    if not current_doc:
        return jsonify({"ok": False, "error": "분류표가 비어있습니다."}), 400
    if not predictions:
        return jsonify({"ok": False, "error": "통합할 예측 정보가 없습니다."}), 400

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY 미설정"}), 500
    client = anthropic.Anthropic(api_key=api_key)

    # 예측 결과 텍스트화
    pred_text_lines = []
    for i, p in enumerate(predictions, 1):
        major = p.get("major", "")
        rec = p.get("recommendation", "")
        if p.get("type") == "shared_minor":
            kw = p.get("shared_keyword", "")
            mids = p.get("shared_in_middles", [])
            pred_text_lines.append(f"{i}. [{major}] '{kw}' 키워드가 {len(mids)}개 중분류에 등장 ({', '.join(mids)}). {rec}")
        else:
            mc = p.get("middle_count", 0)
            mids = p.get("middles", [])
            pred_text_lines.append(f"{i}. [{major}] 중분류 {mc}개 → {rec}")
    pred_text = "\n".join(pred_text_lines)

    system_prompt = """당신은 TC 분류 전문가입니다. 분류표에서 중복 가능성을 줄이도록 정리합니다.

## 절대 규칙

1. **중분류 자체를 함부로 삭제하지 마세요** — 사용자가 명시적으로 요청한 경우만 삭제.
2. **소분류는 정리 가능** — 같은 그룹 내 여러 중분류에 같은 비기능 소분류가 반복되면, 그룹 entry 화면(첫 번째 중분류 또는 'Splash'/'Sign-in Start' 같은 진입 성격) 1개로 통합하고 다른 중분류에선 제거.
3. **통합된 소분류 옆에 [통합] 표시** — 예: "- 로딩 시간 [통합 — 그룹 대표 화면 검증]"
4. **응답은 두 부분 형식 유지**:
   1. [REPLY] 태그: 무엇을 정리했는지 1-3문장 요약
   2. [DOCUMENT] 태그: 정리된 전체 분류표 (마크다운)
5. **분류표 형식 유지** (## 대분류, ### 중분류, 소분류 불릿)
"""

    user_msg = f"""## 현재 분류표
```
{current_doc[:12000]}
```

## 발견된 중복 가능성 ({len(predictions)}개)
{pred_text}

## 통합 지시
위 예측에 따라 분류표의 비기능 소분류 (네트워크/타임아웃/로딩 시간 등) 를 그룹 대표 화면 1개에만 남기고 다른 중분류에선 제거하세요.
스펙 명시 케이스(에러 처리 등 고유 시나리오) 는 유지하세요.
"""

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=16384,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_msg}],
        )
        ai_text = resp.content[0].text
        stop_reason = getattr(resp, "stop_reason", None)

        reply_match = re.search(r'\[REPLY\](.*?)(?=\[DOCUMENT\]|$)', ai_text, re.DOTALL)
        doc_match = re.search(r'\[DOCUMENT\](.*?)$', ai_text, re.DOTALL)
        reply_text = reply_match.group(1).strip() if reply_match else ai_text.strip()
        updated_doc = current_doc
        if doc_match:
            updated_doc = doc_match.group(1).strip()
            if updated_doc.startswith("```"):
                lines = updated_doc.split("\n")
                updated_doc = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()

        truncated = (stop_reason == "max_tokens")
        if truncated:
            return jsonify({
                "ok": False,
                "error": "AI 응답이 너무 길어 잘렸습니다. 분류표가 매우 큰 경우 발생할 수 있어요. 수동으로 미니 채팅에서 통합 요청해 주세요.",
            }), 500

        push_log(sess, f"[분류표 정리] 자동 통합 완료 — {len(predictions)}개 패턴 처리")
        return jsonify({
            "ok": True,
            "updated_doc": updated_doc,
            "reply": reply_text,
            "predictions_resolved": len(predictions),
        })

    except Exception as e:
        return jsonify({"ok": False, "error": f"분류표 정리 실패: {e}"}), 500


@app.route("/merge-tcs/<sid>", methods=["POST"])
def merge_tcs(sid):
    """Stage 2 — TC 자동 통합 + Excel 재빌드 (Step 5).

    1. tc_final.md 로드
    2. AI 호출 — duplicate_report 의 통합 후보 TC 제거 + 대표 TC 비고에 [통합] 태그
    3. tc_final.md 새 버전 저장 (원본 보존)
    4. step_build_excel() 다시 호출 → 새 Excel 생성 (_merged suffix)
    5. 응답: { ok, filename, removed_count, new_total_tc }
    """
    import anthropic
    sess = SESSIONS.get(sid)
    if not sess:
        return jsonify({
            "ok": False,
            "error": "세션이 만료되었습니다. 페이지를 새로고침하세요."
        }), 404

    data = request.get_json(force=True) or {}
    duplicate_report = data.get("duplicate_report") or {}
    patterns = duplicate_report.get("patterns") or []
    if not patterns:
        return jsonify({"ok": False, "error": "통합할 중복 패턴이 없습니다."}), 400

    # tc_final.md 로드
    tc_final_path = sess.get("workspace", Path()) / "tc_final.md"
    if not tc_final_path.exists():
        return jsonify({"ok": False, "error": f"TC 파일을 찾을 수 없습니다: {tc_final_path}"}), 404
    tc_md = tc_final_path.read_text(encoding="utf-8")

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return jsonify({"ok": False, "error": "ANTHROPIC_API_KEY 미설정"}), 500
    client = anthropic.Anthropic(api_key=api_key)

    # 통합 지시 텍스트 생성
    merge_instructions = []
    total_to_remove = 0
    for p in patterns:
        keep = p.get("keep", "")
        remove = p.get("remove") or []
        pattern_name = p.get("pattern", "")
        major = p.get("major", "")
        if keep and remove:
            merge_instructions.append(
                f'- [{major}] "{pattern_name}" 패턴: '
                f'유지 = `{keep}`, 제거 = {", ".join(f"`{r}`" for r in remove)}'
            )
            total_to_remove += len(remove)
    if not merge_instructions:
        return jsonify({"ok": False, "error": "통합할 TC 가 없습니다."}), 400

    instructions_text = "\n".join(merge_instructions)

    system_prompt = """당신은 TC 통합 전문가입니다. 기존 TC 마크다운에서 중복 패턴을 통합 정리합니다.

## 절대 규칙

1. **통합 후보 TC 들을 마크다운에서 완전히 제거** (`### TC-ID — title` 부터 다음 `### ` 또는 `---` 직전까지).
2. **유지 권장 TC 의 비고에 [통합] 태그 추가** — 예: `**비고**\\n- [통합] 그룹 단위 비기능 검증 — 같은 패턴을 다른 화면별로 반복 작성하지 않음 (원칙 G)`
3. **다른 모든 TC 는 그대로 유지** — 명시되지 않은 TC 는 절대 변경 금지.
4. **마크다운 형식 보존** — `### TC-ID`, `| 분류 |`, `**테스트 단계**` 등 모든 형식 유지.
5. **응답은 통합된 마크다운 전체** — 메타 헤더(`# TC 최종본 — ...`) 도 포함하여 그대로 반환.

응답 형식:
[REPLY] 1-2문장 요약
[DOCUMENT] 통합된 전체 마크다운
"""

    user_msg = f"""## 통합 지시
{instructions_text}

## 현재 TC 마크다운 (전체 보존, 위 지시만 적용)
```
{tc_md[:18000]}
```

위 통합 지시를 정확히 적용하여 **수정된 전체 TC 마크다운**을 반환하세요."""

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=16384,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_msg}],
        )
        ai_text = resp.content[0].text
        stop_reason = getattr(resp, "stop_reason", None)

        doc_match = re.search(r'\[DOCUMENT\](.*?)$', ai_text, re.DOTALL)
        reply_match = re.search(r'\[REPLY\](.*?)(?=\[DOCUMENT\]|$)', ai_text, re.DOTALL)
        if not doc_match:
            return jsonify({"ok": False, "error": "AI 응답 파싱 실패 — DOCUMENT 태그 누락"}), 500

        new_tc_md = doc_match.group(1).strip()
        if new_tc_md.startswith("```"):
            lines = new_tc_md.split("\n")
            new_tc_md = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()

        if stop_reason == "max_tokens":
            return jsonify({"ok": False, "error": "AI 응답이 잘렸습니다. TC 가 많은 경우 발생 — 수동 정리 필요"}), 500

        # 새 tc_final.md 저장 (원본은 그대로 둠 — 백업용으로 _v1 보존)
        merged_path = sess["workspace"] / "tc_final_merged.md"
        merged_path.write_text(new_tc_md, encoding="utf-8")

        # TC 개수 재계산
        new_tc_count = len(re.findall(r"^###\s", new_tc_md, re.MULTILINE))
        old_tc_count = len(re.findall(r"^###\s", tc_md, re.MULTILINE))
        actual_removed = max(0, old_tc_count - new_tc_count)
        new_smoke = max(1, round(new_tc_count * 0.35))

        # Excel 재빌드 — 임시로 tc_final.md 를 새 내용으로 교체했다가 빌드 후 복원
        original_tc_md = tc_md
        try:
            tc_final_path.write_text(new_tc_md, encoding="utf-8")
            # build_excel 호출 시 _merged suffix 가 붙도록 sess 에 마킹
            sess["_excel_filename_suffix"] = "_merged"
            project_name = sess.get("project_name", "프로젝트")
            new_excel_path = step_build_excel(sess, new_tc_md, project_name, new_tc_count, new_smoke)
        finally:
            # 원본 tc_final.md 복원 (재시도 등을 위해)
            tc_final_path.write_text(original_tc_md, encoding="utf-8")
            sess.pop("_excel_filename_suffix", None)

        # sess["result"] 갱신 (병합본을 새 결과로)
        sess["result"] = new_excel_path

        push_log(sess, f"[TC 통합] 자동 통합 완료 — {actual_removed}개 TC 제거 (총 {old_tc_count} → {new_tc_count}). 새 Excel: {new_excel_path.name}")

        reply_text = reply_match.group(1).strip() if reply_match else f"{actual_removed}개 TC 통합 완료"

        return jsonify({
            "ok": True,
            "filename": new_excel_path.name,
            "removed_count": actual_removed,
            "new_total_tc": new_tc_count,
            "new_smoke_tc": new_smoke,
            "reply": reply_text,
            "size": new_excel_path.stat().st_size if new_excel_path.exists() else 0,
        })

    except Exception as e:
        import traceback
        push_log(sess, f"[TC 통합] 실패: {e}")
        push_log(sess, traceback.format_exc()[:500])
        return jsonify({"ok": False, "error": f"TC 통합 실패: {e}"}), 500


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

    headers = ["대분류 코드", "대분류명", "TC 생성 포함 (Y/N)", "비고"]
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

    SCOPES = [
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
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


@app.route("/drive/status")
def drive_status():
    """Drive 인증 상태 + 현재 계정 이메일 확인"""
    try:
        service = get_drive_service()
        about = service.about().get(fields="user(emailAddress,displayName)").execute()
        user = about.get("user", {})
        return jsonify({
            "ok": True,
            "authenticated": True,
            "email": user.get("emailAddress", ""),
            "name": user.get("displayName", ""),
        })
    except FileNotFoundError as e:
        return jsonify({"ok": False, "authenticated": False, "error": str(e), "need_credentials": True})
    except Exception as e:
        return jsonify({"ok": False, "authenticated": False, "error": str(e)})


@app.route("/drive/folders")
def drive_folders():
    """Drive 폴더 목록 조회 (검색어 지원)"""
    q = (request.args.get("q") or "").strip()
    try:
        service = get_drive_service()
        query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
        if q:
            # 이름에 검색어 포함된 폴더
            query += f" and name contains '{q}'"
        result = service.files().list(
            q=query,
            fields="files(id,name,parents,modifiedTime)",
            orderBy="modifiedTime desc",
            pageSize=50
        ).execute()
        return jsonify({"ok": True, "folders": result.get("files", [])})
    except FileNotFoundError as e:
        return jsonify({"ok": False, "error": str(e), "need_credentials": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/upload-to-drive", methods=["POST"])
def upload_to_drive():
    data = request.get_json() or {}
    filename = data.get("filename", "")
    sid = data.get("sid", "")
    folder_id = data.get("folder_id", "")  # 사용자가 선택한 폴더 (우선)

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

    # 폴더 ID: 요청 파라미터 > config 기본값
    if not folder_id:
        config = load_config()
        folder_id = config.get("google_drive", {}).get("upload_folder_id")
    if not folder_id:
        return jsonify({"ok": False, "error": "업로드할 폴더를 선택해주세요.", "need_folder": True})

    try:
        from googleapiclient.http import MediaFileUpload
        service = get_drive_service()
        file_metadata = {"name": filename, "parents": [folder_id]}
        media = MediaFileUpload(
            str(file_path),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        uploaded = service.files().create(
            body=file_metadata, media_body=media, fields="id,webViewLink,parents"
        ).execute()
        # 업로드된 폴더 URL 구성
        parent_id = uploaded.get("parents", [folder_id])[0]
        folder_url = f"https://drive.google.com/drive/folders/{parent_id}"
        return jsonify({
            "ok": True,
            "file_id": uploaded.get("id"),
            "link": folder_url,
            "file_link": uploaded.get("webViewLink"),
        })
    except FileNotFoundError as e:
        return jsonify({"ok": False, "error": str(e), "need_credentials": True})
    except Exception as e:
        err_str = str(e)
        if any(k in err_str for k in ["insufficient_scope", "accessNotConfigured",
                                       "forbidden", "403", "Request had insufficient"]):
            return jsonify({"ok": False, "error": "Google Drive 접근 권한이 없습니다.", "need_credentials": True})
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
  /* 헤더 우측 서버 재시작 버튼 */
  .btn-restart-server {
    padding: 6px 12px; border-radius: 6px;
    background: rgba(255,255,255,0.10); color: #FFFFFF;
    border: 1px solid rgba(255,255,255,0.30);
    font-size: 12px; font-weight: 600; cursor: pointer;
    transition: all 0.15s; white-space: nowrap;
    display: inline-flex; align-items: center; gap: 5px;
  }
  .btn-restart-server:hover {
    background: rgba(239, 68, 68, 0.85); border-color: #EF4444;
  }
  .btn-restart-server:disabled { opacity: 0.5; cursor: not-allowed; }
  /* 재시작 진행 오버레이 */
  .restart-overlay {
    position: fixed; inset: 0; z-index: 10000;
    background: rgba(15, 23, 42, 0.85); color: #FFFFFF;
    display: none; align-items: center; justify-content: center;
    flex-direction: column; gap: 16px; text-align: center; padding: 24px;
  }
  .restart-overlay.visible { display: flex; }
  .restart-overlay-spinner {
    width: 56px; height: 56px; border: 4px solid rgba(255,255,255,0.25);
    border-top-color: #FFFFFF; border-radius: 50%;
    animation: restartSpin 0.9s linear infinite;
  }
  @keyframes restartSpin { to { transform: rotate(360deg); } }
  .restart-overlay-title { font-size: 20px; font-weight: 700; letter-spacing: -0.3px; }
  .restart-overlay-msg { font-size: 14px; opacity: 0.85; max-width: 480px; line-height: 1.6; }
  .restart-overlay-status { font-size: 12px; opacity: 0.7; font-family: monospace; }

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
  .btn-clear-sources {
    padding: 7px 14px; border-radius: 8px; font-size: 12px; font-weight: 600;
    background: #FEF2F2; color: #B91C1C; border: 1.5px solid #FCA5A5;
    cursor: pointer; transition: all 0.15s; margin-left: auto;
  }
  .btn-clear-sources:hover { background: #FEE2E2; border-color: #EF4444; color: #991B1B; }
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

  /* 서브스텝 아이콘 — 3가지 명확한 상태: 대기(회색) · 진행 중(파랑 테두리) · 완료(초록 + ✓) */
  .substeps { display: flex; gap: 8px; margin: 14px 0; flex-wrap: wrap; }
  .substep {
    display: flex; align-items: center; gap: 6px;
    padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
    background: #F3F4F6; color: #9CA3AF; border: 1.5px solid #E5E7EB;
    transition: all 0.25s;
  }
  .substep.active {
    background: #DBEAFE; color: #1E40AF; border-color: #3B82F6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    animation: pulse-active 1.6s ease-in-out infinite;
  }
  .substep.done {
    background: #D1FAE5; color: #065F46; border-color: #10B981;
  }
  .substep.done::after {
    content: ' ✓'; margin-left: 2px; font-weight: 800;
  }
  @keyframes pulse-active {
    0%, 100% { box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2); }
    50%      { box-shadow: 0 0 0 5px rgba(59, 130, 246, 0.35); }
  }

  /* (제거됨) .domain-chip — 대분류 체크리스트 UI 삭제로 미사용 */

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
    flex-direction: column; gap: 10px; min-height: 140px; max-height: 280px;
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
  /* ── Sticky Mini AI 채팅 패널 (Step 3 분류 검토 전용) ── */
  /* 3가지 상태: collapsed(입력만, 약 60px) / expanded(메시지+입력, ~280px) / modal(전체화면) */
  .floating-ai-bar {
    position: fixed; left: 0; right: 0; bottom: 0;
    z-index: 9000;
    background: linear-gradient(135deg, rgba(30, 58, 95, 0.97) 0%, rgba(45, 91, 110, 0.97) 100%);
    backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
    border-top: 3px solid #14B8A6;
    box-shadow: 0 -8px 24px rgba(0, 0, 0, 0.18);
    color: #FFFFFF;
    display: none;
    transform: translateY(100%);
    transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1);
  }
  .floating-ai-bar.visible {
    display: flex; flex-direction: column;
    transform: translateY(0);
    animation: floatingAiPulse 1.4s ease-out 0.32s 1;
  }
  @keyframes floatingAiPulse {
    0%, 100% { box-shadow: 0 -8px 24px rgba(0,0,0,0.18); }
    50% { box-shadow: 0 -8px 24px rgba(0,0,0,0.18), 0 0 0 4px rgba(20, 184, 166, 0.55); }
  }
  /* 안전망: card3 hidden / stepBar3 비활성 시 절대 숨김 */
  body:has(#card3.hidden) .floating-ai-bar { display: none !important; }
  body:has(#stepBar3:not(.active)) .floating-ai-bar { display: none !important; }

  /* 헤더 — 라벨 + 메시지 개수 + 컨트롤 버튼 */
  .floating-ai-header {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 20px; border-bottom: 1px solid rgba(255,255,255,0.12);
    background: rgba(0,0,0,0.10);
    cursor: pointer; user-select: none;
  }
  .floating-ai-bar.collapsed .floating-ai-header { border-bottom: none; }
  .floating-ai-header-label {
    flex: 1; font-size: 13px; font-weight: 700; color: #FFFFFF;
    display: flex; align-items: center; gap: 8px; white-space: nowrap;
  }
  .floating-ai-header-label small {
    font-weight: 400; opacity: 0.7; font-size: 11px;
  }
  .floating-ai-msg-badge {
    font-size: 10px; font-weight: 700;
    padding: 2px 8px; border-radius: 999px;
    background: rgba(20, 184, 166, 0.32); color: #A7F3D0;
  }
  .floating-ai-ctrl {
    background: rgba(255,255,255,0.10);
    color: #FFFFFF; border: 1px solid rgba(255,255,255,0.22);
    border-radius: 6px;
    padding: 4px 10px; font-size: 11px; font-weight: 600;
    cursor: pointer; white-space: nowrap;
    transition: background 0.15s ease;
  }
  .floating-ai-ctrl:hover { background: rgba(255,255,255,0.20); }

  /* 메시지 영역 (collapsed 상태에서 숨김) */
  .floating-ai-messages {
    overflow-y: auto; padding: 12px 20px;
    display: flex; flex-direction: column; gap: 8px;
    max-height: 220px; min-height: 80px;
    background: rgba(255,255,255,0.04);
    transition: max-height 0.25s ease, padding 0.25s ease, opacity 0.2s ease;
  }
  .floating-ai-bar.collapsed .floating-ai-messages {
    max-height: 0; min-height: 0; padding: 0 20px;
    opacity: 0; pointer-events: none; overflow: hidden;
  }
  .floating-ai-msg {
    max-width: 88%; padding: 8px 12px; border-radius: 10px;
    font-size: 12.5px; line-height: 1.55;
    word-wrap: break-word; word-break: break-word;
  }
  .floating-ai-msg.assistant {
    align-self: flex-start;
    background: rgba(255,255,255,0.94); color: #1E3A5F;
    border-bottom-left-radius: 3px;
  }
  .floating-ai-msg.user {
    align-self: flex-end;
    background: linear-gradient(135deg, #14B8A6 0%, #0D9488 100%);
    color: #FFFFFF;
    border-bottom-right-radius: 3px;
  }
  .floating-ai-msg.system {
    align-self: center;
    background: rgba(34, 197, 94, 0.18); color: #BBF7D0;
    font-size: 11px;
    border: 1px solid rgba(34, 197, 94, 0.32);
    border-radius: 8px; max-width: 96%;
  }
  .floating-ai-empty {
    align-self: center; color: rgba(255,255,255,0.55);
    font-size: 11.5px; padding: 14px 0;
  }

  /* 입력 영역 */
  .floating-ai-inner {
    max-width: 1100px; margin: 0 auto; width: 100%;
    display: flex; align-items: flex-end; gap: 10px;
    padding: 10px 20px 12px 20px;
  }
  .floating-ai-input {
    flex: 1; border: 1.5px solid rgba(255, 255, 255, 0.25); border-radius: 10px;
    background: rgba(255, 255, 255, 0.96);
    padding: 10px 14px; font-size: 13px; outline: none;
    font-family: inherit; min-height: 38px; max-height: 100px;
    line-height: 1.5; color: var(--text); resize: none;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
    transition: box-shadow 0.18s ease, border-color 0.18s ease;
  }
  .floating-ai-input:focus {
    border-color: #14B8A6;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12), 0 0 0 3px rgba(20, 184, 166, 0.32);
  }
  .floating-ai-send {
    padding: 9px 20px;
    background: linear-gradient(135deg, #14B8A6 0%, #0D9488 100%);
    color: #fff; border: none; border-radius: 10px;
    font-size: 13px; font-weight: 700;
    cursor: pointer; white-space: nowrap;
    box-shadow: 0 2px 8px rgba(20, 184, 166, 0.42);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
  }
  .floating-ai-send:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(20, 184, 166, 0.55);
  }
  .floating-ai-send:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

  /* body padding — collapsed 56px / expanded 약 340px (헤더+메시지+입력) */
  body.has-floating-ai { padding-bottom: 340px; }
  body.has-floating-ai.has-floating-ai-collapsed { padding-bottom: 64px; }

  /* 좁은 화면 */
  @media (max-width: 640px) {
    .floating-ai-header { padding: 8px 14px; }
    .floating-ai-messages { padding: 10px 14px; max-height: 180px; }
    .floating-ai-inner { padding: 8px 14px 10px 14px; gap: 8px; }
    .floating-ai-send { padding: 8px 14px; }
    body.has-floating-ai { padding-bottom: 300px; }
  }

  /* ── Mini Chat 확대 모달 (full-size view) ── */
  .floating-ai-modal {
    position: fixed; inset: 0; z-index: 10000;
    background: rgba(15, 23, 42, 0.72);
    display: none; align-items: center; justify-content: center;
    padding: 20px;
  }
  .floating-ai-modal.open { display: flex; }
  .floating-ai-modal-box {
    background: #FFFFFF; color: var(--text);
    border-radius: 14px;
    width: 100%; max-width: 720px; height: 78vh;
    min-width: 360px; min-height: 320px;
    max-height: 96vh;
    display: flex; flex-direction: column;
    overflow: hidden; position: relative;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    resize: both;  /* native 리사이즈 — 우측 하단 모서리 드래그 */
  }
  /* native resize 핸들 시각 강화 (브라우저 기본 핸들이 작아서 보이게) */
  .floating-ai-modal-resize {
    position: absolute; bottom: 0; right: 0;
    width: 18px; height: 18px;
    background:
      linear-gradient(135deg, transparent 50%, var(--muted) 50%, var(--muted) 60%, transparent 60%, transparent 70%, var(--muted) 70%, var(--muted) 80%, transparent 80%);
    pointer-events: none;  /* native resize 가 잡음 */
    border-bottom-right-radius: 14px;
    opacity: 0.5;
  }
  .floating-ai-modal-header {
    padding: 14px 20px; background: var(--navy); color: #FFFFFF;
    display: flex; align-items: center; gap: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.10);
  }
  .floating-ai-modal-title {
    flex: 1; font-size: 15px; font-weight: 700;
  }
  .floating-ai-modal-close {
    background: rgba(255,255,255,0.12); color: #FFFFFF;
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 6px; padding: 5px 12px;
    font-size: 12px; cursor: pointer;
  }
  .floating-ai-modal-close:hover { background: rgba(255,255,255,0.22); }
  .floating-ai-modal-messages {
    flex: 1; overflow-y: auto; padding: 18px 22px;
    display: flex; flex-direction: column; gap: 10px;
    background: #F8FAFC;
  }
  .floating-ai-modal-input-row {
    display: flex; gap: 10px; padding: 14px 20px;
    border-top: 1px solid var(--border); background: #FFFFFF;
  }
  /* details/summary 기본 마커 제거 (Safari/WebKit 포함) */
  #tcSummaryDetails > summary::-webkit-details-marker { display: none; }
  #tcSummaryDetails > summary { list-style: none; }
  #tcSummaryDetails > summary:hover { background: rgba(59, 130, 246, 0.06); border-radius: 10px; }
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

  /* TC 분류 요약 표 — 옵션 E (메인 행 + 종속 행) */
  .tc-summary-table .tc-summary-row-main:hover { background: #EFF6FF !important; }
  .tc-summary-table .tc-summary-row-main td:last-child:hover { background: #DBEAFE; }
  .tc-summary-table .tc-summary-row-nested { transition: opacity 0.15s ease; }
  .tc-summary-table .tc-summary-row-nested td { border-top: 0 !important; }

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

  /* Drive 폴더 선택 리스트 */
  .drive-folder-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-bottom: 1px solid #E2E8F0;
    cursor: pointer; transition: background 0.1s;
    font-size: 13px;
  }
  .drive-folder-item:hover { background: #EBF2FF; }
  .drive-folder-item.selected { background: #DBEAFE; border-left: 3px solid #2563EB; }
  .drive-folder-item:last-child { border-bottom: none; }

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
    <span class="version-badge" style="cursor:pointer;" onclick="showWhatsNew()" title="{{ app_version }} 릴리즈 노트 보기">{{ app_version }}</span>
  </div>
  <span class="header-sub">Claude AI · PDF / URL / 텍스트 → Excel</span>
  <button type="button" class="btn-restart-server" id="btnRestartServer" onclick="restartServer()" title="코드 변경 반영을 위해 서버를 재시작합니다 (로컬에서만)">
    🔄 서버 재시작
  </button>
</header>

<!-- 서버 재시작 진행 오버레이 -->
<div id="restartOverlay" class="restart-overlay">
  <div class="restart-overlay-spinner"></div>
  <div class="restart-overlay-title">서버 재시작 중...</div>
  <div class="restart-overlay-msg">
    잠시만 기다려주세요. 서버가 다시 살아나면 자동으로 새로고침됩니다.<br>
    <span style="font-size:12px;opacity:0.8;">5~10초가 지나도 새로고침되지 않으면 직접 페이지를 새로고침해 주세요.</span>
  </div>
  <div class="restart-overlay-status" id="restartOverlayStatus">서버 응답 대기 중...</div>
</div>

<!-- What's new 배너 ({{ app_version }} 첫 방문 시 자동 표시, localStorage로 dismiss 기억) -->
<div id="whatsNewBanner" style="display:none; margin:12px 0; padding:12px 16px; background:linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%); border:1px solid #93C5FD; border-radius:10px;">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
    <div style="flex:1; font-size:13px; color:#1E40AF;">
      🎨 <strong>{{ app_version }} — {{ app_version_tagline }}</strong>
      <div style="margin-top:6px; font-size:12px; color:#374151; line-height:1.6;">
        {% for line in app_version_highlights %}• {{ line | safe }}<br>{% endfor %}
      </div>
    </div>
    <div style="display:flex; flex-direction:column; gap:6px;">
      <button onclick="showWhatsNew()" style="padding:4px 10px; font-size:11px; background:#2563EB; color:#FFFFFF; border:none; border-radius:6px; cursor:pointer; white-space:nowrap;">📖 자세히 보기</button>
      <button onclick="dismissWhatsNew()" style="padding:4px 10px; font-size:11px; background:#FFFFFF; color:#6B7280; border:1px solid #D1D5DB; border-radius:6px; cursor:pointer; white-space:nowrap;">✕ 닫기</button>
    </div>
  </div>
</div>

<!-- What's new 상세 모달 -->
<div id="whatsNewModal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); z-index:1000; align-items:center; justify-content:center;">
  <div style="background:#FFFFFF; border-radius:12px; max-width:720px; width:92%; max-height:84vh; overflow:hidden; display:flex; flex-direction:column;">
    <div style="padding:16px 20px; border-bottom:1px solid #E5E7EB; display:flex; justify-content:space-between; align-items:center;">
      <div><strong style="font-size:15px; color:#1E40AF;">📖 {{ app_version }} 릴리즈 노트</strong></div>
      <button onclick="document.getElementById('whatsNewModal').style.display='none'" style="border:none; background:none; font-size:20px; cursor:pointer; color:#6B7280;">✕</button>
    </div>
    <div style="padding:16px 20px; overflow:auto; font-size:13px; line-height:1.7; color:#374151;">
      <h3 style="margin:0 0 8px; color:#1E40AF;">🎨 {{ app_version }} — {{ app_version_date }} ({{ app_version_tagline }})</h3>
      <h4 style="color:#065F46; margin-top:16px;">✨ 이번 변경 요약</h4>
      <ul>
        {% for line in app_version_highlights %}<li>{{ line | safe }}</li>{% endfor %}
      </ul>
      <h4 style="color:#6B7280; margin-top:16px;">💡 전체 변경 이력</h4>
      <ul>
        <li>버전별 상세 내역은 프로젝트 루트의 <code>CHANGELOG.md</code> 참고</li>
        <li>이전 버전 기능 모두 유지 — 실행 방법 변경 없음</li>
      </ul>
    </div>
    <div style="padding:12px 20px; border-top:1px solid #E5E7EB; text-align:right;">
      <button onclick="document.getElementById('whatsNewModal').style.display='none'" style="padding:6px 16px; background:#2563EB; color:#FFFFFF; border:none; border-radius:6px; cursor:pointer;">확인</button>
    </div>
  </div>
</div>

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
        onkeydown="if(event.isComposing||event.keyCode===229)return;if(event.key==='Enter')createDashProject();">
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
               placeholder="예: Supercycl 모바일" value=""
               oninput="onProjectNameInputForResume()">
      </div>

      <!-- ═════════════════════════════════════════════════════════
           입력 소스 — 우선순위 재배치 (v0.10.x)
           1) 구조화 spec 폴더 = 기본 펼침 (권장 / 기획팀 표준)
           2) 개별 소스 = 기본 접힘 (임시 작업용)
           ═════════════════════════════════════════════════════════ -->

      <!-- ① 구조화 spec 폴더 (권장) ────────────────────────────── -->
      <div class="form-group">
        <div id="specFolderSection" style="border:1.5px solid #3B82F6;border-radius:10px;background:linear-gradient(135deg,#EFF6FF 0%,#DBEAFE 100%);overflow:hidden;">
          <button type="button" id="specFolderHeader" onclick="toggleAccordion('spec')"
                  style="width:100%;padding:14px 16px;background:transparent;border:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;text-align:left;">
            <span style="display:flex;align-items:center;gap:10px;">
              <span style="font-size:16px;">📁</span>
              <span style="font-weight:700;font-size:14px;color:#1E3A5F;">구조화 spec 폴더</span>
              <span style="font-size:11px;background:#3B82F6;color:#FFF;padding:2px 8px;border-radius:10px;font-weight:600;">권장</span>
              <span style="font-size:11.5px;color:#475569;font-weight:400;">기획팀 표준 — overview/policy/design/scr 분리</span>
            </span>
            <span id="specFolderChevron" style="font-size:12px;color:#3B82F6;font-weight:700;">▼</span>
          </button>
          <div id="specFolderBody" style="padding:0 16px 16px 16px;">

            <!-- 신규 spec 폴더 경로 + 최근 사용 드롭다운 -->
            <label style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px;">
              <span style="font-size:12px;color:#1E3A5F;font-weight:600;">신규 spec 폴더 경로 <span style="color:#DC2626;">*</span></span>
              <button type="button" id="btnRecentFolders" onclick="toggleRecentFolders()"
                      style="font-size:11px;color:#3B82F6;background:#FFFFFF;border:1px solid #93C5FD;border-radius:4px;padding:3px 9px;cursor:pointer;">
                최근 사용 ▾
              </button>
            </label>
            <input type="text" id="specFolderPath" class="form-input"
                   style="font-size:13px;font-family:monospace;background:#FFFFFF;"
                   placeholder="예: /Users/me/projects/specs/v0.47.2-2026-05-07"
                   oninput="onSpecFolderChanged()"/>
            <!-- 최근 사용 폴더 드롭다운 (프로젝트별) -->
            <div id="recentFoldersPanel" style="display:none;margin-top:4px;background:#FFFFFF;border:1px solid #93C5FD;border-radius:6px;max-height:200px;overflow-y:auto;font-size:12px;"></div>

            <!-- 버전 diff 모드 -->
            <div style="margin-top:10px;padding:10px 12px;background:#FFFBEB;border:1px solid #FCD34D;border-radius:6px;">
              <div style="display:flex;align-items:center;justify-content:space-between;">
                <label style="font-size:12px;color:#78350F;font-weight:600;display:flex;align-items:center;gap:5px;">
                  <span>🔄</span> 버전 diff 모드
                  <span style="font-weight:400;color:#92400E;">— 변경된 SCR 만 재생성</span>
                </label>
                <button type="button" id="btnDiffToggle" onclick="toggleDiffMode()"
                        style="padding:3px 10px;font-size:11px;border:1px solid #FCD34D;background:#FFFFFF;border-radius:4px;cursor:pointer;color:#78350F;">사용</button>
              </div>
              <div id="diffBox" style="display:none;margin-top:8px;">
                <label style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
                  <span style="font-size:11px;color:#78350F;font-weight:600;">이전 버전 폴더 경로</span>
                  <button type="button" id="btnRecentPrevFolders" onclick="toggleRecentPrevFolders()"
                          style="font-size:10px;color:#78350F;background:#FFFFFF;border:1px solid #FCD34D;border-radius:4px;padding:2px 7px;cursor:pointer;">
                    최근 사용 ▾
                  </button>
                </label>
                <input type="text" id="prevSpecFolderPath" class="form-input"
                       style="font-size:12px;font-family:monospace;background:#FFFFFF;"
                       placeholder="비교할 이전 버전 폴더 경로"
                       oninput="onSpecFolderChanged()"/>
                <div id="recentPrevFoldersPanel" style="display:none;margin-top:4px;background:#FFFFFF;border:1px solid #FCD34D;border-radius:6px;max-height:160px;overflow-y:auto;font-size:11px;"></div>
                <div style="margin-top:8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                  <button type="button" onclick="previewDiff()" style="padding:5px 11px;font-size:11px;background:#F59E0B;color:#FFF;border:none;border-radius:5px;cursor:pointer;font-weight:500;">📊 변경 화면 미리보기</button>
                  <label style="font-size:11px;color:#78350F;display:flex;align-items:center;gap:5px;cursor:pointer;">
                    <input type="checkbox" id="includeUnchanged" style="margin:0;"/>
                    동일 화면도 재생성
                  </label>
                </div>
                <div id="diffPreview" style="display:none;margin-top:6px;padding:8px 10px;background:#FFFFFF;border:1px solid #FCD34D;border-radius:5px;font-size:11px;"></div>
              </div>
            </div>

            <!-- 액션 -->
            <div style="display:flex;gap:6px;margin-top:12px;flex-wrap:wrap;align-items:center;">
              <button type="button" onclick="previewSpecFolder()"
                      style="padding:7px 14px;font-size:12.5px;background:#3B82F6;color:#FFF;border:none;border-radius:6px;cursor:pointer;font-weight:600;">
                🔍 미리보기
              </button>
              <button type="button" id="btnResumeSpec" onclick="resumeSpecFolder()"
                      style="display:none;padding:7px 14px;font-size:12.5px;background:#7C3AED;color:#FFF;border:none;border-radius:6px;cursor:pointer;font-weight:600;">
                ▶ 이어서 작업
              </button>
              <span id="specFolderHint" style="font-size:11px;color:#475569;align-self:center;">폴더 경로 입력 후 미리보기로 분류 결과를 확인하세요.</span>
            </div>
            <div id="specFolderPreview" style="display:none;margin-top:10px;padding:10px 12px;background:#FFFFFF;border:1px solid #DBEAFE;border-radius:6px;font-size:12px;"></div>
          </div>
        </div>
      </div>

      <!-- ② 개별 소스 (임시 작업용 — 기본 접힘) ──────────────────── -->
      <div class="form-group">
        <div id="legacySourceSection" style="border:1px solid #CBD5E1;border-radius:10px;background:#F8FAFC;overflow:hidden;">
          <button type="button" id="legacySourceHeader" onclick="toggleAccordion('legacy')"
                  style="width:100%;padding:12px 16px;background:transparent;border:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;text-align:left;">
            <span style="display:flex;align-items:center;gap:10px;">
              <span style="font-size:14px;">📝</span>
              <span style="font-weight:600;font-size:13px;color:#475569;">개별 소스 입력</span>
              <span style="font-size:10.5px;background:#CBD5E1;color:#1F2937;padding:2px 7px;border-radius:8px;font-weight:500;">임시 작업용</span>
              <span style="font-size:11.5px;color:#94A3B8;font-weight:400;">PDF · GitHub URL · 웹페이지 · 마크다운 · 텍스트</span>
            </span>
            <span id="legacySourceChevron" style="font-size:12px;color:#94A3B8;font-weight:700;">▶</span>
          </button>
          <div id="legacySourceBody" style="display:none;padding:0 16px 14px 16px;">
            <div class="source-add-bar" style="margin-bottom:10px;">
              <button type="button" class="btn-add-source" onclick="addSource('pdf')">📄 PDF 추가</button>
              <button type="button" class="btn-add-source" onclick="addSource('url')">🔗 GitHub URL 추가</button>
              <button type="button" class="btn-add-source" onclick="addSource('web')">🌐 웹 URL 추가</button>
              <button type="button" class="btn-add-source" onclick="addSource('md')">📝 마크다운 파일 추가</button>
              <button type="button" class="btn-add-source" onclick="addSource('text')">✏️ 텍스트 추가</button>
              <button type="button" class="btn-clear-sources" id="btnClearAllSources" onclick="clearAllSources()" style="display:none;">🗑 전체 삭제</button>
            </div>
            <div id="sourceList"></div>
            <div id="sourceEmpty" class="source-empty">
              소스를 추가하세요.<br>
              <span style="font-size:12px">PDF · GitHub URL · 웹페이지 · 마크다운 파일 · 텍스트 등을 자유롭게 조합할 수 있습니다.</span>
            </div>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label" style="display:flex;align-items:center;justify-content:space-between">
          <span>TC 생성 범위</span>
          <span style="font-size:11px;color:var(--muted);font-weight:400">선택 — 비우면 전체 TC 생성</span>
        </label>
        <textarea id="focusArea" class="form-input" rows="5"
          style="resize:vertical; min-height:110px; font-size:13px; line-height:1.5;"
          oninput="onInputsChanged()"
          placeholder="특정 기능에 대해서만 TC를 만들려면 여기에 입력하세요.&#10;예) import 기능 / 로그인 및 회원가입 / 결제 모듈의 환불 처리&#10;💡 구조화 spec 모드 (관대한 인식):&#10;   • SCR-104 또는 SCR-102, SCR-104, SCR-106 (개별)&#10;   • SCR-102, 104, 106, 116 (일괄 — SCR 한 번만 적어도 OK)&#10;   • SCR-102~116 (범위)"></textarea>
        <div style="font-size:11px; color:var(--muted); margin-top:3px;">
          입력하면 해당 기능에 집중하여 TC를 생성합니다. 여러 기능은 쉼표 또는 줄바꿈으로 구분하세요.
        </div>
        <!-- 이전 범위 힌트 배너 (프로젝트 선택 시 동적으로 표시) -->
        <div id="previousFocusHint" style="display:none; margin-top:8px; padding:8px 12px; background:#FFFBEB; border:1px solid #FCD34D; border-radius:6px; font-size:12px; color:#92400E; display:none;">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;">
            <div>
              💡 이전 작업 범위:
              <code id="previousFocusValue" style="background:#FFFFFF;padding:2px 6px;border-radius:3px;border:1px solid #FCD34D;font-family:monospace;margin-left:4px;"></code>
            </div>
            <div style="display:flex;gap:6px;">
              <button type="button" onclick="reusePreviousFocus()" style="padding:4px 10px;background:#F59E0B;color:#FFFFFF;border:none;border-radius:4px;font-size:11px;font-weight:600;cursor:pointer;">↪ 재사용</button>
              <button type="button" onclick="dismissPreviousFocusHint()" style="padding:4px 10px;background:#FFFFFF;color:#92400E;border:1px solid #FCD34D;border-radius:4px;font-size:11px;cursor:pointer;">✕ 무시</button>
            </div>
          </div>
        </div>
      </div>

      <div class="form-group" id="generationModeGroup" style="padding:12px 14px;background:#F8FAFC;border:1px solid #E5E7EB;border-radius:8px;">
        <label class="form-label" style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">
          <span>⚙️ 생성 모드</span>
          <span style="font-size:11px;color:var(--muted);font-weight:400;">선택</span>
        </label>
        <div style="display:flex;flex-direction:column;gap:8px;">
          <label style="display:flex;align-items:flex-start;gap:8px;padding:8px 10px;border:1px solid #D1D5DB;border-radius:6px;background:#FFFFFF;cursor:pointer;" id="modeStdLabel">
            <input type="radio" name="genMode" value="summary" checked onchange="onGenModeChanged()" style="margin-top:3px;">
            <div style="flex:1;">
              <div style="font-size:13px;font-weight:600;color:#111827;">정책 반영 모드 <span style="font-size:11px;color:#6B7280;font-weight:400;">(기본)</span></div>
              <div style="font-size:12px;color:#4B5563;margin-top:2px;">정책·기능·분류 3단계 분석으로 규칙을 체계적으로 반영합니다. 대용량·복잡한 문서에 적합.</div>
            </div>
          </label>
          <label style="display:flex;align-items:flex-start;gap:8px;padding:8px 10px;border:1px solid #D1D5DB;border-radius:6px;background:#FFFFFF;cursor:pointer;" id="modeQuickLabel">
            <input type="radio" name="genMode" value="direct" onchange="onGenModeChanged()" style="margin-top:3px;">
            <div style="flex:1;">
              <div style="font-size:13px;font-weight:600;color:#111827;">Quick 모드 <span style="font-size:11px;color:#6B7280;font-weight:400;">(원문 직접)</span></div>
              <div style="font-size:12px;color:#4B5563;margin-top:2px;">요약 단계 없이 원문을 직접 분류합니다. 누락 최소화 · 200KB 이하 권장.</div>
            </div>
          </label>
        </div>
        <div id="modeSourceHint" style="font-size:11px;color:#6B7280;margin-top:8px;">
          ▸ 소스 크기: <span id="modeSourceSize">-</span> · <span id="modeSourceStatus">소스를 추가하면 권장 모드가 안내됩니다.</span>
        </div>
      </div>

      <button class="btn btn-primary" id="startBtn" onclick="startPipeline()">
        🚀 파이프라인 시작
      </button>
    </div>

    <!-- ── 수정 모드 (기획서 diff 기반 TC 갱신) ── -->
    <div id="panelModify" class="hidden">

      <div class="info-box" style="margin-bottom:12px;background:#EEF2FF;border-color:#C7D2FE;">
        📝 <strong>기획서 변경 기반 TC 갱신</strong><br>
        <span style="font-size:12px;color:#4B5563;">이전 기획서와 새 기획서를 비교해 신규/수정/삭제된 화면을 자동 탐지합니다. 기존 TC는 ID를 유지한 채 업데이트됩니다.</span>
      </div>

      <!-- 프로젝트 선택 (선택) -->
      <div class="form-group">
        <label class="form-label" style="display:flex;align-items:center;justify-content:space-between">
          <span>프로젝트 선택 <span style="font-size:11px;color:var(--muted);font-weight:400">(선택 — 기록용)</span></span>
        </label>
        <select class="project-select" id="modifyProjectSelect">
          <option value="">— 단발성 작업 (프로젝트 없음) —</option>
        </select>
      </div>

      <!-- Slot 1: 이전 기획서 -->
      <div class="form-group">
        <label class="form-label">📄 이전 기획서 <span style="color:#DC2626;">*</span></label>
        <div class="src-dropzone" id="oldSpecDropzone" onclick="document.getElementById('oldSpecInput').click()"
             style="border:2px dashed var(--border); border-radius:8px; padding:16px; text-align:center; cursor:pointer; background:#FAFAFA;">
          📎 .md / .txt 파일 드래그 또는 클릭
        </div>
        <input type="file" id="oldSpecInput" accept=".md,.markdown,.txt" style="display:none" onchange="handleDiffFileUpload(event, 'old')">
        <div id="oldSpecStatus" style="font-size:12px; color:var(--success); margin-top:6px; display:none;"></div>
      </div>

      <!-- Slot 2: 새 기획서 -->
      <div class="form-group">
        <label class="form-label">📄 새 기획서 <span style="color:#DC2626;">*</span></label>
        <div class="src-dropzone" id="newSpecDropzone" onclick="document.getElementById('newSpecInput').click()"
             style="border:2px dashed var(--border); border-radius:8px; padding:16px; text-align:center; cursor:pointer; background:#FAFAFA;">
          📎 .md / .txt 파일 드래그 또는 클릭
        </div>
        <input type="file" id="newSpecInput" accept=".md,.markdown,.txt" style="display:none" onchange="handleDiffFileUpload(event, 'new')">
        <div id="newSpecStatus" style="font-size:12px; color:var(--success); margin-top:6px; display:none;"></div>
      </div>

      <!-- Slot 3: 기존 TC -->
      <div class="form-group">
        <label class="form-label">📑 기존 TC 파일 <span style="font-size:11px;color:var(--muted);font-weight:400">(선택 — 없으면 신규 생성 흐름)</span></label>
        <div class="src-dropzone" id="existingTcDropzone" onclick="document.getElementById('existingTcInput').click()"
             style="border:2px dashed var(--border); border-radius:8px; padding:16px; text-align:center; cursor:pointer; background:#FAFAFA;">
          📎 .xlsx / .md 파일 드래그 또는 클릭
        </div>
        <input type="file" id="existingTcInput" accept=".xlsx,.xls,.md,.markdown" style="display:none" onchange="handleDiffFileUpload(event, 'tc')">
        <div id="existingTcStatus" style="font-size:12px; color:var(--success); margin-top:6px; display:none;"></div>
      </div>

      <button class="btn btn-primary" id="startDiffBtn" onclick="startDiffAnalyze()">
        🔍 변경사항 분석
      </button>

      <!-- 변경사항 리포트 영역 (분석 후 노출) -->
      <div id="diffReportArea" class="hidden" style="margin-top:16px; padding:14px; background:#FFFFFF; border:1px solid #E5E7EB; border-radius:10px;">
        <div style="font-size:14px; font-weight:700; color:#1E3A5F; margin-bottom:10px;">📊 변경사항 분석 결과</div>
        <div id="diffReportSummary" style="font-size:13px; color:#4B5563; margin-bottom:10px;"></div>
        <div id="diffReportSections"></div>
        <div style="display:flex; gap:10px; margin-top:14px;">
          <button class="btn btn-primary" style="flex:1" onclick="approveAndUpdate()">✅ 승인 후 TC 갱신 시작</button>
          <button class="btn" style="flex:0 0 auto" onclick="cancelDiff()">취소</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Step 2~4: 파이프라인 통합 카드 (Gate는 별도 card3에서 사용자 개입) -->
  <div class="card hidden" id="card2">
    <div class="card-title" style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;">
      <span>
        <span id="pipelineCardTitle">⚙️ 파이프라인 실행</span>
        <span class="badge" id="pipelineCardBadge">Step 2</span>
      </span>
      <button type="button" onclick="restartFromScratch()"
              style="padding:6px 12px;font-size:12px;background:#F1F5F9;color:#1F2937;border:1px solid #94A3B8;border-radius:6px;cursor:pointer;font-weight:500;">
        ← 처음으로 (입력 변경)
      </button>
    </div>

    <div class="substeps">
      <div class="substep" id="sub1">📄 파싱</div>
      <div class="substep" id="sub2">🔎 정책·기능</div>
      <div class="substep" id="sub3">🗂 분류</div>
      <div class="substep" id="sub4">🔍 검토</div>
      <div class="substep" id="sub5">✍️ TC 생성</div>
      <div class="substep" id="sub6">📊 Excel</div>
    </div>

    <div style="font-size:14px; font-weight:600; color:var(--blue); margin-bottom:6px;">
      <span id="stageLabel">시작 중...</span><span id="countdownLabel" style="font-weight:400; font-size:12px; color:var(--muted);"></span>
    </div>
    <div class="progress-wrap">
      <div class="progress-bar" id="progressBar" style="width:0%"></div>
    </div>

    <div class="log-box" id="logBox" style="max-height:360px; min-height:320px;"></div>
    <div style="margin-top:12px; text-align:right;">
      <button class="btn-stop" id="stopBtn2" onclick="stopPipeline()">⏹ 파이프라인 중단</button>
    </div>
  </div>

  <!-- Step 3: Human Gate 카드 -->
  <div class="card hidden" id="card3">
    <div class="card-title" id="gateTitle" style="display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;">
      <span>🔍 분류표 검토 <span class="badge">Step 3 · Human Gate</span></span>
      <span style="display:flex;gap:6px;flex-wrap:wrap;">
        <button type="button" onclick="restartFromScratch()"
                style="padding:6px 12px;font-size:12px;background:#F1F5F9;color:#1F2937;border:1px solid #94A3B8;border-radius:6px;cursor:pointer;font-weight:500;">
          ← 처음으로 (입력 변경)
        </button>
      </span>
    </div>
    <div class="info-box" id="gateInfoBox">
      AI가 생성한 분류표입니다. 하단 AI 도우미로 수정을 요청하고, 아래 표에서 결과를 확인한 뒤 승인하세요.
    </div>

    <!-- 입력 소스 화면 식별자 안내 (v0.9.13~) — gate 이벤트 도착 시 채워짐 -->
    <div id="sourceScrNotice" style="display:none;margin:10px 0;padding:10px 14px;border-radius:8px;font-size:12.5px;line-height:1.55;"></div>

    <!-- v0.9.22 Stage 1 — 분류표 단계 중복 가능성 예측 알림 -->
    <div id="classifyDuplicateNotice" style="display:none;margin:10px 0;padding:14px 16px;background:#FFFBEB;border:1.5px solid #FCD34D;border-radius:10px;"></div>

    <!-- TC ID 생성 방식 선택 패널 (독립 영역, 항상 표시) -->
    <div id="tcIdModePanel" style="background:linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);border:2px solid #3B82F6;border-radius:12px;padding:16px 20px;margin:14px 0 18px 0;box-shadow:0 2px 8px rgba(59, 130, 246, 0.15);">
      <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;">
        <div style="flex:1;min-width:300px;">
          <div style="font-size:15px;font-weight:700;color:#1E3A5F;margin-bottom:6px;display:flex;align-items:center;gap:8px;">
            <span style="font-size:18px;">🪪</span>
            <span>TC ID 생성 방식</span>
          </div>
          <div id="tcIdModeDesc" style="font-size:12.5px;color:#1E3A5F;line-height:1.6;">
            체크하면 시스템이 화면별 코드(<code style="background:#FFFFFF;padding:1px 5px;border-radius:3px;border:1px solid #93C5FD;font-family:monospace;">SM-SPL-001</code>, <code style="background:#FFFFFF;padding:1px 5px;border-radius:3px;border:1px solid #93C5FD;font-family:monospace;">SM-LGI-001</code>...)로 자동 매핑합니다.<br>
            해제하면 아래 <strong>TC 분류 요약</strong> 표에서 SuiteCode를 직접 입력할 수 있습니다.
          </div>
        </div>
        <label id="tcIdModeLabel" style="display:inline-flex;align-items:center;gap:10px;background:#FFFFFF;padding:12px 16px;border-radius:10px;border:2px solid #3B82F6;cursor:pointer;user-select:none;font-weight:700;color:#1E3A5F;box-shadow:0 1px 3px rgba(0,0,0,0.08);white-space:nowrap;transition:all 0.2s;">
          <input type="checkbox" id="tcIdModeToggle" checked onchange="setTcIdMode(this.checked)" style="width:20px;height:20px;cursor:pointer;accent-color:#3B82F6;">
          <span style="font-size:13.5px;">System Generated TC IDs</span>
        </label>
      </div>
    </div>

    <!-- AI 채팅 영역 (단독 폭) — v0.9.12: 시각적으로 숨김. 미니 채팅 패널이 UI 담당.
         단, sendGateChat() / addGateChatMsg() 가 #gateChatInput / #gateChatMessages 를
         참조하므로 DOM 자체는 유지 (단일 진실 소스). 미니/모달 채팅이 미러링하여 사용. -->
    <div class="gate-chat-panel" style="display:none;">
      <div class="gate-chat-header">
        💬 AI와 대화하여 수정
      </div>
      <div class="gate-chat-messages" id="gateChatMessages">
        <!-- 메시지가 여기에 추가됨 -->
      </div>
      <div class="gate-chat-input-row">
        <textarea class="gate-chat-input" id="gateChatInput"
          placeholder="수정 요청을 입력하세요. 예) AUTH 대분류 케이스 3번 삭제해줘"
          onkeydown="if((event.isComposing||event.keyCode===229))return;if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();sendGateChat();}"></textarea>
        <button class="gate-chat-send" id="gateChatSend" onclick="sendGateChat()">전송</button>
      </div>
    </div>

    <!-- 분류표 & TC 매핑 표 영역 — 메인 (renderGateViewer가 채워넣음) -->
    <div id="gateViewer">
      <!-- TC 분류 요약 표가 여기에 들어감 -->
    </div>

    <!-- 원본 마크다운 보기 — 토글 가능 (기본 접힘) -->
    <details style="margin:14px 0;">
      <summary style="cursor:pointer; padding:8px 14px; background:#F3F4F6; border:1px solid #D1D5DB; border-radius:8px; font-size:13px; font-weight:600; color:#374151; user-select:none; list-style:none; display:flex; align-items:center; gap:6px;">
        <span id="rawDocToggleIcon">▶</span>
        <span>📄 분류표 원본 마크다운 보기 (펼치기)</span>
      </summary>
      <div id="rawDocContainer" style="margin-top:8px; padding:14px; background:#FAFAFA; border:1px solid #E5E7EB; border-radius:8px;">
        <div id="rawDocBadge" style="font-size:11px; color:var(--muted); margin-bottom:8px;"></div>
        <pre id="rawDocContent" style="margin:0; padding:12px; background:#FFFFFF; border:1px solid #E5E7EB; border-radius:6px; font-size:12px; line-height:1.7; max-height:400px; overflow:auto; white-space:pre-wrap; word-break:break-word; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; color:#111827;"></pre>
      </div>
    </details>
    <script>
      // details 펼치기/접기 시 ▶ ↔ ▼ 화살표 + 라벨 전환
      // (분류표 원본 + TC 분류 요약 모두 처리)
      (function() {
        document.addEventListener('toggle', function(e) {
          if (!e.target || e.target.tagName !== 'DETAILS') return;
          // 1) 원본 마크다운 보기 토글
          var rawIcon = e.target.querySelector('#rawDocToggleIcon');
          if (rawIcon) {
            rawIcon.textContent = e.target.open ? '▼' : '▶';
            var sumText = e.target.querySelector('summary span:last-child');
            if (sumText) sumText.textContent = e.target.open ? '📄 분류표 원본 마크다운 보기 (접기)' : '📄 분류표 원본 마크다운 보기 (펼치기)';
            return;
          }
          // 2) TC 분류 요약 토글 (renderGateViewer 가 동적 생성)
          if (e.target.id === 'tcSummaryDetails') {
            var sIcon = e.target.querySelector('#tcSummaryToggleIcon');
            if (sIcon) sIcon.textContent = e.target.open ? '▼' : '▶';
            var hint = e.target.querySelector('#tcSummaryFoldHint');
            if (hint) hint.textContent = e.target.open ? '(클릭하여 접기)' : '(클릭하여 펼치기)';
          }
        }, true);
      })();
    </script>

    <!-- 숨겨진 원본 데이터 저장용 (gate-chat 등에서 참조) -->
    <textarea class="gate-textarea" id="gateContent" style="display:none;"></textarea>

    <!-- SuiteCode 입력 테이블 (Viewer 밖 — 독립 영역) -->
    <div id="suiteCodeSection" style="display:none; margin-top:14px; margin-bottom:14px;"></div>

    <!-- Excel 출력 옵션 (Full/Light/Custom) — 승인 시 step_build_excel로 전달됨 -->
    <div id="excelOptionPanel" style="margin-top:18px;background:#F0F9FF;border:1.5px solid #93C5FD;border-radius:10px;padding:14px 16px;">
      <div style="font-size:14px;font-weight:700;color:#1E3A5F;margin-bottom:10px;display:flex;align-items:center;gap:8px;">
        <span>⚙</span><span>Excel 출력 옵션</span>
        <span style="font-size:11px;color:#6B7280;font-weight:400;">— 승인 시 적용됩니다</span>
      </div>
      <div style="display:flex;flex-direction:column;gap:6px;">
        <label class="excel-preset-row" style="display:flex;align-items:flex-start;gap:10px;cursor:pointer;padding:8px 10px;border-radius:8px;background:#FFFFFF;border:1.5px solid #DBEAFE;">
          <input type="radio" name="excelPreset" value="full" checked onchange="onExcelPresetChange()" style="margin-top:3px;">
          <div style="flex:1;">
            <div style="font-size:13px;font-weight:700;color:#1E3A5F;">📦 Full Set <span style="font-size:11px;color:#6B7280;font-weight:400;">(정식 산출물)</span></div>
            <div style="font-size:11.5px;color:#4B5563;margin-top:2px;">표지 · 통계 · Smoke · Traceability · 변경 이력 · TC 전체 — 정식 배포·공유용</div>
          </div>
        </label>
        <label class="excel-preset-row" style="display:flex;align-items:flex-start;gap:10px;cursor:pointer;padding:8px 10px;border-radius:8px;background:#FFFFFF;border:1.5px solid #DBEAFE;">
          <input type="radio" name="excelPreset" value="light" onchange="onExcelPresetChange()" style="margin-top:3px;">
          <div style="flex:1;">
            <div style="font-size:13px;font-weight:700;color:#1E3A5F;">🪶 Light <span style="font-size:11px;color:#6B7280;font-weight:400;">(중간 산출물 · 반복 작업용)</span></div>
            <div style="font-size:11.5px;color:#4B5563;margin-top:2px;">TC 전체 목록만 — 표지·통계 등 제외 (빠른 확인용)</div>
          </div>
        </label>
        <label class="excel-preset-row" style="display:flex;align-items:flex-start;gap:10px;cursor:pointer;padding:8px 10px;border-radius:8px;background:#FFFFFF;border:1.5px solid #DBEAFE;">
          <input type="radio" name="excelPreset" value="custom" onchange="onExcelPresetChange()" style="margin-top:3px;">
          <div style="flex:1;">
            <div style="font-size:13px;font-weight:700;color:#1E3A5F;">🛠 Custom <span style="font-size:11px;color:#6B7280;font-weight:400;">(시트별 직접 선택)</span></div>
            <div style="font-size:11.5px;color:#4B5563;margin-top:2px;">아래에서 포함할 시트를 직접 체크하세요</div>
          </div>
        </label>
      </div>
      <!-- Custom 모드 — 시트별 체크박스 (기본 숨김) -->
      <div id="excelCustomPanel" style="display:none;margin-top:10px;padding:12px;background:#FFFFFF;border:1px solid #DBEAFE;border-radius:8px;">
        <div style="font-size:11.5px;color:#1E3A5F;font-weight:600;margin-bottom:8px;">포함할 시트 선택</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:6px 14px;">
          <label style="display:flex;align-items:center;gap:6px;font-size:12.5px;color:#374151;cursor:pointer;">
            <input type="checkbox" class="excel-sheet-cb" data-sheet="cover" onchange="onExcelSheetCheckChange()" checked> 📋 표지
          </label>
          <label style="display:flex;align-items:center;gap:6px;font-size:12.5px;color:#374151;cursor:pointer;">
            <input type="checkbox" class="excel-sheet-cb" data-sheet="stats" onchange="onExcelSheetCheckChange()" checked> 📊 TC 통계
          </label>
          <label style="display:flex;align-items:center;gap:6px;font-size:12.5px;color:#374151;cursor:pointer;">
            <input type="checkbox" class="excel-sheet-cb" data-sheet="smoke" onchange="onExcelSheetCheckChange()" checked> 🔥 Smoke Test
          </label>
          <label style="display:flex;align-items:center;gap:6px;font-size:12.5px;color:#374151;cursor:pointer;">
            <input type="checkbox" class="excel-sheet-cb" data-sheet="traceability" onchange="onExcelSheetCheckChange()" checked> 🔗 Traceability
          </label>
          <label style="display:flex;align-items:center;gap:6px;font-size:12.5px;color:#9CA3AF;cursor:not-allowed;" title="필수 시트 — 항상 포함">
            <input type="checkbox" class="excel-sheet-cb" data-sheet="tc_list" checked disabled> 📌 TC 전체 목록 <span style="font-size:10px;">(필수)</span>
          </label>
          <label style="display:flex;align-items:center;gap:6px;font-size:12.5px;color:#374151;cursor:pointer;" id="excelChangeHistoryLabel">
            <input type="checkbox" class="excel-sheet-cb" data-sheet="change_history" onchange="onExcelSheetCheckChange()" checked> 🔄 변경 이력 <span style="font-size:10px;color:#6B7280;">(수정 모드 전용)</span>
          </label>
        </div>
        <div id="excelSheetSummary" style="margin-top:10px;font-size:11.5px;color:#1E3A5F;background:#EFF6FF;padding:6px 10px;border-radius:6px;">
          💡 요약: <strong>전체 시트 (6개)</strong>
        </div>
      </div>
    </div>

    <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-top:18px;">
      <button class="btn btn-success" onclick="approveGate()">
        ✅ 승인 및 TC 생성 시작
      </button>
      <button style="padding:8px 16px;background:#EFF6FF;color:#1D4ED8;border:1.5px solid #93C5FD;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;" onclick="regenerateClassification()">
        🔄 분류표 다시 생성
      </button>
      <button type="button" onclick="exportGateExcel()"
        style="padding:8px 16px; border:1.5px solid var(--teal); border-radius:8px;
          background:none; cursor:pointer; color:var(--teal); font-weight:600; font-size:13px;
          display:flex; align-items:center; gap:5px;">
        📥 Excel로 내보내기
      </button>
      <button class="btn-stop" id="stopBtn3" onclick="stopPipeline()">⏹ 여기서 중단</button>
    </div>
  </div>

  <!-- Step 4는 card2로 통합됨 (진행 상태·로그를 한곳에서 표시) -->

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

    <!-- 원칙 G — 중복 의심 TC 알림 (v0.9.17~). duplicate_warning SSE 이벤트로 채워짐 -->
    <div id="duplicateNotice" style="display:none;margin:12px 0;padding:14px 16px;background:#FFFBEB;border:1.5px solid #FCD34D;border-radius:10px;"></div>

    <!-- TC 통계 -->
    <div class="tc-stats" style="margin-bottom:16px">
      <div class="tc-stat">
        <div class="tc-stat-num" id="statTotal">—</div>
        <div class="tc-stat-label">총 TC</div>
      </div>
      <div class="tc-stat">
        <div class="tc-stat-num" id="statSmoke">—</div>
        <div class="tc-stat-label">🔥 Smoke TC</div>
      </div>
    </div>

    <!-- 추가 작업 -->
    <div style="display:flex; gap:10px; margin-bottom:16px; flex-wrap:wrap;">
      <button onclick="startNextIteration()" style="padding:10px 20px;background:#2563EB;color:#fff;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;">
        🔄 추가 TC 생성 (소스/범위 수정 후 재시작)
      </button>
      <button onclick="startNextIteration(true)" style="padding:10px 16px;background:#fff;color:#1D4ED8;border:1.5px solid #93C5FD;border-radius:8px;font-size:13px;cursor:pointer;">
        📝 범위만 변경하여 재시작
      </button>
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

<!-- Google Drive 폴더 선택 모달 -->
<div class="modal-bg" id="drive-folder-modal">
  <div class="modal" style="max-width:540px;">
    <h2 style="display:flex;align-items:center;gap:8px;">📁 업로드할 Drive 폴더 선택</h2>
    <div id="driveFolderEmail" style="font-size:12px;color:#666;margin-bottom:10px;"></div>
    <input type="text" id="driveFolderSearch" placeholder="폴더명 검색..."
      oninput="loadDriveFolders(this.value)"
      style="width:100%;padding:8px 12px;border:1.5px solid #D0D7DE;border-radius:8px;font-size:13px;margin-bottom:10px;">
    <div id="driveFolderList" style="max-height:320px;overflow-y:auto;border:1px solid #E2E8F0;border-radius:8px;background:#F9FAFB;"></div>
    <div id="driveSelectedFolder" style="font-size:12px;color:#166534;margin-top:8px;min-height:18px;"></div>
    <div class="modal-btns" style="margin-top:14px;">
      <button id="driveUploadBtn" onclick="confirmDriveUpload()" disabled
        style="padding:8px 18px;background:#2563EB;color:#fff;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;">
        ✅ 이 폴더에 업로드
      </button>
      <button class="btn-modal-close" onclick="closeDriveFolderModal()">취소</button>
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
  // 카드 숨김 (card2~card5) + Step 1 입력 카드 복원
  ['card2','card3','card5'].forEach(function(id) {
    var card = document.getElementById(id);
    if (card) card.classList.add('hidden');
  });
  document.getElementById('card1').classList.remove('hidden');
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
  // SuiteCode 섹션 리셋
  var suiteSection = document.getElementById('suiteCodeSection');
  if (suiteSection) { suiteSection.innerHTML = ''; suiteSection.style.display = 'none'; }
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

  // 프로젝트 변경 시 이전 세션의 UI 상태 완전 초기화
  // (중요: 이전 focus_area가 input에 남아 새 파이프라인에 전달되는 버그 방지
  //  + startBtn 등 버튼 상태가 이전 세션에 묶여 비활성으로 남는 문제 방지)
  document.getElementById('focusArea').value = '';
  document.getElementById('previousFocusHint').style.display = 'none';
  window._previousFocusArea = '';

  // SSE 연결 끊기 + 세션 참조 리셋
  if (eventSource) { eventSource.close(); eventSource = null; }
  currentSid = null;
  currentFilename = null;
  stopCountdown();

  // 진행/결과 카드 숨김 + Step 1 입력 카드 복원
  ['card2','card3','card5'].forEach(function(id) {
    var card = document.getElementById(id);
    if (card) card.classList.add('hidden');
  });
  document.getElementById('card1').classList.remove('hidden');

  // 중단/오류 배너 제거
  document.querySelectorAll('.stopped-banner, .error-banner').forEach(function(el) { el.remove(); });

  // 모든 버튼 재활성화 (이전 세션에서 disable된 상태 승계 방지)
  document.getElementById('startBtn').disabled = false;
  var startModifyBtn = document.getElementById('startModifyBtn');
  if (startModifyBtn) startModifyBtn.disabled = false;
  setStopButtonsDisabled(false);

  // TC 모드 토글 상태 리셋 (새 프로젝트는 다시 판별)
  window._autoScreenCode = undefined;

  // Step bar를 1단계로
  setStepBar(1);

  // ── 해당 프로젝트 데이터 로드 ──
  // 이전 작업 상태 확인
  var prevFocus = '';
  try {
    var r = await fetch('/projects/' + encodeURIComponent(name) + '/state');
    var d = await r.json();
    if (d.ok && d.has_state) {
      projectResumeState = d;
      var stageNames = {parsed:'문서 파싱', policy:'정책 분석', features:'기능 목록', classifying:'분류표 생성', gate_waiting:'분류표 검토 대기', tc_writing:'TC 작성'};
      document.getElementById('resumeStage').textContent = stageNames[d.stage] || d.stage;
      document.getElementById('resumeSavedAt').textContent = d.saved_at || '';
      document.getElementById('resumeBar').style.display = 'flex';
      // focus_area는 자동 채우지 않고 힌트로만 제공 — 의도치 않은 범위 제한 방지
      if (d.focus_area) prevFocus = d.focus_area;
    }
  } catch(e) {}
  // 이전 소스 복원
  try {
    var r2 = await fetch('/projects/' + encodeURIComponent(name) + '/sources');
    var d2 = await r2.json();
    if (d2.ok && d2.has_sources && d2.sources.length > 0) {
      sources = [];
      sourceCounter = 0;
      // spec_folder / spec_folder_prev 타입은 일반 입력 소스가 아니라 구조화 모드 박스로 분리
      var specFolderEntry = null;
      var specFolderPrevEntry = null;
      d2.sources.forEach(function(s) {
        if (s.type === 'spec_folder') { specFolderEntry = s; return; }
        if (s.type === 'spec_folder_prev') { specFolderPrevEntry = s; return; }
        var id = ++sourceCounter;
        sources.push({ id: id, type: s.type, content: s.content || '', selected_files: s.selected_files || null });
      });
      renderSources();

      // 구조화 spec 폴더 자동 복원 — 경로 채움 (spec 섹션은 기본 펼침 상태라 토글 불필요)
      if (specFolderEntry) {
        var pathEl = document.getElementById('specFolderPath');
        if (pathEl) pathEl.value = specFolderEntry.content || '';
        // spec 섹션이 접혀있으면 자동으로 펼침 (기본은 펼침이지만 사용자가 닫았을 수 있음)
        var specBody = document.getElementById('specFolderBody');
        if (specBody && specBody.style.display === 'none') {
          toggleAccordion('spec');
        }
        // 이전 폴더가 있으면 diff 박스도 자동 복원
        if (specFolderPrevEntry) {
          var diffBox = document.getElementById('diffBox');
          var prevEl = document.getElementById('prevSpecFolderPath');
          if (prevEl) prevEl.value = specFolderPrevEntry.content || '';
          if (diffBox && diffBox.style.display === 'none' && typeof toggleDiffMode === 'function') {
            toggleDiffMode();
          }
        }
      }

      if (d2.focus_area) prevFocus = d2.focus_area;  // state의 값과 sources의 값 중 존재하는 것
      var loadedCount = sources.length + (specFolderEntry ? 1 : 0) + (specFolderPrevEntry ? 1 : 0);
      var msg = '이전 소스 ' + loadedCount + '개를 불러왔습니다.';
      if (specFolderEntry) msg += ' (📁 구조화 spec 폴더 모드)';
      showToast(msg);
    }
  } catch(e) {}

  // 이전 범위가 있으면 힌트 배너로 표시 (자동 채움 X)
  if (prevFocus) {
    window._previousFocusArea = prevFocus;
    document.getElementById('previousFocusValue').textContent = prevFocus;
    document.getElementById('previousFocusHint').style.display = 'block';
  }
}

// 이전 범위 재사용 (사용자 명시적 클릭 시에만)
function reusePreviousFocus() {
  if (!window._previousFocusArea) return;
  document.getElementById('focusArea').value = window._previousFocusArea;
  document.getElementById('previousFocusHint').style.display = 'none';
  showToast('이전 범위를 불러왔습니다: ' + window._previousFocusArea.substring(0, 40) + (window._previousFocusArea.length > 40 ? '...' : ''));
}

// 힌트 무시
function dismissPreviousFocusHint() {
  document.getElementById('previousFocusHint').style.display = 'none';
  window._previousFocusArea = '';
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
  document.getElementById('card1').classList.remove('hidden');
  document.getElementById('card2').classList.add('hidden');
  document.getElementById('startBtn').disabled = false;
  setStepBar(1);
  showToast('소스를 확인하고 파이프라인을 다시 시작하세요.');
}

function startNextIteration(focusOnly) {
  // 완료/진행 카드 숨김 + Step 1 입력 카드 복원
  ['card2','card3','card5'].forEach(function(id) {
    document.getElementById(id).classList.add('hidden');
  });
  document.getElementById('card1').classList.remove('hidden');
  document.querySelectorAll('.stopped-banner, .error-banner').forEach(function(el) { el.remove(); });
  // Drive 버튼 라벨 reset — 이전 업로드 완료 상태 잔존 방지
  if (typeof resetDriveBtn === 'function') resetDriveBtn();
  // 상단 card2 요소 복원
  var logBox = document.getElementById('logBox');
  if (logBox) { logBox.style.display = ''; logBox.innerHTML = ''; }
  var stopBtn2 = document.getElementById('stopBtn2');
  if (stopBtn2) stopBtn2.style.display = '';
  var progressWrap = document.getElementById('progressBar');
  if (progressWrap && progressWrap.parentElement) progressWrap.parentElement.style.display = '';
  var substeps = document.querySelector('#card2 .substeps');
  if (substeps) substeps.style.display = '';
  // SuiteCode 리셋
  var suiteSection = document.getElementById('suiteCodeSection');
  if (suiteSection) { suiteSection.innerHTML = ''; suiteSection.style.display = 'none'; }
  // 버튼 활성화
  document.getElementById('startBtn').disabled = false;
  setStepBar(1);
  stopCountdown();
  if (eventSource) { eventSource.close(); eventSource = null; }
  // 범위만 변경 모드: 포커스 입력란으로 스크롤
  if (focusOnly) {
    document.getElementById('focusArea').focus();
    document.getElementById('focusArea').scrollIntoView({ behavior: 'smooth', block: 'center' });
    showToast('TC 생성 범위를 수정하고 파이프라인을 시작하세요.');
  } else {
    document.getElementById('card1').scrollIntoView({ behavior: 'smooth', block: 'start' });
    showToast('소스와 범위를 수정하고 파이프라인을 시작하세요.');
  }
}

async function resumePipeline() {
  if (!selectedProject) return;
  document.getElementById('startBtn').disabled = true;
  document.getElementById('card1').classList.add('hidden');
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
    const raw = await r.json();
    // 빈 이름 유령 레코드 제거 (최종 프론트엔드 방어선)
    projects = Array.isArray(raw) ? raw.filter(p => p && (p.name || '').trim()) : [];
    const sel = document.getElementById('projectSelect');
    const selMod = document.getElementById('modifyProjectSelect');
    sel.innerHTML = '<option value="">— 프로젝트를 선택하세요 —</option>';
    if (selMod) selMod.innerHTML = '<option value="">— 단발성 작업 (프로젝트 없음) —</option>';
    projects.forEach(p => {
      const label = p.name + ' (' + (p.updated_at || '신규') + ')';
      const opt = document.createElement('option');
      opt.value = p.name; opt.textContent = label;
      sel.appendChild(opt);
      if (selMod) {
        const opt2 = document.createElement('option');
        opt2.value = p.name; opt2.textContent = label;
        selMod.appendChild(opt2);
      }
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

// ── 기획서 diff 기반 TC 갱신 ─────────────────────────────────
let _diffSid = null;
let _diffReport = null;
let _diffFiles = { old: null, new: null, tc: null };  // {old_spec_path, new_spec_path, existing_tc_path}

async function handleDiffFileUpload(evt, slot) {
  const file = evt.target.files[0];
  if (!file) return;
  const ext = (file.name.split('.').pop() || '').toLowerCase();
  const statusEl = document.getElementById(slot === 'old' ? 'oldSpecStatus' :
                                            slot === 'new' ? 'newSpecStatus' : 'existingTcStatus');
  const dropzone = document.getElementById(slot === 'old' ? 'oldSpecDropzone' :
                                            slot === 'new' ? 'newSpecDropzone' : 'existingTcDropzone');

  // 업로드: MD/TXT는 /upload-md, TC(xlsx/md)는 /upload-existing-tc
  const fd = new FormData();
  fd.append('file', file);
  let endpoint, savedKind;
  if (slot === 'tc') {
    endpoint = '/upload-existing-tc';
    savedKind = 'tc';
  } else {
    endpoint = '/upload-md';
    savedKind = 'spec';
  }
  statusEl.style.display = 'block';
  statusEl.style.color = '#2563EB';
  statusEl.textContent = '⏳ 업로드 중...';
  try {
    const r = await fetch(endpoint, { method: 'POST', body: fd });
    const d = await r.json();
    if (!d.ok) {
      statusEl.style.color = '#DC2626';
      statusEl.textContent = '❌ ' + (d.error || '업로드 실패');
      return;
    }
    _diffFiles[slot] = d.filename;
    statusEl.style.color = 'var(--success)';
    let msg = '✓ ' + d.filename;
    if (d.tc_count !== undefined) msg += ` (TC ${d.tc_count}개 감지)`;
    statusEl.textContent = msg;
    dropzone.style.borderColor = 'var(--success)';
    dropzone.style.background = '#F0FDF4';
  } catch(e) {
    statusEl.style.color = '#DC2626';
    statusEl.textContent = '❌ 네트워크 오류: ' + e.message;
  }
}

async function startDiffAnalyze() {
  if (!_diffFiles.old || !_diffFiles.new) {
    alert('이전 기획서와 새 기획서를 모두 업로드하세요.');
    return;
  }
  const projectName = document.getElementById('modifyProjectSelect').value || '';
  const btn = document.getElementById('startDiffBtn');
  btn.disabled = true;
  btn.textContent = '⏳ 분석 중...';
  try {
    const r = await fetch('/analyze-diff', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_name: projectName,
        old_spec_path: _diffFiles.old,
        new_spec_path: _diffFiles.new,
        existing_tc_path: _diffFiles.tc || '',
      })
    });
    const d = await r.json();
    if (!d.ok) {
      alert('분석 오류: ' + d.error);
      btn.disabled = false; btn.textContent = '🔍 변경사항 분석';
      return;
    }
    _diffSid = d.sid;
    _diffReport = d.report;
    if (d.no_changes) {
      renderDiffReport(d.report, { noChanges: true, existingCount: d.existing_tc_count });
    } else {
      renderDiffReport(d.report, { noChanges: false, existingCount: d.existing_tc_count });
    }
    btn.disabled = false; btn.textContent = '🔍 변경사항 분석';
  } catch(e) {
    alert('네트워크 오류: ' + e.message);
    btn.disabled = false; btn.textContent = '🔍 변경사항 분석';
  }
}

function _escapeHtml(s) {
  return (s || '').replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
}

function renderDiffReport(report, meta) {
  const area = document.getElementById('diffReportArea');
  const summaryEl = document.getElementById('diffReportSummary');
  const sectionsEl = document.getElementById('diffReportSections');
  area.classList.remove('hidden');

  if (meta.noChanges) {
    summaryEl.innerHTML = '🎉 <strong>변경사항이 없습니다.</strong> 두 기획서의 구조적 차이가 탐지되지 않았습니다.';
    sectionsEl.innerHTML = '';
    return;
  }

  if (!report.has_spec_codes) {
    summaryEl.innerHTML = '⚠️ <strong>화면 코드(SCR/SCREEN/PAGE)가 탐지되지 않아 구조 비교가 어렵습니다.</strong><br>기획서에 <code>### SCR-001: 이름</code> 같은 헤더를 추가하거나, 「신규 TC 생성」 탭을 이용하세요.';
    sectionsEl.innerHTML = '';
    return;
  }

  const s = report.summary;
  summaryEl.innerHTML = `🆕 신규 <strong>${s.added_n}</strong>개 · 🔄 수정 <strong>${s.modified_n}</strong>개 · 🗑️ 삭제 <strong>${s.removed_n}</strong>개 · ✅ 유지 <strong>${s.unchanged_n}</strong>개` +
    (meta.existingCount ? ` <span style="color:var(--muted);">(기존 TC ${meta.existingCount}개)</span>` : '');

  let html = '';

  // 툴바: 전체 선택/해제 + 모두 펼치기/접기
  const totalItems = report.added.length + report.modified.length + report.removed.length;
  if (totalItems > 0) {
    html += `<div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap;">
      <button type="button" onclick="toggleSectionSelection('all', true)" style="padding:4px 10px;font-size:11px;background:#EFF6FF;border:1px solid #BFDBFE;border-radius:4px;cursor:pointer;font-weight:600;color:#1E40AF;">✓ 전체 선택 (${totalItems}개)</button>
      <button type="button" onclick="toggleSectionSelection('all', false)" style="padding:4px 10px;font-size:11px;background:#FFFFFF;border:1px solid #D1D5DB;border-radius:4px;cursor:pointer;">☐ 전체 해제</button>
      ${report.modified.length > 0 ? `
        <span style="width:1px;background:#E5E7EB;margin:0 4px;"></span>
        <button type="button" onclick="toggleAllDiffDetails(true)" style="padding:4px 10px;font-size:11px;background:#FFFFFF;border:1px solid #D1D5DB;border-radius:4px;cursor:pointer;">▼ 모두 펼치기</button>
        <button type="button" onclick="toggleAllDiffDetails(false)" style="padding:4px 10px;font-size:11px;background:#FFFFFF;border:1px solid #D1D5DB;border-radius:4px;cursor:pointer;">▲ 모두 접기</button>
      ` : ''}
    </div>`;
  }

  if (report.added.length) {
    html += `<div style="margin-top:10px;display:flex;align-items:center;justify-content:space-between;">
      <strong style="color:#047857;">🆕 신규 화면 (승인 시 TC 생성) <span style="font-size:11px;color:var(--muted);font-weight:normal;">${report.added.length}개</span></strong>
      <div style="display:flex;gap:4px;">
        <button type="button" onclick="toggleSectionSelection('add', true)" style="padding:2px 8px;font-size:11px;background:#F0FDF4;border:1px solid #BBF7D0;border-radius:4px;cursor:pointer;">✓ 전체 선택</button>
        <button type="button" onclick="toggleSectionSelection('add', false)" style="padding:2px 8px;font-size:11px;background:#FFFFFF;border:1px solid #D1D5DB;border-radius:4px;cursor:pointer;">☐ 전체 해제</button>
      </div>
    </div>`;
    html += '<div style="display:flex;flex-direction:column;gap:4px;margin-top:6px;">';
    for (const [idx, a] of report.added.entries()) {
      const detailsId = `diff-add-${idx}`;
      html += `<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:6px;overflow:hidden;">
        <label style="display:flex;align-items:flex-start;gap:8px;padding:6px 10px;cursor:pointer;">
          <input type="checkbox" class="diff-add-chk" value="${_escapeHtml(a.code)}" checked style="margin-top:3px;">
          <div style="flex:1;"><strong>${_escapeHtml(a.code)}</strong> — ${_escapeHtml(a.name)} <span style="font-size:11px;color:var(--muted);">(예상 TC ~${a.estimated_tc_count}개)</span></div>
          ${a.body ? `<button type="button" onclick="toggleDiffDetail('${detailsId}', this)" style="margin-left:auto;padding:2px 8px;font-size:11px;background:#FFFFFF;border:1px solid #86EFAC;border-radius:4px;cursor:pointer;white-space:nowrap;">▸ 내용</button>` : ''}
        </label>
        ${a.body ? `<div id="${detailsId}" style="display:none;padding:8px 12px;border-top:1px solid #BBF7D0;background:#FFFFFF;">
          <div style="font-size:11px;color:var(--muted);margin-bottom:4px;">신규 화면 내용 (미리보기)</div>
          <pre style="font-size:11px;background:#F9FAFB;padding:8px;border-radius:4px;max-height:240px;overflow:auto;white-space:pre-wrap;word-break:break-word;">${_escapeHtml(a.body)}</pre>
        </div>` : ''}
      </div>`;
    }
    html += '</div>';
  }
  if (report.modified.length) {
    html += `<div style="margin-top:10px;display:flex;align-items:center;justify-content:space-between;">
      <strong style="color:#B45309;">🔄 수정 화면 (승인 시 해당 TC ID 유지하며 재작성) <span style="font-size:11px;color:var(--muted);font-weight:normal;">${report.modified.length}개</span></strong>
      <div style="display:flex;gap:4px;">
        <button type="button" onclick="toggleSectionSelection('mod', true)" style="padding:2px 8px;font-size:11px;background:#FEF3C7;border:1px solid #FDE68A;border-radius:4px;cursor:pointer;">✓ 전체 선택</button>
        <button type="button" onclick="toggleSectionSelection('mod', false)" style="padding:2px 8px;font-size:11px;background:#FFFFFF;border:1px solid #D1D5DB;border-radius:4px;cursor:pointer;">☐ 전체 해제</button>
      </div>
    </div>`;
    html += '<div style="display:flex;flex-direction:column;gap:4px;margin-top:6px;">';
    for (const [idx, m] of report.modified.entries()) {
      const tcIds = (m.affected_tc_ids || []).slice(0, 5).join(', ') + (m.affected_count > 5 ? ` 외 ${m.affected_count - 5}` : '');
      const detailsId = `diff-mod-${idx}`;
      html += `<div style="background:#FEF3C7;border:1px solid #FDE68A;border-radius:6px;overflow:hidden;">
        <label style="display:flex;align-items:flex-start;gap:8px;padding:6px 10px;cursor:pointer;">
          <input type="checkbox" class="diff-mod-chk" value="${_escapeHtml(m.code)}" ${m.affected_count>0?'checked':''} style="margin-top:3px;">
          <div style="flex:1;"><strong>${_escapeHtml(m.code)}</strong> — ${_escapeHtml(m.name)}<br>
            <span style="font-size:11px;color:#92400E;">영향 TC: ${m.affected_count}개 ${tcIds ? '(' + _escapeHtml(tcIds) + ')' : '(매핑 없음)'}</span>
          </div>
          <button type="button" onclick="toggleDiffDetail('${detailsId}', this)" style="margin-left:auto;padding:2px 8px;font-size:11px;background:#FFFFFF;border:1px solid #FCD34D;border-radius:4px;cursor:pointer;white-space:nowrap;">▸ 변경 보기</button>
        </label>
        <div id="${detailsId}" style="display:none;padding:8px 12px;border-top:1px solid #FDE68A;background:#FFFFFF;">
          <div style="display:flex;gap:8px;margin-bottom:6px;font-size:11px;">
            <button type="button" onclick="switchDiffMode('${detailsId}', 'unified')" class="diff-mode-btn diff-mode-unified-${idx}" style="padding:3px 10px;background:#FDE68A;border:1px solid #F59E0B;border-radius:4px;cursor:pointer;font-weight:600;">🔀 변경점만 (기본)</button>
            <button type="button" onclick="switchDiffMode('${detailsId}', 'sidebyside')" class="diff-mode-btn diff-mode-sidebyside-${idx}" style="padding:3px 10px;background:#FFFFFF;border:1px solid #D1D5DB;border-radius:4px;cursor:pointer;">📄 전체 2단 보기</button>
          </div>
          <div class="diff-view-unified-${idx}">${_renderUnifiedDiff(m.line_diff)}</div>
          <div class="diff-view-sidebyside-${idx}" style="display:none;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
              <div>
                <div style="font-size:11px;color:#991B1B;font-weight:600;margin-bottom:4px;">— 이전</div>
                <pre style="font-size:11px;background:#FEF2F2;padding:8px;border-radius:4px;max-height:260px;overflow:auto;white-space:pre-wrap;word-break:break-word;">${_escapeHtml(m.old_body || '(비어있음)')}</pre>
              </div>
              <div>
                <div style="font-size:11px;color:#065F46;font-weight:600;margin-bottom:4px;">+ 새</div>
                <pre style="font-size:11px;background:#F0FDF4;padding:8px;border-radius:4px;max-height:260px;overflow:auto;white-space:pre-wrap;">${_escapeHtml(m.new_body || '(비어있음)')}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>`;
    }
    html += '</div>';
  }
  if (report.removed.length) {
    html += `<div style="margin-top:10px;display:flex;align-items:center;justify-content:space-between;">
      <strong style="color:#6B7280;">🗑️ 삭제 화면 (승인 시 기존 TC에 Deprecated 표시) <span style="font-size:11px;color:var(--muted);font-weight:normal;">${report.removed.length}개</span></strong>
      <div style="display:flex;gap:4px;">
        <button type="button" onclick="toggleSectionSelection('rem', true)" style="padding:2px 8px;font-size:11px;background:#F3F4F6;border:1px solid #D1D5DB;border-radius:4px;cursor:pointer;">✓ 전체 선택</button>
        <button type="button" onclick="toggleSectionSelection('rem', false)" style="padding:2px 8px;font-size:11px;background:#FFFFFF;border:1px solid #D1D5DB;border-radius:4px;cursor:pointer;">☐ 전체 해제</button>
      </div>
    </div>`;
    html += '<div style="display:flex;flex-direction:column;gap:4px;margin-top:6px;">';
    for (const [idx, r] of report.removed.entries()) {
      const tcIds = (r.affected_tc_ids || []).slice(0, 5).join(', ') + (r.affected_count > 5 ? ` 외 ${r.affected_count - 5}` : '');
      html += `<label style="display:flex;align-items:flex-start;gap:8px;padding:6px 10px;background:#F3F4F6;border:1px solid #D1D5DB;border-radius:6px;cursor:pointer;">
        <input type="checkbox" class="diff-rem-chk" value="${_escapeHtml(r.code)}" ${r.affected_count>0?'checked':''} style="margin-top:3px;">
        <div style="flex:1;"><strong>${_escapeHtml(r.code)}</strong> — ${_escapeHtml(r.name)}<br>
          <span style="font-size:11px;color:var(--muted);">영향 TC: ${r.affected_count}개 ${tcIds ? '(' + _escapeHtml(tcIds) + ')' : '(매핑 없음)'}</span>
        </div>
      </label>`;
    }
    html += '</div>';
  }
  sectionsEl.innerHTML = html;

  // 체크박스 변경 시 승인 버튼 상태 동기화
  document.querySelectorAll('.diff-add-chk, .diff-mod-chk, .diff-rem-chk').forEach(cb => {
    cb.addEventListener('change', _updateApproveButtonState);
  });
  _updateApproveButtonState();
}

function cancelDiff() {
  document.getElementById('diffReportArea').classList.add('hidden');
  _diffSid = null;
  _diffReport = null;
}

// 섹션(add/mod/rem/all)별 체크박스 일괄 선택/해제
function toggleSectionSelection(section, checked) {
  const selectors = {
    add: '.diff-add-chk',
    mod: '.diff-mod-chk',
    rem: '.diff-rem-chk',
    all: '.diff-add-chk, .diff-mod-chk, .diff-rem-chk',
  };
  const sel = selectors[section];
  if (!sel) return;
  document.querySelectorAll(sel).forEach(cb => {
    cb.checked = checked;
  });
  _updateApproveButtonState();
}

// 라인 단위 diff를 GitHub 스타일 unified diff로 렌더
function _renderUnifiedDiff(blocks) {
  if (!blocks || !blocks.length) {
    return '<div style="font-size:12px;color:var(--muted);padding:8px;">변경 정보가 없습니다.</div>';
  }
  const lineStyle = 'font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;padding:2px 8px;white-space:pre-wrap;word-break:break-word;border-left:3px solid transparent;';
  let html = '<div style="max-height:360px;overflow:auto;background:#F9FAFB;border:1px solid #E5E7EB;border-radius:4px;">';
  for (const blk of blocks) {
    if (blk.tag === 'truncated') {
      html += `<div style="${lineStyle}color:var(--muted);font-style:italic;padding:4px 8px;">... (이후 내용은 생략)</div>`;
      continue;
    }
    if (blk.tag === 'equal') {
      for (const ln of blk.old_lines) {
        const txt = ln === '... (중략)' ? '  …' : '  ' + ln;
        html += `<div style="${lineStyle}color:#6B7280;">${_escapeHtml(txt)}</div>`;
      }
      continue;
    }
    if (blk.tag === 'delete' || blk.tag === 'replace') {
      for (const ln of blk.old_lines) {
        html += `<div style="${lineStyle}background:#FEE2E2;border-left-color:#DC2626;color:#991B1B;">− ${_escapeHtml(ln)}</div>`;
      }
    }
    if (blk.tag === 'insert' || blk.tag === 'replace') {
      for (const ln of blk.new_lines) {
        html += `<div style="${lineStyle}background:#DCFCE7;border-left-color:#16A34A;color:#166534;">+ ${_escapeHtml(ln)}</div>`;
      }
    }
  }
  html += '</div>';
  return html;
}

function switchDiffMode(detailsId, mode) {
  const container = document.getElementById(detailsId);
  if (!container) return;
  const idxMatch = detailsId.match(/\d+$/);
  if (!idxMatch) return;
  const idx = idxMatch[0];
  const unified = container.querySelector('.diff-view-unified-' + idx);
  const side    = container.querySelector('.diff-view-sidebyside-' + idx);
  const btnU    = container.querySelector('.diff-mode-unified-' + idx);
  const btnS    = container.querySelector('.diff-mode-sidebyside-' + idx);
  if (mode === 'unified') {
    if (unified) unified.style.display = 'block';
    if (side)    side.style.display = 'none';
    if (btnU) { btnU.style.background = '#FDE68A'; btnU.style.borderColor = '#F59E0B'; btnU.style.fontWeight = '600'; }
    if (btnS) { btnS.style.background = '#FFFFFF'; btnS.style.borderColor = '#D1D5DB'; btnS.style.fontWeight = 'normal'; }
  } else {
    if (unified) unified.style.display = 'none';
    if (side)    side.style.display = 'block';
    if (btnU) { btnU.style.background = '#FFFFFF'; btnU.style.borderColor = '#D1D5DB'; btnU.style.fontWeight = 'normal'; }
    if (btnS) { btnS.style.background = '#FDE68A'; btnS.style.borderColor = '#F59E0B'; btnS.style.fontWeight = '600'; }
  }
}

// 수정 화면 카드의 변경 내용 펼침/접힘
function toggleDiffDetail(detailsId, btn) {
  const el = document.getElementById(detailsId);
  if (!el) return;
  const opened = el.style.display !== 'none';
  el.style.display = opened ? 'none' : 'block';
  if (btn) {
    const base = btn.textContent.replace(/^[▸▾]\s*/, '');
    btn.textContent = (opened ? '▸ ' : '▾ ') + base;
  }
}

function toggleAllDiffDetails(open) {
  document.querySelectorAll('[id^="diff-mod-"], [id^="diff-add-"]').forEach(el => {
    if (!el.id.match(/^diff-(mod|add)-\d+$/)) return;
    el.style.display = open ? 'block' : 'none';
  });
  // 버튼 라벨 동기화 — 각 카드의 "▸/▾" 표시
  document.querySelectorAll('button').forEach(btn => {
    const t = btn.textContent || '';
    if (t.includes('변경 보기') || t.endsWith('내용')) {
      btn.textContent = (open ? '▾ ' : '▸ ') + t.replace(/^[▸▾]\s*/, '');
    }
  });
}

function _getApprovedSelection() {
  return {
    added:    [...document.querySelectorAll('.diff-add-chk:checked')].map(el => el.value),
    modified: [...document.querySelectorAll('.diff-mod-chk:checked')].map(el => el.value),
    removed:  [...document.querySelectorAll('.diff-rem-chk:checked')].map(el => el.value),
  };
}

function _updateApproveButtonState() {
  const btn = document.querySelector('#diffReportArea .btn-primary');
  if (!btn) return;
  const sel = _getApprovedSelection();
  const total = sel.added.length + sel.modified.length + sel.removed.length;
  if (total === 0) {
    btn.disabled = true;
    btn.style.opacity = '0.5';
    btn.style.cursor = 'not-allowed';
    btn.textContent = '⚠️ 승인할 항목을 1개 이상 선택하세요';
  } else {
    btn.disabled = false;
    btn.style.opacity = '1';
    btn.style.cursor = 'pointer';
    btn.textContent = `✅ 승인 후 TC 갱신 시작 (${total}개)`;
  }
}

async function approveAndUpdate() {
  if (!_diffSid) { alert('분석 세션이 없습니다. 먼저 분석을 실행하세요.'); return; }
  const approved = _getApprovedSelection();
  if (approved.added.length + approved.modified.length + approved.removed.length === 0) {
    alert('승인할 항목을 최소 1개 이상 선택하세요.');
    return;
  }
  document.getElementById('card1').classList.add('hidden');
  document.getElementById('card2').classList.remove('hidden');
  setStepBar(2);
  document.getElementById('card2').scrollIntoView({ behavior: 'smooth', block: 'start' });
  document.getElementById('stageLabel').textContent = 'TC 갱신 시작 중...';

  try {
    const r = await fetch('/update-tc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sid: _diffSid, approved: approved })
    });
    const d = await r.json();
    if (!d.ok) { alert('오류: ' + d.error); return; }
    currentSid = d.sid;
    connectStream(d.sid);
  } catch(e) {
    alert('네트워크 오류: ' + e.message);
  }
}

// TC 수정 시작 (기존 — 레거시, 현재 UI에서는 사용 안 함)
async function startModify() {
  const projectName = document.getElementById('projectSelect').value;
  const changeDesc  = document.getElementById('changeDesc').value.trim();

  if (!projectName) { alert('수정할 프로젝트를 선택하세요.'); return; }
  if (!changeDesc)   { alert('변경사항 내용을 입력하세요.'); return; }

  document.getElementById('startModifyBtn').disabled = true;
  document.getElementById('card1').classList.add('hidden');
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

// ── 입력 변경 감지 ──────────────────────────────────────────────
// 사용자가 소스(추가/삭제/수정) 또는 TC 생성 범위를 변경하면 호출.
// 이전 세션의 결과 카드를 숨기고 startBtn을 활성화해 "다시 시작 가능" 상태로.
// 진행 중 세션(currentSid)이 있으면 해당 카드는 유지 (사용자 실수로 실행 중단 방지).
function onInputsChanged() {
  // 1. 새 파이프라인 시작 가능하도록 버튼 활성
  var startBtn = document.getElementById('startBtn');
  if (startBtn) startBtn.disabled = false;
  var startModifyBtn = document.getElementById('startModifyBtn');
  if (startModifyBtn) startModifyBtn.disabled = false;

  // 2. 이전 결과 카드는 항상 무효화 (입력이 바뀌면 이전 결과는 stale)
  var card5 = document.getElementById('card5');
  if (card5) card5.classList.add('hidden');

  // 3. 실행 중이 아니면 진행/Gate/작성 카드도 숨김 + Step 1 입력 카드 복원
  if (!currentSid) {
    ['card2','card3'].forEach(function(id) {
      var card = document.getElementById(id);
      if (card) card.classList.add('hidden');
    });
    document.getElementById('card1').classList.remove('hidden');
    document.querySelectorAll('.stopped-banner, .error-banner').forEach(function(el) { el.remove(); });
    setStepBar(1);
  }

  // 4. 생성 모드 안내 갱신 (소스 크기 기반 권장 모드 제시)
  refreshGenerationModeHint();
}

// ── 생성 모드 관련 ──────────────────────────────────────────────
// 정책 반영 모드(summary): policy → features → classify 3단계
// Quick 모드(direct): 원문을 직접 분류 — 누락 최소화, 200KB 이하 권장
const DIRECT_MODE_SIZE_LIMIT = 200 * 1024; // 200KB

function estimateSourceBytes() {
  // 각 소스의 content 크기 합산 (UTF-8 기준 대략)
  let total = 0;
  for (const s of sources) {
    if (!s || !s.content) continue;
    try { total += new Blob([s.content]).size; } catch(e) { total += (s.content || '').length; }
  }
  return total;
}

function formatBytes(n) {
  if (n <= 0) return '0 B';
  if (n < 1024) return n + ' B';
  if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB';
  return (n / 1024 / 1024).toFixed(2) + ' MB';
}

function refreshGenerationModeHint() {
  const sizeEl = document.getElementById('modeSourceSize');
  const statusEl = document.getElementById('modeSourceStatus');
  const quickLabel = document.getElementById('modeQuickLabel');
  const quickRadio = document.querySelector('input[name="genMode"][value="direct"]');
  if (!sizeEl || !statusEl) return;

  const bytes = estimateSourceBytes();
  sizeEl.textContent = bytes > 0 ? formatBytes(bytes) : '-';

  if (bytes === 0) {
    statusEl.textContent = '소스를 추가하면 권장 모드가 안내됩니다.';
    statusEl.style.color = '#6B7280';
    if (quickLabel) quickLabel.style.opacity = '1';
    if (quickRadio) quickRadio.disabled = false;
    return;
  }

  if (bytes <= DIRECT_MODE_SIZE_LIMIT) {
    statusEl.innerHTML = '🟢 Quick 모드 사용 가능 (원문 직접 분류 — 누락 최소화)';
    statusEl.style.color = '#047857';
    if (quickLabel) quickLabel.style.opacity = '1';
    if (quickRadio) quickRadio.disabled = false;
  } else {
    statusEl.innerHTML = '🟡 소스가 200KB를 초과합니다 — 정책 반영 모드 권장';
    statusEl.style.color = '#92400E';
    if (quickLabel) quickLabel.style.opacity = '0.55';
    if (quickRadio) {
      quickRadio.disabled = true;
      // 비활성 시 기본 모드로 복귀
      if (quickRadio.checked) {
        const stdRadio = document.querySelector('input[name="genMode"][value="summary"]');
        if (stdRadio) stdRadio.checked = true;
      }
    }
  }
}

function onGenModeChanged() {
  // 선택된 라디오 카드에 outline 강조
  document.querySelectorAll('input[name="genMode"]').forEach(function(r) {
    const box = r.closest('label');
    if (!box) return;
    if (r.checked) {
      box.style.borderColor = '#2563EB';
      box.style.background = '#EFF6FF';
    } else {
      box.style.borderColor = '#D1D5DB';
      box.style.background = '#FFFFFF';
    }
  });
}

// 초기 선택 강조 + What's New 배너 체크
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', function() {
    try { onGenModeChanged(); refreshGenerationModeHint(); } catch(e) {}
    try { checkWhatsNewBanner(); } catch(e) {}
  });
}

// v0.9.6 What's New 배너 표시 — localStorage에 dismiss 기록이 없으면 자동 표시
const _WHATS_NEW_VERSION = '{{ app_version }}';
const _WHATS_NEW_KEY = 'tc_whatsnew_dismissed_' + _WHATS_NEW_VERSION;
// 서버 재시작 후 버전 비교용
window._INITIAL_APP_VERSION = '{{ app_version }}';

function checkWhatsNewBanner() {
  try {
    if (localStorage.getItem(_WHATS_NEW_KEY) === '1') return;
  } catch(e) {}
  const banner = document.getElementById('whatsNewBanner');
  if (banner) banner.style.display = 'block';
}

function dismissWhatsNew() {
  const banner = document.getElementById('whatsNewBanner');
  if (banner) banner.style.display = 'none';
  try { localStorage.setItem(_WHATS_NEW_KEY, '1'); } catch(e) {}
}

function showWhatsNew() {
  const modal = document.getElementById('whatsNewModal');
  if (modal) modal.style.display = 'flex';
}

function getSelectedGenerationMode() {
  const sel = document.querySelector('input[name="genMode"]:checked');
  return sel ? sel.value : 'summary';
}

function addSource(type) {
  const id = ++sourceCounter;
  sources.push({ id, type, content: '' });
  renderSources();
  onInputsChanged();  // 소스 추가 감지
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
  onInputsChanged();  // 소스 삭제 감지
}

function clearAllSources() {
  if (sources.length === 0) return;
  const n = sources.length;
  if (!confirm('입력 소스 ' + n + '개를 모두 삭제하시겠습니까?\\n\\n이 작업은 되돌릴 수 없습니다.')) return;
  sources = [];
  renderSources();
  onInputsChanged();  // 전체 삭제 감지
}

function updateSourceContent(id, value) {
  const s = sources.find(s => s.id === id);
  if (s) s.content = value;
  onInputsChanged();  // 소스 내용 편집 감지 (URL/텍스트 입력 등)
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
      onInputsChanged();  // PDF 업로드 완료 감지
    } else {
      if (zone) zone.innerHTML = '❌ ' + data.error;
    }
  } catch(e) {
    if (zone) zone.innerHTML = '❌ 업로드 실패';
  }
}

// 공통 업로드 헬퍼 — File[] 배열 → /upload-md 순차 업로드 → sources 배열 갱신
async function _uploadMdFilesToSources(id, files) {
  const zone = document.getElementById('srcZone_' + id);
  const uploaded = [];
  const failed = [];

  if (zone) zone.innerHTML = `⏳ ${files.length}개 파일 업로드 중...`;

  for (let i = 0; i < files.length; i++) {
    const f = files[i];
    if (zone) zone.innerHTML = `⏳ 업로드 중 ${i+1}/${files.length}: ${_escapeHtml(f.name)}`;
    const fd = new FormData();
    // webkitdirectory로 들어온 File은 webkitRelativePath 있음 — 서버는 파일명만 쓰므로 파일 객체 그대로 전달
    fd.append('file', f);
    try {
      const resp = await fetch('/upload-md', { method: 'POST', body: fd });
      const data = await resp.json();
      if (data.ok) {
        uploaded.push(data.filename);
      } else {
        failed.push(f.name + ': ' + (data.error || '업로드 실패'));
      }
    } catch(e) {
      failed.push(f.name + ': 네트워크 오류');
    }
  }

  if (uploaded.length === 0) {
    if (zone) zone.innerHTML = '❌ 모든 파일 업로드 실패<br><span style="font-size:11px;">' + failed.map(_escapeHtml).join('<br>') + '</span>';
    return { uploaded: [], failed };
  }

  // 첫 파일 → 현재 카드
  const firstSource = sources.find(s => s.id === id);
  if (firstSource) firstSource.content = uploaded[0];

  // 나머지 파일 → 새 md 소스로 추가
  for (let i = 1; i < uploaded.length; i++) {
    const newId = ++sourceCounter;
    sources.push({ id: newId, type: 'md', content: uploaded[i] });
  }

  renderSources();
  onInputsChanged();

  if (failed.length > 0) {
    showToast('⚠️ ' + failed.length + '개 파일 업로드 실패 — 콘솔 확인');
    console.warn('마크다운 업로드 실패 목록:', failed);
  } else if (uploaded.length > 1) {
    showToast('✅ ' + uploaded.length + '개 마크다운 파일 추가됨');
  }
  return { uploaded, failed };
}

async function onMdFileChange(id, input) {
  if (!input.files.length) return;
  const files = Array.from(input.files);
  await _uploadMdFilesToSources(id, files);
}

async function onMdFolderChange(id, input) {
  if (!input.files.length) return;
  const all = Array.from(input.files);

  // .md / .markdown / .txt 만 필터 (숨김 파일 제외)
  const mdExt = /\.(md|markdown|txt)$/i;
  const filtered = all.filter(f => {
    const name = (f.name || '').toLowerCase();
    if (!name || name.startsWith('.')) return false;
    return mdExt.test(name);
  });

  if (filtered.length === 0) {
    const zone = document.getElementById('srcZone_' + id);
    if (zone) zone.innerHTML = '❌ 선택한 폴더에 .md / .markdown / .txt 파일이 없습니다 (' + all.length + '개 파일 중 0개 매칭)';
    return;
  }

  // 파일명 기준 정렬 (쪽대본 번호 순서 유지 도움 — 01_spec, 02_spec ...)
  filtered.sort((a, b) => {
    const an = (a.webkitRelativePath || a.name).toLowerCase();
    const bn = (b.webkitRelativePath || b.name).toLowerCase();
    return an.localeCompare(bn);
  });

  // 50개 초과 시 경고 확인
  if (filtered.length > 50) {
    const msg = `📁 폴더에서 ${filtered.length}개의 마크다운 파일을 발견했습니다.\n\n모두 업로드하시겠습니까?\n\n(권장: 50개 이하 · 파일이 너무 많으면 TC 생성 시간이 오래 걸리거나 실패할 수 있습니다)`;
    if (!confirm(msg)) {
      const zone = document.getElementById('srcZone_' + id);
      if (zone) zone.innerHTML = '❌ 사용자가 업로드를 취소했습니다 (' + filtered.length + '개 파일).';
      return;
    }
  }

  // 폴더 구조 정보 — 상위 경로 보여주기
  const folderName = (filtered[0].webkitRelativePath || '').split('/')[0] || '(폴더)';
  showToast('📁 "' + folderName + '" 폴더에서 ' + filtered.length + '개 .md 파일 발견 — 업로드 시작');

  await _uploadMdFilesToSources(id, filtered);
}

function renderSources() {
  const list  = document.getElementById('sourceList');
  const empty = document.getElementById('sourceEmpty');
  const clearBtn = document.getElementById('btnClearAllSources');
  if (!list) return;
  // 전체 삭제 버튼: 2개 이상일 때만 노출
  if (clearBtn) clearBtn.style.display = (sources.length >= 2) ? '' : 'none';
  if (sources.length === 0) {
    list.innerHTML = '';
    empty && empty.classList.remove('hidden');
    return;
  }
  empty && empty.classList.add('hidden');
  list.innerHTML = sources.map(src => {
    const badgeClass = src.type;
    const badges = {
      pdf: '📄 PDF', url: '🔗 GitHub URL', web: '🌐 웹 URL', md: '📝 마크다운', text: '✏️ 텍스트',
      spec_folder: '📁 구조화 spec 폴더', spec_folder_prev: '📁 이전 spec 폴더'
    };
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
      if (src.content) {
        body = '<span class="src-file-name">✅ ' + src.content + '</span>';
      } else {
        body = '<div class="src-dropzone" id="srcZone_' + src.id + '" style="padding:16px;">'
             + '<div style="font-size:13px;color:var(--text);margin-bottom:8px;">📝 마크다운 파일 또는 폴더 업로드</div>'
             + '<div style="font-size:11px;color:var(--muted);margin-bottom:10px;">여러 .md 파일 선택 가능 · 폴더 선택 시 내부 .md만 자동 필터</div>'
             + '<div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">'
             + '<button type="button" class="btn" style="padding:6px 14px;font-size:12px;" onclick="document.getElementById(&#39;srcFile_' + src.id + '&#39;).click()">📄 파일 선택</button>'
             + '<button type="button" class="btn" style="padding:6px 14px;font-size:12px;" onclick="document.getElementById(&#39;srcDir_' + src.id + '&#39;).click()">📁 폴더 선택</button>'
             + '</div></div>';
      }
      body += '<input type="file" id="srcFile_' + src.id + '" accept=".md,.markdown,.txt" multiple style="display:none" onchange="onMdFileChange(' + src.id + ', this)">';
      body += '<input type="file" id="srcDir_' + src.id + '" webkitdirectory directory multiple style="display:none" onchange="onMdFolderChange(' + src.id + ', this)">';
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

  // 구조화 spec 폴더 모드 분기 — v0.10.x: spec 폴더 경로가 비어있지 않으면 spec 모드 우선
  const specPathEl = document.getElementById('specFolderPath');
  const specFolderActive = specPathEl && specPathEl.value.trim();
  if (specFolderActive) {
    return startPipelineSpecFolder(projectName, focusArea, specPathEl.value.trim());
  }

  if (sources.length === 0) { alert('구조화 spec 폴더 경로를 입력하거나, 개별 소스를 하나 이상 추가하세요.'); return; }

  const typeNames = { pdf: 'PDF', url: 'GitHub URL', web: '웹 URL', md: '마크다운', text: '텍스트' };
  for (const s of sources) {
    if (!s.content.trim()) {
      alert(typeNames[s.type] + ' 소스의 내용을 입력해주세요.');
      return;
    }
  }

  const payload = sources.map(s => ({ type: s.type, content: s.content, selected_files: s.selected_files || null }));

  document.getElementById('startBtn').disabled = true;
  document.getElementById('card1').classList.add('hidden');
  document.getElementById('card2').classList.remove('hidden');
  setStepBar(2);
  document.getElementById('card2').scrollIntoView({ behavior: 'smooth', block: 'start' });
  // 새 파이프라인 시작 시 중단 버튼 재활성화 (이전 세션 상태 승계 방지)
  setStopButtonsDisabled(false);
  var stopBtn2Init = document.getElementById('stopBtn2');
  if (stopBtn2Init) stopBtn2Init.style.display = '';

  try {
    const resp = await fetch('/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sources: payload, project_name: projectName, focus_area: focusArea || null, generation_mode: getSelectedGenerationMode() })
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

async function startPipelineSpecFolder(projectName, focusArea, folderPath) {
  document.getElementById('startBtn').disabled = true;
  document.getElementById('card1').classList.add('hidden');
  document.getElementById('card2').classList.remove('hidden');
  setStepBar(2);
  document.getElementById('card2').scrollIntoView({ behavior: 'smooth', block: 'start' });
  setStopButtonsDisabled(false);

  // diff 모드 옵션 수집
  const diffBox = document.getElementById('diffBox');
  const prevPath = (document.getElementById('prevSpecFolderPath') && document.getElementById('prevSpecFolderPath').value || '').trim();
  const diffActive = diffBox && diffBox.style.display !== 'none' && prevPath;
  const includeUnchanged = document.getElementById('includeUnchanged') ? document.getElementById('includeUnchanged').checked : false;

  try {
    const resp = await fetch('/start-spec-folder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_name: projectName,
        focus_area: focusArea || null,
        folder_path: folderPath,
        prev_folder_path: diffActive ? prevPath : '',
        include_unchanged: includeUnchanged,
      })
    });
    const data = await resp.json();
    if (!data.ok) {
      alert('오류: ' + data.error);
      document.getElementById('startBtn').disabled = false;
      document.getElementById('card1').classList.remove('hidden');
      document.getElementById('card2').classList.add('hidden');
      return;
    }
    currentSid = data.sid;
    if (data.summary) {
      showToast(`📁 폴더 분류: overview ${data.summary.overview ? '✓' : '✗'} · policy ${data.summary.policy_count} · design ${data.summary.design_count} · 화면 ${data.summary.screens_count}개${diffActive ? ' (diff 모드)' : ''}`, 'success');
    }
    connectStream(data.sid);
  } catch(e) {
    alert('서버 오류: ' + e.message);
    document.getElementById('startBtn').disabled = false;
  }
}

function toggleDiffMode() {
  const box = document.getElementById('diffBox');
  const btn = document.getElementById('btnDiffToggle');
  if (!box || !btn) return;
  const enabled = box.style.display === 'none';
  box.style.display = enabled ? '' : 'none';
  btn.textContent = enabled ? '사용 중 ✓' : '사용';
  btn.style.background = enabled ? '#FCD34D' : '#FFFFFF';
}

async function previewDiff() {
  const newPath = document.getElementById('specFolderPath').value.trim();
  const prevPath = document.getElementById('prevSpecFolderPath').value.trim();
  if (!newPath || !prevPath) { alert('두 폴더 경로를 모두 입력하세요.'); return; }
  const prev = document.getElementById('diffPreview');
  prev.style.display = '';
  prev.innerHTML = '⏳ diff 계산 중...';
  try {
    const r = await fetch('/diff-spec-folders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder_path: newPath, prev_folder_path: prevPath })
    });
    const d = await r.json();
    if (!d.ok) { prev.innerHTML = '<span style="color:#DC2626;">❌ ' + d.error + '</span>'; return; }
    let html = '<div style="line-height:1.6;">';
    html += `<div><strong>🆕 추가:</strong> ${d.added.length}개${d.added.length ? ' — <code>' + d.added.slice(0, 8).join(', ') + (d.added.length > 8 ? ', ...' : '') + '</code>' : ''}</div>`;
    html += `<div><strong>📝 수정:</strong> ${d.modified.length}개${d.modified.length ? ' — <code>' + d.modified.slice(0, 8).join(', ') + (d.modified.length > 8 ? ', ...' : '') + '</code>' : ''}</div>`;
    html += `<div><strong>🗑 삭제:</strong> ${d.removed.length}개${d.removed.length ? ' — <code>' + d.removed.slice(0, 8).join(', ') + (d.removed.length > 8 ? ', ...' : '') + '</code>' : ''}</div>`;
    html += `<div><strong>✅ 동일:</strong> ${d.unchanged_count}개</div>`;
    if (d.common_changed) {
      html += '<div style="margin-top:4px;color:#B45309;"><strong>⚠️ 공통 문서(정책/디자인/overview) 변경됨</strong> — 모든 화면 재생성을 권장합니다 (전체 일관성 위해).</div>';
    }
    html += `<div style="margin-top:6px;color:#059669;"><strong>재생성 대상:</strong> ${d.regenerate_count}개${d.common_changed ? ' (공통 변경 시 전체 처리됨)' : ''}</div>`;
    html += '</div>';
    prev.innerHTML = html;
  } catch(e) {
    prev.innerHTML = '<span style="color:#DC2626;">❌ 서버 오류: ' + e.message + '</span>';
  }
}

// 입력 디바운스 — 타이핑 중 매번 호출하지 않게
let _resumeCheckTimer = null;
function onProjectNameInputForResume() {
  if (_resumeCheckTimer) clearTimeout(_resumeCheckTimer);
  _resumeCheckTimer = setTimeout(() => {
    // 새 구조: spec 아코디언 body 가 펼쳐져 있을 때만 resume 체크
    const body = document.getElementById('specFolderBody');
    if (body && body.style.display !== 'none') checkResumeSpec();
  }, 500);
}

async function checkResumeSpec() {
  const projectName = document.getElementById('projectName').value.trim();
  if (!projectName) return;
  try {
    const r = await fetch('/check-resume-spec?project_name=' + encodeURIComponent(projectName));
    const d = await r.json();
    const btn = document.getElementById('btnResumeSpec');
    if (!btn) return;
    if (d.ok && d.resumable) {
      btn.style.display = '';
      btn.title = `완료된 화면 ${d.completed_count}개 / 전체 ${d.total_screens || '?'}개 (stage=${d.stage})`;
      btn.textContent = `▶ 이어서 작업 (${d.completed_count}/${d.total_screens || '?'} 완료)`;
    } else {
      btn.style.display = 'none';
    }
  } catch(e) {
    // 무시
  }
}

async function resumeSpecFolder() {
  const projectName = document.getElementById('projectName').value.trim() || '프로젝트';
  if (!confirm(`"${projectName}" 의 이전 작업을 이어서 실행하시겠습니까?\\n(이미 완료된 화면은 건너뛰고 미완료 화면만 처리합니다)`)) return;

  document.getElementById('startBtn').disabled = true;
  document.getElementById('card1').classList.add('hidden');
  document.getElementById('card2').classList.remove('hidden');
  setStepBar(2);
  setStopButtonsDisabled(false);

  try {
    const r = await fetch('/start-spec-folder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_name: projectName, resume: true })
    });
    const d = await r.json();
    if (!d.ok) {
      alert('이어서 작업 실패: ' + d.error);
      document.getElementById('startBtn').disabled = false;
      document.getElementById('card1').classList.remove('hidden');
      document.getElementById('card2').classList.add('hidden');
      return;
    }
    currentSid = d.sid;
    showToast(`▶ 이어서 작업 — stage=${d.resumed_stage}`, 'success');
    connectStream(d.sid);
  } catch(e) {
    alert('서버 오류: ' + e.message);
    document.getElementById('startBtn').disabled = false;
  }
}

// ── 신규 아코디언 시스템 (v0.10.x UI 정식화) ────────────────────────
// 이전: toggleSpecFolderMode() 가 별도 박스 표시/숨김
// 현재: spec 섹션은 기본 펼침, legacy 소스는 기본 접힘. toggleAccordion('spec'|'legacy')
function toggleAccordion(which) {
  const map = {
    spec:   { body: 'specFolderBody',   chev: 'specFolderChevron' },
    legacy: { body: 'legacySourceBody', chev: 'legacySourceChevron' },
  };
  const cfg = map[which];
  if (!cfg) return;
  const body = document.getElementById(cfg.body);
  const chev = document.getElementById(cfg.chev);
  if (!body || !chev) return;
  const opening = body.style.display === 'none';
  body.style.display = opening ? '' : 'none';
  chev.textContent = opening ? '▼' : '▶';
  if (which === 'spec' && opening) checkResumeSpec();
}

// 하위 호환 — 이전 toggleSpecFolderMode() 호출하는 곳 보호
function toggleSpecFolderMode() {
  // 이전 코드 호환: 호출되면 spec 아코디언 토글
  toggleAccordion('spec');
}

// ── 최근 사용 폴더 드롭다운 ─────────────────────────────────────────
async function toggleRecentFolders() {
  const panel = document.getElementById('recentFoldersPanel');
  if (!panel) return;
  if (panel.style.display !== 'none' && panel.dataset.loaded === '1') {
    panel.style.display = 'none';
    return;
  }
  await loadRecentFolders('specFolderPath', 'recentFoldersPanel');
}

async function toggleRecentPrevFolders() {
  const panel = document.getElementById('recentPrevFoldersPanel');
  if (!panel) return;
  if (panel.style.display !== 'none' && panel.dataset.loaded === '1') {
    panel.style.display = 'none';
    return;
  }
  await loadRecentFolders('prevSpecFolderPath', 'recentPrevFoldersPanel');
}

async function loadRecentFolders(targetInputId, panelId) {
  const projectName = document.getElementById('projectName').value.trim();
  const panel = document.getElementById(panelId);
  panel.style.display = '';
  panel.innerHTML = '<div style="padding:10px;color:#94A3B8;">⏳ 불러오는 중...</div>';
  try {
    const url = '/recent-spec-folders' + (projectName ? '?project_name=' + encodeURIComponent(projectName) : '');
    const r = await fetch(url);
    const d = await r.json();
    if (!d.ok || !d.folders || d.folders.length === 0) {
      panel.innerHTML = '<div style="padding:10px;color:#94A3B8;">최근 사용한 폴더가 없습니다.</div>';
      panel.dataset.loaded = '1';
      return;
    }
    // 안전한 렌더 — DOM API 사용해 onclick handler 직접 부여 (escape 함정 회피)
    panel.innerHTML = '';
    d.folders.forEach(function(f) {
      var div = document.createElement('div');
      div.style.cssText = 'padding:8px 12px;border-bottom:1px solid #F1F5F9;cursor:pointer;font-family:monospace;color:#1E293B;';
      div.textContent = f;
      div.onclick = function() { pickRecentFolder(targetInputId, panelId, f); };
      div.onmouseover = function() { this.style.background = '#F1F5F9'; };
      div.onmouseout = function() { this.style.background = ''; };
      panel.appendChild(div);
    });
    panel.dataset.loaded = '1';
  } catch (e) {
    panel.innerHTML = '<div style="padding:10px;color:#DC2626;">오류: ' + e.message + '</div>';
  }
}

function pickRecentFolder(targetInputId, panelId, path) {
  const input = document.getElementById(targetInputId);
  if (input) {
    input.value = path;
    input.dispatchEvent(new Event('input'));
  }
  const panel = document.getElementById(panelId);
  if (panel) panel.style.display = 'none';
}

function onSpecFolderChanged() {
  const prev = document.getElementById('specFolderPreview');
  if (prev) { prev.style.display = 'none'; prev.innerHTML = ''; }
  const hint = document.getElementById('specFolderHint');
  if (hint) hint.textContent = '경로가 변경됐습니다. 미리보기를 다시 실행하세요.';
}

async function previewSpecFolder() {
  const path = document.getElementById('specFolderPath').value.trim();
  if (!path) { alert('폴더 경로를 입력하세요.'); return; }
  const prev = document.getElementById('specFolderPreview');
  prev.style.display = '';
  prev.innerHTML = '⏳ 폴더 스캔 중...';
  try {
    const r = await fetch('/preview-spec-folder', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder_path: path })
    });
    const d = await r.json();
    if (!d.ok) { prev.innerHTML = '<span style="color:#DC2626;">❌ ' + d.error + '</span>'; return; }
    let html = '<div style="line-height:1.7;">';
    html += `<div><strong>📂 폴더:</strong> <code>${d.folder}</code></div>`;
    html += `<div><strong>📑 overview:</strong> ${d.overview || '<span style="color:#DC2626;">없음 (분류표 자동 생성 불가)</span>'}</div>`;
    html += `<div><strong>📋 policy:</strong> ${d.policy.length === 0 ? '<span style="color:#9CA3AF;">없음</span>' : d.policy.join(', ')}</div>`;
    html += `<div><strong>🎨 design:</strong> ${d.design.length === 0 ? '<span style="color:#9CA3AF;">없음</span>' : d.design.join(', ')}</div>`;
    html += `<div><strong>🖥️ 화면 md:</strong> ${d.screens.length}개`;
    if (d.screens.length > 0) html += ` <span style="color:#64748B;">(${d.screens.slice(0, 5).join(', ')}${d.screens.length > 5 ? ', ...' : ''})</span>`;
    html += '</div>';
    html += `<div><strong>📊 화면 목록 표 행:</strong> ${d.screen_rows_count}행`;
    if (d.majors.length > 0) html += ` · 대분류: ${d.majors.join(', ')}`;
    html += '</div>';
    if (d.screens.length === 0) {
      html += '<div style="margin-top:6px;color:#DC2626;">⚠️ scr/SCR-*.md 형식의 화면 파일이 필요합니다.</div>';
    } else {
      html += '<div style="margin-top:6px;color:#059669;">✅ 시작 준비 완료. 화면 ' + d.screens.length + '개에 대해 LLM 호출이 발생합니다.</div>';
    }
    html += '</div>';
    prev.innerHTML = html;
  } catch(e) {
    prev.innerHTML = '<span style="color:#DC2626;">❌ 서버 오류: ' + e.message + '</span>';
  }
}

let _sseReconnectCount = 0;
const _SSE_MAX_RECONNECT = 3;

function connectStream(sid) {
  // 이전 중단 배너 제거 + 재연결 카운트 리셋
  document.querySelectorAll('.stopped-banner, .error-banner, .session-lost-banner').forEach(el => el.remove());
  _sseReconnectCount = 0;

  eventSource = new EventSource('/stream/' + sid);
  eventSource.onopen = () => {
    // 성공 연결 → 재연결 카운트 리셋, 중단 버튼 활성
    _sseReconnectCount = 0;
    setStopButtonsDisabled(false);
  };
  eventSource.onmessage = (e) => {
    try {
      const evt = JSON.parse(e.data);
      handleEvent(evt);
    } catch(err) {}
  };
  eventSource.onerror = async () => {
    // 먼저 세션이 서버에 살아있는지 HEAD로 확인
    // (/stream/<sid> 가 404면 세션이 사라진 것 — 영원히 재시도해도 소용없음)
    let sessionAlive = false;
    try {
      const head = await fetch('/stream/' + sid, { method: 'HEAD' });
      sessionAlive = (head.status !== 404);
    } catch(e) {
      // 네트워크 자체 문제 — 재시도 의미 있음
      sessionAlive = true;
    }

    if (!sessionAlive) {
      // 세션 소멸 확정 → 재연결 중단 + 명확한 안내
      if (eventSource) { eventSource.close(); eventSource = null; }
      showSessionLostBanner();
      setStopButtonsDisabled(true);
      stopCountdown();
      return;
    }

    // 세션은 살아있음 — 일반 네트워크 지연 등. 제한된 횟수만 재시도 안내
    _sseReconnectCount++;
    if (_sseReconnectCount === 1) {
      addLog('⚠️ SSE 연결 오류. 재연결 시도 중...', true);
    } else if (_sseReconnectCount >= _SSE_MAX_RECONNECT) {
      addLog(`⚠️ 재연결 실패(${_sseReconnectCount}회). 새로고침이나 세션 확인 필요.`, true);
      if (eventSource) { eventSource.close(); eventSource = null; }
      showSessionLostBanner(true);
      return;
    }
    setStopButtonsDisabled(false);
  };
}

function showSessionLostBanner(afterRetries) {
  // 이미 표시되어 있으면 중복 방지
  if (document.querySelector('.session-lost-banner')) return;
  const banner = document.createElement('div');
  banner.className = 'session-lost-banner';
  banner.style.cssText = 'margin:12px 0;padding:14px 18px;background:#FEF2F2;border:1.5px solid #DC2626;border-radius:10px;color:#991B1B;';
  banner.innerHTML = `
    <div style="font-weight:700;font-size:14px;margin-bottom:6px;">🔌 세션이 종료되었습니다</div>
    <div style="font-size:12.5px;line-height:1.6;color:#7F1D1D;">
      서버와의 연결이 끊어졌습니다${afterRetries ? ' (재연결 시도 실패)' : ''}. 다음 중 하나를 선택하세요:<br>
      • <strong>새로 시작</strong>: 브라우저 새로고침 후 처음부터<br>
      • <strong>이어서 작업</strong>: 프로젝트 선택 후 아래 버튼 (승인 전 단계만 지원)
    </div>
    <div style="margin-top:10px;display:flex;gap:8px;">
      <button onclick="location.reload()" style="padding:6px 14px;background:#DC2626;color:#FFFFFF;border:none;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;">🔄 새로고침</button>
      <button onclick="document.querySelector('.session-lost-banner').remove()" style="padding:6px 14px;background:#FFFFFF;color:#6B7280;border:1px solid #D1D5DB;border-radius:6px;font-size:12px;cursor:pointer;">✕ 닫기</button>
    </div>
  `;
  // 진행 중 카드 위에 삽입
  const card2 = document.getElementById('card2');
  if (card2 && !card2.classList.contains('hidden')) {
    card2.insertBefore(banner, card2.firstChild);
  } else {
    const wrap = document.querySelector('.app') || document.body;
    wrap.insertBefore(banner, wrap.firstChild);
  }
}

function handleEvent(evt) {
  if (evt.type === 'ping') return;

  if (evt.type === 'stage') {
    const { stage, label, pct, eta_sec } = evt.data;
    updateProgress(label, pct, eta_sec);
    updateSubsteps(stage, label);
    // 통합된 card2 제목/배지를 현 단계에 맞게 갱신
    const titleEl = document.getElementById('pipelineCardTitle');
    const badgeEl = document.getElementById('pipelineCardBadge');
    if (titleEl && badgeEl) {
      if (stage <= 2) {
        titleEl.textContent = '⚙️ 분석 및 분류';
        badgeEl.textContent = 'Step 2';
      } else if (stage === 3) {
        titleEl.textContent = '🔍 분류표 검토 대기';
        badgeEl.textContent = 'Step 3';
      } else if (stage === 4) {
        titleEl.textContent = '✍️ TC 생성';
        badgeEl.textContent = 'Step 4';
      } else if (stage >= 5) {
        titleEl.textContent = '📊 Excel 빌드';
        badgeEl.textContent = 'Step 5';
      }
    }
    setStepBar(stage);
  }

  if (evt.type === 'log') {
    // 모든 로그는 card2의 단일 logBox에 표시 (통합 뷰)
    addLog(evt.data.msg);
  }

  if (evt.type === 'gate') {
    const isModify = evt.data.mode === 'modify';
    window._gateMode = isModify ? 'modify' : 'new';
    // 제목/안내문 전환
    document.getElementById('gateTitle').innerHTML = isModify
      ? '📋 영향도 검토 <span class="badge">Step 3 · Human Gate</span>'
      : '🔍 분류표 검토 <span class="badge">Step 3 · Human Gate</span>';
    document.getElementById('gateInfoBox').innerHTML = isModify
      ? 'AI가 분석한 변경 영향도입니다. 하단 AI 도우미로 수정을 요청하고, 아래 내용에서 확인한 뒤 승인하세요.'
      : 'AI가 생성한 분류표입니다. 하단 AI 도우미로 수정을 요청하고, 아래 표에서 확인한 뒤 승인하세요.';
    initGateChat(evt.data.content);
    // 입력 소스 SCR 매핑 — 프론트 전역에 저장 (미니 채팅/뷰어 등에서 참조 가능)
    window._sourceScrMap = evt.data.source_scr_map || {};
    // 사용자 안내: 입력 소스에서 화면 식별자 발견 여부
    renderSourceScrNotice(window._sourceScrMap);
    // v0.9.22 Stage 1 — 분류표 중복 가능성 예측 알림
    window._classifyPrediction = evt.data.duplicate_prediction || { predictions: [], high_risk_count: 0 };
    try { renderClassifyDuplicateNotice(window._classifyPrediction); } catch (_) {}
    // Gate 진입 시 입력/파이프라인 카드는 숨기고 Gate 패널에 집중
    document.getElementById('card1').classList.add('hidden');
    document.getElementById('card2').classList.add('hidden');
    document.getElementById('card3').classList.remove('hidden');
    setStepBar(3);
    // Excel 옵션 — '🔄 변경 이력' 체크박스: 신규 모드면 disabled, 수정 모드면 enabled
    var changeCb = document.querySelector('.excel-sheet-cb[data-sheet="change_history"]');
    var changeLabel = document.getElementById('excelChangeHistoryLabel');
    if (changeCb && changeLabel) {
      if (isModify) {
        changeCb.disabled = false;
        changeLabel.style.color = '#374151';
        changeLabel.style.cursor = 'pointer';
      } else {
        changeCb.disabled = true;
        changeCb.checked = false;
        changeLabel.style.color = '#9CA3AF';
        changeLabel.style.cursor = 'not-allowed';
      }
      try { updateExcelSheetSummary(); } catch(_) {}
    }

    // TC ID 모드 기본값 결정: 프로젝트가 SM/SA면 System Generated ON, 아니면 OFF
    // (screen_code_map 서버 응답으로 screen_based_default 확인)
    var _projName = document.getElementById('projectName').value || '';
    loadScreenCodeMap(_projName).then(function(res) {
      var defaultOn = !!(res && res.screen_based_default);
      // 사용자가 아직 선택하지 않았다면 기본값 적용
      if (window._autoScreenCode === undefined) {
        window._autoScreenCode = defaultOn;
      }
      var topToggle = document.getElementById('tcIdModeToggle');
      if (topToggle) {
        topToggle.checked = !!window._autoScreenCode;
        setTcIdMode(topToggle.checked);
      }
    });

    document.getElementById('card3').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // 원칙 G — 중복 의심 TC 발견 알림 (v0.9.17~). 결과 카드(card5) 에서 표시되도록 sess에 보관.
  if (evt.type === 'duplicate_warning') {
    window._duplicateReport = evt.data;  // {patterns, total_duplicates, suggested_keep, suggested_remove}
    addLog('⚠️ 중복 의심 패턴 ' + (evt.data.patterns || []).length + '개 발견 — 결과 화면에서 상세 확인');
  }

  if (evt.type === 'done') {
    stopCountdown();
    const { filename, size, sid, total_tc, min_tc, smoke_tc } = evt.data;
    currentFilename = filename;
    // 모든 substep을 done 처리 (visual 완결)
    for (let i = 1; i <= 6; i++) {
      const el = document.getElementById('sub' + i);
      if (el) { el.classList.remove('active'); el.classList.add('done'); }
    }
    // 입력(card1)/파이프라인(card2) 숨기고 완료 카드(card5) 노출
    document.getElementById('card1').classList.add('hidden');
    document.getElementById('card2').classList.add('hidden');
    document.getElementById('card5').classList.remove('hidden');
    document.getElementById('resultFilename').textContent = filename;
    document.getElementById('resultMeta').textContent =
      `${(size / 1024).toFixed(1)} KB`;
    document.getElementById('statTotal').textContent = total_tc;
    // Smoke TC: 서버가 smoke_tc를 보내면 우선 사용, 없으면 min_tc 폴백 (하위호환)
    const smokeVal = (typeof smoke_tc === 'number') ? smoke_tc : min_tc;
    document.getElementById('statSmoke').textContent = (smokeVal !== undefined && smokeVal !== null) ? smokeVal : '—';
    // Drive 업로드 버튼 라벨 reset — 이전 결과의 'Drive 업로드 완료' 상태가 새 결과에
    // 그대로 남는 버그 차단. 새 파일은 아직 업로드 전이므로 원래 라벨로 복귀.
    resetDriveBtn();
    setStepBar(5);
    setStopButtonsDisabled(true);
    // 원칙 G — 중복 의심 TC 알림 렌더링 (있을 경우)
    try { renderDuplicateNotice(window._duplicateReport); } catch (_) {}
    document.getElementById('card5').scrollIntoView({ behavior: 'smooth', block: 'start' });
    showToast('🎉 TC 생성 완료!');
    if (eventSource) eventSource.close();
  }

  if (evt.type === 'stopped') {
    stopCountdown();
    setStopButtonsDisabled(true);
    ['card2', 'card3'].forEach(id => {
      const card = document.getElementById(id);
      if (!card.classList.contains('hidden')) {
        const banner = document.createElement('div');
        banner.className = 'stopped-banner';
        banner.innerHTML = '<div class="stopped-icon">⏹</div>' +
          '<div style="flex:1;">' +
            '<div class="stopped-msg">파이프라인이 중단되었습니다.</div>' +
            '<div class="stopped-sub">아래 버튼으로 다음 작업을 선택하세요.</div>' +
          '</div>' +
          '<div style="display:flex;gap:8px;flex-wrap:wrap;">' +
            '<button onclick="restartFromScratch()" style="padding:8px 16px;background:#2563EB;color:#fff;border:none;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;white-space:nowrap;">🏠 처음부터 시작</button>' +
            '<button onclick="retryPipeline()" style="padding:8px 14px;background:#fff;color:#1D4ED8;border:1.5px solid #93C5FD;border-radius:8px;font-size:12px;cursor:pointer;white-space:nowrap;">🔄 이어서 재시작</button>' +
          '</div>';
        banner.style.cssText = 'display:flex;align-items:center;gap:14px;flex-wrap:wrap;';
        card.appendChild(banner);
      }
    });
    document.getElementById('startBtn').disabled = false;
    document.getElementById('startModifyBtn').disabled = false;
    // card1 (입력 카드) 도 함께 노출 — 사용자가 처음부터 시작 / 입력 변경 등 옵션 갖도록
    document.getElementById('card1').classList.remove('hidden');
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

function updateProgress(label, pct, etaSec) {
  document.getElementById('stageLabel').textContent = label + ' (' + pct + '%)';
  document.getElementById('progressBar').style.width = pct + '%';
  // 서버가 eta_sec을 명시하면 우선 사용
  if (typeof etaSec === 'number' && etaSec > 0) {
    startCountdown(etaSec);
    return;
  }
  // 폴백: label 기준으로 대략적인 예상 시간 추정 (pct 정확 매칭 의존 제거)
  const txt = String(label || '').toLowerCase();
  let estSec = 0;
  if (txt.includes('파싱')) estSec = 20;
  else if (txt.includes('정책·기능') || txt.includes('정책+기능') || txt.includes('통합 추출')) estSec = 90;
  else if (txt.includes('인벤토리')) estSec = 60;
  else if (txt.includes('정책') || txt.includes('기능 목록')) estSec = 60;
  else if (txt.includes('분류표')) estSec = 45;
  else if (txt.includes('gate') || txt.includes('검토 대기')) estSec = 0;  // 사용자 대기
  else if (txt.includes('tc 작성') || txt.includes('tc 생성')) estSec = 0; // 가변 — 중분류별로 다름
  else if (txt.includes('품질 검토') || txt.includes('누락')) estSec = 30;
  else if (txt.includes('보강')) estSec = 30;
  else if (txt.includes('excel') || txt.includes('빌드')) estSec = 60;
  else if (txt.includes('완료')) estSec = 0;
  if (estSec > 0) startCountdown(estSec);
  else stopCountdown();
}

// 백엔드 stage(1~5) + label 조합으로 현재 활성 substep 계산
// substep 구성: sub1 파싱 · sub2 정책·기능 · sub3 분류 · sub4 검토 · sub5 TC 생성 · sub6 Excel
function updateSubsteps(stage, label) {
  const ids = ['sub1','sub2','sub3','sub4','sub5','sub6'];
  // 모두 초기화
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.remove('active','done');
  });

  // stage와 label로 현재 substep 인덱스 결정 (1-based)
  const txt = String(label || '').toLowerCase();
  let active = 1;
  if (stage <= 1) {
    active = 1;  // 파싱
  } else if (stage === 2) {
    // 라벨 기준으로 정책·기능 vs 분류 구분
    if (txt.includes('분류표')) active = 3;  // "분류표 생성"
    else active = 2;  // "정책 분석", "기능 목록", "정책·기능 통합 추출" 등
  } else if (stage === 3) {
    active = 3;  // Gate 대기 — 분류 완료 직후
  } else if (stage === 4) {
    // 검토 vs TC 생성 구분
    if (txt.includes('검토') || txt.includes('보강')) active = 4;
    else if (txt.includes('excel') || txt.includes('빌드')) active = 6;
    else active = 5;  // "TC 작성 시작", "TC 작성: ..."
  } else if (stage === 5) {
    // Excel 빌드 또는 완료
    if (txt.includes('완료')) {
      active = 6;
      // 완료 시 sub6까지 done 처리
      for (let i = 1; i <= 6; i++) {
        const el = document.getElementById('sub' + i);
        if (el) el.classList.add('done');
      }
      return;
    }
    active = 6;
  }

  // 이전 substep들은 done, 현재만 active
  for (let i = 1; i < active; i++) {
    const el = document.getElementById('sub' + i);
    if (el) el.classList.add('done');
  }
  const cur = document.getElementById('sub' + active);
  if (cur) cur.classList.add('active');
}

function addLog(msg, isError=false) {
  const box = document.getElementById('logBox');
  const line = document.createElement('div');
  line.className = 'log-line' + (isError ? ' error' : '');
  line.textContent = '[' + new Date().toLocaleTimeString() + '] ' + msg;
  box.appendChild(line);
  box.scrollTop = box.scrollHeight;
}

// NOTE: addTcLog는 제거됨 — 통합 card2의 addLog 하나만 사용
// NOTE: 이전에 있던 "대분류 체크리스트"(parseDomains/renderDomainChecklist/selectAllDomains/getSelectedDomains)는
// 제거되었습니다. 범위 지정은 Step 1의 "TC 생성 범위"(focus_area)로 일원화되었습니다.

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

// ── 입력 소스 화면 식별자 (v0.9.13) — gate 이벤트로 받은 source_scr_map 안내 ──
// ── 원칙 G — 중복 의심 TC 알림 (v0.9.17~) ──
// duplicate_warning SSE 이벤트로 받은 결과를 결과 카드(card5) 에 렌더링
function renderDuplicateNotice(report) {
  var el = document.getElementById('duplicateNotice');
  if (!el) return;
  if (!report || !report.patterns || report.patterns.length === 0) {
    el.style.display = 'none';
    return;
  }
  var patterns = report.patterns;
  var totalDup = report.total_duplicates || 0;

  var html = '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">';
  html += '<span style="font-size:18px;">⚠️</span>';
  html += '<strong style="font-size:14px;color:#92400E;">중복 의심 패턴 ' + patterns.length + '개 발견 (원칙 G)</strong>';
  html += '<span style="font-size:11px;color:#78350F;">통합 시 약 ' + totalDup + '개 TC 감소 가능</span>';
  html += '</div>';
  html += '<div style="font-size:12px;color:#78350F;margin-bottom:10px;line-height:1.55;">';
  html += '같은 그룹 내에 동일한 비기능/에러 패턴이 여러 화면에 반복 작성되었습니다. ';
  html += '아래 패턴 중 통합이 필요한 것을 검토하세요. ';
  html += '<strong>스펙 표에 명시된 에러 케이스는 보존</strong>하고, AI 가 추가한 일반 비기능 TC 만 통합하는 것이 원칙입니다.';
  html += '</div>';

  // 패턴별 상세
  html += '<div style="background:#FFFFFF;border:1px solid #FBBF24;border-radius:8px;overflow:hidden;">';
  patterns.forEach(function(p, idx) {
    var border = idx > 0 ? 'border-top:1px solid #FCD34D;' : '';
    html += '<div style="padding:10px 12px;' + border + '">';
    html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">';
    html += '<span style="font-size:13px;font-weight:700;color:#92400E;">🔁 ' + escapeHtml(p.pattern) + '</span>';
    html += '<span style="font-size:11px;color:#78350F;">— ' + escapeHtml(p.major) + '</span>';
    html += '<span style="margin-left:auto;font-size:11px;background:#FEF3C7;color:#92400E;padding:2px 8px;border-radius:4px;font-weight:600;">' + p.count + '개 TC</span>';
    html += '</div>';
    html += '<div style="font-size:11.5px;color:#374151;line-height:1.6;">';
    html += '<strong>유지 권장</strong> (대표 화면): <code style="background:#D1FAE5;padding:1px 5px;border-radius:3px;color:#065F46;">' + escapeHtml(p.keep) + '</code><br>';
    html += '<strong>통합 후보</strong>: ';
    html += (p.remove || []).map(function(id) {
      return '<code style="background:#FEE2E2;padding:1px 5px;border-radius:3px;color:#991B1B;">' + escapeHtml(id) + '</code>';
    }).join(' ');
    html += '<br><span style="font-size:10px;color:#6B7280;">└ TC: ';
    html += (p.tcs || []).map(function(t) { return escapeHtml(t.id) + ' ' + escapeHtml(t.title || '').substring(0, 40); }).join(' / ');
    html += '</span>';
    html += '</div>';
    html += '</div>';
  });
  html += '</div>';

  // ── v0.9.22: 자동 통합 액션 (단계 가이드 단순화) ──
  html += '<div style="margin-top:14px;padding:12px;background:#ECFDF5;border:1.5px solid #6EE7B7;border-radius:8px;">';
  html += '<div style="font-size:12.5px;font-weight:700;color:#065F46;margin-bottom:6px;display:flex;align-items:center;gap:6px;">';
  html += '<span>💡</span><span>지금 바로 정리하시겠어요?</span>';
  html += '</div>';
  html += '<div style="font-size:11.5px;color:#374151;line-height:1.55;margin-bottom:10px;">';
  html += '아래 <strong>"🔁 자동 통합 + Excel 재생성"</strong> 버튼을 누르면 AI 가 통합 후보 TC 들을 제거하고 새 Excel 을 만들어줍니다. <strong>원본 Excel 은 보존</strong>됩니다 (파일명에 <code style="background:#FFFFFF;padding:1px 4px;border-radius:3px;">_merged</code> 추가).';
  html += '</div>';
  html += '<div style="display:flex;gap:8px;flex-wrap:wrap;">';
  html += '<button onclick="autoMergeTcs()" id="autoMergeTcsBtn" style="padding:9px 16px;background:#10B981;color:#FFFFFF;border:none;border-radius:6px;font-size:13px;font-weight:700;cursor:pointer;">🔁 자동 통합 + Excel 재생성</button>';
  html += '<button onclick="copyDuplicateReportToClipboard()" style="padding:9px 14px;background:#FFFFFF;color:#065F46;border:1.5px solid #6EE7B7;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;">📋 수동 — 분석 결과 복사</button>';
  html += '</div>';
  html += '<div style="font-size:10.5px;color:#6B7280;margin-top:8px;">자동 통합이 실패하거나 직접 검토하고 싶을 때만 복사 버튼을 사용하세요.</div>';
  html += '</div>';

  el.innerHTML = html;
  el.style.display = '';
}

// ── v0.9.22 Stage 2 — TC 자동 통합 + Excel 재생성 ──
async function autoMergeTcs() {
  var report = window._duplicateReport;
  if (!report || !report.patterns || report.patterns.length === 0) {
    alert('통합할 중복 패턴이 없습니다.');
    return;
  }
  if (!currentSid) { alert('세션이 없습니다.'); return; }

  var totalRemove = report.total_duplicates || 0;
  if (!confirm('AI 가 통합 후보 TC ' + totalRemove + '개를 제거하고 새 Excel 을 생성합니다.\\n원본 Excel 은 보존됩니다 (별도 파일).\\n약 30~60초 소요.\\n계속할까요?')) return;

  var btn = document.getElementById('autoMergeTcsBtn');
  if (btn) {
    btn.disabled = true;
    btn.textContent = '⏳ 통합 중... (30~60초)';
    btn.style.background = '#9CA3AF';
    btn.style.cursor = 'wait';
  }

  try {
    var r = await fetch('/merge-tcs/' + currentSid, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ duplicate_report: report }),
    });
    var d = await r.json();
    if (!d.ok) {
      alert('통합 실패: ' + (d.error || 'unknown'));
      if (btn) {
        btn.disabled = false;
        btn.textContent = '🔁 자동 통합 + Excel 재생성';
        btn.style.background = '#10B981';
        btn.style.cursor = 'pointer';
      }
      return;
    }

    // 결과 카드 갱신 — 새 파일명, 새 TC 수
    var fileEl = document.getElementById('resultFilename');
    var metaEl = document.getElementById('resultMeta');
    var totalEl = document.getElementById('statTotal');
    var smokeEl = document.getElementById('statSmoke');
    if (fileEl) fileEl.textContent = d.filename;
    if (metaEl) metaEl.textContent = (d.size ? (d.size / 1024).toFixed(1) + ' KB' : '—') + ' · 통합본';
    if (totalEl) totalEl.textContent = d.new_total_tc;
    if (smokeEl) smokeEl.textContent = d.new_smoke_tc;
    currentFilename = d.filename;

    // 알림 박스 → 녹색 완료 표시
    var notice = document.getElementById('duplicateNotice');
    if (notice) {
      notice.style.background = '#ECFDF5';
      notice.style.borderColor = '#6EE7B7';
      notice.innerHTML = '<div style="display:flex;align-items:center;gap:10px;color:#065F46;font-size:13px;">';
      notice.innerHTML += '<span style="font-size:24px;">✅</span>';
      notice.innerHTML += '<div><strong>자동 통합 완료</strong><br>';
      notice.innerHTML += '<span style="font-size:11.5px;">';
      notice.innerHTML += '제거된 TC: <strong>' + d.removed_count + '개</strong> · ';
      notice.innerHTML += '새 Excel: <code style="background:#FFFFFF;padding:1px 5px;border-radius:3px;">' + escapeHtml(d.filename) + '</code><br>';
      notice.innerHTML += '원본 Excel 은 폴더에 그대로 보존되어 있습니다.';
      notice.innerHTML += '</span></div></div>';
    }
    showToast('✅ ' + d.removed_count + '개 TC 통합 완료 — 새 Excel: ' + d.filename, 'success');
  } catch (e) {
    alert('네트워크 오류: ' + e.message);
    if (btn) {
      btn.disabled = false;
      btn.textContent = '🔁 자동 통합 + Excel 재생성';
      btn.style.background = '#10B981';
      btn.style.cursor = 'pointer';
    }
  }
}

function copyDuplicateReportToClipboard() {
  var report = window._duplicateReport;
  if (!report || !report.patterns) return;

  // v0.9.21: 복사되는 텍스트에 사용 안내 + AI 즉시 실행 가능한 명령형 포함
  var text = '# 중복 의심 패턴 통합 요청 (원칙 G)\\n\\n';
  text += '> 사용 방법: 이 텍스트를 분류표 검토(Step 3) 의 하단 AI 도우미 채팅에 붙여넣고 전송하세요.\\n';
  text += '> AI 가 자동으로 통합 후보 TC 들을 제거하고 대표 화면에만 1개로 통합합니다.\\n\\n';
  text += '---\\n\\n';
  text += '## 분석 요약\\n';
  text += '- 총 ' + report.patterns.length + '개 중복 패턴 발견\\n';
  text += '- 통합 시 약 ' + (report.total_duplicates || 0) + '개 TC 감소 가능\\n\\n';
  text += '## 통합 지시\\n\\n';
  text += '아래 패턴별로 **통합 후보 TC 들을 분류표에서 제거**해줘. **유지 권장 TC** 는 그대로 두고, 그 TC 의 비고에 \\'[통합] 그룹 단위 비기능 검증\\' 태그를 추가해줘.\\n\\n';
  report.patterns.forEach(function(p, idx) {
    text += '### ' + (idx+1) + '. ' + p.pattern + ' (' + p.major + ')\\n';
    text += '- ✅ 유지: `' + p.keep + '`\\n';
    text += '- ❌ 제거: ' + (p.remove || []).map(function(id) { return '`' + id + '`'; }).join(', ') + '\\n';
    if (p.tcs && p.tcs.length) {
      text += '- 상세:\\n';
      p.tcs.forEach(function(t) {
        text += '  - ' + t.id + ' — ' + (t.middle || '') + ' / ' + (t.title || '').substring(0, 60) + '\\n';
      });
    }
    text += '\\n';
  });
  text += '---\\n\\n';
  text += '**스펙 표에 명시된 에러 케이스는 보존**하고, 위 비기능 패턴(네트워크/타임아웃/로딩 등)만 통합해줘.\\n';

  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(function() {
      showToast('📋 복사 완료 — Step 3 의 AI 도우미 채팅에 Cmd+V 후 전송하세요', 'success');
    });
  } else {
    alert(text);
  }
}

// 헬퍼 — 안전한 HTML escape (이미 있으면 재사용 가능)
if (typeof escapeHtml === 'undefined') {
  window.escapeHtml = function(s) {
    if (s === null || s === undefined) return '';
    return String(s).replace(/[&<>"']/g, function(c) {
      return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c];
    });
  };
}

// ── v0.9.22 Stage 1 — 분류표 중복 가능성 예측 알림 ──
function renderClassifyDuplicateNotice(prediction) {
  var el = document.getElementById('classifyDuplicateNotice');
  if (!el) return;
  prediction = prediction || { predictions: [], high_risk_count: 0 };
  if (!prediction.high_risk_count || !prediction.predictions || prediction.predictions.length === 0) {
    el.style.display = 'none';
    return;
  }
  var html = '<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">';
  html += '<span style="font-size:18px;">⚠️</span>';
  html += '<strong style="font-size:13.5px;color:#92400E;">중복 가능성 ' + prediction.predictions.length + '개 그룹 발견 (Stage 1 — TC 작성 전)</strong>';
  html += '</div>';
  html += '<div style="font-size:11.5px;color:#78350F;margin-bottom:10px;line-height:1.55;">';
  html += '같은 대분류 내에 중분류가 많거나 동일 비기능 키워드가 반복되어, AI 가 TC 작성 시 비기능 TC 를 여러 화면에 반복 작성할 가능성이 있습니다. 미리 분류표를 정리하면 TC 결과가 깔끔해집니다.';
  html += '</div>';

  // 예측별 상세
  html += '<div style="background:#FFFFFF;border:1px solid #FBBF24;border-radius:8px;overflow:hidden;margin-bottom:10px;">';
  prediction.predictions.forEach(function(p, idx) {
    var border = idx > 0 ? 'border-top:1px solid #FCD34D;' : '';
    html += '<div style="padding:10px 12px;' + border + '">';
    html += '<div style="font-size:12.5px;font-weight:700;color:#92400E;margin-bottom:4px;">';
    if (p.type === 'shared_minor') {
      html += '🔁 "' + escapeHtml(p.shared_keyword) + '" 키워드 — ' + escapeHtml(p.major);
    } else {
      html += '🔁 그룹 크기 — ' + escapeHtml(p.major) + ' (중분류 ' + p.middle_count + '개)';
    }
    html += '</div>';
    html += '<div style="font-size:11px;color:#374151;line-height:1.5;">';
    html += '<div>' + escapeHtml(p.predicted_pattern || '') + '</div>';
    html += '<div style="margin-top:2px;color:#6B7280;">→ ' + escapeHtml(p.recommendation || '') + '</div>';
    if (p.shared_in_middles && p.shared_in_middles.length) {
      html += '<div style="margin-top:4px;font-size:10.5px;color:#6B7280;">└ 영향 중분류: ' + p.shared_in_middles.map(escapeHtml).join(', ') + '</div>';
    }
    html += '</div>';
    html += '</div>';
  });
  html += '</div>';

  // 액션 버튼
  html += '<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">';
  html += '<button onclick="autoMergeClassification()" style="padding:8px 14px;background:#10B981;color:#FFFFFF;border:none;border-radius:6px;font-size:12.5px;font-weight:700;cursor:pointer;">🔁 분류표 자동 정리</button>';
  html += '<button onclick="dismissClassifyDuplicateNotice()" style="padding:8px 14px;background:#FFFFFF;color:#92400E;border:1.5px solid #FCD34D;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;">✕ 무시 (그대로 진행)</button>';
  html += '<span style="font-size:11px;color:#78350F;margin-left:6px;">자동 정리 실패 시 미니 채팅에서 직접 수정 가능합니다.</span>';
  html += '</div>';

  el.innerHTML = html;
  el.style.display = '';
}

function dismissClassifyDuplicateNotice() {
  var el = document.getElementById('classifyDuplicateNotice');
  if (el) el.style.display = 'none';
}

async function autoMergeClassification() {
  var prediction = window._classifyPrediction;
  if (!prediction || !prediction.predictions || prediction.predictions.length === 0) {
    alert('통합할 예측 정보가 없습니다.');
    return;
  }
  if (!currentSid) { alert('세션이 없습니다.'); return; }
  if (!confirm('AI 가 분류표를 정리합니다.\\n비기능 소분류(네트워크/타임아웃/로딩 등)를 그룹 대표 화면 1개에 통합합니다.\\n계속할까요?')) return;

  var notice = document.getElementById('classifyDuplicateNotice');
  if (notice) {
    notice.innerHTML = '<div style="display:flex;align-items:center;gap:10px;color:#92400E;font-size:13px;font-weight:600;">⏳ AI 가 분류표를 정리하고 있어요... (10~30초)</div>';
  }

  try {
    var currentDoc = document.getElementById('gateContent').value || '';
    var r = await fetch('/merge-classification/' + currentSid, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_doc: currentDoc,
        predictions: prediction.predictions,
      }),
    });
    var d = await r.json();
    if (!d.ok) {
      alert('분류표 정리 실패: ' + (d.error || 'unknown'));
      // 알림 박스 복원
      renderClassifyDuplicateNotice(prediction);
      return;
    }
    // 분류표 갱신
    document.getElementById('gateContent').value = d.updated_doc;
    renderGateViewer(d.updated_doc);
    // 미니 채팅에 안내 메시지 추가
    if (typeof addGateChatMsg === 'function') {
      addGateChatMsg('system', '✅ 분류표 자동 정리 완료 — ' + (d.predictions_resolved || 0) + '개 패턴 처리. ' + (d.reply || ''));
    }
    // 알림 박스 → 녹색 완료 표시로 변경
    if (notice) {
      notice.style.background = '#ECFDF5';
      notice.style.borderColor = '#6EE7B7';
      notice.innerHTML = '<div style="display:flex;align-items:center;gap:10px;color:#065F46;font-size:13px;">';
      notice.innerHTML += '<span style="font-size:18px;">✅</span>';
      notice.innerHTML += '<div><strong>분류표 자동 정리 완료</strong><br>';
      notice.innerHTML += '<span style="font-size:11.5px;">' + escapeHtml(d.reply || '') + ' 분류표를 검토 후 승인하세요.</span></div>';
      notice.innerHTML += '</div>';
    }
    showToast('✅ 분류표 자동 정리 완료', 'success');
  } catch (e) {
    alert('네트워크 오류: ' + e.message);
    renderClassifyDuplicateNotice(prediction);
  }
}

function renderSourceScrNotice(scrMap) {
  var el = document.getElementById('sourceScrNotice');
  if (!el) return;
  scrMap = scrMap || {};
  var entries = Object.entries(scrMap);
  if (entries.length === 0) {
    // 입력 소스에서 화면 식별자 발견 못함 — 빈 칸 정책 안내
    el.style.display = '';
    el.style.background = '#FEF3C7';
    el.style.border = '1px solid #FCD34D';
    el.style.color = '#78350F';
    el.innerHTML =
      '<strong>📌 화면 코드 안내</strong> — ' +
      '입력 소스에서 화면 식별자(<code style="background:#FFFFFF;padding:1px 5px;border-radius:3px;">SCR-NNN</code> 형식)가 발견되지 않았습니다. ' +
      '<br>Excel 의 <strong>화면 코드</strong> 컬럼은 <strong>빈 칸</strong>으로 출력됩니다 (정상). ' +
      '식별자가 필요하면 입력 파일명을 <code style="background:#FFFFFF;padding:1px 5px;border-radius:3px;">SCR-001.md</code> 형식으로 변경하거나, 본문 H1 에 <code style="background:#FFFFFF;padding:1px 5px;border-radius:3px;">SCR-001:</code> 처럼 명시하세요.';
  } else {
    // 매핑 발견됨 — 사용자에게 안내
    el.style.display = '';
    el.style.background = '#ECFDF5';
    el.style.border = '1px solid #6EE7B7';
    el.style.color = '#065F46';
    var rows = entries.map(function(kv) {
      return '<code style="background:#FFFFFF;padding:1px 5px;border-radius:3px;font-size:11px;">' + kv[0] + '</code> → <strong>' + kv[1] + '</strong>';
    }).join(' &nbsp;·&nbsp; ');
    el.innerHTML =
      '<strong>📌 입력 소스 화면 코드 매핑 (' + entries.length + '개)</strong><br>' +
      rows +
      '<br><span style="font-size:11px;opacity:0.85;">생성된 TC 의 <strong>화면 코드</strong> 컬럼은 위 매핑을 따릅니다. 임의 추론 없음.</span>';
  }
}

// ── Human Gate 채팅 ──────────────────────────────────────────────────────────
let gateChatHistory = [];  // [{role, content}, ...]

function initGateChat(docContent) {
  // 문서 저장
  document.getElementById('gateContent').value = docContent;
  // 승인 버튼 상태 리셋
  var approveBtn = document.querySelector('#card3 .btn-success');
  if (approveBtn) { approveBtn.disabled = false; approveBtn.textContent = '✅ 승인 및 TC 생성 시작'; }
  setStopButtonsDisabled(false);
  // SuiteCode 섹션 초기화 (새 분류표마다 리셋)
  var suiteSection = document.getElementById('suiteCodeSection');
  if (suiteSection) { suiteSection.innerHTML = ''; suiteSection.style.display = 'none'; }
  // Viewer 렌더링
  renderGateViewer(docContent);
  // 채팅 초기화
  gateChatHistory = [];
  const msgs = document.getElementById('gateChatMessages');
  msgs.innerHTML = '';
  addGateChatMsg('assistant',
    'AI가 문서를 준비했습니다. 수정이 필요한 부분을 채팅으로 알려주세요. ' +
    '예) "AUTH 대분류의 비밀번호 변경 케이스 삭제해줘" / "PROD 대분류 이름을 상품관리로 바꿔줘"');
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
  // 결과 구조 (중분류별 그룹핑 — A안):
  //   [{
  //     major: '대분류 이름',
  //     middle: '중분류 이름',
  //     minors: ['소분류 1', '소분류 2', ...]
  //   }, ...]
  // 소분류는 다음 두 가지 패턴 모두 지원:
  //   1. `#### 소분류` 헤더 + 그 아래 `- 항목: 설명` 불릿
  //   2. `### 중분류` 직후 바로 `- 항목` 불릿 (헤더 없음)
  // `#### 소분류` 헤더 자체는 데이터가 아니므로 제외.
  var lines = mdText.split('\\n');
  var rows = [];
  var curMajor = '';
  var curMiddle = '';
  var curMinors = [];
  var inMinorSection = false;  // `#### 소분류` 헤더 직후 여부

  function flushMiddle() {
    if (curMajor && curMiddle) {
      rows.push({ major: curMajor, middle: curMiddle, minors: curMinors });
    }
    curMiddle = '';
    curMinors = [];
    inMinorSection = false;
  }

  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    // 대분류
    if (line.match(/^##\s+/) && !line.match(/^###\s+/)) {
      flushMiddle();
      curMajor = line.replace(/^##\s+/, '').replace(/\*\*/g, '').replace(/^대분류[:\s]*/, '').trim();
    }
    // 중분류
    else if (line.match(/^###\s+/) && !line.match(/^####\s+/)) {
      flushMiddle();
      curMiddle = line.replace(/^###\s+/, '').replace(/\*\*/g, '').replace(/^중분류[:\s]*/, '').trim();
      inMinorSection = false;
    }
    // 소분류 섹션 헤더 — '#### 소분류' 같은 헤더는 그 자체로 데이터 아님
    else if (line.match(/^####\s+/)) {
      inMinorSection = true;
    }
    // 불릿 항목 — 중분류 안에 있을 때만 소분류로 수집
    else if ((line.startsWith('- ') || line.startsWith('* ')) && curMiddle) {
      var txt = line.replace(/^[-*]\s+/, '').replace(/\*\*/g, '').trim();
      if (txt) curMinors.push(txt);
    }
  }
  flushMiddle();
  return rows;
}

function updateTcIdPreview(input) {
  // SuiteCode 모드: 같은 대분류(domIdx)에 속한 모든 미리보기 셀에 동일 코드 적용
  var code = input.value.trim().toUpperCase();
  var pcode = input.dataset.pcode || 'SC';
  // System Generated 모드면 사용자가 SuiteCode 바꿔도 ScreenCode 자동 적용이 우선 — 무시
  if (window._autoScreenCode) return;
  // 입력 input의 행을 기준으로, 다음 SuiteCode input(다음 대분류 행)을 만나기 전까지의 모든
  // tcIdPreview_* 셀에 적용
  var row = input.closest('tr');
  if (!row || !row.parentNode) return;
  var rows = Array.prototype.slice.call(row.parentNode.children);
  var startIdx = rows.indexOf(row);
  for (var i = startIdx; i < rows.length; i++) {
    var r = rows[i];
    if (i > startIdx && r.querySelector('input.suite-code-input')) break;  // 다음 대분류 시작 — 중단
    var prev = r.querySelector('[id^="tcIdPreview_"]');
    if (prev) prev.textContent = code ? pcode + '-' + code + '-001' : '-';
  }
}

// ── Screen Code Map 캐시 (Auto 모드 미리보기용) ──
var _screenCodeMap = null;
var _screenCodeMapLoading = null;

async function loadScreenCodeMap(projectName) {
  if (_screenCodeMap) return _screenCodeMap;
  if (_screenCodeMapLoading) return _screenCodeMapLoading;
  _screenCodeMapLoading = fetch('/screen-code-map?project=' + encodeURIComponent(projectName || ''))
    .then(r => r.json())
    .then(d => {
      _screenCodeMap = d.ok ? d : { map: {}, project_code: 'SC', screen_based_default: false };
      _screenCodeMapLoading = null;
      return _screenCodeMap;
    })
    .catch(() => {
      _screenCodeMap = { map: {}, project_code: 'SC', screen_based_default: false };
      _screenCodeMapLoading = null;
      return _screenCodeMap;
    });
  return _screenCodeMapLoading;
}

// Middle name → ScreenCode 프론트엔드 해석 (백엔드 resolve_screen_code와 동일 규칙, v0.9.7b)
// 규칙:
//   - 1단어:     앞 3자
//   - 2단어:     각 단어 앞 2자 연결
//   - 3단어 이상: 앞 단어들 2자 + 마지막 단어 1자
//   - 최대 8자 절단, 대문자화
// 충돌 처리는 백엔드에서만 수행 — FE 미리보기는 기본 파생값만 표시.
function resolveScreenCodeFE(middleName, screenMap) {
  if (!middleName) return 'SCR';
  if (screenMap && screenMap[middleName]) {
    var e = screenMap[middleName];
    if (typeof e === 'object' && e) return e.code || 'SCR';
    return e;
  }
  var words = String(middleName).split(/[\s\-_]+/)
    .map(function(w) { return w.replace(/[^A-Za-z]/g, ''); })
    .filter(function(w) { return w.length > 0; });
  if (words.length === 0) {
    var h = 0;
    for (var i = 0; i < middleName.length; i++) {
      h = ((h << 5) - h) + middleName.charCodeAt(i);
      h = h & h;
    }
    return 'MID' + String(Math.abs(h) % 1000).padStart(3, '0');
  }
  var base;
  if (words.length === 1) {
    base = words[0].substring(0, 3);
  } else if (words.length === 2) {
    base = words[0].substring(0, 2) + words[1].substring(0, 2);
  } else {
    // 3단어 이상: 앞 단어들 앞 2자 + 마지막 단어 앞 1자
    var head = words.slice(0, -1).map(function(w) { return w.substring(0, 2); }).join('');
    var tail = words[words.length - 1].substring(0, 1);
    base = head + tail;
  }
  return base.substring(0, 8).toUpperCase();
}

// 중분류명 정제
function cleanMiddleName(raw) {
  return String(raw || '').replace(/중분류[:\s]*/g, '').replace(/\(.*?\)/g, '').trim();
}

// 통합 TC ID 모드 설정 — 상단 독립 패널의 체크박스 핸들러
// (기존 toggleAutoScreenCode는 이 함수의 alias로 유지)
function setTcIdMode(systemGenerated) {
  window._autoScreenCode = !!systemGenerated;

  // 상단 독립 패널 — 설명 텍스트 업데이트
  var desc = document.getElementById('tcIdModeDesc');
  if (desc) {
    if (systemGenerated) {
      desc.innerHTML =
        '✅ <strong style="color:#1D4ED8;">System Generated 모드 ON</strong> — ' +
        '시스템이 각 화면을 <code style="background:#FFFFFF;padding:1px 5px;border-radius:3px;border:1px solid #93C5FD;font-family:monospace;">screen_code_map.md</code>에 따라 ' +
        '<code style="background:#FFFFFF;padding:1px 5px;border-radius:3px;border:1px solid #93C5FD;font-family:monospace;">SM-SPL-001</code>, ' +
        '<code style="background:#FFFFFF;padding:1px 5px;border-radius:3px;border:1px solid #93C5FD;font-family:monospace;">SM-LGI-001</code> 식으로 ' +
        '자동 매핑합니다. 아래 SuiteCode 입력란은 비활성화됩니다.';
    } else {
      desc.innerHTML =
        '✏️ <strong style="color:#B45309;">Manual 모드</strong> — ' +
        '아래 <strong>TC 분류 요약</strong> 표에서 각 대분류의 <strong>SuiteCode</strong>를 직접 입력하세요. ' +
        '입력한 값으로 <code style="background:#FFFFFF;padding:1px 5px;border-radius:3px;border:1px solid #FCD34D;font-family:monospace;">SM-{SuiteCode}-001</code> 형태의 TC ID가 생성됩니다.';
    }
  }

  // 상단 패널 라벨 색상 표현
  var label = document.getElementById('tcIdModeLabel');
  if (label) {
    label.style.background = systemGenerated ? '#3B82F6' : '#FFFFFF';
    label.style.color = systemGenerated ? '#FFFFFF' : '#1E3A5F';
    label.style.borderColor = systemGenerated ? '#1D4ED8' : '#93C5FD';
  }

  // 분류 요약 테이블 내 체크박스도 동기화 (역순 동기화 루프 방지용 이벤트 없이 값만 설정)
  var innerToggle = document.getElementById('autoScreenCodeToggle');
  if (innerToggle && innerToggle.checked !== systemGenerated) {
    innerToggle.checked = systemGenerated;
  }

  // SuiteCode 입력란 활성/비활성 + 스타일
  var inputs = document.querySelectorAll('.suite-code-input');
  inputs.forEach(function(inp) {
    inp.disabled = systemGenerated;
    inp.style.opacity = systemGenerated ? '0.4' : '1';
    inp.style.background = systemGenerated ? '#F3F4F6' : '#FFFFFF';
    inp.title = systemGenerated ? '자동 모드에서는 편집할 수 없습니다. 각 중분류는 screen_code_map에서 자동 매핑됩니다.' : '';
  });

  // 미리보기 재렌더
  var previewCells = document.querySelectorAll('[id^="tcIdPreview_"]');
  previewCells.forEach(function(cell) {
    var idx = cell.id.replace('tcIdPreview_', '');
    rerenderPreviewForRow(idx, systemGenerated);
  });

  // 헬프 문구 토글 (요약 테이블 내)
  var helpNormal = document.getElementById('suiteCodeHelpNormal');
  var helpAuto = document.getElementById('suiteCodeHelpAuto');
  if (helpNormal) helpNormal.style.display = systemGenerated ? 'none' : '';
  if (helpAuto) helpAuto.style.display = systemGenerated ? '' : 'none';
}

// ─ 분류 요약 표 — 소분류 행 개별/전체 토글 ─
function toggleMinorRow(idx) {
  var row = document.getElementById('minorRow_' + idx);
  var icon = document.getElementById('minorToggleIcon_' + idx);
  if (!row) return;
  var isHidden = row.style.display === 'none';
  row.style.display = isHidden ? '' : 'none';
  if (icon) icon.textContent = isHidden ? '▼' : '▶';
}

function toggleAllMinors(open) {
  // 모든 종속 행 일괄 토글
  var rows = document.querySelectorAll('.tc-summary-row-nested');
  rows.forEach(function(row) {
    row.style.display = open ? '' : 'none';
  });
  // 모든 토글 아이콘도 동기화
  var icons = document.querySelectorAll('[id^="minorToggleIcon_"]');
  icons.forEach(function(icon) {
    icon.textContent = open ? '▼' : '▶';
  });
}

// 기존 호환: 테이블 내 체크박스가 호출하는 함수 → 상단 토글과 동기화
function toggleAutoScreenCode(checkbox) {
  var topToggle = document.getElementById('tcIdModeToggle');
  if (topToggle) topToggle.checked = checkbox.checked;
  setTcIdMode(checkbox.checked);
}

function rerenderPreviewForRow(idx, auto) {
  // A안: 행마다 단일 중분류. data-middle 속성 사용.
  var cell = document.getElementById('tcIdPreview_' + idx);
  if (!cell) return;
  var pcode = cell.dataset.pcode || 'SC';
  if (auto) {
    // ScreenCode 자동 — 중분류 이름으로 코드 파생
    var mid = cell.dataset.middle || '';
    var mapData = (_screenCodeMap && _screenCodeMap.map) ? _screenCodeMap.map : {};
    if (!mid) {
      cell.textContent = '-';
    } else {
      var code = resolveScreenCodeFE(mid, mapData);
      cell.textContent = pcode + '-' + code + '-001';
    }
  } else {
    // Suite-based (수동): 같은 행/그룹의 SuiteCode input 값 사용
    // 행을 거슬러 올라가며 가장 가까운 SuiteCode input(같은 대분류 그룹) 검색
    var row = cell.closest('tr');
    var input = null;
    while (row) {
      input = row.querySelector('input.suite-code-input');
      if (input) break;
      row = row.previousElementSibling;
    }
    var code = input ? input.value.trim().toUpperCase() : '';
    cell.textContent = code ? pcode + '-' + code + '-001' : '-';
  }
}

function renderGateViewer(mdText) {
  var viewer = document.getElementById('gateViewer');
  // 분류 요약 카드
  var cats = extractCategorySummary(mdText);
  var summaryHtml = '';
  if (cats.length > 0) {
    var _projName = document.getElementById('projectName').value || '';
    var _pcode = _projName.toLowerCase().indexOf('mobile') >= 0 || _projName.indexOf('모바일') >= 0 ? 'SM' : 'SC';
    // Screen Code Map 비동기 로드 (렌더 후 상단 패널 모드 기준으로 미리보기 재렌더)
    loadScreenCodeMap(_projName).then(function(res) {
      // 상단 독립 패널 토글이 단일 소스 — 거기 상태 기준으로 미리보기 동기화
      var topToggle = document.getElementById('tcIdModeToggle');
      if (topToggle) {
        // 초기 기본값이 아직 결정 안 됐으면 screen_based_default 적용
        if (window._autoScreenCode === undefined) {
          window._autoScreenCode = !!(res && res.screen_based_default);
          topToggle.checked = window._autoScreenCode;
        }
        setTcIdMode(topToggle.checked);
      }
    });

    summaryHtml = '<details id="tcSummaryDetails" open style="background:#F0F9FF;border:1.5px solid #93C5FD;border-radius:10px;margin-bottom:16px;">';
    // <summary> 자체가 헤더 역할 — 클릭 시 펼침/접힘. list-style:none 으로 기본 마커 제거.
    summaryHtml += '<summary id="tcSummaryHeader" style="cursor:pointer;padding:14px 16px;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:10px;user-select:none;">';
    summaryHtml += '<div style="font-size:14px;font-weight:700;color:#1E3A5F;display:flex;align-items:center;gap:8px;">';
    summaryHtml += '<span id="tcSummaryToggleIcon" style="font-size:12px;color:#3B82F6;">▼</span>';
    summaryHtml += '<span>TC 분류 요약</span>';
    summaryHtml += '<span id="tcSummaryFoldHint" style="font-size:11px;color:#6B7280;font-weight:400;">(클릭하여 접기)</span>';
    summaryHtml += '</div>';
    // 자동 적용 토글 (우측) — summary 내부에서 클릭 시 details 토글되지 않도록 stopPropagation 추가
    summaryHtml += '<label onclick="event.stopPropagation();" style="display:inline-flex;align-items:center;gap:6px;font-size:12px;color:#1E3A5F;cursor:pointer;user-select:none;background:#FFFFFF;padding:5px 10px;border:1.5px solid #93C5FD;border-radius:6px;">';
    summaryHtml += '<input type="checkbox" id="autoScreenCodeToggle" onchange="toggleAutoScreenCode(this)" onclick="event.stopPropagation();" style="margin:0;cursor:pointer;">';
    summaryHtml += '<span>🤖 <strong>시스템 규칙 자동 적용</strong></span>';
    summaryHtml += '</label>';
    summaryHtml += '</summary>';
    // 본문 영역 (접히는 부분)
    summaryHtml += '<div style="padding:0 16px 14px 16px;">';
    // 도움말 — 모드별 2종 (display toggle)
    summaryHtml += '<div id="suiteCodeHelpNormal" style="font-size:12px;color:#4B5563;margin-bottom:10px;">각 대분류의 <strong>SuiteCode</strong>를 입력하세요. 순번(001, 002...)은 자동 생성됩니다.<br>예: SuiteCode에 <code style="background:#DBEAFE;padding:1px 4px;border-radius:3px;">GNBF</code> 입력 → TC ID: <code style="background:#DBEAFE;padding:1px 4px;border-radius:3px;">' + _pcode + '-GNBF-001</code> ...</div>';
    summaryHtml += '<div id="suiteCodeHelpAuto" style="display:none;font-size:12px;color:#4B5563;margin-bottom:10px;">🤖 <strong>시스템 규칙 자동 적용</strong> — 각 중분류(화면)가 <code style="background:#DBEAFE;padding:1px 4px;border-radius:3px;">screen_code_map.md</code>에 등록된 ScreenCode로 자동 매핑됩니다.<br>예: Splash → <code style="background:#DBEAFE;padding:1px 4px;border-radius:3px;">' + _pcode + '-SPL-001</code>, Login Options → <code style="background:#DBEAFE;padding:1px 4px;border-radius:3px;">' + _pcode + '-LGI-001</code> ... (화면별 독립 001~)</div>';
    // 표 상단 컨트롤 — 전체 펼치기/접기
    summaryHtml += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;gap:8px;flex-wrap:wrap;">';
    summaryHtml += '<div style="font-size:11px;color:#6B7280;">💡 각 중분류 행의 <strong>▼ 소분류</strong> 를 클릭하면 상세 항목이 펼쳐집니다.</div>';
    summaryHtml += '<div style="display:flex;gap:6px;">';
    summaryHtml += '<button type="button" onclick="toggleAllMinors(true)" style="padding:4px 10px;font-size:11px;background:#FFFFFF;color:#1E3A5F;border:1px solid #93C5FD;border-radius:6px;cursor:pointer;font-weight:600;">▼ 전체 펼치기</button>';
    summaryHtml += '<button type="button" onclick="toggleAllMinors(false)" style="padding:4px 10px;font-size:11px;background:#FFFFFF;color:#1E3A5F;border:1px solid #93C5FD;border-radius:6px;cursor:pointer;font-weight:600;">▶ 전체 접기</button>';
    summaryHtml += '</div></div>';
    summaryHtml += '<table class="tc-summary-table" style="width:100%;border-collapse:collapse;font-size:12px;">';
    summaryHtml += '<tr style="background:#DBEAFE;">';
    summaryHtml += '<th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;">시트명 (Excel)</th>';
    summaryHtml += '<th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;">SuiteCode</th>';
    summaryHtml += '<th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;">TC ID 미리보기</th>';
    summaryHtml += '<th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;">대분류</th>';
    summaryHtml += '<th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;">중분류 (화면)</th>';
    summaryHtml += '<th style="padding:6px 8px;text-align:left;border:1px solid #93C5FD;width:130px;">소분류</th>';
    summaryHtml += '</tr>';
    // 옵션 E: 메인 행(시트/Suite/TC ID/대분류/중분류 + 소분류 토글) + 종속 행(소분류 상세, colspan=6)
    var prevMajor = null;
    var groupCount = 0;
    var totalMiddles = cats.length;
    var majorIndex = -1;
    var seenMajors = {};
    for (var ci = 0; ci < cats.length; ci++) {
      var c = cats[ci];
      var majorClean = c.major;
      var midClean = (c.middle || '').trim();
      var minorList = (c.minors || []).filter(function(m){ return m && m.trim(); });
      var minorCount = minorList.length;

      var isFirstOfMajor = !(majorClean in seenMajors);
      if (isFirstOfMajor) {
        majorIndex++;
        seenMajors[majorClean] = majorIndex;
      }
      var domIdx = seenMajors[majorClean];

      var sheetName = majorClean;
      var autoCode = majorClean.replace(/[^A-Za-z]/g, '').toUpperCase().substring(0, 4);
      var screenCode = resolveScreenCodeFE(midClean, {});
      var previewId = _pcode + '-' + screenCode + '-001';

      var bg = ci % 2 === 0 ? '#F8FAFC' : '#FFFFFF';
      var nestedBg = ci % 2 === 0 ? '#F1F5F9' : '#F8FAFC';  // 종속 행은 살짝 더 어둡게
      // ─ 메인 행 (기본 정보) ─
      summaryHtml += '<tr class="tc-summary-row-main" style="background:' + bg + ';">';
      if (isFirstOfMajor) {
        summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;font-weight:700;color:#1E3A5F;">' + _escapeHtml(sheetName) + '</td>';
        summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;"><input type="text" class="suite-code-input" data-domain="' + domIdx + '" data-pcode="' + _pcode + '" value="' + autoCode + '" placeholder="예: GNBF" oninput="updateTcIdPreview(this)" style="width:80px;padding:4px 6px;border:1.5px solid #93C5FD;border-radius:4px;font-size:12px;font-weight:700;text-transform:uppercase;font-family:monospace;"></td>';
      } else {
        summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;color:#9CA3AF;font-size:11px;">↳ 동일 시트</td>';
        summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;color:#9CA3AF;">↳</td>';
      }
      summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;font-family:monospace;font-size:11px;color:#1D4ED8;" id="tcIdPreview_' + ci + '" data-pcode="' + _pcode + '" data-middle="' + _escapeHtml(midClean) + '">' + previewId + '</td>';
      summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;">' + (isFirstOfMajor ? _escapeHtml(majorClean) : '<span style="color:#9CA3AF;">↳</span>') + '</td>';
      summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;font-weight:600;">' + _escapeHtml(midClean) + '</td>';
      // 소분류 토글 셀
      if (minorCount > 0) {
        summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;text-align:center;cursor:pointer;user-select:none;" onclick="toggleMinorRow(' + ci + ')" title="클릭하여 소분류 펼치기/접기">';
        summaryHtml += '<span id="minorToggleIcon_' + ci + '" style="color:#3B82F6;font-weight:700;">▼</span> ';
        summaryHtml += '<span style="color:#1E3A5F;font-weight:600;font-size:11px;">' + minorCount + '개</span>';
        summaryHtml += '</td>';
      } else {
        summaryHtml += '<td style="padding:5px 8px;border:1px solid #D1D5DB;text-align:center;color:#9CA3AF;font-size:11px;">없음</td>';
      }
      summaryHtml += '</tr>';
      // ─ 종속 행 (소분류 상세) — 펼침 상태로 시작 (open) ─
      if (minorCount > 0) {
        var minorText = minorList.map(function(m){
          return '<li style="margin-bottom:4px;">' + _escapeHtml(m) + '</li>';
        }).join('');
        summaryHtml += '<tr class="tc-summary-row-nested" id="minorRow_' + ci + '" style="background:' + nestedBg + ';">';
        summaryHtml += '<td colspan="6" style="padding:0;border:1px solid #D1D5DB;border-top:none;">';
        summaryHtml += '<div style="padding:8px 12px 10px 28px;color:#374151;line-height:1.6;">';
        summaryHtml += '<div style="font-size:10.5px;color:#6B7280;font-weight:600;margin-bottom:4px;letter-spacing:0.3px;">↳ 소분류 (' + minorCount + ')</div>';
        summaryHtml += '<ul style="margin:0;padding:0 0 0 14px;list-style:disc;">' + minorText + '</ul>';
        summaryHtml += '</div></td></tr>';
      }
    }
    summaryHtml += '</table>';
    var estMin = totalMiddles * 5;
    var estMax = totalMiddles * 15;
    summaryHtml += '<div style="margin-top:10px;padding:8px 12px;background:#F0FDF4;border:1px solid #86EFAC;border-radius:8px;font-size:12px;color:#166534;display:flex;align-items:center;gap:8px;">';
    summaryHtml += '<span style="font-size:16px;">📊</span>';
    summaryHtml += '<span>예상 TC 수량: <strong>' + estMin + '~' + estMax + '개</strong> (중분류 ' + totalMiddles + '개 × 5~15개)</span>';
    summaryHtml += '</div>';
    summaryHtml += '</div>';   // 본문 div close
    summaryHtml += '</details>';  // 외부 details close
  }
  // 메인 영역(Viewer = gateViewer)에는 통합 표 + 분류표 헤더 표시 (옵션 A — 표 중심)
  var headerLine = '<div style="font-size:13px;color:var(--muted);margin-bottom:10px;">📋 분류표 결과 — 채팅으로 수정하거나 SuiteCode를 입력한 후 승인하세요.</div>';
  var fallbackHtml = '';
  if (!summaryHtml) {
    // 표를 만들 수 없으면 raw 마크다운을 즉시 보여주기 (토글 안 해도 보이게)
    fallbackHtml = '<div style="padding:14px; background:#FEF3C7; border:1px solid #FCD34D; border-radius:8px; font-size:12px; color:#92400E; margin-bottom:10px;">⚠️ 분류표 구조 자동 인식 실패 — 아래 원본 문서를 확인하시거나, AI에게 "표 형식으로 다시 정리해줘"로 요청하세요.</div>';
    fallbackHtml += '<pre style="margin:0; padding:14px; background:#FAFAFA; border:1px solid #E5E7EB; border-radius:6px; font-size:12px; line-height:1.7; max-height:400px; overflow:auto; white-space:pre-wrap; word-break:break-word; font-family:ui-monospace,SFMono-Regular,Menlo,monospace;">' + _escapeHtml(mdText) + '</pre>';
  }
  viewer.innerHTML = headerLine + (summaryHtml || fallbackHtml);
  viewer.classList.add('gate-doc-updated');
  setTimeout(() => viewer.classList.remove('gate-doc-updated'), 700);

  // 원본 마크다운은 토글 영역(rawDocContent)에 별도 렌더 — 펼쳐진 상태일 때만 사용자가 봄
  var rawCell = document.getElementById('rawDocContent');
  if (rawCell) rawCell.textContent = mdText;
  var rawBadge = document.getElementById('rawDocBadge');
  if (rawBadge) rawBadge.textContent = '최근 업데이트: ' + new Date().toLocaleTimeString();

  // 레거시: suiteCodeSection은 더 이상 사용하지 않지만 안전상 비워둠
  var suiteSection = document.getElementById('suiteCodeSection');
  if (suiteSection) {
    suiteSection.innerHTML = '';
    suiteSection.style.display = 'none';
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
      // 히스토리 추가 (컨텍스트 유지용 — 축약 버전)
      gateChatHistory.push({ role: 'user', content: '요청: ' + msg });
      gateChatHistory.push({ role: 'assistant', content: d.reply });
      // v0.9.20: 변경 여부에 따라 다른 메시지
      var statusMsg = '';
      if (d.changed) {
        statusMsg = '✅ 분류표가 업데이트되었습니다. 아래 표에서 확인하세요.';
        if (d.sync_status === 'synced') {
          statusMsg += ' 본문 정책·기능 문서도 자동 동기화 완료 — TC 작성 시 일관됨.';
        } else if (d.sync_status === 'failed') {
          statusMsg += ' (⚠️ 본문 동기화 실패 — 분류표 변경만 반영됨.)';
        }
      } else if (d.truncated) {
        statusMsg = '⚠️ AI 응답이 너무 길어 잘렸습니다. 분류표는 변경되지 않았어요. 더 작은 단위로 나눠 다시 요청해 주세요.';
      } else {
        // 변경 없음 — 명령이 모호했거나 AI 가 질문으로 해석한 경우
        statusMsg = 'ℹ️ 분류표가 변경되지 않았습니다. 요청이 모호했을 수 있어요. 더 명확하게 다시 요청해 주세요. (예: "Splash 중분류 삭제해줘", "AUTH 대분류의 3번 케이스 삭제")';
      }
      addGateChatMsg('system', statusMsg);
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
    document.getElementById('card1').classList.add('hidden');
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

// ── Excel 출력 옵션 (Full / Light / Custom) ──
const EXCEL_PRESETS = {
  full:   { cover:true,  stats:true,  smoke:true,  traceability:true,  tc_list:true, change_history:true },
  light:  { cover:false, stats:false, smoke:false, traceability:false, tc_list:true, change_history:false },
  // custom 은 마지막 사용자 체크 상태 그대로 — localStorage 에서 복원
};

function onExcelPresetChange() {
  const preset = document.querySelector('input[name="excelPreset"]:checked')?.value || 'full';
  const customPanel = document.getElementById('excelCustomPanel');
  if (preset === 'custom') {
    customPanel.style.display = '';
    // Custom 진입 시 마지막 저장된 체크 상태 복원
    try {
      const saved = JSON.parse(localStorage.getItem('tc_excel_custom_sheets') || 'null');
      if (saved) applySheetChecks(saved);
    } catch (_) {}
  } else {
    customPanel.style.display = 'none';
    // 프리셋 → 체크박스 동기화 (시각화)
    applySheetChecks(EXCEL_PRESETS[preset]);
  }
  updateExcelSheetSummary();
  // 사용자 선택 저장
  try { localStorage.setItem('tc_excel_preset', preset); } catch (_) {}
}

function onExcelSheetCheckChange() {
  // 체크박스 직접 변경 시 — 자동으로 Custom 모드로 전환
  const customRadio = document.querySelector('input[name="excelPreset"][value="custom"]');
  if (customRadio && !customRadio.checked) {
    customRadio.checked = true;
    document.getElementById('excelCustomPanel').style.display = '';
  }
  updateExcelSheetSummary();
  // Custom 체크 상태 저장
  try {
    localStorage.setItem('tc_excel_custom_sheets', JSON.stringify(collectExcelSheets()));
    localStorage.setItem('tc_excel_preset', 'custom');
  } catch (_) {}
}

function applySheetChecks(sheets) {
  document.querySelectorAll('.excel-sheet-cb').forEach(function(cb) {
    const key = cb.dataset.sheet;
    if (key === 'tc_list') return;  // 필수 — 건드리지 않음
    if (cb.disabled) return;
    if (key in sheets) cb.checked = !!sheets[key];
  });
}

function collectExcelSheets() {
  const sheets = {};
  document.querySelectorAll('.excel-sheet-cb').forEach(function(cb) {
    sheets[cb.dataset.sheet] = !!cb.checked;
  });
  sheets.tc_list = true;  // 강제
  return sheets;
}

function updateExcelSheetSummary() {
  const sheets = collectExcelSheets();
  const labels = {
    cover:'표지', stats:'통계', smoke:'Smoke',
    traceability:'Traceability', tc_list:'TC 목록', change_history:'변경 이력',
  };
  const enabled = Object.keys(sheets).filter(k => sheets[k]);
  const el = document.getElementById('excelSheetSummary');
  if (!el) return;
  if (enabled.length === Object.keys(labels).length) {
    el.innerHTML = '💡 요약: <strong>전체 시트 (' + enabled.length + '개)</strong>';
  } else {
    el.innerHTML = '💡 요약: <strong>' + enabled.map(k => labels[k]).join(' + ') + ' = ' + enabled.length + '개 시트</strong>';
  }
}

function getSelectedExcelSheets() {
  // approveGate 가 호출 — 현재 선택된 sheets dict 반환
  const preset = document.querySelector('input[name="excelPreset"]:checked')?.value || 'full';
  if (preset === 'full' || preset === 'light') {
    return { ...EXCEL_PRESETS[preset] };
  }
  return collectExcelSheets();
}

// 페이지 로드 시 — localStorage 에서 마지막 선택 복원
function restoreExcelOption() {
  try {
    const lastPreset = localStorage.getItem('tc_excel_preset') || 'full';
    const r = document.querySelector('input[name="excelPreset"][value="' + lastPreset + '"]');
    if (r) { r.checked = true; }
    if (lastPreset === 'custom') {
      const saved = JSON.parse(localStorage.getItem('tc_excel_custom_sheets') || 'null');
      if (saved) applySheetChecks(saved);
      document.getElementById('excelCustomPanel').style.display = '';
    } else {
      applySheetChecks(EXCEL_PRESETS[lastPreset] || EXCEL_PRESETS.full);
    }
    updateExcelSheetSummary();
  } catch (_) {}
}
// DOM ready 후 1회 복원
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', function() {
    try { restoreExcelOption(); } catch(e) {}
  });
}

async function approveGate() {
  if (!currentSid) return;
  const content = document.getElementById('gateContent').value.trim();
  if (!content) { alert('내용이 비어있습니다.'); return; }

  // Auto 모드 여부 (체크박스 상태)
  var autoScreenCode = !!window._autoScreenCode;

  // SuiteCode 수집
  var suiteCodeInputs = document.querySelectorAll('.suite-code-input');
  var suiteCodes = {};
  var hasEmpty = false;
  suiteCodeInputs.forEach(function(input) {
    var code = input.value.trim().toUpperCase();
    if (!code) hasEmpty = true;
    suiteCodes[input.dataset.domain] = code;
  });
  // Auto 모드에서는 SuiteCode 입력 검증 생략 (screen_code_map이 중분류별로 자동 매핑)
  if (!autoScreenCode && suiteCodeInputs.length > 0 && hasEmpty) {
    alert('모든 대분류의 SuiteCode를 입력해주세요.\\n(또는 "🤖 시스템 규칙 자동 적용" 체크박스를 켜면 자동 매핑됩니다.)'); return;
  }
  // SuiteCode 목록 (순서대로) — Auto 모드에서도 백엔드 로그 표시용으로 전송
  var suiteCodeList = [];
  for (var i = 0; i < suiteCodeInputs.length; i++) {
    suiteCodeList.push(suiteCodeInputs[i].value.trim().toUpperCase().replace(/^-+|-+$/g, ''));
  }

  // 대분류 선택 UI는 제거됨 — 범위 제한은 Step 1의 "TC 생성 범위"(focus_area)로 일원화
  // selected_domains는 항상 null(=전체) 전송. 백엔드 하위 호환 유지.
  const selectedDomains = null;

  const approveBtn = document.querySelector('#card3 .btn-success');
  approveBtn.disabled = true;
  approveBtn.textContent = '⏳ 처리 중...';

  var codeMsg;
  if (autoScreenCode) {
    codeMsg = ' (🤖 시스템 규칙 자동 적용 — 화면별 ScreenCode로 자동 매핑)';
  } else {
    codeMsg = suiteCodeList.length > 0 ? ' (SuiteCode: ' + suiteCodeList.join(', ') + ')' : '';
  }
  const scopeMsg = '분류표 전체 범위로 TC를 생성합니다.' + codeMsg + ' 계속할까요?';
  if (!confirm(scopeMsg)) {
    approveBtn.disabled = false;
    approveBtn.textContent = '✅ 승인 및 TC 생성 시작';
    return;
  }

  try {
    const resp = await fetch('/approve/' + currentSid, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content,
        selected_domains: selectedDomains,
        suite_codes: suiteCodeList,
        auto_screen_code: autoScreenCode,
        excel_sheets: getSelectedExcelSheets()
      })
    });
    const data = await resp.json();
    if (data.ok) {
      // Gate 닫고 파이프라인 카드로 복귀 — 이후 TC 작성/빌드 로그는 card2에서 계속 표시
      document.getElementById('card1').classList.add('hidden');
      document.getElementById('card3').classList.add('hidden');
      document.getElementById('card2').classList.remove('hidden');
      document.getElementById('stageLabel').textContent = 'TC 작성 시작...';
      setStepBar(4);
      document.getElementById('card2').scrollIntoView({ behavior: 'smooth', block: 'start' });
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
  ['stopBtn2', 'stopBtn3'].forEach(id => {
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
  btn.innerHTML = '⏳ 인증 확인 중...';
  // 1. 인증 상태 확인
  try {
    const sr = await fetch('/drive/status');
    const sd = await sr.json();
    if (!sd.ok || !sd.authenticated) {
      if (sd.need_credentials) {
        openDriveModal();
        btn.innerHTML = '⚠️ Drive 연동 설정 필요';
        btn.style.borderColor = '#e53e3e';
        btn.style.color = '#e53e3e';
        btn.disabled = false;
        return;
      }
      // 토큰 만료 → 백엔드에서 재인증 필요 (get_drive_service 내부에서 브라우저 열림)
      btn.innerHTML = '⏳ 로그인 창이 열립니다...';
      showToast('Google 로그인이 필요합니다. 브라우저 창에서 로그인을 완료하세요.', 'info');
      // drive/status 재호출로 인증 유도
      await fetch('/drive/status');
      btn.innerHTML = DRIVE_SVG + ' Google Drive에 올리기';
      btn.disabled = false;
      showToast('로그인 완료 후 다시 Drive 버튼을 눌러주세요.');
      return;
    }
    // 2. 폴더 선택 모달 열기
    openDriveFolderModal(sd.email || '');
    btn.innerHTML = DRIVE_SVG + ' Google Drive에 올리기';
    btn.disabled = false;
  } catch(e) {
    showToast('❌ 오류: ' + e.message, 'error');
    btn.innerHTML = DRIVE_SVG + ' Google Drive에 올리기';
    btn.disabled = false;
  }
}

async function openDriveFolderModal(email) {
  const modal = document.getElementById('drive-folder-modal');
  modal.classList.add('open');
  document.getElementById('driveFolderEmail').textContent = email ? '로그인 계정: ' + email : '';
  document.getElementById('driveFolderSearch').value = '';
  await loadDriveFolders('');
  document.getElementById('driveFolderSearch').focus();
}

function closeDriveFolderModal() {
  document.getElementById('drive-folder-modal').classList.remove('open');
}

async function loadDriveFolders(query) {
  const list = document.getElementById('driveFolderList');
  list.innerHTML = '<div style="padding:20px;text-align:center;color:#888;">⏳ 폴더 조회 중...</div>';
  try {
    const url = '/drive/folders' + (query ? '?q=' + encodeURIComponent(query) : '');
    const r = await fetch(url);
    const d = await r.json();
    if (!d.ok) {
      list.innerHTML = '<div style="padding:20px;color:#c53030;">❌ ' + (d.error || '폴더 조회 실패') + '</div>';
      return;
    }
    if (d.folders.length === 0) {
      list.innerHTML = '<div style="padding:20px;text-align:center;color:#888;">검색 결과 없음</div>';
      return;
    }
    list.innerHTML = '';
    d.folders.forEach(function(f) {
      var div = document.createElement('div');
      div.className = 'drive-folder-item';
      div.onclick = function(e) { selectDriveFolder(f.id, f.name, e.currentTarget); };
      div.innerHTML = '<span style="font-size:18px;">📁</span> <span style="flex:1;">' + f.name + '</span>' +
        '<span style="font-size:11px;color:#888;">' + (f.modifiedTime || '').substring(0, 10) + '</span>';
      list.appendChild(div);
    });
  } catch(e) {
    list.innerHTML = '<div style="padding:20px;color:#c53030;">❌ ' + e.message + '</div>';
  }
}

let _selectedDriveFolder = null;
function selectDriveFolder(id, name, element) {
  _selectedDriveFolder = { id: id, name: name };
  document.querySelectorAll('.drive-folder-item').forEach(el => el.classList.remove('selected'));
  if (element) element.classList.add('selected');
  document.getElementById('driveUploadBtn').disabled = false;
  document.getElementById('driveSelectedFolder').textContent = '✓ 선택됨: ' + name;
}

// Drive 업로드 버튼을 원래 라벨/스타일로 복귀 — 새 결과 도착 또는 새 파이프라인 시작 시 호출
function resetDriveBtn() {
  const btn = document.getElementById('driveBtn');
  if (!btn) return;
  // SVG + "Google Drive에 올리기" 라벨 복원
  if (typeof DRIVE_SVG !== 'undefined') {
    btn.innerHTML = DRIVE_SVG + ' Google Drive에 올리기';
  } else {
    btn.textContent = 'Google Drive에 올리기';
  }
  btn.style.borderColor = '';
}

async function confirmDriveUpload() {
  if (!_selectedDriveFolder) { alert('폴더를 선택해주세요.'); return; }
  const uploadBtn = document.getElementById('driveUploadBtn');
  uploadBtn.disabled = true;
  uploadBtn.textContent = '⏳ 업로드 중...';
  try {
    const r = await fetch('/upload-to-drive', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sid: currentSid,
        filename: currentFilename,
        folder_id: _selectedDriveFolder.id
      })
    });
    const d = await r.json();
    if (d.ok) {
      closeDriveFolderModal();
      showToast('✅ "' + _selectedDriveFolder.name + '" 폴더에 업로드 완료!');
      const btn = document.getElementById('driveBtn');
      btn.innerHTML = DRIVE_SVG + ' Drive 업로드 완료';
      btn.style.borderColor = '#34a853';
      if (d.link) window.open(d.link, '_blank');
    } else {
      alert('❌ ' + d.error);
      uploadBtn.disabled = false;
      uploadBtn.textContent = '✅ 이 폴더에 업로드';
    }
  } catch(e) {
    alert('오류: ' + e.message);
    uploadBtn.disabled = false;
    uploadBtn.textContent = '✅ 이 폴더에 업로드';
  }
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
  document.getElementById('card1').classList.add('hidden');
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

// ── 서버 재시작 (헤더 버튼) ──
async function restartServer() {
  const btn = document.getElementById('btnRestartServer');
  const overlay = document.getElementById('restartOverlay');
  const status = document.getElementById('restartOverlayStatus');

  // 1) 활성 세션 확인 (사전 체크)
  let activeSessions = 0;
  try {
    const r = await fetch('/admin/status');
    const d = await r.json();
    activeSessions = d.active_sessions || 0;
  } catch (_) {}

  // 2) confirm 다이얼로그 (활성 세션 있으면 강한 경고)
  let msg = '서버를 재시작하시겠습니까?\\n\\n';
  msg += '• 코드 변경사항이 반영됩니다.\\n';
  msg += '• 진행 중인 SSE 연결이 모두 끊깁니다.\\n';
  if (activeSessions > 0) {
    msg = '⚠️ 진행 중인 작업이 ' + activeSessions + '개 있습니다!\\n\\n';
    msg += '재시작하면 진행 중인 TC 생성이 모두 중단되며,\\n';
    msg += '복원이 어려울 수 있습니다.\\n\\n';
    msg += '정말 재시작하시겠습니까?';
  }
  if (!confirm(msg)) return;

  // 3) 재시작 요청 (활성 세션이 있으면 force=1)
  btn.disabled = true;
  overlay.classList.add('visible');
  status.textContent = '재시작 요청 전송 중...';

  try {
    const url = '/admin/restart' + (activeSessions > 0 ? '?force=1' : '');
    const r = await fetch(url, { method: 'POST' });
    const d = await r.json();
    if (!d.ok) {
      overlay.classList.remove('visible');
      btn.disabled = false;
      alert('재시작 실패: ' + (d.message || d.error || 'unknown error'));
      return;
    }
  } catch (e) {
    // 네트워크 오류 — 이미 서버가 죽었을 수 있음 (정상 흐름)
    status.textContent = '서버가 종료되었습니다. 살아나길 기다리는 중...';
  }

  // 4) 서버 살아남 폴링 → 새 버전이면 reload
  pollServerAlive();
}

// 서버가 다시 살아날 때까지 폴링 (최대 30초)
async function pollServerAlive() {
  const status = document.getElementById('restartOverlayStatus');
  const startedAt = Date.now();
  const maxMs = 30 * 1000;
  let attempt = 0;
  const initialVersion = window._INITIAL_APP_VERSION || '';

  while (Date.now() - startedAt < maxMs) {
    attempt++;
    status.textContent = '서버 응답 확인 중... (시도 ' + attempt + ')';
    try {
      const r = await fetch('/admin/status', { cache: 'no-store' });
      if (r.ok) {
        const d = await r.json();
        const newVersion = d.version || '';
        // 버전이 바뀌었거나 동일해도 살아있음 → reload
        status.textContent = '✅ 서버 응답 감지: ' + newVersion + ' — 새로고침합니다.';
        await new Promise(r => setTimeout(r, 600));
        // 강제 reload (캐시 우회)
        window.location.reload();
        return;
      }
    } catch (_) {
      // 아직 죽어있음 — 계속 폴링
    }
    await new Promise(r => setTimeout(r, 800));
  }

  // 30초 초과 → 사용자에게 수동 새로고침 요청
  status.textContent = '⚠️ 30초 동안 응답 없음. 직접 새로고침해 주세요.';
}

// ── Sticky Mini AI 채팅 패널 (Step 3 분류 검토 전용) ──
// - 메인 #gateChatMessages 에서 메시지를 미러링하여 하단에서도 응답 즉시 확인 가능
// - 3가지 상태: collapsed(입력만) / expanded(메시지+입력) / modal(확대)
// - v0.9.12: 다국어 placeholder + 모달 리사이즈 지원
(function() {
  // ─ 다국어 placeholder ─
  // localStorage 'tc_ui_lang' 우선, 없으면 navigator.language 자동 감지
  const I18N = {
    ko: {
      placeholder: '예) AUTH 대분류 케이스 3번 삭제해줘 — Enter로 전송, Shift+Enter 줄바꿈',
      placeholderModal: '예) AUTH 대분류 케이스 3번 삭제해줘 — Enter로 전송, Shift+Enter 줄바꿈',
      labelMain: '💬 AI 도우미',
      labelHint: '표 검토 중에도 바로 대화하세요',
      btnLarge: '⛶ 크게',
      btnClose: '✕ 닫기',
      modalTitle: '💬 AI 도우미 — 분류표 검토',
      empty: '아직 대화가 없어요. 아래에서 요청을 입력해보세요.',
    },
    en: {
      placeholder: 'e.g. Delete AUTH domain case #3 — Enter to send, Shift+Enter for newline',
      placeholderModal: 'e.g. Delete AUTH domain case #3 — Enter to send, Shift+Enter for newline',
      labelMain: '💬 AI Helper',
      labelHint: 'Chat anytime while reviewing the table',
      btnLarge: '⛶ Expand',
      btnClose: '✕ Close',
      modalTitle: '💬 AI Helper — Classification Review',
      empty: 'No conversation yet. Type a request below to start.',
    },
    ja: {
      placeholder: '例) AUTH ドメインのケース3を削除して — Enter で送信、Shift+Enter で改行',
      placeholderModal: '例) AUTH ドメインのケース3を削除して — Enter で送信、Shift+Enter で改行',
      labelMain: '💬 AI アシスタント',
      labelHint: '表を確認しながらいつでも対話',
      btnLarge: '⛶ 拡大',
      btnClose: '✕ 閉じる',
      modalTitle: '💬 AI アシスタント — 分類表レビュー',
      empty: 'まだ会話がありません。下に要求を入力してください。',
    },
    zh: {
      placeholder: '例) 删除 AUTH 域名案例 #3 — Enter 发送, Shift+Enter 换行',
      placeholderModal: '例) 删除 AUTH 域名案例 #3 — Enter 发送, Shift+Enter 换行',
      labelMain: '💬 AI 助手',
      labelHint: '审阅表格时随时对话',
      btnLarge: '⛶ 放大',
      btnClose: '✕ 关闭',
      modalTitle: '💬 AI 助手 — 分类表审阅',
      empty: '尚无对话。在下方输入请求开始。',
    },
  };
  function detectLang() {
    try {
      const saved = localStorage.getItem('tc_ui_lang');
      if (saved && I18N[saved]) return saved;
    } catch (_) {}
    const nav = (navigator.language || 'ko').toLowerCase();
    if (nav.startsWith('en')) return 'en';
    if (nav.startsWith('ja')) return 'ja';
    if (nav.startsWith('zh')) return 'zh';
    return 'ko';  // 기본값
  }
  const T = I18N[detectLang()];
  // 전역에 노출 — 다른 코드에서 언어 변경 시 호출 가능
  window.setStickyAiLang = function(lang) {
    if (!I18N[lang]) return false;
    try { localStorage.setItem('tc_ui_lang', lang); } catch(_) {}
    location.reload();
    return true;
  };
  // ─ DOM 구성 ─
  const bar = document.createElement('div');
  bar.id = 'floatingAiBar';
  bar.className = 'floating-ai-bar';
  bar.innerHTML =
    '<div class="floating-ai-header" id="floatingAiHeader">' +
      '<div class="floating-ai-header-label">' +
        '<span>' + T.labelMain + '</span>' +
        '<span class="floating-ai-msg-badge" id="floatingAiMsgBadge" style="display:none;">0</span>' +
        '<small>' + T.labelHint + '</small>' +
      '</div>' +
      '<button class="floating-ai-ctrl" id="floatingAiExpandBtn" title="' + T.btnLarge + '">' + T.btnLarge + '</button>' +
      '<button class="floating-ai-ctrl" id="floatingAiCollapseBtn" title="▾">▾</button>' +
    '</div>' +
    '<div class="floating-ai-messages" id="floatingAiMessages">' +
      '<div class="floating-ai-empty" id="floatingAiEmpty">' + T.empty + '</div>' +
    '</div>' +
    '<div class="floating-ai-inner">' +
      '<textarea class="floating-ai-input" id="floatingAiInput" rows="1" ' +
        'placeholder="' + T.placeholder + '"></textarea>' +
      '<button class="floating-ai-send" id="floatingAiSend">' + (detectLang() === 'ko' ? '전송' : detectLang() === 'en' ? 'Send' : detectLang() === 'ja' ? '送信' : '发送') + '</button>' +
    '</div>';
  document.body.appendChild(bar);

  // ─ 확대 모달 DOM ─
  const modal = document.createElement('div');
  modal.id = 'floatingAiModal';
  modal.className = 'floating-ai-modal';
  const sendLabel = detectLang() === 'ko' ? '전송' : detectLang() === 'en' ? 'Send' : detectLang() === 'ja' ? '送信' : '发送';
  modal.innerHTML =
    '<div class="floating-ai-modal-box" id="floatingAiModalBox">' +
      '<div class="floating-ai-modal-header">' +
        '<div class="floating-ai-modal-title">' + T.modalTitle + '</div>' +
        '<button class="floating-ai-modal-close" id="floatingAiModalClose">' + T.btnClose + '</button>' +
      '</div>' +
      '<div class="floating-ai-modal-messages" id="floatingAiModalMessages"></div>' +
      '<div class="floating-ai-modal-input-row">' +
        '<textarea class="floating-ai-input" id="floatingAiModalInput" rows="2" ' +
          'placeholder="' + T.placeholderModal + '" ' +
          'style="border-color:var(--border);"></textarea>' +
        '<button class="floating-ai-send" id="floatingAiModalSend">' + sendLabel + '</button>' +
      '</div>' +
      '<div class="floating-ai-modal-resize" id="floatingAiModalResize" title="크기 조절"></div>' +
    '</div>';
  document.body.appendChild(modal);

  const input = document.getElementById('floatingAiInput');
  const sendBtn = document.getElementById('floatingAiSend');
  const collapseBtn = document.getElementById('floatingAiCollapseBtn');
  const expandBtn = document.getElementById('floatingAiExpandBtn');
  const header = document.getElementById('floatingAiHeader');
  const miniMessages = document.getElementById('floatingAiMessages');
  const emptyMsg = document.getElementById('floatingAiEmpty');
  const msgBadge = document.getElementById('floatingAiMsgBadge');
  const modalMessages = document.getElementById('floatingAiModalMessages');
  const modalInput = document.getElementById('floatingAiModalInput');
  const modalSend = document.getElementById('floatingAiModalSend');
  const modalClose = document.getElementById('floatingAiModalClose');

  // 기본은 접힘 상태 — 사용자가 자주 쓰는 입력만 보임 (메시지는 헤더 클릭하면 펼침)
  bar.classList.add('collapsed');
  document.body.classList.add('has-floating-ai-collapsed');

  // 메인 입력창과 동기화하여 sendGateChat() 재사용
  async function submitFromInput(srcInput) {
    const msg = srcInput.value.trim();
    if (!msg) return;
    const mainInput = document.getElementById('gateChatInput');
    if (!mainInput) return;
    mainInput.value = msg;
    srcInput.value = '';
    sendBtn.disabled = true;
    modalSend.disabled = true;
    // 메시지를 보내는 순간 펼침 상태로 자동 전환 → 응답 보일 수 있게
    if (bar.classList.contains('collapsed')) toggleCollapsed(false);
    try {
      await sendGateChat();
    } finally {
      sendBtn.disabled = false;
      modalSend.disabled = false;
    }
  }
  sendBtn.addEventListener('click', () => submitFromInput(input));
  input.addEventListener('keydown', function(e) {
    // v0.9.24: IME (한글/일본어/중국어 등) 조합 중 Enter 무시
    // - keyCode === 229: 일부 브라우저에서 IME composition 중 표시
    // - e.isComposing: 표준 (Chrome/Firefox/Safari)
    if (e.isComposing || e.keyCode === 229) return;
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitFromInput(input);
    }
  });
  modalSend.addEventListener('click', () => submitFromInput(modalInput));
  modalInput.addEventListener('keydown', function(e) {
    if (e.isComposing || e.keyCode === 229) return;
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitFromInput(modalInput);
    }
  });

  // ─ collapse / expand 토글 ─
  function toggleCollapsed(forceCollapsed) {
    const willCollapse = (typeof forceCollapsed === 'boolean')
      ? forceCollapsed
      : !bar.classList.contains('collapsed');
    bar.classList.toggle('collapsed', willCollapse);
    document.body.classList.toggle('has-floating-ai-collapsed', willCollapse);
    collapseBtn.textContent = willCollapse ? '▴' : '▾';
    collapseBtn.title = willCollapse ? '펼치기' : '접기';
    if (!willCollapse) {
      // 펼쳤으니 메시지 영역 스크롤 맨 아래로
      setTimeout(() => { miniMessages.scrollTop = miniMessages.scrollHeight; }, 60);
    }
  }
  // 헤더 전체 클릭 → 토글 (단, 버튼 클릭 시는 무시)
  header.addEventListener('click', function(e) {
    if (e.target.closest('button')) return;
    toggleCollapsed();
  });
  collapseBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    toggleCollapsed();
  });

  // ─ 모달 열기/닫기 + 크기 영속 ─
  const modalBox = document.getElementById('floatingAiModalBox');
  function applySavedModalSize() {
    try {
      const saved = JSON.parse(localStorage.getItem('tc_modal_size') || 'null');
      if (saved && saved.w && saved.h) {
        modalBox.style.width = saved.w + 'px';
        modalBox.style.height = saved.h + 'px';
        modalBox.style.maxWidth = 'none';  // saved size 가 max 보다 클 수 있게
      }
    } catch (_) {}
  }
  function saveModalSize() {
    try {
      const w = modalBox.offsetWidth;
      const h = modalBox.offsetHeight;
      if (w > 100 && h > 100) {
        localStorage.setItem('tc_modal_size', JSON.stringify({ w, h }));
      }
    } catch (_) {}
  }
  // ResizeObserver 로 사용자가 드래그 종료한 후 자동 저장
  if (window.ResizeObserver) {
    let resizeTimer = null;
    new ResizeObserver(function() {
      if (resizeTimer) clearTimeout(resizeTimer);
      resizeTimer = setTimeout(saveModalSize, 300);  // 드래그 멈춘 후 0.3초
    }).observe(modalBox);
  }

  function openModal() {
    syncMessages();  // 최신 동기화
    applySavedModalSize();
    modal.classList.add('open');
    setTimeout(() => modalInput.focus(), 60);
    setTimeout(() => { modalMessages.scrollTop = modalMessages.scrollHeight; }, 60);
  }
  function closeModal() { modal.classList.remove('open'); }
  expandBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    openModal();
  });
  modalClose.addEventListener('click', closeModal);
  modal.addEventListener('click', function(e) {
    if (e.target === modal) closeModal();
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && modal.classList.contains('open')) closeModal();
  });

  // ─ 메시지 동기화: 메인 #gateChatMessages → mini + modal ─
  // 메인 채팅 패널의 메시지를 그대로 미러링 (단방향 — 메인이 단일 진실 소스)
  function syncMessages() {
    const main = document.getElementById('gateChatMessages');
    if (!main) return;
    const mainNodes = Array.from(main.querySelectorAll('.gate-msg'));
    // 미러 클래스 매핑
    function buildClone(node, prefix) {
      const div = document.createElement('div');
      let role = 'assistant';
      if (node.classList.contains('user')) role = 'user';
      else if (node.classList.contains('system')) role = 'system';
      div.className = prefix + ' ' + prefix + '-' + role;
      // mini-chat 클래스명 매핑
      if (prefix === 'floating-ai-msg') {
        div.className = 'floating-ai-msg ' + role;
      } else {
        // 모달은 메인 gate-msg 와 동일 스타일 그대로 활용
        div.className = 'gate-msg ' + role;
      }
      div.textContent = node.textContent;
      return div;
    }

    // mini 갱신 (innerHTML 한 번에 교체 — 단순)
    miniMessages.innerHTML = '';
    if (mainNodes.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'floating-ai-empty';
      empty.textContent = '아직 대화가 없어요. 아래에서 요청을 입력해보세요.';
      miniMessages.appendChild(empty);
    } else {
      mainNodes.forEach(n => miniMessages.appendChild(buildClone(n, 'floating-ai-msg')));
    }
    // modal 갱신
    modalMessages.innerHTML = '';
    mainNodes.forEach(n => modalMessages.appendChild(buildClone(n, 'gate-msg')));

    // 메시지 개수 뱃지
    if (mainNodes.length > 0) {
      msgBadge.style.display = '';
      msgBadge.textContent = String(mainNodes.length);
    } else {
      msgBadge.style.display = 'none';
    }
    // 자동 스크롤 — 항상 최신 메시지 보이게
    setTimeout(() => {
      miniMessages.scrollTop = miniMessages.scrollHeight;
      modalMessages.scrollTop = modalMessages.scrollHeight;
    }, 30);
  }

  // 메인 채팅 패널 변경 감지
  const mainMessages = document.getElementById('gateChatMessages');
  if (mainMessages) {
    new MutationObserver(syncMessages).observe(mainMessages, {
      childList: true, subtree: true, characterData: true,
    });
    // 초기 동기화
    setTimeout(syncMessages, 200);
  }

  // 가시성 제어: Step 3 (분류표 검토) 화면일 때 항상 표시
  // v0.9.12: 메인 채팅 패널이 숨겨졌으므로 viewport 위치 기반 판정 제거.
  //          Step 3 진입 = 미니 채팅 항상 노출 (사용자가 항상 접근 가능)
  function updateVisibility() {
    const card3 = document.getElementById('card3');
    const stepBar3 = document.getElementById('stepBar3');
    const card3Visible = card3 && !card3.classList.contains('hidden');
    const stepBar3Active = stepBar3 && stepBar3.classList.contains('active');
    if (!card3Visible || !stepBar3Active) {
      bar.classList.remove('visible');
      document.body.classList.remove('has-floating-ai');
      return;
    }
    bar.classList.add('visible');
    document.body.classList.add('has-floating-ai');
  }

  // 스크롤/리사이즈/카드 토글에 반응
  let scrollRaf = null;
  function onScrollOrResize() {
    if (scrollRaf) return;
    scrollRaf = requestAnimationFrame(function() {
      updateVisibility();
      scrollRaf = null;
    });
  }
  window.addEventListener('scroll', onScrollOrResize, { passive: true });
  window.addEventListener('resize', onScrollOrResize);

  // card3 + stepBar3 클래스 변경 감지 (hidden / active 토글) + 첫 진입 안내 토스트
  const card3Watch = document.getElementById('card3');
  const stepBar3Watch = document.getElementById('stepBar3');
  if (card3Watch) {
    new MutationObserver(function() {
      updateVisibility();
      // 진짜 Step 3 진입 — card3 보이고 + stepBar3 active 일 때만 안내 토스트
      const isCard3Visible = !card3Watch.classList.contains('hidden');
      const isStep3Active = stepBar3Watch && stepBar3Watch.classList.contains('active');
      if (isCard3Visible && isStep3Active) {
        try {
          if (localStorage.getItem('tc_sticky_ai_hint_v098c') !== '1') {
            localStorage.setItem('tc_sticky_ai_hint_v098c', '1');
            if (typeof showToast === 'function') {
              setTimeout(function() {
                showToast('💡 분류표를 스크롤하면 하단에 AI 입력바가 자동으로 떠요', 'success');
              }, 1200);
            }
          }
        } catch (_) {}
      }
    }).observe(card3Watch, {
      attributes: true, attributeFilter: ['class']
    });
  }
  // stepBar3 의 active 클래스 변경도 감지 (SSE 재연결 등으로 card3 만 unhidden 되는 경우 방어)
  if (stepBar3Watch) {
    new MutationObserver(updateVisibility).observe(stepBar3Watch, {
      attributes: true, attributeFilter: ['class']
    });
  }
  // 초기 1회
  setTimeout(updateVisibility, 100);
})();
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
    # ── SO_REUSEADDR/SO_REUSEPORT 활성화 + listen socket 캡처 (자기 재시작 지원) ──
    # 문제 1: 기본 소켓은 os.execv 후 새 프로세스가 'Address already in use' 로 즉시 bind 실패
    #         → SO_REUSEADDR/SO_REUSEPORT 활성화로 해결
    # 문제 2: execv 후에도 옛 listen socket fd가 살아있어서 OS가 connection을 임의로 두 fd 중 하나에
    #         배분 → 옛 fd로 가면 처리 안 됨
    #         → execv 직전에 우리 listen socket 을 명시적 close 해야 함 → app._listen_sock 캡처
    import socket as _socket_mod
    from werkzeug.serving import BaseWSGIServer as _BWS
    _orig_server_bind = _BWS.server_bind
    def _patched_server_bind(self):
        # bind 직전에 SO_REUSEADDR/SO_REUSEPORT 강제 활성화
        try:
            self.socket.setsockopt(_socket_mod.SOL_SOCKET, _socket_mod.SO_REUSEADDR, 1)
        except OSError:
            pass
        if hasattr(_socket_mod, "SO_REUSEPORT"):
            try:
                self.socket.setsockopt(_socket_mod.SOL_SOCKET, _socket_mod.SO_REUSEPORT, 1)
            except OSError:
                pass
        result = _orig_server_bind(self)
        # 자기 재시작 핸들러가 close 할 수 있도록 listen socket 캡처
        try:
            app._listen_sock = self.socket
        except Exception:
            pass
        return result
    _BWS.server_bind = _patched_server_bind
    # 일반 app.run 사용 — patched bind 가 자동 적용됨
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True, use_reloader=False)
