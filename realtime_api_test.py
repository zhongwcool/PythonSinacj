#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分时数据API可靠性测试脚本
分别测试实时数据和分钟数据的API可靠性
"""

from realtime_data_fetcher import RealtimeDataFetcher
import time
import datetime

def test_realtime_api(fetcher, stock_codes, test_name="实时数据API"):
    """测试实时数据API"""
    print(f"\n🔍 测试 {test_name}")
    print("=" * 60)
    
    results = {}
    
    for stock_code, stock_name in stock_codes:
        print(f"\n📈 测试 {stock_name}({stock_code})...")
        
        try:
            start_time = time.time()
            realtime_data = fetcher.get_realtime_data(stock_code, 'realtime')
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            if realtime_data:
                # 数据质量检查
                data_quality = check_realtime_data_quality(realtime_data)
                
                result = {
                    'status': '成功',
                    'response_time_ms': round(response_time, 2),
                    'data_quality': data_quality,
                    'current_price': realtime_data.get('当前价格', 0),
                    'change_percent': realtime_data.get('涨跌幅', 0),
                    'volume': realtime_data.get('成交量', 0),
                    'update_time': realtime_data.get('更新时间', '')
                }
                
                print(f"✅ 成功 - {response_time:.0f}ms")
                print(f"   当前价格: {result['current_price']:.2f}")
                print(f"   涨跌幅: {result['change_percent']:+.2f}%")
                print(f"   成交量: {result['volume']:,.0f}")
                print(f"   数据质量: {data_quality['score']}/100")
                
            else:
                result = {
                    'status': '失败',
                    'response_time_ms': round(response_time, 2),
                    'data_quality': {'score': 0, 'issues': ['无数据返回']},
                    'current_price': 0,
                    'change_percent': 0,
                    'volume': 0,
                    'update_time': ''
                }
                print(f"❌ 失败 - 无数据返回, {response_time:.0f}ms")
                
        except Exception as e:
            result = {
                'status': '错误',
                'response_time_ms': 0,
                'data_quality': {'score': 0, 'issues': [f'异常: {str(e)}']},
                'current_price': 0,
                'change_percent': 0,
                'volume': 0,
                'update_time': ''
            }
            print(f"❌ 错误 - {str(e)}")
        
        results[stock_code] = result
        time.sleep(1)  # 避免请求过于频繁
    
    return results

def test_minute_api(fetcher, stock_codes, test_name="分钟数据API"):
    """测试分钟数据API"""
    print(f"\n🔍 测试 {test_name}")
    print("=" * 60)
    
    results = {}
    
    for stock_code, stock_name in stock_codes:
        print(f"\n📈 测试 {stock_name}({stock_code})...")
        
        try:
            start_time = time.time()
            minute_df = fetcher.get_minute_data(stock_code, days=1, data_source='auto')
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            if minute_df is not None and not minute_df.empty:
                # 数据质量检查
                data_quality = check_minute_data_quality(minute_df)
                
                result = {
                    'status': '成功',
                    'response_time_ms': round(response_time, 2),
                    'data_quality': data_quality,
                    'data_count': len(minute_df),
                    'date_range': f"{minute_df['时间'].min().strftime('%Y-%m-%d %H:%M')} 至 {minute_df['时间'].max().strftime('%Y-%m-%d %H:%M')}",
                    'latest_price': minute_df.iloc[-1]['收盘价'] if '收盘价' in minute_df.columns else 0
                }
                
                print(f"✅ 成功 - {len(minute_df)}条数据, {response_time:.0f}ms")
                print(f"   时间范围: {result['date_range']}")
                print(f"   最新价格: {result['latest_price']:.2f}")
                print(f"   数据质量: {data_quality['score']}/100")
                
            else:
                result = {
                    'status': '失败',
                    'response_time_ms': round(response_time, 2),
                    'data_quality': {'score': 0, 'issues': ['无数据返回']},
                    'data_count': 0,
                    'date_range': '无',
                    'latest_price': 0
                }
                print(f"❌ 失败 - 无数据返回, {response_time:.0f}ms")
                
        except Exception as e:
            result = {
                'status': '错误',
                'response_time_ms': 0,
                'data_quality': {'score': 0, 'issues': [f'异常: {str(e)}']},
                'data_count': 0,
                'date_range': '无',
                'latest_price': 0
            }
            print(f"❌ 错误 - {str(e)}")
        
        results[stock_code] = result
        time.sleep(2)  # 避免请求过于频繁
    
    return results

def check_realtime_data_quality(data):
    """检查实时数据质量"""
    issues = []
    score = 100
    
    # 检查必要字段
    required_fields = ['当前价格', '涨跌幅', '成交量', '更新时间']
    missing_fields = [field for field in required_fields if field not in data or data[field] == '']
    if missing_fields:
        issues.append(f"缺少字段: {missing_fields}")
        score -= 20
    
    # 检查价格合理性
    if '当前价格' in data and data['当前价格'] <= 0:
        issues.append("价格异常")
        score -= 15
    
    # 检查涨跌幅合理性
    if '涨跌幅' in data and abs(data['涨跌幅']) > 20:
        issues.append("涨跌幅异常")
        score -= 10
    
    # 检查成交量合理性
    if '成交量' in data and data['成交量'] < 0:
        issues.append("成交量异常")
        score -= 10
    
    return {
        'score': max(0, score),
        'issues': issues
    }

def check_minute_data_quality(df):
    """检查分钟数据质量"""
    issues = []
    score = 100
    
    # 检查数据完整性
    if df.empty:
        issues.append("数据为空")
        score -= 100
    
    # 检查必要列
    required_columns = ['时间', '开盘价', '最高价', '最低价', '收盘价', '成交量']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        issues.append(f"缺少列: {missing_columns}")
        score -= 20
    
    # 检查数据类型
    if '收盘价' in df.columns:
        try:
            null_count = df['收盘价'].isnull().sum()
            if null_count > 0:
                issues.append(f"收盘价有{null_count}个空值")
                score -= 10
        except:
            issues.append("收盘价数据类型错误")
            score -= 15
    
    # 检查数据合理性
    if '收盘价' in df.columns and '最高价' in df.columns and '最低价' in df.columns:
        try:
            # 检查最高价是否大于等于最低价
            invalid_high_low = (df['最高价'] < df['最低价']).sum()
            if invalid_high_low > 0:
                issues.append(f"最高价小于最低价: {invalid_high_low}条")
                score -= 10
        except:
            pass
    
    return {
        'score': max(0, score),
        'issues': issues
    }

def print_api_summary_report(all_results, api_name):
    """打印API汇总报告"""
    print(f"\n📊 {api_name} 汇总报告")
    print("=" * 60)
    
    total_tests = len(all_results)
    successful_tests = sum(1 for r in all_results.values() if r['status'] == '成功')
    failed_tests = total_tests - successful_tests
    
    print(f"总测试数: {total_tests}")
    print(f"成功数: {successful_tests}")
    print(f"失败数: {failed_tests}")
    print(f"成功率: {(successful_tests/total_tests*100):.1f}%")
    
    if successful_tests > 0:
        avg_response_time = sum(r['response_time_ms'] for r in all_results.values() if r['status'] == '成功') / successful_tests
        avg_data_quality = sum(r['data_quality']['score'] for r in all_results.values() if r['status'] == '成功') / successful_tests
        print(f"平均响应时间: {avg_response_time:.0f}ms")
        print(f"平均数据质量: {avg_data_quality:.1f}/100")
    
    # 详细结果
    print("\n详细结果:")
    for stock_code, result in all_results.items():
        status_icon = "✅" if result['status'] == '成功' else "❌"
        print(f"  {status_icon} {stock_code}: {result['status']} - {result['response_time_ms']:.0f}ms")

def main():
    print("🚀 分时数据API可靠性测试")
    print("=" * 80)
    print(f"测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建数据获取器
    fetcher = RealtimeDataFetcher()
    
    # 测试股票列表
    test_stocks = [
        ("sz000498", "山东路桥"),
        ("sh000001", "上证指数"),
        ("sz399001", "深证成指"),
        ("sh600000", "浦发银行"),
        ("sz000001", "平安银行")
    ]
    
    # 测试实时数据API
    realtime_results = test_realtime_api(fetcher, test_stocks, "实时数据API")
    print_api_summary_report(realtime_results, "实时数据API")
    
    # 测试分钟数据API
    minute_results = test_minute_api(fetcher, test_stocks, "分钟数据API")
    print_api_summary_report(minute_results, "分钟数据API")
    
    # 综合推荐
    print("\n" + "=" * 80)
    print("🏆 API推荐")
    print("=" * 80)
    
    # 实时数据API推荐
    realtime_success_rate = (sum(1 for r in realtime_results.values() if r['status'] == '成功') / len(realtime_results)) * 100
    realtime_avg_time = sum(r['response_time_ms'] for r in realtime_results.values() if r['status'] == '成功') / sum(1 for r in realtime_results.values() if r['status'] == '成功') if sum(1 for r in realtime_results.values() if r['status'] == '成功') > 0 else 0
    
    # 分钟数据API推荐
    minute_success_rate = (sum(1 for r in minute_results.values() if r['status'] == '成功') / len(minute_results)) * 100
    minute_avg_time = sum(r['response_time_ms'] for r in minute_results.values() if r['status'] == '成功') / sum(1 for r in minute_results.values() if r['status'] == '成功') if sum(1 for r in minute_results.values() if r['status'] == '成功') > 0 else 0
    
    print("📊 实时数据API:")
    print(f"   成功率: {realtime_success_rate:.1f}%")
    print(f"   平均响应时间: {realtime_avg_time:.0f}ms")
    
    print("\n📊 分钟数据API:")
    print(f"   成功率: {minute_success_rate:.1f}%")
    print(f"   平均响应时间: {minute_avg_time:.0f}ms")
    
    print("\n💡 建议:")
    if realtime_success_rate > 80:
        print("✅ 实时数据API表现良好，适合实时监控")
    else:
        print("⚠️  实时数据API需要改进")
    
    if minute_success_rate > 80:
        print("✅ 分钟数据API表现良好，适合技术分析")
    else:
        print("⚠️  分钟数据API需要改进")

if __name__ == "__main__":
    main() 