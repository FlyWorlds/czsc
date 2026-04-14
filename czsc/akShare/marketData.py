import os
import akshare as ak
import pandas as pd

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

symbols = ["000001", "000063", "002594"]
save_dir = r"D:\quantitative\CZSC投研数据\自定义"
os.makedirs(save_dir, exist_ok=True)


# ---------- AKShare 获取 ----------
def fetch_by_akshare(symbol: str) -> pd.DataFrame:
    return ak.stock_zh_a_hist(
        symbol=symbol,
        period="daily",
        start_date="20240101",
        end_date="20260413",
        adjust=""
    )


# ---------- 聚宽 获取 ----------
def to_jq_code(symbol: str) -> str:
    suffix = ".XSHG" if symbol.startswith("6") else ".XSHE"
    return symbol + suffix

_jq_authed = False

def fetch_by_jqdata(symbol: str) -> pd.DataFrame:
    global _jq_authed
    if not _jq_authed:
        import jqdatasdk as jq
        jq.auth(JQ_USER, JQ_PASS)
        _jq_authed = True
    import jqdatasdk as jq
    df = jq.get_price(
        security=to_jq_code(symbol),
        start_date="2025-01-04",
        end_date="2026-01-11",
        frequency="daily",
        fields=["open", "close", "high", "low", "volume", "money"],
        skip_paused=False,
        fq=None,
    )
    df.index.name = "日期"
    df = df.rename(columns={
        "open": "开盘",
        "close": "收盘",
        "high": "最高",
        "low": "最低",
        "volume": "成交量",
        "money": "成交额",
    })
    return df


# ---------- 主流程 ----------
for symbol in symbols:
    df = None

    # 1. 先尝试 AKShare
    try:
        print(f"{symbol} [AKShare] 尝试...")
        df = fetch_by_akshare(symbol)
        print(f"{symbol} [AKShare] 成功")
    except Exception as e:
        print(f"{symbol} [AKShare] 失败: {e}")

    # 2. AKShare 失败，降级到聚宽
    if df is None or df.empty:
        try:
            print(f"{symbol} [聚宽] 降级尝试...")
            df = fetch_by_jqdata(symbol)
            print(f"{symbol} [聚宽] 成功")
        except Exception as e:
            print(f"{symbol} [聚宽] 失败: {e}")

    # 3. 保存
    if df is not None and not df.empty:
        save_path = os.path.join(save_dir, f"{symbol}_daily.csv")
        df.to_csv(save_path, index=True, encoding="utf-8-sig")
        print(f"{symbol} 保存成功，共 {len(df)} 条 -> {save_path}")
    else:
        print(f"{symbol} 所有数据源均失败，跳过")

