from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.GxBLHTransAsPublicClass import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear



class XYZ_4p(GxBLHTransAsPublicClass):
    """此模型是三维四参数参数转换模型，适用于国家及省级空间直角坐标转换"""

    def __init__(self, centry_point, public_points):
        '''
        三维四参数转换模型转换模型参数说明：
        参数1区域中心点的大地经纬度，单位为度
        参数2支持公共点的浮点型二维数组，其中数量不少于2个，并且每个元素存储原坐标系坐标和新坐标系坐标(X1,Y1,Z1,X2,Y2,Z2)
        '''
        self.public_num = 2  # 至少要求的公共点数量
        self.dimension = 3  # 当前模型坐标的维度
        self.model_name = '三维四参数转换模型'
        self.load_data(public_points)  # 加载数据
        self.__public_points = self.Public_points
        self.centry_point = centry_point

    def A_coefficient(self, points):
        '''构建系数矩阵'''
        B = self.centry_point[0]
        L = self.centry_point[1]
        B = self.angle2rad(B)
        L = self.angle2rad(L)
        cosB = np.cos(B)
        sinB = np.sin(B)
        cosL = np.cos(L)
        sinL = np.sin(L)

        A = pd.DataFrame()
        for i in range(points.shape[0]):
            X = points[i, 0]
            Y = points[i, 1]
            Z = points[i, 2]
            array = np.array(
                [[Z * cosB * sinL - Y * sinB], [-Z * cosB * cosL + X * sinB], [Y * cosB * cosL - X * cosB * sinL]])
            A_i = np.concatenate((np.eye(self.dimension), array), axis=1)
            A = pd.concat([A, pd.DataFrame(A_i)], axis= 0)
        A = np.array(A)
        return A

    def b_vector(self):
        '''获得b向量'''
        b = self.__public_points[:, self.dimension:] - self.__public_points[:, :self.dimension]
        return b.ravel()

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
        self.__prams_array = self.res['x']
        print(f'''
        模型：{self.model_name},
        模型训练阶段:{self.res['message']},
        参数：{self.res['x']},
        综合坐标分量中误差为：{self.MSE_array},
        综合点位中误差为：{self.MSE_point},
        ''')
        return {'model': self.model_name, 'message': self.res['message'],
                'x': {'OffsetX': self.__prams_array[0], 'OffsetY': self.__prams_array[1], 'OffsetZ': self.__prams_array[2], 'Rotation': self.__prams_array[3],},
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

if __name__ == '__main__':
    L = [[3391528.524, 483058.025, 212.191, 3391480.452, 483007.7061, 212.191],
         [3397833.33, 503800.445, 16.058, 3397785.261, 503750.1382, 16.154],
         [3397832.012, 522616.596, 136.225, 3397783.94, 522566.2938, 136.225],
         [3372118.452, 518833.498, 18.755, 3372070.366, 518783.1979, 18.755],
         [3370410.392, 497127.368, 19.814, 3370362.308, 497077.0512, 19.814],
         [3368398.831, 487063.781, 20.342, 3368350.746, 487013.4587, 20.342],
         [3377215.451, 482559.198, 38.342, 3377167.373, 482508.8726, 38.342]]

    L_BL = np.array([(30.64354056288796, 101.82326215300266),
                     (30.70052345042203, 102.03966935973139),
                     (30.700303055707387, 102.23607305532296),
                     (30.468432943488217, 102.19611767900675),
                     (30.45316988551926, 101.97009123717905),
                     (30.434959105720658, 101.8653380479768),
                     (30.51442948428045, 101.81829932421914)])
    centry_point = np.mean(L_BL, axis=0)

    L = [GxCoordinatePointPair(idx, CoordinateType.XYZ, item[0], item[1], item[2], item[3], item[4], item[5]) for
         idx, item in enumerate(L)]
    CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.XYZ)
    public_array = CoordinatePointPairArray.ToNumpyArray(3)
    brs = XYZ_4p(centry_point, public_array)
    dic = brs.fit()
    print(brs.Predict_points)