# Agent_skill

面向 AgentSkills 生态的可复用 skill 仓库，当前同时服务 Codex 和 OpenClaw。

仓库保持平铺的 `skills/` 结构，方便同步、安装、更新，以及在不同 CLI 之间复用同一套 skill 目录。

## 当前包含的 skills

- `article-note-mentor`
  - 中文研究型论文笔记主流程。覆盖读论文、五段式深度笔记、格式标注、Feishu 终稿、Markdown 归档。
- `article-note-feishu-polish`
  - 兼容入口。实际能力已并入 `article-note-mentor`，保留旧命令和迁移说明。
- `dataset-analysis-mentor`
  - 深度数据分析工作流，适合 EDA、图数据、时序 / 漂移 / 缺失 / 长尾 / 异常检测场景。
- `graduation-project-dgraph-mentor`
  - 面向 `Graduation_Project` 的持久化项目上下文 skill。自动维护项目结构、`experiment/` 代码地图、数据集统计、AUC 目标、实验对比规则和最近 5 次变更记忆。
- `moonrabbit`
  - 跨 CLI 的人格化聊天主 skill。负责 MoonRabbit 的活跃 / 理智 / 引导 / 安全暧昧四种模式、开场白、停答暗号和安全红线。
- `moonrabbit-memory`
  - MoonRabbit 的配套记忆 skill。负责联系人键、画像压缩、停答状态、恢复暗号与 OpenClaw / 微信映射示例。
- `pua`
  - 在任务反复失败、停滞或被动等待时触发的强约束推进 skill，用来强制扩展排查路径并避免轻易放弃。
- `read-paper-mentor`
  - 交互式论文阅读、翻译、公式讲解、实验解释、批判性理解。
- `research-figure-mentor`
  - 论文级图表与结构图工作流，适合系统架构图、流程图、数据图、神经网络结构图与两轮校验式出图。
- `teach-code-mentor`
  - 面向教学和自学的代码讲解 skill，适合按执行流或数据流做系统化解释。
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
│  ├─ article-note-feishu-polish/
│  ├─ article-note-mentor/
│  ├─ dataset-analysis-mentor/
│  ├─ graduation-project-dgraph-mentor/
│  ├─ moonrabbit/
│  │  ├─ agents/
│  │  └─ references/
│  ├─ moonrabbit-memory/
│  │  ├─ agents/
│  │  └─ references/
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

## Skill 根目录约定

普通 skill 都遵循：

```text
<skill-root>/<skill-name>/SKILL.md
```

例如：

```text
~/.codex/skills/moonrabbit/SKILL.md
~/.openclaw/skills/moonrabbit/SKILL.md
```

不要把整个仓库直接克隆到：

```text
~/.codex/skills/Agent_skill
```

或：

```text
~/.openclaw/skills/Agent_skill
```

因为 CLI 识别的是 `skills/<skill-name>/SKILL.md`，不是 `skills/Agent_skill/skills/<skill-name>/SKILL.md`。

正确做法是：

1. 把仓库克隆到任意普通目录。
2. 再把仓库里的 `skills/` 内容同步到目标 CLI 的技能目录。

## 安装目标

### Codex

- Windows 默认路径：`%USERPROFILE%\.codex\skills\`
- macOS / Linux 默认路径：`~/.codex/skills/`
- 如果设置了 `CODEX_HOME`，则实际路径是：`$CODEX_HOME/skills/`

### OpenClaw

- 共享技能路径推荐：`~/.openclaw/skills/`
- 如果设置了 `OPENCLAW_HOME`，则实际路径是：`$OPENCLAW_HOME/skills/`

OpenClaw 安装到共享技能目录后，还需要你在 agent 配置里显式挂到 allowlist，或者让 agent 使用无限制 skills。

## 安装脚本

仓库提供双端安装脚本，并新增了目标参数：

- `codex`
- `openclaw`
- `all`

默认目标仍然是 `codex`，这样不会破坏现有用法。

### Windows

```powershell
git clone https://github.com/LiuAnclouds/Agent_skill.git D:\tools\Agent_skill

