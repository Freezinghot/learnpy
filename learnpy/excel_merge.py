# !/usr/bin/env python
# -*-coding:utf-8 -*-
# File  : excel_merge.py
# Author:author name
# Time  :2021/11/2 17:03
# Desc  :合并两个表里同样名称的站点
import pandas as pd
# 从excel导入表
A = pd.read_excel('E:\\MODIS\\MCD19A2\\AOD_Max.xls', sheet_name='AOD_Max') # 读取 excel
B = pd.read_excel('E:\\MODIS\\MCD19A2\\AOD_Max.xls', sheet_name='Station_Max', index_col=0)
# 去除重复行
X = A.drop_duplicates(subset=['Sta_ID'])
# 更换索引列
X = X.set_index('Sta_ID')
# 按索引列合并
merge = pd.concat([X, B], axis=1, join='inner')
print(merge)
# pandas表存出
writer = pd.ExcelWriter('E:\\MODIS\\MCD19A2\\AOD_Sta.xls')
merge.to_excel(writer,float_format='%.5f')
writer.save()
