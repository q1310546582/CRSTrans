from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

class GxXYZTransAsPublicClass(object):
    '''用于XYZ或XY参数模型的公共父类'''
    # 传入公共点
    @property
    def Public_points(self):
        return self.__public_points

    def load_data(self, public_points):
        if (public_points.any() != None):
            if (len(public_points) < self.public_num):
                return "Insufficient number of control points"
            self.__public_points = public_points
            self.isFitted = False  # 是否拟合标志
        else:
            return "Missing parameter"

    def fit(self):
        pass

    def predict(self, convert_points):
        pass

    def RMSE(self, train_points, result_points):
        '''评价并返回'''
        n = train_points.shape[0]
        residual_array = result_points - train_points
        correct_array = (np.sum(np.power(train_points - result_points, 2), axis=0) / (n - 1))  # [vv]/n-1矩阵
        MSE_array = np.sqrt(correct_array)  # 坐标分量中误差矩阵
        MSE_point = np.sqrt(np.sum(correct_array))  # 点位中误差值
        return residual_array, MSE_array, MSE_point

    def A_coefficient(self, points):
        pass

    def b_vector(self):
        pass