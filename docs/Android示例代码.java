package com.example.stockapi;

import android.os.AsyncTask;
import android.util.Log;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

/**
 * 股票数据API调用示例
 * 适用于Android工程
 */
public class StockApiExample {
    
    private static final String TAG = "StockApiExample";
    
    /**
     * 股票数据模型
     */
    public static class StockData {
        public String name;           // 股票名称
        public double price;          // 当前价格
        public double change;         // 涨跌额
        public double changePercent;  // 涨跌幅
        public double high;           // 最高价
        public double low;            // 最低价
        public long volume;           // 成交量
        public String time;           // 时间
        
        @Override
        public String toString() {
            return String.format("%s: %.2f (%.2f%%)", name, price, changePercent);
        }
    }
    
    /**
     * K线数据模型
     */
    public static class KlineData {
        public String time;           // 时间
        public double open;           // 开盘价
        public double high;           // 最高价
        public double low;            // 最低价
        public double close;          // 收盘价
        public long volume;           // 成交量
        
        @Override
        public String toString() {
            return String.format("%s: O:%.2f H:%.2f L:%.2f C:%.2f V:%d", 
                time, open, high, low, close, volume);
        }
    }
    
    /**
     * 获取实时股票数据 - 新浪财经
     */
    public static void getRealTimeData(String stockCode, StockDataCallback callback) {
        new AsyncTask<String, Void, StockData>() {
            @Override
            protected StockData doInBackground(String... params) {
                String stockCode = params[0];
                try {
                    String urlString = "http://hq.sinajs.cn/list=" + stockCode;
                    URL url = new URL(urlString);
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("GET");
                    conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
                    conn.setConnectTimeout(10000);
                    conn.setReadTimeout(10000);
                    
                    BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream(), "GBK"));
                    String line = reader.readLine();
                    reader.close();
                    
                    if (line != null && line.contains("=")) {
                        String data = line.split("=")[1].replace("\"", "");
                        String[] fields = data.split(",");
                        
                        StockData stockData = new StockData();
                        stockData.name = fields[0];
                        stockData.price = Double.parseDouble(fields[3]);
                        stockData.change = Double.parseDouble(fields[3]) - Double.parseDouble(fields[2]);
                        stockData.changePercent = (stockData.change / Double.parseDouble(fields[2])) * 100;
                        stockData.high = Double.parseDouble(fields[4]);
                        stockData.low = Double.parseDouble(fields[5]);
                        stockData.volume = Long.parseLong(fields[8]);
                        stockData.time = fields[30] + " " + fields[31];
                        
                        return stockData;
                    }
                } catch (Exception e) {
                    Log.e(TAG, "获取实时数据失败: " + e.getMessage());
                }
                return null;
            }
            
