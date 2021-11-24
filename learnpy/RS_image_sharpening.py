# !/usr/bin/env python
# -*-coding:utf-8 -*-
# File  : RS_image_sharpening.py
# Author:author name
# Time  :2021/11/20 14:44
# Desc  : 遥感影像增强
import numpy as np
import gdal
import math
import matplotlib.pyplot as plt
import cv2
from skimage import filters
from skimage.morphology import disk

#  读取tif数据集
def readTif(fileName, xoff=0, yoff=0, data_width=0, data_height=0):
    dataset = gdal.Open(fileName)
    if dataset == None:
        print(fileName + "文件无法打开")
    #  栅格矩阵的列数
    width = dataset.RasterXSize
    #  栅格矩阵的行数
    height = dataset.RasterYSize
    #  波段数
    bands = dataset.RasterCount
    #  获取数据
    if (data_width == 0 and data_height == 0):
        data_width = width
        data_height = height
    data = dataset.ReadAsArray(xoff, yoff, data_width, data_height)
    #  获取仿射矩阵信息
    geotrans = dataset.GetGeoTransform()
    #  获取投影信息
    proj = dataset.GetProjection()
    return width, height, bands, data, geotrans, proj


#  保存tif文件函数
def writeTiff(im_data, im_geotrans, im_proj, path):
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
    # 创建文件
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype)
    if (dataset != None):
        dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        dataset.SetProjection(im_proj)  # 写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
    del dataset

# 对单通道图像增强
def imageSharpening(data, width, height, A):
    data_sharp = np.zeros((width, height))
    for i in range(width):
        for j in range(height):
            data_sharp[i,j] = A * (math.log(data[i,j]+1))
            if data_sharp[i,j] < 0:
                data_sharp[i,j] = 0
            elif data_sharp[i,j] > 255:
                data_sharp[i,j] = 255
    return data_sharp

# 直方图均衡
def equalization_histogram(img):
    new_img = np.zeros([bands, width, height], np.uint8)
    for i in range(bands):
        # 计算原图灰度直方图
        band = np.array(img[i], dtype=np.uint8)
        histogram = {}
        for j in range(band.shape[0]):
            for k in range(band.shape[1]):
                pix = band[j][k]
                if pix in histogram:
                    histogram[pix] += 1
                else:
                    histogram[pix] = 1

        sorted_histogram = {}  # 建立排好序的映射表
        sorted_list = sorted(histogram)  # 根据灰度值进行从低至高的排序
        # 生成直方图统计
        for j in range(len(sorted_list)):
            sorted_histogram[sorted_list[j]] = histogram[sorted_list[j]]

        pr = {}  # 建立概率分布映射表

        for j in sorted_histogram.keys():
            pr[j] = sorted_histogram[j] / (band.shape[0] * band.shape[1])

        tmp = 0
        for m in pr.keys():
            tmp += pr[m]
            pr[m] = max(sorted_histogram) * tmp

        for k in range(band.shape[0]):
            for l in range(band.shape[1]):
                new_img[i][k][l] = pr[band[k][l]]

    return new_img

# 计算灰度直方图
def GrayHist(img):
    height, width = img.shape[:2]
    grayHist = np.zeros([256], np.uint64)
    for i in range(height):
        for j in range(width):
            grayHist[img[i][j]] += 1
    return grayHist

# gamma变换
def gama_transfer(img,power1):
    out_img = np.zeros([bands, width, height],np.uint8)
    for i in range(bands):
        # 计算原图灰度直方图
        band = np.array(data[i], dtype=np.uint8)
        img = 255*np.power(band/255,power1)
        img = np.around(img)
        img[img>255] = 255
        out_img[i] = img.astype(np.uint8)
    return out_img
# 中值滤波
def median_filter(img, disk):
    out_img = np.zeros([bands, width, height],np.uint8)
    for i in range(bands):
        # 计算原图灰度直方图
        band = np.array(img[i], dtype=np.uint8)
        img[i] = filters.median(band,disk)
        img[i] = np.around(img[i])
        out_img[i] = img[i].astype(np.uint8)
    img[img > 255] = 255
    return out_img
# sobel算子
def sobel_transfer(img):
    out_img = np.zeros([bands, width, height], np.uint8)
    for i in range(bands):
        edges = filters.sobel(img[i])
        out_img[i] = edges.astype(np.uint8)
    return out_img
# 高斯滤波
def gaussian_transfer(img, sigma):
    out_img = np.zeros([bands, width, height], np.uint8)
    for i in range(bands):
        newimg = filters.gaussian_filter(img,sigma=0.4)
        out_img[i] = newimg.astype(np.uint8)
    return out_img

fileName = 'E:\\GF2\\GF2_20190120_PMS_Urban.tif'
SaveName = 'E:\\GF2\\GF2_20190120_PMS_Urban_Histogram.tif'
width, height, bands, data, geotrans, proj = readTif(fileName)
print("Image loaded,calculating...")
# gamma变换
#data_gamma = gama_transfer(data, 2)
#data_gaussian = gaussian_transfer(data, 0.5)
# 直方图均衡化
newdata = equalization_histogram(data)
# 中值滤波
#data_median = median_filter(data, disk(3))  # (图像数据，滤波器核大小)

writeTiff(newdata, geotrans, proj, SaveName)
print("Finihed")

