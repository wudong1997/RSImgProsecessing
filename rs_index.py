import matplotlib.pyplot as plt
import numpy as np
import show_pic
import readRSImg
import cv2


def ndvi(img):
    red = img[:, :, 3]
    nir = img[:, :, 4]

    NDVI = (nir - red) / (nir + red)
    return NDVI


def ndwi(img):
    green = img[:, :, 2]
    nir = img[:, :, 4]

    NDWI = (green - nir) / (green + nir)
    return NDWI


def otsu(gray_img):
    ret1, th1 = cv2.threshold(gray_img, thresh=0.1, maxval=1, type=cv2.THRESH_BINARY)
    show_pic.show_single_band(gray_img)
    show_pic.draw_hist(gray_img)
    plt.figure(dpi=300)
    plt.show()


ls8 = readRSImg.landsat8()
img = ls8.read_envi('E:\\RSImg\\atmos')
ndwi_img = ndvi(img)

otsu(ndwi_img)
