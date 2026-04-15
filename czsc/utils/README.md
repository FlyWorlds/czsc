# CZSC Utils 说明

本目录是通用工具库，覆盖 K 线重采样、指标计算、绘图、缓存、统计、I/O 等基础能力。

## 目录作用（按功能）

- **K线与时间**：`bar_generator.py`、`calendar.py`
- **信号与统计**：`sig.py`、`stats.py`、`corr.py`、`signal_analyzer.py`
- **交易辅助**：`trade.py`、`cross.py`
- **绘图能力**：`echarts_plot.py`、`plotly_plot.py`、`plt_plot.py`
- **数据与缓存**：`data_client.py`、`cache.py`、`io.py`
- **其他工具**：`word_writer.py`、`oss.py`、`index_composition.py` 等
- `__init__.py`：聚合并导出高频使用工具函数

## 使用建议

- 上层模块尽量通过 `czsc.utils` 聚合入口调用，减少直接依赖内部细节；
- 新增工具优先保证“纯函数化”和可测试性；
- 涉及外部服务（如 OSS / 数据客户端）的函数建议加超时和重试策略。
