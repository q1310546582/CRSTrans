from GxEllipsoidEnum import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.TransToEllipseAsPublicClass import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

class TransToEllipseBLHFromEllipseXYZ(TransToEllipseAsPublicClass):

    def XYZ2BLH(self, X, Y, Z):
        sqrt = np.sqrt
        sin = np.sin
        cos = np.cos
        atan = np.arctan
        e = sqrt(self.e1)
        if X == 0 and Y > 0:
            L = 90
        elif X == 0 and Y < 0:
            L = -90
        elif X < 0 and Y >= 0:
            L = atan(Y / X)
            L = self.rad2angle(L)
            L = L + 180
        elif X < 0 and Y <= 0:
            L = atan(Y / X)
            L = self.rad2angle(L)
            L = L - 180
        else:
            L = atan(Y / X)
            L = self.rad2angle(L)

        sqrtXY = sqrt(X ** 2 + Y ** 2)
        b0 = atan(Z / sqrtXY)
        N = self.a / sqrt((1 - e * e * sin(b0) * sin(b0)))

        H0 = 1e9
        H1 = sqrtXY / cos(b0) - N

        while abs(H1 - H0) > 0.0001:
            b0 = atan(Z / ((1 - self.e1 * N / (N + H1)) * sqrtXY))
            N = self.a / sqrt((1 - self.e1 * sin(b0) * sin(b0)))
            H0, H1 = H1, sqrt(X ** 2 + Y ** 2) / cos(b0) - N

        B = self.rad2angle(b0)
        return B, L, H1  # 返回大地纬度B、经度L、海拔高度H (m)

    def predict(self, array=None):
        if (array != None):
            self.Convert_points = array
        result = []
        for i in self.Convert_points:
            X = i[0]
            Y = i[1]
            Z = i[2]
            result.append(self.XYZ2BLH(X, Y, Z))
        return result

if __name__ == '__main__':
    L2 = [[3391528.524, 483058.025, 212.191],
     [3397833.33, 503800.445, 16.058],
     [3397832.012, 522616.596, 136.225,],
     [3372118.452, 518833.498, 18.755,],
     [3370410.392, 497127.368, 19.814,],
     [3368398.831, 487063.781, 20.342,],
     [3377215.451, 482559.198, 38.342,]]
    L2 = [GxCoordinatePoint(item[0], item[1], item[2], CoordinateType.XYZ) for idx, item in enumerate(L2)]
    CoordinatePointArray = GxCoordinatePointArray(L2, CoordinateType.XYZ)
    convert_points = CoordinatePointArray.ToNumpyArray(3)
    xyz2blh = TransToEllipseBLHFromEllipseXYZ(GxEllipsoidEnum['Beijing54'], convert_points=convert_points)
    print(xyz2blh.predict())

    L2 = [[3391480.452,483007.7061,212.191],
        [3397785.261,503750.1382,16.154],
        [3397783.94,522566.2938,136.225],
        [3372070.366,518783.1979,18.755],
        [3370362.308,497077.0512,19.814],
        [3368350.746,487013.4587,20.342],
        [3377167.373,482508.8726,38.342],]
    L2 = [GxCoordinatePoint(item[0], item[1], item[2], CoordinateType.XYZ) for idx, item in enumerate(L2)]
    CoordinatePointArray = GxCoordinatePointArray(L2, CoordinateType.XYZ)
    convert_points = CoordinatePointArray.ToNumpyArray(3)
    xyz2blh = TransToEllipseBLHFromEllipseXYZ(GxEllipsoidEnum['Xian80'], convert_points=convert_points)
    print(xyz2blh.predict())