# Remote Sensing Image Processing
基于python的遥感数字影像处理

## Conda


## python GDAL库
### 安装  
GDAL(Geospatial Data Abstraction Library)是一个用于栅格数据操作的库，是开源地理空间基金会（Open Source Geospatial Foundation，OSGeo）的一个项目  
GDAL是一个操作各种栅格地理数据格式的库。包括读取、写入、转换、处理各种栅格数据格式。  
GDAL是基于C/C++开发的，直接使用pip安装有时会有问题，可从https://gdal.org/download.html 网站上下载GDAL的wheel文件进行安装。  
或使用Conda进行安装。  
```
conda install -c conda-forge gdal
```
### 读取文件
```
    def read(self):
        """
        根据不同传感器类型读取对应的数据
        :return: 图像数组
        """

        dataset = gdal.Open(self.path)
        data_type = dataset.GetRasterBand(1).DataType

        # 图像栅格矩阵的行列数
        self.x_size = dataset.RasterXSize
        self.y_size = dataset.RasterYSize

        self.geotransform = dataset.GetGeoTransform()   # 仿射矩阵，左上角像素的大地坐标和像素分辨率
        self.projection = dataset.GetProjection()   # 地图投影

        image = np.zeros((self.y_size, self.x_size, len(sensor_type)), dtype=np.float32)
        
        for band in range(bands):
            band_img = dataset.GetRasterBand(band + 1)
            image[:, :, band] = band_img.ReadAsArray()

        self.nan_position = np.where(image == 0)  # 将图片中的0替换为nan
        image[self.nan_position] = np.nan
        del dataset

        return image
```
### 将图像写入文件
```
def write(image, file_path, GeoTrans=None, Project=None, format='ENVI'):
    """
    将图像写至文件
    :param image: 需要保存的图像
    :param file_path: 保存路径
    :param GeoTrans: 坐标系
    :param Project: 投影系
    :param format: 保存格式，默认为ENVI
    """

    driver = gdal.GetDriverByName(format)   # 文件格式 
    new_dataset = driver.Create(file_path, image.shape[1], image.shape[0], image.shape[2], gdal.GDT_Float32)

    new_dataset.SetGeoTransform(GeoTrans)   # 写入仿射变换参数
    new_dataset.SetProjection(Project)  # 写入投影

    for band in range(bands):
        new_dataset.GetRasterBand(band + 1).WriteArray(image[:, :, band])   # 写入数组数据
        new_dataset.FlushCache()
```
### 波段计算
```
def ndvi(img):
    red = img[:, :, 3]
    nir = img[:, :, 4]

    NDVI = (nir - red) / (nir + red)
    return NDVI
```
## python大气校正模块 py6s库
Py6S 是通过 Python 对 the Second Simulation of the Satellite Signal in the Solar Spectrum (6S) 大气传输模型进行二次模拟的接口。  
### py6s安装
Windows环境下推荐使用Conda进行安装（其他环境不清楚），手动安装极其麻烦（非常不推荐）  
Py6S 及其所有依赖项（包括 6S 本身）可通过conda上的包管理器获得conda-forge。  
这是安装 Py6S 的最简单方法，强烈推荐。  
  
通过conda，运行以下命令创建一个包含 Py6S 及其所有依赖项的新环境：  
```
conda create -n py6s-env -c conda-forge py6s
```
测试py6s是否正确安装
```
python
>>> from Py6S import *
>>> SixS.test()
6S wrapper script by Robin Wilson
Using 6S located at <PATH_TO_SIXS_EXE>
Running 6S using a set of test parameters
The results are:
Expected result: 619.158000
Actual result: 619.158000
#### Results agree, Py6S is working correctly
```

### 进行大气校正
```
def atmos_cali(image):
    """
    利用6s算法对图像进行大气校正
    :param image: 输入需要进行校正的遥感影像
    :return: 返回校正结果
    """
    bands = image.shape[2]
    mtl = readMTL.mtl()
    mtl.read_mtl()

    lat_cen = math.fabs(mtl.lat_cen)
    lon_cen = mtl.lon_cen

    # 创建6s对象，6s具体使用方法可参见SixS()源文件
    s = SixS()
    s.geometry = Geometry.User()

    # 太阳方位角及高度角，从MTL文件中读取
    s.geometry.solar_a = mtl.sun_azimuth
    s.geometry.solar_z = 90 - mtl.sun_elevation
    s.geometry.view_a = 0
    s.geometry.view_z = 0

    # 日期信息，从MTL文件中读取
    s.geometry.month = mtl.date[1]
    s.geometry.day = mtl.date[2]

    if lat_cen <= 30:
        s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.Tropical)    # 大气配置文件
    elif 30 < lat_cen <= 60:
        ...
    elif 60 < lat_cen:
        ...

    s.aero_profile = AtmosProfile.PredefinedType(AeroProfile.Continental)   # 气溶胶配置文件。
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(0.36)    # 地面反射率设置。

    s.altitudes = Altitudes()
    s.altitudes.set_target_custom_altitude(2.3)
    s.altitudes.set_sensor_satellite_level()

    s.aot550 = 0.14497  # 用于模拟的气溶胶光学厚度值（550nm处）

    # 波段中心波长
    cen_wavelength = [Wavelength(PredefinedWavelengths.LANDSAT_OLI_B1), ...]

    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(-0.1)   # 是否进行大气校正的设置，以及该校正的参数。

    temp = np.zeros_like(image, dtype=np.float32)   # 创建空数组
    atmos_re = np.zeros_like(image, dtype=np.float32)   # 空数组，储存结果

    for band in range(bands):
        s.wavelength = cen_wavelength[band]
        s.run()
        xa = s.outputs.coef_xa
        xb = s.outputs.coef_xb
        xc = s.outputs.coef_xc
        x = s.outputs.values
        print(x)

        temp[:, :, band] = xa * image[:, :, band] - xb
        atmos_re[:, :, band] = temp[:, :, band] / (1 + temp[:, :, band] * xc) *1000

    del temp
    return atmos_re
```
### 结果对比
