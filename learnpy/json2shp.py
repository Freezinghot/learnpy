
# !/usr/bin/env python
# -*-coding:utf-8 -*-
# File  : json2shp.py
# Author:author name
# Time  :2021/10/19 9:39
# Desc  :
# GeoJson to shp
import geopandas as gpd
#data = gpd.read_file('E:\\Haohai\\淄博\\370301.json')
#data.to_file('E:\\Haohai\\淄博\\370301.shp', driver='ESRI Shapefile', encoding='utf-8')
data = gpd.read_file('E:\\Haohai\\淄博\\淄博市全部_Polygon.shp')
data.to_file("E:\\Haohai\\淄博\\370300.json", driver='GeoJSON', encoding="utf-8")