import cv2
import numpy as np
import readRSImg
import show_pic


ls8 = readRSImg.landsat8()
img, pan_img = ls8.read()

print(pan_img.shape)
band_index = [3, 2, 1]

RGB_img = img[:, :, band_index].astype(np.float32)
RGB_img = cv2.resize(RGB_img, (pan_img.shape[1], pan_img.shape[0]), interpolation=cv2.INTER_CUBIC)


BGR_img = cv2.cvtColor(RGB_img, cv2.COLOR_RGB2BGR)
HSV_img = cv2.cvtColor(BGR_img, cv2.COLOR_BGR2HSV)

H, S, V = cv2.split(HSV_img)

HSV_img = cv2.merge((H, S, pan_img))

RGB_img = cv2.cvtColor(HSV_img, cv2.COLOR_HSV2RGB)
# show_pic.show_colorful_img(RGB_img, [0, 1, 2])

ls8.write(RGB_img,'E:\\RSImg\\high_img')

