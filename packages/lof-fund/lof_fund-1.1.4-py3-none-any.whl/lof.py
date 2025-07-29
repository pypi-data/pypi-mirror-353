#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' 
一个获取基金溢价率的脚本 

直接运行此脚本或者调用lof_premium函数

```python
from lof import lof_premium

if __name__ == "__main__":
    df_lof = lof_premium()   # 默认返回溢价率±5%的基金，并携带基金t+n信息
    print(df_lof)
```
'''

__author__ = 'Egg*4'
# %%
import akshare as ak
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import logging
import os
import time


logger = logging.getLogger("logger")

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename="lof_premium.log",encoding='utf-8')

logger.setLevel(logging.DEBUG)
console_handler.setLevel(logging.WARNING)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    fmt="%(asctime)s %(name)s:%(levelname)s:%(funcName)s:%(lineno)d:%(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S",  # 修正月份格式
)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# %%
def checkFundCode(row:pd.Series):
    """
    有数据审查功能的添加基金T+n信息的函数。如果基金代码遗传则会记录到日志
    """
    try:
        code = row["场外代码"]
    except Exception as e:
        logger.critical("缺少 `场外代码` 字段")
        raise e
    if code is pd.NA or code is np.nan:
        logger.warning(f"代码字段为空值,跳过\n{str(row)} ")
        return {}
    else:
        return fund_tn_rules(code)
    
def fund_tn_rules(fund_code:str|int):
    """
    - fund_code: 传入一个场外基金代码

    基金的买入确认日表示以何日为基准，买入确认日为T+1，表示基金在T日申购的份额，在T+1日可以确认份额。在T+2日可以卖出。
    """
    url = f"https://fundf10.eastmoney.com/jjfl_{fund_code}.html"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    # 解析申购赎回规则（需根据实际页面结构调整）
    tbnull_label = soup.find("label", class_="tbnull")
    if tbnull_label and "该基金尚未开通天天基金代销" in tbnull_label.text:
        logger.warning(f"{fund_code} 该基金尚未开通天天基金代销，暂无相关数据。")
        return {
            "买入确认日":"未代销",
            "卖出确认日":"未代销",
            "jjfl_url" :url
        }
    try:
    # 获取买入确认日和卖出确认日
        buy_tn = soup.find("td", class_="th", string="买入确认日").find_next_sibling("td").text
        sell_tn = soup.find("td", class_="th", string="卖出确认日").find_next_sibling("td").text
        t_n_info = {
            "买入确认日":buy_tn,
            "卖出确认日":sell_tn,
            "jjfl_url" :url
        }
        return t_n_info
    except AttributeError as e:
        logger.error(f"{fund_code} 代码找不到买入确认日和卖出确认日, 请检查网页结构是否变化, url:{url}")
        return {}
    except Exception as e:
        logger.error(f"{fund_code} 代码获取买入确认日和卖出确认日时出错, url:{url}")
        return {}
    
def add_fund_tn_col(lof_df:pd.DataFrame):
    """ 
    - lof_df: 必须有`场外代码`字段, 表示基金的场外代码

    给基金加上T+n信息,会添加上两个字段：["买入确认日","卖出确认日"]
    """
    
    tn_info:pd.Series = lof_df.apply(checkFundCode, axis=1)
    
    # 将 tn_info 转换为 DataFrame
    tn_df = pd.DataFrame(tn_info.tolist())
    
    # 合并到 lof_df
    lof_df = pd.concat([lof_df, tn_df], axis=1)

    return lof_df

# %%
def get_fund_data():
    """获取合并后的场内外基金数据"""
    fund_df = ak.fund_purchase_em()
    fund_df.drop(columns=['序号', '基金类型'], inplace=True)
    lof_spot = ak.fund_lof_spot_em()
    lof_spot = lof_spot[~lof_spot["最新价"].isnull()]
    lof_spot['最新价'] = lof_spot['最新价'].astype(float)
    merged_df = pd.merge(fund_df, lof_spot, left_on='基金代码', right_on='代码', how='right')
    return merged_df

# %%
# (row['最新价'] - nav_value) / nav_value * 100
def calculate_premium(row):
    """计算溢价率"""
    try:
        nav_value = row['最新净值/万份收益']
        latest_price = row['最新价']
        if nav_value is pd.NA or latest_price is pd.NA:
            return None
        return (latest_price - nav_value) / nav_value * 100
    except Exception as e:
        logger.error(f"计算溢价率异常：{str(e)}")
        return None

def filter_premium(df_lof_premium:pd.DataFrame,rate:float=5) -> pd.DataFrame:
    """
    df_lof_premium: LOF基金溢价率数据

    rate: 筛选出溢价率±rate%的LOF基金,默认筛选出溢价率±5%的LOF基金
    """
    return (
            df_lof_premium[
            (df_lof_premium['溢价率%'] >= rate) | (df_lof_premium['溢价率%'] <= -rate)
            ].sort_values(by="溢价率%",ascending=False).reset_index(drop=True)
        )

def lof_premium(rate:float|int = 5.0, t_n:bool=True) -> pd.DataFrame:
    """
    A股基金溢价率信息

    含有以下列名：
    `['场外代码', '基金简称', '最新净值/万份收益', '最新净值/万份收益-报告时间', '申购状态', '赎回状态', '下一开放日',
       '购买起点', '日累计限定金额', 溢价率%, '手续费', '场内代码', '名称', '最新价', '涨跌额', '涨跌幅', '成交量', '成交额',
       '开盘价', '最高价', '最低价', '昨收', '换手率', '流通市值', '总市值','买入确认日','卖出确认日']`
       
    ## Parameters
        **rate** : float or int, default 5.0
        默认筛选出基金溢价率±5%的基金

        **t_n** : bool, default True
        加上基金的T+n信息,若设置为False,返回结果将没有`["买入确认日","卖出确认日"]`字段
    
    """
    merged_df = get_fund_data()
    merged_df['溢价率%'] = merged_df.apply(calculate_premium, axis=1)

    merged_df.sort_values(by='溢价率%', ascending=False, inplace=True)

    merged_df.rename(columns={'基金代码': '场外代码', '代码': '场内代码'}, inplace=True)
    filter_df = filter_premium(merged_df,rate)
    return add_fund_tn_col(filter_df) if t_n else filter_df
    

def main():
    df_lof = lof_premium()
    # columns = ["场外代码",'场内代码', '名称', '最新价', '最新净值/万份收益', '溢价率%', '申购状态',
    #    '赎回状态', '下一开放日',"买入确认日","卖出确认日", '购买起点', '日累计限定金额', '手续费']
    
    filtered_df = df_lof
    # 如果lof_premium文件夹不存在，则创建
    if not os.path.exists('lof_premium'):
        os.makedirs('lof_premium')
    # 保存文件到lof_premium文件夹
    # 获取当前年月日
    today = time.strftime("%Y%m%d")
    save_path = f'./lof_premium/{today}.csv'
    filtered_df.to_csv(save_path, index=False, encoding='utf-8-sig')
    logger.info(f"数据已保存到 {save_path}")

if __name__ == "__main__":
    main()