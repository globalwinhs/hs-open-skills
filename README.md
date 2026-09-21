# HS Open Skills

一组面向外贸业务的开放 Agent Skills。当前包含信用证审核、目标市场分析、批量客户开发和单一客户背调。

这 4 个 Skill 已移除特定企业、客户、银行、订单、港口、价格底线和本机路径等私有信息。首次使用时，可在用户确认后把可复用的企业或产品画像保存在用户自己的电脑上；不会把账号、密码、密钥、客户名单或交易文件写进画像。

## 包含的 Skills

| Skill | 用途 | 主要输出 |
|---|---|---|
| [`lc-expert-skill-2-o`](skills/lc-expert-skill-2-o/) | 审核信用证草稿及信用证项下交单文件 | 风险、不符点、改证或改单建议 |
| [`hs-target-market-analyze-o`](skills/hs-target-market-analyze-o/) | 比较出口产品适合优先进入的国家或地区 | 市场排序、证据、障碍和验证动作 |
| [`hs-bulk-customer-develop-o`](skills/hs-bulk-customer-develop-o/) | 批量寻找、核实、去重并排序 B2B 潜在客户 | 客户名单、公开联系方式、匹配理由 |
| [`hs-customer-background-servey-o`](skills/hs-customer-background-servey-o/) | 对单一询盘客户或指定公司做背景调查 | 主体、业务、采购信号、联系人和风险 |

> `servey` 沿用原 Skill 名称，避免安装后出现名称不一致；它表示 customer background survey。

## 最快安装

- **豆包工作 / WorkBuddy**：从 [`packages/`](packages/) 下载对应 ZIP，在客户端的技能页面选择“上传技能”。
- **Claude Code**：把所需 Skill 文件夹复制到 `~/.claude/skills/`，或复制到项目内的 `.claude/skills/`。
- **ChatGPT**：使用“项目”或“自定义 GPT”加载 `SKILL.md` 与参考资料。ChatGPT 网页版不是按本地 `SKILL.md` 目录原生安装，完整步骤见安装说明。

详细步骤：[跨平台安装与使用指引](docs/INSTALL.md)

## 首次使用

安装后直接描述任务即可。建议第一次这样说：

```text
我要使用这个 Skill。请先读取 SKILL.md 和 profile-schema.md，检查我是否需要建立本机/项目画像。
先列出需要我补充的最少资料和拟保存内容；未经我确认，不要保存画像，也不要把客户资料、密码、密钥或交易文件写入长期配置。
```

随后按 Skill 提示提供文件或资料。例如：

- 信用证审核：“请审核这份信用证草稿，先列高风险条款，再给出可直接发送给客户的改证清单。”
- 目标市场分析：“请比较德国、波兰、土耳其三个市场，判断我的工业阀门应优先进入哪里，并保留来源链接。”
- 批量客户开发：“在已确定的德国市场内，寻找 30 家符合条件的工业阀门进口商，不要猜测邮箱。”
- 单一客户背调：“请核实这家询盘公司的主体、主营业务、产品匹配、公开联系人和交易风险。”

## 运行环境

- 只有 Python 标准库依赖，建议 Python 3.9 或更高版本。
- `scripts/profile_store.py` 用于验证并保存本机画像；保存动作必须带 `--confirm`。
- 市场分析、批量客户开发、单一客户背调包含输入校验和报告生成脚本。
- ChatGPT 等无法直接运行本地脚本的平台仍可按 `SKILL.md` 完成分析，但需要人工保存画像并核对输出格式。

## 安全与边界

- 安装第三方 Skill 前，请先阅读 `SKILL.md` 和 `scripts/`。
- 不要把账号、密码、API Key、私钥、私人联系方式或完整交易文件保存为长期画像。
- 联系方式只能来自公开可核验来源，不猜测、不拼接。
- 信用证、制裁、出口管制、公司状态等会变化；使用时应核查最新官方来源和日期。
- Skill 提供业务辅助，不替代银行、律师、保险机构或监管部门的最终判断。

## 许可证

本仓库按 [MIT License](LICENSE) 开放。第三方规则、网站数据、商标及用户提交资料仍归各自权利人所有。

## 参考平台文档

- [Claude Code Skills 官方文档](https://code.claude.com/docs/en/skills)
- [WorkBuddy 技能官方文档](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)
- [ChatGPT Projects 官方帮助](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)
- [创建和编辑 GPTs 官方帮助](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts)

