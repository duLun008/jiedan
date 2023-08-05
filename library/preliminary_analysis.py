'''
Description: 
Autor: dulun
Date: 2023-07-13 14:29:05
LastEditors: dulun
LastEditTime: 2023-07-13 14:41:02
'''
import pandas as pd

# 读取Excel文件
file_path = 'data/图书借还2017.xlsx'
df = pd.read_excel(file_path)

# 查看前几行数据
print(df.head())

# 查看表格信息
print(df.info())

# 查看统计摘要
print(df.describe())
