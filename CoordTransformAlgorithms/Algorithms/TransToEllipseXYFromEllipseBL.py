from TransToEllipseAsPublicClass import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear
from GxEllipsoidEnum import *

class GaussPositiveTransformer(TransToEllipseAsPublicClass):
    """此模型是高斯格吕格正算模型"""

    def __init__(self, interval, ellipsoid, convert_points=None):
        '''
        高斯格吕格正反算模型参数说明：
        参数1为当前分度带为3°带还是6°带
        参数2为当中标系参数，枚举型
        参数3支持待转换的浮点型二维数组，每个元素存储一个点坐标，(X,Y)或(B,L)
        '''
        self.load_data(convert_points)
        self.ellipsoid = ellipsoid.value
        self.staticPrams_init(self.ellipsoid)
        if (interval == 3 or interval == 6):
            self.interval = interval
        else:
            return 'Please enter the correct zoning value'

    def predict(self, array=None):
        if (array != None):
            self.Convert_points = array
        result = []
        if (self.interval == 6):
            self.N0 = np.ceil(self.Convert_points[0][1] / 6)  # 6度带带号
            L0 = 6 * self.N0 - 3
            for i in self.Convert_points:
                B = i[0]
                L = i[1]
                l = L - L0
                l = self.angle2rad(l)
                B = self.angle2rad(B)
                X = self.pram_X(self.a0, self.a2, self.a4, self.a6, B)
                n = self.pram_n(self.ellipsoid, B)
                c = self.pram_c(self.ellipsoid)
                V = self.pram_V(n)
                N = self.pram_N(c, V)
                t = np.tan(B)
                cosB = np.cos(B)
                sinB = np.sin(B)
                result.append(self.BL2XY(X, N, sinB, cosB, t, l, n))

        elif (self.interval == 3):
            self.N0 = np.ceil((self.Convert_points[0][1] - 1.5) / 3)  # 3度带带号
            L0 = 3 * self.N0
            for i in self.Convert_points:
                B = i[0]
                L = i[1]
                l = L - L0
                l = self.angle2rad(l)
                B = self.angle2rad(B)
                X = self.pram_X(self.a0, self.a2, self.a4, self.a6, B)
                n = self.pram_n(self.ellipsoid, B)
                c = self.pram_c(self.ellipsoid)
                V = self.pram_V(n)
                N = self.pram_N(c, V)
                t = np.tan(B)
                cosB = np.cos(B)
                sinB = np.sin(B)
                result.append(self.BL2XY(X, N, sinB, cosB, t, l, n))
        return result

    def BL2XY(self, X, N, sinB, cosB, t, l, n):
        x = X + N / 2 * sinB * cosB * np.power(l, 2) + N / 24 * sinB * np.power(cosB, 3) * (
                    5 - t ** 2 + 9 * n ** 2 + 4 * n ** 4) * np.power(l, 4) + N / 720 * sinB * np.power(cosB, 5) * (
                        61 - 58 * np.power(t, 2) + np.power(t, 4)) * np.power(l, 6)
        y = N * cosB * l + N / 6 * np.power(cosB, 3) * (1 - np.power(t, 2) + np.power(n, 2)) * np.power(l,
                                                                                                        3) + N / 120 * np.power(
            cosB, 5) * (5 - 18 * np.power(t, 2) + np.power(t, 4) + 14 * np.power(n, 2) - 58 * np.power(n * t,
                                                                                                       2)) * np.power(l,
                                                                                                                      5)
        return (x, y + self.N0 * 1000000 + 500000)

if __name__ == '__main__':
    # band:20 GCS: Beijing1954 interval: 6
    # L2 = [[30.5, 114 + 20 / 60], [30.5, 114 + 20 / 60]]
    # band:36 GCS: Xian1980 interval: 3
    L2 = [(27.52856704744024, 109.21192458167171),
          (27.52925787642881, 109.21115938544501),
          (27.52890346109618, 109.20995157126964),
          (27.529617507544057, 109.21102828481943)]

    L2 = [GxCoordinatePoint(item[0], item[1], 0, CoordinateType.BL) for idx, item in enumerate(L2)]
    CoordinatePointArray = GxCoordinatePointArray(L2, CoordinateType.BL)
    convert_points = CoordinatePointArray.ToNumpyArray(2)
    GaussPositiveTrans = GaussPositiveTransformer(3, GxEllipsoidEnum['Xian80'], convert_points)
    L3 = GaussPositiveTrans.predict()
    print(L3)