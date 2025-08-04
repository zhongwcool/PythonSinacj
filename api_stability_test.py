#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新浪财经API稳定性测试脚本
测试API: http://hq.sinajs.cn/list=sz000498
每3秒更新一次，记录和统计成功率
"""

import requests
import time
import datetime
from collections import deque
import statistics
import json
import os

class APIStabilityTester:
    def __init__(self, api_url, interval=3):
        self.api_url = api_url
        self.interval = interval
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = deque(maxlen=100)  # 保存最近100次响应时间
        self.start_time = datetime.datetime.now()
        self.log_file = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.results = []
        
    def make_request(self):
        """发起API请求并记录结果"""
        try:
            # 添加请求头模拟浏览器访问
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Referer': 'http://finance.sina.com.cn/'
            }
            
            start_time = time.time()
            response = requests.get(self.api_url, headers=headers, timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            if response.status_code == 200 and response.text.strip():
                # 检查返回内容是否有效（新浪财经API返回的是JavaScript格式）
                if 'var hq_str_sz000498=' in response.text:
                    self.successful_requests += 1
                    status = "成功"
                    # 解析股票数据
                    data_part = response.text.split('="')[1].split('";')[0]
                    stock_data = data_part.split(',')
                    # 新浪财经API数据格式解析
                    # 0:股票名称, 1:今日开盘价, 2:昨日收盘价, 3:当前价格, 4:今日最高价, 5:今日最低价
                    # 6:竞买价, 7:竞卖价, 8:成交股数, 9:成交金额
                    # 10:买一量, 11:买一价, 12:买二量, 13:买二价, 14:买三量, 15:买三价, 16:买四量, 17:买四价, 18:买五量, 19:买五价
                    # 20:卖一量, 21:卖一价, 22:卖二量, 23:卖二价, 24:卖三量, 25:卖三价, 26:卖四量, 27:卖四价, 28:卖五量, 29:卖五价
                    # 30:日期, 31:时间
                    current_price = stock_data[3] if len(stock_data) > 3 else '0'
                    yesterday_close = stock_data[2] if len(stock_data) > 2 else '0'
                    
                    # 计算涨跌额和涨跌幅
                    try:
                        current = float(current_price)
                        yesterday = float(yesterday_close)
                        change_amount = current - yesterday
                        change_percent = (change_amount / yesterday * 100) if yesterday != 0 else 0
                    except (ValueError, ZeroDivisionError):
                        change_amount = 0
                        change_percent = 0
                    
                    stock_info = {
                        '股票名称': stock_data[0] if len(stock_data) > 0 else '',
                        '当前价格': current_price,
                        '昨日收盘': yesterday_close,
                        '涨跌额': f"{change_amount:+.3f}" if change_amount != 0 else '0.000',
                        '涨跌幅': f"{change_percent:+.2f}%" if change_percent != 0 else '0.00%',
                        '今日最高': stock_data[4] if len(stock_data) > 4 else '',
                        '今日最低': stock_data[5] if len(stock_data) > 5 else '',
                        '成交量': stock_data[8] if len(stock_data) > 8 else '',
                        '成交金额': stock_data[9] if len(stock_data) > 9 else '',
                        '买一价': stock_data[11] if len(stock_data) > 11 else '',
                        '买一量': stock_data[10] if len(stock_data) > 10 else '',
                        '卖一价': stock_data[21] if len(stock_data) > 21 else '',
                        '卖一量': stock_data[20] if len(stock_data) > 20 else '',
                        '更新时间': stock_data[30] + ' ' + stock_data[31] if len(stock_data) > 31 else ''
                    }
                else:
                    self.failed_requests += 1
                    status = "失败 - 数据格式异常"
                    stock_info = {}
            else:
                self.failed_requests += 1
                status = f"失败 - HTTP {response.status_code}"
                stock_info = {}
                
        except requests.exceptions.Timeout:
            self.failed_requests += 1
            response_time = 10000  # 超时设为10秒
            status = "失败 - 请求超时"
            stock_info = {}
        except requests.exceptions.RequestException as e:
            self.failed_requests += 1
            response_time = 0
            status = f"失败 - 网络错误: {str(e)}"
            stock_info = {}
        except Exception as e:
            self.failed_requests += 1
            response_time = 0
            status = f"失败 - 未知错误: {str(e)}"
            stock_info = {}
            
        self.total_requests += 1
        self.response_times.append(response_time)
        
        # 记录结果
        result = {
            'timestamp': datetime.datetime.now().isoformat(),
            'request_id': self.total_requests,
            'status': status,
            'response_time_ms': round(response_time, 2),
            'stock_info': stock_info
        }
        self.results.append(result)
        
        return result
    
    def get_statistics(self):
        """获取统计信息"""
        if self.total_requests == 0:
            return {}
            
        success_rate = (self.successful_requests / self.total_requests) * 100
        failure_rate = (self.failed_requests / self.total_requests) * 100
        
        running_time = datetime.datetime.now() - self.start_time
        
        stats = {
            '运行时间': str(running_time).split('.')[0],
            '总请求次数': self.total_requests,
            '成功次数': self.successful_requests,
            '失败次数': self.failed_requests,
            '成功率': f"{success_rate:.2f}%",
            '失败率': f"{failure_rate:.2f}%"
        }
        
        if self.response_times:
            stats.update({
                '平均响应时间': f"{statistics.mean(self.response_times):.2f}ms",
                '最快响应时间': f"{min(self.response_times):.2f}ms",
                '最慢响应时间': f"{max(self.response_times):.2f}ms",
                '响应时间中位数': f"{statistics.median(self.response_times):.2f}ms"
            })
            
        return stats
    
    def save_log(self):
        """保存日志到文件"""
        log_data = {
            'test_info': {
                'api_url': self.api_url,
                'interval': self.interval,
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.datetime.now().isoformat()
            },
            'statistics': self.get_statistics(),
            'detailed_results': self.results
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def print_status(self, result):
        """打印当前状态"""
        os.system('cls' if os.name == 'nt' else 'clear')  # 清屏
        
        print("=" * 80)
        print("🔍 新浪财经API稳定性测试")
        print("=" * 80)
        print(f"📡 测试API: {self.api_url}")
        print(f"⏱️  更新间隔: {self.interval}秒")
        print(f"📝 日志文件: {self.log_file}")
        print()
        
        # 显示最新请求结果
        print("📊 最新请求结果:")
        print("-" * 40)
        print(f"时间: {result['timestamp']}")
        print(f"状态: {result['status']}")
        print(f"响应时间: {result['response_time_ms']}ms")
        
        if result['stock_info']:
            print("\n📈 股票信息:")
            for key, value in result['stock_info'].items():
                if value:
                    print(f"  {key}: {value}")
        
        print()
        
        # 显示统计信息
        stats = self.get_statistics()
        print("📈 统计信息:")
        print("-" * 40)
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        print()
        print("💡 按 Ctrl+C 停止测试")
        print("=" * 80)
    
    def run(self):
        """运行测试"""
        # 开始前先清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("🚀 开始API稳定性测试...")
        print(f"📡 目标API: {self.api_url}")
        print(f"⏱️  测试间隔: {self.interval}秒")
        print()
        
        try:
            while True:
                result = self.make_request()
                self.print_status(result)
                
                # 每10次请求保存一次日志
                if self.total_requests % 10 == 0:
                    self.save_log()
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  测试已停止")
            self.save_log()
            
            print("\n📊 最终统计结果:")
            print("-" * 50)
            final_stats = self.get_statistics()
            for key, value in final_stats.items():
                print(f"{key}: {value}")
            
            print(f"\n📝 详细日志已保存到: {self.log_file}")
            print("✅ 测试完成!")

def main():
    # API配置
    api_url = "http://hq.sinajs.cn/list=sz000498"
    interval = 3  # 3秒间隔
    
    # 创建测试器实例
    tester = APIStabilityTester(api_url, interval)
    
    # 运行测试
    tester.run()

if __name__ == "__main__":
    main() 