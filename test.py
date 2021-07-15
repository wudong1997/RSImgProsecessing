import cv2
import readRSImg
import rs_index
import show_pic


if __name__ == '__main__':

    ls8 = readRSImg.landsat8()
    img = ls8.read_envi(path='E:\\RSImg\\high_img')

    print(img.shape)

