# Product Hunt Daily Skill

一个通过 Codex 内置浏览器采集 Product Hunt 每日榜单的开源 Skill。无需 Product Hunt API Token，可获取指定日期的 All/Featured 产品、产品详情、Launch Team/Hunter，以及官网公开的职业联系方式和联系渠道。

Skill 入口：[product-hunt-daily/SKILL.md](product-hunt-daily/SKILL.md)

## 真实运行示例

示例按 Product Hunt 日期（`America/Los_Angeles`）归档。每个日期目录都包含可读榜单、规范化 JSON、CSV、联系审计、来源清单和浏览器原始观察。

<!-- examples-table:start -->
| 日期 | 状态 | 官方可见产品 | Featured | 详情页 | 联系检查 | 公开邮箱 | 示例 |
|---|---|---:|---:|---:|---:|---:|---|
| 2026-08-12 | completed | 18 | 17 | 18/18 | 18/18 | 5 | [查看示例](examples/2026-08-12/) |
<!-- examples-table:end -->

## 示例目录约定

```text
examples/
└── YYYY-MM-DD/
    ├── README.md             单日结果、异常与能力说明
    ├── all-products.md       可读产品列表
    ├── contacts.json         规范化完整数据
    ├── contacts.csv          表格导出
    ├── contact-audit.md      联系证据覆盖审计
    ├── sources.md            来源清单
    └── browser-capture.json  内置浏览器原始观察
```

新增日期时，在 `examples/YYYY-MM-DD/` 保存同一组文件，再运行 `python3 product-hunt-daily/scripts/update_example_index.py` 自动校验并更新索引。日期必须使用 Product Hunt 的 `America/Los_Angeles` 日历日；当天尚未结束的样例标记为 `in_progress`，历史日期完成核验后标记为 `completed`。

## 数据边界

- 示例只记录网页在采集时公开显示的内容，不使用 API、Token 或第三方榜单。
- 票数和评论数是访问时页面显示值，历史页也可能继续变化。
- Launch Team/Hunter 不等于公司的完整组织架构。
- 不猜测邮箱；每条联系方式都保留公开来源和置信度。
- Product Hunt 两个官方视图不一致时，同时保留原始编号和视图来源，不伪造缺号产品。
