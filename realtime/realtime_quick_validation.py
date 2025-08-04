#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速数据源验证工具
快速验证多个数据源是否有效获取开盘到现在的实时数据
覆盖所有主要数据源：新浪财经、腾讯财经、东方财富
"""

import requests
import time
import datetime
import json
from typing import Dict, List

class QuickDataValidation:
    def __init__(self):
        # 创建会话对象，保持连接
        self.session = requests.Session()
        
        # 更完整的请求头，模拟真实浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        # 测试股票列表 - 包含不同类型的股票
        self.test_stocks = [
            ("sz000498", "山东路桥"),      # 深市股票
            ("sh600000", "浦发银行"),      # 沪市股票
            ("sh000001", "上证指数"),      # 指数
            ("sz399001", "深证成指")       # 指数
        ]
        
        # 数据源配置
        self.data_sources = [
            {
                'name': '新浪财经',
                'test_func': self._test_sina_realtime,
                'description': '实时价格数据'
            },
            {
                'name': '腾讯财经',
                'test_func': self._test_tencent_realtime,
                'description': '实时价格数据'
            },
            {
                'name': '东方财富',
                'test_func': self._test_eastmoney_minute,
                'description': '分钟级数据'
            }
        ]
    
    def _test_sina_realtime(self, stock_code: str, stock_name: str) -> dict:
        """测试新浪财经实时数据"""
        try:
            start_time = time.time()
            
            # 新浪财经特定的请求头
            sina_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Referer': 'http://finance.sina.com.cn/',
                'Host': 'hq.sinajs.cn'
            }
            
            url = f"http://hq.sinajs.cn/list={stock_code}"
            response = self.session.get(url, headers=sina_headers, timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response.text.strip():
                if f'var hq_str_{stock_code}=' in response.text:
                    data_part = response.text.split('="')[1].split('";')[0]
                    stock_data = data_part.split(',')
                    
                    if len(stock_data) > 3 and stock_data[3] != '':
                        current_price = float(stock_data[3])
                        stock_name = stock_data[0]
                        volume = int(stock_data[8]) if len(stock_data) > 8 and stock_data[8] != '' else 0
                        
                        return {
                            'status': 'success',
                            'response_time': response_time,
                            'data': {
                                '股票名称': stock_name,
                                '当前价格': current_price,
                                '成交量': volume,
                                '更新时间': f"{stock_data[30]} {stock_data[31]}" if len(stock_data) > 31 else ''
                            }
                        }
            
            return {
                'status': 'failed',
                'response_time': response_time,
                'error': f'HTTP {response.status_code} 或数据格式错误'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _test_tencent_realtime(self, stock_code: str, stock_name: str) -> dict:
        """测试腾讯财经实时数据"""
        try:
            start_time = time.time()
            
            # 腾讯财经特定的请求头
            tencent_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Referer': 'http://stock.gtimg.cn/',
                'Host': 'qt.gtimg.cn'
            }
            
            url = f"http://qt.gtimg.cn/q={stock_code}"
            response = self.session.get(url, headers=tencent_headers, timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response.text.strip():
                if f'v_{stock_code}=' in response.text:
                    data_part = response.text.split('="')[1].split('";')[0]
                    stock_data = data_part.split('~')
                    
                    if len(stock_data) > 3 and stock_data[3] != '':
                        current_price = float(stock_data[3])
                        stock_name = stock_data[1]
                        volume = int(stock_data[6]) if len(stock_data) > 6 and stock_data[6] != '' else 0
                        
                        return {
                            'status': 'success',
                            'response_time': response_time,
                            'data': {
                                '股票名称': stock_name,
                                '当前价格': current_price,
                                '成交量': volume,
                                '更新时间': stock_data[30] if len(stock_data) > 30 else ''
                            }
                        }
            
            return {
                'status': 'failed',
                'response_time': response_time,
                'error': f'HTTP {response.status_code} 或数据格式错误'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _test_eastmoney_minute(self, stock_code: str, stock_name: str) -> dict:
        """测试东方财富分钟数据"""
        try:
            start_time = time.time()
            
            # 东方财富特定的请求头
            eastmoney_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'http://quote.eastmoney.com/',
                'Host': 'push2his.eastmoney.com'
            }
            
            # 东方财富分钟数据API
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                'secid': f'0.{stock_code[2:]}' if stock_code.startswith('sz') else f'1.{stock_code[2:]}',
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': 1,  # 1分钟K线
                'fqt': 0,
                'beg': 0,
                'end': 20500101,
                'smplmt': 10,
                'lmt': 10
            }
            
            response = self.session.get(url, params=params, headers=eastmoney_headers, timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('data') and data['data'].get('klines'):
                        klines = data['data']['klines']
                        if len(klines) > 0:
                            latest_line = klines[0].split(',')
                            latest_time = latest_line[0] if len(latest_line) > 0 else 'N/A'
                            latest_price = float(latest_line[2]) if len(latest_line) > 2 else 0
                            latest_volume = int(latest_line[5]) if len(latest_line) > 5 else 0
                            
                            return {
                                'status': 'success',
                                'response_time': response_time,
                                'data': {
                                    '股票名称': stock_name,
                                    '当前价格': latest_price,
                                    '成交量': latest_volume,
                                    '更新时间': latest_time,
                                    '数据条数': len(klines)
                                }
                            }
                except json.JSONDecodeError:
                    pass
            
            return {
                'status': 'failed',
                'response_time': response_time,
                'error': f'HTTP {response.status_code} 或数据格式错误'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    

    
    def validate_data_source(self, stock_code: str, stock_name: str) -> dict:
        """验证单个股票的所有数据源"""
        print(f"\n🔍 验证 {stock_name}({stock_code}) 的所有数据源...")
        
        results = {}
        total_success = 0
        total_failed = 0
        
        for source in self.data_sources:
            source_name = source['name']
            test_func = source['test_func']
            description = source['description']
            
            print(f"  📡 测试 {source_name} ({description})...")
            result = test_func(stock_code, stock_name)
            results[source_name] = result
            
            if result['status'] == 'success':
                total_success += 1
                data = result['data']
                print(f"    ✅ 成功 - {result['response_time']:.3f}s")
                print(f"      价格: {data['当前价格']}")
                print(f"      成交量: {data['成交量']:,}" if data['成交量'] else "      成交量: N/A")
                print(f"      时间: {data['更新时间']}")
            else:
                total_failed += 1
                print(f"    ❌ 失败 - {result.get('error', '未知错误')}")
            
            # 避免请求过于频繁
            time.sleep(1)
        
        return {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'results': results,
            'total_success': total_success,
            'total_failed': total_failed,
            'success_rate': (total_success / len(self.data_sources)) * 100
        }
    
    def run_validation(self):
        """运行所有数据源验证"""
        print("🚀 快速数据源验证")
        print("=" * 80)
        print(f"验证时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("目标: 快速验证所有数据源是否有效获取开盘到现在的实时数据")
        print("=" * 80)
        
        all_results = []
        total_stocks_success = 0
        total_stocks_failed = 0
        
        for stock_code, stock_name in self.test_stocks:
            result = self.validate_data_source(stock_code, stock_name)
            all_results.append(result)
            
            if result['success_rate'] >= 50:  # 至少50%的数据源可用
                total_stocks_success += 1
            else:
                total_stocks_failed += 1
        
        # 打印汇总报告
        self._print_summary_report(all_results, total_stocks_success, total_stocks_failed)
    
    def _print_summary_report(self, all_results: List[dict], total_stocks_success: int, total_stocks_failed: int):
        """打印汇总报告"""
        print("\n" + "=" * 80)
        print("📊 快速验证汇总报告")
        print("=" * 80)
        
        total_stocks = len(all_results)
        stock_success_rate = (total_stocks_success / total_stocks) * 100
        
        print(f"测试股票数: {total_stocks}")
        print(f"股票成功率: {stock_success_rate:.1f}% ({total_stocks_success}/{total_stocks})")
        
        # 数据源统计
        source_stats = {}
        for result in all_results:
            for source_name, source_result in result['results'].items():
                if source_name not in source_stats:
                    source_stats[source_name] = {'success': 0, 'failed': 0, 'response_times': []}
                
                if source_result['status'] == 'success':
                    source_stats[source_name]['success'] += 1
                    source_stats[source_name]['response_times'].append(source_result['response_time'])
                else:
                    source_stats[source_name]['failed'] += 1
        
        print(f"\n📡 数据源统计:")
        for source_name, stats in source_stats.items():
            total_tests = stats['success'] + stats['failed']
            success_rate = (stats['success'] / total_tests) * 100 if total_tests > 0 else 0
            avg_response_time = sum(stats['response_times']) / len(stats['response_times']) if stats['response_times'] else 0
            
            status_icon = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
            print(f"  {status_icon} {source_name}: {success_rate:.1f}% ({stats['success']}/{total_tests}) - 平均响应: {avg_response_time:.3f}s")
        
        print("\n💡 建议:")
        if stock_success_rate >= 80:
            print("✅ 数据源整体表现优秀，可以正常使用")
        elif stock_success_rate >= 60:
            print("⚠️  数据源表现一般，建议检查网络连接")
        else:
            print("❌ 数据源表现较差，建议检查API状态或网络连接")
        
        # 推荐最佳数据源
        best_sources = []
        for source_name, stats in source_stats.items():
            total_tests = stats['success'] + stats['failed']
            if total_tests > 0:
                success_rate = (stats['success'] / total_tests) * 100
                avg_response_time = sum(stats['response_times']) / len(stats['response_times']) if stats['response_times'] else 0
                best_sources.append((source_name, success_rate, avg_response_time))
        
        if best_sources:
            best_sources.sort(key=lambda x: (x[1], -x[2]), reverse=True)  # 按成功率降序，响应时间升序
            print(f"\n🏆 推荐数据源: {best_sources[0][0]} (成功率: {best_sources[0][1]:.1f}%, 响应时间: {best_sources[0][2]:.3f}s)")

def main():
    """主函数"""
    validator = QuickDataValidation()
    validator.run_validation()

if __name__ == "__main__":
    main() 