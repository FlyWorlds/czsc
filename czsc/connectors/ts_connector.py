# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2023/6/24 18:49
describe: Tushare数据源

模块说明：
1) 基于 `TsDataCache` 读取本地 Tushare 缓存数据；
2) 提供标的列表查询与标准 K 线读取接口；
3) 对外保持与其他连接器一致的 `get_symbols / get_raw_bars` 调用方式。

注意：
- 依赖本地缓存目录 `ts_data_path`（默认 `D:\ts_data`）；
- 本模块主要走本地缓存读取，不直接发起在线拉取。
"""
import os
from czsc import data

# Tushare 本地缓存对象：统一复用于本模块查询
dc = data.TsDataCache(data_path=os.environ.get('ts_data_path', r'D:\ts_data'))


def get_symbols(step):
    """按投研阶段返回标的列表。"""
    if step.upper() == 'ALL':
        return data.get_symbols(dc, 'index') + data.get_symbols(dc, 'stock') + data.get_symbols(dc, 'etfs')
    return data.get_symbols(dc, step)


def get_raw_bars(symbol, freq, sdt, edt, fq='后复权', raw_bar=True):
    """读取本地缓存并返回 K 线数据（可选 RawBar）。"""
    ts_code, asset = symbol.split("#")
    freq = str(freq)
    # CZSC 中文复权参数映射到 tushare 复权参数
    adj = "qfq" if fq == "前复权" else "hfq"

    if "分钟" in freq:
        # 例如：'5分钟' -> '5min'
        freq = freq.replace("分钟", "min")
        bars = dc.pro_bar_minutes(ts_code, sdt=sdt, edt=edt, freq=freq, asset=asset, adj=adj, raw_bar=raw_bar)

    else:
        # 日/周/月 频率映射
        _map = {"日线": "D", "周线": "W", "月线": "M"}
        freq = _map[freq]
        bars = dc.pro_bar(ts_code, start_date=sdt, end_date=edt, freq=freq, asset=asset, adj=adj, raw_bar=raw_bar)
    return bars
