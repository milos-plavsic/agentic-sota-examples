from __future__ import annotations

import json
from pathlib import Path


def _load_rows(root: Path) -> list[dict[str, object]]:
    nightly = root / "reports" / "nightly-benchmark.json"
    if nightly.exists():
        return json.loads(nightly.read_text(encoding="utf-8"))

    rows: list[dict[str, object]] = []
    for p in sorted((root / "reports").glob("*-summary.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        rows.append(
            {
                "project": d["project"],
                "confidence_score": float(d["confidence_score"]),
                "iterations": int(d["iterations"]),
                "stop_reason": d["loop_terminated_reason"],
                "used_fallback": bool(d["used_fallback"]),
            }
        )
    return rows


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    rows = _load_rows(root)
    out = root / "docs" / "LATEST_BENCHMARK_SUMMARY.md"

    lines = [
        "# Latest Benchmark Summary",
        "",
        f"Generated automatically from benchmark artifacts ({len(rows)} projects).",
        "",
        "| Project | Confidence | Iterations | Stop Reason | Fallback |",
        "|---|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['project']}` | {float(row['confidence_score']):.3f} | "
            f"{int(row['iterations'])} | `{row['stop_reason']}` | `{str(bool(row['used_fallback'])).lower()}` |"
        )
    if rows:
        avg = sum(float(r["confidence_score"]) for r in rows) / len(rows)
        fallback_n = sum(1 for r in rows if bool(r["used_fallback"]))
        lines.extend(["", f"- Average confidence: **{avg:.3f}**", f"- Fallback usage: **{fallback_n}/{len(rows)}**"])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(out))


if __name__ == "__main__":
    main()
