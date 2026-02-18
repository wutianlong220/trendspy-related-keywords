from trendspy import Trends
import pandas as pd
import json
import time
import random
from datetime import datetime
import requests
from urllib.parse import quote
import re

def get_related_queries(keyword, geo='', timeframe='today 12-m'):
    """
    获取关键词的相关查询数据，带请求限制
    """
    while True:  # 添加无限重试循环
        tr = Trends(hl='zh-CN')
        
        # 随机化 User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        headers = {
            'referer': 'https://www.google.com/',
            'User-Agent': random.choice(user_agents),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        try:
            print(f"[{keyword}] 开始查询...", flush=True)

            # 检查请求限制
            print(f"[{keyword}] 检查请求限制...", flush=True)
            request_limiter.wait_if_needed()
            print(f"[{keyword}] 请求限制检查通过", flush=True)

            # 添加随机延时
            delay = random.uniform(1, 3)
            print(f"[{keyword}] 等待 {delay:.1f} 秒后开始请求...", flush=True)
            time.sleep(delay)

            print(f"[{keyword}] 正在调用 Google Trends API (可能需要30-120秒)...", flush=True)
            related_data = tr.related_queries(
                keyword,
                headers=headers,
                geo=geo,
                timeframe=timeframe
            )
            print(f"[{keyword}] 成功获取数据！", flush=True)
            return related_data
            
        except Exception as e:
            error_msg = str(e)
            print(f"[{keyword}] ❌ 尝试获取数据时出错: {error_msg}", flush=True)

            # 如果是配额超限错误，等待后重试
            if "API quota exceeded" in error_msg:
                wait_time = random.uniform(300, 360)  # 等待5-6分钟
                print(f"[{keyword}] ⚠️  API配额超限，等待 {wait_time:.1f} 秒后重试...", flush=True)
                time.sleep(wait_time)
                print(f"[{keyword}] 🔄 开始重试...", flush=True)
                continue  # 继续下一次重试

            # 如果是NoneType错误，也等待后重试
            if "'NoneType' object has no attribute 'raise_for_status'" in error_msg:
                wait_time = random.uniform(60, 120)  # 等待1-2分钟
                print(f"[{keyword}] ⚠️  请求返回为空，等待 {wait_time:.1f} 秒后重试...", flush=True)
                time.sleep(wait_time)
                print(f"[{keyword}] 🔄 开始重试...", flush=True)
                continue  # 继续下一次重试

            # 其他错误则直接抛出
            print(f"[{keyword}] ❌ 遇到不可恢复的错误，停止重试", flush=True)
            raise

def batch_get_queries(keywords, geo='', timeframe='today 12-m', delay_between_queries=5):
    """
    批量获取多个关键词的数据，带间隔控制
    """
    results = {}

    print(f"\n{'='*60}", flush=True)
    print(f"开始批量查询 {len(keywords)} 个关键词", flush=True)
    print(f"{'='*60}\n", flush=True)

    for idx, keyword in enumerate(keywords, 1):
        try:
            print(f"\n[{idx}/{len(keywords)}] 开始处理关键词: {keyword}", flush=True)
            results[keyword] = get_related_queries(keyword, geo, timeframe)

            # 在请求之间添加延时
            if keyword != keywords[-1]:  # 如果不是最后一个关键词
                delay = delay_between_queries + random.uniform(0, 2)  # 基础延时加0-2秒的随机延时
                print(f"[{keyword}] ✅ 完成，等待 {delay:.1f} 秒后继续下一个查询...\n", flush=True)
                time.sleep(delay)
            else:
                print(f"[{keyword}] ✅ 完成（最后一个关键词）\n", flush=True)

        except Exception as e:
            print(f"[{keyword}] ❌ 获取数据失败: {str(e)}", flush=True)
            results[keyword] = None

            # 如果遇到错误，增加额外等待时间
            print(f"[{keyword}] 等待 10 秒后继续...", flush=True)
            time.sleep(10)

    print(f"\n{'='*60}", flush=True)
    print(f"批量查询完成！成功: {len([k for k,v in results.items() if v])}/{len(keywords)}", flush=True)
    print(f"{'='*60}\n", flush=True)

    return results

