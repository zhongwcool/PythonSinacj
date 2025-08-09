#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
30分钟分时数据获取工具
支持多个数据源获取分钟级K线数据
"""

import datetime
import json
import os
import time
from typing import Optional

import pandas as pd
import requests


class MinuteDataFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
    
    def get_sina_minute_data(self, stock_code: str, period: int = 30) -> Optional[pd.DataFrame]:
        """
        从新浪财经获取分钟级数据
        period: 分钟周期，支持1, 5, 15, 30, 60分钟
        """
        try:
            # 新浪财经分钟数据API
            # 格式：http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000498&scale=30&ma=5&datalen=1023
            url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
            params = {
                'symbol': stock_code,
                'scale': period,  # 分钟周期
                'ma': 5,          # 5日均线
                'datalen': 1023   # 最大数据长度
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
                    
                    # 处理时间格式
                    df['时间'] = pd.to_datetime(df['时间'])
                    df = df.sort_values('时间')
                    
                    return df
            return None
            
        except Exception as e:
            print(f"获取新浪分钟数据失败: {e}")
            return None
    
    def get_eastmoney_minute_data(self, stock_code: str, period: int = 30) -> Optional[pd.DataFrame]:
        """
        从东方财富获取分钟级数据
        period: 分钟周期，支持1, 5, 15, 30, 60分钟
        """
        try:
            # 东方财富分钟数据API
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            
            # 根据分钟周期设置klt参数
            klt_map = {1: 1, 5: 5, 15: 15, 30: 30, 60: 60}
            klt = klt_map.get(period, 30)
            
            params = {
                'secid': f'0.{stock_code[2:]}' if stock_code.startswith('sz') else f'1.{stock_code[2:]}',
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'klt': klt,      # 分钟周期
                'fqt': 0,        # 不复权
                'beg': 0,
                'end': 20500101,
                'smplmt': 1023,
                'lmt': 1023
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
    
    def get_tencent_minute_data(self, stock_code: str, period: int = 30) -> Optional[pd.DataFrame]:
        """
        从腾讯财经获取分钟级数据
        period: 分钟周期，支持1, 5, 15, 30, 60分钟
        """
        try:
            # 腾讯财经分钟数据API
            url = "http://ifzq.gtimg.cn/appstock/app/kline/mkline"
            
            # 根据分钟周期设置kline_type参数
            kline_type_map = {1: 'm1', 5: 'm5', 15: 'm15', 30: 'm30', 60: 'm60'}
            kline_type = kline_type_map.get(period, 'm30')
            
            params = {
                'param': f'{stock_code},{kline_type},,1023,qfq',
                '_': int(time.time() * 1000)
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and data['data'].get(stock_code):
                    stock_data = data['data'][stock_code]
                    if stock_data.get(kline_type):
                        klines = stock_data[kline_type]
                        rows = []
                        for line in klines:
                            rows.append({
                                '时间': line[0],
                                '开盘价': float(line[1]),
                                '收盘价': float(line[2]),
                                '最高价': float(line[3]),
                                '最低价': float(line[4]),
                                '成交量': float(line[5])
                            })
                        
                        df = pd.DataFrame(rows)
                        df['时间'] = pd.to_datetime(df['时间'])
                        df = df.sort_values('时间')
                        
                        return df
            return None
            
        except Exception as e:
            print(f"获取腾讯财经分钟数据失败: {e}")
            return None
    
    def get_minute_data(self, stock_code: str, period: int = 30, data_source: str = 'auto') -> Optional[pd.DataFrame]:
        """
        获取分钟级数据的主函数
        period: 分钟周期，支持1, 5, 15, 30, 60分钟
        data_source: 'sina', 'eastmoney', 'tencent', 'auto'
        """
        print(f"正在获取 {stock_code} 的 {period} 分钟分时数据...")
        
        if data_source == 'auto':
            # 自动选择数据源
            sources = [
                ('新浪财经', self.get_sina_minute_data),
                ('东方财富', self.get_eastmoney_minute_data),
                ('腾讯财经', self.get_tencent_minute_data)
            ]
            
            for source_name, source_func in sources:
                print(f"尝试从 {source_name} 获取数据...")
                df = source_func(stock_code, period)
                if df is not None and not df.empty:
                    print(f"✅ 成功从 {source_name} 获取到 {len(df)} 条数据")
                    return df
                else:
                    print(f"❌ 从 {source_name} 获取数据失败")
            
            print("❌ 所有数据源都获取失败")
            return None
        
        elif data_source == 'sina':
            return self.get_sina_minute_data(stock_code, period)
        elif data_source == 'eastmoney':
            return self.get_eastmoney_minute_data(stock_code, period)
        elif data_source == 'tencent':
            return self.get_tencent_minute_data(stock_code, period)
        else:
            print(f"❌ 不支持的数据源: {data_source}")
            return None
    
    def save_to_csv(self, df: pd.DataFrame, stock_code: str, period: int, filename: str = None):
        """保存数据到CSV文件"""
        # 获取调用脚本所在目录的outputs子目录
        import inspect
        caller_frame = inspect.currentframe().f_back
        if caller_frame:
            caller_file = caller_frame.f_globals.get('__file__')
            if caller_file:
                script_dir = os.path.dirname(os.path.abspath(caller_file))
                output_dir = os.path.join(script_dir, "outputs")
            else:
                # 如果无法获取调用者文件路径，则使用当前工作目录
                output_dir = os.path.join(os.getcwd(), "outputs")
        else:
            # 如果无法获取调用者信息，则使用当前工作目录
            output_dir = os.path.join(os.getcwd(), "outputs")

        # 确保outputs目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{stock_code}_{period}min_data_{timestamp}.csv"

        # 将文件保存到outputs目录
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"✅ 数据已保存到: {filepath}")
    
    def save_to_json(self, df: pd.DataFrame, stock_code: str, period: int, filename: str = None):
        """保存数据到JSON文件"""
        # 获取调用脚本所在目录的outputs子目录
        import inspect
        caller_frame = inspect.currentframe().f_back
        if caller_frame:
            caller_file = caller_frame.f_globals.get('__file__')
            if caller_file:
                script_dir = os.path.dirname(os.path.abspath(caller_file))
                output_dir = os.path.join(script_dir, "outputs")
            else:
                # 如果无法获取调用者文件路径，则使用当前工作目录
                output_dir = os.path.join(os.getcwd(), "outputs")
        else:
            # 如果无法获取调用者信息，则使用当前工作目录
            output_dir = os.path.join(os.getcwd(), "outputs")

        # 确保outputs目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{stock_code}_{period}min_data_{timestamp}.json"
        
        # 转换时间格式为字符串
        df_copy = df.copy()
        df_copy['时间'] = df_copy['时间'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        data = {
            '股票代码': stock_code,
            '分钟周期': period,
            '数据条数': len(df),
            '获取时间': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '数据': df_copy.to_dict('records')
        }

        # 将文件保存到outputs目录
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ 数据已保存到: {filepath}")
    
    def print_summary(self, df: pd.DataFrame, stock_code: str, period: int):
        """打印数据摘要"""
        if df is None or df.empty:
            print("❌ 没有数据可显示")
            return
        
        print(f"\n📊 {stock_code} {period}分钟分时数据摘要")
        print("=" * 60)
        print(f"数据条数: {len(df)}")
        print(f"时间范围: {df['时间'].min()} 到 {df['时间'].max()}")
        print(f"最新时间: {df['时间'].max()}")
        
        # 最新数据
        latest = df.iloc[-1]
        print(f"\n📈 最新数据:")
        print(f"  时间: {latest['时间']}")
        print(f"  开盘价: {latest['开盘价']:.2f}")
        print(f"  最高价: {latest['最高价']:.2f}")
        print(f"  最低价: {latest['最低价']:.2f}")
        print(f"  收盘价: {latest['收盘价']:.2f}")
        print(f"  成交量: {latest['成交量']:,.0f}")
        
        # 统计信息
        print(f"\n📊 统计信息:")
        print(f"  最高价: {df['最高价'].max():.2f}")
        print(f"  最低价: {df['最低价'].min():.2f}")
        print(f"  平均成交量: {df['成交量'].mean():,.0f}")
        print(f"  总成交量: {df['成交量'].sum():,.0f}")
        
        # 涨跌幅计算
        if len(df) > 1:
            first_price = df.iloc[0]['收盘价']
            last_price = df.iloc[-1]['收盘价']
            change = last_price - first_price
            change_pct = (change / first_price) * 100
            print(f"  期间涨跌: {change:+.2f} ({change_pct:+.2f}%)")

def main():
    """主函数 - 测试30分钟分时数据获取"""
    fetcher = MinuteDataFetcher()
    
    # 配置参数
    stock_code = "sz000498"  # 山东路桥
    period = 30              # 30分钟周期
    
    print("🚀 开始获取30分钟分时数据...")
    print(f"📈 股票代码: {stock_code}")
    print(f"⏱️  分钟周期: {period}分钟")
    print("=" * 60)
    
    # 获取数据
    df = fetcher.get_minute_data(stock_code, period, 'auto')
    
    if df is not None and not df.empty:
        # 打印摘要
        fetcher.print_summary(df, stock_code, period)
        
        # 保存数据
        fetcher.save_to_csv(df, stock_code, period)
        fetcher.save_to_json(df, stock_code, period)
        
        print(f"\n✅ 数据获取完成！共获取 {len(df)} 条记录")
    else:
        print("❌ 数据获取失败")

if __name__ == "__main__":
    main()
