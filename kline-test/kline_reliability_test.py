#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源可靠性测试脚本
分别测试新浪财经、东方财富、Yahoo Finance的可靠性
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from kline_data_fetcher import KlineDataFetcher
import time
import datetime
import pandas as pd


def test_single_data_source(fetcher, data_source_name, data_source_func, stock_codes, days=30):
    """测试单个数据源的可靠性"""
    print(f"\n🔍 测试 {data_source_name} 数据源")
    print("=" * 50)

    results = {}

    for stock_code, stock_name in stock_codes:
        print(f"\n📈 测试 {stock_name}({stock_code})...")

        try:
            start_time = time.time()

            # 调用对应的数据源函数
            df = data_source_func(stock_code, days)

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒

            if df is not None and not df.empty:
                # 数据质量检查
                data_quality = check_data_quality(df)

                result = {
                    'status': '成功',
                    'data_count': len(df),
                    'response_time_ms': round(response_time, 2),
                    'data_quality': data_quality,
                    'date_range': f"{df['日期'].min().strftime('%Y-%m-%d')} 至 {df['日期'].max().strftime('%Y-%m-%d')}",
                    'latest_price': df.iloc[-1]['收盘价'] if '收盘价' in df.columns else None
                }

                print(f"✅ 成功 - {len(df)}条数据, {response_time:.0f}ms")
                print(f"   数据质量: {data_quality['score']}/100")
                print(f"   日期范围: {result['date_range']}")
                print(f"   最新价格: {result['latest_price']:.2f}" if result['latest_price'] else "   最新价格: 无")

            else:
                result = {
                    'status': '失败',
                    'data_count': 0,
                    'response_time_ms': round(response_time, 2),
                    'data_quality': {'score': 0, 'issues': ['无数据返回']},
                    'date_range': '无',
                    'latest_price': None
                }
                print(f"❌ 失败 - 无数据返回, {response_time:.0f}ms")

        except Exception as e:
            result = {
                'status': '错误',
                'data_count': 0,
                'response_time_ms': 0,
                'data_quality': {'score': 0, 'issues': [f'异常: {str(e)}']},
                'date_range': '无',
                'latest_price': None
            }
            print(f"❌ 错误 - {str(e)}")

        results[stock_code] = result

        # 避免请求过于频繁
        time.sleep(1)

    return results


def check_data_quality(df):
    """检查数据质量"""
    issues = []
    score = 100

    # 检查数据完整性
    if df.empty:
        issues.append("数据为空")
        score -= 100

    # 检查必要列是否存在
    required_columns = ['日期', '开盘价', '最高价', '最低价', '收盘价', '成交量']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        issues.append(f"缺少列: {missing_columns}")
        score -= 20

    # 检查数据类型
    if '收盘价' in df.columns:
        try:
            df['收盘价'] = pd.to_numeric(df['收盘价'], errors='coerce')
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

            # 检查价格是否在合理范围
            zero_prices = (df['收盘价'] <= 0).sum()
            if zero_prices > 0:
                issues.append(f"收盘价异常: {zero_prices}条")
                score -= 10
        except:
            pass

    # 检查日期连续性
    if '日期' in df.columns:
        try:
            df_sorted = df.sort_values('日期')
            date_diff = df_sorted['日期'].diff().dt.days
            # 检查是否有超过7天的间隔（可能是节假日）
            large_gaps = (date_diff > 7).sum()
            if large_gaps > 0:
                issues.append(f"日期间隔过大: {large_gaps}处")
                score -= 5
        except:
            pass

    return {
        'score': max(0, score),
        'issues': issues
    }


