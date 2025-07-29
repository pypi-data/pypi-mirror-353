# 功能

获取场内外LOF基金溢价信息，寻找套利机会。

## 使用示例

先安装模块
```bash
pip install lof-fund
```
----
使用`lof_premium`即可获得基金溢价率信息。
```python
from lof import lof_premium

if __name__ == "__main__":
    df_lof = lof_premium()   # 默认返回溢价率±5%的基金，并携带基金t+n信息
    print(df_lof)
    
```
或者直接控制台运行
```bash
lofpm
```

# 关键信息

[x] 场内外基金的溢/折价

[x] 基金申赎T日信息

[x] 申赎状态

[x] 申赎额度

## 可供选择的字段：
```
['场外代码', '基金简称', '最新净值/万份收益', 
'最新净值/万份收益-报告时间', '申购状态', 
'赎回状态', '下一开放日','购买起点', , 溢价率%
'日累计限定金额','手续费', '场内代码', '名称',
'最新价', '涨跌额', '涨跌幅', '成交量','成交额',
'开盘价', '最高价', '最低价', '昨收', '换手率',
'流通市值', '总市值','买入确认日', '卖出确认日']

Data columns (total 27 columns):
 #   Column          Non-Null Count  Dtype  
---  ------          --------------  -----
 0   场外代码            350 non-null    object
 1   基金简称            350 non-null    object
 2   最新净值/万份收益       350 non-null    float64
 3   最新净值/万份收益-报告时间  350 non-null    object
 4   申购状态            350 non-null    object
 5   赎回状态            350 non-null    object
 6   下一开放日           37 non-null     object
 7   购买起点            350 non-null    float64
 8   日累计限定金额         350 non-null    float64
 9   手续费             350 non-null    float64
 10  场内代码            351 non-null    object
 11  名称              351 non-null    object
 12  最新价             351 non-null    float64
 13  涨跌额             351 non-null    float64
 14  涨跌幅             351 non-null    float64
 15  成交量             346 non-null    float64
 16  成交额             346 non-null    float64
 17  开盘价             346 non-null    float64
 18  最高价             346 non-null    float64
 19  最低价             346 non-null    float64
 20  昨收              351 non-null    float64
 21  换手率             347 non-null    float64
 22  流通市值            351 non-null    int64
 23  总市值             351 non-null    int64
 24  溢价率%            350 non-null    float64
 25  买入确认日           350 non-null    object
 26  卖出确认日           350 non-null    object
dtypes: float64(15), int64(2), object(10)
```

# 数据来源

天天基金接口
https://fund.eastmoney.com/161116.html

基金档案（获取T+n信息）：https://fundf10.eastmoney.com/jjfl_161129.html

基金公告：https://fundf10.eastmoney.com/jjgg_161116.html

# v2.0 (ing)
考虑爬集思录的数据或优化原版。

集思录可能出现数据问题,2025/6/3出现过此问题。

# v1 (now)

使用akshare和爬虫程序完成了基本需求，但是速度较慢