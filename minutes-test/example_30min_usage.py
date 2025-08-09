#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
30分钟分时数据使用示例
"""

import os
import sys

# 添加父目录的core模块路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from minute_data_fetcher import MinuteDataFetcher


def main():
    """30分钟分时数据使用示例"""
    fetcher = MinuteDataFetcher()

    # 示例1: 获取山东路桥的30分钟数据
    print("📈 示例1: 获取山东路桥(sz000498)的30分钟分时数据")
    print("=" * 60)

    stock_code = "sz000498"
    period = 30

    df = fetcher.get_minute_data(stock_code, period, 'auto')

    if df is not None and not df.empty:
        fetcher.print_summary(df, stock_code, period)

        # 保存数据
        fetcher.save_to_csv(df, stock_code, period)

        # 显示最近5条数据
        print(f"\n📊 最近5条数据:")
        print(df.tail(5)[['时间', '开盘价', '最高价', '最低价', '收盘价', '成交量']].to_string(index=False))

    print("\n" + "=" * 60)

    # 示例2: 获取不同周期的数据
    print("📈 示例2: 获取不同周期的分时数据")
    print("=" * 60)

    periods = [1, 5, 15, 30, 60]

    for p in periods:
        print(f"\n⏱️  获取 {p} 分钟数据...")
        df_p = fetcher.get_minute_data(stock_code, p, 'auto')

        if df_p is not None and not df_p.empty:
            print(f"✅ 成功获取 {len(df_p)} 条 {p} 分钟数据")
            latest = df_p.iloc[-1]
            print(f"   最新时间: {latest['时间']}")
            print(f"   最新价格: {latest['收盘价']:.2f}")
        else:
            print(f"❌ 获取 {p} 分钟数据失败")

    print("\n" + "=" * 60)

    # 示例3: 测试不同数据源
    print("📈 示例3: 测试不同数据源")
    print("=" * 60)

    sources = ['sina', 'eastmoney', 'tencent']

    for source in sources:
        print(f"\n📡 测试 {source} 数据源...")
        df_source = fetcher.get_minute_data(stock_code, period, source)

        if df_source is not None and not df_source.empty:
            print(f"✅ {source} 数据源成功，获取 {len(df_source)} 条数据")
        else:
            print(f"❌ {source} 数据源失败")

    print("\n" + "=" * 60)
    print("🎉 30分钟分时数据获取示例完成！")


if __name__ == "__main__":
    main()
