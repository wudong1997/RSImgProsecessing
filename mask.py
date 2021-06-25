import numpy as np
import numpy.ma


def mask_def(mask_img, threshold, masked_value=None):
    """
    通过mask_img与阈值生成图像掩膜
    :param mask_img: 用于生成mask的图像
    :param threshold: 阈值
    :param masked_value: 1为掩膜大于阈值的区域， 0为掩膜小于阈值的区域
    :return: 生成的掩膜2维矩阵
    """
    mask_matrix = None

    try:
        if masked_value == 1:
            mask_matrix = mask_img > threshold
        elif masked_value == 0:
            mask_matrix = mask_img < threshold
    except Exception as e:
        print('输入了除1和0以外的其他值.')

    return mask_matrix


def do_mask(base_img, mask_matrix):
    """
    对遥感影像进行掩膜操作
    :param base_img:原图像
    :param mask_matrix:掩膜2维矩阵
    :return: 返回掩膜后的图像
    """
    m, n, k = base_img.shape
    mask = np.full((m, n, k), True)

    for i in range(k):
        mask[:, :, i] = mask_matrix

    return numpy.ma.array(base_img, mask=mask)
