# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Google Trends 自动监控工具,用于定期查询关键词趋势数据、生成报告并通过邮件或微信发送通知。

支持通过 GitHub Actions 自动化运行定时任务。

## 运行和测试

### 测试模式
```bash
# 使用配置文件中的关键词运行一次测试
python trends_monitor.py --test

# 指定测试关键词
python trends_monitor.py --test --keywords "Python" "AI"
```

### 正常运行
```bash
# 按照配置的时间定时运行
python trends_monitor.py
```

### 微信工具
```bash
# 查询微信联系人/群ID,用于配置接收者
python wechat_utils.py
```

### 安装依赖
```bash
pip install -r requirements.txt
```

### GitHub Actions
- 定时任务通过 [.github/workflows/trends.yml](.github/workflows/trends.yml) 配置
- 每天 UTC 15:05 (北京时间 23:05) 自动运行
- 支持手动触发 (workflow_dispatch)
- 需要在 GitHub Secrets 中配置环境变量:
  - `TRENDS_SMTP_SERVER`
  - `TRENDS_SMTP_PORT`
  - `TRENDS_SENDER_EMAIL`
  - `TRENDS_SENDER_PASSWORD`
  - `TRENDS_RECIPIENT_EMAIL`
  - `TRENDS_WECHAT_RECEIVER`

## 配置管理

所有配置集中在 [config.py](config.py) 中:

- `KEYWORDS`: 要监控的关键词列表
- `TRENDS_CONFIG`: 查询时间范围和地区
- `RATE_LIMIT_CONFIG`: 请求频率控制(最小/最大延迟、批次大小)
- `SCHEDULE_CONFIG`: 定时任务配置(小时、分钟、随机延迟)
- `MONITOR_CONFIG`: 高增长趋势阈值
- `NOTIFICATION_CONFIG`: 通知方式('email', 'wechat', 'both')
- `EMAIL_CONFIG`: SMTP 邮件配置
- 环境变量通过 `.env` 文件配置(参考 [.env.example](.env.example))

## 架构说明

### 核心模块

- **[trends_monitor.py](trends_monitor.py)**: 主程序
  - `process_trends()`: 主处理流程,创建数据目录、批量处理关键词、生成报告
  - `process_keywords_batch()`: 批量处理一组关键词
  - `generate_daily_report()`: 生成 CSV 格式的每日报告
  - `check_rising_trends()`: 检查超过阈值的上升趋势
  - `run_scheduler()`: 定时调度器

- **[querytrends.py](querytrends.py)**: Google Trends API 交互
  - `get_related_queries()`: 单个关键词查询,带无限重试机制
  - `batch_get_queries()`: 批量查询,自动添加请求间延迟
  - `RequestLimiter`: 请求频率限制器类(每分钟/每小时限制)
  - `save_related_queries()`: 保存 JSON 格式数据

- **[notification.py](notification.py)**: 通知系统
  - `NotificationManager`: 统一的通知管理接口
  - 支持邮件(HTML 格式)和微信(纯文本)两种通知方式
  - 微信长消息自动分段发送
  - `_format_wechat_message()`: 将 HTML 报告转换为友好的微信文本格式

- **[wechat_utils.py](wechat_utils.py)**: 微信集成
  - `WeChatManager`: 单例模式的微信管理类
  - 支持登录状态缓存(`itchat.pkl`)
  - 按备注名/昵称/群名查找用户
  - 提供搜索联系人/群的交互式工具

### 关键设计模式

1. **请求限制**: `RequestLimiter` 类同时限制每分钟和每小时的请求数,配合随机延迟避免触发 API 限制
   - 每分钟最多 30 个请求
   - 每小时最多 200 个请求

2. **无限重试**: `get_related_queries()` 在遇到以下错误时会自动等待并无限重试:
   - "API quota exceeded" - 等待 5-6 分钟后重试
   - "'NoneType' object has no attribute 'raise_for_status'" - 等待 1-2 分钟后重试
   - 其他错误直接抛出,不重试

3. **批量处理**: 关键词按 `batch_size` 分批处理,批次间有 `batch_interval` 间隔

4. **Timeframe 转换**: `get_date_range_timeframe()` 支持特殊格式如 `last-2-d`、`last-3-d`,自动转换为日期范围格式

5. **指数退避重试**: 使用 `@backoff.on_exception` 装饰器处理网络错误,最多重试 3 次

6. **单例模式**: `WeChatManager` 使用线程安全的单例模式,确保全局只有一个微信连接实例

### 数据流

```
KEYWORDS → batch_get_queries() → Google Trends API
                                      ↓
                          save_related_queries() → JSON 文件
                                      ↓
                          generate_daily_report() → CSV 报告
                                      ↓
                          NotificationManager → 邮件/微信
```

### 数据存储

- 每日数据保存在 `data_YYYYMMDD/` 目录
- JSON: `related_queries_{keyword}_{timestamp}.json`
- CSV: `daily_report_{YYYYMMDD}.csv`

### 通知系统

- **NotificationManager** 统一管理邮件和微信通知
- 邮件使用 HTML 格式,支持附件
- 微信自动将 HTML 报告转换为友好的文本格式
- 长消息自动分段发送 (chunk_size=2000)
- 高增长趋势分批发送,每批最多 10 个趋势

### 调试

程序使用 `print()` 输出详细的调试信息 (flush=True 确保实时输出):
- `[关键词] 开始查询...`
- `[关键词] 检查请求限制...`
- `[关键词] 等待 X 秒后开始请求...`
- `[关键词] 正在调用 Google Trends API (可能需要30-120秒)...`

日志文件: [trends_monitor.log](trends_monitor.log)

## 注意事项

1. Gmail 需要开启两步验证并生成应用专用密码
2. 微信首次使用需扫码登录,登录状态会缓存在 `itchat.pkl`
3. Google Trends API 有请求频率限制,程序已实现智能限流
4. 修改 [config.py](config.py) 中的配置后无需重启,下次运行会自动加载新配置
5. TRENDS_CONFIG 中的 `timeframe` 支持 `last-2-d`、`last-3-d` 等特殊格式
6. 微信通知功能需要安装 `itchat`,如果未安装会自动跳过微信功能
7. `trends_monitor.py` 中有重复的邮件发送代码 (第41-74行),这是历史遗留问题,应使用 `NotificationManager` 代替

## Timeframe 参数说明

`querytrends.py` 中的 `timeframe` 参数支持以下格式:

- `now 1-d` - 最近 1 天
- `now 7-d` - 最近 7 天
- `now 30-d` - 最近 30 天
- `now 90-d` - 最近 90 天
- `today 12-m` - 最近 12 个月
- `last-2-d` / `last-3-d` - 特殊格式,自动转换为日期范围
- `2024-01-01 2024-01-31` - 自定义日期范围
