# Product Hunt 日期示例索引

所有示例以 Product Hunt 日历日期（`America/Los_Angeles`）为索引，最新日期在前。

| 日期 | 状态 | 官方可见产品 | Featured | 视图范围 | 详情覆盖 | 联系覆盖 | 公开邮箱 |
|---|---|---:|---:|---|---:|---:|---:|
| [2026-08-12](2026-08-12/) | completed | 18 | 17 | official_view_union | 18/18 | 18/18 | 5 |

## 如何增加日期

1. 使用 `product-hunt-daily` Skill 完成目标日期采集及全部校验。
2. 将最终交付物保存到 `examples/YYYY-MM-DD/`。
3. 以该日期目录的 `README.md` 记录结果摘要、官网异常、阻断项和数据边界。
4. 在仓库根目录运行 `python3 product-hunt-daily/scripts/update_example_index.py`，自动校验并重建索引。

临时或未完成的运行结果应留在 `product-hunt-daily/output/`。只有通过标准化、CSV 导出、审计和来源清单校验的结果才能进入本目录。
