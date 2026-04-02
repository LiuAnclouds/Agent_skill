# Agent_skill

个人自用的 Codex skills 仓库，按技能目录拆分保存，方便在不同设备之间同步、安装和更新。

当前仓库包含这些 skills：

- `article-note-mentor`
  - 中文研究型论文笔记主流程。覆盖读论文、五段式深度笔记、格式标注、Feishu 终稿、Markdown 归档。
- `article-note-feishu-polish`
  - 兼容入口。实际能力已并入 `article-note-mentor`，保留旧命令和迁移说明。
- `dataset-analysis-mentor`
  - 深度数据分析工作流，适合 EDA、图数据、时序 / 漂移 / 缺失 / 长尾 / 异常检测场景。
- `read-paper-mentor`
  - 交互式论文阅读、翻译、公式讲解、实验解释、批判性理解。
- `research-figure-mentor`
  - 论文级图表与结构图工作流，适合系统架构图、流程图、数据图、神经网络结构图与两轮校验式出图。
- `teach-code-mentor`
  - 面向教学和自学的代码讲解 skill，适合按执行流或数据流做系统化解释。
- `graduation-project-dgraph-mentor`
  - 面向 `Graduation_Project` 的持久化项目上下文 skill。自动维护项目结构、`experiment/` 代码地图、数据集统计、AUC 目标、实验对比规则和最近 5 次变更记忆。
- `pua`
  - 在任务反复失败、停滞或被动等待时触发的强约束推进 skill，用来强制扩展排查路径并避免轻易放弃。
- `.system/`
  - 同步保存一组系统级 skills 与工具资源，当前包含：
    - `imagegen`
    - `openai-docs`
    - `plugin-creator`
    - `skill-creator`
    - `skill-installer`

## 仓库结构

```text
Agent_skill/
├─ skills/
│  ├─ .system/
│  │  ├─ imagegen/
│  │  ├─ openai-docs/
│  │  ├─ plugin-creator/
│  │  ├─ skill-creator/
│  │  └─ skill-installer/
│  ├─ article-note-feishu-polish/
│  ├─ article-note-mentor/
│  ├─ dataset-analysis-mentor/
│  ├─ graduation-project-dgraph-mentor/
│  ├─ pua/
│  ├─ read-paper-mentor/
│  ├─ research-figure-mentor/
│  └─ teach-code-mentor/
├─ scripts/
│  ├─ install_windows.ps1
│  └─ install_unix.sh
├─ LICENSE
└─ README.md
```

## Codex 的技能加载位置

Codex 会从下面的位置自动发现 skills：

