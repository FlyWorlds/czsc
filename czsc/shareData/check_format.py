import pandas as pd

results = []

# 读取 marketData.py 生成的日线 CSV
try:
    df_daily = pd.read_csv(r"D:\quantitative\CZSC投研数据\自定义\000001_daily.csv", nrows=3)
    results.append("=== 日线 CSV (marketData.py 生成) ===")
    results.append(f"列名: {df_daily.columns.tolist()}")
    results.append(f"数据类型:\n{df_daily.dtypes}")
    results.append(f"前3行:\n{df_daily.head(3)}\n")
except Exception as e:
    results.append(f"日线CSV读取失败: {e}\n")

# 读取 marketData.py 生成的30分钟 CSV
try:
    df_30min = pd.read_csv(r"D:\quantitative\CZSC投研数据\自定义\000001_30min.csv", nrows=3)
    results.append("=== 30分钟 CSV (marketData.py 生成) ===")
    results.append(f"列名: {df_30min.columns.tolist()}")
    results.append(f"数据类型:\n{df_30min.dtypes}")
    results.append(f"前3行:\n{df_30min.head(3)}\n")
except Exception as e:
    results.append(f"30分钟CSV读取失败: {e}\n")

# 读取 parquet 标准格式
try:
    df_parquet = pd.read_parquet(r"D:\quantitative\CZSC投研数据\中证500成分股\000039.SZ.parquet")
    df_parquet = df_parquet.head(3)
    results.append("=== parquet 标准格式 ===")
    results.append(f"列名: {df_parquet.columns.tolist()}")
    results.append(f"数据类型:\n{df_parquet.dtypes}")
    results.append(f"前3行:\n{df_parquet}\n")
except Exception as e:
    results.append(f"parquet读取失败: {e}\n")

with open(r"D:\quantitative\czsc\czsc\shareData\format_compare.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
