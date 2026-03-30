# Feishu 终稿工作流

这个文件规定从格式标注到飞书写回，再到纠错监督回传的固定闭环。纠错能力内置在 `article-note-mentor` 主 skill 中，不新增第二个对外入口。

## 前提

- 已配置 `FEISHU_APP_ID`
- 已配置 `FEISHU_APP_SECRET`
- 飞书应用已被添加到目标文档
- 已有主 Markdown、`.format-annotations.md` 与 `.format-annotations.json`
- 终稿脚本入口固定为 `scripts/feishu_docx_finalize.py`

## 推荐入口

- `--mode preview`：只做联机预览，不写回
- `--mode apply`：按当前候选直接写回
- `--mode audit`：输出 `.feishu-audit.md/.json`
- `--mode finalize`：推荐入口，固定执行 `preview -> apply -> audit -> 安全补打 -> final preview`

## 固定顺序

1. 读取目标飞书文档块树与主 Markdown
2. 读取或重建格式标注 JSON
3. 生成 `preview` 报告，确认候选动作仍然停留在样式落地层
4. `apply` 前生成本地 backup
5. 执行样式落地、块类型替换、空白收缩和残余管道表格重建
6. 重新拉取飞书块树并执行 `audit`
7. 如果 audit 中仍存在可安全自动修复项，则执行一轮补打
8. 做 `final preview`，确认 `candidate_updates = 0`，或只剩稳定的非自动修复残差

## 验收规则

- `table_candidate` 不能因为文档别处存在真实表格而算满足，必须在注释位置附近命中
- 若目标位置仍是 Markdown 管道表格，应重建为真实 Feishu table block
- 若目标位置已是原生 table block，应保留并验收位置、行列和内容是否匹配
- `highlight_color` 必须覆盖关键纠偏句、边界提醒句、Conclusion 收束句，而不是只处理标签前缀
- `bullet_list / numbered_list / quote_block` 要验收块类型是否真正落地，而不是只看文本里是否出现 `•`、`1.` 或引用语气
- `tighten_spacing` 只允许删除纯空文本块和明显冗余空行；`preserve_spacing` 要保护标题、表格、公式、引用前后的留白

## 安全补打边界

- 允许自动补打：粗体、斜体、行内代码、受控颜色、列表、引用、明显空白收缩、按位置重建残余 Markdown 管道表格
- 不允许自动补打：正文事实改写、章节重排、方法重写、已有真实表格破坏、模糊公式猜测性转换
- 任何需要删除旧块再插入新块的动作，都必须走“先建后删，删失败就回滚”的安全路径

## 归档要求

- 主笔记继续保留原 Markdown 文件
- 格式标注固定写出 `.format-annotations.md/.json`
- 验收报告固定写出 `.feishu-audit.md/.json`
- 预览与写回报告、`apply-result.json`、`backup/blocks.json`、`backup/raw_content.txt` 要保留在同一归档层，方便回退和幂等检查

## 幂等要求

- 第二次 `preview` 的候选修改应接近 0
- 第二次 `finalize` 不应继续生成新的可自动修复项
- 颜色、列表、引用、表格和留白都不允许来回抖动

## 当前实现提醒

当前主样本飞书文档 `W9k1d9OIfoW9bDxQKe9cwOGdnPe` 已存在真实表格块与引用容器，所以终稿层默认优先利用这些结构，而不是重新把整篇导入成另一套版式；真正需要处理的是残余管道表格、缺失颜色、未命中的列表/引用块，以及局部空白节奏。
