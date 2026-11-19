# 笔记字段

一篇一个文件：`{vault}/sources/{年}/{YYYY-MM-DD}-{slug}.md`。

## frontmatter

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `title` | 是 | 原文标题，不改写 |
| `url` | 是 | 原始链接，原样保留 |
| `canonical_url` | 是 | 规范化后用于去重的链接（见下） |
| `site` | 是 | 公众号名 / 站点 / UP 主 |
| `source_type` | 是 | `article` / `video` / `post` |
| `author` | 否 | 署名作者，没有就留空 |
| `published` | 否 | 原文发布日期 `YYYY-MM-DD`，抓不到留空 |
| `fetched` | 是 | 落盘时间，ISO 8601 带时区 |
| `content_hash` | 是 | 正文去空白后 sha256 前 16 位 |
| `tags` | 是 | 3–5 个，取自正文用词 |
| `summary` | 否 | 150–300 字中文摘要；`status: inbox` 时可空 |
| `status` | 是 | `inbox` / `digested` / `archived` / `dead` |
| `partial` | 否 | 正文抓不全时 `true` |

## 正文

```markdown
## 原文

（正文，段落照抄，不改错字；视频为字幕整理稿，去掉时间码）

## 金句

- 原文里值得单独留下的句子，逐字引用，附上下文一句

## 我的看法

（可选。只在用户明确要求时写，与原文严格分开）
```

## URL 规范化

去掉：`utm_*`、`from`、`isappinstalled`、`scene`、`spm`、`share_*`、`chksm` 以外的追踪参数；
末尾 `/` 去掉；域名与协议小写；保留 `mp.weixin.qq.com` 的 `__biz`、`mid`、`idx`、`sn` 四个参数。

## 与总表的关系

| 内容 | 落点 |
| --- | --- |
| 书 / 网文 / 影视 / 学习资料 | `Lifetime-Archive_总表.xlsx`（14 列，现有结构不动） |
| 文章 / 视频 / 帖子 | `sources/`（本文件定义的字段） |
| 索引 | `sources/index.md`，由 `tools/index.py` 生成 |

两边不互写。一本书读完后写的长笔记放 `notes/<书名>/`。
