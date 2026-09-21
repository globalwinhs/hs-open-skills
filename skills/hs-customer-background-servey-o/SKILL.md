---
name: hs-customer-background-servey-o
description: 对单一询盘客户或指定公司进行主体核实、业务判断、产品匹配、采购信号、公开联系人和风险调查，形成带来源的背调报告。首次使用可建立本机交易风险画像；不用于批量找客户，也不猜测私人联系方式。
---

# 开源单一客户背调

回答五个问题：主体是否真实、实际做什么、是否可能购买、应该联系谁、报价或交易前还要核实什么。

## 首次使用

运行 `python3 scripts/profile_store.py show`。没有配置时，参考 [交易风险画像字段](references/profile-schema.md)，只收集可跨客户复用的产品匹配和风险政策。展示拟保存内容和路径，获得确认后运行：

```bash
python3 scripts/profile_store.py save --input <风险画像.json> --confirm
```

用户可以跳过保存。不得把本次客户名称、询盘、邮箱、调查结果或交易资料写入长期画像。

## 输入

- 公司名称、询盘人姓名与邮箱
- 官网、域名、电话、地址或社交主页
- 询盘内容、产品、数量、交付地和付款要求
- 用户已经掌握的文件或线索

只有同名实体无法区分且会改变结论时才追问。

## 调查要求

1. 先核实主体，再判断业务和产品匹配。
2. 公司注册、监管披露、认证机构、企业官网等一手来源优先。
3. 每条关键结论标记为 `verified`、`probable`、`unverified` 或 `conflicting`。
4. 公开联系人必须保留出处；不得猜测邮箱、手机号、职务或个人身份。
5. 没有公开证据只能写“未发现”，不能写“不存在”。
6. 付款异常、域名异常、身份错配、制裁、诉讼和信用风险要给出人工复核建议，不替代律师、银行、保险机构或合规审查。
7. 当前法规、制裁和工商状态必须在本次调查中核查日期，不从长期画像继承。

## 交付

按 [数据模板](assets/input-template.json) 整理结果，运行：

```bash
python3 scripts/validate_input.py --input <背调数据.json>
python3 scripts/background_report.py --input <背调数据.json> --out-dir <输出目录>
```

检查 `customer-background.md` 和 `public-contacts.csv` 后交付。
