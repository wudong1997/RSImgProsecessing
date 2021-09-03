import numpy as np
import cv2
import pywt


def wavelet(hs_img, hr_img):
    """
    小波变换图像融合
    :param hs_img: 高光谱图像(high-spectrum image)
    :param hr_img: 高分辨率(全色波段)图像(high-resolution image)
    :return: 融合后的图像
    """
    hs_img = hs_img
    hr_img = hr_img

    m, n, bands = hs_img.shape
    M, N, _ = hr_img.shape

    hs_img = cv2.resize(hs_img, (N, M), interpolation=cv2.INTER_CUBIC)
    hr_img = np.squeeze(hr_img)

    pc = pywt.wavedec2(hr_img, 'haar', level=2)

    rec = []
    for i in range(bands):
        temp = pywt.wavedec2(hs_img[:, :, i], 'haar', level=2)
        pc[0] = temp[0]

        temp = pywt.waverec2(pc, 'haar')
        temp = np.expand_dims(temp, -1)

        rec.append(temp)

    wave_res = np.concatenate(rec, axis=-1)

    return wave_res

