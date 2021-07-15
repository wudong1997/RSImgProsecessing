from osgeo import gdal
import numpy as np

import show_pic
import show_pic as pic


class landsat8(object):

    def __init__(self):
        self.pub_path = 'E:\\RSImg\\LC08_L1TP_119039_20201213_20210313_01_T1\\LC08_L1TP_119039_20201213_20210313_01_T1'
        self.bands = 11
        self.band_file_name = []
        self.nan_position = []

        self.projection = None
        self.geotransform = None

        self.x_size = 0
        self.y_size = 0

    def read(self):
        for band in range(self.bands):
            band_file_name = self.pub_path + '_B' + str(band + 1) + '.tif'
            self.band_file_name.append(band_file_name)

        dataset = gdal.Open(self.band_file_name[0])
        data_type = dataset.GetRasterBand(1).DataType

        self.x_size = dataset.RasterXSize
        self.y_size = dataset.RasterYSize

        self.geotransform = dataset.GetGeoTransform()
        self.projection = dataset.GetProjection()

        image = np.zeros((self.y_size, self.x_size, self.bands), dtype=np.float32)

        for band in range(self.bands):
            if band == 7:
                continue
            else:
                dataset = gdal.Open(self.band_file_name[band])
                band_image = dataset.GetRasterBand(1)
                image[:, :, band] = band_image.ReadAsArray()

        self.nan_position = np.where(image == 0)  # 将图片中的0替换为nan
        image[self.nan_position] = np.nan

        # 读取全色波段数据
        dataset_pan = gdal.Open(self.band_file_name[7])
        image_pan = np.zeros((dataset_pan.RasterYSize, dataset_pan.RasterXSize), dtype=np.float32)
        pan_image = dataset_pan.GetRasterBand(1)
        image_pan[:, :] = pan_image.ReadAsArray()

        self.nan_position = np.where(image_pan == 0)
        image_pan[self.nan_position] = np.nan

        del dataset
        return image, image_pan

    def read_envi(self, path=''):
        dataset = gdal.Open(path)
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

    def write(self, image, file_name, format='ENVI'):
        bands = image.shape[2]

        driver = gdal.GetDriverByName(format)
        new_dataset = driver.Create(file_name, image.shape[1], image.shape[0], bands, gdal.GDT_Float32)

        new_dataset.SetGeoTransform(self.geotransform)
        new_dataset.SetProjection(self.projection)

        for band in range(bands):
            new_dataset.GetRasterBand(band + 1).WriteArray(image[:, :, band])
            new_dataset.FlushCache()

        del new_dataset

    def write_single_band(self, image, file_name, format='ENVI'):
        driver = gdal.GetDriverByName(format)
        new_dataset = driver.Create(file_name, self.x_size, self.y_size, 1, gdal.GDT_Float32)

        new_dataset.SetGeoTransform(self.geotransform)
        new_dataset.SetProjection(self.projection)

        new_dataset.GetRasterBand(1).WriteArray(image[:, :])
        new_dataset.FlushCache()

        del new_dataset

    def rad_calibration(self):
        img, img_pan = self.read()

        import readMTL
        mtl = readMTL.mtl()
        mtl.read_mtl()

        mult = mtl.mult
        add = mtl.add

        cali_img = np.zeros_like(img, dtype=np.float32)
        cali_img_pan = np.zeros_like(img_pan, dtype=np.float32)

        for band in range(self.bands):
            gain = mult[band]
            offset = add[band]
            cali_img[:, :, band] = img[:, :, band] * gain + offset
        cali_img_pan[:, :] = img_pan[:, :] * mult[7] + add[7]

        return cali_img, cali_img_pan
