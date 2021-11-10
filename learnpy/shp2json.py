# -*- coding: utf-8 -*-
# @File  : shp2json.py
# @Author: Freezinghot
# @Date  : 2021/3/4
# @Desc  : shp转json
# shp to GeoJson
import geopandas as gpd
import glob


def shp2json(data_name, json_Path):
    data = gpd.read_file(data_name, encoding='utf-8')   # encoding=gbk/utf-8
    data.to_file(json_Path+"\\"+(data_name.split("\\")[-1]).split(".")[0]+".json", driver='GeoJSON', encoding="utf-8")


if __name__ == "__main__":
    shp_Path = "C:\\Users\\63441\\Desktop\\shp"      # shp文件存储路径
    json_Path = "C:\\Users\\63441\\Desktop\\shp\\json"   # json文件存储路径
    # 下面开始数据处理
    # 读取所有shp数据
    data_list = glob.glob(shp_Path + "\\*.shp")
    for i in range(len(data_list)):
        data_name = data_list[i]
        shp2json(data_name, json_Path)
        print(data_name + "-----转换成功")
    print("----转换结束----")

