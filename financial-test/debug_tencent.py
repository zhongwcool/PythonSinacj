#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试腾讯财经数据格式
"""

import requests


def debug_tencent_data(stock_code="sz000002"):
    """调试腾讯财经数据格式"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

    url = f"http://qt.gtimg.cn/q={stock_code}"

    print(f"🔍 调试腾讯财经数据: {stock_code}")
    print(f"URL: {url}")
    print("-" * 60)

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            print(f"✅ 请求成功")
            print(f"原始响应: {response.text}")
            print("-" * 60)

            if f'v_{stock_code}=' in response.text:
                data_part = response.text.split('="')[1].split('";')[0]
                stock_data = data_part.split('~')

                print(f"数据字段数量: {len(stock_data)}")
                print("-" * 60)

                # 打印所有字段
                for i, field in enumerate(stock_data):
                    print(f"字段[{i}]: {field}")

                print("-" * 60)
                print("关键字段分析:")
                print(f"  股票名称[0]: {stock_data[0] if len(stock_data) > 0 else 'N/A'}")
                print(f"  股票代码[1]: {stock_data[1] if len(stock_data) > 1 else 'N/A'}")
                print(f"  当前价格[2]: {stock_data[2] if len(stock_data) > 2 else 'N/A'}")
                print(f"  昨收价[3]: {stock_data[3] if len(stock_data) > 3 else 'N/A'}")
                print(f"  开盘价[4]: {stock_data[4] if len(stock_data) > 4 else 'N/A'}")
                print(f"  成交量[5]: {stock_data[5] if len(stock_data) > 5 else 'N/A'}")
                print(f"  换手率[37]: {stock_data[37] if len(stock_data) > 37 else 'N/A'}")
                print(f"  市盈率[38]: {stock_data[38] if len(stock_data) > 38 else 'N/A'}")
                print(f"  市净率[39]: {stock_data[39] if len(stock_data) > 39 else 'N/A'}")
                print(f"  总市值[40]: {stock_data[40] if len(stock_data) > 40 else 'N/A'}")
                print(f"  流通市值[41]: {stock_data[41] if len(stock_data) > 41 else 'N/A'}")

            else:
                print("❌ 未找到预期的数据格式")
        else:
            print(f"❌ 请求失败: {response.status_code}")

    except Exception as e:
        print(f"❌ 请求异常: {e}")


if __name__ == "__main__":
    debug_tencent_data("sz000002")
    print("\n" + "=" * 60)
    debug_tencent_data("sh600000")
