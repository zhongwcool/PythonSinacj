# 股票数据API文档索引

## 📚 文档列表

### 1. [股票数据API文档.md](./股票数据API文档.md)
**完整详细的API文档**
- 实时股票数据API（新浪财经、腾讯财经、网易财经）
- 分钟级数据API（新浪财经、东方财富、腾讯财经）
- 日K线数据API（新浪财经、东方财富、Yahoo Finance）
- 详细的HTTP配置和参数说明
- Android工程集成建议
- 错误处理和注意事项

### 2. [API快速参考表.md](./API快速参考表.md)
**快速查找参考表**
- 简化的API接口表格
- HTTP配置模板
- Android权限配置
- 常用股票代码
- 快速使用示例

### 3. [Android示例代码.java](./Android示例代码.java)
**完整的Android示例代码**
- 实时数据获取示例
- 分钟级数据获取示例
- 日K线数据获取示例
- 数据模型定义
- 异步处理示例
- 错误处理示例

---

## 🎯 快速开始

### 获取实时数据
```java
// 使用新浪财经API获取实时数据
StockApiExample.getRealTimeData("sz000498", new StockApiExample.StockDataCallback() {
    @Override
    public void onResult(StockApiExample.StockData stockData) {
        if (stockData != null) {
            Log.d("StockAPI", "股票: " + stockData.name + ", 价格: " + stockData.price);
        }
    }
});
```

### 获取30分钟数据
```java
// 使用新浪财经API获取30分钟数据
StockApiExample.getMinuteData("sz000498", 30, new StockApiExample.KlineDataCallback() {
    @Override
    public void onResult(List<StockApiExample.KlineData> klineList) {
        if (klineList != null) {
            Log.d("StockAPI", "获取到 " + klineList.size() + " 条30分钟数据");
        }
    }
});
```

### 获取日K数据
```java
// 使用新浪财经API获取90日K线数据
StockApiExample.getDailyData("sz000498", 90, new StockApiExample.KlineDataCallback() {
    @Override
    public void onResult(List<StockApiExample.KlineData> klineList) {
        if (klineList != null) {
            Log.d("StockAPI", "获取到 " + klineList.size() + " 条日K数据");
        }
    }
});
```

---

## 📊 支持的API类型

| 数据类型 | 支持的数据源 | 推荐使用 |
|----------|-------------|----------|
| 实时数据 | 新浪财经、腾讯财经、网易财经 | 新浪财经 |
| 分钟数据 | 新浪财经、东方财富、腾讯财经 | 新浪财经 |
| 日K数据 | 新浪财经、东方财富、Yahoo Finance | 新浪财经 |

---

## 🔧 Android配置要求

### 权限配置
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### 网络安全配置
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
```

### 支持的Android版本
- Android 4.0 (API 14) 及以上
- 推荐 Android 5.0 (API 21) 及以上

---

## 📝 使用建议

1. **数据源选择**：
   - 实时数据：推荐使用新浪财经API，稳定性好
   - 分钟数据：推荐使用新浪财经API，数据完整
   - 日K数据：推荐使用新浪财经API，历史数据丰富

2. **请求频率**：
   - 实时数据：建议3-5秒间隔
   - 分钟数据：建议1-5分钟间隔
   - 日K数据：建议每天更新一次

3. **错误处理**：
   - 必须处理网络异常
   - 必须处理数据解析异常
   - 建议实现重试机制

4. **性能优化**：
   - 使用异步请求
   - 实现数据缓存
   - 避免频繁请求

---

## 🆘 常见问题

### Q: 网络请求失败怎么办？
A: 检查网络权限配置，确保网络安全配置正确，尝试使用不同的数据源。

### Q: 数据解析失败怎么办？
A: 检查API返回的数据格式，确保解析逻辑正确，添加异常处理。

### Q: 请求频率过高被限制怎么办？
A: 降低请求频率，增加请求间隔，实现请求队列管理。

### Q: 如何选择合适的API？
A: 根据数据需求选择：
- 实时数据：新浪财经API
- 分钟数据：新浪财经API
- 日K数据：新浪财经API
- 备用方案：东方财富API

---

## 📞 技术支持

如有问题，请参考：
1. 详细的API文档
2. Android示例代码
3. 常见问题解答
4. 错误日志分析

---

## 📅 更新日志

- **2025-08-08**: 初始版本发布
  - 支持实时数据、分钟数据、日K数据
  - 提供完整的Android示例代码
  - 包含详细的API文档和配置说明
