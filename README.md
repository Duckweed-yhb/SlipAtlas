# SlipAtlas · 简图

把散落在公众号推文、视频、长文里的东西，削成可检索的「简」。

霜·浑·简 三件里的**输入**：FrostSword 动手，ArmilGrid 定向，SlipAtlas 只管往里读。

英文版见 [README.en.md](README.en.md)。

## 它做什么

1. **抓**——给一个链接，取正文（视频取字幕），落成一篇本地 Markdown
2. **摘**——中文摘要，只写作者说了什么、凭什么这么说，不写读后感
3. **标**——3–5 个标签，只用正文里出现过的词
4. **存**——URL 规范化 + 正文 hash 去重，同一篇不会进来两次
5. **查**——跨篇检索问答，答案必须指回原文

## 它不做什么

- 不做职业建议（那是 ArmilGrid 的活）
- 不替你下结论，只交代原文说了什么、值不值得继续读
- 抓不到就明说，不补写、不猜正文

## 装

```powershell
git clone https://github.com/Duckweed-yhb/SlipAtlas.git
```

把整个仓库放进技能目录（别只拷 `SKILL.md`，`tools/` 和 `schema.md` 会被用到）：

```powershell
Copy-Item -Recurse SlipAtlas "$env:USERPROFILE\.claude\skills\slipatlas"
Copy-Item SlipAtlas\config.example.toml "$env:USERPROFILE\.claude\skills\slipatlas\config.toml"
```

`config.toml` 里填阅读库路径；不填就用默认 `E:/future/yhb/07-阅读与藏书/Lifetime-Archive`。

## 用

| 指令 | 干什么 |
| --- | --- |
| `/slip intake <链接>` | 抓一篇，落盘，打标 |
| `/slip intake <链接> --text-file body.md` | 抓不到时，粘贴正文再落盘 |
| `/slip digest` | 处理 `status: inbox` 的队列，补摘要与标签 |
| `/slip ask <问题>` | 跨篇检索问答 |
| `/slip list` | 看还有多少没处理 |

## 数据落在哪

```
Lifetime-Archive/
└─ sources/
   ├─ 2026/
   │  └─ 2026-11-19-<slug>.md     # 一篇一个文件，字段见 schema.md
   └─ index.md                    # 由 tools/index.py 生成，不要手改
```

书和影视继续走 `Lifetime-Archive_总表.xlsx`（14 列那张，不动它）；文章和视频走 `sources/`。

## 现状

v0.1.0，骨架可用但不是全功能。

| 能力 | 状态 |
| --- | --- |
| `tools/index.py` 生成索引 | 可用 |
| `tools/intake.py` 一般网页 | 可用（装了 `trafilatura` 才干净，否则是粗糙正则） |
| `tools/intake.py --text-file` 粘贴正文 | 可用 |
| 公众号直抓 | 占位：需要 `config.toml` 里的 cookie，反爬改动频繁 |
| 视频转文字 | 占位：有字幕走 `--text-file`，无字幕接 whisper |

字段与约定见 [schema.md](schema.md)，agent 行为规范见 [SKILL.md](SKILL.md)。
