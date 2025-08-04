#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面分时数据API测试工具
测试多个数据源的稳定性、响应速度、数据质量等指标
"""

import requests
import pandas as pd
import time
import datetime
import json
import os
from typing import List, Dict, Optional, Tuple
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class ComprehensiveAPITester:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'http://finance.sina.com.cn/'
        }
        
        # 测试股票列表
        self.test_stocks = [
            ("sz000498", "山东路桥"),
            ("sh000001", "上证指数"),
            ("sh600000", "浦发银行"),
            ("sz000002", "万科A"),
            ("sh600036", "招商银行"),
            ("sz000858", "五粮液"),
            ("sh600519", "贵州茅台")
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
            'errors': [],
            'data_samples': []
        }
        
        # 进行多次测试
        for i in range(5):  # 减少测试次数避免被封
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
                        quality_score = self._check_sina_realtime_quality(stock_data)
                        results['data_quality_scores'].append(quality_score)
                        
                        # 保存数据样本
                        if i == 0:  # 只保存第一次成功的数据样本
                            results['data_samples'].append({
                                'current_price': float(stock_data[3]) if len(stock_data) > 3 and stock_data[3] != '' else 0,
                                'stock_name': stock_data[0] if len(stock_data) > 0 else '',
                                'volume': int(stock_data[8]) if len(stock_data) > 8 and stock_data[8] != '' else 0
                            })
                        
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
            
            time.sleep(1)  # 增加间隔避免被封
        
        return results
    
    def test_tencent_realtime_api(self, stock_code: str, stock_name: str) -> Dict:
        """测试腾讯财经实时数据API"""
        print(f"🔍 测试腾讯财经实时API: {stock_name}({stock_code})")
        
        results = {
            'api_name': '腾讯财经实时API',
            'stock_code': stock_code,
            'stock_name': stock_name,
            'success_count': 0,
            'fail_count': 0,
            'response_times': [],
            'data_quality_scores': [],
            'errors': [],
            'data_samples': []
        }
        
        # 进行多次测试
        for i in range(5):
            try:
                start_time = time.time()
                
                url = f"http://qt.gtimg.cn/q={stock_code}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                response_time = time.time() - start_time
                results['response_times'].append(response_time)
                
                if response.status_code == 200 and response.text.strip():
                    if f'v_{stock_code}=' in response.text:
                        data_part = response.text.split('="')[1].split('";')[0]
                        stock_data = data_part.split('~')
                        
                        # 数据质量检查
                        quality_score = self._check_tencent_realtime_quality(stock_data)
                        results['data_quality_scores'].append(quality_score)
                        
                        # 保存数据样本
                        if i == 0:
                            results['data_samples'].append({
                                'current_price': float(stock_data[3]) if len(stock_data) > 3 and stock_data[3] != '' else 0,
                                'stock_name': stock_data[1] if len(stock_data) > 1 else '',
                                'volume': int(stock_data[6]) if len(stock_data) > 6 and stock_data[6] != '' else 0
                            })
                        
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
            
            time.sleep(0.5)
        
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
            'errors': [],
            'data_samples': []
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
                            
                            # 保存数据样本
                            if i == 0 and len(klines) > 0:
                                latest_line = klines[0].split(',')
                                results['data_samples'].append({
                                    'data_count': len(klines),
                                    'latest_time': latest_line[0] if len(latest_line) > 0 else '',
                                    'latest_price': float(latest_line[2]) if len(latest_line) > 2 else 0
                                })
                            
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
    
    def test_netease_realtime_api(self, stock_code: str, stock_name: str) -> Dict:
        """测试网易财经实时数据API"""
        print(f"🔍 测试网易财经实时API: {stock_name}({stock_code})")
        
        results = {
            'api_name': '网易财经实时API',
            'stock_code': stock_code,
            'stock_name': stock_name,
            'success_count': 0,
            'fail_count': 0,
            'response_times': [],
            'data_quality_scores': [],
            'errors': [],
            'data_samples': []
        }
        
        # 进行多次测试
        for i in range(5):
            try:
                start_time = time.time()
                
                # 网易财经实时数据API
                url = f"http://api.money.126.net/data/feed/{stock_code}/money.api"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                response_time = time.time() - start_time
                results['response_times'].append(response_time)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data and stock_code in data:
                            stock_data = data[stock_code]
                            
                            # 数据质量检查
                            quality_score = self._check_netease_realtime_quality(stock_data)
                            results['data_quality_scores'].append(quality_score)
                            
                            # 保存数据样本
                            if i == 0:
                                results['data_samples'].append({
                                    'current_price': stock_data.get('price', 0),
                                    'stock_name': stock_data.get('name', ''),
                                    'change_percent': stock_data.get('percent', 0)
                                })
                            
                            results['success_count'] += 1
                            print(f"  ✅ 第{i+1}次测试成功 - 响应时间: {response_time:.3f}s - 质量评分: {quality_score:.2f}")
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
            
            time.sleep(0.5)
        
        return results
    
    def _check_sina_realtime_quality(self, stock_data: List[str]) -> float:
        """检查新浪实时数据质量"""
        score = 0.0
        total_checks = 0
        
        # 检查必要字段
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
                if 0 < current_price < 10000:
                    score += 1
                total_checks += 1
            except ValueError:
                pass
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def _check_tencent_realtime_quality(self, stock_data: List[str]) -> float:
        """检查腾讯实时数据质量"""
        score = 0.0
        total_checks = 0
        
        # 检查必要字段
        required_fields = [1, 3, 4, 5, 6]  # 股票名称、当前价格、昨收、开盘、成交量
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
                if 0 < current_price < 10000:
                    score += 1
                total_checks += 1
            except ValueError:
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
    
    def _check_netease_realtime_quality(self, stock_data: Dict) -> float:
        """检查网易实时数据质量"""
        score = 0.0
        total_checks = 0
        
        # 检查必要字段
        required_fields = ['price', 'name', 'percent', 'volume']
        for field in required_fields:
            total_checks += 1
            if field in stock_data and stock_data[field] is not None:
                score += 1
        
        # 检查价格合理性
        if 'price' in stock_data and stock_data['price'] is not None:
            try:
                price = float(stock_data['price'])
                if 0 < price < 10000:
                    score += 1
                total_checks += 1
            except (ValueError, TypeError):
                pass
        
        return score / total_checks if total_checks > 0 else 0.0
    
    def run_comprehensive_test(self):
        """运行全面的API可靠性测试"""
        print("🚀 开始全面分时数据API可靠性测试")
        print("=" * 70)
        
        all_results = []
        
        # 测试各个API
        apis_to_test = [
            ('sina_realtime', self.test_sina_realtime_api),
            ('tencent_realtime', self.test_tencent_realtime_api),
            ('eastmoney_minute', self.test_eastmoney_minute_api),
            ('netease_realtime', self.test_netease_realtime_api)
        ]
        
        for api_name, test_func in apis_to_test:
            print(f"\n📊 测试{api_name}...")
            for stock_code, stock_name in self.test_stocks:
                result = test_func(stock_code, stock_name)
                all_results.append(result)
        
        # 生成测试报告
        self._generate_comprehensive_report(all_results)
    
    def _generate_comprehensive_report(self, results: List[Dict]):
        """生成全面测试报告"""
        print("\n" + "=" * 70)
        print("📋 全面API可靠性测试报告")
        print("=" * 70)
        
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
                    'stocks_tested': [],
                    'data_samples': []
                }
            
            stats = api_stats[api_name]
            total_tests = result['success_count'] + result['fail_count']
            
            stats['total_tests'] += total_tests
            stats['success_count'] += result['success_count']
            stats['fail_count'] += result['fail_count']
            stats['response_times'].extend(result['response_times'])
            stats['quality_scores'].extend(result['data_quality_scores'])
            stats['stocks_tested'].append(result['stock_code'])
            stats['data_samples'].extend(result['data_samples'])
        
        # 输出统计结果
        for api_name, stats in api_stats.items():
            print(f"\n🔍 {api_name}")
            print("-" * 50)
            
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
            
            # 显示数据样本
            if stats['data_samples']:
                print(f"📋 数据样本: {stats['data_samples'][0] if stats['data_samples'] else '无'}")
        
        # 生成推荐
        self._generate_recommendations(api_stats)
        
        # 保存详细报告
        self._save_comprehensive_report(results)
        
        print("\n" + "=" * 70)
        print("✅ 全面API可靠性测试完成！")
    
    def _generate_recommendations(self, api_stats: Dict):
        """生成API使用建议"""
        print("\n💡 API使用建议")
        print("-" * 50)
        
        # 按成功率排序
        sorted_apis = sorted(api_stats.items(), key=lambda x: x[1]['success_count'] / x[1]['total_tests'], reverse=True)
        
        print("🏆 推荐使用顺序:")
        for i, (api_name, stats) in enumerate(sorted_apis, 1):
            success_rate = (stats['success_count'] / stats['total_tests'] * 100) if stats['total_tests'] > 0 else 0
            avg_response_time = statistics.mean(stats['response_times']) if stats['response_times'] else 0
            
            if success_rate > 80:
                status = "✅ 推荐"
            elif success_rate > 50:
                status = "⚠️  备用"
            else:
                status = "❌ 不推荐"
            
            print(f"{i}. {api_name}: {status} (成功率: {success_rate:.1f}%, 响应时间: {avg_response_time:.3f}s)")
    
    def _save_comprehensive_report(self, results: List[Dict]):
        """保存全面测试报告"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_api_report_{timestamp}.json"
        
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
    tester = ComprehensiveAPITester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 