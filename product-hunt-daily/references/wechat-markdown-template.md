# Product Hunt 日报 Markdown 模板

```markdown
# Product Hunt 日榜观察：{{榜单日期}}

> 数据口径：通过 Codex 内置浏览器读取 Product Hunt Daily 的完整 All 与 Featured 视图；Product Hunt 日界线使用 America/Los_Angeles。抓取时间：{{accessed_at}}。状态：{{live_or_completed}}。

今天共收录 {{all_count}} 个产品，其中 Featured {{featured_count}} 个、非 Featured {{unfeatured_count}} 个。当前日期仍在进行时，排名、票数和 Featured 状态均可能变化。

## 完整产品列表

| All 位置 | Featured 排名 | 产品 | Makers | Votes | Comments | 一句话看点 |
|---:|---:|---|---|---:|---:|---|
| 1 | 1 | [{{产品名}}]({{product_hunt_url}}) | {{makers}} | {{votes}} | {{comments}} | {{tagline}} |

## 前 5 个产品观察

### 1. {{产品名}}：{{一句话定位}}

{{解决什么问题、面向谁、发布表达和可借鉴点。保持克制并链接产品页/官网。}}

## 今日趋势

1. {{基于全量分类或产品定位的观察}}
2. {{基于 Featured 与非 Featured 差异的观察}}
3. {{对独立开发者或出海团队的可执行启发}}

## 数据说明

- `rank` 是网页 All 视图的可见顺序，不是官方奖项。
- `featured_rank` 是网页 Featured 视图的可见顺序。
- 票数和评论数是浏览器抓取时页面显示的当前值；历史日期也不应描述为冻结的日终值。
- 公司、团队和公开联系方式保存在独立研究附件中；正文默认不公开邮箱。

## 来源

- [Product Hunt Daily Leaderboard]({{leaderboard_url}})
- {{top_product_links}}
```
