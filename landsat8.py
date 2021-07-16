from osgeo import gdal
import numpy as np
import show_pic


class landsat8(object):
    def __init__(self, path):
        self.path = path
        self.band_file_name = []
        self.nan_position = []

        self.projection = None
        self.geotransform = None

        self.x_size = 0
        self.y_size = 0

        self.OLI = np.arange(0, 7, 1)
        self.Pan = np.arange(7, 8, 1)
        self.SWIR = np.arange(9, 11, 1)

    def read(self, sensor_type):
        for band in sensor_type:
            band_file_name = self.path + '_B' + str(band + 1) + '.tif'
            self.band_file_name.append(band_file_name)

        dataset = gdal.Open(self.band_file_name[0])
        data_type = dataset.GetRasterBand(1).DataType

        self.x_size = dataset.RasterXSize
        self.y_size = dataset.RasterYSize

        self.geotransform = dataset.GetGeoTransform()
        self.projection = dataset.GetProjection()

        image = np.zeros((self.y_size, self.x_size, len(sensor_type)), dtype=np.float32)

        for band in range(len(sensor_type)):
            dataset = gdal.Open(self.band_file_name[band])
            band_image = dataset.GetRasterBand(1)
            image[:, :, band] = band_image.ReadAsArray()

        self.nan_position = np.where(image == 0)  # 将图片中的0替换为nan
        image[self.nan_position] = np.nan
        del dataset

        return image

    def read_OLI(self):
        return self.read(self.OLI)

    def read_Pan(self):
        return self.read(self.Pan)

    def read_SWIR(self):
        return self.read(self.SWIR)

    def read_envi(self):
        dataset = gdal.Open(self.path)
        data_type = dataset.GetRasterBand(1).DataType

        self.x_size = dataset.RasterXSize
        self.y_size = dataset.RasterYSize

        self.geotransform = dataset.GetGeoTransform()
        self.projection = dataset.GetProjection()

        self.bands = dataset.RasterCount

        image = np.zeros((self.y_size, self.x_size, self.bands), dtype=np.float32)

        for band in range(self.bands):
            band_img = dataset.GetRasterBand(band + 1)
            image[:, :, band] = band_img.ReadAsArray()

        self.nan_position = np.where(image == 0)  # 将图片中的0替换为nan
        image[self.nan_position] = np.nan

        del dataset
        return image


def write(image, file_path, GeoTrans=None, Project=None, format='ENVI'):
    if len(image.shape) == 3:
        bands = image.shape[2]

        driver = gdal.GetDriverByName(format)
        new_dataset = driver.Create(file_path, image.shape[1], image.shape[0], bands, gdal.GDT_Float32)

        new_dataset.SetGeoTransform(GeoTrans)
        new_dataset.SetProjection(Project)

        for band in range(bands):
            new_dataset.GetRasterBand(band + 1).WriteArray(image[:, :, band])
            new_dataset.FlushCache()

    else:
        driver = gdal.GetDriverByName(format)
        new_dataset = driver.Create(file_path, image.shape[1], image.shape[0], 1, gdal.GDT_Float32)

        new_dataset.SetGeoTransform(GeoTrans)
        new_dataset.SetProjection(Project)

        new_dataset.GetRasterBand(1).WriteArray(image[:, :])
        new_dataset.FlushCache()

    del new_dataset


def rad_calibration(self, img, img_type=None):
    import readMTL
    mtl = readMTL.mtl()
    mtl.read_mtl()

    mult = mtl.mult
    add = mtl.add

    cali_img = np.zeros_like(img, dtype=np.float32)

    if img_type is None:
        bands = img.shape[2]

        for band in range(bands):
            gain = mult[band]
            offset = add[band]
            cali_img[:, :, band] = img[:, :, band] * gain + offset

    elif img_type is 'Pan':
        gain = mult[7]
        offset = add[7]

        cali_img[:, :] = img[:, :] * gain + offset

    elif img_type is 'SWIR':
        bands = img.shape[2]

        for band in range(bands):
            gain = mult[band+9]
            offset = add[band+9]
            cali_img[:, :, band] = img[:, :, band] * gain + offset

    return cali_img

