# 贡献指南

感谢你帮助改进 Product Hunt Daily Skill。欢迎提交经过验证的日期示例、页面兼容修复、字段与校验改进、多语言文档和数据质量案例。

## 日期示例

新示例必须放在 `examples/YYYY-MM-DD/`，日期使用 Product Hunt 的 `America/Los_Angeles` 日历日，并包含：

- `README.md`
- `all-products.md`
- `contacts.json`
- `contacts.csv`
- `contact-audit.md`
- `sources.md`
- `browser-capture.json`

运行 `python3 product-hunt-daily/scripts/update_example_index.py`。脚本必须通过后才能把历史日期标为 `completed`。

## 数据要求

- 只使用 Product Hunt 和官网公开可见信息。
- 不猜测邮箱，不收集私人联系方式，不绕过登录、CAPTCHA 或访问限制。
- 不把评论者、仓库贡献者或公司员工自动标为 Product Hunt Maker。
- 保留原始排名、来源 URL、访问时间、置信度与异常说明。
- Product Hunt 官方视图不一致时，必须保存两套证据，不能虚构缺号产品。

## 翻译

简体中文 `README.md` 是默认文档，`README.en.md` 是英文完整版本。其他语言放在 `i18n/`。翻译应保持事实、数字、链接、风险说明和联盟披露一致；不要自行增加未经核实的产品能力或社区数字。

## 提交前检查

```bash
python3 product-hunt-daily/scripts/update_example_index.py
python3 product-hunt-daily/scripts/export_contacts.py examples/YYYY-MM-DD/contacts.json /tmp/contacts.csv
python3 product-hunt-daily/scripts/audit_contacts.py examples/YYYY-MM-DD/contacts.json /tmp/contact-audit.md
git diff --check
```

提交只应包含与当前改动有关的文件。欢迎在 Pull Request 中说明采集日期、浏览器阻断、视图异常和验证结果。
