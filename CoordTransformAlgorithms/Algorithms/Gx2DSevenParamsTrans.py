from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
from GxBLHTransAsPublicClass import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear
from GxEllipsoidEnum import *


class Gx2DSevenParamsTrans(GxBLHTransAsPublicClass):
    """此模型是二维七参数转换模型，适用于局部坐标系的坐标转换，区域<2*2°"""

    def __init__(self, source_ellipsoid, target_ellipsoid, public_points):
        '''
        平面四参数转换模型转换模型参数说明：
        参数1支持待转换的浮点型二维数组，每个元素存储一个点坐标，(B,L)
        '''
        self.source_ellipsoid = source_ellipsoid.value
        self.target_ellipsoid = target_ellipsoid.value
        self.public_num = 4  # 至少要求的公共点数量
        self.dimension = 2  # 当前模型坐标的维度
        self.load_data(public_points)  # 加载数据
        self.model_name = '二维七参数模型'
        self.__public_points = self.Public_points

    def A_coefficient(self, points):
        '''构建系数矩阵'''
        A = pd.DataFrame()

        ellipsoid = self.source_ellipsoid
        a = ellipsoid['A']
        f = ellipsoid['F']
        e2 = ellipsoid['e1']
        r = (180 * 3600) / np.pi
        c = self.pram_c(ellipsoid)

        for i in range(points.shape[0]):
            L = self.angle2rad(points[i, 1])
            B = self.angle2rad(points[i, 0])

            sinB = np.sin(B)
            cosB = np.cos(B)
            sinL = np.sin(L)
            cosL = np.cos(L)
            tgB = np.tan(B)

            n = self.pram_n(ellipsoid, B)
            V = self.pram_V(n)
            N = self.pram_N(c, V)
            M = self.pram_M(c, V)

            A11 = -sinL / (N * cosB) * r
            A12 = cosL / (N * cosB) * r
            A13 = 0
            A14 = tgB * cosL
            A15 = tgB * sinL
            A16 = -1
            A17 = 0

            A21 = -sinB * cosL / M * r
            A22 = -sinB * sinL / M * r
            A23 = cosB / M * r
            A24 = -sinL
            A25 = cosL
            A26 = 0
            A27 = -N / M * e2 * sinB * cosB * r

            A_i = np.array([[A21, A22, A23, A24, A25, A26, A27],
                            [A11, A12, A13, A14, A15, A16, A17], ])

            A = pd.concat((A, pd.DataFrame(A_i)), axis=0)

        A = np.array(A)

        return A

    def b_vector(self, points):
        '''获得b向量'''
        b = self.__public_points[:, self.dimension:] - self.__public_points[:, :self.dimension]
        C = self.c_vector(points)
        b = np.apply_along_axis(self.angle2seconds, 1, b)
        b = b.ravel() - C
        return b

    def fit(self):
        '''通过公共点训练最小二乘法模型'''
        # AX=b
        self.A = self.A_coefficient(self.__public_points)
        self.b = self.b_vector(self.__public_points)
        res = lsq_linear(self.A, self.b, lsmr_tol='auto')
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
        L_test = test_array
        C_test = self.c_vector(test_array)
        temp = (A_test.dot(self.res.x.ravel()) + C_test).reshape((-1, self.dimension))
        temp = np.apply_along_axis(self.seconds2angle, 1, temp)
        predict_points = (temp + L_test)
        return predict_points

    def c_vector(self, points):
        '''构建向量c'''
        C = pd.DataFrame()
        ellipsoid = self.source_ellipsoid
        a = ellipsoid['A']
        f = ellipsoid['F']
        e2 = ellipsoid['e1']
        r = (180 * 3600) / np.pi
        c = self.pram_c(ellipsoid)

        ellipsoid2 = self.target_ellipsoid
        a2 = ellipsoid2['A']
        f2 = ellipsoid2['F']
        a_ = a2 - a
        f_ = f2 - f
        a_f = np.array([a_, f_]).T
        for i in range(points.shape[0]):
            L = self.angle2rad(points[i, 1])
            B = self.angle2rad(points[i, 0])

            sinB = np.sin(B)
            cosB = np.cos(B)
            sinL = np.sin(L)
            cosL = np.cos(L)
            tgB = np.tan(B)

            n = self.pram_n(ellipsoid, B)
            V = self.pram_V(n)
            N = self.pram_N(c, V)
            M = self.pram_M(c, V)

            e2sinB2 = e2 * (sinB ** 2)
            C11 = 0
            C12 = 0
            C21 = N / (M * a) * e2 * sinB * cosB * r
            C22 = (2 - e2sinB2) / (1 - f) * sinB * cosB * r

            C_i = np.array([[C21, C22], [C11, C12]]).dot(a_f)

            C = pd.concat((C, pd.DataFrame(C_i)), axis=0)
        C = np.array(C).ravel()
        return C

    def angle2seconds(self, row):
        return [row[0] * 3600, row[1] * 3600]

    def seconds2angle(self, row):
        return [row[0] / 3600, row[1] / 3600]

if __name__ == '__main__':

    L = [(30.64354056288796, 101.82326215300266, 212.191, 30.643635522569028, 101.82273416037872, 212.191),
         (30.70052345042203, 102.03966935973139, 16.058, 30.700620284521527, 102.03914493180069, 16.154),
         (30.700303055707387, 102.23607305532296, 136.225, 30.700400648851325, 102.23555208521243, 136.225),
         (30.468432943488217, 102.19611767900675, 18.755, 30.46852629300121, 102.1955972753666, 18.755),
         (30.45316988551926, 101.97009123717905, 19.814, 30.453262088185053, 101.9695668317505, 19.814),
         (30.434959105720658, 101.8653380479768, 20.342, 30.43505056725842, 101.86481187429928, 20.342),
         (30.51442948428045, 101.81829932421914, 38.342, 30.514522171905337, 101.81777187804823, 38.342)]

    L = [GxCoordinatePointPair(idx, CoordinateType.BL, item[0], item[1], 0, item[3], item[4], 0) for idx, item in
         enumerate(L)]
    CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.BL)
    bl_7p = Gx2DSevenParamsTrans(source_ellipsoid=GxEllipsoidEnum['Beijing54'], target_ellipsoid=GxEllipsoidEnum['Xian80'],
                  public_points=CoordinatePointPairArray.ToNumpyArray())
    dic = bl_7p.fit()
    # print(np.concatenate([bl_7p.Public_points[:, 2:],bl_7p.Predict_points], axis = 1))
    print(bl_7p.predict(CoordinatePointPairArray.ToNumpyArray()[:1, :2]))
