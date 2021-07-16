import math
import numpy as np
from Py6S import *
import readMTL


def toa_cali(image, bands, img_type=None):
    import readMTL
    mtl = readMTL.mtl()
    mtl.read_mtl()

    sun_ele = mtl.sun_elevation
    d = mtl.earth_sun_distance
    ESUN = [1889.0, 1971.0, 1850.0, 1571.0, 970.50, 246.20, 76.88, 1750.00, 369.00]

    toa_img = np.zeros_like(image, dtype=np.float32)

    if img_type == 'Multi':
        for band in range(bands):
            toa_img[:, :, band] = math.pi * d * d * image[:, :, band] / (ESUN[band] * math.sin(sun_ele / 180 * math.pi))
    elif img_type == 'Pan':
        toa_img[:, :] = math.pi * d * d * image[:, :] / (ESUN[7] * math.sin(sun_ele / 180 * math.pi))
    elif img_type == 'Thermal':
        for band in range(bands):
            toa_img[:, :, band] = math.pi * d * d * image[:, :, 9 + band] / (ESUN[9 + band] * math.sin(sun_ele / 180 * math.pi))

    return toa_img


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

    # 太阳方位角及高度角
    s.geometry.solar_a = mtl.sun_azimuth
    s.geometry.solar_z = 90 - mtl.sun_elevation
    s.geometry.view_a = 0
    s.geometry.view_z = 0

    # 日期信息，从MTL文件中读取
    s.geometry.month = mtl.date[1]
    s.geometry.day = mtl.date[2]

    if lat_cen <= 30:
        s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.Tropical)
    elif 30 < lat_cen <= 60:
        if 4 < s.geometry.month <= 9:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeSummer)
        else:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.MidlatitudeWinter)
    elif 60 < lat_cen:
        if 4 < s.geometry.month <= 9:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.SubarcticSummer)
        else:
            s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.SubarcticWinter)

    s.aero_profile = AtmosProfile.PredefinedType(AeroProfile.Continental)
    s.ground_reflectance = GroundReflectance.HomogeneousLambertian(0.36)

    s.altitudes = Altitudes()
    s.altitudes.set_target_custom_altitude(2.3)
    s.altitudes.set_sensor_satellite_level()

    s.aot550 = 0.14497

    # 波段中心波长
    cen_wavelength = [Wavelength(PredefinedWavelengths.LANDSAT_OLI_B1),
                      Wavelength(PredefinedWavelengths.LANDSAT_OLI_B2),
                      Wavelength(PredefinedWavelengths.LANDSAT_OLI_B3),
                      Wavelength(PredefinedWavelengths.LANDSAT_OLI_B4),
                      Wavelength(PredefinedWavelengths.LANDSAT_OLI_B5),
                      Wavelength(PredefinedWavelengths.LANDSAT_OLI_B6),
                      Wavelength(PredefinedWavelengths.LANDSAT_OLI_B7)]

    s.atmos_corr = AtmosCorr.AtmosCorrLambertianFromReflectance(-0.1)

    temp = np.zeros_like(image, dtype=np.float32)
    atmos_re = np.zeros_like(image, dtype=np.float32)

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
