# HS Open Skills

当前公开发布一个面向外贸业务的 Agent Skill：信用证审核。

## 信用证审核 Skill

[`lc-expert-o`](https://github.com/globalwinhs/hs-open-skills/tree/main/skills/lc-expert-o) 用于审核信用证草稿及信用证项下交单文件，识别软条款、不符点、期限、运输、保险、银行、单据和合规风险，并给出可执行的改证或改单建议。

公开版已移除特定企业、客户、银行、订单、港口、本机路径和内部政策等私有信息。首次使用时，可在用户确认后把可复用的企业审证偏好保存在用户自己的电脑上；不会把信用证号码、客户资料、交易文件、账号、密码或密钥写入画像。

## 方法一：使用 npx 安装

适用于支持 [`skills` CLI](https://github.com/vercel-labs/skills) 的本地 Agent，例如 Claude Code 和 Codex。需要先安装 Node.js。

交互式安装：

```bash
npx skills add globalwinhs/hs-open-skills --skill lc-expert-o
```

安装到当前用户、供所有项目使用：

```bash
npx skills add globalwinhs/hs-open-skills --skill lc-expert-o --global
```

指定安装到 Claude Code：

```bash
npx skills add globalwinhs/hs-open-skills --skill lc-expert-o --agent claude-code --global --yes
```

指定安装到 Codex：

```bash
npx skills add globalwinhs/hs-open-skills --skill lc-expert-o --agent codex --global --yes
```

`skills` CLI 默认会收集匿名安装遥测。如需关闭，可在命令前设置 `DISABLE_TELEMETRY=1`。安装前请先阅读 Skill 的 `SKILL.md` 和 `scripts/`。

## 方法二：使用 git clone 安装

```bash
git clone https://github.com/globalwinhs/hs-open-skills.git
cd hs-open-skills
```

Claude Code 全局安装：

```bash
mkdir -p ~/.claude/skills
cp -R skills/lc-expert-o ~/.claude/skills/
```

Codex 全局安装：

```bash
mkdir -p ~/.codex/skills
cp -R skills/lc-expert-o ~/.codex/skills/
```

详细步骤及豆包工作、WorkBuddy、ChatGPT 的使用方式见：[跨平台安装与使用指引](docs/INSTALL.md)。

## ZIP 安装包

豆包工作和 WorkBuddy 可下载 [`lc-expert-o.zip`](https://github.com/globalwinhs/hs-open-skills/raw/refs/heads/main/packages/lc-expert-o.zip)，再从客户端的技能页面上传。

## 首次使用

安装后可以这样开始：

```text
请使用信用证审核 Skill。先读取 SKILL.md 和相关审核框架，检查这是一份信用证草稿、交单文件还是专项复核。
如果需要建立企业审证画像，先列出最少需要补充的资料和拟保存内容，等我确认后再保存。不得把客户资料、信用证号码、交易文件、密码或密钥写入长期配置。
```

随后上传信用证或交单文件，并说明审核目标。例如：

```text
请审核这份信用证草稿，先列出高风险条款和无法核实项，再给出可直接发送给客户的改证清单。
```

## 运行环境

- Skill 脚本只依赖 Python 标准库，建议 Python 3.9 或更高版本。
- `scripts/profile_store.py` 用于校验并保存本机企业审证画像；保存动作必须带 `--confirm`。
- ChatGPT 等不能直接运行本地脚本的平台仍可按 `SKILL.md` 执行审核，但需人工保存画像并核对输出。

## 安全边界

- 安装第三方 Skill 前，请先阅读 `SKILL.md`、`references/` 和 `scripts/`。
- 不要把账号、密码、API Key、私钥、私人联系方式或完整交易文件保存为长期画像。
- 制裁、出口管制、银行政策和公司状态会变化，使用时应核查最新官方来源与日期。
- 本 Skill 提供业务风险辅助，不替代银行、律师、保险机构或监管部门的最终判断。

## 许可证

本仓库按 [MIT License](LICENSE) 开放。第三方规则、网站数据、商标及用户提交资料仍归各自权利人所有。

## 参考文档

- [`skills` CLI 官方仓库](https://github.com/vercel-labs/skills)
- [`skills` CLI 官方文档](https://www.skills.sh/docs/cli)
- [Claude Code Skills 官方文档](https://code.claude.com/docs/en/skills)
- [WorkBuddy 技能官方文档](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)
- [ChatGPT Projects 官方帮助](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)
- [创建和编辑 GPTs 官方帮助](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts)

