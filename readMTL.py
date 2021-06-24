class mtl(object):

    def __init__(self):
        self.mult = []
        self.add = []

        self.date = []
        self.time = []

        self.sun_azimuth = 0
        self.sun_elevation = 0

        self.earth_sun_distance = 0

        self.lat_cen = 0
        self.lon_cen = 0

        self.pub_path = 'E:\\RSImg\\LC08_L1TP_119039_20201213_20210313_01_T1\\LC08_L1TP_119039_20201213_20210313_01_T1'

    def read_mtl(self):
        global ul_lat, ur_lat, ul_lon, ur_lon, ll_lon, lr_lon, lr_lat, ll_lat
        filename = self.pub_path + '_MTL.txt'
        f = open(filename, 'r')
        metadata = f.readlines()
        f.close()
        temp_line = 0

        for line in metadata:
            if line.__contains__('DATE_ACQUIRED'):
                arr = line.split('=')[1].split('-')
                for i in arr:
                    self.date.append(float(i))
            elif line.__contains__('SCENE_CENTER_TIME'):
                arr = line.split('=')[1].split('"')[1].split(':')
                for i in arr[0:2]:
                    self.time.append(float(i))

            elif line.__contains__('SUN_AZIMUTH'):
                self.sun_azimuth = float(line.split('=')[1])
            elif line.__contains__('SUN_ELEVATION'):
                self.sun_elevation = float(line.split('=')[1])

            elif line.__contains__('CORNER_UL_LAT_PRODUCT'):
                ul_lat = float(line.split('=')[1])
            elif line.__contains__('CORNER_UL_LON_PRODUCT'):
                ul_lon = float(line.split('=')[1])
            elif line.__contains__('CORNER_UR_LAT_PRODUCT '):
                ur_lat = float(line.split('=')[1])
            elif line.__contains__('CORNER_UR_LON_PRODUCT'):
                ur_lon = float(line.split('=')[1])
            elif line.__contains__('CORNER_LL_LAT_PRODUCT'):
                ll_lat = float(line.split('=')[1])
            elif line.__contains__('CORNER_LL_LON_PRODUCT'):
                ll_lon = float(line.split('=')[1])
            elif line.__contains__('CORNER_LR_LAT_PRODUCT '):
                lr_lat = float(line.split('=')[1])
            elif line.__contains__('CORNER_LR_LON_PRODUCT'):
                lr_lon = float(line.split('=')[1])

            elif line.__contains__('EARTH_SUN_DISTANCE'):
                self.earth_sun_distance = float(line.split('=')[1])
            elif line.__contains__('RADIOMETRIC_RESCALING'):
                break
            temp_line += 1

        self.lat_cen = (ul_lat + ur_lat + ll_lat + lr_lat) / 4
        self.lon_cen = (ul_lon + ur_lon + ll_lon + lr_lon) / 4

        rad_mult = metadata[temp_line + 1:temp_line + 12]
        rad_add = metadata[temp_line + 12:temp_line + 23]

        for line in rad_mult:
            self.mult.append(float(line.split('=')[1]))
        for line in rad_add:
            self.add.append(float(line.split('=')[1]))
