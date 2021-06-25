import numpy as np
import numpy.ma

import readRSImg
import rs_index
import show_pic
import pca


if __name__ == '__main__':

    ls8 = readRSImg.landsat8()
    img = ls8.read_envi(path='E:\\RSImg\\pca_test.tif')
    ndwi_img = rs_index.ndwi(img)

    mask = np.full((img.shape[0], img.shape[1], img.shape[2]), True)

    band_mask = ndwi_img > 0.1
    for i in range(img.shape[2]):
        mask[:, :, i] = band_mask

    img = numpy.ma.array(img, mask=mask)

    out = pca.pca(img)

    show_pic.show_single_band(out[:, :, 1])


