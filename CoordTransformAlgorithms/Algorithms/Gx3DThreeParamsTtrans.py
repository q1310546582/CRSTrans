from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.GxXYZTransAsPublicClass import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

class XYZ_3p(GxXYZTransAsPublicClass):

    """此模型是空间直角三参数参数转换模型，适用于小地区空间直角坐标转换"""
    def __init__(self, public_points):
        '''
        平面四参数转换模型转换模型参数说明：
        参数1支持公共点的浮点型二维数组，其中数量不少于3个，并且每个元素存储原坐标系坐标和新坐标系坐标(X1,Y1,Z1,X2,Y2,Z2)
        '''

        self.public_num = 1  # 至少要求的公共点数量
        self.dimension = 3  # 当前模型坐标的维度
        self.model_name = '三参数转换模型'
        self.load_data(public_points)  # 加载数据
        self.__public_points = self.Public_points

    def A_coefficient(self,points):
        pass

    def fit(self):
        self.__public_points = self.Public_points
        self.isFitted = True
        X = np.mean((self.__public_points[:,3] - self.__public_points[:,0]).ravel())
        Y = np.mean((self.__public_points[:,4] - self.__public_points[:,1]).ravel())
        Z = np.mean((self.__public_points[:,5] - self.__public_points[:,2]).ravel())
        self.__prams_array = np.array([X,Y,Z])

        # 将公共点代入训练好的模型得到结果
        self.Predict_points  = self.predict(self.__public_points[:, :self.dimension])
        # 计算中误差矩阵
        self.residual_array, self.MSE_array, self.MSE_point = self.RMSE(self.__public_points[:, self.dimension:],
                                                                        self.Predict_points )
        print(f'''
        模型：{self.model_name},
        参数：{self.__prams_array},
        综合坐标分量中误差为：{self.MSE_array},
        综合点位中误差为：{self.MSE_point},
        ''')
        return {'model': self.model_name,  'x': self.__prams_array,
                'residual_array': self.residual_array,
                'axisMSE': self.MSE_array, 'MSE': self.MSE_point}

    def predict(self,test_array):
        '''预测新的坐标点'''
        if(self.isFitted == False):  #如果还未训练，先进行训练
            self.__prams_array = self.fit()

        return test_array + self.__prams_array

if __name__ == '__main__':
    L = [[2806701.406, 627258.9498, 2063.3785, 2806708.622, 627370.3638, 2063.3785],
         [2873139.972, 633482.3323, 2743.2418, 2873147.609, 633593.605, 2743.2418],
         [2792423.335, 552021.8638, 1750.1515, 2792430.262, 552132.8593, 1750.1515],
         [2784351.56, 600303.7481, 2049.1774, 2784358.567, 600415.0586, 2049.1774],
         [2728946.236, 656786.3844, 1960.387, 2728953.06, 656898.1871, 1960.387]]

    L = [GxCoordinatePointPair(idx, CoordinateType.XYZ, item[0], item[1], item[2], item[3], item[4], item[5]) for
         idx, item in enumerate(L)]
    CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.XYZ)
    public_array = CoordinatePointPairArray.ToNumpyArray(3)
    brs = XYZ_3p(public_array)
    dic = brs.fit()
    print(brs.Predict_points)
