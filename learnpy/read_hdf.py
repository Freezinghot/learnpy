# !/usr/bin/env python
# -*-coding:utf-8 -*-
# File  : read_hdf.py
# Author:author name
# Time  :2021/11/1 16:08
# Desc  :
#  gdal打开hdf数据集
import gdal, osr
import numpy as np
import os
#  gdal打开hdf数据集
datasets = gdal.Open(r"E:\MODIS\MCD19A2\20210101_31\MCD19A2.A2021001.h27v05.006.2021003031411.hdf")

#  获取hdf中的子数据集
SubDatasets = datasets.GetSubDatasets()
#  获取子数据集的个数
SubDatasetsNum =  len(datasets.GetSubDatasets())
#  输出各子数据集的信息
print("子数据集一共有{0}个: ".format(SubDatasetsNum))
for i in range(SubDatasetsNum):
    print(datasets.GetSubDatasets()[i])

#  获取hdf中的元数据
Metadata = datasets.GetMetadata()
#  获取元数据的个数
MetadataNum = len(Metadata)
#  输出各子数据集的信息
print("元数据一共有{0}个: ".format(MetadataNum))
for key,value in Metadata.items():
    print('{key}:{value}'.format(key = key, value = value))