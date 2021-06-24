import numpy as np
import readRSImg
import show_pic
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
    bands = image.shape[2]
    data = []
    for band in range(bands):
        image[:, :, band] = pic.gray_process(image[:, :, band])
        arr = image[:, :, band].flatten()
        data.append(arr)

    data = np.mat(data)
    data = normalize(data)

    covX = np.cov(data)
    featValue, featVec = np.linalg.eig(covX)
    value_index = np.argsort(-featValue)  # 将特征值由大到小排列

    reconData = np.dot(data.T, featVec)

    return reconData, value_index


def KTTransformation(image):
    blue = image[:, :, 1]
    green = image[:, :, 2]
    red = image[:, :, 3]

    nir = image[:, :, 4]
    swir1 = image[:, :, 5]
    swir2 = image[:, :, 6]

    bright_part = 0.352 * blue + 0.3899 * green + 0.3825 * red + 0.6985 * nir + 0.2343 * swir1 + 0.1867 * swir2
    green_part = -0.3301 * blue - 0.3455 * green - 0.4508 * red + 0.6970 * nir - 0.0448 * swir1 - 0.284 * swir2
    water_part = 0.2651 * blue + 0.2367 * green + 0.1296 * red + 0.059 * nir - 0.7506 * swir1 - 0.5386 * swir2

    show_pic.show_single_band(bright_part)
    show_pic.show_single_band(green_part)
    show_pic.show_single_band(water_part)


ls8 = readRSImg.landsat8()
# img = ls8.read_envi(path='E:\\RSImg\\pca_test.tif')
    #
    # out, index = pca(img)
    # m, n, k = img.shape
    #
    # pca_img = np.zeros((m, n, k), dtype=np.float32)
    # for i in index:
    #     pca_img[:, :, i] = out[:, i].reshape(m, n)
    #
    # pic.show_colorful_img(pca_img, [0, 1, 2])
img = ls8.read_envi(path='E:\\RSImg\\atmos')

KTTransformation(img)
