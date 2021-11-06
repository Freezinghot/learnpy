# !/usr/bin/env python
# -*-coding:utf-8 -*-
# File  : bandmath.py
# Author:author name
# Time  :2021/11/5 10:38
# Desc  :MODIS——tif波段计算完成版
from osgeo import gdal, osr
from osgeo import gdal_array
import os
import time
import numpy as np
'''
批量读取tif文件(适用于多波段tif文件)存入数组,并进行定标
'''
def readTifAsArray(tifPath):
    dataset = gdal.Open(tifPath)
    #dataarray = dataset.ReadAsArray()
    if dataset == None:
        print(tifPath + "文件错误")
        return tifPath

    image_datatype = dataset.GetRasterBand(1).DataType
    row = dataset.RasterYSize
    col = dataset.RasterXSize
    nb = dataset.RasterCount
    proj = dataset.GetProjection()
    gt = dataset.GetGeoTransform()

    if nb != 1:
        array = np.zeros((nb, row, col),
                         dtype=gdal_array.GDALTypeCodeToNumericTypeCode(
                             image_datatype))

        for b in range(nb):
            band = dataset.GetRasterBand(b + 1)
            nan = band.GetNoDataValue()
            array[b, :, :] = band.ReadAsArray()

    else:
        array = np.zeros((row, col),
                         dtype=gdal_array.GDALTypeCodeToNumericTypeCode(
                             image_datatype))
        band = dataset.GetRasterBand(1)
        nan = band.GetNoDataValue()
        array = band.ReadAsArray()
    return array, nan, gt, proj

'''  
写出tif文件
'''
def writeTiff(im_data, nan, im_geotrans, im_proj, path):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    elif len(im_data.shape) == 2:
        im_data = np.array([im_data])
        im_bands, im_height, im_width = im_data.shape

    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype)

    if (dataset != None):
        dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        dataset.SetProjection(im_proj)  # 写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
        outBand = dataset.GetRasterBand(i + 1)
        outBand.FlushCache()
        outBand.SetNoDataValue(nan)
    del dataset


def monthlyMean(tifFloder, saveFloder):
    tifNameList = os.listdir(tifFloder)
    array, nan, gt, proj = readTifAsArray(tifFloder+os.sep+tifNameList[0])
    im_bands, im_height, im_width = array.shape

    layerlist = np.empty((im_bands, im_height, im_width), dtype=np.float32)
    for i in range(len(tifNameList)):
        filename, txt = os.path.splitext(tifNameList[i])
        if txt == '.tif':
            tifPath = tifFloder + os.sep + tifNameList[i]
            array = np.array(readTifAsArray(tifPath))[0]

            if not layerlist.all():
                #layerlist = np.array([layerlist, array])
                layerlist = np.concatenate((layerlist,array), axis=0)

    band,col,row = np.shape(layerlist)
    pix = np.empty((band), dtype=np.float32)
    pixmean = np.zeros((col,row))
    for j in range(col):
        for k in range(row):
            pix = layerlist[:,j, k]
            mark = []
            for l in range(len(pix)):
                #pl = round(pix[l], 4)
                if (pix[l] == np.float32(nan)) or (pix[l] == 0.0):
                    mark.append(l)
            pix = np.delete(pix, mark)
            if len(pix):        # 判断是否为空
                pixmean[j, k] = np.mean(pix)
        print(str(round(j/col, 2)*100)+'% finished')
    outName = saveFloder + os.sep + 'monthly_mean.tif'
    calData = writeTiff(pixmean, nan, gt, proj, outName)
    print('{filename} deal end '.format(filename=outName))
    del calData

start = time.time()
print("START")
monthlyMean(r'E:\MODIS\MCD19A2\test\warp',
               r'E:\MODIS\MCD19A2\test\mean')
end = time.time()
print('END. Spend time: {s} s'.format(s=end - start))
