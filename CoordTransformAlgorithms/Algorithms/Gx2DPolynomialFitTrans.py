from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.GxXYZTransAsPublicClass import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear

class Poly_fit(GxXYZTransAsPublicClass):
    """此模型是平面多项式拟合模型，适用于小地区坐标转换"""

    def __init__(self, public_points, CoordinateType, order=2):
        '''
        平面多项式拟合模型参数说明：
        参数1支持待转换的浮点型二维数组，每个元素存储一个点坐标，(X,Y)或(B,L)
        '''
        self.CoordinateType = CoordinateType
        if (order == 2):
            self.public_num = 2  # 至少要求的公共点数量
        elif (order == 3):
            self.public_num = 4
        self.dimension = 2  # 当前模型坐标的维度
        self.load_data(public_points)  # 加载数据
        self.model_name = 'Plane polynomial fitting model'
        self.n = order
        self.__public_points = self.Public_points

    def angle2rad(self, x):
        return x * np.pi / 180.0

    def A_coefficient(self, points):
        '''构建系数矩阵'''
        A = pd.DataFrame()
        if (self.n == 2):
            for i in range(points.shape[0]):
                if (self.CoordinateType == CoordinateType.BL):
                    L = self.angle2rad(points[i, 1])
                    B = self.angle2rad(points[i, 0])
                elif (self.CoordinateType == CoordinateType.XY):
                    L = points[i, 1]
                    B = points[i, 0]
                A11 = 1
                A12 = B
                A13 = L
                A14 = B * L
                A15 = B ** 2
                A16 = L ** 2
                A_i = np.array([[A11, A12, A13, A14, A15, A16]])
                A = pd.concat((A, pd.DataFrame(A_i)), axis=0)

        elif (self.n == 3):
            for i in range(points.shape[0]):
                if (self.CoordinateType == CoordinateType.BL):
                    L = self.angle2rad(points[i, 1])
                    B = self.angle2rad(points[i, 0])
                elif (self.CoordinateType == CoordinateType.XY):
                    L = points[i, 1]
                    B = points[i, 0]
                A11 = 1
                A12 = B
                A13 = L
                A14 = B ** 2
                A15 = B * L
                A16 = L ** 2
                A17 = B ** 3
                A18 = (B ** 2) * L
                A19 = B * (L ** 2)
                A10 = L ** 3
                A_i = np.array([[A11, A12, A13, A14, A15, A16, A17, A18, A19, A10]])
                A = pd.concat((A, pd.DataFrame(A_i)), axis=0)
        A = np.array(A)
        return A

    def b_vector(self):
        '''获得b向量'''
        # 构建b
        b1 = self.__public_points[:, 2] - self.__public_points[:, 0]
        b1 = b1.ravel()
        b2 = self.__public_points[:, 3] - self.__public_points[:, 1]
        b2 = b2.ravel()
        return b1, b2

    def fit(self):
        '''通过公共点训练最小二乘法模型，并获得改正数、坐标分量中误差、点位中误差矩阵'''
        # 构建A
        A = self.A_coefficient(self.__public_points)
        # 构建b
        b1, b2 = self.b_vector()

        self.isFitted = True
        res1 = lsq_linear(A, b1, lsmr_tol='auto')
        res2 = lsq_linear(A, b2, lsmr_tol='auto')
        self.res1 = res1
        self.res2 = res2

        # 将公共点代入训练好的模型得到结果
        self.Predict_points = self.predict(self.__public_points[:, :self.dimension])
        # 计算中误差矩阵
        self.residual_array, self.MSE_array, self.MSE_point = self.RMSE(self.__public_points[:, self.dimension:],
                                                                        self.Predict_points)
        self.__prams_array1 = self.res1['x']
        self.__prams_array2 = self.res2['x']
        print(f'''
        模型：{self.model_name},
        模型训练阶段:{self.res1['message']},
        参数1：{self.res1['x']},
        参数2：{self.res2['x']},
        综合坐标分量中误差为：{self.MSE_array},
        综合点位中误差为：{self.MSE_point},
        ''')
        return {'model': self.model_name, 'message': self.res1['message'],
                    'x': dict({f"paramX{i}":v for i,v in enumerate(self.__prams_array1)}, **{f"paramY{i}":v for i,v in enumerate(self.__prams_array2)}),
                'residual_array': self.residual_array,
                'axisMSE': self.MSE_array, 'MSE': self.MSE_point}

    def predict(self, test_array):
        '''预测新的坐标点'''
        if (self.isFitted == False):  # 如果还未训练，先进行训练
            self.fit()
        A_test = self.A_coefficient(test_array)
        L1_test = test_array[:, 0].ravel()
        L2_test = test_array[:, 1].ravel()
        predict_points_B = (A_test.dot(self.res1.x.ravel()) + L1_test).ravel()
        predict_points_L = (A_test.dot(self.res2.x.ravel()) + L2_test).ravel()
        return np.array([predict_points_B, predict_points_L]).T

