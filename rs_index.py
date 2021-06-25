def ndvi(img):
    red = img[:, :, 3]
    nir = img[:, :, 4]

    NDVI = (nir - red) / (nir + red)
    return NDVI


def ndwi(img):
    green = img[:, :, 2]
    nir = img[:, :, 4]

    NDWI = (green - nir) / (green + nir)
    return NDWI
