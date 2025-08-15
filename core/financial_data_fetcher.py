#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票财务数据获取工具 - 修复版本
修复了字段解析错误和单位转换问题
"""

import datetime
import json
import time
from typing import Dict, Optional

import requests


class FinancialDataFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

    def get_tencent_financial_data_fixed(self, stock_code: str) -> Optional[Dict]:
        """
        从腾讯财经获取财务数据 - 修复版本
        修复了字段解析错误和单位转换问题
        """
        try:
            # 腾讯财经财务数据API
            url = f"http://qt.gtimg.cn/q={stock_code}"

            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200 and response.text.strip():
                # 解析腾讯财经数据
                if f'v_{stock_code}=' in response.text:
                    data_part = response.text.split('="')[1].split('";')[0]
                    stock_data = data_part.split('~')

                    # 调试信息
                    print(f"腾讯财经原始数据长度: {len(stock_data)}")
                    if len(stock_data) > 45:
                        print(f"关键字段值:")
                        print(f"  股票名称: {stock_data[0]}")
                        print(f"  当前价格: {stock_data[2]}")
                        print(f"  换手率: {stock_data[37]}")
                        print(f"  总市值: {stock_data[40]}")
                        print(f"  流通市值: {stock_data[41]}")

                    def safe_float(value, default=0):
                        try:
                            return float(value) if value and value != '' else default
                        except (ValueError, TypeError):
                            return default

                    def safe_int(value, default=0):
                        try:
                            return int(float(value)) if value and value != '' else default
                        except (ValueError, TypeError):
                            return default

                    def format_market_cap(value):
                        """格式化市值显示"""
                        try:
                            val = float(value)
                            if val >= 100000000:  # 大于1亿
                                return f"{val / 100000000:.2f}亿"
                            elif val >= 10000:  # 大于1万
                                return f"{val / 10000:.2f}万"
                            else:
                                return f"{val:,.0f}"
                        except:
                            return "0"

                    def format_turnover_rate(value):
                        """格式化换手率"""
                        try:
                            val = float(value)
                            if 0 < val <= 100:  # 正常换手率范围
                                return f"{val:.2f}%"
                            else:
                                return "-"
                        except:
                            return "-"

                    financial_data = {
                        '股票代码': stock_code,
                        '股票名称': stock_data[1] if len(stock_data) > 1 else '',  # 修正：股票名称在字段[1]
                        '当前价格': safe_float(stock_data[3]),  # 修正：当前价格在字段[3]
                        '昨收价': safe_float(stock_data[4]),  # 修正：昨收价在字段[4]
                        '开盘价': safe_float(stock_data[5]),  # 修正：开盘价在字段[5]
                        '最高价': safe_float(stock_data[33]),
                        '最低价': safe_float(stock_data[34]),
                        '成交量': safe_int(stock_data[6]),  # 修正：成交量在字段[6]
                        '成交额': safe_float(stock_data[36]) * 10000,  # 转换为元
                        '换手率': f"{safe_float(stock_data[37]) / 10000:.2f}%" if safe_float(
                            stock_data[37]) > 0 else '-',  # 修正：换手率需要除以10000
                        '市盈率(动态)': safe_float(stock_data[38]) if safe_float(stock_data[38]) > 0 else "N/A",
                        '市净率': safe_float(stock_data[39]),
                        '总市值': f"{safe_float(stock_data[45]):.2f}亿" if safe_float(stock_data[45]) > 0 else "0",
                        # 修正：总市值在字段[45]，单位是亿元
                        '流通市值': f"{safe_float(stock_data[44]):.2f}亿" if safe_float(stock_data[44]) > 0 else "0",
                        # 修正：流通市值在字段[44]，单位是亿元
                        '涨跌额': safe_float(stock_data[31]),
                        '涨跌幅': f"{safe_float(stock_data[32]):.2f}%" if safe_float(stock_data[32]) != 0 else '-',
                        '数据来源': '腾讯财经',
                        '数据时间戳': datetime.datetime.now().isoformat()
                    }

                    return financial_data
            return None

        except Exception as e:
            print(f"获取腾讯财经财务数据失败: {e}")
            return None

    def get_sina_financial_data_fixed(self, stock_code: str) -> Optional[Dict]:
        """
        从新浪财经获取财务数据 - 修复版本
        修复了单位转换问题
        """
        try:
            # 更新headers，添加Referer
            sina_headers = self.headers.copy()
            sina_headers['Referer'] = 'http://finance.sina.com.cn'

            # 1. 获取实时行情数据
            realtime_url = f"http://hq.sinajs.cn/list={stock_code}"
            realtime_response = requests.get(realtime_url, headers=sina_headers, timeout=10)

            if realtime_response.status_code != 200:
                return None

            # 解析实时行情数据
            realtime_text = realtime_response.text
            if f'v_{stock_code}=' not in realtime_text and f'hq_str_{stock_code}=' not in realtime_text:
                return None

            # 提取数据部分
            if f'hq_str_{stock_code}=' in realtime_text:
                data_part = realtime_text.split('="')[1].split('";')[0]
                realtime_data = data_part.split(',')

                if len(realtime_data) < 32:
                    return None

                def safe_float(value, default=0):
                    try:
                        return float(value) if value and value != '' else default
                    except (ValueError, TypeError):
                        return default

                def safe_int(value, default=0):
                    try:
                        return int(float(value)) if value and value != '' else default
                    except (ValueError, TypeError):
                        return default

                def format_market_cap(value):
                    """格式化市值显示"""
                    try:
                        val = float(value)
                        if val >= 100000000:  # 大于1亿
                            return f"{val / 100000000:.2f}亿"
                        elif val >= 10000:  # 大于1万
                            return f"{val / 10000:.2f}万"
                        else:
                            return f"{val:,.0f}"
                    except:
                        return "0"

                current_price = safe_float(realtime_data[3])
                pre_close = safe_float(realtime_data[2])
                change = current_price - pre_close
                change_pct = (change / pre_close * 100) if pre_close > 0 else 0

                financial_data = {
                    '股票代码': stock_code,
                    '股票名称': realtime_data[0] if len(realtime_data) > 0 else '',
                    '当前价格': current_price,
                    '昨收价': pre_close,
                    '开盘价': safe_float(realtime_data[1]),
                    '最高价': safe_float(realtime_data[4]),
                    '最低价': safe_float(realtime_data[5]),
                    '成交量': safe_int(realtime_data[8]),
                    '成交额': safe_float(realtime_data[9]),
                    '涨跌额': change,
                    '涨跌幅': f"{change_pct:.2f}%",
                    '数据来源': '新浪财经',
                    '数据时间戳': datetime.datetime.now().isoformat()
                }

                # 2. 尝试获取财务指标数据（如果可用）
                try:
                    # 尝试使用新浪财经的财务数据API
                    finance_url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
                    finance_params = {
                        'page': 1,
                        'num': 1,
                        'sort': 'symbol',
                        'asc': 1,
                        'node': 'hs_a',
                        'symbol': stock_code
                    }

                    finance_response = requests.get(finance_url, params=finance_params, headers=sina_headers, timeout=5)

                    if finance_response.status_code == 200:
                        finance_data = finance_response.json()
                        if finance_data and len(finance_data) > 0:
                            stock_info = finance_data[0]

                            # 添加财务指标，修复单位问题
                            financial_data.update({
                                '市盈率(动态)': safe_float(stock_info.get('per', 0)) if safe_float(
                                    stock_info.get('per', 0)) > 0 else "N/A",
                                '市净率': safe_float(stock_info.get('pb', 0)),
                                '总市值': f"{safe_float(stock_info.get('mktcap', 0)) / 10000:.2f}亿" if safe_float(
                                    stock_info.get('mktcap', 0)) > 0 else "0",  # 修复：新浪财经总市值单位是万元，需要转换为亿元
                                '流通市值': f"{safe_float(stock_info.get('nmc', 0)) / 10000:.2f}亿" if safe_float(
                                    stock_info.get('nmc', 0)) > 0 else "0",  # 修复：新浪财经流通市值单位是万元，需要转换为亿元
                                '换手率': f"{safe_float(stock_info.get('turnoverratio', 0)):.2f}%"
                            })
                except Exception as e:
                    # 如果财务数据获取失败，继续使用实时行情数据
                    print(f"新浪财经财务指标获取失败，使用实时行情数据: {e}")

                return financial_data
                
            return None

        except Exception as e:
            print(f"获取新浪财经财务数据失败: {e}")
            return None

    def get_eastmoney_financial_data_fixed(self, stock_code: str) -> Optional[Dict]:
        """
        从东方财富获取财务数据 - 修复版本
        修复了价格字段获取问题
        """
        try:
            # 构建股票ID
            if stock_code.startswith('sz'):
                secid = f"0.{stock_code[2:]}"
            elif stock_code.startswith('sh'):
                secid = f"1.{stock_code[2:]}"
            else:
                print(f"❌ 不支持的股票代码格式: {stock_code}")
                return None

            # 东方财富财务数据API
            url = "http://push2.eastmoney.com/api/qt/stock/get"

            # 使用关键字段 - 根据东方财富APP数据调整，添加更多换手率相关字段
            fields = "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f85,f86,f127,f164,f116,f117,f164,f168,f169"

            params = {
                'secid': secid,
                'fields': fields,
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'fltt': '2',
                'invt': '2',
                'wbp2u': '|0|0|0|web'
            }

            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    stock_data = data['data']

                    def safe_float(value, default=0):
                        try:
                            return float(value) if value and value != '' else default
                        except (ValueError, TypeError):
                            return default

                    def format_market_cap(value):
                        """格式化市值显示"""
                        try:
                            val = float(value)
                            if val >= 100000000:  # 大于1亿
                                return f"{val / 100000000:.2f}亿"
                            elif val >= 10000:  # 大于1万
                                return f"{val / 10000:.2f}万"
                            else:
                                return f"{val:,.0f}"
                        except:
                            return "0"

                    financial_data = {
                        '股票代码': stock_code,
                        '股票名称': stock_data.get('f58', ''),
                        '当前价格': safe_float(stock_data.get('f44', 0)),
                        '昨收价': safe_float(stock_data.get('f48', 0)),
                        '开盘价': safe_float(stock_data.get('f47', 0)),
                        '最高价': safe_float(stock_data.get('f45', 0)),
                        '最低价': safe_float(stock_data.get('f46', 0)),
                        '成交量': safe_float(stock_data.get('f51', 0)),
                        '成交额': safe_float(stock_data.get('f52', 0)),
                        '换手率': f"{safe_float(stock_data.get('f168', 0)):.2f}%" if safe_float(
                            stock_data.get('f168', 0)) > 0 else '-',  # 修正：使用f168字段获取换手率
                        '市盈率(动态)': f"{safe_float(stock_data.get('f57', 0)):.2f}" if safe_float(
                            stock_data.get('f57', 0)) != 0 else "N/A",
                        '市净率': safe_float(stock_data.get('f127', 0)),
                        '总市值': format_market_cap(stock_data.get('f116', 0)),  # 使用f116字段获取总市值
                        '流通市值': format_market_cap(stock_data.get('f117', 0)),  # 使用f117字段获取流通市值
                        '涨跌额': safe_float(stock_data.get('f49', 0)),
                        '涨跌幅': f"{safe_float(stock_data.get('f50', 0)):.2f}%" if safe_float(
                            stock_data.get('f50', 0)) != 0 else '-',
                        '数据来源': '东方财富',
                        '数据时间戳': datetime.datetime.now().isoformat()
                    }

                    return financial_data
            return None

        except Exception as e:
            print(f"获取东方财富财务数据失败: {e}")
            return None

    def get_financial_data_fixed(self, stock_code: str, data_source: str = 'auto') -> Optional[Dict]:
        """
        获取财务数据 - 修复版本
        data_source: 'auto' - 自动选择, 'eastmoney' - 东方财富, 'sina' - 新浪财经, 'tencent' - 腾讯财经
        """
        print(f"正在获取 {stock_code} 的财务数据（修复版本）...")

        if data_source == 'auto':
            # 自动选择数据源
            sources = [
                ('东方财富', self.get_eastmoney_financial_data_fixed),
                ('新浪财经', self.get_sina_financial_data_fixed),
                ('腾讯财经', self.get_tencent_financial_data_fixed)
            ]

            for source_name, source_func in sources:
                print(f"尝试从 {source_name} 获取数据...")
                data = source_func(stock_code)
                if data is not None:
                    print(f"✅ 成功从 {source_name} 获取到数据")
                    return data
                else:
                    print(f"❌ 从 {source_name} 获取数据失败")
                    time.sleep(1)

            print("❌ 所有数据源都无法获取数据")
            return None

        elif data_source == 'eastmoney':
            return self.get_eastmoney_financial_data_fixed(stock_code)
        elif data_source == 'sina':
            return self.get_sina_financial_data_fixed(stock_code)
        elif data_source == 'tencent':
            return self.get_tencent_financial_data_fixed(stock_code)
        else:
            print(f"❌ 不支持的数据源: {data_source}")
            return None

    def save_to_json(self, data: Dict, stock_code: str, filename: str = None):
        """保存财务数据到JSON文件"""
        if filename is None:
            filename = f"{stock_code}_financial_data_fixed_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def print_financial_summary(self, data: Dict):
        """打印财务数据摘要"""
        print(f"📊 财务数据摘要:")
        print(f"  股票代码: {data.get('股票代码', 'N/A')}")
        print(f"  股票名称: {data.get('股票名称', 'N/A')}")
        print(f"  当前价格: {data.get('当前价格', 'N/A')}")
        print(f"  换手率: {data.get('换手率', 'N/A')}")
        print(f"  市盈率(动态): {data.get('市盈率(动态)', 'N/A')}")
        print(f"  市净率: {data.get('市净率', 'N/A')}")
        print(f"  总市值: {data.get('总市值', 'N/A')}")
        print(f"  流通市值: {data.get('流通市值', 'N/A')}")
        print(f"  成交量: {data.get('成交量', 'N/A')}")
        print(f"  成交额: {data.get('成交额', 'N/A')}")
        print(f"  涨跌幅: {data.get('涨跌幅', 'N/A')}")
        print(f"  数据来源: {data.get('数据来源', 'N/A')}")
