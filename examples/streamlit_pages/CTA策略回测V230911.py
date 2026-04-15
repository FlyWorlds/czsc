# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2023/9/11 11:24
describe: 期货CTA投研
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, '.')
sys.path.insert(0, '..')
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
os.environ['base_path'] = str(WORKSPACE_ROOT / "CTA投研")   # 回测结果保存路径
# os.environ['czsc_min_bi_len'] = '7'                   # 最小笔长度，内部无包含关系K线数量
# os.environ['czsc_bi_change_th'] = '-1'                # 笔划分时，是否用涨跌幅优化笔划分
os.environ['signals_module_name'] = 'czsc.signals'      # 信号函数所在模块
os.environ.setdefault('czsc_research_cache', str(WORKSPACE_ROOT / "CZSC投研数据"))
import czsc
import json
import glob
import hashlib
import pandas as pd
import streamlit as st
import plotly.express as px
from loguru import logger
from typing import List
from stqdm import stqdm as tqdm
from streamlit_extras.mandatory_date_range import date_range_picker
from multiprocessing import cpu_count
from czsc.connectors.research import get_symbols, get_raw_bars
from concurrent.futures import ProcessPoolExecutor, as_completed


st.set_page_config(layout="wide", page_title="CTA策略回测", page_icon="🧭")


class JsonStreamStrategy(czsc.CzscStrategyBase):
    """读取 streamlit 传入的 json 策略，进行回测"""
    @property
    def positions(self) -> List[czsc.Position]:
        """返回当前的持仓策略"""
        json_strategies = self.kwargs.get("json_strategies")
        assert json_strategies, "请在初始化策略时，传入参数 json_strategies"
        positions = []
        for _, pos in json_strategies.items():
            pos["symbol"] = self.symbol
            positions.append(czsc.Position.load(pos))
        return positions


@st.cache_data()
def read_holds_and_pairs(files_traders, pos_name, fee=1):
    holds, pairs = [], []
    for file in tqdm(files_traders):
        try:
            trader = czsc.dill_load(file)
            pos = trader.get_position(pos_name)
            if not pos.holds:
                logger.info(f"{trader.symbol} {pos_name} 无持仓，跳过")
                continue

            hd = pd.DataFrame(pos.holds)
            hd['symbol'] = trader.symbol
            hd = czsc.subtract_fee(hd, fee=fee)
            holds.append(hd)

            pr = pd.DataFrame(pos.pairs)
            pairs.append(pr)
        except Exception as e:
            logger.warning(f"{file} {pos_name} 读取失败: {e}")

    dfh = pd.concat(holds, ignore_index=True)
    dfp = pd.concat(pairs, ignore_index=True)
    return dfh, dfp


@st.cache_data()
def get_daily_nv(df):
    """获取每日净值"""
    res = []
    for symbol, hd in tqdm(df.groupby('symbol')):
        hd = hd.sort_values('dt', ascending=True)
        try:
            daily = hd.groupby('date').agg({'edge_pre_fee': 'sum', 'edge_post_fee': 'sum'}).reset_index()
            daily['symbol'] = symbol
            res.append(daily)
        except Exception as e:
            logger.exception(f"{symbol} 日收益获取失败: {e}")

    dfr = pd.concat(res, ignore_index=True)
    return dfr


def show_pos_detail(file_trader, pos_name):
    """显示持仓策略详情"""
    trader = czsc.dill_load(file_trader)
    pos = trader.get_position(pos_name)
    with st.expander(f"{pos_name} 持仓策略详情", expanded=False):
        _pos = pos.dump()
        _pos.pop('symbol')
        st.json(_pos)


