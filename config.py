import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Notification Configuration
NOTIFICATION_CONFIG = {
    'method': 'email',  # 可选值: 'email', 'wechat', 'both'
    'wechat_receiver': os.getenv('TRENDS_WECHAT_RECEIVER', ''),  # 微信接收者的备注名或微信号
}

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': os.getenv('TRENDS_SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('TRENDS_SMTP_PORT', '587')),
    'sender_email': os.getenv('TRENDS_SENDER_EMAIL', ''),
    'sender_password': os.getenv('TRENDS_SENDER_PASSWORD', ''),
    'recipient_email': os.getenv('TRENDS_RECIPIENT_EMAIL', '')
}

# Keywords to monitor
KEYWORDS = [
    # A
    "action",
    "advisor",
    "agent",
    "analyzer",
    "anime",
    "answer",
    "assistant",

    # B
    "Best",
    "builder",

    # C
    "calculator",
    "cartoon",
    "cataloger",
    "character",
    "chart",
    "chat",
    "cheat",
    "checker",
    "clue",
    "code",
    "coloring page",
    "comparator",
    "compiler",
    "composer",
    "connector",
    "constructor",
    "converter",

    # D
    "crawler",
    "creator",

    # E
    "editor",
    "emoji",
    "enhancer",
    "evaluator",
    "example",
    "extractor",

    # F
    "face",
    "filter",
    "finder",
    "font",
    "format",

    # G
    "generator",
    "graph",
    "guide",

    # H
    "How to",
    "helper",
    "hint",
    "humanizer",

    # I
    "icon",
    "ideas",
    "illustration",
    "image",
    "interior design",

    # L
    "layout",
    "list",
    "logo",

    # M
    "maker",
    "manager",
    "meme",
    "model",
    "modifier",
    "monitor",
    "music",

    # O
    "online",
    "optimizer",

    # P
    "paraphaser",
    "pattern",
    "photo",
    "picture",
    "planner",
    "portal",
    "portrait",
    "processor",
    "product photo",

    # R
    "receiver",
    "recorder",
    "resources",
    "responder",
    "restore",

    # S
    "sample",
    "scheduler",
    "scraper",
    "sender",
    "simulator",
    "solver",
    "song",
    "sound",
    "speech",
    "starter",
    "style",
    "summarizer",
    "syncer",

    # T
    "tattoo",
    "template",
    "tester",
    "text",
    "tool",
    "top",
    "tracker",
    "transcriber",
    "translator",

    # U
    "uploader",
    "upscaler",

    # V
    "verifier",
    "video",
    "viewer",
    "voice",

    # W
    "writer",
]


# Trends Query Configuration
TRENDS_CONFIG = {
    'timeframe': 'last-3-d',  # 可选值: now 1-d, now 7-d, now 30-d, now 90-d, today 12-m, 
                            # last-2-d, last-3-d 或者 "2024-01-01 2024-01-31"
    'geo': '',  # 地区代码，例如: 'US' 表示美国, 'CN' 表示中国, '' 表示全球
}

# Rate Limiting Configuration
RATE_LIMIT_CONFIG = {
    'max_retries': 3,
    'min_delay_between_queries': 30,  # 最小延迟30秒（适应更多关键词）
    'max_delay_between_queries': 60,  # 最大延迟60秒（适应更多关键词）
    'batch_size': 5,  # 每批处理的关键词数量
    'batch_interval': 600,  # 批次间隔时间（秒）- 增加到10分钟
}

# Schedule Configuration
SCHEDULE_CONFIG = {
    'hour': 23,                    # 计划执行的小时（0-23）
    'minute': 5,                 # 计划执行的分钟（0-59）
    'random_delay_minutes': 15   # 随机延迟的最大分钟数（可选）
}

# Monitoring Configuration
MONITOR_CONFIG = {
    'rising_threshold': 500,  # 高增长趋势阈值
}

# Logging Configuration
LOGGING_CONFIG = {
    'log_file': 'trends_monitor.log',
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}

# Data Storage Configuration
STORAGE_CONFIG = {
    'data_dir_prefix': 'data_',  # 数据目录前缀
    'report_filename_prefix': 'daily_report_',  # 报告文件名前缀
    'json_filename_prefix': 'related_queries_'  # JSON文件名前缀
} 