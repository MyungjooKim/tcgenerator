#!/usr/bin/env python3
"""옵션 조합 TC 생성 CLI — 결과 확인용 최소 진입점.

사용:
  python3 run_combo_tc.py <project> [--sample N] [out.md]
    --sample N : 처음 N개 OC + 시나리오 첫 2개만 (테스트용, 비용 절감)
    (생략) 전체 생성

  예: python3 run_combo_tc.py supercycl --sample 5
      python3 run_combo_tc.py supercycl combo_tc.md

ANTHROPIC_API_KEY 환경변수 필요.
"""
import sys
import os
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import app_v2


def trim_combo_data(data: dict, sample_n: int | None = None,
                    oc_filter: str | None = None,
                    scn_filter: str | None = None) -> dict:
    """샘플 모드. raw_md 자체를 필터된 항목만 남기게 재구성.
    sample_n: OC 첫 N개 + 시나리오 첫 2개
    oc_filter: 'OC-070,OC-071,...' 또는 'OC-07*' (prefix)
    scn_filter: 'S7' 또는 'S1,S7'
    필터 미지정 시 해당 종류는 0개 (sample_n 사용 시만 기본값).
    """
    import re as _re
    combos = data["combos"]
    scenarios = data["scenarios"]

    # 정책: --oc 또는 --scn 중 하나라도 명시되면 "필터 모드".
    # 필터 모드에서 명시 안 된 종류는 0개 (사용자 의도가 명확하므로).
    # sample_n 만 있으면 "기본 샘플 모드" — OC N개 + 시나리오 첫 2개.
    is_filter_mode = bool(oc_filter or scn_filter)

    # 1) OC 필터
    if oc_filter:
        ids = [s.strip().upper() for s in oc_filter.split(",")]
        def match(c_id):
            for p in ids:
                if p.endswith("*"):
                    if c_id.startswith(p[:-1]): return True
                elif c_id == p: return True
            return False
        combos = [c for c in combos if match(c["id"])]
    elif is_filter_mode:
        # scn_filter 만 지정됨 → OC 는 0개
        combos = []
    elif sample_n:
        combos = combos[:sample_n]
    # else: combos 전체 유지 (필터 미지정, sample 미지정)

    # 2) 시나리오 필터
    if scn_filter:
        ids = [s.strip().upper() for s in scn_filter.split(",")]
        scenarios = [s for s in scenarios if s["id"].upper() in ids]
    elif is_filter_mode:
        # oc_filter 만 지정됨 → 시나리오 0개
        scenarios = []
    elif sample_n:
        scenarios = scenarios[:2]
    # else: scenarios 전체 유지

    # 3) raw_md 재구성 — 필터된 OC/시나리오만 포함
    # 샘플 모드일 때만 raw_md 재구성 (필터 또는 sample_n 적용된 경우)
    is_sample = bool(sample_n or oc_filter or scn_filter)
    if is_sample:
        new_raw = _rebuild_raw_md(data["raw_md"], combos, scenarios)
    else:
        new_raw = data["raw_md"]

    return {
        "raw_md": new_raw,
        "combos": combos,
        "scenarios": scenarios,
        "_sample_mode": is_sample,
    }


def _rebuild_raw_md(raw_md: str, kept_combos: list, kept_scenarios: list) -> str:
    """raw_md 를 재구성 — 필터된 OC 행과 시나리오 블록만 남김.
    헤더/Reference 섹션은 유지, 표 행은 ID 매칭으로 필터.
    """
    import re as _re
    kept_oc_ids = {c["id"] for c in kept_combos}
    kept_scn_ids = {s["id"] for s in kept_scenarios}

    out_lines = []
    lines = raw_md.splitlines()
    in_section4 = False
    current_scn_keep = True  # ## 4 진입 전에는 모든 라인 유지
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 섹션 4 진입 감지
        if stripped.startswith("## 4.") or stripped.startswith("## 4 "):
            in_section4 = True
            out_lines.append(line)
            i += 1
            continue
        if stripped.startswith("## 5.") or stripped.startswith("## 5 "):
            in_section4 = False
            current_scn_keep = True

        # 섹션 4 안: 시나리오 헤더 검사
        if in_section4:
            m_scn = _re.match(r"^###\s+(?:⭐\s*)?(S\d+):", stripped)
            if m_scn:
                current_scn_keep = m_scn.group(1) in kept_scn_ids
            elif stripped.startswith("### ") and not stripped.startswith("### "):
                # 다른 ### (페르소나 매트릭스 등)
                current_scn_keep = True
            if not current_scn_keep:
                # 다음 시나리오 헤더 또는 ## 5 까지 skip
                i += 1
                continue

        # OC 표 행 필터 (섹션 3)
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if cells:
                first = cells[0].upper()
                m_oc = _re.match(r"^OC-\d+$", first)
                if m_oc:
                    if first not in kept_oc_ids:
                        i += 1
                        continue

        out_lines.append(line)
        i += 1

    return "\n".join(out_lines)


def main():
    parser = argparse.ArgumentParser(description="옵션 조합 TC 생성 CLI")
    parser.add_argument("project", help="프로젝트 이름 (예: supercycl)")
    parser.add_argument("output", nargs="?", default=None, help="출력 md 경로")
    parser.add_argument("--sample", type=int, default=None,
                        help="샘플 모드 — 처음 N개 OC + 시나리오 첫 2개만 생성")
    parser.add_argument("--oc", type=str, default=None,
                        help="OC 필터 (콤마 구분, * 접두 가능). 예: OC-070,OC-071 또는 OC-07*")
    parser.add_argument("--scn", type=str, default=None,
                        help="시나리오 필터 (콤마 구분). 예: S7 또는 S1,S7")
    args = parser.parse_args()

    out_path = Path(args.output) if args.output else Path(
        f"combo_tc_{args.project}{'_sample' if args.sample else ''}.md"
    )

    print(f"[1/3] {args.project} 의 order_combinations.md 파싱 중...")
    data = app_v2.parse_order_combinations(args.project)
    if not data:
        print(f"  ✗ order_combinations.md 를 찾을 수 없음 (project: {args.project})")
        sys.exit(1)
    print(f"  ✓ combos {len(data['combos'])}개, scenarios {len(data['scenarios'])}개, "
          f"steps {sum(len(s['steps']) for s in data['scenarios'])}개")

    if args.sample or args.oc or args.scn:
        data = trim_combo_data(data, args.sample, args.oc, args.scn)
        sample_steps = sum(len(s['steps']) for s in data['scenarios'])
        print(f"  ⓘ 샘플 모드 — OC {len(data['combos'])}개 + 시나리오 step {sample_steps}개 만 생성")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("  ✗ ANTHROPIC_API_KEY 환경변수 미설정")
        sys.exit(1)

    print(f"\n[2/3] LLM 호출 (그레이박스 TC 생성)...")
    tc_md, count = app_v2.step_write_combo_tc(None, args.project, data, project_code="SM")
    print(f"  ✓ {count}개 TC 생성")

    print(f"\n[3/3] {out_path} 에 저장...")
    out_path.write_text(tc_md, encoding="utf-8")
    print(f"  ✓ 완료 ({len(tc_md):,} 자)")
    print(f"\n=== 첫 2000자 미리보기 ===\n")
    print(tc_md[:2000])
    print(f"\n... [중략] ...\n")
    print(f"전체 결과: {out_path.resolve()}")


if __name__ == "__main__":
    main()
