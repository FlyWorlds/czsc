# CZSC 项目运行与使用说明（Windows）

本文档面向“刚从 Git 拉下来的本地源码项目”，目标是快速跑通 `czsc`，并理解项目主要目录与文件用途。

## 1. 项目运行（从零开始）

### 1.1 进入项目目录

```powershell
cd D:\quantitative\czsc
```

### 1.2 创建虚拟环境（推荐 Python 3.12）

```powershell
C:\Python312\python.exe -m venv .venv
```

激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

### 1.3 安装依赖

```powershell
python -m pip install -i https://pypi.org/simple -r requirements.txt
python -m pip install -i https://pypi.org/simple setuptools wheel
```

> 说明：如果你公司/本机默认 pip 源不完整（如缺 `pyecharts`），优先使用官方源 `https://pypi.org/simple`。

### 1.4 验证安装是否成功

```powershell
python -c "import czsc; print(czsc.__version__)"
```

### 1.5 运行示例

```powershell
python .\examples\use_cta_research.py
```

或：

```powershell
python .\examples\run_dummy_backtest.py
```

## 2. 你当前环境的关键约束

`czsc/connectors/research.py` 中默认投研数据目录已调整为：

```text
D:\quantitative\CZSC投研数据
```

同时支持环境变量覆盖：

```powershell
$env:czsc_research_cache = "D:\quantitative\CZSC投研数据"
```

如果目录不存在，`research.py` 会直接抛错提示。

## 3. 项目目录作用说明

根目录主要结构如下：

- `czsc/`：核心源码包（策略、信号、交易、连接器、工具函数都在这里）
- `examples/`：可直接运行的示例脚本（建议新手从这里入手）
- `test/`：单元测试与功能测试
- `docs/`：文档与资料
- `requirements.txt`：运行依赖列表
- `setup.py`：打包配置与入口命令配置（如 `czsc` 命令）
- `README.md`：项目介绍与外部文档入口
- `.flake8`：代码风格与 lint 配置

## 4. `czsc/` 子目录与文件作用

- `czsc/__init__.py`：包初始化与对外导出 API（`import czsc` 后可直接访问的大量对象在这里聚合）
- `czsc/cmd.py`：命令行入口（`czsc` CLI，当前内置 `aphorism` 子命令）
- `czsc/analyze.py`：K 线分析核心逻辑（分型、笔等核心分析能力）
- `czsc/objects.py`：交易对象定义（信号、因子、事件、持仓、K线对象等）
- `czsc/strategies.py`：策略抽象与策略构建
- `czsc/signals/`：信号函数库（不同技术逻辑的信号实现）
- `czsc/traders/`：交易与回测执行逻辑（信号驱动、绩效统计等）
- `czsc/sensors/`：研究/扫描类模块（事件匹配、CTA 研究等）
- `czsc/connectors/`：数据连接层（如投研数据、本地/外部数据连接器）
- `czsc/utils/`：通用工具（绘图、缓存、日历、统计、IO等）
- `czsc/data/`：数据访问与缓存相关实现
- `czsc/fsa/`：飞书相关能力（消息、表格等）

## 5. `research.py` 怎么用

文件路径：`czsc/connectors/research.py`

主要提供两个函数：

- `get_symbols(name)`：读取某个分组下的标的代码（也支持 `name='ALL'`）
- `get_raw_bars(symbol, freq, sdt, edt)`：读取某标的并返回 CZSC 标准 K 线对象列表

建议用“模块导入”方式调用，不要直接把它当普通脚本路径去跑：

```python
from czsc.connectors.research import get_symbols, get_raw_bars

symbols = get_symbols("ALL")
bars = get_raw_bars("000001.SZ", "日线", "2020-01-01", "2020-12-31")
print(len(symbols), len(bars))
```

## 6. 常见问题与解决

### 问题1：`ModuleNotFoundError: No module named 'loguru'`

原因：依赖未安装完整。  
解决：激活 `.venv` 后执行：

```powershell
python -m pip install -i https://pypi.org/simple -r requirements.txt
```

### 问题2：直接运行 `python .\czsc\connectors\research.py` 报 `No module named 'czsc'`

原因：直接运行包内文件会触发相对导入路径问题。  
解决：改为模块方式：

```powershell
python -m czsc.connectors.research
```

### 问题3：提示 tushare token

这不是项目崩溃，是部分数据功能需要配置 tushare token。  
如果你仅用本地投研共享数据，可先忽略；若用 tushare 数据源，再按 tushare 文档配置 token。

