# !/usr/bin/env python
# -*-coding:utf-8 -*-
# File  : MODIS_Batch.py
# Author:author name
# Time  :2021/11/4 14:19
# Desc  : 批处理MODIS.hdf文件,批量读取tif文件并进行几何校正,定标和投影转换,裁剪
from osgeo import gdal, osr
from osgeo import gdal_array
import os
import time
import numpy as np

'''
批量读取文件夹中hdf格式的modis产品数据并进行几何校正(WGS84)
'''
def readHdfWithGeo(hdfFloder, saveFloder):
    # 获取输入文件夹中所有的文件名
    hdfNameList = os.listdir(hdfFloder)
    # 遍历文件名列表中所有文件
    for i in range(len(hdfNameList)):
        # 获取文件名后缀
        dirname, basename = os.path.split(hdfNameList[i])
        filename, txt = os.path.splitext(basename)
        # 判断文件后缀是否为 .hdf
        if txt == '.hdf':
            hdfPath = hdfFloder + os.sep + hdfNameList[i]
            # 打开hdf文件
            datasets = gdal.Open(hdfPath)
            # 打开子数据集
            dsSubDatasets = datasets.GetSubDatasets()
            # 打开01数据集
            Raster01 = gdal.Open(dsSubDatasets[0][0])
            b = Raster01.ReadAsArray()
            # 获取元数据
            metaData = datasets.GetMetadata()
            # for key, value in metaData.items():
            #   print('{key}:{value}'.format(key = key, value = value))
            # 获取数据时间
            time = metaData['RANGEBEGINNINGDATE']
            # 命名输出完整路径文件名
            outName = saveFloder + os.sep + time + '.tif'
            # 进行几何校正
            geoData = gdal.Warp(outName, Raster01,
                                dstSRS='EPSG:4326', format='GTiff',
                                resampleAlg=gdal.GRA_Bilinear,outputType=gdal.GDT_Float32)
            del geoData
            print('{outname} deal end'.format(outname=outName))

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
'''
批量定标
'''
def cal(tifFloder, saveFloder, scale):
    tifNameList = os.listdir(tifFloder)

    for i in range(len(tifNameList)):

        filename, txt = os.path.splitext(tifNameList[i])

        if txt == '.tif':
            tifPath = tifFloder + os.sep + tifNameList[i]
            array = readTifAsArray(tifPath)
            outName = saveFloder + os.sep + filename + '_cal' + txt
            calData = writeTiff(array[0] / scale, array[1] / scale,
                                array[2], array[3], outName)
            print('{filename} deal end '.format(filename=outName))
            del calData

'''
批量重投影
'''
def reproject(tifFloder, saveFloder, proj4):
    tifNameList = os.listdir(tifFloder)

    srs = osr.SpatialReference()
    srs.ImportFromProj4(proj4)

    for i in range(len(tifNameList)):

        filename, txt = os.path.splitext(tifNameList[i])

        if txt == '.tif':
            tifPath = tifFloder + os.sep + tifNameList[i]
            outName = saveFloder + os.sep + filename + '_rep' + txt
            reproData = gdal.Warp(outName, tifPath, dstSRS=srs,
                                  xRes=1000, yRes=1000,
                                  resampleAlg=gdal.GRA_Bilinear,
                                  outputType=gdal.GDT_Float32)
            print('{filename} deal end '.format(filename=outName))
            del reproData

'''
批量裁剪
'''
def cut(tifFloder, saveFloder, shpFile):
    tifNameList = os.listdir(tifFloder)

    for i in range(len(tifNameList)):

        filename, txt = os.path.splitext(tifNameList[i])

        if txt == '.tif':
            tifPath = tifFloder + os.sep + tifNameList[i]
            outName = saveFloder + os.sep + filename + '_cut' + txt
            cut_ds = gdal.Warp(outName, tifPath,
                               cutlineDSName=shpFile,
                               cropToCutline=True)
            print('{filename} deal end '.format(filename=outName))
            del cut_ds

# START**需要在对应路径中设置文件存储
# 批量转为tif
start = time.time()

readHdfWithGeo(r'E:\MODIS\MCD19A2\20210101_31',
               r'E:\MODIS\MCD19A2\20210101_31\geotif')
end = time.time()
print("完成tif转换")
print('deal spend: {s} s'.format(s=end - start))

# 定标
start = time.time()
cal(r'E:\MODIS\MCD19A2\20210101_31\geotif',
    r'E:\MODIS\MCD19A2\20210101_31\cal', 10000)
end = time.time()
print("完成定标")
print('deal spend: {s} s'.format(s=end - start))

# 重投影
start = time.time()
reproject(r'E:\MODIS\MCD19A2\20210101_31\cal',
          r'E:\MODIS\MCD19A2\20210101_31\albers',
          '+proj=aea +lat_0=0 +lon_0=105 +lat_1=25 +lat_2=47 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs')
end = time.time()
print("完成重投影")
print('deal spend: {s} s'.format(s=end - start))

# 裁剪
start = time.time()
cut(r'E:\MODIS\MCD19A2\20210101_31\albers',
    r'E:\MODIS\MCD19A2\20210101_31\warp',
    r'E:\矢量\山东省\山东省_省界.shp')
end = time.time()
print("完成裁剪")
print('deal spend: {s} s'.format(s=end - start))
