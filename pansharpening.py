import numpy as np
from scipy import ndimage
from scipy import signal


def pansharpening(pan_img, multi_img):
    M, N = pan_img.shape
    m, n, C = multi_img.shape

    ratio = int(np.round(M / m))
    print('get sharpening ratio: ', ratio)

    assert int(np.round(M / m)) == int(np.round(N / n))

    u_multi = upsample_interp23(multi_img, ratio)

    print('unsample finished')

    if np.mod(ratio, 2) == 0:
        ratio = ratio + 1

    pan_img = np.tile(pan_img, (1, 1, C))
    pan_img = (pan_img - np.mean(pan_img, axis=(0, 1))) * \
              (np.std(u_multi, axis=(0, 1), ddof=1) / np.std(pan_img, axis=(0, 1), ddof=1)) + np.mean(u_multi, axis=(0, 1))

    kernel = np.ones((ratio, ratio))
    kernel = kernel/np.sum(kernel)

    I_SFIM = np.zeros((M, N, C))

    print('start pansharpening')
    for i in range(C):
        lrpan = signal.convolve2d(pan_img[:, :, i], kernel, mode='same', boundary='wrap')
        I_SFIM[:, :, i] = u_multi[:, :, i] * pan_img[:, :, i]/(lrpan + 1e-8)

    return I_SFIM


def upsample_interp23(image, ratio):
    global I1LRU
    image = np.transpose(image, (2, 0, 1))

    b, r, c = image.shape

    CDF23 = 2 * np.array(
        [0.5, 0.305334091185, 0, -0.072698593239, 0, 0.021809577942, 0, -0.005192756653, 0, 0.000807762146, 0,
         -0.000060081482])
    d = CDF23[::-1]
    CDF23 = np.insert(CDF23, 0, d[:-1])
    BaseCoeff = CDF23

    first = 1
    for z in range(1, np.int64(np.log2(ratio)) + 1):
        I1LRU = np.zeros((b, 2 ** z * r, 2 ** z * c))
        if first:
            I1LRU[:, 1:I1LRU.shape[1]:2, 1:I1LRU.shape[2]:2] = image
            first = 0
        else:
            I1LRU[:, 0:I1LRU.shape[1]:2, 0:I1LRU.shape[2]:2] = image

        for ii in range(0, b):
            t = I1LRU[ii, :, :]
            for j in range(0, t.shape[0]):
                t[j, :] = ndimage.correlate(t[j, :], BaseCoeff, mode='wrap')
            for k in range(0, t.shape[1]):
                t[:, k] = ndimage.correlate(t[:, k], BaseCoeff, mode='wrap')
            I1LRU[ii, :, :] = t
        image = I1LRU

    re_image = np.transpose(I1LRU, (1, 2, 0))

    return re_image
