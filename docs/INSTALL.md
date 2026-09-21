# 信用证审核 Skill 安装与使用指引

本公开仓库只发布 `lc-expert-skill-2-o`。安装前建议先查看 [`SKILL.md`](https://github.com/globalwinhs/hs-open-skills/blob/main/skills/lc-expert-skill-2-o/SKILL.md) 和 `scripts/`。

## 1. npx 安装

适用于支持 [`skills` CLI](https://github.com/vercel-labs/skills) 的本地 Agent。电脑需先安装 Node.js。

### 交互式安装

在希望使用 Skill 的项目目录中运行：

```bash
npx skills add globalwinhs/hs-open-skills --skill lc-expert-skill-2-o
```

安装器会列出支持的 Agent 和安装位置，按提示选择即可。项目级安装是默认方式。

### 全局安装

让 Skill 在当前用户的所有项目中可用：

```bash
npx skills add globalwinhs/hs-open-skills --skill lc-expert-skill-2-o --global
```

### 指定 Agent 并跳过交互

Claude Code：

```bash
npx skills add globalwinhs/hs-open-skills --skill lc-expert-skill-2-o --agent claude-code --global --yes
```

Codex：

```bash
npx skills add globalwinhs/hs-open-skills --skill lc-expert-skill-2-o --agent codex --global --yes
```

### 检查与更新

```bash
npx skills list
npx skills update lc-expert-skill-2-o
```

`skills` CLI 默认收集匿名安装遥测。若不希望参与，可运行：

```bash
DISABLE_TELEMETRY=1 npx skills add globalwinhs/hs-open-skills --skill lc-expert-skill-2-o
```

## 2. git clone 手动安装

先克隆仓库：

```bash
git clone https://github.com/globalwinhs/hs-open-skills.git
cd hs-open-skills
```

### Claude Code

全局安装：

```bash
mkdir -p ~/.claude/skills
cp -R skills/lc-expert-skill-2-o ~/.claude/skills/
```

只安装到当前项目：

```bash
mkdir -p .claude/skills
cp -R skills/lc-expert-skill-2-o .claude/skills/
```

重新打开 Claude Code 后，可以直接描述任务让它自动匹配，或输入：

```text
/lc-expert-skill-2-o
```

### Codex

全局安装：

```bash
mkdir -p ~/.codex/skills
cp -R skills/lc-expert-skill-2-o ~/.codex/skills/
```

只安装到当前项目：

```bash
mkdir -p .codex/skills
cp -R skills/lc-expert-skill-2-o .codex/skills/
```

## 3. 豆包工作

1. 下载 [`lc-expert-skill-2-o.zip`](https://github.com/globalwinhs/hs-open-skills/raw/refs/heads/main/packages/lc-expert-skill-2-o.zip)。
2. 在豆包工作左侧进入“插件 · 技能 · 伙伴”。
3. 切换到“技能”，点击“添加” → “上传技能”。
4. 选择 ZIP，按页面提示完成导入。
5. 新建工作任务，直接说明要审核的是信用证草稿、交单文件还是指定条款。

如果当前客户端没有“上传技能”，选择“与豆包对话新建技能”，提供本仓库中信用证审核 Skill 的 GitHub 文件夹链接，并要求保留 `SKILL.md`、`references/`、`assets/` 和 `scripts/` 的相对结构。

## 4. WorkBuddy

1. 下载 [`lc-expert-skill-2-o.zip`](https://github.com/globalwinhs/hs-open-skills/raw/refs/heads/main/packages/lc-expert-skill-2-o.zip)。
2. 打开 WorkBuddy 的“技能”页面，点击“添加技能”。
3. 选择“上传技能”，导入 ZIP。
4. 在“已安装”中确认 Skill 已启用。
5. 新建任务并描述审核目标；WorkBuddy 会按描述自动匹配，也可手动选择 Skill。

官方说明：[WorkBuddy 技能](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)

## 5. ChatGPT

ChatGPT 网页版目前不按 Claude Code 或 WorkBuddy 的本地 Skills 目录原生安装。可使用以下兼容方式。

### ChatGPT 项目

1. 新建一个 ChatGPT 项目，例如“信用证审核”。
2. 上传 `SKILL.md`、`references/profile-schema.md`、`references/review-framework.md` 和 `assets/profile-template.json`。
3. 在项目指令中加入：

```text
处理信用证相关任务时，先读取已上传的 SKILL.md，并严格按其中的审核依据、风险分级、证据边界和输出要求执行。
references 是审核框架和企业画像字段，assets 是画像模板。首次建立画像前，先展示拟保存内容并等待确认；不得把客户资料、信用证号码、交易文件、密码或密钥写入长期画像。
如果当前环境不能运行 scripts，请人工核对相同字段，并明确标注未执行脚本验证。
```

4. 在项目内新建对话，上传本次信用证或交单文件并说明审核目标。

官方说明：[Projects in ChatGPT](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)

### 自定义 GPT

如果账号支持创建 GPT：

1. 把 `SKILL.md` 的行为规则放入 GPT 的 Instructions。
2. 把 `references/` 和 `assets/` 上传为 Knowledge。
3. 按需启用网页搜索和数据分析能力。
4. 先用不含真实客户隐私的示例文件测试，再用于正式业务。

官方说明：[Creating and editing GPTs](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts)

## 6. 首次企业审证画像

支持本地脚本的平台可在 Skill 目录中运行：

```bash
python3 scripts/profile_store.py show
python3 scripts/profile_store.py validate --input assets/profile-template.json
```

把模板复制为自己的 JSON 并填写后，先检查内容。只有确认不含敏感字段且愿意保存时，才执行：

```bash
python3 scripts/profile_store.py save --input /path/to/profile.json --confirm
```

用户可以跳过画像，直接完成当前审核。画像只保存可跨项目复用的企业审证偏好，不保存客户名称、信用证号码、金额、完整单据、账号、密码或密钥。

## 7. 开始使用

```text
请使用信用证审核 Skill 审核我上传的文件。先确认审核模式和文件范围，高风险与无法核实项排在前面；每个问题写明位置、原文或事实、判断依据、可能后果和建议动作。
```

Skill 提供业务风险辅助，不替代银行最终审单、律师意见或监管裁定。
