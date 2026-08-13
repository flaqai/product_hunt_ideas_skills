# Product Hunt 2026-08-12：真实运行示例

[返回示例索引](../README.md) · [查看完整产品列表](all-products.md) · [查看联系审计](contact-audit.md)

本示例由 `product-hunt-daily` Skill 通过 Codex 内置浏览器采集，全程未使用 Product Hunt API、Token、RSS、搜索引擎或第三方榜单。

## 运行结果

- Product Hunt 日期：2026-08-12（`America/Los_Angeles`）
- 历史日状态：`completed`
- All 官方视图：17 个编号产品
- Featured 官方视图：17 个编号产品
- 两个官方视图的去重并集：18 个产品
- 产品详情页：18/18 已打开并核对
- 官方 Visit 入口：首页检查 18/18
- Product Hunt 明确标注的 Launch Team/Hunter：18/18 已记录
- 首页直接公开邮箱：5 个产品
- 仅公开联系表单：2 个产品
- 官网可访问但首页未公开邮箱/表单：9 个产品（其中若干提供 GitHub、LinkedIn、X 或 Discord）
- 联系页面不可用：2 个产品（Grok 进入 X 登录页；RightCard 的 App Store 链接发生地区重定向）

## 示例文件

- [`all-products.md`](all-products.md)：完整可读榜单
- [`contacts.json`](contacts.json)：规范化完整数据
- [`contacts.csv`](contacts.csv)：便于表格分析的导出
- [`contact-audit.md`](contact-audit.md)：联系信息覆盖与缺口
- [`sources.md`](sources.md)：Product Hunt、Maker 与官网证据清单
- [`browser-capture.json`](browser-capture.json)：浏览器原始结构化观察

## 官方页面差异

Product Hunt 的历史页本身存在持久差异，并非采集器丢行：

- Linforge（官网编号 17）只出现在 Featured。
- Statewave（官网编号 20）只出现在 All。
- 官网未展示编号 18、19 的产品卡片。
- 页面中的 Framer AI Agents 没有榜单编号，属于 promoted 卡片，已排除。
- All 页的 DOM 顺序不是排名顺序，例如 3 会先于 2、8 会先于 6/7；导出按页面打印编号排序。

因此结果同时保存两套概念：`displayed_rank` 是 Product Hunt 打印的原始编号，`rank` 是对 18 个官方可见产品去重后的连续导出序号。Linforge 被标记为 `observed_in_all: false`、`observed_in_featured: true`，不会伪装成 All 页产品。

## Skill 展现出的能力

1. 无 Token 获取指定日期 All 与 Featured 两个官方视图。
2. 排除无编号推广卡，按 canonical Product Hunt URL 去重。
3. 打开每个产品页，采集名称、tagline、描述、票数、评论数、Topics、官方 Visit URL 与 Launch Team/Hunter。
4. 打开官方站点首页，收集公开邮箱、联系表单及职业渠道，并保留证据 URL。
5. 对官网视图差异、登录阻断、地区重定向和异常邮箱域名进行显式标注。
6. 生成可读 Markdown、规范化 JSON、详细 CSV、联系证据审计和来源清单。

## 本次发现并修复的问题

- 修复了依赖 DOM 顺序导致的排名错乱：新增显示编号排序和 `displayed_rank`。
- 修复了大页面完整 DOM 快照超时：改用局部正文/链接查询和分段收集。
- 修复了“Featured 必须永远是 All 子集”的过度假设：默认仍严格校验，只有在两次官方复核均一致且显式开启 `allow_official_view_union` 时，才允许官方视图并集恢复。
- 新增 `observed_in_all`、`observed_in_featured`、`recovered_from_view`，让恢复来源可审计。
- CSV 现在保留完整产品描述、媒体、链接、Maker、页面检查状态和视图证据，不再只是邮箱表。
- 新增自动生成 `sources.md`，补齐标准交付物。
- 所有 18 个产品的联系研究均有明确状态；没有邮箱时不会猜测。

## 数据使用说明

票数和评论数是 2026-08-13 访问历史页时页面显示的当前值，可能与 2026-08-12 当天收盘值不同。团队仅表示 Product Hunt 在该 launch 上显示的 Launch Team/Hunter，不等于公司的完整组织架构。公开联系方式也只反映访问时官网首页可见信息。
