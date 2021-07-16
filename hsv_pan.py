import cv2
import numpy as np
from landsat8 import landsat8, write
import show_pic

path = 'E:\\RSImg\\LC08_L1TP_119039_20201213_20210313_01_T1\\LC08_L1TP_119039_20201213_20210313_01_T1'
dataset_OLI = landsat8(path)
img = dataset_OLI.read_OLI()

dataset_Pan = landsat8(path)
pan_img = dataset_Pan.read_Pan()

band_index = [3, 2, 1]


def hsv_pan(low_img, high_img, index=None):
    """
    HSV图像融合
    :param low_img: 低分辨率高光谱图像
    :param high_img: 过分辨率全色波段图像
    :param index: 进行融合的三个波段，
                HSV变换只能针对三个通道的图像进行变换
    """
    if index is None:
        index = [0, 1, 2]

    RGB_img = img[:, :, band_index].astype(np.float32)
    RGB_img = cv2.resize(RGB_img, (pan_img.shape[1], pan_img.shape[0]), interpolation=cv2.INTER_CUBIC)

    BGR_img = cv2.cvtColor(RGB_img, cv2.COLOR_RGB2BGR)
    HSV_img = cv2.cvtColor(BGR_img, cv2.COLOR_BGR2HSV)

    H, S, V = cv2.split(HSV_img)

    HSV_img = cv2.merge((H, S, pan_img))

    RGB_img = cv2.cvtColor(HSV_img, cv2.COLOR_HSV2RGB)
    # show_pic.show_colorful_img(RGB_img, [0, 1, 2])
    # write(RGB_img, 'E:\\RSImg\\high_img', GeoTrans=dataset_Pan.geotransform, Project=dataset_Pan.projection)

    return RGB_img

