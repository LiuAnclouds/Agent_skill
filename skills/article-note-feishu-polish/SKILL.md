---
name: article-note-feishu-polish
description: Compatibility shim only. Feishu finalization has been merged into article-note-mentor.
---

# article-note-feishu-polish

这个 skill 已并入
[$article-note-mentor](C:/Users/徐康杰/.codex/skills/article-note-mentor/SKILL.md)。

## 当前状态

- 不再作为正式独立入口使用
- 不再承载完整规则说明
- 不再维护独立的终稿工作流
- 仅保留兼容脚本和迁移说明，避免旧命令直接失效

## 正确入口

请改用 `article-note-mentor` 处理完整链路：

1. 论文读取与结构定稿
2. 内容写作与分模块深化
3. 格式评论阶段
4. Feishu 原位终稿阶段
5. Markdown 留存归档

## 兼容脚本

旧路径下的 `scripts/feishu_docx_polish.py` 仍可运行，但会转发到主 skill 的：

- `article-note-mentor/scripts/feishu_docx_finalize.py`

## 迁移说明

更多迁移细节见：

- `MIGRATION.md`
