from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

class GxBLHTransAsPublicClass(object):
    '''用于大地坐标转换模型参数的公共父类'''

    def load_data(self, public_points):
        if (public_points.any() != None):
            if (len(public_points) < self.public_num):
                return "Insufficient number of control points"
            self.__public_points = public_points
            self.__predict_points = []
            self.isFitted = False  # 是否拟合标志
        else:
            return "Missing parameter"

    def RMSE(self, train_points, result_points):
        '''评价并返回'''
        n = train_points.shape[0]
        residual_array = train_points - result_points
        correct_array = (np.sum(np.power(train_points - result_points, 2), axis=0) / (n - 1))  # [vv]/n-1矩阵
        MSE_array = np.sqrt(correct_array)  # 坐标分量中误差矩阵
        MSE_point = np.sqrt(np.sum(correct_array))  # 点位中误差值
        return residual_array, MSE_array, MSE_point

    @property
    def Public_points(self):
        return self.__public_points

    @property
    def Predict_points(self):
        return self.__predict_points

    @Predict_points.setter
    def Predict_points(self, value):
        self.__predict_points = value

    def rad2angle(self, x):
        return x / np.pi * 180

    def angle2rad(self, x):
        return x * np.pi / 180.0

    def rad2seconds(self, x):
        return x / np.pi * 180 * 3600

    def pram_n(self, ellipsoid, B):
        return ellipsoid['e2'] * np.power(np.cos(B), 2)

    def pram_V(self, pram_n):
        return np.sqrt(1 + pram_n)

    def pram_W(self, ellipsoid, B):
        return np.sqrt(1 - ellipsoid['e1'] * np.power(np.sin(B), 2))

    def pram_c(self, ellipsoid):
        return np.power(ellipsoid['A'], 2) / ellipsoid['B']

    def pram_M(self, c, V):
        return c / np.power(V, 3)

    def pram_N(self, c, V):
        return c / V

    def fit(self):
        pass

    def predict(self, test_array, isCorrectLocation=False):
        pass

    def A_coefficient(self, points):
        pass

    def b_vector(self):
        pass

    def BLH2rad(self, row):
        return [self.angle2rad(row[0]), self.angle2rad(row[1]), row[2]]

    def rad2BLH(self, row):
        return [self.rad2angle(row[0]), self.rad2angle(row[1]), row[2]]

