# Product Hunt Daily Skill

<p align="center">
  <strong>无需 Product Hunt API Token，通过 Codex 内置浏览器获取指定日期的完整产品榜单、产品详情、Launch Team/Hunter 与官网公开联系渠道。</strong>
</p>

<p align="center">
  <strong>简体中文</strong> ·
  <a href="README.en.md">English</a> ·
  <a href="i18n/ja-JP.md">日本語</a> ·
  <a href="i18n/es-ES.md">Español</a> ·
  <a href="i18n/fr-FR.md">Français</a> ·
  <a href="i18n/de-DE.md">Deutsch</a> ·
  <a href="i18n/ko-KR.md">한국어</a> ·
  <a href="i18n/pt-BR.md">Português</a> ·
  <a href="i18n/README.md">12 种语言</a>
</p>

![Languages](https://img.shields.io/badge/languages-12-00b894)
![Browser only](https://img.shields.io/badge/acquisition-in--app_browser-6c5ce7)
![API token](https://img.shields.io/badge/Product_Hunt_API_token-not_required-0984e3)
![License](https://img.shields.io/badge/license-MIT-blue)

> [!IMPORTANT]
> Product Hunt 榜单会动态变化，历史页的票数、评论数和页面结构也可能更新。本项目保留采集时间、原始页面编号、视图来源和异常说明，不把网页快照描述成官方冻结数据。

## 这是什么

`product-hunt-daily` 是一个可复用的 Codex Skill，用于研究某一天在 Product Hunt 发布的产品。它通过内置浏览器读取官方可见页面，不要求配置 Product Hunt API Token，也不会使用第三方榜单补齐数据。

一次完整运行可以生成：

- All 与 Featured 两个官方视图的产品清单；
- 产品名称、tagline、描述、票数、评论数、Topics 与官方 Visit URL；
- Product Hunt 明确显示的 Launch Team、Maker、Hunter/Submitter；
- 官网公开邮箱、联系表单、GitHub、LinkedIn、X、Discord 等职业渠道；
- 可审计的 JSON、CSV、Markdown、联系覆盖报告和来源清单；
- 按 Product Hunt 日期归档、可持续追加的真实运行示例。

## Product Hunt 为什么有价值

Product Hunt 不只是一个排行榜。对独立开发者、AI 创业者、产品团队、投资研究和出海营销来说，它可以同时提供多个观察窗口：

| 价值 | 可以获得什么 |
|---|---|
| 新产品发现 | 快速了解当天出现的工具、AI 产品、开发者服务和新商业模式 |
| 市场与竞品研究 | 对比定位、文案、定价方向、功能组合、话题分类和用户反馈 |
| 发布与冷启动 | 获得早期曝光、真实评论、产品反馈和第一批种子用户 |
| 社会证明 | 积累公开的投票、评论、榜单位置与社区讨论，但不应把排名当作唯一成功指标 |
| 团队与生态发现 | 找到 Maker、Hunter、连续创业者、开发者以及相关产品生态 |
| BD 与合作线索 | 基于官网公开渠道联系团队，开展采访、集成、联盟、渠道或社区合作 |
| 内容选题 | 为日报、周报、行业分析、选品、公众号和社媒内容提供可追溯素材 |
| 趋势观察 | 按日期持续积累数据，观察 AI、开发工具、生产力、营销和垂直 SaaS 的变化 |

Product Hunt 排名不能代表长期留存、收入或产品质量，也不能保证发布成功。更可靠的用法是把榜单与官网、用户评论、长期产品进展和自己的业务判断结合起来。

## 能力与数据边界

| 能力 | 处理方式 |
|---|---|
| 无 Token 获取榜单 | 只使用 Codex 内置浏览器和 Product Hunt 官方可见页面 |
| 完整列表 | 同时检查 All 与 Featured，并对 canonical Product Hunt URL 去重 |
| 页面顺序异常 | 保存官网打印的 `displayed_rank`，另生成连续导出序号 `rank` |
| 跨视图差异 | 默认严格校验；只有重复确认后才启用可审计的官方视图并集 |
| 推广卡 | 排除没有榜单编号的 promoted 卡片 |
| 团队信息 | 只记录 Product Hunt 明确标注的 Launch Team/Maker/Hunter，不扩张成完整组织架构 |
| 联系方式 | 只收集官网主动公开的职业联系方式，不猜邮箱、不提交表单 |
| 证据 | 保存来源 URL、访问时间、置信度、检查页面和阻断原因 |

## 快速开始

### 1. 安装 Skill

将 [`product-hunt-daily`](product-hunt-daily/) 目录复制到 Codex Skills 目录：

```bash
mkdir -p ~/.codex/skills
cp -R product-hunt-daily ~/.codex/skills/product-hunt-daily
```

也可以直接在当前仓库中让 Codex 使用 [`product-hunt-daily/SKILL.md`](product-hunt-daily/SKILL.md)。

### 2. 向 Codex 提出任务

```text
使用 product-hunt-daily Skill，通过内置浏览器获取今天 Product Hunt 的完整产品列表、产品详情、Launch Team 和官网公开联系渠道，并导出 JSON、CSV 与 Markdown。
```

指定日期：

```text
抓取 2026-08-12 的 Product Hunt 完整榜单，将结果作为按日期归档的开源示例。
```

“今天”始终按 Product Hunt 使用的 `America/Los_Angeles` 日历日计算，可能和你的本地日期不同。

## 标准交付物

```text
product-hunt-daily-YYYY-MM-DD/
├── browser-capture.json   内置浏览器原始结构化观察
├── contacts.json          规范化完整数据与嵌套证据
├── all-products.md        可读产品列表
├── contacts.csv           产品、团队与联系信息表格
├── contact-audit.md       联系证据覆盖与缺口
├── sources.md             Product Hunt 与官网来源清单
└── article.md             可选的日期报告
```

## 真实运行示例

示例按 Product Hunt 日期（`America/Los_Angeles`）归档。每个日期目录都可独立复核，并由脚本校验后进入索引。

<!-- examples-table:start -->
| 日期 | 状态 | 官方可见产品 | Featured | 详情页 | 联系检查 | 公开邮箱 | 示例 |
|---|---|---:|---:|---:|---:|---:|---|
| 2026-08-12 | completed | 18 | 17 | 18/18 | 18/18 | 5 | [查看示例](examples/2026-08-12/) |
<!-- examples-table:end -->

完整日期目录见 [`examples/`](examples/README.md)，机器可读索引见 [`examples/index.json`](examples/index.json)。新增日期后运行：

```bash
python3 product-hunt-daily/scripts/update_example_index.py
```

脚本会验证日期、完整交付物和规范化 JSON，然后自动更新项目首页与日期索引。

## 关于 Flaq AI

[Flaq AI](https://flaq.ai/about/) 是由 FLAQ AI PTE. LTD. 运营的多模型 AI 平台，将图像、视频、音频和语言模型放在一个平台中，帮助开发者、创意团队和企业完成模型发现、能力比较、API 集成和实际生产工作流。

对于 Product Hunt 的产品团队，Flaq AI 可以用于：

- 制作发布页所需的产品图、演示视频、社媒素材和广告创意；
- 为 AI 产品或 Agent 接入图像、视频、音频和语言模型 API；
- 快速比较不同模型，验证新功能和内容工作流；
- 将 Product Hunt 发布后的反馈转化为新的产品演示、教程和营销素材。

访问 [Flaq AI](https://flaq.ai/) 或查看其[模型与团队介绍](https://flaq.ai/about/)。

## Flaq AI 联盟推广计划

开发者、创作者、教育者、AI Agent 构建者和模型评测者可以加入 [Flaq AI Affiliate Program](https://flaq.ai/affiliate-program/)，创建个人推荐链接，并通过向合适的用户推荐 Flaq AI 服务获得佣金。

截至 2026-08-13，官方页面公开规则为：

- 被推荐用户的首笔有效付费订单：**20% 佣金**；
- 注册后 60 天归因窗口内的后续有效付费订单：**10% 佣金**；
- 退款、拒付、风险取消、归因状态和联盟政策会影响最终可支付佣金。

条款可能变化，请始终以[联盟计划官方页面](https://flaq.ai/affiliate-program/)和当前协议为准。推广时应清楚披露联盟关系，不承诺收益、产品结果或长期不变的价格与佣金。

详细说明见：[Flaq AI 联盟推广指南](docs/flaq-ai-affiliate-program.md)。

## Product Hunt 互助交流微信群

如果你正在准备 Product Hunt 发布、寻找真实反馈、交流发布节奏，或希望认识更多出海产品、独立开发和 AI 创业伙伴，欢迎加入 Product Hunt 互助交流微信群。

- 添加微信：**aihelloleo**
- 备注：**Product Hunt 互助**
- 当前已有：**3 个互助微信群**
- 社区规模：**1000+ 互助群友**

群内交流应以真实产品反馈、经验分享和互相支持为主。请遵守 Product Hunt 规则，不进行虚假账号、机器刷票、付费买票或其他操纵排名的行为。

## 多语言文档

本项目支持 12 种语言。简体中文 `README.md` 是默认首页，英文版提供完整国际说明，其他语言提供本地化项目入口。查看[多语言目录](i18n/README.md)。

## 贡献

欢迎提交新日期示例、页面结构兼容修复、字段改进、文档翻译和真实的数据质量案例。请阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md)。不要提交猜测邮箱、私人联系方式、抓取到的隐藏数据或未经验证的“完整”榜单。

## License

本项目采用 [MIT License](LICENSE)。Product Hunt、Flaq AI 及示例中出现的产品名称和商标归各自权利人所有。

## 搜索关键词

Product Hunt 榜单 · Product Hunt 今日产品 · Product Hunt 数据抓取 · Product Hunt Launch · Product Hunt Maker · Product Hunt 团队 · Product Hunt 联系方式 · Product Hunt 发布互助 · Product Hunt 微信群 · 独立开发者出海 · AI 产品发现 · Product Hunt CSV · Product Hunt JSON · Codex Skill · Flaq AI · Flaq AI Affiliate Program
