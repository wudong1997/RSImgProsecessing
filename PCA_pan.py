import numpy
import cv2
from sklearn.decomposition import PCA


def PCA_pansharpening(hs_img, hr_img):
    hs_img = hs_img
    hr_img = hr_img

    hs_img = cv2.resize(hs_img, (hr_img.shape[1], hr_img.shape[0]), interpolation=cv2.INTER_CUBIC)

    m, n, bands = hs_img.shape
    M, N, _ = hr_img.shape

    assert int(numpy.round(M / m)) == int(numpy.round(N / n))

    p = PCA(n_components=bands)
    pca_hs = p.fit_transform(numpy.reshape(hs_img, (M * N, bands)))

    pca_hs = numpy.reshape(pca_hs, (M, N, bands))
    I = pca_hs[:, :, 0]

    hr_img = (hr_img - numpy.mean(hr_img)) * numpy.std(I, ddof=1) / (numpy.std(hr_img, ddof=1)) + numpy.mean(I)
    pca_hs[:, :, 0] = hr_img[:, :, 0]

    I_PCA = p.inverse_transform(pca_hs)

    I_PCA = I_PCA - numpy.mean(I_PCA, axis=(0, 1)) + numpy.mean(hs_img)

    return I_PCA