- Windows 默认路径：`%USERPROFILE%\.codex\skills\`
- macOS / Linux 默认路径：`~/.codex/skills/`
- 如果你设置了 `CODEX_HOME`，则实际路径是：`$CODEX_HOME/skills/`

普通 skill 通常满足这种结构：

```text
<codex-home>/skills/<skill-name>/SKILL.md
```

例如：

```text
C:\Users\<你的用户名>\.codex\skills\article-note-mentor\SKILL.md
```

系统 bundle 下的 skill 则位于：

```text
<codex-home>/skills/.system/<skill-name>/SKILL.md
```

## 很重要的目录说明

不要把这个仓库直接克隆成：

```text
%USERPROFILE%\.codex\skills\Agent_skill
```

这样不会被 Codex 直接当成技能目录加载，因为 Codex 识别的是：

```text
skills/<skill-name>/SKILL.md
```

而不是：

```text
skills/Agent_skill/skills/<skill-name>/SKILL.md
```

正确做法是：

1. 先把仓库 `git clone` 到任意普通目录。
2. 再把仓库里的 `skills/` 内容同步到本机的 `~/.codex/skills/`。

注意：不要在 shell 里直接依赖 `skills/*` 这种 glob 去复制，因为它通常不会包含隐藏目录 `.system/`。

本仓库已经提供了安装脚本来做这件事，默认会镜像同步所有顶层 skill 目录和 `.system/` bundle。

## 在其他设备上安装

### Windows

1. 先把仓库克隆到任意目录，例如：

```powershell
git clone https://github.com/LiuAnclouds/Agent_skill.git D:\tools\Agent_skill
```

2. 运行安装脚本：

```powershell
powershell -ExecutionPolicy Bypass -File D:\tools\Agent_skill\scripts\install_windows.ps1
```

默认会安装到：

```text
%USERPROFILE%\.codex\skills\
```

如果你设置了 `CODEX_HOME`，脚本会优先安装到：

```text
$env:CODEX_HOME\skills\
```

3. 重启 Codex，或者新开一个 Codex 会话。

### macOS / Linux

1. 克隆仓库：

```bash
git clone https://github.com/LiuAnclouds/Agent_skill.git ~/Agent_skill
```

2. 运行安装脚本：

```bash
bash ~/Agent_skill/scripts/install_unix.sh
```

默认会安装到：

```text
~/.codex/skills/
```

如果设置了 `CODEX_HOME`，则会安装到：

```text
$CODEX_HOME/skills/
```

3. 重启 Codex，或者新开一个 Codex 会话。

## 只安装部分 skills

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File D:\tools\Agent_skill\scripts\install_windows.ps1 -SkillNames read-paper-mentor,pua,.system
```

### macOS / Linux

```bash
bash ~/Agent_skill/scripts/install_unix.sh read-paper-mentor pua .system
```

## 手动安装

如果你不想用脚本，也可以手动镜像复制：

1. 创建目标目录：

```text
<codex-home>/skills/
```

2. 推荐直接同步整个 `skills/` 目录内容：

### Windows

```powershell
robocopy .\skills $env:USERPROFILE\.codex\skills /MIR /XD __pycache__ backups /XF *.pyc
```

如果你设置了 `CODEX_HOME`，把目标目录换成：

```powershell
$env:CODEX_HOME\skills
```

### macOS / Linux

```bash
rsync -a --delete --exclude "__pycache__" --exclude "backups" --exclude "*.pyc" ./skills/ "${CODEX_HOME:-$HOME/.codex}/skills/"
```

3. 如果你只想手动复制部分目录，至少要显式包含这些路径：

```text
Agent_skill/skills/article-note-mentor        -> <codex-home>/skills/article-note-mentor
Agent_skill/skills/dataset-analysis-mentor    -> <codex-home>/skills/dataset-analysis-mentor
Agent_skill/skills/read-paper-mentor          -> <codex-home>/skills/read-paper-mentor
Agent_skill/skills/research-figure-mentor     -> <codex-home>/skills/research-figure-mentor
Agent_skill/skills/teach-code-mentor          -> <codex-home>/skills/teach-code-mentor
Agent_skill/skills/article-note-feishu-polish -> <codex-home>/skills/article-note-feishu-polish
Agent_skill/skills/pua                        -> <codex-home>/skills/pua
Agent_skill/skills/.system                    -> <codex-home>/skills/.system
```

4. 确认复制后存在：

```text
<codex-home>/skills/<skill-name>/SKILL.md
```

## 更新到最新版本

如果另一台设备已经有这个仓库，只要：

1. 进入仓库目录：

```bash
cd <your-cloned-Agent_skill-repo>
```

2. 拉取最新代码：

```bash
git pull
```

3. 重新运行安装脚本：

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows.ps1
```

### macOS / Linux

```bash
bash ./scripts/install_unix.sh
```

4. 重启 Codex 或开新会话。

## 验证是否安装成功

安装后，检查目标目录下是否出现这些文件夹：

```text
<codex-home>/skills/article-note-mentor/
<codex-home>/skills/dataset-analysis-mentor/
<codex-home>/skills/read-paper-mentor/
<codex-home>/skills/research-figure-mentor/
<codex-home>/skills/teach-code-mentor/
<codex-home>/skills/article-note-feishu-polish/
<codex-home>/skills/pua/
<codex-home>/skills/.system/openai-docs/
```

并且普通 skill 目录里应包含 `SKILL.md`，`.system/<skill-name>/` 里也应包含 `SKILL.md`。

## 备注

- `article-note-feishu-polish` 是兼容层，不是新的主流程。需要论文笔记与飞书终稿时，实际能力以 `article-note-mentor` 为准。
- 部分 skill 依赖你本机已有环境变量或外部服务权限。例如 Feishu 相关流程通常需要本机配置 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`。
- 安装脚本现在会镜像同步目标目录。也就是说，如果仓库里已经删除某个文件，重新运行安装脚本时，本机对应 skill 目录中的旧文件也会被删除。
- 仓库包含 `.system/` bundle；如果你手动复制，请不要漏掉这个隐藏目录。
