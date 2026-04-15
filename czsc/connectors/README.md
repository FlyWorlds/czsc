# CZSC Connectors 说明

本目录用于管理不同数据源/交易端的连接器，实现统一的数据读取与交易接口适配。

## 目录作用

- `jq_connector.py`：聚宽（JoinQuant）HTTP 数据接口连接器
- `qmt_connector.py`：QMT（迅投）行情与交易连接器（含交易管理示例）
- `research.py`：本地投研共享数据连接器（parquet 数据）
- `ts_connector.py`：Tushare 本地缓存连接器
- `gm_connector.py`：掘金（GM）连接器

## 统一接口约定

多数连接器遵循以下函数约定，方便上层策略无缝切换数据源：

- `get_symbols(...)`：获取标的列表
- `get_raw_bars(symbol, freq, sdt, edt, fq=..., **kwargs)`：获取标准 `RawBar` 列表

## 使用建议

- **优先通过 import 调用**：连接器文件通常是函数集合，直接执行 `.py` 文件不一定有输出。
- **先配置本地依赖**：
  - 聚宽：确保 `jq.token` 已设置
  - Tushare：确保 `ts_data_path` 指向本地缓存
  - 投研共享：确保 `czsc_research_cache` 指向数据目录
  - QMT/GM：确保本机环境已安装并可连接对应客户端或 SDK
- **策略层面保持解耦**：上层尽量只依赖统一接口，避免绑定某个连接器的私有实现细节。

## 快速示例

```python
from czsc.connectors import jq_connector

bars = jq_connector.get_raw_bars(
    symbol="000001.XSHG",
    freq="日线",
    sdt="2024-01-01",
    edt="2024-12-31",
    fq="前复权",
)
print(len(bars))
```

## 备注

- 若新增连接器，建议至少实现 `get_symbols` 与 `get_raw_bars`，并在本文件补充说明。
- 连接器中的账号、密码、token 等敏感信息应通过本地配置文件或环境变量管理，不要写入仓库。
