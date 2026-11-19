"""抓取并落盘一篇。两种用法：

  python tools/intake.py <url>
  python tools/intake.py <url> --text-file body.md --title "标题" --site "某某公众号"

抓公众号失败时，让用户把正文粘成 body.md 再用 --text-file，不要改代码硬刚反爬。
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


def fetch_html(url: str, cookie: str = "") -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})
    if cookie:
        req.add_header("Cookie", cookie)
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


def extract(url: str, html: str) -> tuple[str, str]:
    """返回 (标题, 正文)。装了 trafilatura 就用它，否则退回粗糙正则。"""
    title = ""
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    if m:
        title = re.sub(r"\s+", " ", m.group(1)).strip()
    try:
        import trafilatura  # type: ignore

        body = trafilatura.extract(html, include_comments=False, include_tables=False) or ""
        if body.strip():
            return title, body.strip()
    except ImportError:
        pass
    body = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", "", html)
    body = re.sub(r"(?i)<br\s*/?>", "\n", body)
    body = re.sub(r"(?i)</(p|div|h\d|li|section)>", "\n\n", body)
    body = re.sub(r"(?s)<[^>]+>", "", body)
    body = re.sub(r"&nbsp;?", " ", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return title, "\n".join(line.strip() for line in body.splitlines()).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--text-file", help="已抓好或粘贴的正文，跳过网络请求")
    ap.add_argument("--title", default="")
    ap.add_argument("--site", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--published", default="")
    ap.add_argument("--source-type", default="article", choices=["article", "video", "post"])
    ap.add_argument("--tags", default="", help="逗号分隔，留空则交给摘要环节补")
    ap.add_argument("--status", default="inbox", choices=["inbox", "digested", "archived"])
    args = ap.parse_args()

    canonical = common.normalize_url(args.url)
    cookie = common.config().get("intake", {}).get("wechat_cookie", "")

    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8").strip()
        title = args.title
    else:
        html = fetch_html(args.url, cookie)
        title, text = extract(args.url, html)
        if not text.strip():
            print("抓取失败：正文为空。请把正文存成文件后用 --text-file 重跑。", file=sys.stderr)
            return 2
        title = args.title or title

    if not text.strip():
        print("正文为空，未落盘。", file=sys.stderr)
        return 2

    chash = common.content_hash(text)
    dup = common.find_duplicate(canonical, chash)
    if dup:
        print(f"已存在，跳过：{dup}")
        return 0

    site = args.site or (re.sub(r"^https?://", "", canonical).split("/")[0])
    date = args.published or common.now_iso()[:10]
    stem = f"{date}-{common.slugify(title or 'untitled')}"
    folder = common.sources_dir() / date[:4]
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{stem}.md"

    meta = {
        "title": title,
        "url": args.url,
        "canonical_url": canonical,
        "site": site,
        "source_type": args.source_type,
        "author": args.author,
        "published": args.published,
        "fetched": common.now_iso(),
        "content_hash": chash,
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
        "status": args.status,
        "partial": False,
    }
    body = f"\n## 原文\n\n{text}\n"
    target.write_text(common.render_note(meta, body), encoding="utf-8")
    print(f"已落盘：{target}")
    print("下一步：补摘要与标签，然后 python tools/index.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
