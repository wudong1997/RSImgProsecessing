import numpy
import cv2
from sklearn.decomposition import PCA
from hist_matching import hist_match


def PCA_pansharpening(hs_img, hr_img):
    """
    PCA法图像融合
    :param hs_img: 高光谱图像(high-spectrum image)
    :param hr_img: 高分辨率(全色波段)图像(high-resolution image)
    :return: 融合后的图像
    """
    hs_img = hs_img
    hr_img = hr_img

    hs_img = cv2.resize(hs_img, (hr_img.shape[1], hr_img.shape[0]), interpolation=cv2.INTER_CUBIC)

    m, n, bands = hs_img.shape
    M, N, _ = hr_img.shape

    assert int(numpy.round(M / m)) == int(numpy.round(N / n))

    p = PCA(n_components=bands)
    # fit_transform(self, X, y=None): X:一个格式为(样本数, 特征数)的数组
    # 用于sklearn数据预处理, 可以理解为fit()与transform()的结合
    # fit(): 求得训练集X的均值，方差，最大值，最小值等这些训练集X固有的属性。可以理解为一个训练过程
    # transform(): 在fit()的基础上，进行标准化，降维，归一化等操作
    pca_hs = p.fit_transform(numpy.reshape(hs_img, (M * N, bands)))

    pca_hs = numpy.reshape(pca_hs, (M, N, bands))
    I = pca_hs[:, :, 0]

    # hr_img = (hr_img - numpy.mean(hr_img)) * numpy.std(I, ddof=1) / (numpy.std(hr_img, ddof=1)) + numpy.mean(I)
    hr_img = hist_match(hr_img, I)
    pca_hs[:, :, 0] = hr_img[:, :, 0]

    # PCA 逆变换
    I_PCA = p.inverse_transform(pca_hs)

    # PCA去中心化
    I_PCA = I_PCA - numpy.mean(I_PCA, axis=(0, 1)) + numpy.mean(hs_img)

    return I_PCA
