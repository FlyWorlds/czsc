# CZSC FSA 说明

本目录是 CZSC 的飞书（Feishu / Lark）能力封装层，提供消息通知、电子表格与多维表格操作接口。

## 目录作用

- `base.py`：飞书 API 基类与统一请求函数（鉴权、重试、通用文件操作）
- `im.py`：即时消息能力（文本、图片、文件发送；用户 ID 查询）
- `spreed_sheets.py`：电子表格能力（创建、读取、写入、样式、工作表管理）
- `bi_table.py`：多维表格能力（列出数据表、读取记录）
- `__init__.py`：对外便捷函数封装（快速推送消息、读取表格等）

## 核心能力

- **统一鉴权与请求重试**：`FeishuApiBase` 负责 access token 获取与缓存，`request` 负责标准请求与错误处理
- **消息推送**：支持机器人 Webhook 推送、飞书应用批量推送文本/图片/文件
- **表格读写**：支持电子表格与多维表格读取，便于策略结果落表与协作
- **文件操作**：支持飞书云空间文件上传、下载、复制、移动、删除

## 常用入口

```python
from czsc.fsa import push_message, read_feishu_sheet

# 1) 发送文本消息
push_message(
    msg="策略运行完成",
    msg_type="text",
    feishu_app_id="your_app_id",
    feishu_app_secret="your_app_secret",
    feishu_members=["ou_xxx"],
)

# 2) 读取电子表格
df = read_feishu_sheet(
    spread_sheet_token="sht_xxx",
    feishu_app_id="your_app_id",
    feishu_app_secret="your_app_secret",
)
print(df.head())
```

## 使用建议

- 飞书凭证（`app_id` / `app_secret`）建议通过环境变量或配置文件管理，不要硬编码；
- 批量推送时建议做频控，避免短时高频触发接口限制；
- 对线上告警场景，建议同时保留本地日志，便于回溯推送失败原因；
- 首次接入时先用小范围成员（或测试群）验证消息格式与权限。

## 备注

- 目录中的 `spreed_sheets.py` 文件名沿用历史命名（应为 `spread_sheets` 的拼写），当前项目内已稳定使用该名称；
- 若后续扩展企业微信/钉钉等渠道，建议保持与本目录一致的“基类 + 子模块 + 便捷函数”结构。
