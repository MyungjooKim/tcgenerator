"""
Supercycl TC Excel Builder — v3 (대분류/중분류/소분류 분류 체계 적용)
변경점 (v2 → v3):
  - 파서: 대분류/중분류/소분류 필드 추출 추가
  - TC 목록 컬럼: "도메인" → "대분류 | 중분류 | 소분류" 3열로 분리
  - 분류표 없는 TC는 기존 도메인 기반 폴백 동작
  - 통계 시트: 중분류별 TC 수 섹션 추가

사용법:
  python3 scripts/build_excel.py --phase P2_Mobile --tc phase2-mobile/_workspace/05_review/tc_final.md --output phase2-mobile/outputs
  python3 scripts/build_excel.py --phase P1_Youthmeta --tc phase1-youthmeta/workspace/youthmeta_3_tc.md --output phase1-youthmeta/outputs
"""

import re, sys
from datetime import datetime
from pathlib import Path
import argparse
from collections import defaultdict

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    print("openpyxl 미설치. 실행: pip install openpyxl")
    sys.exit(1)

# ── Phase 설정 ─────────────────────────────────────────────────────

PHASE_CONFIG = {
    "P2_Mobile": {
        "name": "Supercycl 모바일 체험",
        "code": "P2_Mobile",
        "exchanges": [],
        "testers": {},
        "test_env": "Hyperliquid Testnet (Chain ID 998)",
        "platform": "Web(Mobile) — iOS Safari / Android Chrome",
        "target": "모바일 체험 시나리오 — 온보딩·거래·시그널·설정",
        "methodology": "User Journey  ·  BDD Given/When/Then  ·  블랙박스  ·  화면 관찰 기반",
    },
    "P_WebApp": {
        "name": "TC 자동화 웹앱",
        "code": "P_WebApp",
        "exchanges": [],
        "testers": {},
        "test_env": "Web 기반 TC 자동 생성",
        "platform": "Web(Mobile) / iOS Safari / Android Chrome / 공통",
        "target": "기획서/GitHub URL/텍스트 기반 자동 생성 TC",
        "methodology": "BDD Given/When/Then  ·  블랙박스  ·  화면 관찰 기반",
    },
    "P1_Youthmeta": {
        "name": "Supercycl × Youthmeta",
        "code": "P1_Youthmeta",
        "exchanges": ["Gate", "OKX", "Bybit", "Bitget", "Hyperliquid"],
        "testers": {
            "Gate":         ("Tester 2", "2E4057"),
            "OKX":          ("Tester 1", "1C6E38"),
            "Bybit":        ("Tester 1", "1C6E38"),
            "Bitget":       ("Tester 2", "2E4057"),
            "Hyperliquid":  ("Tester 2", "2E4057"),
        },
        "test_env": "https://aggr-dev.supercycl.io/?partner=Youthmeta",
        "platform": "Web (Chrome / Brave)",
        "target": "자동 TP/SL 설정 기능  +  유스메타 유입 유저 레버리지 2배 고정",
        "methodology": "User Journey  ·  BDD Given/When/Then  ·  블랙박스",
    },
}

# ── 도메인별 그룹 헤더 색상 ────────────────────────────────────────

DOMAIN_COLORS = {
    "AUTH": "1F3864",   # dark navy
    "REFF": "2E4057",   # dark blue-gray
    "LEVR": "7B2D8B",   # purple
    "TPSL": "C44D00",   # dark orange
    "TRAD": "0070C0",   # blue
    "SGNL": "1C6E38",   # dark green
    "MOBL": "4472C4",   # medium blue
    "SETG": "375623",   # dark green (settings)
    "ROUT": "833C00",   # brown
    "FUND": "375623",
    "ETC":  "636363",   # gray
}

DOMAIN_LABELS = {
    "AUTH": "인증 · 온보딩 · 자금 지급",
    "REFF": "레퍼럴 코드 자동 등록",
    "LEVR": "레버리지 2배 고정",
    "TPSL": "자동 TP/SL",
    "TRAD": "거래 · 주문 · 포지션",
    "SGNL": "YouthMeta 시그널",
    "MOBL": "Testnet UI · 모바일 반응형",
    "SETG": "설정 (SettingsPage)",
    "ROUT": "라우팅 · 접근 제어",
    "FUND": "자금 지급",
    "ETC":  "기타",
}

