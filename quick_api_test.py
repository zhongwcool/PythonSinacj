#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速API测试工具
快速验证各个分时数据API的基本功能和可用性
"""

import requests
import time
import json
from typing import Dict, Optional

class QuickAPITester:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 测试股票
        self.test_stock = "sz000498"  # 山东路桥
    
    def test_sina_realtime(self) -> Dict:
        """测试新浪财经实时API"""
        print("🔍 测试新浪财经实时API...")
        
        try:
            start_time = time.time()
            url = f"http://hq.sinajs.cn/list={self.test_stock}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response.text.strip():
                if f'var hq_str_{self.test_stock}=' in response.text:
                    data_part = response.text.split('="')[1].split('";')[0]
                    stock_data = data_part.split(',')
                    
                    if len(stock_data) > 3 and stock_data[3] != '':
                        current_price = float(stock_data[3])
                        stock_name = stock_data[0]
                        
                        print(f"  ✅ 成功 - 响应时间: {response_time:.3f}s")
                        print(f"     股票: {stock_name}")
                        print(f"     当前价格: {current_price}")
                        
                        return {
                            'status': 'success',
                            'response_time': response_time,
                            'stock_name': stock_name,
                            'current_price': current_price
                        }
            
            print(f"  ❌ 失败 - HTTP {response.status_code}")
            return {'status': 'failed', 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def test_sina_minute(self) -> Dict:
        """测试新浪财经分钟API"""
        print("🔍 测试新浪财经分钟API...")
        
        try:
            start_time = time.time()
            url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
            params = {
                'symbol': self.test_stock,
                'scale': 1,
                'ma': 5,
                'datalen': 10  # 只获取10条数据
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data and len(data) > 0:
                        print(f"  ✅ 成功 - 响应时间: {response_time:.3f}s")
                        print(f"     数据条数: {len(data)}")
                        print(f"     最新时间: {data[0].get('d', 'N/A')}")
                        
                        return {
                            'status': 'success',
                            'response_time': response_time,
                            'data_count': len(data),
                            'latest_time': data[0].get('d', 'N/A')
                        }
                    else:
                        print(f"  ❌ 失败 - 空数据")
                        return {'status': 'failed', 'error': '空数据'}
                except json.JSONDecodeError:
                    print(f"  ❌ 失败 - JSON解析错误")
                    return {'status': 'failed', 'error': 'JSON解析错误'}
            else:
                print(f"  ❌ 失败 - HTTP {response.status_code}")
                return {'status': 'failed', 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def test_eastmoney_minute(self) -> Dict:
        """测试东方财富分钟API"""
        print("🔍 测试东方财富分钟API...")
        
        try:
            start_time = time.time()
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                'secid': f'0.{self.test_stock[2:]}',  # sz000498 -> 0.000498
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': 1,
                'fqt': 0,
                'beg': 0,
                'end': 20500101,
                'smplmt': 10,
                'lmt': 10
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('data') and data['data'].get('klines'):
                        klines = data['data']['klines']
                        if len(klines) > 0:
                            latest_line = klines[0].split(',')
                            latest_time = latest_line[0] if len(latest_line) > 0 else 'N/A'
                            
                            print(f"  ✅ 成功 - 响应时间: {response_time:.3f}s")
                            print(f"     数据条数: {len(klines)}")
                            print(f"     最新时间: {latest_time}")
                            
                            return {
                                'status': 'success',
                                'response_time': response_time,
                                'data_count': len(klines),
                                'latest_time': latest_time
                            }
                        else:
                            print(f"  ❌ 失败 - 空数据")
                            return {'status': 'failed', 'error': '空数据'}
                    else:
                        print(f"  ❌ 失败 - 数据格式错误")
                        return {'status': 'failed', 'error': '数据格式错误'}
                except json.JSONDecodeError:
                    print(f"  ❌ 失败 - JSON解析错误")
                    return {'status': 'failed', 'error': 'JSON解析错误'}
            else:
                print(f"  ❌ 失败 - HTTP {response.status_code}")
                return {'status': 'failed', 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def test_tencent_realtime(self) -> Dict:
        """测试腾讯财经实时API"""
        print("🔍 测试腾讯财经实时API...")
        
        try:
            start_time = time.time()
            # 腾讯财经实时数据API
            url = f"http://qt.gtimg.cn/q={self.test_stock}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response.text.strip():
                if f'v_{self.test_stock}=' in response.text:
                    data_part = response.text.split('="')[1].split('";')[0]
                    stock_data = data_part.split('~')
                    
                    if len(stock_data) > 3 and stock_data[3] != '':
                        current_price = float(stock_data[3])
                        stock_name = stock_data[1]
                        
                        print(f"  ✅ 成功 - 响应时间: {response_time:.3f}s")
                        print(f"     股票: {stock_name}")
                        print(f"     当前价格: {current_price}")
                        
                        return {
                            'status': 'success',
                            'response_time': response_time,
                            'stock_name': stock_name,
                            'current_price': current_price
                        }
            
            print(f"  ❌ 失败 - HTTP {response.status_code}")
            return {'status': 'failed', 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def run_all_tests(self):
        """运行所有API测试"""
        print("🚀 开始快速API测试")
        print("=" * 50)
        print(f"测试股票: {self.test_stock}")
        print()
        
        results = {}
        
        # 测试各个API
        results['sina_realtime'] = self.test_sina_realtime()
        print()
        
        results['sina_minute'] = self.test_sina_minute()
        print()
        
        results['eastmoney_minute'] = self.test_eastmoney_minute()
        print()
        
        results['tencent_realtime'] = self.test_tencent_realtime()
        print()
        
        # 生成测试总结
        self._print_summary(results)
    
    def _print_summary(self, results: Dict):
        """打印测试总结"""
        print("=" * 50)
        print("📋 测试总结")
        print("=" * 50)
        
        api_names = {
            'sina_realtime': '新浪财经实时API',
            'sina_minute': '新浪财经分钟API',
            'eastmoney_minute': '东方财富分钟API',
            'tencent_realtime': '腾讯财经实时API'
        }
        
        success_count = 0
        total_count = len(results)
        
        for api_key, result in results.items():
            api_name = api_names.get(api_key, api_key)
            status = result.get('status', 'unknown')
            
            if status == 'success':
                success_count += 1
                response_time = result.get('response_time', 0)
                print(f"✅ {api_name}: 成功 ({response_time:.3f}s)")
            else:
                error = result.get('error', '未知错误')
                print(f"❌ {api_name}: 失败 - {error}")
        
        print()
        print(f"📊 总体结果: {success_count}/{total_count} 个API可用")
        
        if success_count == total_count:
            print("🎉 所有API都正常工作！")
        elif success_count > 0:
            print("⚠️  部分API可用，建议使用可用的API")
        else:
            print("🚨 所有API都无法访问，请检查网络连接")

def main():
    """主函数"""
    tester = QuickAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 