import readRSImg
import numpy as np
import show_pic
import AtmosphricCalibration as ac


ls8 = readRSImg.landsat8()

img, pan_img = ls8.rad_calibration()
index = np.array([3, 2, 1])

multi_img = img[:, :, 0:7]
ls8.write(multi_img, 'E:\\RSImg\\rad_cali')

# multi_img = ac.toa_cal(multi_img, 7, img_type='Multi')
# ls8.write(multi_img, 'E:\\RSImg\\toa', 7)

multi_img = ac.atmos_cla(multi_img)
show_pic.show_colorful_img(multi_img, index)
ls8.write(multi_img, 'E:\\RSImg\\atmos')
