from GxEllipsoidEnum import *
from TransToEllipseAsPublicClass import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *

import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

class GaussNegativeTransformer(TransToEllipseAsPublicClass):
    """此模型是高斯格吕格反算模型"""

    def __init__(self, L0, interval, ellipsoid, convert_points=None, includeBandNum = True, includeFalseEasting = True):
        '''
        高斯格吕格正反算模型参数说明：
        参数1为当前分度带为3°带还是6°带
        参数2为当中标系参数，枚举型
        参数3支持待转换的浮点型二维数组，每个元素存储一个点坐标，(X,Y)或(B,L)
        '''
        self.load_data(convert_points)
        self.ellipsoid = ellipsoid.value
        self.staticPrams_init(self.ellipsoid)
        self.L0 = L0
        if (interval == 3 and includeBandNum == True):
            self.N0 = L0/3

        elif (interval == 6 and includeBandNum == True):
            self.N0 = (L0 + 3)/6

        if (includeBandNum == False):
            self.N0  = 0
        if (includeFalseEasting == False):
            self.FalseEasting = 0
        else:
            self.FalseEasting = 500000


    def predict(self, array=None):

        if (array != None):
            self.Convert_points = array
        result = []
        for i in self.Convert_points:
            x = i[0]
            y = i[1] - self.N0 * 1000000 - self.FalseEasting

            B0 = x / self.a0
            FBf = -self.a2 / 2 * np.sin(2 * B0) + self.a4 / 4 * np.sin(4 * B0) - self.a6 / 6 * np.sin(
                6 * B0) + self.a8 / 8 * np.sin(8 * B0)
            Bf = (x - FBf) / self.a0
            while (np.abs(Bf - B0) > 4.8e-10):  # 迭代法求解底点纬度Bf
                B0 = Bf
                FBf = -self.a2 / 2 * np.sin(2 * B0) + self.a4 / 4 * np.sin(4 * B0) - self.a6 / 6 * np.sin(
                    6 * B0) + self.a8 / 8 * np.sin(8 * B0)
                Bf = (x - FBf) / self.a0

            cosBf = np.cos(Bf)
            sinBf = np.sin(Bf)
            Nf = self.a / np.sqrt((1 - self.e1 * sinBf**2))
            Mf = self.a * (1 - self.e1) / np.sqrt(np.power((1 - self.e1 * (sinBf**2)), 3))
            nf = self.e2 * cosBf
            tf = np.tan(Bf)

            result.append(self.XY2BL(Bf, Mf, Nf, nf, cosBf, sinBf, tf, y))
        return result

    def XY2BL(self, Bf, Mf, Nf, nf, cosBf, sinBf, tf, y):
        B = Bf - tf * np.power(y, 2) / (2 * Mf * Nf) + \
            tf * (5 + 3 * np.power(tf, 2) + np.power(nf, 2) - 9 * np.power(nf, 2) * np.power(tf, 2)) * np.power(y,4) / (24 * Mf * np.power(Nf, 3)) - \
            tf * (61 + 90 * np.power(tf, 2) + 45 * np.power(tf, 4)) * np.power(y,6) / (720 * Mf * np.power(Nf, 5))

        l = y / (Nf * cosBf) - \
            np.power(y,3) * (1 + 2 * tf**2 + nf**2) / (6 * Nf**3 * cosBf) + \
            (5 + 28 * tf**2 + 24 * tf**4 + 6 * nf**2 + 8 * (nf * tf)**2) * np.power(y,5) / (120 * Nf**5 * cosBf)

        return self.rad2angle(B), self.L0 + self.rad2angle(l)

if __name__ == '__main__':
    # band:20 GCS: Beijing1954 interval: 6
    # L = [(3378627.23968484, 20243953.4127856), (3378627.23968484, 20243953.4127856)]
    # band:36 GCS: Xian1980 interval: 3
    L = [[3046786.311,36619727.096,859.654],
    [3046862.134,36619650.747,864.782],
    [3046821.690,36619531.800,880.333],
    [3046901.864,36619637.405,874.796],]
    # band:34 GCS Control Points: [Beijing1954[:3]，Xian80[3:]] interval: 3
    L = [[3391528.524, 483058.025, 212.191, 3391480.452, 483007.7061, 212.191],
         [3397833.33, 503800.445, 16.058, 3397785.261, 503750.1382, 16.154],
         [3397832.012, 522616.596, 136.225, 3397783.94, 522566.2938, 136.225],
         [3372118.452, 518833.498, 18.755, 3372070.366, 518783.1979, 18.755],
         [3370410.392, 497127.368, 19.814, 3370362.308, 497077.0512, 19.814],
         [3368398.831, 487063.781, 20.342, 3368350.746, 487013.4587, 20.342],
         [3377215.451, 482559.198, 38.342, 3377167.373, 482508.8726, 38.342]]


    L = [GxCoordinatePoint(item[3], item[4], 0, CoordinateType.XY) for idx, item in enumerate(L)]
    CoordinatePointArray = GxCoordinatePointArray(L, CoordinateType.XY)
    convert_points = CoordinatePointArray.ToNumpyArray(2)
    GaussPositiveTrans = GaussNegativeTransformer(102, 3, GxEllipsoidEnum['Xian80'], convert_points, includeBandNum= False)
    result = GaussPositiveTrans.predict()
    print(result)