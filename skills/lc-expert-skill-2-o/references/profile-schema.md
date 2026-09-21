# 企业配置字段

首次配置只保存可跨订单复用的企业政策。未确认字段保持空值，不使用示例值代替。

```json
{
  "company": {
    "beneficiary_name": "",
    "beneficiary_address": "",
    "products": [],
    "usual_currencies": []
  },
  "banking": {
    "advising_banks": [],
    "nominated_banks": [],
    "confirmation_policy": "",
    "discounting_policy": ""
  },
  "commercial_policy": {
    "accepted_credit_types": [],
    "maximum_tenor_days": null,
    "quantity_tolerance_percent": null,
    "amount_tolerance_percent": null,
    "minimum_production_days": null,
    "minimum_document_preparation_days": null
  },
  "shipping": {
    "usual_loading_ports": [],
    "accepted_incoterms": [],
    "partial_shipments_policy": "",
    "transshipment_policy": ""
  },
  "documents": {
    "normally_available": [],
    "unavailable_or_restricted": [],
    "third_party_issuers": []
  },
  "risk_policy": {
    "restricted_jurisdictions": [],
    "restricted_banks": [],
    "mandatory_manual_review_triggers": []
  },
  "delivery": {
    "preferred_report_format": "markdown",
    "preferred_output_location": "ask_each_time"
  }
}
```

限制：

- 不保存客户名单、单票金额、信用证号、完整单据或历史报告。
- 不保存网银信息、账号、密码、API Key、Token 或证书私钥。
- 制裁名单和法律规则不进入企业配置，应在审核时查询当前官方来源。
- 银行、港口、公差、期限和单据能力都是企业偏好，不是通用国际规则。

