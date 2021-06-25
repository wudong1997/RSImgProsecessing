import numpy as np
import show_pic as pic


def normalize(matrix):
    """
    对矩阵进行去中心化运算
    :param matrix:
    :return: 中心化后的矩阵
    """
    m, n = np.shape(matrix)
    aver = np.mean(matrix)
    aver_matrix = np.tile(aver, (m, 1))
    XNorm = matrix - aver_matrix

    return XNorm


def pca(image):
    """
    对遥感影像进行主成分分析
    :param image: 输入遥感影响
    :return: 输出主成分分析变换后的遥感影像
    """
    m, n, bands = image.shape
    data = []
    for band in range(bands):
        image[:, :, band] = pic.gray_process(image[:, :, band])
        arr = image[:, :, band].flatten()
        data.append(arr)

    data = np.mat(data)
    data = normalize(data)

    covX = np.cov(data) # 计算协方差矩阵
    featValue, featVec = np.linalg.eig(covX) # 计算协方差矩阵的特征值和特征向量
    value_index = np.argsort(-featValue)  # 将特征值由大到小排列

    reconData = np.dot(data.T, featVec)
    pca_img = np.zeros((m, n, bands), dtype=np.float32)

    for i in value_index:
        pca_img[:, :, i] = reconData[:, i].reshape(m, n)

    return pca_img


def KTTransformation(image):
    m, n, bands = image.shape

    blue = image[:, :, 1]
    green = image[:, :, 2]
    red = image[:, :, 3]

    nir = image[:, :, 4]
    swir1 = image[:, :, 5]
    swir2 = image[:, :, 6]

    bright_part = 0.352 * blue + 0.3899 * green + 0.3825 * red + 0.6985 * nir + 0.2343 * swir1 + 0.1867 * swir2
    green_part = -0.3301 * blue - 0.3455 * green - 0.4508 * red + 0.6970 * nir - 0.0448 * swir1 - 0.284 * swir2
    water_part = 0.2651 * blue + 0.2367 * green + 0.1296 * red + 0.059 * nir - 0.7506 * swir1 - 0.5386 * swir2

    KT_img = np.zeros((m, n, 3), dtype=np.float32)
    KT_img[:, :, 0] = bright_part
    KT_img[:, :, 1] = green_part
    KT_img[:, :, 2] = water_part

    return KT_img
