"""SlipAtlas 公共工具：配置、frontmatter 读写、URL 规范化、内容 hash、slug。仅用标准库。"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

CST = timezone(timedelta(hours=8))
DEFAULT_VAULT = Path(r"E:/future/yhb/07-阅读与藏书/Lifetime-Archive")

TRACKING_PARAMS = re.compile(
    r"^(utm_|from$|isappinstalled$|scene$|spm$|share_|chksm$|clicktime$|enterid$|ascene$|devicetype$|version$|nettype$|abtest_|key$|pass_ticket$|wx_header$)"
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_config(config_path: Path) -> dict:
    """极简 TOML 读取：只认 [section] 与 key = "value"。够用，不引第三方。"""
    if not config_path.exists():
        return {}
    data: dict[str, dict[str, str]] = {}
    section = "root"
    for line in config_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            data.setdefault(section, {})
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            v = v.strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            data.setdefault(section, {})[k.strip()] = v
    return data


def config() -> dict:
    return _read_config(repo_root() / "config.toml")


def vault_path() -> Path:
    raw = config().get("vault", {}).get("path", "").strip()
    return Path(raw) if raw else DEFAULT_VAULT


def sources_dir() -> Path:
    return vault_path() / "sources"


def now_iso() -> str:
    return datetime.now(CST).replace(microsecond=0).isoformat()


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    url = re.sub(r"^https?://", lambda m: m.group(0).lower(), url)
    url = url.split("#", 1)[0]
    if "?" in url:
        base, query = url.split("?", 1)
        if "mp.weixin.qq.com" in base.lower():
            keep = ["__biz", "mid", "idx", "sn"]
            pairs = [p for p in query.split("&") if p.split("=", 1)[0] in keep]
        else:
            pairs = [p for p in query.split("&") if not TRACKING_PARAMS.match(p.split("=", 1)[0])]
        url = base + ("?" + "&".join(pairs) if pairs else "")
    return url.rstrip("/")


def content_hash(text: str) -> str:
    flat = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(flat.encode("utf-8")).hexdigest()[:16]


def slugify(title: str, max_len: int = 40) -> str:
    title = re.sub(r"[\\/:*?\"<>|]", "", title).strip()
    title = re.sub(r"\s+", "-", title)
    return (title[:max_len].strip("-") or "untitled").lower()


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    meta: dict = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            meta[k] = [x.strip().strip('"') for x in inner.split(",") if x.strip()]
        elif v.lower() in {"true", "false"}:
            meta[k] = v.lower() == "true"
        else:
            meta[k] = v.strip('"')
    return meta, body


def render_note(meta: dict, body: str) -> str:
    lines = ["---"]
    for k, v in meta.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif v is None or v == "":
            continue
        else:
            lines.append(f'{k}: "{v}"')
    lines.append("---")
    lines.append("")
    return "\n".join(lines) + body.rstrip() + "\n"


def iter_notes():
    root = sources_dir()
    if not root.exists():
        return
    for path in sorted(root.rglob("*.md")):
        if path.name == "index.md":
            continue
        try:
            meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        except OSError:
            continue
        yield path, meta, body


def find_duplicate(canonical_url: str, chash: str) -> Path | None:
    for path, meta, _ in iter_notes():
        if canonical_url and meta.get("canonical_url") == canonical_url:
            return path
        if chash and meta.get("content_hash") == chash:
            return path
    return None
