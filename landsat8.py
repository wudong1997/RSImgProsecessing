from osgeo import gdal
import numpy as np


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
        """
        根据不同传感器类型读取对应的数据
        :param sensor_type: 传感器类型，包括OLI、Pan、SWIR
        :return: 图像数组
        """
        for band in sensor_type:
            band_file_name = self.path + '_B' + str(band + 1) + '.tif'
            self.band_file_name.append(band_file_name)

        dataset = gdal.Open(self.band_file_name[0])
        data_type = dataset.GetRasterBand(1).DataType

        # 图像栅格矩阵的行列数
        self.x_size = dataset.RasterXSize
        self.y_size = dataset.RasterYSize

        self.geotransform = dataset.GetGeoTransform()   # 仿射矩阵，左上角像素的大地坐标和像素分辨率
        self.projection = dataset.GetProjection()   # 地图投影

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
        """
        读取envi保存后的遥感影像数据
        调用该函数时创建对象时输入的路径应为完整路径
        :return:
        """
        dataset = gdal.Open(self.path)
        data_type = dataset.GetRasterBand(1).DataType

        self.x_size = dataset.RasterXSize
        self.y_size = dataset.RasterYSize

        self.geotransform = dataset.GetGeoTransform()
        self.projection = dataset.GetProjection()

        bands = dataset.RasterCount

        image = np.zeros((self.y_size, self.x_size, bands), dtype=np.float32)

        for band in range(bands):
            band_img = dataset.GetRasterBand(band + 1)
            image[:, :, band] = band_img.ReadAsArray()

        self.nan_position = np.where(image == 0)  # 将图片中的0替换为nan
        image[self.nan_position] = np.nan

        del dataset
        return image


def write(image, file_path, GeoTrans=None, Project=None, format='ENVI'):
    """
    将图像写至文件
    :param image: 需要保存的图像
    :param file_path: 保存路径
    :param GeoTrans: 坐标系
    :param Project: 投影系
    :param format: 保存格式，默认为ENVI
    """
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


def rad_calibration(img, img_type=None):
    """
    辐射定标函数
    :param img: 输入需要进行辐射定标的图像
    :param img_type: 根据数据类型读取响应的辐射定标参数
    :return: 定标后的图像
    """
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

    elif img_type == 'Pan':
        gain = mult[7]
        offset = add[7]

        cali_img[:, :] = img[:, :] * gain + offset

    elif img_type == 'SWIR':
        bands = img.shape[2]

        for band in range(bands):
            gain = mult[band+9]
            offset = add[band+9]
            cali_img[:, :, band] = img[:, :, band] * gain + offset

    return cali_img

