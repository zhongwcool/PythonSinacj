#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有财务数据源
对比不同数据源的数据质量和可用性
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.financial_data_fetcher import FinancialDataFetcher
import time
import json


def test_all_sources():
    """测试所有数据源"""

    # 测试股票列表
    test_stocks = [
        "sz000498",  # 山东路桥
        "sh600000",  # 浦发银行
        "sz000001",  # 平安银行
        "sh600036",  # 招商银行
        "sz000002"  # 万科A
    ]

    # 数据源列表
    sources = [
        ('东方财富', 'eastmoney'),
        ('新浪财经', 'sina'),
        ('腾讯财经', 'tencent')
    ]

    fetcher = FinancialDataFetcher()

    print("🚀 开始测试所有财务数据源...")
    print("=" * 80)

    for stock_code in test_stocks:
        print(f"\n📊 测试股票: {stock_code}")
        print("-" * 60)

        results = {}

        for source_name, source_code in sources:
            print(f"\n🔍 测试 {source_name}...")

            try:
                start_time = time.time()
                data = fetcher.get_financial_data(stock_code, data_source=source_code)
                end_time = time.time()

                if data:
                    response_time = end_time - start_time
                    print(f"✅ {source_name} 成功 - 响应时间: {response_time:.3f}秒")

                    # 提取关键指标
                    key_metrics = {
                        '股票名称': data.get('股票名称', 'N/A'),
                        '当前价格': data.get('当前价格', 'N/A'),
                        '换手率': data.get('换手率', 'N/A'),
                        '市盈率(动态)': data.get('市盈率(动态)', 'N/A'),
                        '市净率': data.get('市净率', 'N/A'),
                        '总市值': data.get('总市值', 'N/A'),
                        '流通市值': data.get('流通市值', 'N/A'),
                        '成交量': data.get('成交量', 'N/A'),
                        '成交额': data.get('成交额', 'N/A'),
                        '涨跌幅': data.get('涨跌幅', 'N/A'),
                        '响应时间': f"{response_time:.3f}秒",
                        '数据字段数': len(data)
                    }

                    results[source_name] = key_metrics

                    # 打印关键指标
                    print(f"  股票名称: {key_metrics['股票名称']}")
                    print(f"  当前价格: {key_metrics['当前价格']}")
                    print(f"  换手率: {key_metrics['换手率']}")
                    print(f"  市盈率: {key_metrics['市盈率(动态)']}")
                    print(f"  市净率: {key_metrics['市净率']}")
                    print(f"  总市值: {key_metrics['总市值']}")
                    print(f"  数据字段数: {key_metrics['数据字段数']}")

                else:
                    print(f"❌ {source_name} 失败")
                    results[source_name] = None

            except Exception as e:
                print(f"❌ {source_name} 异常: {e}")
                results[source_name] = None

            time.sleep(1)  # 避免请求过于频繁

        # 保存结果
        filename = f"{stock_code}_all_sources_test_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n💾 结果已保存到: {filename}")

        # 对比分析
        print("\n📊 数据源对比分析:")
        print("-" * 40)

        successful_sources = [name for name, data in results.items() if data is not None]
        if len(successful_sources) > 1:
            print(f"✅ 成功获取数据的数据源: {', '.join(successful_sources)}")

            # 对比价格数据
            prices = {}
            for source_name, data in results.items():
                if data and data.get('当前价格') != 'N/A':
                    try:
                        prices[source_name] = float(str(data['当前价格']).replace('元', ''))
                    except:
                        pass

            if len(prices) > 1:
                print(f"💰 价格对比:")
                for source, price in prices.items():
                    print(f"  {source}: {price:.2f}元")

                # 计算价格差异
                price_values = list(prices.values())
                max_price = max(price_values)
                min_price = min(price_values)
                price_diff = max_price - min_price
                price_diff_pct = (price_diff / min_price) * 100 if min_price > 0 else 0

                print(f"  价格差异: {price_diff:.2f}元 ({price_diff_pct:.2f}%)")
        else:
            print("❌ 只有一个数据源成功获取数据，无法进行对比")

        print("\n" + "=" * 80)


def test_single_stock_detailed(stock_code="sz000498"):
    """详细测试单个股票的所有数据源"""

    print(f"🔍 详细测试股票: {stock_code}")
    print("=" * 80)

    fetcher = FinancialDataFetcher()

    # 测试东方财富数据源（最全面）
    print("\n📊 东方财富数据源详细数据:")
    print("-" * 60)

    eastmoney_data = fetcher.get_financial_data(stock_code, data_source='eastmoney')
    if eastmoney_data:
        fetcher.print_financial_summary(eastmoney_data)

        # 保存详细数据
        filename = f"{stock_code}_eastmoney_detailed_{time.strftime('%Y%m%d_%H%M%S')}.json"
        fetcher.save_to_json(eastmoney_data, stock_code, filename)
    else:
        print("❌ 东方财富数据获取失败")

    # 测试腾讯财经数据源
    print("\n📊 腾讯财经数据源详细数据:")
    print("-" * 60)

    tencent_data = fetcher.get_financial_data(stock_code, data_source='tencent')
    if tencent_data:
        fetcher.print_financial_summary(tencent_data)

        # 保存详细数据
        filename = f"{stock_code}_tencent_detailed_{time.strftime('%Y%m%d_%H%M%S')}.json"
        fetcher.save_to_json(tencent_data, stock_code, filename)
    else:
        print("❌ 腾讯财经数据获取失败")

    # 测试新浪财经数据源
    print("\n📊 新浪财经数据源详细数据:")
    print("-" * 60)

    sina_data = fetcher.get_financial_data(stock_code, data_source='sina')
    if sina_data:
        fetcher.print_financial_summary(sina_data)

        # 保存详细数据
        filename = f"{stock_code}_sina_detailed_{time.strftime('%Y%m%d_%H%M%S')}.json"
        fetcher.save_to_json(sina_data, stock_code, filename)
    else:
        print("❌ 新浪财经数据获取失败")


def main():
    """主函数"""
    print("🎯 财务数据源测试工具")
    print("=" * 80)

    while True:
        print("\n请选择测试模式:")
        print("1. 测试所有数据源（多股票对比）")
        print("2. 详细测试单个股票")
        print("3. 退出")

        choice = input("\n请输入选择 (1-3): ").strip()

        if choice == '1':
            test_all_sources()
        elif choice == '2':
            stock_code = input("请输入股票代码 (默认: sz000498): ").strip()
            if not stock_code:
                stock_code = "sz000498"
            test_single_stock_detailed(stock_code)
        elif choice == '3':
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重新输入")


if __name__ == "__main__":
    main()
