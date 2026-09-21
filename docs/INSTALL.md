# 跨平台安装与使用指引

先从仓库首页确认你要安装的 Skill。一次只启用当前任务所需的 Skill，避免多个相近流程互相干扰。

## 1. 豆包工作

适用于“豆包工作”桌面客户端，不是普通豆包对话页。

1. 打开本仓库的 [`packages/`](https://github.com/globalwinhs/hs-open-skills/tree/main/packages) 目录，下载所需的 ZIP 文件。
2. 在豆包工作左侧进入“插件 · 技能 · 伙伴”。
3. 切换到“技能”，点击“添加” → “上传技能”。
4. 选择刚下载的 ZIP，按界面提示完成导入。
5. 新建工作任务，直接描述需求；也可以在输入框输入 `/` 或从“更多技能”中选择已安装 Skill。

首次使用建议发送：

```text
请使用刚安装的 Skill 处理这项任务。先读取 SKILL.md；如果缺少企业或产品画像，只询问会影响结果的字段。先向我展示拟保存内容，等我确认后再保存。不得保存客户资料、交易文件、密码或密钥。
```

如果你的客户端版本没有“上传技能”，可以选择“与豆包对话新建技能”，提供该 Skill 的 GitHub 文件夹链接，并要求豆包严格保留 `SKILL.md`、`references/`、`assets/` 和 `scripts/` 的相对结构。完成后检查技能详情，确认名称和说明与仓库一致。

## 2. WorkBuddy

1. 从 [`packages/`](https://github.com/globalwinhs/hs-open-skills/tree/main/packages) 下载所需的 ZIP 文件。
2. 打开 WorkBuddy 的“技能”页面，点击“添加技能”。
3. 选择“上传技能”，导入 ZIP。
4. 在“已安装”中确认 Skill 已启用。
5. 新建任务并直接描述需求；WorkBuddy 会按描述自动匹配，也可以手动选择 Skill。

WorkBuddy 官方提醒，第三方 Skill 可能读写本地文件或执行脚本。安装前应先查看来源、权限和脚本内容；涉及删除、批量写入或外部发送时，先小范围验证。

官方说明：[WorkBuddy 技能](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)

## 3. ChatGPT

ChatGPT 网页版目前不按 Claude Code/WorkBuddy 的本地 Skills 目录原生安装。下面是兼容使用方式。

### 方式 A：ChatGPT 项目

1. 新建一个 ChatGPT 项目，例如“外贸业务 Skills”。
2. 上传所需 Skill 的 `SKILL.md`、`references/` 和 `assets/` 文件。不要上传包含客户隐私或密钥的资料。
3. 在项目指令中加入：

```text
处理相关任务时，先读取已上传 Skill 的 SKILL.md，并严格按其中的输入、证据、边界和输出要求执行。
references 是规则说明，assets 是输入模板。首次建立画像前，先展示拟保存内容并等待确认；不得把客户资料、交易文件、密码或密钥写入长期画像。
如果当前环境不能运行 scripts，请按相同字段人工校验，并明确标注未执行脚本验证。
```

4. 在项目内新建对话，上传本次任务文件并描述目标。

官方说明：[Projects in ChatGPT](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)

### 方式 B：自定义 GPT

如果你的账号支持创建 GPT：

1. 把 `SKILL.md` 中的行为规则放入 GPT 的 Instructions。
2. 把 `references/` 和 `assets/` 上传为 Knowledge。
3. 按需启用网页搜索、数据分析等能力。
4. 用一份不含真实客户隐私的示例资料测试，再用于正式任务。

行为规则应放在 Instructions，参考资料放在 Knowledge。官方说明：[Creating and editing GPTs](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts)

## 4. Claude Code

Claude Code 原生支持包含 `SKILL.md` 的 Agent Skills。

### 个人安装：所有项目可用

```bash
git clone https://github.com/globalwinhs/hs-open-skills.git
mkdir -p ~/.claude/skills
cp -R hs-open-skills/skills/lc-expert-skill-2-o ~/.claude/skills/
cp -R hs-open-skills/skills/hs-target-market-analyze-o ~/.claude/skills/
cp -R hs-open-skills/skills/hs-bulk-customer-develop-o ~/.claude/skills/
cp -R hs-open-skills/skills/hs-customer-background-servey-o ~/.claude/skills/
```

### 项目安装：只在当前项目可用

在项目根目录运行：

```bash
mkdir -p .claude/skills
cp -R /path/to/hs-open-skills/skills/lc-expert-skill-2-o .claude/skills/
```

其余 Skill 按需复制。重新打开 Claude Code 后，可以直接描述任务让它自动匹配，或输入：

```text
/lc-expert-skill-2-o
/hs-target-market-analyze-o
/hs-bulk-customer-develop-o
/hs-customer-background-servey-o
```

官方说明：[Extend Claude with skills](https://code.claude.com/docs/en/skills)

## 首次画像保存

支持本地脚本的平台可在对应 Skill 目录中运行：

```bash
python3 scripts/profile_store.py show
python3 scripts/profile_store.py validate --input assets/profile-template.json
```

把模板复制为自己的 JSON 并填写后，先检查内容。只有确认无敏感字段且愿意保存时，才执行：

```bash
python3 scripts/profile_store.py save --input /path/to/profile.json --confirm
```

默认保存位置：

- macOS：`~/Library/Application Support/OpenTradeSkills/<skill>/profile.json`
- Windows：`%LOCALAPPDATA%/OpenTradeSkills/<skill>/profile.json`
- Linux：`$XDG_CONFIG_HOME/open-trade-skills/<skill>/profile.json`，未设置时使用 `~/.config/open-trade-skills/...`

如需改位置，可设置环境变量 `OPEN_TRADE_SKILLS_DATA_DIR`。

## 使用顺序建议

这三个获客 Skill 不是一回事，建议按以下顺序使用：

1. `hs-target-market-analyze-o`：先决定做哪个市场。
2. `hs-bulk-customer-develop-o`：再在确定市场内建立潜在客户名单。
3. `hs-customer-background-servey-o`：对重点客户或真实询盘做深入核实。

信用证审核 `lc-expert-skill-2-o` 是独立的成交与交付风控流程。