# ── 색상 팔레트 ────────────────────────────────────────────────────

C_DARK   = "1F3864"; C_WHITE  = "FFFFFF"
C_BLUE1  = "2E75B6"; C_BLUE2  = "DDEBF7"
C_GREEN  = "E2EFDA"; C_YELLOW = "FFF2CC"
C_RED    = "FCE4D6"; C_GRAY   = "E0E0E0"
C_ROW_A  = "FFFFFF"; C_ROW_B  = "F5F9FE"

PRIORITY_COLOR = {"High": "FCE4D6", "Medium": "FFF3E0", "Low": "E8F5E9"}
CATEGORY_COLOR = {"Positive": "E2EFDA", "Negative": "FCE4D6", "Edge": "FFF2CC"}

# ── 스타일 헬퍼 ────────────────────────────────────────────────────

def make_fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def make_font(bold=False, color="000000", size=10, name="Arial"):
    return Font(bold=bold, color=color, size=size, name=name)

def make_border():
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s, right=s, top=s, bottom=s)

def make_align(wrap=True, h="left", v="center"):
    return Alignment(wrap_text=wrap, horizontal=h, vertical=v)

def set_cell(ws, row, col, value, bold=False, bg=None, font_color="000000",
             size=10, align_h="left", wrap=True, font_name="Arial"):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = make_font(bold=bold, color=font_color, size=size, name=font_name)
    if bg:
        cell.fill = make_fill(bg)
    cell.alignment = make_align(wrap=wrap, h=align_h)
    cell.border = make_border()
    return cell

# ── TC 파싱 ────────────────────────────────────────────────────────

