# 股票数据API文档

## 概述

本文档整理了可用于获取股票数据的各种API接口，包括实时数据、分钟级数据和日K线数据。所有API均支持HTTP GET请求，适合Android工程调用。

---

## 1. 实时股票数据API

### 1.1 新浪财经实时数据API

**接口地址**: `http://hq.sinajs.cn/list=股票代码`

**请求方式**: GET

**参数说明**:
- `股票代码`: 股票代码，如 `sz000498`（深圳）、`sh600000`（上海）

**请求示例**:
```
GET http://hq.sinajs.cn/list=sz000498
```

**响应格式**: 文本格式
```
var hq_str_sz000498="山东路桥,6.07,6.08,6.07,0.00,0.00,6.07,3564435,216456789.00,100,6.06,123400,6.05,234500,6.04,345600,6.03,456700,6.02,567800,6.07,98700,6.08,87600,6.09,76500,6.10,65400,6.11,54300,2025-08-08,15:00:00,00,D|0|0";
```

**响应字段解析**:
```
股票名称,今日开盘价,昨日收盘价,当前价格,今日最高价,今日最低价,竞买价,竞卖价,成交股数,成交金额,买一量,买一价,买二量,买二价,买三量,买三价,买四量,买四价,买五量,买五价,卖一量,卖一价,卖二量,卖二价,卖三量,卖三价,卖四量,卖四价,卖五量,卖五价,日期,时间,状态,其他
```

**HTTP配置**:
```java
// Android Java示例
URL url = new URL("http://hq.sinajs.cn/list=sz000498");
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
conn.setConnectTimeout(10000);
conn.setReadTimeout(10000);
```

### 1.2 腾讯财经实时数据API

**接口地址**: `http://qt.gtimg.cn/q=股票代码`

**请求方式**: GET

**请求示例**:
```
GET http://qt.gtimg.cn/q=sz000498
```

**响应格式**: 文本格式
```
v_sz000498="51~山东路桥~000498~6.07~6.08~6.07~3564435~216456789~6.06~123400~6.05~234500~6.04~345600~6.03~456700~6.02~567800~6.07~98700~6.08~87600~6.09~76500~6.10~65400~6.11~54300~20250808~15:00:00~00~0~0";
```

**HTTP配置**:
```java
URL url = new URL("http://qt.gtimg.cn/q=sz000498");
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
conn.setConnectTimeout(10000);
conn.setReadTimeout(10000);
```

### 1.3 网易财经实时数据API

**接口地址**: `http://api.money.126.net/data/feed/股票代码`

**请求方式**: GET

**请求示例**:
```
GET http://api.money.126.net/data/feed/000498
```

**响应格式**: JSON格式
```json
{
  "000498": {
    "code": "000498",
    "name": "山东路桥",
    "price": 6.07,
    "percent": 0.00,
    "change": 0.00,
    "high": 6.08,
    "low": 6.06,
    "volume": 3564435,
    "amount": 216456789,
    "time": "2025-08-08 15:00:00"
  }
}
```

**HTTP配置**:
```java
URL url = new URL("http://api.money.126.net/data/feed/000498");
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("Accept", "application/json");
conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
conn.setConnectTimeout(10000);
conn.setReadTimeout(10000);
```

---

## 2. 分钟级数据API

### 2.1 新浪财经分钟数据API

**接口地址**: `http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData`

**请求方式**: GET

**参数说明**:
- `symbol`: 股票代码，如 `sz000498`
- `scale`: 分钟周期，支持 `1`, `5`, `15`, `30`, `60`
- `ma`: 均线参数，如 `5`
- `datalen`: 数据长度，最大 `1023`

**请求示例**:
```
GET http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000498&scale=30&ma=5&datalen=1023
```

**响应格式**: JSON格式
```json
[
  {
    "day": "2025-08-08 15:00:00",
    "open": "6.07",
    "high": "6.08",
    "low": "6.06",
    "close": "6.07",
    "volume": "3564435"
  }
]
```

**HTTP配置**:
```java
String urlString = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData" +
                   "?symbol=sz000498&scale=30&ma=5&datalen=1023";
URL url = new URL(urlString);
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
conn.setRequestProperty("Accept", "application/json");
conn.setConnectTimeout(10000);
conn.setReadTimeout(10000);
```

### 2.2 东方财富分钟数据API

**接口地址**: `http://push2his.eastmoney.com/api/qt/stock/kline/get`

**请求方式**: GET

