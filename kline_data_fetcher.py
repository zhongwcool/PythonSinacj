#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票历史K线数据获取工具
支持多种数据源获取90日K线数据
"""

import requests
import pandas as pd
import time
import datetime
import json
import os
from typing import List, Dict, Optional

class KlineDataFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
    
    def get_sina_kline_data(self, stock_code: str, days: int = 90) -> Optional[pd.DataFrame]:
        """
        从新浪财经获取K线数据
        注意：新浪财经的K线API需要特殊处理
        """
        try:
            # 新浪财经K线数据API
            # 格式：http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000498&scale=240&ma=5&datalen=90
            url = f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
            params = {
                'symbol': stock_code,
                'scale': 240,  # 日K线
                'ma': 5,       # 5日均线
                'datalen': days
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    # 动态处理列名，因为新浪API返回的列数可能不同
                    df = pd.DataFrame(data)
                    
                    # 根据实际列数动态设置列名
                    if len(df.columns) == 6:
                        df.columns = ['日期', '开盘价', '最高价', '最低价', '收盘价', '成交量']
                    elif len(df.columns) == 8:
                        df.columns = ['日期', '开盘价', '最高价', '最低价', '收盘价', '成交量', '成交额', '换手率']
                    else:
                        # 如果列数不匹配，使用通用列名
                        df.columns = [f'col_{i}' for i in range(len(df.columns))]
                        # 只保留前6列作为标准K线数据
                        df = df.iloc[:, :6]
                        df.columns = ['日期', '开盘价', '最高价', '最低价', '收盘价', '成交量']
                    
                    # 转换数据类型
                    for col in ['开盘价', '最高价', '最低价', '收盘价', '成交量']:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # 按日期排序
                    df['日期'] = pd.to_datetime(df['日期'])
                    df = df.sort_values('日期')
                    
                    # 只保留最近90天的数据
                    df = df.tail(days)
                    
                    return df
            return None
            
        except Exception as e:
            print(f"获取新浪K线数据失败: {e}")
            return None
    
    def get_eastmoney_kline_data(self, stock_code: str, days: int = 90) -> Optional[pd.DataFrame]:
        """
        从东方财富获取K线数据（备用方案）
        """
        try:
            # 东方财富K线数据API
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                'secid': f'0.{stock_code[2:]}' if stock_code.startswith('sz') else f'1.{stock_code[2:]}',
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': 101,  # 日K线
                'fqt': 0,    # 不复权
                'beg': 0,
                'end': 20500101,
                'smplmt': days,
                'lmt': days
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
                            '日期': parts[0],
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
                    df['日期'] = pd.to_datetime(df['日期'])
                    df = df.sort_values('日期')
                    
                    return df
            return None
            
        except Exception as e:
            print(f"获取东方财富K线数据失败: {e}")
            return None
    
    def get_yahoo_kline_data(self, stock_code: str, days: int = 90) -> Optional[pd.DataFrame]:
        """
        从Yahoo Finance获取K线数据（国际股票）
        """
        try:
            # 转换股票代码格式
            if stock_code.startswith('sz'):
                yahoo_code = f"{stock_code[2:]}.SZ"
            elif stock_code.startswith('sh'):
                yahoo_code = f"{stock_code[2:]}.SS"
            else:
                yahoo_code = stock_code
            
            # 计算日期范围
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=days + 30)  # 多取30天确保有足够数据
            
            url = "https://query1.finance.yahoo.com/v8/finance/chart/" + yahoo_code
            params = {
                'period1': int(start_date.timestamp()),
                'period2': int(end_date.timestamp()),
                'interval': '1d',
                'events': 'history'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('chart') and data['chart'].get('result'):
                    result = data['chart']['result'][0]
                    timestamps = result['timestamp']
                    quotes = result['indicators']['quote'][0]
                    
                    rows = []
                    for i, timestamp in enumerate(timestamps):
                        rows.append({
                            '日期': datetime.datetime.fromtimestamp(timestamp),
                            '开盘价': quotes['open'][i] if quotes['open'][i] else None,
                            '最高价': quotes['high'][i] if quotes['high'][i] else None,
                            '最低价': quotes['low'][i] if quotes['low'][i] else None,
                            '收盘价': quotes['close'][i] if quotes['close'][i] else None,
                            '成交量': quotes['volume'][i] if quotes['volume'][i] else None
                        })
                    
                    df = pd.DataFrame(rows)
                    df = df.dropna()  # 删除空值
                    df = df.tail(days)  # 只保留最近90天
                    
                    return df
            return None
            
        except Exception as e:
            print(f"获取Yahoo Finance K线数据失败: {e}")
            return None
    
    def get_kline_data(self, stock_code: str, days: int = 90, data_source: str = 'auto') -> Optional[pd.DataFrame]:
        """
        获取K线数据的主函数
        data_source: 'sina', 'eastmoney', 'yahoo', 'auto'
        """
        print(f"正在获取 {stock_code} 的 {days} 日K线数据...")
        
        if data_source == 'auto':
            # 自动选择数据源
            sources = [
                ('新浪财经', self.get_sina_kline_data),
                ('东方财富', self.get_eastmoney_kline_data),
                ('Yahoo Finance', self.get_yahoo_kline_data)
            ]
            
            for source_name, source_func in sources:
                print(f"尝试从 {source_name} 获取数据...")
                df = source_func(stock_code, days)
                if df is not None and not df.empty:
                    print(f"✅ 成功从 {source_name} 获取到 {len(df)} 条数据")
                    return df
                else:
                    print(f"❌ 从 {source_name} 获取数据失败")
                    time.sleep(1)  # 避免请求过于频繁
            
            print("❌ 所有数据源都无法获取数据")
            return None
            
        elif data_source == 'sina':
            return self.get_sina_kline_data(stock_code, days)
        elif data_source == 'eastmoney':
            return self.get_eastmoney_kline_data(stock_code, days)
        elif data_source == 'yahoo':
            return self.get_yahoo_kline_data(stock_code, days)
        else:
            print(f"❌ 不支持的数据源: {data_source}")
            return None
    
    def save_to_csv(self, df: pd.DataFrame, stock_code: str, filename: str = None):
        """保存数据到CSV文件"""
        if filename is None:
            filename = f"{stock_code}_kline_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ 数据已保存到: {filename}")
    
    def save_to_json(self, df: pd.DataFrame, stock_code: str, filename: str = None):
        """保存数据到JSON文件"""
        if filename is None:
            filename = f"{stock_code}_kline_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 转换日期格式
        df_copy = df.copy()
        df_copy['日期'] = df_copy['日期'].dt.strftime('%Y-%m-%d')
        
        data = {
            'stock_code': stock_code,
            'data_count': len(df),
            'fetch_time': datetime.datetime.now().isoformat(),
            'kline_data': df_copy.to_dict('records')
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据已保存到: {filename}")
    
    def print_summary(self, df: pd.DataFrame, stock_code: str):
        """打印数据摘要"""
        if df is None or df.empty:
            print("❌ 没有数据可显示")
            return
        
        print("\n" + "="*60)
        print(f"📊 {stock_code} K线数据摘要")
        print("="*60)
        print(f"数据条数: {len(df)}")
        print(f"日期范围: {df['日期'].min().strftime('%Y-%m-%d')} 至 {df['日期'].max().strftime('%Y-%m-%d')}")
        print()
        
        # 最新数据
        latest = df.iloc[-1]
        print("📈 最新交易日数据:")
        print(f"  日期: {latest['日期'].strftime('%Y-%m-%d')}")
        print(f"  开盘价: {latest['开盘价']:.2f}")
        print(f"  最高价: {latest['最高价']:.2f}")
        print(f"  最低价: {latest['最低价']:.2f}")
        print(f"  收盘价: {latest['收盘价']:.2f}")
        print(f"  成交量: {latest['成交量']:,.0f}")
        print()
        
        # 统计信息
        print("📊 统计信息:")
        print(f"  最高价: {df['最高价'].max():.2f}")
        print(f"  最低价: {df['最低价'].min():.2f}")
        print(f"  平均成交量: {df['成交量'].mean():,.0f}")
        print(f"  总成交量: {df['成交量'].sum():,.0f}")
        
        # 涨跌幅统计
        if '涨跌幅' in df.columns:
            up_days = len(df[df['涨跌幅'] > 0])
            down_days = len(df[df['涨跌幅'] < 0])
            flat_days = len(df[df['涨跌幅'] == 0])
            print(f"  上涨天数: {up_days}")
            print(f"  下跌天数: {down_days}")
            print(f"  平盘天数: {flat_days}")

def main():
    # 配置参数
    stock_code = "sz000498"  # 股票代码
    days = 90                # 获取天数
    data_source = "auto"     # 数据源: auto, sina, eastmoney, yahoo
    
    # 创建数据获取器
    fetcher = KlineDataFetcher()
    
    # 获取数据
    df = fetcher.get_kline_data(stock_code, days, data_source)
    
    if df is not None and not df.empty:
        # 显示摘要
        fetcher.print_summary(df, stock_code)
        
        # 保存数据
        fetcher.save_to_csv(df, stock_code)
        fetcher.save_to_json(df, stock_code)
        
        # 显示前5条数据
        print("\n📋 前5条数据:")
        print(df.head().to_string(index=False))
        
    else:
        print("❌ 无法获取K线数据")

if __name__ == "__main__":
    main() 