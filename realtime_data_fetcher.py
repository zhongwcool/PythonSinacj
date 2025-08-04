#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分时数据获取工具
支持实时分时数据、历史分时数据获取
"""

import requests
import pandas as pd
import time
import datetime
import json
import os
from typing import List, Dict, Optional

class RealtimeDataFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
    
    def get_sina_realtime_data(self, stock_code: str) -> Optional[Dict]:
        """
        从新浪财经获取实时分时数据
        """
        try:
            # 新浪财经实时数据API
            url = f"http://hq.sinajs.cn/list={stock_code}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200 and response.text.strip():
                # 解析新浪财经实时数据
                if f'var hq_str_{stock_code}=' in response.text:
                    data_part = response.text.split('="')[1].split('";')[0]
                    stock_data = data_part.split(',')
                    
                    # 新浪财经实时数据格式解析
                    # 0:股票名称, 1:今日开盘价, 2:昨日收盘价, 3:当前价格, 4:今日最高价, 5:今日最低价
                    # 6:竞买价, 7:竞卖价, 8:成交股数, 9:成交金额
                    # 10:买一量, 11:买一价, 12:买二量, 13:买二价, 14:买三量, 15:买三价, 16:买四量, 17:买四价, 18:买五量, 19:买五价
                    # 20:卖一量, 21:卖一价, 22:卖二量, 23:卖二价, 24:卖三量, 25:卖三价, 26:卖四量, 27:卖四价, 28:卖五量, 29:卖五价
                    # 30:日期, 31:时间
                    
                    current_price = float(stock_data[3]) if stock_data[3] != '' else 0
                    yesterday_close = float(stock_data[2]) if stock_data[2] != '' else 0
                    
                    # 计算涨跌额和涨跌幅
                    change_amount = current_price - yesterday_close
                    change_percent = (change_amount / yesterday_close * 100) if yesterday_close != 0 else 0
                    
                    realtime_data = {
                        '股票代码': stock_code,
                        '股票名称': stock_data[0] if len(stock_data) > 0 else '',
                        '当前价格': current_price,
                        '涨跌额': change_amount,
                        '涨跌幅': change_percent,
                        '今日开盘': float(stock_data[1]) if len(stock_data) > 1 and stock_data[1] != '' else 0,
                        '昨日收盘': yesterday_close,
                        '今日最高': float(stock_data[4]) if len(stock_data) > 4 and stock_data[4] != '' else 0,
                        '今日最低': float(stock_data[5]) if len(stock_data) > 5 and stock_data[5] != '' else 0,
                        '成交量': int(stock_data[8]) if len(stock_data) > 8 and stock_data[8] != '' else 0,
                        '成交额': float(stock_data[9]) if len(stock_data) > 9 and stock_data[9] != '' else 0,
                        '买一价': float(stock_data[11]) if len(stock_data) > 11 and stock_data[11] != '' else 0,
                        '买一量': int(stock_data[10]) if len(stock_data) > 10 and stock_data[10] != '' else 0,
                        '卖一价': float(stock_data[21]) if len(stock_data) > 21 and stock_data[21] != '' else 0,
                        '卖一量': int(stock_data[20]) if len(stock_data) > 20 and stock_data[20] != '' else 0,
                        '更新时间': f"{stock_data[30]} {stock_data[31]}" if len(stock_data) > 31 else '',
                        '数据时间戳': datetime.datetime.now().isoformat()
                    }
                    
                    return realtime_data
            return None
            
        except Exception as e:
            print(f"获取新浪实时数据失败: {e}")
            return None
    
    def get_sina_minute_data(self, stock_code: str, days: int = 1) -> Optional[pd.DataFrame]:
        """
        从新浪财经获取分钟级分时数据
        """
        try:
            # 新浪财经分钟数据API
            url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
            params = {
                'symbol': stock_code,
                'scale': 1,  # 1分钟K线
                'ma': 5,     # 5日均线
                'datalen': days * 240  # 一天约240分钟
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    df = pd.DataFrame(data)
                    
                    # 根据实际列数动态设置列名
                    if len(df.columns) >= 6:
                        df.columns = ['时间', '开盘价', '最高价', '最低价', '收盘价', '成交量'] + list(df.columns[6:])
                    
                    # 转换数据类型
                    for col in ['开盘价', '最高价', '最低价', '收盘价', '成交量']:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # 转换时间格式
                    if '时间' in df.columns:
                        df['时间'] = pd.to_datetime(df['时间'])
                        df = df.sort_values('时间')
                    
                    return df
            return None
            
        except Exception as e:
            print(f"获取新浪分钟数据失败: {e}")
            return None
    
    def get_eastmoney_minute_data(self, stock_code: str, days: int = 1) -> Optional[pd.DataFrame]:
        """
        从东方财富获取分钟级分时数据
        """
        try:
            # 东方财富分钟数据API
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                'secid': f'0.{stock_code[2:]}' if stock_code.startswith('sz') else f'1.{stock_code[2:]}',
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': 1,    # 1分钟K线
                'fqt': 0,    # 不复权
                'beg': 0,
                'end': 20500101,
                'smplmt': days * 240,
                'lmt': days * 240
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and data['data'].get('klines'):
                    klines = data['data']['klines']
                    rows = []
                    for line in klines:
                        parts = line.split(',')
                        rows.append({
                            '时间': parts[0],
                            '开盘价': float(parts[1]),
                            '收盘价': float(parts[2]),
                            '最高价': float(parts[3]),
                            '最低价': float(parts[4]),
                            '成交量': float(parts[5]),
                            '成交额': float(parts[6]),
                            '振幅': float(parts[7]),
                            '涨跌幅': float(parts[8]),
                            '涨跌额': float(parts[9]),
                            '换手率': float(parts[10])
                        })
                    
                    df = pd.DataFrame(rows)
                    df['时间'] = pd.to_datetime(df['时间'])
                    df = df.sort_values('时间')
                    
                    return df
            return None
            
        except Exception as e:
            print(f"获取东方财富分钟数据失败: {e}")
            return None
    
    def get_realtime_data(self, stock_code: str, data_type: str = 'realtime') -> Optional[Dict]:
        """
        获取实时数据
        data_type: 'realtime' - 实时价格, 'minute' - 分钟数据
        """
        if data_type == 'realtime':
            return self.get_sina_realtime_data(stock_code)
        else:
            print("不支持的数据类型")
            return None
    
    def get_minute_data(self, stock_code: str, days: int = 1, data_source: str = 'auto') -> Optional[pd.DataFrame]:
        """
        获取分钟级分时数据
        """
        print(f"正在获取 {stock_code} 的 {days} 天分钟数据...")
        
        if data_source == 'auto':
            # 自动选择数据源
            sources = [
                ('新浪财经', self.get_sina_minute_data),
                ('东方财富', self.get_eastmoney_minute_data)
            ]
            
            for source_name, source_func in sources:
                print(f"尝试从 {source_name} 获取数据...")
                df = source_func(stock_code, days)
                if df is not None and not df.empty:
                    print(f"✅ 成功从 {source_name} 获取到 {len(df)} 条数据")
                    return df
                else:
                    print(f"❌ 从 {source_name} 获取数据失败")
                    time.sleep(1)
            
            print("❌ 所有数据源都无法获取数据")
            return None
            
        elif data_source == 'sina':
            return self.get_sina_minute_data(stock_code, days)
        elif data_source == 'eastmoney':
            return self.get_eastmoney_minute_data(stock_code, days)
        else:
            print(f"❌ 不支持的数据源: {data_source}")
            return None
    
    def save_to_csv(self, df: pd.DataFrame, stock_code: str, filename: str = None):
        """保存数据到CSV文件"""
        if filename is None:
            filename = f"{stock_code}_minute_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ 数据已保存到: {filename}")
    
    def save_to_json(self, data: Dict, stock_code: str, filename: str = None):
        """保存实时数据到JSON文件"""
        if filename is None:
            filename = f"{stock_code}_realtime_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据已保存到: {filename}")
    
    def print_realtime_summary(self, data: Dict):
        """打印实时数据摘要"""
        if not data:
            print("❌ 没有数据可显示")
            return
        
        print("\n" + "="*60)
        print(f"📊 {data['股票代码']} 实时数据")
        print("="*60)
        print(f"股票名称: {data['股票名称']}")
        print(f"当前价格: {data['当前价格']:.2f}")
        print(f"涨跌额: {data['涨跌额']:+.3f}")
        print(f"涨跌幅: {data['涨跌幅']:+.2f}%")
        print(f"今日开盘: {data['今日开盘']:.2f}")
        print(f"昨日收盘: {data['昨日收盘']:.2f}")
        print(f"今日最高: {data['今日最高']:.2f}")
        print(f"今日最低: {data['今日最低']:.2f}")
        print(f"成交量: {data['成交量']:,.0f}")
        print(f"成交额: {data['成交额']:,.0f}")
        print(f"买一价: {data['买一价']:.2f} (量: {data['买一量']:,.0f})")
        print(f"卖一价: {data['卖一价']:.2f} (量: {data['卖一量']:,.0f})")
        print(f"更新时间: {data['更新时间']}")
    
    def print_minute_summary(self, df: pd.DataFrame, stock_code: str):
        """打印分钟数据摘要"""
        if df is None or df.empty:
            print("❌ 没有数据可显示")
            return
        
        print("\n" + "="*60)
        print(f"📊 {stock_code} 分钟数据摘要")
        print("="*60)
        print(f"数据条数: {len(df)}")
        print(f"时间范围: {df['时间'].min().strftime('%Y-%m-%d %H:%M')} 至 {df['时间'].max().strftime('%Y-%m-%d %H:%M')}")
        print()
        
        # 最新数据
        latest = df.iloc[-1]
        print("📈 最新数据:")
        print(f"  时间: {latest['时间'].strftime('%Y-%m-%d %H:%M')}")
        print(f"  开盘价: {latest['开盘价']:.2f}")
        print(f"  最高价: {latest['最高价']:.2f}")
        print(f"  最低价: {latest['最低价']:.2f}")
        print(f"  收盘价: {latest['收盘价']:.2f}")
        print(f"  成交量: {latest['成交量']:,.0f}")
        
        # 统计信息
        print("\n📊 统计信息:")
        print(f"  最高价: {df['最高价'].max():.2f}")
        print(f"  最低价: {df['最低价'].min():.2f}")
        print(f"  平均成交量: {df['成交量'].mean():,.0f}")
        print(f"  总成交量: {df['成交量'].sum():,.0f}")

def main():
    # 配置参数
    stock_code = "sz000498"  # 股票代码
    
    # 创建数据获取器
    fetcher = RealtimeDataFetcher()
    
    # 1. 获取实时数据
    print("🚀 获取实时数据...")
    realtime_data = fetcher.get_realtime_data(stock_code, 'realtime')
    
    if realtime_data:
        fetcher.print_realtime_summary(realtime_data)
        fetcher.save_to_json(realtime_data, stock_code)
    
    print("\n" + "="*60)
    
    # 2. 获取分钟数据
    print("🚀 获取分钟数据...")
    minute_df = fetcher.get_minute_data(stock_code, days=1, data_source='auto')
    
    if minute_df is not None and not minute_df.empty:
        fetcher.print_minute_summary(minute_df, stock_code)
        fetcher.save_to_csv(minute_df, stock_code)
        
        # 显示前5条数据
        print("\n📋 前5条数据:")
        print(minute_df.head().to_string(index=False))
        
    else:
        print("❌ 无法获取分钟数据")

if __name__ == "__main__":
    main() 