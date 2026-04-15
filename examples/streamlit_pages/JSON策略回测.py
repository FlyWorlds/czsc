import os
from pathlib import Path
import czsc
import json
import glob
import hashlib
import pandas as pd
import streamlit as st
import plotly.express as px
from tqdm import tqdm
from loguru import logger
from czsc.utils.stats import net_value_stats
from datetime import timedelta
from multiprocessing import cpu_count
from czsc.connectors.research import get_symbols, get_raw_bars

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
CTA_ROOT = WORKSPACE_ROOT / "CTA投研"
os.environ.setdefault('czsc_research_cache', str(WORKSPACE_ROOT / "CZSC投研数据"))

st.set_page_config(layout="wide", page_title="CZSC策略回测", page_icon="🧊")

with st.sidebar:
    st.title("CZSC策略回测")
    form = st.form(key='my_form')
    files = form.file_uploader(label='上传策略文件', type='json', accept_multiple_files=True)
    symbol_gruop = form.selectbox(label="回测品类", options=['A股主要指数', 'A股场内基金', '中证500成分股', '期货主力'], index=3)
    start_date = form.date_input(label='开始日期', value=pd.to_datetime('2019-01-01'))
    end_date = form.date_input(label='结束日期', value=pd.to_datetime('2022-01-01'))
    max_workers = form.number_input(label='最大进程数', value=4, min_value=1, max_value=cpu_count() // 2)
    submit_button = form.form_submit_button(label='开始回测')

@st.cache_data()
def read_data(files_traders, pos_name):
    res = []
    for file in tqdm(files_traders):
        try:
            trader = czsc.dill_load(file)
            pos = trader.get_position(pos_name)

            hd = pd.DataFrame(pos.holds)
            hd['n1b'] = (hd['price'].shift(-1) / hd['price'] - 1) * 10000
            hd['edge_fee0'] = hd['pos'] * hd['n1b']
            hd['edge_fee2'] = hd['edge_fee0'] - hd['pos'].diff().abs() * 1
            hd['edge_fee4'] = hd['edge_fee0'] - hd['pos'].diff().abs() * 2

            hd['date'] = hd['dt'].dt.date
            daily = hd.groupby('date').agg({'edge_fee0': 'sum', 'edge_fee2': 'sum', 'edge_fee4': 'sum'}).reset_index()
            daily['symbol'] = trader.symbol
            res.append(daily)
        except Exception as e:
            logger.warning(f"{file} {pos_name} 读取失败: {e}")

    dfr = pd.concat(res, ignore_index=True)
    return dfr

if files and start_date and max_workers:
    strategies = {file.name: json.loads(file.getvalue().decode("utf-8")) for file in files}
    symbols = get_symbols(symbol_gruop)

    # 生成临时回测结果路径
    hash_code = hashlib.sha256(f"{str(strategies)}_{str(symbols)}".encode('utf-8')).hexdigest()[:8].upper()
    results_path = CTA_ROOT / f"{symbol_gruop}_{start_date}_{end_date}_{hash_code}"

    if not results_path.exists():
        results_path.mkdir(exist_ok=True, parents=True)
        (results_path / "upload_positions").mkdir(exist_ok=True, parents=True)

        files_position = []
        for key, value in strategies.items():
            file_pos = results_path / "upload_positions" / key
            files_position.append(str(file_pos))
            czsc.save_json(value, str(file_pos))

        params = {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "symbol_group": symbol_gruop,
            "symbols": symbols,
        }
        czsc.save_json(params, str(results_path / "params.json"))

        # 回测
        cta = czsc.CTAResearch(czsc.CzscJsonStrategy, get_raw_bars, results_path=str(results_path),
                            files_position=files_position,
                            signals_module_name='czsc.signals')
        bar_sdt = pd.to_datetime(start_date) - timedelta(days=365)
        with st.spinner('正在执行策略回测，请耐心等候 ...'):
            cta.backtest(symbols, max_workers=int(max_workers), bar_sdt=bar_sdt, sdt=start_date, edt=end_date)

    # 生成回测报告
    file_traders = glob.glob(str(results_path / "backtest_*" / "traders" / "*.trader"))

    st.subheader("一、品种等权收益曲线")
    all_pos_names = [x.name for x in czsc.dill_load(file_traders[0]).positions]
    pos_name = st.selectbox("选择持仓", all_pos_names, index=0)

    dfr = read_data(file_traders, pos_name)
    dfg = dfr.groupby('date').agg({'edge_fee0': 'mean', 'edge_fee2': 'mean', 'edge_fee4': 'mean'}).cumsum()
    dfg.rename({'edge_fee0': '等权费前收益', 'edge_fee2': '双边扣费2BP', 'edge_fee4': '双边扣费4BP'}, axis=1, inplace=True)

    fig = px.line(dfg, x=dfg.index, y=['等权费前收益', '双边扣费2BP', '双边扣费4BP'], labels=[], title="全部品种日收益等权")
    st.plotly_chart(fig, use_container_width=True, height=600)

    dfg['dt'] = dfg.index.to_list()
    stats = []
    for col in ['等权费前收益', '双边扣费2BP', '双边扣费4BP']:
        dfg_ = dfg[['dt', col]].copy().rename(columns={col: 'edge'}).reset_index(drop=True)
        dfg_['edge'] = dfg_['edge'].diff()
        stats_ = net_value_stats(dfg_, sub_cost=False)
        stats_['name'] = col
        stats.append(stats_)
    st.dataframe(pd.DataFrame(stats).set_index('name'), use_container_width=True)