if __name__ == '__main__':
    # poly_fit For XY
    L1 = [[3391528.524, 483058.025, 212.191, 3391480.452, 483007.7061, 212.191],
          [3397833.33, 503800.445, 16.058, 3397785.261, 503750.1382, 16.154],
          [3397832.012, 522616.596, 136.225, 3397783.94, 522566.2938, 136.225],
          [3372118.452, 518833.498, 18.755, 3372070.366, 518783.1979, 18.755],
          [3370410.392, 497127.368, 19.814, 3370362.308, 497077.0512, 19.814],
          [3368398.831, 487063.781, 20.342, 3368350.746, 487013.4587, 20.342],
          [3377215.451, 482559.198, 38.342, 3377167.373, 482508.8726, 38.342]]
    L1 = [GxCoordinatePointPair(idx, CoordinateType.XYZ, item[0], item[1], item[2], item[3], item[4], item[5]) for
          idx, item in enumerate(L1)]
    CoordinatePointPairArray = GxCoordinatePointPairArray(L1, CoordinateType.XYZ)
    public_array = CoordinatePointPairArray.ToNumpyArray(2)
    poly = Poly_fit(public_array, CoordinateType=CoordinateType.XY)
    dic = poly.fit()
    # poly_fit For BL
    L2 = [[36.440904, 99.221520, 36.441403346, 99.215204500],
         [30.442593, 100.411054, 30.443325306, 100.404859486],
         [33.290936, 102.051562, 33.291600050, 102.045263514],
         [39.020923, 102.422003, 39.021409650, 102.415518185],
         [41.100049, 103.260618, 41.100478134, 103.254033959],
         [41.154516, 107.175903, 41.155030393, 107.173213747],
         [39.142510, 106.065984, 39.143063872, 106.063402544],
         [30.324387, 105.015458, 30.325201198, 105.013159620],
         [27.470060, 104.264953, 27.470951462, 104.262728769],
         [27.490465, 107.283888, 27.491404905, 107.281596711],
         [33.433354, 108.352388, 33.434135609, 108.345928169],
         [36.382730, 108.364481, 36.383421756, 108.361931339],
         [39.461085, 109.452977, 39.461704334, 109.450289954],
         [41.042783, 112.543337, 41.043437137, 112.540530593],
         [38.030502, 112.483700, 38.031243792, 112.481014616],
         [35.142390, 112.183799, 35.143203115, 112.181218668],
         [32.071257, 111.232282, 32.072141657, 111.225810116],
         [29.164946, 110.364171, 29.165897395, 110.361784896],
         [30.141627, 113.391747, 30.142607663, 113.385283325],
         [27.194633, 110.021590, 27.195629770, 110.015257666],
         [27.535150, 113.091790, 27.540184367, 113.085389628],
         [36.131781, 115.474996, 36.132642541, 115.472321862],
         [38.551863, 115.491777, 38.552649958, 115.485004195],
         [30.204721, 116.401165, 30.205756100, 116.374651342],
         [35.571778, 118.111033, 35.572700222, 118.104331555], ]
    L2 = [GxCoordinatePointPair(idx, CoordinateType.BL, item[0], item[1], 0, item[2], item[3], 0) for idx, item in
         enumerate(L2)]
    CoordinatePointPairArray2 = GxCoordinatePointPairArray(L2, CoordinateType.BL)
    public_array2 = CoordinatePointPairArray2.ToNumpyArray(2)
    poly2 = Poly_fit(public_array2, CoordinateType=CoordinateType.BL)
    dic2 = poly2.fit()

    print(np.concatenate([poly2.Public_points[:, 2:], poly2.Predict_points], axis=1))