def print_summary_report(all_results):
    """打印汇总报告"""
    print("\n" + "=" * 80)
    print("📊 数据源可靠性测试汇总报告")
    print("=" * 80)

    for data_source, results in all_results.items():
        print(f"\n🔍 {data_source} 数据源:")
        print("-" * 40)

        total_tests = len(results)
        successful_tests = sum(1 for r in results.values() if r['status'] == '成功')
        failed_tests = total_tests - successful_tests

        print(f"总测试数: {total_tests}")
        print(f"成功数: {successful_tests}")
        print(f"失败数: {failed_tests}")
        print(f"成功率: {(successful_tests / total_tests * 100):.1f}%")

        if successful_tests > 0:
            avg_response_time = sum(
                r['response_time_ms'] for r in results.values() if r['status'] == '成功') / successful_tests
            avg_data_quality = sum(
                r['data_quality']['score'] for r in results.values() if r['status'] == '成功') / successful_tests
            print(f"平均响应时间: {avg_response_time:.0f}ms")
            print(f"平均数据质量: {avg_data_quality:.1f}/100")

        # 详细结果
        print("\n详细结果:")
        for stock_code, result in results.items():
            status_icon = "✅" if result['status'] == '成功' else "❌"
            print(f"  {status_icon} {stock_code}: {result['status']} - {result['data_count']}条数据")


def main():
    print("🚀 数据源可靠性测试")
    print("=" * 80)
    print(f"测试时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 创建数据获取器
    fetcher = KlineDataFetcher()

    # 测试股票列表
    test_stocks = [
        ("sz000498", "山东路桥"),
        ("sh000001", "上证指数"),
        ("sz399001", "深证成指"),
        ("sh600000", "浦发银行"),
        ("sz000001", "平安银行")
    ]

    all_results = {}

    # 测试新浪财经
    print("\n" + "=" * 80)
    print("🔍 测试新浪财经数据源")
    print("=" * 80)
    sina_results = test_single_data_source(
        fetcher,
        "新浪财经",
        fetcher.get_sina_kline_data,
        test_stocks,
        days=30
    )
    all_results["新浪财经"] = sina_results

    # 测试东方财富
    print("\n" + "=" * 80)
    print("🔍 测试东方财富数据源")
    print("=" * 80)
    eastmoney_results = test_single_data_source(
        fetcher,
        "东方财富",
        fetcher.get_eastmoney_kline_data,
        test_stocks,
        days=30
    )
    all_results["东方财富"] = eastmoney_results

    # 测试Yahoo Finance
    print("\n" + "=" * 80)
    print("🔍 测试Yahoo Finance数据源")
    print("=" * 80)
    yahoo_results = test_single_data_source(
        fetcher,
        "Yahoo Finance",
        fetcher.get_yahoo_kline_data,
        test_stocks,
        days=30
    )
    all_results["Yahoo Finance"] = yahoo_results

    # 打印汇总报告
    print_summary_report(all_results)

    # 推荐最佳数据源
    print("\n" + "=" * 80)
    print("🏆 数据源推荐")
    print("=" * 80)

    recommendations = []
    for data_source, results in all_results.items():
        total_tests = len(results)
        successful_tests = sum(1 for r in results.values() if r['status'] == '成功')
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        if successful_tests > 0:
            avg_response_time = sum(
                r['response_time_ms'] for r in results.values() if r['status'] == '成功') / successful_tests
            avg_data_quality = sum(
                r['data_quality']['score'] for r in results.values() if r['status'] == '成功') / successful_tests
        else:
            avg_response_time = 0
            avg_data_quality = 0

        recommendations.append({
            'data_source': data_source,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'avg_data_quality': avg_data_quality
        })

    # 按成功率排序
    recommendations.sort(key=lambda x: x['success_rate'], reverse=True)

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['data_source']}")
        print(f"   成功率: {rec['success_rate']:.1f}%")
        print(f"   平均响应时间: {rec['avg_response_time']:.0f}ms")
        print(f"   平均数据质量: {rec['avg_data_quality']:.1f}/100")
        print()

    print("💡 建议:")
    if recommendations[0]['success_rate'] > 80:
        print(f"✅ 推荐使用 {recommendations[0]['data_source']} 作为主要数据源")
    else:
        print("⚠️  建议使用 'auto' 模式，让程序自动选择最佳数据源")


if __name__ == "__main__":
    main()
