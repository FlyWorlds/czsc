# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2023/3/5 20:45
describe: CZSC投研数据共享接口

投研数据共享说明（含下载地址）：https://s0cqcxuy3p.feishu.cn/wiki/wikcnzuPawXtBB7Cj7mqlYZxpDh

模块说明：
1) 提供本地投研共享数据的读取入口；
2) 支持按分组列出可用标的；
3) 将 parquet 行情重采样为 CZSC 标准 RawBar。

注意：
- 本模块依赖本地数据目录，需先配置环境变量 `czsc_research_cache`；
- 读取的是本地共享数据，不会联网请求第三方接口。
"""
import os
import czsc
import glob
import pandas as pd


def _resolve_cache_path():
    """解析投研共享数据目录，兼容不同系统上的常见路径布局。"""
    env_path = os.environ.get("czsc_research_cache")
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    workspace_root = os.path.dirname(project_root)
    candidates = [
        env_path,
        r"D:\quantitative\CZSC投研数据",
        os.path.join(project_root, "CZSC投研数据"),
        os.path.join(workspace_root, "CZSC投研数据"),
        os.path.join(os.path.expanduser("~"), "Documents", "Quantitative", "CZSC投研数据"),
    ]
    checked = []
    for path in candidates:
        if not path:
            continue
        normalized = os.path.abspath(os.path.expanduser(path))
        if normalized not in checked:
            checked.append(normalized)
        if os.path.exists(normalized):
            if env_path and normalized != env_path:
                os.environ["czsc_research_cache"] = normalized
            return normalized

    raise ValueError(
        "请设置环境变量 czsc_research_cache 为投研共享数据的本地缓存路径。\n"
        f"当前检查过的路径都不存在：{checked}\n\n"
        "投研数据共享说明（含下载地址）："
        "https://s0cqcxuy3p.feishu.cn/wiki/wikcnzuPawXtBB7Cj7mqlYZxpDh"
    )


cache_path = _resolve_cache_path()


def get_symbols(name, **kwargs):
    """获取指定分组下的所有标的代码

    :param name: 分组名称，可选值：'A股主要指数', 'A股场内基金', '中证500成分股', '期货主力'
    :param kwargs:
    :return:
    """
    # ALL：扫描所有分组目录；否则仅扫描指定分组目录
    if name.upper() == 'ALL':
        files = glob.glob(os.path.join(cache_path, "*", "*.parquet"))
    else:
        files = glob.glob(os.path.join(cache_path, name, "*.parquet"))
    return [os.path.basename(x).replace('.parquet', '') for x in files]


def get_raw_bars(symbol, freq, sdt, edt, fq='前复权', **kwargs):
    """获取 CZSC 库定义的标准 RawBar 对象列表

    :param symbol: 标的代码
    :param freq: 周期，支持 Freq 对象，或者字符串，如
            '1分钟', '5分钟', '15分钟', '30分钟', '60分钟', '日线', '周线', '月线', '季线', '年线'
    :param sdt: 开始时间
    :param edt: 结束时间
    :param fq: 除权类型，投研共享数据默认都是后复权，不需要再处理
    :param kwargs:
    :return:
    """
    # 兼容统一连接器签名；本地共享数据默认已做处理，此处不再二次复权
    kwargs['fq'] = fq
    file = glob.glob(os.path.join(cache_path, "*", f"{symbol}.parquet"))[0]
    freq = czsc.Freq(freq)
    kline = pd.read_parquet(file)
    if 'dt' not in kline.columns:
        # 兼容历史字段命名：datetime -> dt
        kline['dt'] = pd.to_datetime(kline['datetime'])
    kline = kline[(kline['dt'] >= pd.to_datetime(sdt)) & (kline['dt'] <= pd.to_datetime(edt))]
    if kline.empty:
        return []
    # 源数据按 1 分钟基准重采样到目标周期
    _bars = czsc.resample_bars(kline, freq, raw_bars=True, base_freq='1分钟')
    return _bars
