# 股票K线数据获取工具

## 功能说明

这个工具可以帮助您获取股票的90日K线数据，支持多种数据源：

- **新浪财经** - 国内股票数据
- **东方财富** - 国内股票数据（备用）
- **Yahoo Finance** - 国际股票数据

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 基本使用

```python
from kline_data_fetcher import KlineDataFetcher

# 创建数据获取器
fetcher = KlineDataFetcher()

# 获取sz000498的90日K线数据
df = fetcher.get_kline_data("sz000498", days=90, data_source="auto")

if df is not None:
    # 显示数据摘要
    fetcher.print_summary(df, "sz000498")
    
    # 保存到CSV文件
    fetcher.save_to_csv(df, "sz000498")
    
    # 保存到JSON文件
    fetcher.save_to_json(df, "sz000498")
```

### 2. 运行示例

```bash
# 运行主程序
python kline_data_fetcher.py

# 运行使用示例
python example_usage.py
```

### 3. 支持的股票代码格式

- **深市股票**: `sz000498`, `sz000001`
- **沪市股票**: `sh600000`, `sh000001`
- **指数**: `sh000001`(上证指数), `sz399001`(深证成指)

## 数据格式

获取的数据包含以下字段：

| 字段名 | 说明 |
|--------|------|
| 日期 | 交易日期 |
| 开盘价 | 当日开盘价 |
| 最高价 | 当日最高价 |
| 最低价 | 当日最低价 |
| 收盘价 | 当日收盘价 |
| 成交量 | 当日成交量 |
| 成交额 | 当日成交额（部分数据源） |
| 涨跌幅 | 涨跌幅百分比（部分数据源） |
| 涨跌额 | 涨跌金额（部分数据源） |
| 换手率 | 换手率（部分数据源） |

## 注意事项

1. **数据源选择**: 建议使用 `data_source="auto"`，程序会自动尝试多个数据源
2. **请求频率**: 避免过于频繁的请求，建议间隔1-2秒
3. **网络环境**: 某些数据源可能需要稳定的网络连接
4. **数据准确性**: 不同数据源的数据可能有细微差异

## 常见问题

### Q: 为什么新浪财经API获取失败？
A: 新浪财经的API有时会返回不同格式的数据，程序会自动处理，如果仍然失败会尝试其他数据源。

### Q: 可以获取多少天的数据？
A: 理论上可以获取任意天数的数据，但建议不超过365天，避免请求超时。

### Q: 支持哪些股票？
A: 支持A股市场的所有股票和主要指数，以及部分国际股票。

## 文件说明

- `kline_data_fetcher.py` - 主要的K线数据获取工具
- `example_usage.py` - 使用示例
- `api_stability_test.py` - API稳定性测试工具（原有功能）
- `requirements.txt` - 依赖包列表

## 输出文件

程序会生成以下文件：

- `sz000498_kline_data_YYYYMMDD_HHMMSS.csv` - CSV格式的K线数据
- `sz000498_kline_data_YYYYMMDD_HHMMSS.json` - JSON格式的K线数据 