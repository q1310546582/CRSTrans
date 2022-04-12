from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.GxXYZTransAsPublicClass import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

class Brusa_Wolf(GxXYZTransAsPublicClass):
    """此模型是依据最小二乘法布尔莎-沃尔夫七参数转换模型"""

    def __init__(self, public_points):
        '''
        平面四参数转换模型转换模型参数说明：
        参数1支持公共点的浮点型二维数组，其中数量不少于3个，并且每个元素存储原坐标系坐标和新坐标系坐标(X1,Y1,Z1,X2,Y2,Z2)
        '''

        self.public_num = 3  # 至少要求的公共点数量
        self.dimension = 3  # 当前模型坐标的维度
        self.model_name = '布尔莎_沃尔夫模型'
        self.load_data(public_points)  # 加载数据
        self.__public_points = self.Public_points

    def fit(self):
        '''通过公共点训练最小二乘法模型，并改正数、坐标分量中误差、点位中误差矩阵'''
        # 构建A
        A = self.A_coefficient(self.__public_points[:, :self.dimension])
        # 构建b
        b = self.b_vector()
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
        L_test = test_array.ravel()
        result_points = (A_test.dot(self.res.x.ravel()) + L_test).reshape((-1, 3))
        return result_points

    def A_coefficient(self, points):
        '''构建系数矩阵'''
        A = pd.DataFrame()
        for i in range(points.shape[0]):
            X = points[i, 0]
            Y = points[i, 1]
            Z = points[i, 2]
            array = np.array([[0, -Z, Y, X], [Z, 0, -X, Y], [-Y, X, 0, Z]])
            A_i = np.concatenate((np.eye(3), array), axis=1)
            A = pd.concat([A, pd.DataFrame(A_i)], axis = 0)
        A = np.array(A)
        return A

    def b_vector(self):
        '''获得b向量'''
        b = self.__public_points[:, self.dimension:] - self.__public_points[:, :self.dimension]
        return b.ravel()

if __name__ == '__main__':
    L = [[3391528.524, 483058.025, 212.191, 3391480.452, 483007.7061, 212.191],
         [3397833.33, 503800.445, 16.058, 3397785.261, 503750.1382, 16.154],
         [3397832.012, 522616.596, 136.225, 3397783.94, 522566.2938, 136.225],
         [3372118.452, 518833.498, 18.755, 3372070.366, 518783.1979, 18.755],
         [3370410.392, 497127.368, 19.814, 3370362.308, 497077.0512, 19.814],
         [3368398.831, 487063.781, 20.342, 3368350.746, 487013.4587, 20.342],
         [3377215.451, 482559.198, 38.342, 3377167.373, 482508.8726, 38.342]]

    L = [GxCoordinatePointPair(idx, CoordinateType.XYZ, item[0], item[1], item[2], item[3], item[4], item[5]) for
         idx, item in enumerate(L)]
    CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.XYZ)
    public_array = CoordinatePointPairArray.ToNumpyArray(3)
    brs = Brusa_Wolf(public_array)
    dic = brs.fit()
    print(brs.Predict_points)