## 7. 建议的日常使用流程

每次开发前：

```powershell
cd D:\quantitative\czsc
.\.venv\Scripts\Activate.ps1
```

运行示例或测试：

```powershell
python .\examples\use_cta_research.py
pytest -q
```

---

如果你愿意，我可以在下一步再给你补一版“按功能分类的 examples 对照表”（例如：回测类、实时类、信号验证类分别运行哪个脚本）。

## 8. 文件级清单（逐文件作用）

说明：以下按当前仓库 `git ls-files` 清单整理，每个文件给出一句用途说明。

### 8.1 根目录与工程配置

- `.flake8`：Flake8 代码风格与检查规则。
- `.gitignore`：Git 忽略文件规则。
- `.readthedocs.yaml`：Read the Docs 构建配置。
- `LICENSE`：开源许可证（Apache）。
- `README.md`：项目总览与外部资料入口。
- `requirements.txt`：项目运行依赖。
- `setup.py`：打包与安装入口（含 `czsc` 命令行入口）。
- `red.md`：本地维护的运行/结构说明文档。
- `.vscode/settings.json`：VSCode/Cursor 工作区设置。
- `.github/workflows/python-publish.yml`：发布流程 CI 配置。
- `.github/workflows/pythonpackage.yml`：Python 包测试/构建 CI 配置。

### 8.2 `czsc/` 核心源码

- `czsc/__init__.py`：聚合导出包级 API 与版本信息。
- `czsc/analyze.py`：缠论核心分析逻辑（分型、笔、结构等）。
- `czsc/aphorism.py`：随机输出缠论语录。
- `czsc/cmd.py`：命令行入口与子命令定义。
- `czsc/eda.py`：探索分析相关工具。
- `czsc/enum.py`：枚举定义（方向、操作、频率等）。
- `czsc/envs.py`：环境变量读取与默认配置。
- `czsc/objects.py`：核心对象模型（Signal/Factor/Event/Bar/Position 等）。
- `czsc/strategies.py`：策略基类与 JSON 策略封装。

#### `czsc/connectors/` 数据连接层

- `czsc/connectors/__init__.py`：连接器模块初始化。
- `czsc/connectors/gm_connector.py`：掘金（GM）相关连接与适配。
- `czsc/connectors/jq_connector.py`：JoinQuant（聚宽）数据连接。
- `czsc/connectors/qmt_connector.py`：QMT 终端连接与数据/交易适配。
- `czsc/connectors/research.py`：本地投研共享数据读取接口。
- `czsc/connectors/ts_connector.py`：Tushare 数据连接与封装。

#### `czsc/data/` 数据访问层

- `czsc/data/__init__.py`：数据子模块初始化。
- `czsc/data/base.py`：数据层通用基类/抽象能力。
- `czsc/data/ts.py`：Tushare 数据访问实现。
- `czsc/data/ts_cache.py`：Tushare 本地缓存机制实现。

#### `czsc/fsa/` 飞书相关能力

- `czsc/fsa/__init__.py`：飞书能力聚合导出。
- `czsc/fsa/base.py`：飞书 API 基础调用封装。
- `czsc/fsa/bi_table.py`：飞书多维表格相关接口封装。
- `czsc/fsa/im.py`：飞书 IM 消息发送能力。
- `czsc/fsa/spreed_sheets.py`：飞书电子表格接口封装。

#### `czsc/sensors/` 研究与扫描

- `czsc/sensors/__init__.py`：sensors 聚合导出。
- `czsc/sensors/cta.py`：CTA 研究与回测流程封装。
- `czsc/sensors/event.py`：事件匹配传感器实现。
- `czsc/sensors/feature.py`：特征分析基类与流程。
- `czsc/sensors/plates.py`：板块轮动/板块研究相关逻辑。
- `czsc/sensors/utils.py`：sensors 公共辅助函数。

#### `czsc/signals/` 信号函数库

- `czsc/signals/__init__.py`：信号模块聚合导出。
- `czsc/signals/ang.py`：角度类技术信号。
- `czsc/signals/bar.py`：K线形态与序列信号。
- `czsc/signals/byi.py`：笔相关信号。
- `czsc/signals/coo.py`：协同/组合类信号逻辑。
- `czsc/signals/cxt.py`：上下文结构类信号。
- `czsc/signals/jcc.py`：经典形态/烛台信号。
- `czsc/signals/pos.py`：仓位状态与持仓相关信号。
- `czsc/signals/tas.py`：TA 指标类信号（含 TA-Lib 相关逻辑）。
- `czsc/signals/vol.py`：量能与成交量相关信号。
- `czsc/signals/zdy.py`：自定义扩展信号集合。

