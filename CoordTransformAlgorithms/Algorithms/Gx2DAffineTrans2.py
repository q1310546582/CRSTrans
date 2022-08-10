from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.GxXYZTransAsPublicClass import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear


class Gx2DAffineTrans(GxXYZTransAsPublicClass):
    """此模型是依据最小二乘法的二维仿射变换模型"""

    def __init__(self, public_points):
        '''
        平面四参数转换模型转换模型参数说明：
        参数1支持公共点的浮点型二维数组，其中数量不少于3个，并且每个元素存储原坐标系坐标和新坐标系坐标(X1,Y1,Z1,X2,Y2,Z2)
        '''

        self.public_num = 3  # 至少要求的公共点数量
        self.dimension = 2  # 当前模型坐标的维度
        self.model_name = '仿射变换模型'
        self.load_data(public_points)  # 加载数据
        self.__public_points = self.Public_points

    def fit(self):
        '''通过公共点训练最小二乘法模型，并改正数、坐标分量中误差、点位中误差矩阵'''
        # 构建A
        A = self.A_coefficient(self.__public_points[:, :])
        # 构建b
        b = self.b_vector()

        res = lsq_linear(A, b, lsmr_tol='auto')
        self.isFitted = True
        self.res = res
        # 将公共点代入训练好的模型得到结果
        self.Predict_points = self.predict(self.__public_points[:, :])
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
        result_points = (A_test.dot(self.res.x.ravel())).reshape((-1, self.dimension))
        return result_points

    def A_coefficient(self, points):
        '''构建系数矩阵'''
        A = pd.DataFrame()
        for i in range(points.shape[0]):
            src_X = points[i, 0]
            src_Y = points[i, 1]
            array = np.array([[1, src_X, src_Y, 0, 0, 0],
                              [0, 0, 0, 1, src_X, src_Y]])
            A = pd.concat([A, pd.DataFrame(array)], axis=0)
        A = np.array(A)
        return A

    def b_vector(self):
        '''获得b向量'''
        b = self.__public_points[:, self.dimension:]
        return b.ravel()

if __name__ == '__main__':
    L = [[10.0, 457.0, 46.0, 920.0],
         [395.0, 291.0, 46.0, 100.0],
         [624.0, 291.0, 600.0, 100.0],
         [1000.0, 457.0, 600.0, 920.0], ]

    L = [GxCoordinatePointPair(idx, CoordinateType.XY, item[0], item[1], 0, item[2], item[3], 0) for
         idx, item in enumerate(L)]
    CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.XY)
    public_array = CoordinatePointPairArray.ToNumpyArray(2)
    print(public_array)
    aff = Gx2DAffineTrans(public_array)
    dic = aff.fit()
    print(aff.Predict_points)