def show_backtest_results(file_traders, pos_name, fee=1):
    dfh, dfp = read_holds_and_pairs(file_traders, pos_name, fee=fee)
    dfr = get_daily_nv(dfh)
    show_pos_detail(file_traders[0], pos_name)

    st.subheader("一、单笔收益评价")

    pp = czsc.PairsPerformance(dfp)
    # st.write(pp.basic_info)
    df1 = pp.agg_statistics('标的代码')
    _res = pp.basic_info
    _res['标的代码'] = "全部品种"
    df1 = pd.concat([pd.DataFrame([_res]), df1], ignore_index=True)
    _cols = [
        '标的代码',
        '开始时间',
        '结束时间',
        '交易标的数量',
        '总体交易次数',
        '平均持仓K线数',
        '平均单笔收益',
        '单笔收益标准差',
        '交易胜率',
        '单笔盈亏比',
        '累计盈亏比',
        '盈亏平衡点',
        '每根K线收益',
    ]
    df1 = df1[_cols].set_index('标的代码')
    color_cols = ['交易标的数量', '总体交易次数', '平均持仓K线数', '平均单笔收益', '单笔收益标准差',
                  '交易胜率', '单笔盈亏比', '累计盈亏比', '盈亏平衡点', '每根K线收益']
    df1 = df1.style.format('{0:,.2f}', subset=color_cols, na_rep="-").background_gradient(cmap='RdYlGn_r', subset=color_cols)

    st.dataframe(df1, use_container_width=True)

    st.divider()

    st.subheader("二、品种等权收益曲线")
    dfg = dfr.groupby('date').agg({'edge_pre_fee': 'mean', 'edge_post_fee': 'mean'}).cumsum()
    dfg.rename({'edge_pre_fee': '等权费前收益', 'edge_post_fee': f'双边扣费{2*fee}BP'}, axis=1, inplace=True)

    fig = px.line(dfg, x=dfg.index, y=['等权费前收益', f'双边扣费{2*fee}BP'], labels=[], title="全部品种日收益等权")
    st.plotly_chart(fig, use_container_width=True, height=600)

    dfg['dt'] = dfg.index.to_list()
    stats = []
    for col in ['等权费前收益', f'双边扣费{2*fee}BP']:
        dfg_ = dfg[['dt', col]].copy().rename(columns={col: 'edge'}).reset_index(drop=True)
        dfg_['edge'] = dfg_['edge'].diff()
        stats_ = czsc.net_value_stats(dfg_, sub_cost=False)
        stats_['name'] = col
        stats.append(stats_)
    st.dataframe(pd.DataFrame(stats).set_index('name'), use_container_width=True)


def symbol_backtest(strategies, symbol, bar_sdt, sdt, edt, results_path):
    """回测单个标的

    :param strategies: 策略配置
    :param symbol: 标的代码
    :param bar_sdt: 行情开始日期
    :param sdt: 回测开始日期
    :param edt: 回测结束日期
    :param results_path: 回测结果保存路径
    """
    file_trader = results_path / f"{symbol}.trader"
    if file_trader.exists():
        logger.info(f"{symbol} 已回测，跳过")
        return

    try:
        tactic = JsonStreamStrategy(json_strategies=strategies, symbol=symbol)
        bars = get_raw_bars(symbol, tactic.base_freq, sdt=bar_sdt, edt=edt)
        trader = tactic.backtest(bars, sdt=sdt)
        czsc.dill_dump(trader, file_trader)
    except:
        logger.exception(f"{symbol} 回测失败")


@st.cache_data(ttl=60 * 60 * 24)
def backtest_all(strategies, results_path):
    """回测全部标的

    :param strategies: 策略配置
    :param results_path: 回测结果保存路径
    """
    bar_sdt = st.session_state.bar_sdt
    gruop = st.session_state.gruop
    sdt = st.session_state.sdt
    edt = st.session_state.edt
    max_workers = st.session_state.max_workers
    symbols = get_symbols(gruop)

    if max_workers <= 1:
        for symbol in tqdm(symbols, desc="On Bar 回测进度"):
            symbol_backtest(strategies, symbol, bar_sdt, sdt, edt, results_path)
    else:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            tasks = [executor.submit(symbol_backtest, strategies, symbol, bar_sdt, sdt, edt, results_path)
                    for symbol in symbols]
            for future in tqdm(as_completed(tasks), desc="On Bar 回测进度", total=len(tasks)):
                future.result()