**参数说明**:
- `secid`: 股票ID，格式为 `市场.代码`，如 `0.000498`（深圳）、`1.600000`（上海）
- `fields1`: 字段1，固定值 `f1,f2,f3,f4,f5,f6`
- `fields2`: 字段2，固定值 `f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61`
- `klt`: 分钟周期，支持 `1`, `5`, `15`, `30`, `60`
- `fqt`: 复权类型，`0`=不复权，`1`=前复权，`2`=后复权
- `beg`: 开始日期，`0`表示不限制
- `end`: 结束日期，`20500101`表示不限制
- `smplmt`: 数据限制，如 `1023`
- `lmt`: 数据限制，如 `1023`

**请求示例**:
```
GET http://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.000498&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=30&fqt=0&beg=0&end=20500101&smplmt=1023&lmt=1023
```

**响应格式**: JSON格式
```json
{
  "data": {
    "klines": [
      "2025-08-08 15:00:00,6.07,6.07,6.08,6.06,3564435,216456789,0.33,0.00,0.00,0.00"
    ]
  }
}
```

**响应字段解析**:
```
时间,开盘价,收盘价,最高价,最低价,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
```

**HTTP配置**:
```java
String urlString = "http://push2his.eastmoney.com/api/qt/stock/kline/get" +
                   "?secid=0.000498&fields1=f1,f2,f3,f4,f5,f6" +
                   "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61" +
                   "&klt=30&fqt=0&beg=0&end=20500101&smplmt=1023&lmt=1023";
URL url = new URL(urlString);
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
conn.setRequestProperty("Accept", "application/json");
conn.setConnectTimeout(10000);
conn.setReadTimeout(10000);
```

### 2.3 腾讯财经分钟数据API

**接口地址**: `http://ifzq.gtimg.cn/appstock/app/kline/mkline`

**请求方式**: GET

**参数说明**:
- `param`: 参数，格式为 `股票代码,周期类型,开始日期,结束日期,复权类型,数据长度`
- `_`: 时间戳

**请求示例**:
```
GET http://ifzq.gtimg.cn/appstock/app/kline/mkline?param=sz000498,m30,,,qfq,1023&_=1691481600000
```

**周期类型说明**:
- `m1`: 1分钟
- `m5`: 5分钟
- `m15`: 15分钟
- `m30`: 30分钟
- `m60`: 60分钟

**响应格式**: JSON格式
```json
{
  "data": {
    "sz000498": {
      "m30": [
        ["2025-08-08 15:00:00", 6.07, 6.07, 6.08, 6.06, 3564435]
      ]
    }
  }
}
```

**响应字段解析**:
```
[时间,开盘价,收盘价,最高价,最低价,成交量]
```

**HTTP配置**:
```java
long timestamp = System.currentTimeMillis();
String urlString = "http://ifzq.gtimg.cn/appstock/app/kline/mkline" +
                   "?param=sz000498,m30,,,qfq,1023&_=" + timestamp;
URL url = new URL(urlString);
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
conn.setRequestProperty("Accept", "application/json");
conn.setConnectTimeout(10000);
conn.setReadTimeout(10000);
```

---

## 3. 日K线数据API

### 3.1 新浪财经日K数据API

**接口地址**: `http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData`

**请求方式**: GET

**参数说明**:
- `symbol`: 股票代码，如 `sz000498`
- `scale`: 周期，日K线使用 `240`
- `ma`: 均线参数，如 `5`
- `datalen`: 数据长度，如 `90`

**请求示例**:
```
GET http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000498&scale=240&ma=5&datalen=90
```

**响应格式**: JSON格式
```json
[
  {
    "day": "2025-08-08",
    "open": "6.07",
    "high": "6.08",
    "low": "6.06",
    "close": "6.07",
    "volume": "3564435"
  }
]
```

**HTTP配置**:
```java
String urlString = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData" +
                   "?symbol=sz000498&scale=240&ma=5&datalen=90";
URL url = new URL(urlString);
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
conn.setRequestProperty("Accept", "application/json");
conn.setConnectTimeout(10000);
conn.setReadTimeout(10000);
```

### 3.2 东方财富日K数据API

**接口地址**: `http://push2his.eastmoney.com/api/qt/stock/kline/get`

**请求方式**: GET

**参数说明**:
- `secid`: 股票ID，格式为 `市场.代码`
- `fields1`: 字段1，固定值 `f1,f2,f3,f4,f5,f6`
- `fields2`: 字段2，固定值 `f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61`
- `klt`: 周期，日K线使用 `101`
- `fqt`: 复权类型，`0`=不复权，`1`=前复权，`2`=后复权
- `beg`: 开始日期，`0`表示不限制
- `end`: 结束日期，`20500101`表示不限制
- `smplmt`: 数据限制，如 `90`
- `lmt`: 数据限制，如 `90`

**请求示例**:
```
GET http://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.000498&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=0&beg=0&end=20500101&smplmt=90&lmt=90
```

