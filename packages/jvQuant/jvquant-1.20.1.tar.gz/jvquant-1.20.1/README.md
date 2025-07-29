# jvQuant Python社区功能包说明

该功能包分为**WebSocket实时行情**、**CTP柜台**、**在线数据库**三个模块。

请参考官方社区文档: [官方文档](http://jvquant.com/wiki)

## WebSocket实时行情推送

支持**沪深**、**港股**、**美股** 三大市场全部证券，Level1/Level2行情实时推送。

### WebSocket行情接入示例

```python3
import time
import jvQuant
import logging

def logHandle(log):
    print("Text消息推送:", log)


def dataHandle(data):
    print("Binary行情推送", data)

    
ws = jvQuant.websocket_client
market = "ab"  # 市场标志;沪深:ab；港股:hk；美股:us;
token = "jvQuant平台Token"

# 连接WebSocket行情服务器

# 调试模式，打印所有信息
wsclient = ws.Construct(market, token, logHandle, dataHandle, logging.DEBUG)

# 生产模式，打印关键信息
# wsclient = ws.Construct(market, token, logHandle, dataHandle, logging.INFO)

# 新增level2订阅代码
wsclient.addLv2(["600519", "000001", "i000001"])

# 新增level1订阅代码
wsclient.addLv1(["600519", "000001", "i000001"])

# 港股订阅示例
#wsclient.addLv1(["00700", "09888", "09618"])
# 美股订阅示例
#wsclient.addLv1(["aapl", "nvda", "msft"])

# 查询已订阅列表
wsclient.cmd("list")
time.sleep(5)

# 取消level1订阅代码
wsclient.delLv1(["000001"])
# 取消level2订阅代码
wsclient.delLv2(["i000001"])

# 查询已订阅列表
wsclient.cmd("list")

# 等待子线程退出
wsclient.th_handle.join()
```

## CTP柜台交易

券商柜台全部功能实现:

- 证券交易
- 持仓查询
- 交易查询
- 委托撤单

### CTP接入示例:

```python3
import jvQuant
import logging

ctp = jvQuant.ctp_client

acc = "12位资金账号"
pwd = "6位交易密码"
token = "jvQuant平台Token"

# 调试模式，打印所有信息
ctpclient = ctp.Construct(token, acc, pwd, "", True, logging.DEBUG)

# 生产模式，打印关键信息
#ctpclient = ctp.Construct(token, acc, pwd, "", True, logging.INFO)

# 在关闭自动刷新Ticket时，可自定义连接柜台时机
# response = ctpclient.login()

# 查询持仓信息
response = ctpclient.check_hold()

# 查询委托状态
response = ctpclient.check_order()

# 委托买入
response = ctpclient.buy("600519", "贵州茅台", "1572.12", "1000")

# 委托卖出
response = ctpclient.sale("600519", "贵州茅台", "1572.12", "1000")

# 撤销委托
response = ctpclient.cancel("9702")

# 等待子线程退出
ctpclient.th_handle.join()
```

## 在线数据库服务

实现功能服务如下:

- **智能语义**查询
- 获取**所有证券**的申万行业分类
- 获取所有**可转债**基本信息
- 历史分时数据查询:提供2008~至今历**史分时数据**查询及打包下载
- K线查询:支持**股票**、**可转债**、**ETF**、**指数**，提供近30年K线查询。支持**日K/周K/月K**，**前复权、后复权、不复权**等
- Level2**逐笔委托**队列查询
- Level2**千档盘口**查询

### SQL接入示例:

```python3
import jvQuant
import logging

sql = jvQuant.sql_client

token = "jvQuant平台Token"

# 调试模式，打印所有信息
sqlclient = sql.Construct(token, logging.DEBUG)

# 生产模式，打印关键信息
# sqlclient = sql.Construct(token, logging.INFO)

# 获取所有可转债基本信息
response = sqlclient.bond()

# 获取所有证券的申万行业分类
response = sqlclient.industry()

# Level2千档盘口查询
response = sqlclient.level_queue("600519")

# Level2逐笔委托队列查询
response = sqlclient.order_book("000001", 0)  # 最新队列
response = sqlclient.order_book("600519", 40676443)  # 倒推查询

# 历史分时数据查询
response = sqlclient.minute("600519", '2016-06-21', 2)
response = sqlclient.minute("i000001", '2009-06-21', 2)  # 指数分时

# 智能语义查询
response = sqlclient.query("主板,非ST,价格,近5日涨幅,市盈率，市值大于20亿小于100亿，量比，营业额，利润率，利润，行业，股东人数，IPO时间", 1, 0, "INDUSTRY")
response = sqlclient.query("集合竞价抢筹,30日均线向上,量比", 1, 1, "QRR")

# K线查询
response = sqlclient.kline("600519", "stock", "前复权", "week", 2)
response = sqlclient.kline("000001", "index", "后复权", "day", 2)
response = sqlclient.kline("000001", "stock", "不复权", "day", 2)

# 历史分时数据打包下载
# 遍历下载2008~2016年历史分时
for i in range(2008, 2016):
    sqlclient.download_history(str(i))

# 指定年份下载
sqlclient.download_history("2024")
sqlclient.download_history("2025")

```


- 问题反馈:`help@jvQuant.com`
- 官方社区文档: [官方文档](http://jvquant.com/wiki)
