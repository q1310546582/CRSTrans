from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.TransToEllipseAsPublicClass import *
from GxEllipsoidEnum import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

class TransToEllipseXYZFromEllipseBLH(TransToEllipseAsPublicClass):

    def BLH2XYZ(self, B, L, H, N):
        cosB = np.cos(B)
        cosL = np.cos(L)
        sinB = np.sin(B)
        sinL = np.sin(L)
        X = (N + H) * cosB * cosL
        Y = (N + H) * cosB * sinL
        Z = (N * (1 - self.e1) + H) * sinB
        return (X, Y, Z)

    def predict(self, array=None):
        if (array != None):
            self.Convert_points = array
        result = []
        for i in self.Convert_points:
            B = i[0]
            L = i[1]
            H = i[2]
            L = self.angle2rad(L)
            B = self.angle2rad(B)
            n = self.pram_n(self.ellipsoid, B)
            c = self.pram_c(self.ellipsoid)
            V = self.pram_V(n)
            N = self.pram_N(c, V)
            result.append(self.BLH2XYZ(B, L, H, N))
        return result


if __name__ == '__main__':
    L3 = [(0.003593679068088974, 8.106160245336536, -2952488.028144622),
     (0.0002712198252023537, 8.433861559370229, -2943265.199898959),
     (0.0022989384751252125, 8.744073686241792, -2940456.392918814),
     (0.00031895172778723547, 8.746926504931606, -2966446.199759575),
     (0.0003374544264327394, 8.390491169612337, -2971369.3299888712),
     (0.0003468019634142133, 8.227828113854907, -2974814.1116370186),
     (0.0006521071962914812, 8.13176242603048, -2966728.0964017967)]
 #    L3 = [[0.0036123147684730054, 8.105442254560224, -2952437.7356483033],
 # [0.00026921228967600216, 8.433149510928464, -2943215.262326423],
 # [0.0022774280160725623, 8.743366099904243, -2940406.492947784],
 # [0.0002971127370899514, 8.746212289963513, -2966396.093486582],
 # [0.0003380483908569524, 8.389771495951718, -2971319.200242429],
 # [0.0003576279290932116, 8.22710564772422, -2974763.96183846],
 # [0.0006690269550958913, 8.131040925647195, -2966677.9769919165]]

    L3 = [GxCoordinatePoint(item[0],item[1],item[2],CoordinateType.BLH) for idx, item in enumerate(L3)]
    CoordinatePointArrayBLH = GxCoordinatePointArray(L3, CoordinateType.BLH)
    convert_pointsBLH = CoordinatePointArrayBLH.ToNumpyArray(3)
    blh2xyz = TransToEllipseXYZFromEllipseBLH(GxEllipsoidEnum['Beijing54'] ,convert_points = convert_pointsBLH)
    print(blh2xyz.predict())