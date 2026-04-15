# CZSC Data 说明

本目录提供 CZSC 的数据基础能力，包含频率/代码转换工具、Tushare 接口封装与本地缓存。

## 目录作用

- `base.py`：频率映射、不同平台代码格式转换、导出 EBK 工具
- `ts.py`：Tushare Pro 接口轻封装与 K 线标准化转换
- `ts_cache.py`：`TsDataCache` 本地缓存层（研究场景常用）
- `__init__.py`：统一导出 `TsDataCache`、`base` 工具与 `get_symbols`

## 核心能力

- **频率映射**：如 `1分钟 <-> 1min`、`日线 <-> D`，并兼容 JQ/GM/TS 表达
- **代码转换**：支持 JQ / GM / Tushare / 通达信 之间互转
- **本地缓存读取**：`TsDataCache` 将常用数据接口缓存到本地，减少重复请求
- **K线标准化**：将数据转换为 CZSC 的 `RawBar` 结构，方便策略层直接使用

## 常用入口

```python
from czsc.data import TsDataCache, get_symbols

dc = TsDataCache(data_path=r"D:\ts_data")
symbols = get_symbols(dc, "train")
bars = dc.pro_bar_minutes("000001.SZ", sdt="2024-01-01 09:30:00", edt="2024-12-31 15:00:00", freq="5min")
print(len(symbols), len(bars))
```

## 使用建议

- `TsDataCache` 适合研究与回测：用磁盘换时间，避免重复拉取；
- 首次跑全市场会占用较大磁盘空间（通常几十 GB 级）；
- 若切换环境，请确认：
  - Tushare token 已可用
  - `data_path` 指向可写目录
  - 旧缓存是否需要清理（可用 `dc.clear()`）

## 备注

- 若上层已通过 `connectors` 统一访问数据，本目录通常作为底层依赖存在；
- 修改 `base.py` 的转换规则会影响多个连接器，建议同步回归测试。