powershell -ExecutionPolicy Bypass -File D:\tools\Agent_skill\scripts\install_windows.ps1
```

只装 MoonRabbit 到 OpenClaw：

```powershell
powershell -ExecutionPolicy Bypass -File D:\tools\Agent_skill\scripts\install_windows.ps1 -Target openclaw -SkillNames moonrabbit,moonrabbit-memory
```

同时同步到 Codex 和 OpenClaw：

```powershell
powershell -ExecutionPolicy Bypass -File D:\tools\Agent_skill\scripts\install_windows.ps1 -Target all -SkillNames moonrabbit,moonrabbit-memory
```

### macOS / Linux

```bash
git clone https://github.com/LiuAnclouds/Agent_skill.git ~/Agent_skill

bash ~/Agent_skill/scripts/install_unix.sh
```

只装 MoonRabbit 到 OpenClaw：

```bash
bash ~/Agent_skill/scripts/install_unix.sh --target openclaw moonrabbit moonrabbit-memory
```

同时同步到 Codex 和 OpenClaw：

```bash
bash ~/Agent_skill/scripts/install_unix.sh --target all moonrabbit moonrabbit-memory
```

## 只安装部分 skills

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File D:\tools\Agent_skill\scripts\install_windows.ps1 -SkillNames read-paper-mentor,pua
```

### macOS / Linux

```bash
bash ~/Agent_skill/scripts/install_unix.sh read-paper-mentor pua
```

## `.system` 的处理

仓库包含 `.system/` bundle。

- 对 Codex，默认会跟随自动安装一起同步。
- 对 OpenClaw，自动安装时默认跳过 `.system`，避免无意覆盖或混入 CLI 自带的系统 skill。
- 如果你明确知道自己在做什么，仍然可以显式选择 `.system`。

## 手动安装

如果你不想用脚本，也可以手动同步：

### Codex

```bash
rsync -a --delete --exclude "__pycache__" --exclude "backups" --exclude "*.pyc" ./skills/ "${CODEX_HOME:-$HOME/.codex}/skills/"
```

### OpenClaw

```bash
rsync -a --delete --exclude "__pycache__" --exclude "backups" --exclude "*.pyc" --exclude ".system" ./skills/ "${OPENCLAW_HOME:-$HOME/.openclaw}/skills/"
```

如果是 Windows，使用 `robocopy` 把所需 skill 目录镜像到目标根目录即可。

## OpenClaw 额外一步

安装到 `~/.openclaw/skills/` 之后，推荐在 `~/.openclaw/openclaw.json` 中显式暴露 MoonRabbit：

```json
{
  "agents": {
    "defaults": {
      "skills": ["moonrabbit", "moonrabbit-memory"]
    }
  }
}
```

然后重启 OpenClaw gateway 或新开会话。

## 更新到最新版本

```bash
cd <your-cloned-Agent_skill-repo>
git pull
```

然后重新运行安装脚本：

```bash
bash ./scripts/install_unix.sh
```

或：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows.ps1
```

## 验证是否安装成功

安装后，至少确认目标目录里出现：

```text
<target-root>/moonrabbit/SKILL.md
<target-root>/moonrabbit-memory/SKILL.md
```

如果是 Codex，还应能看到你选择安装的其他 skill，以及 `.system/` 中的系统 skill。

如果是 OpenClaw，再额外确认：

- `openclaw skills info moonrabbit`
- `openclaw skills info moonrabbit-memory`

## 备注

- `moonrabbit` 是主聊天 skill，`moonrabbit-memory` 是配套记忆 skill，建议一起安装。
- MoonRabbit 带全局安全红线：一旦碰到违规或高风险内容，优先终止正常人格回复，只做最短拒绝或安全转向。
- `article-note-feishu-polish` 是兼容层，不是新的主流程。需要论文笔记与飞书终稿时，实际能力以 `article-note-mentor` 为准。
- 部分 skill 依赖你本机已有环境变量或外部服务权限。例如 Feishu 相关流程通常需要本机配置 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`。
- 安装脚本会镜像同步目标目录。仓库里删除的文件，重新安装时会从目标技能目录同步删除。