def main():
    with st.sidebar:
        st.title("CTA策略回测")
        st.divider()
        with st.form(key='my_form_czsc'):
            files = st.file_uploader(label='上传策略文件', type='json', accept_multiple_files=True)
            col1, col2 = st.columns([1, 1])
            bar_sdt = col2.date_input(label='行情开始日期', value=pd.to_datetime('2018-01-01'))
            gruop = col1.selectbox(label="回测品类", options=['A股主要指数', 'A股场内基金', '中证500成分股', '期货主力'], index=3)
            sdt, edt = date_range_picker("回测起止日期", default_start=pd.to_datetime('2019-01-01'), default_end=pd.to_datetime('2022-01-01'))
            col1, col2 = st.columns([1, 1])
            max_workers = int(col1.number_input(label='指定进程数量', value=cpu_count() // 4, min_value=1, max_value=cpu_count() // 2))
            fee = int(col2.number_input(label='单边手续费（单位：BP）', value=2, min_value=0, max_value=100))
            submit_button = st.form_submit_button(label='开始回测')

    if submit_button:
        st.session_state.files = files
        st.session_state.bar_sdt = bar_sdt
        st.session_state.gruop = gruop
        st.session_state.sdt = sdt
        st.session_state.edt = edt
        st.session_state.max_workers = max_workers
        st.session_state.fee = fee


    if not hasattr(st.session_state, 'files'):
        st.warning("请先设置策略回测参数")
        st.stop()

    files = st.session_state.files
    bar_sdt = st.session_state.bar_sdt
    gruop = st.session_state.gruop
    sdt = st.session_state.sdt
    edt = st.session_state.edt
    max_workers = st.session_state.max_workers
    fee = st.session_state.fee

    strategies = {file.name: json.loads(file.getvalue().decode("utf-8")) for file in files}
    hash_code = hashlib.sha256(f"{str(strategies)}".encode('utf-8')).hexdigest()[:8].upper()
    results_path = Path(os.getenv("base_path")) / "CTA策略回测" / f"{sdt}_{edt}_{hash_code}" / gruop
    results_path.mkdir(exist_ok=True, parents=True)

    with st.sidebar.expander("策略详情", expanded=False):
        tactic = JsonStreamStrategy(json_strategies=strategies, symbol='symbol')
        st.caption(f"K线周期列表：{tactic.freqs}")
        st.caption("独立信号列表：")
        st.json(tactic.unique_signals)
        st.caption("信号函数配置：")
        st.json(tactic.signals_config)

    backtest_all(strategies, results_path)

    file_traders = glob.glob(str(results_path / "*.trader"))
    if not file_traders:
        st.warning("当前回测参数下，没有任何标的回测结果；请调整回测参数后重试")
        st.stop()

    all_pos_names = [x.name for x in czsc.dill_load(file_traders[0]).positions]
    tabs = st.tabs(['全部品种', '选择特定品种组合'])

    with tabs[0]:
        pos_name = st.selectbox("选择持仓", all_pos_names, index=0, key="pos_name")
        show_backtest_results(file_traders, pos_name, fee=fee)

    with tabs[1]:
        candidates = [Path(x).stem for x in file_traders]
        sel_symbols = []
        with st.form(key='my_form_czsc_2'):
            col1, col2 = st.columns([1, 3])
            pos_name_a = col1.selectbox("选择持仓", all_pos_names, index=0, key="pos_name_a")
            sel_symbols = col2.multiselect("选择品种", candidates, default=candidates[:3])
            submit_button = st.form_submit_button(label='分析特定品种组合')

        if not sel_symbols:
            st.warning("请先选择品种组合")
            st.stop()

        sel_files= [x for x in file_traders if Path(x).stem in sel_symbols]
        show_backtest_results(sel_files, pos_name_a, fee=fee)


if __name__ == "__main__":
    main()