def parse_tc_markdown(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    tcs = []
    blocks = re.split(r'\n(?=### )', content)

    for block in blocks:
        if not block.strip().startswith('###'):
            continue

        tc = {}

        first_line = block.split('\n')[0]

        # 최소 TC: ### **SC-XXX-YYY-001** — 제목
        bold_header = re.match(r'###\s+\*\*(.+?)\*\*\s*—\s*(.+?)\s*$', first_line)
        # 일반 TC:  ### SC-XXX-YYY-001 — 제목
        norm_header = re.match(r'###\s+(.+?)\s+—\s+(.+?)\s*$', first_line)

        if bold_header:
            tc["star"]  = True
            tc["id"]    = bold_header.group(1).strip()
            tc["title"] = bold_header.group(2).strip()
        elif norm_header:
            tc["star"]  = False
            tc["id"]    = norm_header.group(1).strip()
            tc["title"] = norm_header.group(2).strip()
        else:
            # — 구분자 없는 경우 폴백
            plain = re.match(r'###\s+\*\*(.+?)\*\*\s*$', first_line)
            if plain:
                tc["star"]  = True
                tc["id"]    = plain.group(1).strip()
                tc["title"] = tc["id"]
            else:
                plain2 = re.match(r'###\s+(.+?)\s*$', first_line)
                if not plain2:
                    continue
                tc["star"]  = False
                tc["id"]    = plain2.group(1).strip()
                tc["title"] = tc["id"]

        tc["is_new"]  = "[신규]" in tc["title"]
        tc["title"]   = tc["title"].replace("[신규]", "").strip()

        tc["category"] = extract_table_field(block, "분류") or ""
        tc["priority"] = extract_table_field(block, "우선순위") or ""
        tc["platform"] = extract_table_field(block, "플랫폼") or ""
        tc["screen"]   = extract_table_field(block, "연관 화면") or ""

        # 대분류/중분류/소분류 추출 (신규 형식)
        # 대분류 필드 예: "Authentication & Onboarding (AUTH)" → "AUTH" 코드 파싱
        cat_raw = extract_table_field(block, "대분류") or ""
        tc["major"]  = cat_raw  # 대분류 (전체 텍스트)
        tc["middle"] = extract_table_field(block, "중분류") or ""
        tc["minor"]  = extract_table_field(block, "소분류") or ""

        # 도메인 코드 결정: 신규 SC- 형식이면 두 번째 세그먼트, 구형이면 첫 번째
        parts = tc["id"].split("-")
        if parts[0] == "SC" and len(parts) >= 3:
            tc["domain"] = parts[1]  # SC-AUTH-LOGN-001 → AUTH
        elif len(parts) >= 1:
            tc["domain"] = parts[0]  # AUTH-OAUTH-001 → AUTH
        else:
            tc["domain"] = "ETC"

        tc["given"] = extract_section(block, "사전 조건")
        tc["when"]  = extract_section(block, "테스트 단계")
        tc["then"]  = extract_section(block, "예상 결과")
        tc["note"]  = extract_section(block, "비고")

        tc["exchange_na"] = parse_exchange_na(tc["note"])

        tcs.append(tc)

    return tcs

def extract_table_field(block, field_name):
    m = re.search(rf'\|\s*{field_name}\s*\|\s*(.+?)\s*\|', block)
    return m.group(1).strip() if m else ""

def extract_section(block, section_name):
    m = re.search(
        rf'\*\*{section_name}\*\*\s*\n(.*?)(?=\n\*\*|\n---|\Z)',
        block, re.DOTALL
    )
    if not m:
        return ""
    raw_lines = [l for l in m.group(1).strip().split('\n') if l.strip()]
    # 사전 조건만 번호 개조식, 나머지(테스트 단계/예상 결과/비고)는 불릿만 제거
    if section_name == "사전 조건":
        result = []
        n = 1
        for l in raw_lines:
            stripped = l.strip()
            if re.match(r'^\d+\.', stripped):
                result.append(stripped)
                n = int(re.match(r'^(\d+)', stripped).group(1)) + 1
            elif re.match(r'^[-*]\s+', stripped):
                body = re.sub(r'^[-*]\s+', '', stripped)
                result.append(f"{n}. {body}")
                n += 1
            else:
                result.append(f"{n}. {stripped}")
                n += 1
        return "\n".join(result)
    else:
        # 불릿/번호 제거 → 텍스트만
        result = []
        for l in raw_lines:
            stripped = l.strip()
            stripped = re.sub(r'^[-*]\s+', '', stripped)
            stripped = re.sub(r'^\d+\.\s*', '', stripped)
            result.append(stripped)
        return "\n".join(result)

def parse_exchange_na(note_text):
    na = {}
    if not note_text:
        return na
    for line in note_text.split('\n'):
        for ex in ["Gate", "OKX", "Bybit", "Bitget", "Hyperliquid"]:
            if re.search(rf'{ex}.*N/A', line, re.IGNORECASE):
                na[ex] = True
    return na

# ── 버전 자동 증가 ─────────────────────────────────────────────────

def get_next_version(output_dir, phase_code, date_str):
    pattern = re.compile(rf'SPCY_TC_{phase_code}_{date_str}_v(\d+)\.xlsx')
    existing = [int(m.group(1)) for f in Path(output_dir).glob("*.xlsx")
                if (m := pattern.match(f.name))]
    return max(existing) + 1 if existing else 1

# ── 표지 시트 ──────────────────────────────────────────────────────

def build_cover(ws, tcs, config, date_str, version):
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 52

    total = len(tcs)
    star  = sum(1 for t in tcs if t["star"])

    # 메인 타이틀
    set_cell(ws, 2, 2, f"{config['name']}  |  테스트 케이스 명세서",
             bold=True, bg=C_DARK, font_color=C_WHITE, size=14, align_h="left")
    ws.merge_cells("B2:C2")
    ws.row_dimensions[2].height = 30

    set_cell(ws, 3, 2,
             f"테스트 케이스 명세서  ·  v{version}  ·  BDD Given/When/Then",
             bold=False, bg=C_BLUE1, font_color=C_WHITE, size=10)
    ws.merge_cells("B3:C3")
    ws.row_dimensions[3].height = 18

    # 기본 정보
    ws.row_dimensions[4].height = 8
    info = [
        ("대상 기능",   config["target"]),
        ("테스트 환경", config["test_env"]),
        ("플랫폼",      config["platform"]),
        ("TC 방법론",   config["methodology"]),
        ("작성일",      f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}  (v{version})"),
    ]
    for i, (k, v) in enumerate(info, start=5):
        set_cell(ws, i, 2, k, bold=True, bg=C_BLUE1, font_color=C_WHITE)
        set_cell(ws, i, 3, v, bold=False, bg=C_BLUE2)
        ws.row_dimensions[i].height = 18

    # TC 통계 요약
    ws.row_dimensions[10].height = 10
    set_cell(ws, 11, 2, "TC 통계 요약", bold=True, bg=C_DARK, font_color=C_WHITE, size=11)
    ws.merge_cells("B11:C11")
    ws.row_dimensions[11].height = 22

    high   = sum(1 for t in tcs if t["priority"] == "High")
    medium = sum(1 for t in tcs if t["priority"] == "Medium")
    low    = sum(1 for t in tcs if t["priority"] == "Low")
    pos    = sum(1 for t in tcs if t["category"] == "Positive")
    neg    = sum(1 for t in tcs if t["category"] == "Negative")
    edge   = sum(1 for t in tcs if t["category"] == "Edge")

    stats = [
        ("총 TC 수",      f"{total}개"),
        ("★ 최소 TC 세트", f"{star}개  ({star*100//total if total else 0}%)"),
        ("High 우선순위",  f"{high}개  ({high*100//total if total else 0}%)"),
        ("Positive",      f"{pos}개"),
        ("Negative",      f"{neg}개"),
        ("Edge",          f"{edge}개"),
    ]
    for i, (k, v) in enumerate(stats, start=12):
        bg = C_BLUE2 if i % 2 == 0 else C_WHITE
        set_cell(ws, i, 2, k, bold=True, bg=C_BLUE1, font_color=C_WHITE)
        set_cell(ws, i, 3, v, bold=False, bg=bg)
        ws.row_dimensions[i].height = 18

    # 도메인별 TC 수
    row = 12 + len(stats) + 1
    ws.row_dimensions[row].height = 10
    row += 1
    set_cell(ws, row, 2, "도메인별 구성", bold=True, bg=C_DARK, font_color=C_WHITE, size=11)
    ws.merge_cells(f"B{row}:C{row}")
    ws.row_dimensions[row].height = 22
    row += 1

    domain_counts = defaultdict(int)
    for tc in tcs:
        domain_counts[tc["domain"]] += 1

    for i, (domain, cnt) in enumerate(sorted(domain_counts.items())):
        color = DOMAIN_COLORS.get(domain, "636363")
        label = DOMAIN_LABELS.get(domain, domain)
        set_cell(ws, row, 2, f"{domain}  ·  {label}", bold=True,
                 bg=color, font_color=C_WHITE)
        set_cell(ws, row, 3, f"{cnt}개", bold=False,
                 bg=C_BLUE2 if i % 2 == 0 else C_WHITE, align_h="center")
        ws.row_dimensions[row].height = 18
        row += 1

    # 판정 코드 범례
    ws.row_dimensions[row].height = 10
    row += 1
    set_cell(ws, row, 2, "판정 코드", bold=True, bg=C_DARK, font_color=C_WHITE, size=11)
    ws.merge_cells(f"B{row}:C{row}")
    ws.row_dimensions[row].height = 22
    row += 1

    for code, desc in [
        ("Pass",  "기대 결과와 일치"),
        ("Fail",  "버그 발생 → 결함 리포트 필수"),
        ("N/T",   "Not Tested  (미실시, 기본값)"),
        ("N/A",   "Not Applicable  (해당 없음)"),
    ]:
        set_cell(ws, row, 2, code, bold=True, bg=C_BLUE1, font_color=C_WHITE, align_h="center")
        set_cell(ws, row, 3, desc, bg=C_BLUE2)
        ws.row_dimensions[row].height = 18
        row += 1


# ── TC 전체목록 시트 ───────────────────────────────────────────────

def _tc_list_columns(config):
    """Phase에 따른 컬럼 정의 반환"""
    exchanges = config["exchanges"]

    # 분류표 사용 여부 감지: 첫 TC에 middle(중분류) 값이 있으면 신규 형식
    has_classification = any(tc.get("middle") for tc in [])  # 동적으로 판단
    # → build_tc_list 호출 시 tcs를 전달받아 판단

    fixed = [
        ("TC ID",              14),
        ("대분류",              13),
        ("중분류",              13),
        ("소분류",              16),
        ("사전조건",            28),
        ("테스트 스텝",         40),
        ("기대결과",            38),
        ("중요도",               9),
        ("관련 거래소",         10),
    ]

    all_cols = fixed
    return all_cols


def _priority_to_kr(priority):
    """우선순위 영문 → 한글 변환"""
    mapping = {"High": "높음", "Medium": "보통", "Low": "낮음",
               "높음": "높음", "보통": "보통", "낮음": "낮음"}
    return mapping.get(priority, priority or "보통")

def _calc_col_widths(col_names, all_row_data, min_widths=None, max_width=60):
    """각 컬럼의 75 퍼센타일 기반 최적 너비 계산.
    멀티라인 셀은 모든 줄 중 가장 긴 줄 기준."""
    col_lengths = [[] for _ in col_names]

    # 헤더 길이
    header_widths = []
    for i, name in enumerate(col_names):
        hw = sum(2 if ord(c) > 127 else 1 for c in name) + 2
        header_widths.append(hw)

    # 각 셀의 가장 긴 줄 길이 수집
    for row_data in all_row_data:
        for i, val in enumerate(row_data):
            if not val:
                col_lengths[i].append(0)
                continue
            lines = str(val).split('\n')
            max_line_w = max(
                sum(2 if ord(c) > 127 else 1 for c in line) + 2
                for line in lines if line.strip()
            ) if lines else 0
            col_lengths[i].append(max_line_w)

    # 75 퍼센타일 계산
    widths = []
    for i, lengths in enumerate(col_lengths):
        min_w = (min_widths or {}).get(col_names[i], 8)
        if not lengths:
            widths.append(max(header_widths[i], min_w))
            continue
        sorted_l = sorted(lengths)
        p75_idx = int(len(sorted_l) * 0.75)
        p75 = sorted_l[min(p75_idx, len(sorted_l) - 1)]
        widths.append(max(p75, header_widths[i], min_w))

    return [min(w, max_width) for w in widths]


def build_tc_list(ws, tcs, config, include_reason=False):
    """TC 목록 시트 생성"""
    cols = _tc_list_columns(config)
    col_names = [c[0] for c in cols]

    # Row 1: 헤더 (너비는 데이터 수집 후 설정)
    for i, name in enumerate(col_names, 1):
        set_cell(ws, 1, i, name, bold=True, bg=C_DARK, font_color=C_WHITE,
                 size=10, align_h="center")
    ws.row_dimensions[1].height = 22

    data_start = 2

    # 데이터 행 (도메인 그룹 헤더 삽입)
    prev_domain = None
    r = data_start
    row_idx = 0
    all_row_data = []  # 너비 계산용

    for tc in tcs:
        domain = tc["domain"]

        # 도메인 변경 시 그룹 헤더 행 삽입
        if domain != prev_domain:
            prev_domain = domain
            color  = DOMAIN_COLORS.get(domain, "636363")
            label  = DOMAIN_LABELS.get(domain, domain)
            text   = f"{domain}  ·  {label}"
            for i in range(1, len(col_names) + 1):
                set_cell(ws, r, i, text if i == 1 else "",
                         bold=True, bg=color, font_color=C_WHITE,
                         size=10, align_h="left")
            ws.merge_cells(f"A{r}:{get_column_letter(len(col_names))}{r}")
            ws.row_dimensions[r].height = 20
            r += 1
            row_idx = 0

        bg_base = C_ROW_A if row_idx % 2 == 0 else C_ROW_B

        # 대분류 표시
        major_display = tc.get("major", "") or tc["domain"]

        # 중분류/소분류
        middle_display = tc.get("middle") or DOMAIN_LABELS.get(tc["domain"], tc["domain"])
        minor_display  = tc.get("minor") or ""

        # 거래소 정보 추출
        exchange_text = ""
        note = tc.get("note", "")
        for ex in ["HL", "Hyperliquid", "BN", "Binance", "OKX", "Bybit", "Bitget", "Gate"]:
            if ex.lower() in note.lower():
                exchange_text = ex
                break

        col_data = {
            "TC ID":         tc["id"],
            "대분류":         major_display,
            "중분류":         middle_display,
            "소분류":         minor_display,
            "사전조건":       tc["given"],
            "테스트 스텝":    tc["when"],
            "기대결과":       tc["then"],
            "중요도":         _priority_to_kr(tc["priority"]),
            "관련 거래소":    exchange_text,
        }

        row_values = [col_data.get(name, "") for name in col_names]
        all_row_data.append(row_values)

        for i, (col_name, _) in enumerate(cols, 1):
            if col_name == "TC ID":
                cbg  = bg_base
                bold = tc["star"]
            elif col_name == "중요도":
                cbg  = PRIORITY_COLOR.get(tc["priority"], bg_base)
                bold = True
            else:
                cbg  = bg_base
                bold = tc["star"]
            set_cell(ws, r, i, col_data.get(col_name, ""), bold=bold, bg=cbg)

        ws.row_dimensions[r].height = 80
        r += 1
        row_idx += 1

    # 컬럼 너비 자동 조정 (첫 줄 길이 기반)
    min_widths = {"TC ID": 18, "중요도": 9, "관련 거래소": 10}
    widths = _calc_col_widths(col_names, all_row_data, min_widths=min_widths, max_width=55)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # 필터 & 틀 고정
    last_col = get_column_letter(len(col_names))
    ws.auto_filter.ref = f"A1:{last_col}{r - 1}"
    ws.freeze_panes   = f"A{data_start + 1}"


# ── 통계 시트 ──────────────────────────────────────────────────────

def build_stats(ws, tcs, version):
    total  = len(tcs)
    star   = sum(1 for t in tcs if t["star"])

    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 10
    ws.column_dimensions["D"].width = 10

    def sec_header(row, text):
        set_cell(ws, row, 2, text, bold=True, bg=C_DARK, font_color=C_WHITE, size=11)
        ws.merge_cells(f"B{row}:D{row}")
        ws.row_dimensions[row].height = 22

    def stat_row(row, label, count, pct_base=None, alt=False):
        bg = C_BLUE2 if alt else C_WHITE
        set_cell(ws, row, 2, label, bold=False, bg=bg)
        set_cell(ws, row, 3, count, bold=False, bg=bg, align_h="center")
        pct = f"{count*100//pct_base}%" if pct_base else ""
        set_cell(ws, row, 4, pct, bold=False, bg=bg, align_h="center")
        ws.row_dimensions[row].height = 18

    # 타이틀
    set_cell(ws, 2, 2,
             f"TC 통계  (v{version}  ·  전체 {total}개  ·  최소 세트 {star}개)",
             bold=True, bg=C_DARK, font_color=C_WHITE, size=12)
    ws.merge_cells("B2:D2")
    ws.row_dimensions[2].height = 26

    ws.row_dimensions[3].height = 8

    # ─ 전체 요약
    sec_header(4, "─ 전체 요약 ─")
    stat_row(5,  "전체 TC 수",    total,  total, alt=True)
    stat_row(6,  "★ 최소 TC 세트", star,  total, alt=False)

    # ─ 도메인별
    ws.row_dimensions[7].height = 8
    sec_header(8, "─ 도메인별 ─")
    domain_counts = defaultdict(int)
    for tc in tcs:
        domain_counts[tc["domain"]] += 1
    for i, (domain, cnt) in enumerate(sorted(domain_counts.items())):
        label = f"{domain}  ·  {DOMAIN_LABELS.get(domain, domain)}"
        stat_row(9 + i, label, cnt, total, alt=(i % 2 == 0))

    # ─ 우선순위별
    row = 9 + len(domain_counts) + 1
    ws.row_dimensions[row].height = 8
    row += 1
    sec_header(row, "─ 우선순위별 ─")
    row += 1
    for i, prio in enumerate(["High", "Medium", "Low"]):
        cnt = sum(1 for t in tcs if t["priority"] == prio)
        bg_map = {"High": "FCE4D6", "Medium": "FFF3E0", "Low": "E8F5E9"}
        cell_bg = bg_map.get(prio, C_WHITE)
        set_cell(ws, row, 2, prio, bold=True, bg=cell_bg)
        set_cell(ws, row, 3, cnt, bold=False, bg=cell_bg, align_h="center")
        set_cell(ws, row, 4, f"{cnt*100//total if total else 0}%", bg=cell_bg, align_h="center")
        ws.row_dimensions[row].height = 18
        row += 1

    # ─ 분류별
    ws.row_dimensions[row].height = 8
    row += 1
    sec_header(row, "─ 분류별 (TC 유형) ─")
    row += 1
    for i, cat in enumerate(["Positive", "Negative", "Edge"]):
        cnt = sum(1 for t in tcs if t["category"] == cat)
        cbg = CATEGORY_COLOR.get(cat, C_WHITE)
        set_cell(ws, row, 2, cat, bold=True, bg=cbg)
        set_cell(ws, row, 3, cnt, bold=False, bg=cbg, align_h="center")
        set_cell(ws, row, 4, f"{cnt*100//total if total else 0}%", bg=cbg, align_h="center")
        ws.row_dimensions[row].height = 18
        row += 1

    # ─ 중분류별 (분류표 있는 경우)
    middle_counts = defaultdict(int)
    for tc in tcs:
        m = tc.get("middle", "")
        if m:
            middle_counts[m] += 1

    if middle_counts:
        ws.row_dimensions[row].height = 8
        row += 1
        sec_header(row, "─ 중분류별 ─")
        row += 1
        for i, (mid, cnt) in enumerate(sorted(middle_counts.items())):
            stat_row(row, mid, cnt, total, alt=(i % 2 == 0))
            row += 1

    # ─ [미결] / [신규]
    ws.row_dimensions[row].height = 8
    row += 1
    sec_header(row, "─ 태그별 ─")
    row += 1
    migyul = sum(1 for t in tcs if "[미결]" in t.get("note", ""))
    new_tc = sum(1 for t in tcs if t.get("is_new"))
    dev_ck = sum(1 for t in tcs if "[개발 확인]" in t.get("note", ""))
    for i, (label, cnt) in enumerate([
        ("[미결] 태그 (정책 미확정)", migyul),
        ("[신규] 태그 (코드 기반 도출)", new_tc),
        ("[개발 확인] 태그", dev_ck),
    ]):
        stat_row(row, label, cnt, total, alt=(i % 2 == 0))
        row += 1


# ── 최소 TC 세트 시트 ──────────────────────────────────────────────

def build_minimal(ws, tcs, config):
    star_tcs = [t for t in tcs if t["star"]]
    build_tc_list(ws, star_tcs, config, include_reason=True)


# ── 메인 ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase",  default="P2_Mobile")
    parser.add_argument("--tc",     default="phase2-mobile/_workspace/05_review/tc_final.md")
    parser.add_argument("--output", default="phase2-mobile/outputs")
    args = parser.parse_args()

    base       = Path(__file__).parent.parent
    tc_path    = base / args.tc
    output_dir = base / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    config   = PHASE_CONFIG.get(args.phase, PHASE_CONFIG["P2_Mobile"])
    date_str = datetime.today().strftime("%Y%m%d")
    version  = get_next_version(output_dir, args.phase, date_str)
    filename = f"SPCY_TC_{args.phase}_{date_str}_v{version}.xlsx"
    out_path = output_dir / filename

    print(f"TC 파싱 중: {tc_path}")
    tcs = parse_tc_markdown(tc_path)
    print(f"  → {len(tcs)}개 TC 파싱 완료")

    wb = openpyxl.Workbook()

    ws_cover = wb.active;                ws_cover.title = "📋 표지"
    ws_list  = wb.create_sheet("🧪 TC 전체목록")
    ws_stats = wb.create_sheet("📊 TC 통계")
    ws_min   = wb.create_sheet("🎯 최소 TC 세트")

    build_cover(ws_cover, tcs, config, date_str, version)
    build_tc_list(ws_list, tcs, config)
    build_stats(ws_stats, tcs, version)
    build_minimal(ws_min, tcs, config)

    wb.save(out_path)

    star  = sum(1 for t in tcs if t["star"])
    high  = sum(1 for t in tcs if t["priority"] == "High")
    print(f"\n✅ Excel 저장 완료: {out_path}")
    print(f"   총 TC: {len(tcs)}개 | High: {high}개 | ★ 최소 TC 세트: {star}개")
    print(f"   Phase: {config['code']} | 버전: v{version}")
    print(f"   거래소 컬럼: {config['exchanges'] if config['exchanges'] else '없음 (단일 거래소)'}")


if __name__ == "__main__":
    main()
