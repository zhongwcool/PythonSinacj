#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票K线数据获取工具 - 使用示例
"""

from kline_data_fetcher import KlineDataFetcher

def main():
    print("🚀 股票K线数据获取工具")
    print("=" * 40)
    
    # 创建数据获取器
    fetcher = KlineDataFetcher()
    
    # 获取sz000498的90日K线数据
    print("📈 正在获取sz000498的90日K线数据...")
    df = fetcher.get_kline_data("sz000498", days=90, data_source="auto")
    
    if df is not None and not df.empty:
        print(f"✅ 成功获取 {len(df)} 条数据")
        
        # 显示数据摘要
        fetcher.print_summary(df, "sz000498")
        
        # 保存数据
        fetcher.save_to_csv(df, "sz000498")
        fetcher.save_to_json(df, "sz000498")
        
        # 显示前3条数据
        print("\n📋 前3条数据:")
        print(df.head(3).to_string(index=False))
        
    else:
        print("❌ 获取数据失败")

if __name__ == "__main__":
    main() 