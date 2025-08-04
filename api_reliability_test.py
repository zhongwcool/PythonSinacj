#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分时数据API可靠性测试工具
测试不同数据源的稳定性、响应速度、数据质量等指标
"""

import requests
import pandas as pd
import time
import datetime
import json
import os
from typing import List, Dict, Optional, Tuple
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class APIReliabilityTester:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        # 测试股票列表
        self.test_stocks = [
            ("sz000498", "山东路桥"),
            ("sh000001", "上证指数"),
            ("sh600000", "浦发银行"),
            ("sz000002", "万科A"),
            ("sh600036", "招商银行")
        ]
        
        # 测试结果存储
        self.test_results = {}
        self.lock = threading.Lock()
    
    def test_sina_realtime_api(self, stock_code: str, stock_name: str) -> Dict:
        """测试新浪财经实时数据API"""
        print(f"🔍 测试新浪财经实时API: {stock_name}({stock_code})")
        
        results = {
            'api_name': '新浪财经实时API',
            'stock_code': stock_code,
            'stock_name': stock_name,
            'success_count': 0,
            'fail_count': 0,
            'response_times': [],
            'data_quality_scores': [],
            'errors': []
        }
        
        # 进行多次测试
        for i in range(10):
            try:
                start_time = time.time()
                
                url = f"http://hq.sinajs.cn/list={stock_code}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                response_time = time.time() - start_time
                results['response_times'].append(response_time)
                
                if response.status_code == 200 and response.text.strip():
                    if f'var hq_str_{stock_code}=' in response.text:
                        data_part = response.text.split('="')[1].split('";')[0]
                        stock_data = data_part.split(',')
                        
                        # 数据质量检查
                        quality_score = self._check_data_quality(stock_data, 'sina_realtime')
                        results['data_quality_scores'].append(quality_score)
                        
                        results['success_count'] += 1
                        print(f"  ✅ 第{i+1}次测试成功 - 响应时间: {response_time:.3f}s - 质量评分: {quality_score:.2f}")
                    else:
                        results['fail_count'] += 1
                        results['errors'].append(f"第{i+1}次: 数据格式错误")
                        print(f"  ❌ 第{i+1}次测试失败 - 数据格式错误")
                else:
                    results['fail_count'] += 1
                    results['errors'].append(f"第{i+1}次: HTTP {response.status_code}")
                    print(f"  ❌ 第{i+1}次测试失败 - HTTP {response.status_code}")
                    
            except Exception as e:
                results['fail_count'] += 1
                results['errors'].append(f"第{i+1}次: {str(e)}")
                print(f"  ❌ 第{i+1}次测试异常: {e}")
            
            time.sleep(0.5)  # 避免请求过于频繁
        
        return results
    
    def test_sina_minute_api(self, stock_code: str, stock_name: str) -> Dict:
        """测试新浪财经分钟数据API"""
        print(f"🔍 测试新浪财经分钟API: {stock_name}({stock_code})")
        
        results = {
            'api_name': '新浪财经分钟API',
            'stock_code': stock_code,
            'stock_name': stock_name,
            'success_count': 0,
            'fail_count': 0,
            'response_times': [],
            'data_quality_scores': [],
            'errors': []
        }
        
        # 进行多次测试
        for i in range(5):  # 分钟数据测试次数较少，避免过于频繁
            try:
                start_time = time.time()
                
                url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
                params = {
                    'symbol': stock_code,
                    'scale': 1,
                    'ma': 5,
                    'datalen': 240
                }
                
                response = requests.get(url, params=params, headers=self.headers, timeout=15)
                
                response_time = time.time() - start_time
                results['response_times'].append(response_time)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data and len(data) > 0:
                            # 数据质量检查
                            quality_score = self._check_minute_data_quality(data)
                            results['data_quality_scores'].append(quality_score)
                            
                            results['success_count'] += 1
                            print(f"  ✅ 第{i+1}次测试成功 - 响应时间: {response_time:.3f}s - 数据条数: {len(data)} - 质量评分: {quality_score:.2f}")
                        else:
                            results['fail_count'] += 1
                            results['errors'].append(f"第{i+1}次: 空数据")
                            print(f"  ❌ 第{i+1}次测试失败 - 空数据")
                    except json.JSONDecodeError:
                        results['fail_count'] += 1
                        results['errors'].append(f"第{i+1}次: JSON解析失败")
                        print(f"  ❌ 第{i+1}次测试失败 - JSON解析失败")
                else:
                    results['fail_count'] += 1
                    results['errors'].append(f"第{i+1}次: HTTP {response.status_code}")
                    print(f"  ❌ 第{i+1}次测试失败 - HTTP {response.status_code}")
                    
            except Exception as e:
                results['fail_count'] += 1
                results['errors'].append(f"第{i+1}次: {str(e)}")
                print(f"  ❌ 第{i+1}次测试异常: {e}")
            
            time.sleep(1)  # 分钟数据请求间隔更长
        
        return results
    
    def test_eastmoney_minute_api(self, stock_code: str, stock_name: str) -> Dict:
        """测试东方财富分钟数据API"""
        print(f"🔍 测试东方财富分钟API: {stock_name}({stock_code})")
        
        results = {
            'api_name': '东方财富分钟API',
            'stock_code': stock_code,
            'stock_name': stock_name,
            'success_count': 0,
            'fail_count': 0,
            'response_times': [],
            'data_quality_scores': [],
            'errors': []
        }
        
        # 进行多次测试
        for i in range(5):
            try:
                start_time = time.time()
                
                url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
                params = {
                    'secid': f'0.{stock_code[2:]}' if stock_code.startswith('sz') else f'1.{stock_code[2:]}',
                    'fields1': 'f1,f2,f3,f4,f5,f6',
                    'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                    'klt': 1,
                    'fqt': 0,
                    'beg': 0,
                    'end': 20500101,
                    'smplmt': 240,
                    'lmt': 240
                }
                
                response = requests.get(url, params=params, headers=self.headers, timeout=15)
                
                response_time = time.time() - start_time
                results['response_times'].append(response_time)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get('data') and data['data'].get('klines'):
                            klines = data['data']['klines']
                            
                            # 数据质量检查
                            quality_score = self._check_eastmoney_data_quality(klines)
                            results['data_quality_scores'].append(quality_score)
                            
                            results['success_count'] += 1
                            print(f"  ✅ 第{i+1}次测试成功 - 响应时间: {response_time:.3f}s - 数据条数: {len(klines)} - 质量评分: {quality_score:.2f}")
                        else:
                            results['fail_count'] += 1
                            results['errors'].append(f"第{i+1}次: 数据格式错误")
                            print(f"  ❌ 第{i+1}次测试失败 - 数据格式错误")
                    except json.JSONDecodeError:
                        results['fail_count'] += 1
                        results['errors'].append(f"第{i+1}次: JSON解析失败")
                        print(f"  ❌ 第{i+1}次测试失败 - JSON解析失败")
                else:
                    results['fail_count'] += 1
                    results['errors'].append(f"第{i+1}次: HTTP {response.status_code}")
                    print(f"  ❌ 第{i+1}次测试失败 - HTTP {response.status_code}")
                    
            except Exception as e:
                results['fail_count'] += 1
                results['errors'].append(f"第{i+1}次: {str(e)}")
                print(f"  ❌ 第{i+1}次测试异常: {e}")
            
            time.sleep(1)
        
        return results
    
    def _check_data_quality(self, stock_data: List[str], data_type: str) -> float:
        """检查数据质量"""
        score = 0.0
        total_checks = 0
        
        if data_type == 'sina_realtime':
            # 检查必要字段是否存在且不为空
            required_fields = [0, 1, 2, 3, 4, 5, 8, 9]  # 股票名称、开盘、昨收、当前、最高、最低、成交量、成交额
            for field_idx in required_fields:
                total_checks += 1
                if len(stock_data) > field_idx and stock_data[field_idx] != '':
                    try:
                        float(stock_data[field_idx])
                        score += 1
                    except ValueError:
                        pass
            
            # 检查价格合理性
            if len(stock_data) > 3 and stock_data[3] != '':
                try:
                    current_price = float(stock_data[3])
                    if 0 < current_price < 10000:  # 价格在合理范围内
                        score += 1
                    total_checks += 1
                except ValueError:
                    pass
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _check_minute_data_quality(self, data: List[Dict]) -> float:
        """检查分钟数据质量"""
        if not data or len(data) == 0:
            return 0.0
        
        score = 0.0
        total_checks = 0
        
        # 检查数据完整性
        for item in data[:10]:  # 检查前10条数据
            total_checks += 1
            if isinstance(item, dict) and 'd' in item and 'o' in item and 'c' in item:
                try:
                    # 检查价格合理性
                    open_price = float(item['o'])
                    close_price = float(item['c'])
                    if 0 < open_price < 10000 and 0 < close_price < 10000:
                        score += 1
                except (ValueError, TypeError):
                    pass
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _check_eastmoney_data_quality(self, klines: List[str]) -> float:
        """检查东方财富数据质量"""
        if not klines or len(klines) == 0:
            return 0.0
        
        score = 0.0
        total_checks = 0
        
        # 检查数据完整性
        for line in klines[:10]:  # 检查前10条数据
            total_checks += 1
            parts = line.split(',')
            if len(parts) >= 6:  # 至少包含时间、开高低收、成交量、成交额
                try:
                    # 检查价格合理性
                    open_price = float(parts[1])
                    close_price = float(parts[2])
                    if 0 < open_price < 10000 and 0 < close_price < 10000:
                        score += 1
                except (ValueError, IndexError):
                    pass
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def run_comprehensive_test(self):
        """运行全面的API可靠性测试"""
        print("🚀 开始分时数据API可靠性测试")
        print("=" * 60)
        
        all_results = []
        
        # 测试新浪财经实时API
        print("\n📊 测试新浪财经实时API...")
        for stock_code, stock_name in self.test_stocks:
            result = self.test_sina_realtime_api(stock_code, stock_name)
            all_results.append(result)
        
        # 测试新浪财经分钟API
        print("\n📊 测试新浪财经分钟API...")
        for stock_code, stock_name in self.test_stocks:
            result = self.test_sina_minute_api(stock_code, stock_name)
            all_results.append(result)
        
        # 测试东方财富分钟API
        print("\n📊 测试东方财富分钟API...")
        for stock_code, stock_name in self.test_stocks:
            result = self.test_eastmoney_minute_api(stock_code, stock_name)
            all_results.append(result)
        
        # 生成测试报告
        self._generate_test_report(all_results)
    
    def _generate_test_report(self, results: List[Dict]):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📋 API可靠性测试报告")
        print("=" * 60)
        
        # 按API分组统计
        api_stats = {}
        
        for result in results:
            api_name = result['api_name']
            if api_name not in api_stats:
                api_stats[api_name] = {
                    'total_tests': 0,
                    'success_count': 0,
                    'fail_count': 0,
                    'response_times': [],
                    'quality_scores': [],
                    'stocks_tested': []
                }
            
            stats = api_stats[api_name]
            total_tests = result['success_count'] + result['fail_count']
            
            stats['total_tests'] += total_tests
            stats['success_count'] += result['success_count']
            stats['fail_count'] += result['fail_count']
            stats['response_times'].extend(result['response_times'])
            stats['quality_scores'].extend(result['data_quality_scores'])
            stats['stocks_tested'].append(result['stock_code'])
        
        # 输出统计结果
        for api_name, stats in api_stats.items():
            print(f"\n🔍 {api_name}")
            print("-" * 40)
            
            success_rate = (stats['success_count'] / stats['total_tests'] * 100) if stats['total_tests'] > 0 else 0
            avg_response_time = statistics.mean(stats['response_times']) if stats['response_times'] else 0
            avg_quality_score = statistics.mean(stats['quality_scores']) if stats['quality_scores'] else 0
            
            print(f"📈 成功率: {success_rate:.1f}% ({stats['success_count']}/{stats['total_tests']})")
            print(f"⏱️  平均响应时间: {avg_response_time:.3f}秒")
            print(f"🎯 平均数据质量评分: {avg_quality_score:.2f}")
            print(f"📊 测试股票: {', '.join(stats['stocks_tested'])}")
            
            if stats['response_times']:
                min_time = min(stats['response_times'])
                max_time = max(stats['response_times'])
                print(f"⏱️  响应时间范围: {min_time:.3f}s - {max_time:.3f}s")
        
        # 保存详细报告
        self._save_detailed_report(results)
        
        print("\n" + "=" * 60)
        print("✅ API可靠性测试完成！")
    
    def _save_detailed_report(self, results: List[Dict]):
        """保存详细测试报告"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_reliability_report_{timestamp}.json"
        
        report_data = {
            'test_time': datetime.datetime.now().isoformat(),
            'test_stocks': self.test_stocks,
            'results': results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细报告已保存: {filename}")

def main():
    """主函数"""
    tester = APIReliabilityTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 