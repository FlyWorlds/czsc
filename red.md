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
