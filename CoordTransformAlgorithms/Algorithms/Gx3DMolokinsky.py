from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.GxXYZTransAsPublicClass import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

class Molokinsky(GxXYZTransAsPublicClass):
    """此模型是莫洛金斯基七参数转换模型，适用于国家及省级空间直角坐标转换"""

    def __init__(self, transition_point, public_points):
        '''
        平面四参数转换模型转换模型参数说明：
        参数1:莫洛金斯基模型的转换中心采用网的重心。[X,Y,Z]
        参数2:支持公共点的浮点型二维数组，其中数量不少于3个，并且每个元素存储原坐标系坐标和新坐标系坐标(X1,Y1,Z1,X2,Y2,Z2)
        '''

        self.public_num = 3  # 至少要求的公共点数量
        self.dimension = 3  # 当前模型坐标的维度
        self.load_data(public_points)  # 加载数据
        self.__public_points = self.Public_points
        self.transition_point = transition_point
        self.Xp = self.transition_point[0]
        self.Yp = self.transition_point[1]
        self.Zp = self.transition_point[2]
        self.model_name = '莫洛金斯基模型'

    def A_coefficient(self, points):
        '''构建系数矩阵'''
        A = pd.DataFrame()
        for i in range(points.shape[0]):
            X = points[i, 0]
            Y = points[i, 1]
            Z = points[i, 2]
            array = np.array(
                [[0, -(Z - self.Zp), Y - self.Yp, X - self.Xp], [Z - self.Zp, 0, -(X - self.Xp), Y - self.Yp],
                 [-(Y - self.Yp), X - self.Xp, 0, Z - self.Zp]])
            A_i = np.concatenate((np.eye(self.dimension), array), axis=1)
            A = pd.concat([A, pd.DataFrame(A_i)], axis= 0)
        A = np.array(A)
        return A

    def b_vector(self, points):
        '''获得b向量'''
        P = pd.DataFrame()
        for i in range(points.shape[0]):
            P = P.append([[self.Xp, self.Yp, self.Zp]])
        print(P)
        P = np.array(P)
        self.P = P.ravel()

        b = self.__public_points[:, self.dimension:] - P
        return b.ravel()

    def fit(self):
        '''通过公共点训练最小二乘法模型，并改正数、坐标分量中误差、点位中误差矩阵'''
        # 构建A
        A = self.A_coefficient(self.__public_points[:, :self.dimension])
        b = self.b_vector(self.__public_points[:, :self.dimension])
        print(b)
        res = lsq_linear(A, b, lsmr_tol='auto')
        self.isFitted = True
        self.res = res
        # 将公共点代入训练好的模型得到结果
        self.Predict_points = self.predict(self.__public_points[:, :self.dimension])
        # 计算中误差矩阵
        self.residual_array, self.MSE_array, self.MSE_point = self.RMSE(self.__public_points[:, self.dimension:],
                                                                        self.Predict_points)
        print(f'''
        模型：{self.model_name},
        模型训练阶段:{self.res['message']},
        参数：{self.res['x']},
        综合坐标分量中误差为：{self.MSE_array},
        综合点位中误差为：{self.MSE_point},
        ''')
        return {'model': self.model_name, 'message': self.res['message'], 'x': self.res['x'],
                'residual_array': self.residual_array,
                'axisMSE': self.MSE_array, 'MSE': self.MSE_point}

    def predict(self, test_array):
        '''预测新的坐标点'''
        if (self.isFitted == False):  # 如果还未训练，先进行训练
            self.res = self.fit()
        A_test = self.A_coefficient(test_array)
        result_points = (A_test.dot(self.res.x.ravel()) + self.P).reshape((-1, 3))
        return result_points

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
    transition_point = np.mean(public_array, axis=0)[:3]
    brs = Molokinsky(transition_point, public_array)
    dic = brs.fit()
    print(brs.Predict_points)