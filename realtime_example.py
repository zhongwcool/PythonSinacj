#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分时数据获取工具使用示例
"""

from realtime_data_fetcher import RealtimeDataFetcher
import time

def main():
    print("🚀 分时数据获取工具")
    print("=" * 50)
    
    # 创建数据获取器
    fetcher = RealtimeDataFetcher()
    
    # 测试股票列表
    test_stocks = [
        ("sz000498", "山东路桥"),
        ("sh000001", "上证指数"),
        ("sh600000", "浦发银行")
    ]
    
    # 1. 获取实时数据
    print("\n📈 获取实时数据...")
    for stock_code, stock_name in test_stocks:
        print(f"\n正在获取 {stock_name}({stock_code}) 的实时数据...")
        
        realtime_data = fetcher.get_realtime_data(stock_code, 'realtime')
        
        if realtime_data:
            print(f"✅ 成功获取 {stock_name} 实时数据")
            print(f"   当前价格: {realtime_data['当前价格']:.2f}")
            print(f"   涨跌幅: {realtime_data['涨跌幅']:+.2f}%")
            print(f"   成交量: {realtime_data['成交量']:,.0f}")
            
            # 保存数据
            fetcher.save_to_json(realtime_data, stock_code)
        else:
            print(f"❌ 获取 {stock_name} 实时数据失败")
        
        time.sleep(1)  # 避免请求过于频繁
    
    print("\n" + "=" * 50)
    
    # 2. 获取分钟数据
    print("📊 获取分钟数据...")
    for stock_code, stock_name in test_stocks:
        print(f"\n正在获取 {stock_name}({stock_code}) 的分钟数据...")
        
        minute_df = fetcher.get_minute_data(stock_code, days=1, data_source='auto')
        
        if minute_df is not None and not minute_df.empty:
            print(f"✅ 成功获取 {stock_name} 分钟数据 - {len(minute_df)} 条")
            
            # 显示摘要
            fetcher.print_minute_summary(minute_df, stock_code)
            
            # 保存数据
            fetcher.save_to_csv(minute_df, stock_code)
            
            # 显示前3条数据
            print("\n📋 前3条数据:")
            print(minute_df.head(3).to_string(index=False))
            
        else:
            print(f"❌ 获取 {stock_name} 分钟数据失败")
        
        time.sleep(2)  # 避免请求过于频繁
    
    print("\n" + "=" * 50)
    print("🎉 分时数据获取完成！")

def demo_realtime_monitoring():
    """演示实时监控功能"""
    print("\n🔍 实时监控演示")
    print("=" * 50)
    
    fetcher = RealtimeDataFetcher()
    stock_code = "sz000498"
    
    print(f"开始监控 {stock_code} 的实时数据...")
    print("按 Ctrl+C 停止监控")
    print()
    
    try:
        for i in range(5):  # 监控5次
            realtime_data = fetcher.get_realtime_data(stock_code, 'realtime')
            
            if realtime_data:
                print(f"[{i+1}] {realtime_data['更新时间']} - 价格: {realtime_data['当前价格']:.2f} ({realtime_data['涨跌幅']:+.2f}%)")
            else:
                print(f"[{i+1}] 获取数据失败")
            
            time.sleep(3)  # 每3秒更新一次
            
    except KeyboardInterrupt:
        print("\n⏹️  监控已停止")

if __name__ == "__main__":
    # 运行基本示例
    main()
    
    # 运行实时监控演示
    demo_realtime_monitoring() 