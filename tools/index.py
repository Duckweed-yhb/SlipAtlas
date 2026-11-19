"""扫描 vault 的 sources/，重写 sources/index.md。用法：python tools/index.py"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def build() -> str:
    notes = list(common.iter_notes())
    by_type = Counter((m.get("source_type") or "未知") for _, m, _ in notes)
    by_status = Counter((m.get("status") or "未知") for _, m, _ in notes)

    rows = []
    for path, meta, _ in notes:
        date = meta.get("published") or meta.get("fetched", "")[:10]
        tags = "、".join(meta.get("tags", [])) if isinstance(meta.get("tags"), list) else meta.get("tags", "")
        rel = path.relative_to(common.sources_dir()).as_posix()
        rows.append((date, meta.get("title", ""), meta.get("site", ""), meta.get("source_type", ""), tags, meta.get("status", ""), rel))
    rows.sort(key=lambda r: r[0], reverse=True)

    out = ["# 简图索引", ""]
    out.append("由 `tools/index.py` 生成，不要手改。改字段请改 md 文件本身，然后重跑索引。")
    out.append("")
    total = len(notes)
    parts = [f"{k} {v}" for k, v in by_type.most_common()]
    out.append(f"共 {total} 篇（{('，'.join(parts) or '暂无')}）；状态：{('，'.join(f'{k} {v}' for k, v in by_status.most_common()) or '暂无')}")
    out.append("")
    if rows:
        out.append("| 日期 | 标题 | 来源 | 类型 | 标签 | 状态 | 文件 |")
        out.append("| --- | --- | --- | --- | --- | --- | --- |")
        for r in rows:
            title = r[1].replace("|", "\\|")
            out.append(f"| {r[0]} | {title} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | `{r[6]}` |")
    else:
        out.append("（还没有条目。`/slip intake <链接>` 之后再跑一次索引。）")
    out.append("")
    return "\n".join(out)


def main() -> int:
    target_dir = common.sources_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "index.md"
    text = build()
    target.write_text(text, encoding="utf-8")
    print(f"已写入 {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