#### `czsc/traders/` 交易与回测执行

- `czsc/traders/__init__.py`：traders 聚合导出。
- `czsc/traders/base.py`：交易执行核心基类与流程。
- `czsc/traders/dummy.py`：离线 Dummy 回测执行器。
- `czsc/traders/optimize.py`：开平仓参数优化流程。
- `czsc/traders/performance.py`：绩效统计与评估指标。
- `czsc/traders/rwc.py`：Redis 权重客户端与相关能力。
- `czsc/traders/sig_parse.py`：信号解析与配置生成。
- `czsc/traders/weight_backtest.py`：权重组合回测引擎。

#### `czsc/utils/` 工具库

- `czsc/utils/__init__.py`：工具函数聚合导出。
- `czsc/utils/bar_generator.py`：多周期 K 线生成器。
- `czsc/utils/bi_info.py`：笔信息统计与汇总。
- `czsc/utils/cache.py`：缓存目录管理与清理。
- `czsc/utils/calendar.py`：交易日历工具。
- `czsc/utils/china_calendar.feather`：中国交易日历数据文件。
- `czsc/utils/corr.py`：相关性分析工具。
- `czsc/utils/cross.py`：截面分析辅助方法。
- `czsc/utils/data_client.py`：数据客户端封装。
- `czsc/utils/echarts_plot.py`：ECharts 绘图能力。
- `czsc/utils/features.py`：特征工程辅助函数。
- `czsc/utils/index_composition.py`：指数成分处理工具。
- `czsc/utils/io.py`：IO 与序列化辅助函数。
- `czsc/utils/minites_split.feather`：分钟分段辅助数据。
- `czsc/utils/oss.py`：阿里云 OSS 上传下载工具。
- `czsc/utils/plotly_plot.py`：Plotly 绘图能力。
- `czsc/utils/plt_plot.py`：Matplotlib 绘图能力。
- `czsc/utils/qywx.py`：企业微信消息通知工具。
- `czsc/utils/sig.py`：信号加工与计算辅助函数。
- `czsc/utils/signal_analyzer.py`：信号分析器主流程。
- `czsc/utils/st_components.py`：Streamlit 可视化组件。
- `czsc/utils/stats.py`：统计计算工具。
- `czsc/utils/ta.py`：技术指标计算封装。
- `czsc/utils/ta1.py`：技术指标计算扩展版本。
- `czsc/utils/trade.py`：交易价格/持仓收益相关工具。
- `czsc/utils/word_writer.py`：Word 报告输出工具。

### 8.3 `docs/` 文档与构建

- `docs/Makefile`：Sphinx 文档构建脚本（Unix）。
- `docs/make.bat`：Sphinx 文档构建脚本（Windows）。
- `docs/README.md`：文档目录说明。
- `docs/requirements.txt`：文档构建依赖。
- `docs/czsc.drawio`：架构图/流程图源文件。
- `docs/source/conf.py`：Sphinx 配置入口。
- `docs/source/index.rst`：文档首页目录。
- `docs/source/modules.rst`：模块文档索引。
- `docs/source/czsc.rst`：`czsc` 包 API 文档页。
- `docs/source/czsc.data.rst`：`czsc.data` API 文档页。
- `docs/source/命令行工具.md`：命令行工具使用文档。
- `docs/source/学习资料.md`：学习资料整理文档。
- `docs/source/开发日志.md`：开发记录与变更说明。

### 8.4 `examples/` 示例脚本

- `examples/__init__.py`：示例包初始化。
- `examples/use_cta_research.py`：CTA 投研回测示例（你当前在用）。
- `examples/use_optimize.py`：信号/策略优化示例。
- `examples/use_signals_validate.py`：信号准确性验证示例。
- `examples/run_dummy_backtest.py`：Dummy 回测示例。
- `examples/create_json_strategies.py`：生成 JSON 策略配置示例。
- `examples/create_one_three.py`：策略构建示例脚本。
- `examples/close_sma5_dist.py`：收盘价与 SMA5 距离统计示例。
- `examples/gm_backtest.py`：GM 回测示例。
- `examples/gm_realtime.py`：GM 实时运行示例。
- `examples/qmt_realtime.py`：QMT 实时运行示例。
- `examples/30分钟笔非多即空.py`：30分钟级别策略示例。
- `examples/TS数据源的形态选股.py`：Tushare 数据源形态选股示例。

