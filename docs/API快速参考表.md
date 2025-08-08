# 股票数据API快速参考表

## 📊 实时数据API

| 数据源 | 接口地址 | 请求方式 | 响应格式 | 示例 |
|--------|----------|----------|----------|------|
| 新浪财经 | `http://hq.sinajs.cn/list=股票代码` | GET | 文本 | `sz000498` |
| 腾讯财经 | `http://qt.gtimg.cn/q=股票代码` | GET | 文本 | `sz000498` |
| 网易财经 | `http://api.money.126.net/data/feed/股票代码` | GET | JSON | `000498` |

## ⏱️ 分钟数据API

| 数据源 | 接口地址 | 周期参数 | 响应格式 | 示例 |
|--------|----------|----------|----------|------|
| 新浪财经 | `http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData` | `scale=1/5/15/30/60` | JSON | `symbol=sz000498&scale=30` |
| 东方财富 | `http://push2his.eastmoney.com/api/qt/stock/kline/get` | `klt=1/5/15/30/60` | JSON | `secid=0.000498&klt=30` |
| 腾讯财经 | `http://ifzq.gtimg.cn/appstock/app/kline/mkline` | `param=股票代码,m1/m5/m15/m30/m60` | JSON | `param=sz000498,m30` |

## 📈 日K数据API

| 数据源 | 接口地址 | 周期参数 | 响应格式 | 示例 |
|--------|----------|----------|----------|------|
| 新浪财经 | `http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData` | `scale=240` | JSON | `symbol=sz000498&scale=240` |
| 东方财富 | `http://push2his.eastmoney.com/api/qt/stock/kline/get` | `klt=101` | JSON | `secid=0.000498&klt=101` |
| Yahoo Finance | `https://query1.finance.yahoo.com/v8/finance/chart/股票代码` | `interval=1d` | JSON | `000498.SZ?interval=1d` |

---

## 🔧 HTTP配置模板

### Java Android 配置

```java
// 通用HTTP配置
URL url = new URL("API地址");
HttpURLConnection conn = (HttpURLConnection) url.openConnection();
conn.setRequestMethod("GET");
conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
conn.setRequestProperty("Accept", "application/json");
conn.setConnectTimeout(10000);
conn.setReadTimeout(10000);
```

### Kotlin Android 配置

```kotlin
// 通用HTTP配置
val url = URL("API地址")
val conn = url.openConnection() as HttpURLConnection
conn.requestMethod = "GET"
conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
conn.setRequestProperty("Accept", "application/json")
conn.connectTimeout = 10000
conn.readTimeout = 10000
```

---

## 📱 Android权限配置

### AndroidManifest.xml
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### 网络安全配置 (res/xml/network_security_config.xml)
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

---

## 🎯 常用股票代码

| 股票名称 | 深圳代码 | 上海代码 | 指数代码 |
|----------|----------|----------|----------|
| 山东路桥 | `sz000498` | - | - |
| 浦发银行 | - | `sh600000` | - |
| 上证指数 | - | - | `sh000001` |
| 深证成指 | - | - | `sz399001` |
| 创业板指 | - | - | `sz399006` |

---

## ⚡ 快速使用示例

### 获取实时数据
```java
// 新浪财经实时数据
String url = "http://hq.sinajs.cn/list=sz000498";
```

### 获取30分钟数据
```java
// 新浪财经30分钟数据
String url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000498&scale=30&ma=5&datalen=1023";
```

### 获取日K数据
```java
// 新浪财经日K数据
String url = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000498&scale=240&ma=5&datalen=90";
```

---

## 📝 注意事项

1. **请求频率**: 建议间隔3秒以上
2. **错误处理**: 必须处理网络异常
3. **数据缓存**: 建议本地缓存减少请求
4. **异步处理**: 网络请求必须在后台线程
5. **超时设置**: 建议设置10秒超时
6. **User-Agent**: 必须设置浏览器标识
