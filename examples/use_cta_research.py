# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2023/6/7 21:12
describe: 
"""
import sys
import os
sys.path.insert(0, '.')
sys.path.insert(0, '..')

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
quantitative_root = os.path.dirname(project_root)
research_cache = os.path.join(quantitative_root, "CZSC投研数据")

# 优先使用项目同级的投研共享数据目录，避免不同系统上的默认路径不一致。
if 'czsc_research_cache' not in os.environ and os.path.exists(research_cache):
    os.environ['czsc_research_cache'] = research_cache

from czsc import CTAResearch
from czsc.strategies import CzscStrategyExample2
from czsc.connectors.research import get_raw_bars, get_symbols

# 输出目录设置为“项目目录同级”，即 D:\quantitative\CTA投研\策略测试
results_path = os.path.join(quantitative_root, "CTA投研", "策略测试")

bot = CTAResearch(results_path=results_path, signals_module_name='czsc.signals',
                  strategy=CzscStrategyExample2, read_bars=get_raw_bars)

# 策略回放
# bot.replay(symbol='600256.SH', sdt='20220101', edt='20230101', refresh=True)


if __name__ == '__main__':
    # 策略回测，如果是使用多进程，必须在 __main__ 中执行，且必须是在命令行中执行
    bot.backtest(symbols=get_symbols("中证500成分股")[10:20], max_workers=3, bar_sdt='20190101', edt='20220101', sdt='20200101')


