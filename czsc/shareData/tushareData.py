import os
import tushare as ts
import pandas as pd

# ===== Tushare Token 配置 =====
# 首次使用需设置，之后会保存在本地，无需重复设置：
# ts.set_token("your_token_here")
# ==============================

# 股票代码（纯数字），自动转换为 Tushare 格式
symbols = ["000001", "000063", "002594"]

# 时间范围
START_DATE = "20190101"
END_DATE   = "20260413"

# 保存目录
save_dir = r"D:\quantitative\CZSC投研数据\自定义"
os.makedirs(save_dir, exist_ok=True)

# 列名映射：Tushare → 中文
COL_MAP = {
    "trade_date": "日期",
    "open":       "开盘",
    "high":       "最高",
    "low":        "最低",
    "close":      "收盘",
    "pre_close":  "昨收",
    "change":     "涨跌额",
    "pct_chg":    "涨跌幅",
    "vol":        "成交量",
    "amount":     "成交额",
}


def to_ts_code(symbol: str) -> str:
    """纯数字代码转 Tushare 格式：6开头→.SH，其余→.SZ"""
    suffix = ".SH" if symbol.startswith("6") else ".SZ"
    return symbol + suffix


def fetch_daily(pro, symbol: str) -> pd.DataFrame:
    ts_code = to_ts_code(symbol)
    df = pro.daily(
        ts_code=ts_code,
        start_date=START_DATE,
        end_date=END_DATE,
    )
    if df is None or df.empty:
        raise ValueError(f"{ts_code} 返回数据为空")

    df = df.rename(columns=COL_MAP)
    # Tushare 返回的是倒序（最新在前），改为正序
    df = df.sort_values("日期").reset_index(drop=True)
    # 只保留已映射的列
    df = df[[c for c in COL_MAP.values() if c in df.columns]]
    return df


def main():
    pro = ts.pro_api()

    for symbol in symbols:
        try:
            print(f"{symbol} [Tushare] 获取中...")
            df = fetch_daily(pro, symbol)
            save_path = os.path.join(save_dir, f"{symbol}_daily.csv")
            df.to_csv(save_path, index=False, encoding="utf-8-sig")
            print(f"{symbol} 保存成功，共 {len(df)} 条 -> {save_path}")
        except Exception as e:
            print(f"{symbol} 失败: {e}")


if __name__ == "__main__":
    main()
