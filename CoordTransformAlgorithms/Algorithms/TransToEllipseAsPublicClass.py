from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear
from GxEllipsoidEnum import *

class TransToEllipseAsPublicClass(object):
    """此模型是同一基准下坐标互转换模型"""

    def __init__(self, ellipsoid, convert_points=None):
        '''
        参数说明：
        参数3支持待转换的浮点型二维数组，每个元素存储一个点坐标
        '''
        self.load_data(convert_points)
        self.ellipsoid = ellipsoid.value
        self.staticPrams_init(self.ellipsoid)

    # 加载待转换的坐标数组
    def load_data(self, convert_points):
        if (convert_points.any() != None):
            self.__convert_points = convert_points

    def staticPrams_init(self, ellipsoid):
        self.e1 = ellipsoid['e1']
        self.e2 = ellipsoid['e2']
        self.a = ellipsoid['A']
        self.m0 = self.a * (1 - self.e1)
        self.m2 = 3 / 2 * self.e1 * self.m0
        self.m4 = 5 / 4 * self.e1 * self.m2
        self.m6 = 7 / 6 * self.e1 * self.m4
        self.m8 = 9 / 8 * self.e1 * self.m6
        self.a0 = self.m0 + self.m2 / 2 + 3 / 8 * self.m4 + 5 / 16 * self.m6 + 35 / 128 * self.m8
        self.a2 = self.m2 / 2 + self.m4 / 2 + 15 / 32 * self.m6 + 7 / 16 * self.m8
        self.a4 = self.m4 / 8 + 3 / 16 * self.m6 + 7 / 32 * self.m8
        self.a6 = self.m6 / 32 + self.m8 / 16
        self.a8 = self.m8 / 128

    @property
    def Convert_points(self):
        return self.__convert_points

    @Convert_points.setter
    def Convert_points(self, value):
        self.__convert_points = value

    def pram_X(self, a0, a2, a4, a6, B):
        sin2B = np.sin(2 * B)
        sin4B = np.sin(4 * B)
        sin6B = np.sin(6 * B)
        return a0 * B - a2 / 2 * sin2B + a4 / 4 * sin4B - a6 / 6 * sin6B

    def predict(self, array=None):
        return self.__predict(self, array)

    def angle2rad(self, x):
        return x * np.pi / 180.0

    def rad2angle(self, x):
        return x * 180 / np.pi

    def pram_V(self, pram_n):
        return np.sqrt(1 + pram_n ** 2)

    def pram_n(self, ellipsoid, B):
        return np.sqrt(ellipsoid['e2']) * np.cos(B)

    def pram_V(self, pram_n):
        return np.sqrt(1 + pram_n ** 2)

    def pram_c(self, ellipsoid):
        return np.power(ellipsoid['A'], 2) / ellipsoid['B']

    def pram_M(self, c, V):
        return c / np.power(V, 3)

    def pram_N(self, c, V):
        return c / V

    def predict(self):
        pass