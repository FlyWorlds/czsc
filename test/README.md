# CZSC Test 说明

本目录是项目单元测试与回归测试集合，用于验证核心模块行为稳定性。

## 目录作用

- `test_analyze.py`：分析流程相关测试
- `test_bar_generator.py`：K线合成与周期处理测试
- `test_data.py`：数据层接口与数据处理测试
- `test_objects.py`：核心对象行为测试
- `test_strategy.py`：策略定义与执行基础测试
- `test_trader_base.py` / `test_trader_sig.py`：交易员与信号流程测试
- `test_utils.py` / `test_trade_utils.py`：工具函数测试
- `test_plot.py` / `test_plotly_plot.py` / `test_word_writer.py`：可视化与报告输出测试
- `test_calendar.py`：交易日历相关测试
- `data/`：测试数据样本

## 使用建议

- 提交前至少运行与改动相关的测试文件；
- 若新增信号/策略逻辑，建议补最小可复现测试；
- 涉及随机过程的测试建议固定随机种子，减少不稳定失败。
