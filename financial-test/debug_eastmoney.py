#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试东方财富数据字段
"""

import requests


def debug_eastmoney_data(stock_code="sz000002"):
    """调试东方财富数据字段"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

    # 构建股票ID
    if stock_code.startswith('sz'):
        secid = f"0.{stock_code[2:]}"
    elif stock_code.startswith('sh'):
        secid = f"1.{stock_code[2:]}"
    else:
        print(f"❌ 不支持的股票代码格式: {stock_code}")
        return

    # 东方财富财务数据API
    url = "http://push2.eastmoney.com/api/qt/stock/get"

    # 使用更多字段来调试
    fields = "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f85,f86,f127,f164,f116,f117,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180"

    params = {
        'secid': secid,
        'fields': fields,
        'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
        'fltt': '2',
        'invt': '2',
        'wbp2u': '|0|0|0|web'
    }

    print(f"🔍 调试东方财富数据: {stock_code}")
    print(f"URL: {url}")
    print(f"secid: {secid}")
    print(f"fields: {fields}")
    print("-" * 60)

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            print(f"✅ 请求成功")
            data = response.json()

            if data.get('data'):
                stock_data = data['data']

                print(f"📊 东方财富数据字段分析:")
                print("-" * 60)

                # 打印所有字段
                for field_code, value in stock_data.items():
                    print(f"字段[{field_code}]: {value}")

                print("-" * 60)
                print("🔍 关键字段分析:")
                print(f"  当前价格[f44]: {stock_data.get('f44', 'N/A')}")
                print(f"  换手率[f43]: {stock_data.get('f43', 'N/A')}")
                print(f"  换手率[f164]: {stock_data.get('f164', 'N/A')}")
                print(f"  换手率[f168]: {stock_data.get('f168', 'N/A')}")
                print(f"  换手率[f169]: {stock_data.get('f169', 'N/A')}")
                print(f"  总市值[f116]: {stock_data.get('f116', 'N/A')}")
                print(f"  流通市值[f117]: {stock_data.get('f117', 'N/A')}")
                print(f"  市盈率[f57]: {stock_data.get('f57', 'N/A')}")

                # 寻找接近0.29的换手率值
                print("-" * 60)
                print("🔍 寻找接近0.29的换手率值:")
                for field_code, value in stock_data.items():
                    try:
                        val = float(value)
                        if 0.1 <= val <= 1.0:  # 在0.1-1.0范围内的值
                            print(f"  字段[{field_code}]: {value} (可能是换手率)")
                    except:
                        pass

            else:
                print("❌ 未获取到数据")
        else:
            print(f"❌ 请求失败: {response.status_code}")

    except Exception as e:
        print(f"❌ 请求异常: {e}")


if __name__ == "__main__":
    debug_eastmoney_data("sz000002")