**响应格式**: JSON格式
```json
{
  "data": {
    "klines": [
      "2025-08-08,6.07,6.07,6.08,6.06,3564435,216456789,0.33,0.00,0.00,0.00"
    ]
  }
}
```

**HTTP配置**:
```java
String urlString = "http://push2his.eastmoney.com/api/qt/stock/kline/get" +
                   "?secid=0.000498&fields1=f1,f2,f3,f4,f5,f6" +
                   "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61" +
                   "&klt=101&fqt=0&beg=0&end=20500101&smplmt=90&lmt=90";
URL url = new URL(urlString);
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
conn.setRequestProperty("Accept", "application/json");
conn.setConnectTimeout(10000);
conn.setReadTimeout(10000);
```

### 3.3 Yahoo Finance日K数据API

**接口地址**: `https://query1.finance.yahoo.com/v8/finance/chart/股票代码`

**请求方式**: GET

**参数说明**:
- `period1`: 开始时间戳
- `period2`: 结束时间戳
- `interval`: 间隔，日K线使用 `1d`
- `events`: 事件，固定值 `history`

**请求示例**:
```
GET https://query1.finance.yahoo.com/v8/finance/chart/000498.SZ?period1=1691481600&period2=1691568000&interval=1d&events=history
```

**响应格式**: JSON格式
```json
{
  "chart": {
    "result": [
      {
        "timestamp": [1691481600],
        "indicators": {
          "quote": [
            {
              "open": [6.07],
              "high": [6.08],
              "low": [6.06],
              "close": [6.07],
              "volume": [3564435]
            }
          ]
        }
      }
    ]
  }
}
```

**HTTP配置**:
```java
long startTime = 1691481600L;
long endTime = 1691568000L;
String urlString = "https://query1.finance.yahoo.com/v8/finance/chart/000498.SZ" +
                   "?period1=" + startTime + "&period2=" + endTime +
                   "&interval=1d&events=history";
URL url = new URL(urlString);
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
conn.setRequestProperty("Accept", "application/json");
conn.setConnectTimeout(10000);
conn.setReadTimeout(10000);
```

---

## 4. 股票代码格式说明

### 4.1 中国市场股票代码

**深圳市场**:
- 格式: `sz` + 6位数字代码
- 示例: `sz000498`（山东路桥）

**上海市场**:
- 格式: `sh` + 6位数字代码
- 示例: `sh600000`（浦发银行）

### 4.2 指数代码

**主要指数**:
- `sh000001`: 上证指数
- `sz399001`: 深证成指
- `sz399006`: 创业板指

---

## 5. Android工程集成建议

### 5.1 网络权限配置

在 `AndroidManifest.xml` 中添加网络权限：

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### 5.2 网络安全配置

在 `res/xml/network_security_config.xml` 中配置：

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">hq.sinajs.cn</domain>
        <domain includeSubdomains="true">qt.gtimg.cn</domain>
        <domain includeSubdomains="true">api.money.126.net</domain>
        <domain includeSubdomains="true">money.finance.sina.com.cn</domain>
        <domain includeSubdomains="true">push2his.eastmoney.com</domain>
        <domain includeSubdomains="true">ifzq.gtimg.cn</domain>
        <domain includeSubdomains="true">query1.finance.yahoo.com</domain>
    </domain-config>
</network-security-config>
```

在 `AndroidManifest.xml` 中引用：

```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

### 5.3 异步请求处理

建议使用异步线程处理网络请求：

```java
// 使用AsyncTask或Thread
new Thread(new Runnable() {
    @Override
    public void run() {
        // 执行网络请求
        String result = fetchStockData();
        
        // 在主线程更新UI
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                // 更新UI
                updateUI(result);
            }
        });
    }
}).start();
```

### 5.4 错误处理

```java
try {
    // 网络请求
    String result = fetchStockData();
    // 处理结果
} catch (Exception e) {
    // 错误处理
    Log.e("StockAPI", "请求失败: " + e.getMessage());
    // 显示错误信息
    showErrorMessage("网络请求失败，请检查网络连接");
}
```

---

## 6. 注意事项

1. **请求频率限制**: 建议控制请求频率，避免过于频繁的请求
2. **数据缓存**: 建议对数据进行缓存，减少重复请求
3. **网络异常处理**: 需要处理网络异常和超时情况
4. **数据格式验证**: 需要验证返回数据的格式和完整性
5. **股票代码验证**: 确保股票代码格式正确
6. **时间同步**: 注意服务器时间与本地时间的差异

---

## 7. 更新日志

- **2025-08-08**: 初始版本，包含实时数据、分钟数据和日K数据API
- 支持新浪财经、东方财富、腾讯财经、网易财经、Yahoo Finance等数据源
