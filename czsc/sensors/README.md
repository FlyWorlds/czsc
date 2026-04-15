# CZSC Sensors 说明

本目录提供“感应器（Sensors）”相关能力，用于在策略研究中做事件匹配、特征构建与组合评估。

## 目录作用

- `cta.py`：CTA 研究流程相关封装（如 `CTAResearch`）
- `event.py`：事件匹配感应器（如 `EventMatchSensor`）
- `feature.py`：特征工程相关工具
- `plates.py`：板块/分组研究相关工具
- `utils.py`：传感器通用工具（换手率、离散化、指数 beta 等）
- `__init__.py`：对外统一导出常用入口

## 核心能力

- **事件驱动筛选**：按信号或条件匹配触发事件
- **研究阶段分层**：支持研究、验证、筛选类流程
- **统计辅助**：提供常见统计与分组分析工具

## 常用入口

```python
from czsc.sensors import CTAResearch, EventMatchSensor
```

## 使用建议

- 感应器更偏“投研与验证”，实盘下单建议配合 `traders` 模块；
- 建议将事件定义与参数配置版本化，便于回溯实验结果；
- 大样本运行前先用小样本做参数烟雾测试，减少批量计算成本。