            @Override
            protected void onPostExecute(StockData result) {
                if (callback != null) {
                    callback.onResult(result);
                }
            }
        }.execute(stockCode);
    }
    
    /**
     * 获取分钟级K线数据 - 新浪财经
     */
    public static void getMinuteData(String stockCode, int period, KlineDataCallback callback) {
        new AsyncTask<Object, Void, List<KlineData>>() {
            @Override
            protected List<KlineData> doInBackground(Object... params) {
                String stockCode = (String) params[0];
                int period = (Integer) params[1];
                
                try {
                    String urlString = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData" +
                                     "?symbol=" + stockCode + "&scale=" + period + "&ma=5&datalen=1023";
                    URL url = new URL(urlString);
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("GET");
                    conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
                    conn.setRequestProperty("Accept", "application/json");
                    conn.setConnectTimeout(10000);
                    conn.setReadTimeout(10000);
                    
                    BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.append(line);
                    }
                    reader.close();
                    
                    JSONArray jsonArray = new JSONArray(response.toString());
                    List<KlineData> klineList = new ArrayList<>();
                    
                    for (int i = 0; i < jsonArray.length(); i++) {
                        JSONObject jsonObject = jsonArray.getJSONObject(i);
                        KlineData klineData = new KlineData();
                        klineData.time = jsonObject.getString("day");
                        klineData.open = Double.parseDouble(jsonObject.getString("open"));
                        klineData.high = Double.parseDouble(jsonObject.getString("high"));
                        klineData.low = Double.parseDouble(jsonObject.getString("low"));
                        klineData.close = Double.parseDouble(jsonObject.getString("close"));
                        klineData.volume = Long.parseLong(jsonObject.getString("volume"));
                        klineList.add(klineData);
                    }
                    
                    return klineList;
                } catch (Exception e) {
                    Log.e(TAG, "获取分钟数据失败: " + e.getMessage());
                }
                return null;
            }
            
            @Override
            protected void onPostExecute(List<KlineData> result) {
                if (callback != null) {
                    callback.onResult(result);
                }
            }
        }.execute(stockCode, period);
    }
    
    /**
     * 获取日K线数据 - 新浪财经
     */
    public static void getDailyData(String stockCode, int days, KlineDataCallback callback) {
        new AsyncTask<Object, Void, List<KlineData>>() {
            @Override
            protected List<KlineData> doInBackground(Object... params) {
                String stockCode = (String) params[0];
                int days = (Integer) params[1];
                
                try {
                    String urlString = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData" +
                                     "?symbol=" + stockCode + "&scale=240&ma=5&datalen=" + days;
                    URL url = new URL(urlString);
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("GET");
                    conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
                    conn.setRequestProperty("Accept", "application/json");
                    conn.setConnectTimeout(10000);
                    conn.setReadTimeout(10000);
                    
                    BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.append(line);
                    }
                    reader.close();
                    
                    JSONArray jsonArray = new JSONArray(response.toString());
                    List<KlineData> klineList = new ArrayList<>();
                    
                    for (int i = 0; i < jsonArray.length(); i++) {
                        JSONObject jsonObject = jsonArray.getJSONObject(i);
                        KlineData klineData = new KlineData();
                        klineData.time = jsonObject.getString("day");
                        klineData.open = Double.parseDouble(jsonObject.getString("open"));
                        klineData.high = Double.parseDouble(jsonObject.getString("high"));
                        klineData.low = Double.parseDouble(jsonObject.getString("low"));
                        klineData.close = Double.parseDouble(jsonObject.getString("close"));
                        klineData.volume = Long.parseLong(jsonObject.getString("volume"));
                        klineList.add(klineData);
                    }
                    
                    return klineList;
                } catch (Exception e) {
                    Log.e(TAG, "获取日K数据失败: " + e.getMessage());
                }
                return null;
            }
            
            @Override
            protected void onPostExecute(List<KlineData> result) {
                if (callback != null) {
                    callback.onResult(result);
                }
            }
        }.execute(stockCode, days);
    }
    
    /**
     * 获取东方财富分钟数据
     */
    public static void getEastMoneyMinuteData(String stockCode, int period, KlineDataCallback callback) {
        new AsyncTask<Object, Void, List<KlineData>>() {
            @Override
            protected List<KlineData> doInBackground(Object... params) {
                String stockCode = (String) params[0];
                int period = (Integer) params[1];
                
                try {
                    // 转换股票代码格式
                    String secid;
                    if (stockCode.startsWith("sz")) {
                        secid = "0." + stockCode.substring(2);
                    } else if (stockCode.startsWith("sh")) {
                        secid = "1." + stockCode.substring(2);
                    } else {
                        secid = "0." + stockCode;
                    }
                    
                    String urlString = "http://push2his.eastmoney.com/api/qt/stock/kline/get" +
                                     "?secid=" + secid +
                                     "&fields1=f1,f2,f3,f4,f5,f6" +
                                     "&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61" +
                                     "&klt=" + period +
                                     "&fqt=0&beg=0&end=20500101&smplmt=1023&lmt=1023";
                    
                    URL url = new URL(urlString);
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("GET");
                    conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
                    conn.setRequestProperty("Accept", "application/json");
                    conn.setConnectTimeout(10000);
                    conn.setReadTimeout(10000);
                    
                    BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.append(line);
                    }
                    reader.close();
                    
                    JSONObject jsonObject = new JSONObject(response.toString());
                    JSONArray klines = jsonObject.getJSONObject("data").getJSONArray("klines");
                    List<KlineData> klineList = new ArrayList<>();
                    
                    for (int i = 0; i < klines.length(); i++) {
                        String[] fields = klines.getString(i).split(",");
                        KlineData klineData = new KlineData();
                        klineData.time = fields[0];
                        klineData.open = Double.parseDouble(fields[1]);
                        klineData.close = Double.parseDouble(fields[2]);
                        klineData.high = Double.parseDouble(fields[3]);
                        klineData.low = Double.parseDouble(fields[4]);
                        klineData.volume = Long.parseLong(fields[5]);
                        klineList.add(klineData);
                    }
                    
                    return klineList;
                } catch (Exception e) {
                    Log.e(TAG, "获取东方财富分钟数据失败: " + e.getMessage());
                }
                return null;
            }
            
            @Override
            protected void onPostExecute(List<KlineData> result) {
                if (callback != null) {
                    callback.onResult(result);
                }
            }
        }.execute(stockCode, period);
    }
    
    /**
     * 回调接口 - 实时数据
     */
    public interface StockDataCallback {
        void onResult(StockData stockData);
    }
    
    /**
     * 回调接口 - K线数据
     */
    public interface KlineDataCallback {
        void onResult(List<KlineData> klineList);
    }
    
    /**
     * 使用示例
     */
    public static void usageExample() {
        // 获取实时数据
        getRealTimeData("sz000498", new StockDataCallback() {
            @Override
            public void onResult(StockData stockData) {
                if (stockData != null) {
                    Log.d(TAG, "实时数据: " + stockData.toString());
                }
            }
        });
        
        // 获取30分钟数据
        getMinuteData("sz000498", 30, new KlineDataCallback() {
            @Override
            public void onResult(List<KlineData> klineList) {
                if (klineList != null) {
                    Log.d(TAG, "30分钟数据条数: " + klineList.size());
                    for (KlineData kline : klineList) {
                        Log.d(TAG, kline.toString());
                    }
                }
            }
        });
        
        // 获取日K数据
        getDailyData("sz000498", 90, new KlineDataCallback() {
            @Override
            public void onResult(List<KlineData> klineList) {
                if (klineList != null) {
                    Log.d(TAG, "日K数据条数: " + klineList.size());
                    for (KlineData kline : klineList) {
                        Log.d(TAG, kline.toString());
                    }
                }
            }
        });
    }
}
