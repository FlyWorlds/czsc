import os
import akshare as ak
import pandas as pd
from pathlib import Path

os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

# ===== 聚宽账号配置（AKShare 失败时备用）=====
JQ_USER = "13018096678"
JQ_PASS = "Qweqwe123."
# =============================================

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
symbols   = ["000001", "000063", "002594"]
save_dir  = WORKSPACE_ROOT / "CZSC投研数据" / "自定义"
START_DATE = "20240101"
END_DATE   = "20260413"
save_dir.mkdir(exist_ok=True, parents=True)


# ===================================================================
# 工具函数
# ===================================================================
def to_jq_code(symbol: str) -> str:
    suffix = ".XSHG" if symbol.startswith("6") else ".XSHE"
    return symbol + suffix


def to_ts_code(symbol: str) -> str:
    suffix = ".SH" if symbol.startswith("6") else ".SZ"
    return symbol + suffix


_jq_authed = False

def _ensure_jq_auth():
    global _jq_authed
    if not _jq_authed:
        import jqdatasdk as jq
        jq.auth(JQ_USER, JQ_PASS)
        _jq_authed = True


def normalize(df: pd.DataFrame, symbol: str, freq: str) -> pd.DataFrame:
    """将各数据源的 DataFrame 统一转换为标准格式，与 parquet 保持一致：
    列: symbol | dt | open | close | high | low | vol | amount
    """
    # AKShare 日线列名映射
    ak_daily_map = {
        "日期": "dt", "开盘": "open", "收盘": "close",
        "最高": "high", "最低": "low", "成交量": "vol", "成交额": "amount",
    }
    # AKShare 分钟列名映射
    ak_min_map = {
        "时间": "dt", "开盘": "open", "收盘": "close",
        "最高": "high", "最低": "low", "成交量": "vol", "成交额": "amount",
    }
    # 聚宽列名映射（rename 后已是中文）
    jq_map = {
        "日期": "dt", "时间": "dt",
        "开盘": "open", "收盘": "close", "最高": "high", "最低": "low",
        "成交量": "vol", "成交额": "amount",
    }

    # 合并所有可能的映射，按实际列名匹配
    col_map = {**ak_daily_map, **ak_min_map, **jq_map}
    df = df.rename(columns=col_map)

    # 若 dt 在索引中（聚宽返回的格式），重置到列
    if "dt" not in df.columns and df.index.name in ("dt", "日期", "时间", None):
        df = df.reset_index()
        df = df.rename(columns={df.columns[0]: "dt"})

    # 确保 dt 为 datetime 类型
    df["dt"] = pd.to_datetime(df["dt"])

    # 补充 symbol 列
    ts_code = to_ts_code(symbol)
    df.insert(0, "symbol", ts_code)

    # 只保留标准列，补全缺失列为 NaN
    std_cols = ["symbol", "dt", "open", "close", "high", "low", "vol", "amount"]
    for col in std_cols:
        if col not in df.columns:
            df[col] = None
    df = df[std_cols]

    # 按时间正序排列
    df = df.sort_values("dt").reset_index(drop=True)
    return df


# ===================================================================
# 1 分钟数据
# ===================================================================
def fetch_1min_akshare(symbol: str) -> pd.DataFrame:
    """AKShare 1分钟数据，仅近 ~5 个交易日"""
    return ak.stock_zh_a_minute(symbol=symbol, period="1", adjust="")


def fetch_1min_jqdata(symbol: str) -> pd.DataFrame:
    """聚宽 1分钟数据，免费试用账号仅限 2025-01-04 至 2026-01-11
    注意：单次最多返回 5000 条，约 21 个交易日；需分段拉取完整数据
    """
    _ensure_jq_auth()
    import jqdatasdk as jq
    from datetime import datetime, timedelta

    security = to_jq_code(symbol)
    jq_start = datetime(2025, 1, 4)
    jq_end   = datetime(2026, 1, 11)

    all_dfs = []
    cursor = jq_start
    # 每段拉取 20 个交易日（约 4800 条 1min bar，不超过 5000 上限）
    step = timedelta(days=20)

    while cursor < jq_end:
        seg_end = min(cursor + step, jq_end)
        df = jq.get_price(
            security=security,
            start_date=cursor.strftime("%Y-%m-%d"),
            end_date=seg_end.strftime("%Y-%m-%d"),
            frequency="1m",
            fields=["open", "close", "high", "low", "volume", "money"],
            skip_paused=False,
            fq=None,
        )
        if df is not None and not df.empty:
            all_dfs.append(df)
        cursor = seg_end + timedelta(days=1)

    if not all_dfs:
        return pd.DataFrame()

    result = pd.concat(all_dfs)
    result = result[~result.index.duplicated(keep='first')]
    return result.rename(columns={"volume": "vol", "money": "amount"})


# ===================================================================
# 通用下载：先 AKShare，失败降级到聚宽
# ===================================================================
def download(symbol: str) -> pd.DataFrame | None:
    """下载 1分钟 K线数据，先尝试 AKShare，失败降级到聚宽"""
    df = None
    try:
        print(f"{symbol} [1分钟][AKShare] 尝试...")
        df = fetch_1min_akshare(symbol)
        if df is not None and not df.empty:
            print(f"{symbol} [1分钟][AKShare] 成功，{len(df)} 条")
            return normalize(df, symbol, "1min")
    except Exception as e:
        print(f"{symbol} [1分钟][AKShare] 失败: {e}")

    try:
        print(f"{symbol} [1分钟][聚宽] 降级尝试...")
        df = fetch_1min_jqdata(symbol)
        if df is not None and not df.empty:
            print(f"{symbol} [1分钟][聚宽] 成功，{len(df)} 条")
            return normalize(df, symbol, "1min")
    except Exception as e:
        print(f"{symbol} [1分钟][聚宽] 失败: {e}")

    return None


# ===================================================================
# 主流程
# ===================================================================
if __name__ == "__main__":
    for symbol in symbols:
        ts_code = to_ts_code(symbol)
        df = download(symbol)
        if df is not None:
            # 文件名与中证500成分股目录保持一致：{ts_code}.parquet
            path = save_dir / f"{ts_code}.parquet"
            df.to_parquet(path, index=False)
            print(f"  -> 保存: {path}")
            print(f"     共 {len(df)} 条，时间范围: {df['dt'].min()} ~ {df['dt'].max()}\n")