#### `examples/animotion/`

- `examples/animotion/czsc_app.py`：可视化应用入口示例。
- `examples/animotion/czsc_human_replay.py`：人工回放可视化示例。
- `examples/animotion/czsc_qmt_checkpoint.py`：QMT 检查点可视化示例。
- `examples/animotion/czsc_stream.py`：流式可视化示例。
- `examples/animotion/templates/index.html`：可视化页面模板。
- `examples/animotion/templates/index_human_replay.html`：人工回放页面模板。

#### `examples/develop/`

- `examples/develop/__init__.py`：开发示例包初始化。
- `examples/develop/bar_end_time.py`：K线结束时间验证示例。
- `examples/develop/event_match_sensor.py`：事件匹配流程开发示例。
- `examples/develop/fixed_number_selector.py`：固定数量选股器示例。
- `examples/develop/index_composition.py`：指数成分研究示例。
- `examples/develop/weight_backtest.py`：权重回测开发示例。

#### `examples/dropit/`

- `examples/dropit/__init__.py`：临时/草稿示例包初始化。
- `examples/dropit/create_trade_price.py`：交易价格数据生成实验脚本。
- `examples/dropit/strategy_quick_start.py`：策略快速上手草稿示例。

#### `examples/signals_dev/`

- `examples/signals_dev/__init__.py`：信号开发示例初始化。
- `examples/signals_dev/signal_match.py`：信号匹配调试脚本。
- `examples/signals_dev/tas_macd_bc_V230803.py`：MACD 背驰信号版本脚本（V230803）。
- `examples/signals_dev/tas_macd_bc_V230804.py`：MACD 背驰信号版本脚本（V230804）。
- `examples/signals_dev/tas_macd_bc_ubi_V230804.py`：MACD 背驰 UBI 版本脚本。

#### `examples/streamlit_pages/`

- `examples/streamlit_pages/__init__.py`：Streamlit 页面包初始化。
- `examples/streamlit_pages/CTA策略回测V230911.py`：CTA 回测页面示例（V230911）。
- `examples/streamlit_pages/JSON策略回放V230911.py`：JSON 策略回放页面示例（V230911）。
- `examples/streamlit_pages/JSON策略回测.py`：JSON 策略回测页面示例。
- `examples/streamlit_pages/信号观察.py`：信号可视化观察页面。
- `examples/streamlit_pages/期货CTA投研.py`：期货 CTA 投研页面示例。
- `examples/streamlit_pages/history/JSON策略回放.py`：历史版 JSON 回放页面。
- `examples/streamlit_pages/history/策略回放.py`：历史版策略回放页面。

#### `examples/test_offline/`（离线测试示例）

- `examples/test_offline/__init__.py`：离线测试示例初始化。
- `examples/test_offline/test_data_client.py`：数据客户端离线测试。
- `examples/test_offline/test_fsa.py`：飞书接口离线测试。
- `examples/test_offline/test_resample_bar.py`：重采样逻辑测试。
- `examples/test_offline/test_rwc.py`：Redis 权重客户端测试。
- `examples/test_offline/test_ts_cache.py`：Tushare 缓存测试。
- `examples/test_offline/test_weight_backtest.py`：权重回测测试。

### 8.5 `test/` 单元测试与测试数据

- `test/__init__.py`：测试包初始化。
- `test/test_analyze.py`：`analyze` 模块测试。
- `test/test_bar_generator.py`：K线生成器测试。
- `test/test_calendar.py`：交易日历测试。
- `test/test_data.py`：数据层功能测试。
- `test/test_objects.py`：对象模型测试。
- `test/test_plot.py`：绘图函数测试（matplotlib）。
- `test/test_plotly_plot.py`：Plotly 绘图测试。
- `test/test_strategy.py`：策略基类与策略流程测试。
- `test/test_trade_utils.py`：交易工具函数测试。
- `test/test_trader_base.py`：交易器基础能力测试。
- `test/test_trader_sig.py`：交易信号逻辑测试。
- `test/test_utils.py`：通用工具函数测试。
- `test/test_word_writer.py`：Word 报告输出测试。
- `test/data/000001.SH_D.csv`：测试用日线样例数据。
- `test/data/000001.XSHG_1min.zip`：测试用分钟级样例数据。