def save_related_queries(keyword, related_data):
    """
    保存相关查询数据到JSON文件
    """
    if not related_data:
        return
    
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    json_data = {
        'keyword': keyword,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'related_queries': {
            'top': related_data['top'].to_dict(orient='records') if isinstance(related_data.get('top'), pd.DataFrame) else related_data.get('top'),
            'rising': related_data['rising'].to_dict(orient='records') if isinstance(related_data.get('rising'), pd.DataFrame) else related_data.get('rising')
        }
    }
    
    # 保存为JSON文件
    filename = f"related_queries_{keyword}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    return filename

def print_related_queries(related_data):
    """
    打印相关查询词数据
    """
    if not related_data:
        print("没有相关查询数据")
        return
    
    print("\n相关查询词统计:")
    print("=" * 50)
    
    # 打印热门查询
    if 'top' in related_data and related_data['top'] is not None:
        print("\n热门查询:")
        print("-" * 30)
        df = related_data['top']
        if isinstance(df, pd.DataFrame):
            for _, row in df.iterrows():
                print(f"- {row['query']:<30} (相关度: {row['value']})")
    
    # 打印上升趋势查询
    if 'rising' in related_data and related_data['rising'] is not None:
        print("\n上升趋势查询:")
        print("-" * 30)
        df = related_data['rising']
        if isinstance(df, pd.DataFrame):
            for _, row in df.iterrows():
                print(f"- {row['query']:<30} (增长: {row['value']})")


# 主函数
# timeframe可能的值：
# today 12-m：12个月
# now 1-d：1天
# now 7-d：7天
# now 30-d：30天
# now 90-d：90天
# 日期格式：2024-12-28 2024-12-30
def main():
    # 设置要查询的关键词列表
    keywords = ['game']  # 可以添加多个关键词
    geo = ''
    timeframe = 'now 1-d'
    
    print("开始批量查询...")
    print(f"地区: {geo if geo else '全球'}")
    print(f"时间范围: {timeframe}")
    
    try:
        # 批量获取数据
        results = batch_get_queries(
            keywords,
            geo=geo,
            timeframe=timeframe,
            delay_between_queries=100  # 设置请求间隔
        )

        # 处理和保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        for keyword, data in results.items():
            if data:
                print(f"\n处理 {keyword} 的数据:")
                print_related_queries(data)
                filename = save_related_queries(keyword, data)
                print(f"数据已保存到文件: {filename}")
            else:
                print(f"\n未能获取 {keyword} 的数据")
                
    except Exception as e:
        print(f"批量查询过程中出错: {str(e)}")

class RequestLimiter:
    def __init__(self):
        self.requests = []  # 存储请求时间戳
        self.max_requests_per_min = 30  # 每分钟最大请求数
        self.max_requests_per_hour = 200  # 每小时最大请求数
        
    def can_make_request(self):
        """检查是否可以发起新请求"""
        current_time = time.time()
        
        # 清理超过1小时的旧请求记录
        self.requests = [t for t in self.requests if current_time - t < 3600]
        
        # 获取最近1分钟的请求数
        recent_min_requests = len([t for t in self.requests if current_time - t < 60])
        
        # 获取最近1小时的请求数
        recent_hour_requests = len(self.requests)
        
        if (recent_min_requests >= self.max_requests_per_min or 
            recent_hour_requests >= self.max_requests_per_hour):
            return False
        
        return True
    
    def add_request(self):
        """记录新的请求"""
        self.requests.append(time.time())
    
    def wait_if_needed(self):
        """如果需要，等待直到可以发送请求"""
        while not self.can_make_request():
            wait_time = random.uniform(5, 10)
            print(f"达到请求限制，等待 {wait_time:.1f} 秒...")
            time.sleep(wait_time)
        self.add_request()

# 创建全局请求限制器
request_limiter = RequestLimiter()

if __name__ == "__main__":
    main()
