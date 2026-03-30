# article-note-feishu-polish 迁移说明

`article-note-feishu-polish` 已并入 `article-note-mentor`，不再作为独立正式能力维护。

## 已迁入主 skill 的内容

- 格式评论阶段
- Feishu 原位终稿阶段
- backup / preview / apply 工作流
- 标题、引用、列表、颜色、留白、公式与表格处理规则

## 新的正式入口

- `C:\Users\徐康杰\.codex\skills\article-note-mentor\SKILL.md`
- `C:\Users\徐康杰\.codex\skills\article-note-mentor\scripts\feishu_docx_finalize.py`

## 旧路径如何处理

- 旧 `SKILL.md` 只保留兼容说明
- 旧 `openai.yaml` 只提示改用主 skill
- 旧 `scripts/feishu_docx_polish.py` 只做参数转发

## 备注

如果你之前只记得旧 skill 名称，也应改用主 skill，因为现在写作深化、格式评论、Feishu 终稿和 Markdown 归档都被视为同一条流水线。
