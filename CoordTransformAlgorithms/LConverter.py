from scipy.optimize import lsq_linear
import numpy as np
import pandas as pd
from enum import Enum
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''坐标转换算法模块：
    此模块包含以下对象：
    1. 用于大地坐标系转换的三维七参数模型类BLH_7p
    2. 用于大地坐标系转换的二维七参数模型类BL_7p
    3. 用于空间直角坐标系转换的布尔莎模型类Brusa_Wolf
    4. 用于空间直角坐标系转换的莫洛金斯基模型类Molokisky
    5. 用于空间坐标系转换的三维四参数模型类XYZ_4p
    6. 用于空间直角坐标系转换的三维三参数模型类XYZ_3p
    7. 用于平面直角坐标系转换的二维四参数模型类XY_4p
    8. 用于平面大地坐标系、平面直角坐标系转换的平面多项式拟合模型类Poly_fit
    9. 用于同一椭球体下的高斯正反算模型类Gaussian
    10. 用于同一椭球体下的大地坐标与空间直角坐标正反算模型类XYZ_BLH
    11. 用于栅格仿射变换的交换矩阵WarpPerspectiveMatrix
'''


class IGxCRS_TransForXYZ(object):
    '''用于XYZ或XY参数模型的公共父类'''

    # 传入的转换点、公共点以及坐标改正矩阵是在模型训练好后不可修改的，只可以读取
    @property
    def Convert_points(self):
        return self.__convert_points
    @property
    def Public_points(self):
        return self.__public_points
    @property
    def Difference_array(self): 
        return self.__difference_array   
    
    def load_data(self,convertFile_name,publicFile_name,convert_points,public_points,encoding,):
        self.isFitted = False # 是否拟合标志
        self.__difference_array = np.zeros(self.dimension) # 改正数矩阵
        if(convertFile_name != None and publicFile_name != None):
            try:
                with open('{}'.format(convertFile_name), 'r', encoding = encoding) as f:
                    convertFiledata = f.readlines()
                self.__convert_points = np.array([self.__str2floatList(line) for line in convertFiledata])
                with open('{}'.format(publicFile_name), 'r', encoding = encoding) as f:
                    publicFiledata = f.readlines()
                self.__public_points = np.array([self.__str2floatList(line) for line in publicFiledata])  
                if(len(self.__public_points) < self.public_num): return "公共点数量不足，请重新输入"
            except IOError:
                print(IOError)
                print("Error: 没有找到文件或读取文件失败，请检查格式或路径是否正确")
                return None
        elif(convert_points != None and public_points != None):
            if(len(public_points) < self.public_num): return "公共点数量不足，请重新输入"
            self.__convert_points = np.array(convert_points)
            self.__public_points = np.array(public_points)
        else:
            print("请检查输入参数是否正确")
            return None
        
    def __str2floatList(self,x):
        return list(map(float,x.strip().split(',')))        
    
    def fit(self):
        '''通过公共点训练最小二乘法模型，并改正数、坐标分量中误差、点位中误差矩阵'''
        # 构建A
        A = self.A_coefficient(self.__public_points)
        # 构建b
        b = self.__public_points[:,self.dimension:] - self.__public_points[:,:self.dimension]
        b = b.ravel()
        res = lsq_linear(A, b, lsmr_tol='auto')
        self.isFitted = True
        self.res = res
        # 将公共点代入训练好的模型得到结果
        predict_points = self.predict(self.__public_points[:,:self.dimension]) 
        # 计算中误差矩阵
        self.MSE_array,self.MSE_point,self.__difference_array = self.RMSE(self.__public_points[:,self.dimension:], predict_points)  
        print(f'''
        模型：{self.model_name},
        模型训练阶段:{self.res['message']},
        参数：{self.res['x']},
        坐标分量中误差为：{self.MSE_array},
        点位中误差为：{self.MSE_point},
        坐标改正数为：{self.__difference_array}
        ''')
        return self.res
    
    def fit_transform(self):
        '''通过公共点训练最小二乘法模型，并且输出转换点的新坐标点'''
        predict_points = self.predict(self.__convert_points)
        return predict_points
    
    def predict(self,test_array, isCorrectLocation = False):
        '''预测新的坐标点'''
        if(self.isFitted == False):  #如果还未训练，先进行训练
            self.res = self.fit()
        A_test = self.A_coefficient(test_array)
        L_test = test_array.ravel()
        predict_points = (A_test.dot(self.res.x.ravel()) + L_test).reshape((-1, self.dimension))
        if(self.__difference_array.all() != 0 and isCorrectLocation == True): #如果坐标改正矩阵存在并且isCorrectLocation==True，则改正预测值
            return predict_points + self.__difference_array
        return predict_points
    
    def RMSE(self,train_points,result_points):
        '''评价并返回'''
        n = train_points.shape[0] - 1 
        correct_array = (np.sum(np.power(train_points - result_points,2), axis = 0) / (n-1)) # [vv]/n-1矩阵
        MSE_array = np.sqrt(correct_array) #  坐标分量中误差矩阵
        MSE_point = np.sqrt(np.sum(correct_array))  # 点位中误差值
        difference_array = np.sum(train_points - result_points, axis = 0) / n # 各坐标分量改正值
        return MSE_array,MSE_point,difference_array
    
    def A_coefficient(self,points):
        pass

class XYZ_3p(IGxCRS_TransForXYZ):

    """此模型是空间直角三参数参数转换模型，适用于小地区空间直角坐标转换"""
    def __init__(self,convert_points = None, public_points = None,convertFile_name = None,publicFile_name = None, encoding = 'utf-8'):
        ''' 
        平面四参数转换模型转换模型参数说明：
        参数1支持待转换的浮点型二维数组，每个元素存储一个点坐标，(X,Y,Z)
        参数2支持公共点的浮点型二维数组，其中数量不少于3个，并且每个元素存储原坐标系坐标和新坐标系坐标(X1,Y1,Z1,X2,Y2,Z2)
        参数3支持待转换的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储一个点X,Y,Z
        参数4支持公共点的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储两个点X1,Y1,Z1,X2,Y2,Z2
        参数1、2或参数3、4为同时填入的参数
        '''
        self.public_num =  1# 至少要求的公共点数量
        self.dimension = 3 # 当前模型坐标的维度
        self.load_data(convertFile_name,publicFile_name,convert_points,public_points,encoding) # 加载数据
        self.model_name = '三参数转换模型'
    def A_coefficient(self,points):
        pass

    def fit(self):
        self.__public_points = self.Public_points
        self.isFitted = True
        X = np.mean((self.__public_points[:,3] - self.__public_points[:,0]).ravel())
        Y = np.mean((self.__public_points[:,4] - self.__public_points[:,1]).ravel())
        Z = np.mean((self.__public_points[:,5] - self.__public_points[:,2]).ravel())
        self.__prams_array = np.array([X,Y,Z])
        print(self.__prams_array)
        
        # 将公共点代入训练好的模型得到结果
        predict_points = self.predict(self.__public_points[:,:self.dimension]) 
        # 计算中误差矩阵
        self.MSE_array,self.MSE_point,self.__difference_array = self.RMSE(self.__public_points[:,self.dimension:], predict_points)  
        print(f'''
        模型：{self.model_name},
        坐标分量中误差为：{self.MSE_array},
        参数为:{self.__prams_array},
        点位中误差为：{self.MSE_point},
        坐标改正数为：{self.__difference_array}
        ''')
        return self.__prams_array

    def predict(self,test_array):
        '''预测新的坐标点'''
        if(self.isFitted == False):  #如果还未训练，先进行训练
            self.__prams_array = self.fit()

        return test_array + self.__prams_array
    
    
class XY_4p(IGxCRS_TransForXYZ):
    """此模型是平面四参数转换模型，适用于局部小区域平面坐标转换"""
    def __init__(self, convert_points = None, public_points = None,convertFile_name = None,publicFile_name = None, encoding = 'utf-8'):
        ''' 
        平面四参数转换模型转换模型参数说明：
        参数1支持待转换的浮点型二维数组，每个元素存储一个点坐标，(X,Y,Z)
        参数2支持公共点的浮点型二维数组，其中数量不少于2个，并且每个元素存储原坐标系坐标和新坐标系坐标(X1,Y1,X2,Y2)
        参数3支持待转换的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储一个点X,Y
        参数4支持公共点的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储两个点X1,Y1,X2,Y2,
        参数1、2或参数3、4为同时填入的参数
        '''
        self.public_num = 2 # 至少要求的公共点数量
        self.dimension = 2# 当前模型坐标的维度
        self.load_data(convertFile_name,publicFile_name,convert_points,public_points,encoding) # 加载数据
        self.model_name = '平面四参数转换模型'
        
    def A_coefficient(self,points):
        '''构建系数矩阵'''
        A = pd.DataFrame()
        for i in range(points.shape[0]):
            X = points[i,0]
            Y = points[i,1]
            array = np.array([[X,Y],[Y,X]])
            A_i = np.concatenate((np.eye(self.dimension),array), axis = 1)
            A = A.append(pd.DataFrame(A_i))
        A = np.array(A)
        return A
 
class Brusa_Wolf(IGxCRS_TransForXYZ):

    """此模型是布尔莎-沃尔夫七参数转换模型，适用于国家及省级空间直角坐标转换"""
    def __init__(self, convert_points = None, public_points = None,convertFile_name = None,publicFile_name = None, encoding = 'utf-8'):
        ''' 
        布尔莎七参数转换模型转换模型参数说明：
        参数1支持待转换的浮点型二维数组，每个元素存储一个点坐标，(X,Y)
        参数2支持公共点的浮点型二维数组，其中数量不少于3个，并且每个元素存储原坐标系坐标和新坐标系坐标(X1,Y1,Z1,X2,Y2,Z2)
        参数3支持待转换的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储一个点X,Y,Z
        参数4支持公共点的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储两个点X1,Y1,Z1,X2,Y2,Z2
        参数1、2或参数3、4为同时填入的参数
        '''
        self.public_num = 3 # 至少要求的公共点数量
        self.dimension = 3 # 当前模型坐标的维度
        self.load_data(convertFile_name,publicFile_name,convert_points,public_points,encoding) # 加载数据
        self.model_name = '布尔莎转换模型'
    def A_coefficient(self,points):
        '''构建系数矩阵'''
        A = pd.DataFrame()
        for i in range(points.shape[0]):
            X = points[i,0]
            Y = points[i,1]
            Z = points[i,2]
            array = np.array([[0,-Z,Y,X],[Z,0,-X,Y],[-Y,X,0,Z]])
            A_i = np.concatenate((np.eye(self.dimension),array), axis = 1)
            A = A.append(pd.DataFrame(A_i))
        A = np.array(A)
        return A
        
class Molokinsky(IGxCRS_TransForXYZ):

    """此模型是莫洛金斯基七参数转换模型，适用于国家及省级空间直角坐标转换"""
    def __init__(self, centry_point,convert_points = None, public_points = None,convertFile_name = None,publicFile_name = None, encoding = 'utf-8'):
        ''' 
        莫洛金斯基转换模型转换模型参数说明：
        参数1为莫洛金斯基在原坐标系下的旋转中心点(X,Y,Z)，类型为一维数组
        参数2支持待转换的浮点型二维数组，每个元素存储一个点坐标，(X,Y,Z)
        参数3支持公共点的浮点型二维数组，其中数量不少于3个，并且每个元素存储原坐标系坐标和新坐标系坐标(X1,Y1,Z1,X2,Y2,Z2)
        参数4支持待转换的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储一个点X,Y,Z
        参数5支持公共点的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储两个点X1,Y1,Z1,X2,Y2,Z2
        参数2、3或参数4、5为同时填入的参数
        '''
        self.public_num = 3 # 至少要求的公共点数量
        self.dimension = 3 # 当前模型坐标的维度
        self.load_data(convertFile_name,publicFile_name,convert_points,public_points,encoding) # 加载数据
        self.centry_point = centry_point # 过渡点，旋转中心
        self.Xp = self.centry_point[0]
        self.Yp = self.centry_point[1]
        self.Zp = self.centry_point[2]
        self.model_name = '莫洛金斯基模型'
    def A_coefficient(self,points):
        '''构建系数矩阵'''
        A = pd.DataFrame()
        for i in range(points.shape[0]):
            X = points[i,0]
            Y = points[i,1]
            Z = points[i,2]
            array = np.array([[0,-(Z-self.Zp),Y-self.Yp,X-self.Xp],[Z-self.Zp,0,-(X-self.Xp),Y-self.Yp],[-(Y-self.Yp),X-self.Xp,0,Z-self.Zp]])
            A_i = np.concatenate((np.eye(self.dimension),array), axis = 1)
            A = A.append(pd.DataFrame(A_i))
        A = np.array(A)
        return A

    def B_constant(self,points):
        B = pd.DataFrame()    
        for i in range(points.shape[0]):
            B = B.append([self.Xp,self.Yp,self.Zp])
        return np.array(B).ravel()
        
    def fit(self):
        '''通过公共点训练最小二乘法模型，并改正数、坐标分量中误差、点位中误差矩阵'''
        # 构建A
        self.__public_points = self.Public_points
        A = self.A_coefficient(self.__public_points)
        B = self.B_constant(self.__public_points)
        b = self.__public_points[:,self.dimension:].ravel() - B
        res = lsq_linear(A, b, lsmr_tol='auto')
        self.isFitted = True
        self.res = res
        # 将公共点代入训练好的模型得到结果
        predict_points = self.predict(self.__public_points[:,:self.dimension]) 
        # 计算中误差矩阵
        self.MSE_array,self.MSE_point,self.__difference_array = self.RMSE(self.__public_points[:,self.dimension:], predict_points)  
        print(f'''
        模型：{self.model_name},
        模型训练阶段:{self.res['message']},
        参数：{self.res['x']},
        坐标分量中误差为：{self.MSE_array},
        点位中误差为：{self.MSE_point},
        坐标改正数为：{self.__difference_array}
        ''')
        return self.res
        
class Ellipsoid(Enum):
    '''a为长半轴
    b为短半轴
    f为变率
    e1为第一偏心率平方
    e2为第二偏心率平方'''
    Beijing54={
        'a': 6378245.0000,
        'b': 6356863.0188,
        'f': 1/298.3,
        'e1': 0.006693421622966,
        'e2': 0.006738525414683,
        'EPSG':4214,

    }
    Xian80={
        'a': 6378140.0000,
        'b': 6356755.2882,
        'f': 1/298.257,
        'e1': 0.00669438499959,
        'e2': 0.00673950181947,
        'EPSG':4610
    }
    WGS84={
        'a': 6378137.0000,
        'b': 6356752.3142,
        'f': 1/298.257223563, 
        'e1': 0.00669437999013,
        'e2': 0.00673949674223,
        'EPSG':4326,
    }
    CGCS2000={
        'a': 6378137.00000,
        'b': 6356752.31414,
        'f': 1/298.257222101,
        'e1': 0.00669438002290,
        'e2': 0.00673949677548,
        'EPSG':4479
    }
    
    
class IGxCRS_TransForLBH(object):
    '''用于大地坐标转换模型参数的公共父类'''

    # 传入的转换点、公共点以及坐标改正矩阵是在模型训练好后不可修改的，只可以读取
    @property
    def Convert_points(self):
        return self.__convert_points
    @property
    def Public_points(self):
        return self.__public_points
    @property
    def Difference_array(self): 
        return self.__difference_array   
        
    def rad2angle(self,x):
        return 60/180 * np.pi
    
    def angle2rad(self,x):
        return x*np.pi/180.0
    
    def pram_n(self,ellipsoid,B):
        return ellipsoid['e2'] * np.power(np.cos(B),2)

    def pram_V(self,pram_n):
        return np.sqrt(1 + pram_n)
    
    def pram_W(self,ellipsoid,B):
        return np.sqrt(1 - ellipsoid['e1']*np.power(np.sin(B),2))
    
    def pram_c(self,ellipsoid):
        return np.power(ellipsoid['a'],2)/ellipsoid['b']
    
    def pram_M(self,c,V):
        return c/np.power(V,3)
    
    def pram_N(self,c,V):
        return c/V
        
    def load_data(self,convertFile_name,publicFile_name,convert_points,public_points,encoding,):
        self.isFitted = False # 是否拟合标志
        self.__difference_array = np.zeros(self.dimension) # 改正数矩阵
        if(convertFile_name != None and publicFile_name != None):
            try:
                with open('{}'.format(convertFile_name), 'r', encoding = encoding) as f:
                    convertFiledata = f.readlines()
                self.__convert_points = np.array([self.__str2floatList(line) for line in convertFiledata])
                with open('{}'.format(publicFile_name), 'r', encoding = encoding) as f:
                    publicFiledata = f.readlines()
                self.__public_points = np.array([self.__str2floatList(line) for line in publicFiledata])  
                if(len(self.__public_points) < self.public_num): return "公共点数量不足，请重新输入"
            except IOError:
                print(IOError)
                print("Error: 没有找到文件或读取文件失败，请检查格式或路径是否正确")
                return None
        elif(convert_points != None and public_points != None):
            if(len(public_points) < self.public_num): return "公共点数量不足，请重新输入"
            self.__convert_points = np.array(convert_points)
            self.__public_points = np.array(public_points)
        else:
            print("请检查输入参数是否正确")
            return None
        
    def __str2floatList(self,x):
        return list(map(float,x.strip().split(',')))        
    
    def fit(self):
        '''通过公共点训练最小二乘法模型，并改正数、坐标分量中误差、点位中误差矩阵'''
        # AX+C=Y 构建A,C,b，A为方程系数，C为常数项，Y为因变量，b = Y-C
        self.A,self.C,self.b = self.A_C_b(self.__public_points)
        res = lsq_linear(self.A, self.b, lsmr_tol='auto')
        self.isFitted = True
        self.res = res
        # 将公共点代入训练好的模型得到结果
        predict_points = self.predict(self.__public_points[:,:self.dimension]) 
        # 计算中误差矩阵
        self.MSE_array,self.MSE_point,self.__difference_array = self.RMSE(self.__public_points[:,self.dimension:], predict_points)  
        print(f'''
        模型：{self.model_name},
        模型训练阶段:{self.res['message']},
        参数：{self.res['x']},
        坐标分量中误差为：{self.MSE_array},
        坐标改正数为：{self.__difference_array}
        ''')
        return self.res
    
    def fit_transform(self):
        '''通过公共点训练最小二乘法模型，并且输出转换点的新坐标点'''
        predict_points = self.predict(self.__convert_points)
        return predict_points
    
    def predict(self,test_array, isCorrectLocation = False):
        '''预测新的坐标点'''
        if(self.isFitted == False):  #如果还未训练，先进行训练
            self.res = self.fit()
        A_test = self.A_coefficient(test_array)
        predict_points = test_array + (A_test.dot(self.res.x.ravel()) + self.C).reshape((-1, self.dimension))
        if(self.__difference_array.all() != 0 and isCorrectLocation == True): #如果坐标改正矩阵存在并且isCorrectLocation==True，则改正预测值
            return predict_points + self.__difference_array
        return predict_points
    
    def RMSE(self,train_points,result_points):
        '''评价并返回'''
        n = train_points.shape[0] - 1 
        correct_array = (np.sum(np.power(train_points - result_points,2), axis = 0) / (n-1)) # [vv]/n-1矩阵
        MSE_array = np.sqrt(correct_array) #  坐标分量中误差矩阵
        MSE_point = np.sqrt(np.sum(correct_array))  # 点位中误差值
        difference_array = np.sum(train_points - result_points, axis = 0) / n # 各坐标分量改正值
        return MSE_array,MSE_point,difference_array
    
    def A_coefficient(self,points):
        pass
    def A_C_b(self,points):
        pass

class BLH_7p(IGxCRS_TransForLBH):

    """此模型是三维七参数转换模型，适用于国家及省级大地坐标转换"""
    def __init__(self, convert_points = None, public_points = None,convertFile_name = None,publicFile_name = None, encoding = 'utf-8'):
        ''' 
        平面四参数转换模型转换模型参数说明：
        参数1支持待转换的浮点型二维数组，每个元素存储一个点坐标，(L,B,H)
        参数2支持公共点的浮点型二维数组，其中数量不少于3个，并且每个元素存储原坐标系坐标和新坐标系坐标(L1,B1,H1,L2,B2,H2)
        参数3支持待转换的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储一个点L,B,H
        参数4支持公共点的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储两个点L1,B1,H1,L2,B2,H2
        参数1、2或参数3、4为同时填入的参数
        '''
        self.public_num = 3 # 至少要求的公共点数量
        self.dimension = 3 # 当前模型坐标的维度
        self.load_data(convertFile_name,publicFile_name,convert_points,public_points,encoding) # 加载数据
        self.model_name = '三维七参数模型'
        
    def A_C_b(self,points):
        '''构建系数矩阵，常数向量C,向量b'''
        A = pd.DataFrame()
        C = pd.DataFrame()
        b = pd.DataFrame()
        ellipsoid = Ellipsoid['WGS84'].value      
        a = ellipsoid['a']
        f = ellipsoid['f']
        e2 = ellipsoid['e1']
        r = (180*3600)/ np.pi
        c = self.pram_c(ellipsoid)
        
        ellipsoid2 = Ellipsoid['Xian80'].value    
        a2 = ellipsoid2['a']
        f2 = ellipsoid2['f']
        a_ = a2 - a
        f_ = f2 - f
        a_f = np.array([a_,f_]).T
        for i in range(points.shape[0]):
            L = self.angle2rad(points[i,0])
            B = self.angle2rad(points[i,1])
            H = points[i,2]
            
            L2 = self.angle2rad(points[i,3])
            B2 = self.angle2rad(points[i,4])
            H2 = points[i,5]
            sinB = np.sin(B)
            cosB = np.cos(B)
            sinL = np.sin(L)
            cosL = np.cos(L)
            tgB = np.tan(B)

            n = self.pram_n(ellipsoid, B)
            V = self.pram_V(n)
            N = self.pram_N(c,V)
            M = self.pram_M(c,V)
            NH = N + H
            MH = M + H

            
            A11 = -sinL / (NH*cosB) * r
            A12 = cosL / (NH*cosB) * r
            A13 = 0
            A14 = tgB * cosL
            A15 = tgB * sinL
            A16 = -1
            A17 = 0
            
            A21 = -sinB*cosL/MH * r
            A22 = -sinB*sinL/MH * r
            A23 = cosB/MH * r
            A24 = -sinL
            A25 = cosL
            A26 = 0
            A27 = -N/MH * e2 * sinB * cosB * r
            
            A31 = cosB*cosL
            A32 = sinB*sinL
            A33 = sinB
            A34 = -N*e2*sinB*cosB*sinL/r
            A35 = N*e2*sinB*cosB*cosL/r
            A36 = 0
            A37 = NH - N*e2*(sinB**2)

            A_i = np.array([[A11, A12, A13, A14, A15, A16, A17],
                             [A21, A22, A23, A24, A25, A26, A27],
                             [A31, A32, A33, A34, A35, A36, A37]])
            A = A.append(pd.DataFrame(A_i))
            
            e2sinB2 = e2*(sinB**2)
            C11 = 0
            C12 = 0
            C21 = N/(MH*a)*e2*sinB*cosB*r
            C22 = M*(2-e2sinB2)/(MH*(1 - f))*sinB*cosB*r
            C31 = -N/a*(1 - e2sinB2)
            C32 = M/(1-f)*(1 - e2sinB2)*(sinB**2)
            
            C_i = np.array([[C11,C12],[C21,C22],[C31,C32]]).dot(a_f)
            b_i = np.array([L2-L,B2-B,H2-H])
            C = C.append(pd.DataFrame(C_i))
            b = b.append(pd.DataFrame(b_i))
        A = np.array(A)
        C = np.array(C).ravel()
        b = np.array(b).ravel() - C
        return A,C,b
        
    def A_coefficient(self,points):
        '''构建系数矩阵'''
        A = pd.DataFrame()

        ellipsoid = Ellipsoid['WGS84'].value      
        a = ellipsoid['a']
        f = ellipsoid['f']
        e2 = ellipsoid['e1']
        r = (180*3600)/ np.pi
        c = self.pram_c(ellipsoid)

        for i in range(points.shape[0]):
            L = self.angle2rad(points[i,0])
            B = self.angle2rad(points[i,1])
            H = points[i,2]
            
            sinB = np.sin(B)
            cosB = np.cos(B)
            sinL = np.sin(L)
            cosL = np.cos(L)
            tgB = np.tan(B)

            n = self.pram_n(ellipsoid, B)
            V = self.pram_V(n)
            N = self.pram_N(c,V)
            M = self.pram_M(c,V)
            NH = N + H
            MH = M + H

            
            A11 = -sinL / (NH*cosB) * r
            A12 = cosL / (NH*cosB) * r
            A13 = 0
            A14 = tgB * cosL
            A15 = tgB * sinL
            A16 = -1
            A17 = 0
            
            A21 = -sinB*cosL/MH * r
            A22 = -sinB*sinL/MH * r
            A23 = cosB/MH * r
            A24 = -sinL
            A25 = cosL
            A26 = 0
            A27 = -N/MH * e2 * sinB * cosB * r
            
            A31 = cosB*cosL
            A32 = sinB*sinL
            A33 = sinB
            A34 = -N*e2*sinB*cosB*sinL/r
            A35 = N*e2*sinB*cosB*cosL/r
            A36 = 0
            A37 = NH - N*e2*(sinB**2)

            A_i = np.array([[A11, A12, A13, A14, A15, A16, A17],
                             [A21, A22, A23, A24, A25, A26, A27],
                             [A31, A32, A33, A34, A35, A36, A37]])
            A = A.append(pd.DataFrame(A_i))

        A = np.array(A)

        return A       

class BL_7p(IGxCRS_TransForLBH):

    """此模型是二维七参数转换模型，适用于局部坐标系的坐标转换，区域<2*2°"""
    def __init__(self, convert_points = None, public_points = None,convertFile_name = None,publicFile_name = None, encoding = 'utf-8'):
        ''' 
        平面四参数转换模型转换模型参数说明：
        参数1支持待转换的浮点型二维数组，每个元素存储一个点坐标，(L,B)
        参数2支持公共点的浮点型二维数组，其中数量不少于3个，并且每个元素存储原坐标系坐标和新坐标系坐标(L1,B1,L2,B2)
        参数3支持待转换的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储一个点L,B
        参数4支持公共点的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储两个点L1,B1,L2,B2
        参数1、2或参数3、4为同时填入的参数
        '''
        self.public_num = 2 # 至少要求的公共点数量
        self.dimension = 2 # 当前模型坐标的维度
        self.load_data(convertFile_name,publicFile_name,convert_points,public_points,encoding) # 加载数据
        self.model_name = '二维七参数模型'
        
    def A_C_b(self,points):
        '''构建系数矩阵，常数向量C,向量b'''
        A = pd.DataFrame()
        C = pd.DataFrame()
        b = pd.DataFrame()
        ellipsoid = Ellipsoid['WGS84'].value      
        a = ellipsoid['a']
        f = ellipsoid['f']
        e2 = ellipsoid['e1']
        r = (180*3600)/ np.pi
        c = self.pram_c(ellipsoid)
        
        ellipsoid2 = Ellipsoid['Xian80'].value    
        a2 = ellipsoid2['a']
        f2 = ellipsoid2['f']
        a_ = a2 - a
        f_ = f2 - f
        a_f = np.array([a_,f_]).T
        for i in range(points.shape[0]):
            L = self.angle2rad(points[i,0])
            B = self.angle2rad(points[i,1])
            
            L2 = self.angle2rad(points[i,2])
            B2 = self.angle2rad(points[i,3])

            sinB = np.sin(B)
            cosB = np.cos(B)
            sinL = np.sin(L)
            cosL = np.cos(L)
            tgB = np.tan(B)

            n = self.pram_n(ellipsoid, B)
            V = self.pram_V(n)
            N = self.pram_N(c,V)
            M = self.pram_M(c,V)
            
            A11 = -sinL/(N*cosB)*r
            A12 = cosL/(N*cosB)*r
            A13 = 0
            A14 = tgB*cosL
            A15 = tgB*sinL
            A16 = -1
            A17 = 0
            
            A21 = -sinB*cosL/M * r
            A22 = -sinB*sinL/M * r
            A23 = cosB/M * r
            A24 = -sinL
            A25 = cosL
            A26 = 0
            A27 = -N/M*e2*sinB*cosB*r

            A_i = np.array([[A11, A12, A13, A14, A15, A16, A17],
                             [A21, A22, A23, A24, A25, A26, A27],])
            A = A.append(pd.DataFrame(A_i))
            
            e2sinB2 = e2*(sinB**2)
            C11 = 0
            C12 = 0
            C21 = N/(M*a)*e2*sinB*cosB*r
            C22 = (2-e2sinB2)/(1-f)*sinB*cosB*r
            
            C_i = np.array([[C11,C12],[C21,C22]]).dot(a_f)
            b_i = np.array([L2-L,B2-B])
            C = C.append(pd.DataFrame(C_i))
            b = b.append(pd.DataFrame(b_i))
        A = np.array(A)
        C = np.array(C).ravel()
        b = np.array(b).ravel() - C
        return A,C,b
        
    def A_coefficient(self,points):
        '''构建系数矩阵'''
        A = pd.DataFrame()

        ellipsoid = Ellipsoid['WGS84'].value      
        a = ellipsoid['a']
        f = ellipsoid['f']
        e2 = ellipsoid['e1']
        r = (180*3600)/ np.pi
        c = self.pram_c(ellipsoid)

        for i in range(points.shape[0]):
            L = self.angle2rad(points[i,0])
            B = self.angle2rad(points[i,1])

            sinB = np.sin(B)
            cosB = np.cos(B)
            sinL = np.sin(L)
            cosL = np.cos(L)
            tgB = np.tan(B)

            n = self.pram_n(ellipsoid, B)
            V = self.pram_V(n)
            N = self.pram_N(c,V)
            M = self.pram_M(c,V)

            A11 = -sinL/(N*cosB)*r
            A12 = cosL/(N*cosB)*r
            A13 = 0
            A14 = tgB*cosL
            A15 = tgB*sinL
            A16 = -1
            A17 = 0
            
            A21 = -sinB*cosL/M * r
            A22 = -sinB*sinL/M * r
            A23 = cosB/M * r
            A24 = -sinL
            A25 = cosL
            A26 = 0
            A27 = -N/M*e2*sinB*cosB*r

            A_i = np.array([[A11, A12, A13, A14, A15, A16, A17],
                             [A21, A22, A23, A24, A25, A26, A27],])

            A = A.append(pd.DataFrame(A_i))

        A = np.array(A)

        return A        
        
class XYZ_4p(IGxCRS_TransForXYZ):

    """此模型是三维四参数参数转换模型，适用于国家及省级空间直角坐标转换"""
    def __init__(self,centry_point, convert_points = None, public_points = None,convertFile_name = None,publicFile_name = None, encoding = 'utf-8'):
        ''' 
        平面四参数转换模型转换模型参数说明：
        参数1支持待转换的浮点型二维数组，每个元素存储一个点坐标，(X,Y)
        参数2支持公共点的浮点型二维数组，其中数量不少于3个，并且每个元素存储原坐标系坐标和新坐标系坐标(X1,Y1,Z1,X2,Y2,Z2)
        参数3支持待转换的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储一个点X,Y,Z
        参数4支持公共点的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储两个点X1,Y1,Z1,X2,Y2,Z2
        参数5为测区内中心点P0对应的大地经纬度[B0,L0]
        参数1、2、5或参数3、4、5为同时填入的参数
        '''
        self.public_num = 2 # 至少要求的公共点数量
        self.dimension = 3 # 当前模型坐标的维度
        self.load_data(convertFile_name,publicFile_name,convert_points,public_points,encoding) # 加载数据
        self.model_name = '三维四参数转换模型'
        self.centry_point = centry_point
    def angle2rad(self,x):
        return x*np.pi/180.0
    def A_coefficient(self,points):
        '''构建系数矩阵'''
        B = self.centry_point[0]
        L = self.centry_point[1]
        cosB = angle2rad(B)
        sinL = angle2rad(L)
        A = pd.DataFrame()
        for i in range(points.shape[0]):
            X = points[i,0]
            Y = points[i,1]
            Z = points[i,2]
            array = np.array([[Z*cosB*sinL - Y*sinB],[-Z*cosB*cosL + X*sinB],[Y*cosB*cosL - X*cosB*sinL]])
            A_i = np.concatenate((np.eye(self.dimension),array), axis = 1)
            A = A.append(pd.DataFrame(A_i))
        A = np.array(A)
        return A
        
class Poly_fit(object):

    """此模型是平面多项式拟合模型，适用于小地区坐标转换"""
    # 传入的转换点、公共点以及坐标改正矩阵是在模型训练好后不可修改的，只可以读取
    @property
    def Convert_points(self):
        return self.__convert_points
    @property
    def Public_points(self):
        return self.__public_points
    @property
    def Difference_array(self): 
        return self.__difference_array   
    
    def __init__(self,n = 2, convert_points = None, public_points = None,convertFile_name = None,publicFile_name = None, encoding = 'utf-8'):
        ''' 
        平面四参数转换模型转换模型参数说明：
        参数1支持待转换的浮点型二维数组，每个元素存储一个点坐标，(X,Y)或(B,L)
        参数2支持公共点的浮点型二维数组，其中数量不少于3个，并且每个元素存储原坐标系坐标和新坐标系坐标(X1,Y1,X2,Y2)或(B1,L1,B2,L2)
        参数3支持待转换的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储一个点(X,Y)或(B,L)
        参数4支持公共点的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储两个点(X1,Y1,X2,Y2)或(B1,L1,B2,L2)
        参数1、2或参数3、4为同时填入的参数
        '''
        if(n == 2):
            self.public_num = 2# 至少要求的公共点数量
        elif(n == 3):
            self.public_num = 4
        self.dimension = 2 # 当前模型坐标的维度
        self.load_data(convertFile_name,publicFile_name,convert_points,public_points,encoding) # 加载数据
        self.model_name = '平面多项式拟合模型'
        self.n = n

    def load_data(self,convertFile_name,publicFile_name,convert_points,public_points,encoding,):
        self.isFitted = False # 是否拟合标志
        self.__difference_array = np.zeros(self.dimension) # 改正数矩阵
        if(convertFile_name != None and publicFile_name != None):
            try:
                with open('{}'.format(convertFile_name), 'r', encoding = encoding) as f:
                    convertFiledata = f.readlines()
                self.__convert_points = np.array([self.__str2floatList(line) for line in convertFiledata])
                with open('{}'.format(publicFile_name), 'r', encoding = encoding) as f:
                    publicFiledata = f.readlines()
                self.__public_points = np.array([self.__str2floatList(line) for line in publicFiledata])  
                if(len(self.__public_points) < self.public_num): return "公共点数量不足，请重新输入"
            except IOError:
                print(IOError)
                print("Error: 没有找到文件或读取文件失败，请检查格式或路径是否正确")
                return None
        elif(convert_points != None and public_points != None):
            if(len(public_points) < self.public_num): return "公共点数量不足，请重新输入"
            self.__convert_points = np.array(convert_points)
            self.__public_points = np.array(public_points)
        else:
            print("请检查输入参数是否正确")
            return None
        
    def __str2floatList(self,x):
        return list(map(float,x.strip().split(',')))      
    
    def angle2rad(self,x):
        return x*np.pi/180.0
    
    def A_coefficient(self,points):
        '''构建系数矩阵'''
        A = pd.DataFrame()
        if(self.n == 2):
            for i in range(points.shape[0]):
                L = self.angle2rad(points[i,1])
                B = self.angle2rad(points[i,0]) 
                A11 = 1 
                A12 = B
                A13 = L
                A14 = B*L
                A15 = B**2
                A16 = L**2
                A_i = np.array([[A11,A12,A13,A14,A15,A16]])
                A = A.append(pd.DataFrame(A_i))

        elif(self.n == 3):
            for i in range(points.shape[0]):
                L = self.angle2rad(points[i,1])
                B = self.angle2rad(points[i,0]) 
                A11 = 1
                A12 = B
                A13 = L
                A14 = B**2
                A15 = B*L
                A16 = L**2
                A17 = B**3
                A18 = (B**2)*L
                A19 = B*(L**2)
                A10 = L**3
                A_i = np.array([[A11,A12,A13,A14,A15,A16,A17,A18,A19,A10]])
                A = A.append(pd.DataFrame(A_i))
        A = np.array(A)
        return A
        
    def fit(self):
        '''通过公共点训练最小二乘法模型，并获得改正数、坐标分量中误差、点位中误差矩阵'''
        # 构建A
        A = self.A_coefficient(self.__public_points)
        # 构建b
        b1= self.__public_points[:,2] - self.__public_points[:,0]
        b1= b1.ravel()
        b2= self.__public_points[:,3] - self.__public_points[:,1]
        b2= b2.ravel()
        
        self.isFitted = True        
        res1 = lsq_linear(A, b1, lsmr_tol='auto')
        res2 = lsq_linear(A, b2, lsmr_tol='auto')
        self.res1 = res1
        self.res2 = res2        
        # 将公共点代入训练好的模型得到结果
        predict_points_B,predict_points_L = self.predict(self.__public_points[:,:self.dimension]) 
        predict_points = np.array([predict_points_B,predict_points_L]).T
        # 计算中误差矩阵
        self.MSE_array,self.MSE_point,self.__difference_array = self.RMSE(self.__public_points[:,self.dimension:4], predict_pointspredict_points)  
        print(f'''
        模型：{self.model_name},
        模型训练阶段:{self.res1['message']},
        参数1：{self.res1['x']},
        参数2：{self.res2['x']},
        坐标分量中误差为：{self.MSE_array},
        点位中误差为：{self.MSE_point},
        坐标改正数为：{self.__difference_array}
        ''')
        return self.res1,self.res2
    
    def fit_transform(self,isCorrectLocation = False):
        '''通过公共点训练最小二乘法模型，并且输出转换点的新坐标点'''
        predict_points_L,predict_points_B = self.predict(self.__public_points[:,:self.dimension]) 
        predict_points = np.array([predict_points_L,predict_points_B]).T
        return predict_points
    
    def predict(self,test_array, isCorrectLocation = False):
        '''预测新的坐标点'''
        if(self.isFitted == False):  #如果还未训练，先进行训练
            self.fit()
        A_test = self.A_coefficient(test_array)
        L1_test = test_array[:,0].ravel()
        L2_test = test_array[:,1].ravel()
        predict_points_B = (A_test.dot(self.res1.x.ravel()) + L1_test).ravel()
        predict_points_L = (A_test.dot(self.res2.x.ravel()) + L2_test).ravel()
        if(self.__difference_array.all() != 0 and isCorrectLocation == True): #如果坐标改正矩阵存在并且isCorrectLocation==True，则改正预测值
            return predict_points + self.__difference_array
        return predict_points_B,predict_points_L
    
    def RMSE(self,train_points,result_points):
        '''评价并返回'''
        n = train_points.shape[0] - 1 
        correct_array = (np.sum(np.power(train_points - result_points,2), axis = 0) / (n-1)) # [vv]/n-1矩阵
        MSE_array = np.sqrt(correct_array) #  坐标分量中误差矩阵
        MSE_point = np.sqrt(np.sum(correct_array))  # 点位中误差值
        difference_array = np.sum(train_points - result_points, axis = 0) / n # 各坐标分量改正值
        return MSE_array,MSE_point,difference_array


    

        
class Gaussian(object):
    """此模型是高斯格吕格正反算模型，经纬度与XY坐标的相互转换"""
    def __init__(self,interval,ellipsoid,convert_points = None,convertFile_name = None, encoding = 'utf-8'):
        ''' 
        高斯格吕格正反算模型参数说明：
        参数1为当前分度带为3°带还是6°带
        参数2为当中标系参数，枚举型
        参数3支持待转换的浮点型二维数组，每个元素存储一个点坐标，(X,Y)或(B,L)
        参数3支持待转换的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储一个点X,Y或B,L
        '''

        self.model_name = '高斯格吕格模型'
        self.load_data(convertFile_name,convert_points,encoding)
        self.ellipsoid = ellipsoid.value
        self.staticPrams_init(self.ellipsoid)
        if(interval == 3 or interval == 6):
            self.interval = interval
        else:
            return '请输入正确的分带值'
    def load_data(self,convertFile_name,convert_points,encoding,):
        if(convertFile_name != None):
            try:
                with open('{}'.format(convertFile_name), 'r', encoding = encoding) as f:
                    convertFiledata = f.readlines()
                self.__convert_points = np.array([self.__str2floatList(line) for line in convertFiledata])
                self.dimension = self.__convert_points.shape[1]/2 # 当前模型坐标的维度
                self.__predict = self.define_model() # 根据输入的是XY还是BL动态定义正反算模型
            except IOError:
                print(IOError)
                print("Error: 没有找到文件或读取文件失败，请检查格式或路径是否正确")
                return None
        elif(convert_points != None ):
            self.__convert_points = np.array(convert_points)
            self.__predict = self.define_model()
        else:
            print("请检查输入参数是否正确")
            return None
        
    def __str2floatList(self,x):
        return list(map(float,x.strip().split(',')))      
    
    def define_model(self):
        '''根据数值的大小判断定义正算模型还是反算模型'''
        if(np.abs(self.__convert_points[0][0]) < 1000) :
            # 动态定义高斯正算模型
            print('根据数据，自动定义为高斯正算模型')
            def predict(self, array = None):
                if(array != None):
                    self.__convert_points = array
                result = []
                if(self.interval == 6):
                    self.N0 = np.ceil(self.__convert_points[0][1]/6) #6度带带号
                    L0 = 6*self.N0 - 3
                    for i in self.__convert_points:
                        B = i[0]
                        L = i[1]
                        l = L - L0
                        l = self.angle2rad(l)
                        B = self.angle2rad(B)
                        X = self.pram_X(self.a0,self.a2,self.a4,self.a6,B)
                        n = self.pram_n(self.ellipsoid,B)
                        c = self.pram_c(self.ellipsoid)
                        V = self.pram_V(n)
                        N = self.pram_N(c,V)
                        t = np.tan(B)
                        cosB = np.cos(B)
                        sinB = np.sin(B)
                        result.append(self.BL2XY(X,N,sinB,cosB,t,l,n))
                
                elif(self.interval == 3):
                    self.N0=np.ceil((self.__convert_points[0][1] - 1.5)/3) #3度带带号
                    L0 = 3*self.N0
                    for i in self.__convert_points:
                        B = i[0]
                        L = i[1]
                        l = L - L0
                        l = self.angle2rad(l)
                        B = self.angle2rad(B)
                        X = self.pram_X(self.a0,self.a2,self.a4,self.a6,B)
                        n = self.pram_n(self.ellipsoid,B)
                        c = self.pram_c(self.ellipsoid)
                        V = self.pram_V(n)
                        N = self.pram_N(c,V)
                        t = np.tan(B)
                        cosB = np.cos(B)
                        sinB = np.sin(B)
                        result.append(self.BL2XY(X,N,sinB,cosB,t,l,n))
                return result    
        else:
            # 动态定义高斯反算模型
            print('根据数据，自动定义为高斯反算模型')
            def predict(self, L0, array = None):
                N0 = (L0 + 3)/self.interval
                if(array != None):
                    self.__convert_points = array
                result = []
                for i in self.__convert_points:
                    x = i[0]
                    y = i[1] - N0*1000000 - 500000
                    B0 = x/self.a0
                    FBf = -self.a2/2*np.sin(2*B0) + self.a4/4*np.sin(4*B0) - self.a6/6*np.sin(6*B0) + self.a8/8*np.sin(8*B0) 
                    Bf = (x - FBf)/self.a0
                    while(np.abs(Bf - B0) > 4.8e-10): # 迭代法求解底店纬度Bf
                        B0 = Bf
                        FBf = -self.a2/2*np.sin(2*B0) + self.a4/4*np.sin(4*B0) - self.a6/6*np.sin(6*B0) + self.a8/8*np.sin(8*B0) 
                        Bf = (x - FBf)/self.a0
                    tf = np.tan(Bf)
                    cosBf = np.cos(Bf)
                    sinBf = np.sin(Bf)
                    Nf = self.a/np.sqrt((1-self.e1*sinBf**2))
                    Mf = self.a*(1-self.e1)/np.sqrt(np.power((1-self.e1*cosBf),3))
                    nf = self.e2*np.cos(Bf)
                    tf = np.tan(Bf)
                    cosBf = np.cos(Bf)
                    sinBf = np.sin(Bf)
                    result.append(self.XY2BL(Bf,Mf,Nf,nf,cosBf,sinBf,tf,L0,y))
                return result   
        return predict
                
    def staticPrams_init(self,ellipsoid):
        self.e1 = ellipsoid['e1']
        self.e2 = ellipsoid['e2']
        self.a = ellipsoid['a']
        self.m0 = self.a*(1-self.e1)
        self.m2 = 3/2*self.e1*self.m0
        self.m4 = 5/4*self.e1*self.m2
        self.m6 = 7/6*self.e1*self.m4
        self.m8 = 9/8*self.e1*self.m6
        self.a0 = self.m0 + self.m2/2 + 3/8*self.m4 + 5/16*self.m6 + 35/128*self.m8
        self.a2 = self.m2/2 + self.m4/2 +15/32*self.m6 + 7/16*self.m8
        self.a4 = self.m4/8 + 3/16*self.m6 + 7/32*self.m8
        self.a6 = self.m6/32 + self.m8/16
        self.a8 = self.m8/128        
    
    def pram_X(self,a0,a2,a4,a6, B):
        sin2B = np.sin(2*B)
        sin4B = np.sin(4*B)
        sin6B = np.sin(6*B)
        return a0*B - a2/2*sin2B + a4/4*sin4B - a6/6*sin6B
    
    def predict(self, array = None, L0 = None):
        '''若为高斯反算模型，请添加关键字参数 L0 = 中央经度'''
        if L0 != None:
            return self.__predict(self, L0, array)
        else:
            return self.__predict(self, array)
    
    def angle2rad(self,x):
        return x*np.pi/180.0
        
    def rad2angel(self,x):
        return x*180/np.pi
        
    def pram_V(self,pram_n):
        return np.sqrt(1 + pram_n**2)
    
    def pram_n(self,ellipsoid,B):
        return np.sqrt(ellipsoid['e2']) * np.cos(B) 
    
    def pram_V(self,pram_n):
        return np.sqrt(1 + pram_n**2)
    
    def pram_c(self,ellipsoid):
        return np.power(ellipsoid['a'],2)/ellipsoid['b']
    
    def pram_M(self,c,V):
        return c/np.power(V,3)
    
    def pram_N(self,c,V):
        return c/V
    
    def BL2XY(self,X,N,sinB,cosB,t,l,n):
        x = X + N/2*sinB*cosB*np.power(l,2) + N/24*sinB*np.power(cosB,3)*(5-t**2 + 9*n**2 + 4*n**4)*np.power(l,4) + N/720*sinB*np.power(cosB,5)*(61-58*np.power(t,2)+np.power(t,4))*np.power(l,6)
        y = N*cosB*l + N/6*np.power(cosB,3)*(1-np.power(t,2)+np.power(n,2))*np.power(l,3) + N/120*np.power(cosB,5)*(5-18*np.power(t,2)+np.power(t,4)+14*np.power(n,2)-58*np.power(n*t,2))*np.power(l,5)
        return (x,y+self.N0*1000000 + 500000)
    
    def XY2BL(self,Bf,Mf,Nf,nf,cosBf,sinBf,tf,L0,y):
        B = Bf - tf/(2*Mf*Nf)*np.power(y,2) + tf/(24*Mf*np.power(Nf,3))*(5+3*np.power(tf,3)+np.power(nf,2)-9*np.power(nf,2)*np.power(tf,2))*np.power(y,4)  - tf/(720*Mf*np.power(Nf,5))*(61+90*np.power(tf,2)+45*np.power(tf,4))*np.power(y,6)
        l = 1/(Nf*cosBf)*y - 1/(6*Nf**3*cosBf)*(1+2*tf**2+nf**2)*y**3 + 1/(120*Nf**5*cosBf)*(5+28*tf**2+24*tf**4+6*nf**2+8*(nf*tf)**2)*y**5
        return self.rad2angel(B),L0+self.rad2angel(l)     


class XYZ_BLH(object):
    """此模型是同一椭球体下XYZ_BLH正反算模型"""
    def __init__(self,ellipsoid,convert_points = None,convertFile_name = None, encoding = 'utf-8'):
        ''' 
        三维坐标正反算模型参数说明：
        参数1为当中标系参数，枚举型
        参数2支持待转换的浮点型二维数组，每个元素存储一个点坐标，(X,Y,Z)或(B,L,H)
        参数3支持待转换的txt、csv文件的路径，文件数据要求以","作为分隔符，每行存储一个点X,Y,Z或B,L,H
        '''

        self.model_name = 'XYZ_BLH正反算模型'
        self.load_data(convertFile_name,convert_points,encoding)
        self.ellipsoid = ellipsoid.value
        self.staticPrams_init(self.ellipsoid)
    def load_data(self,convertFile_name,convert_points,encoding,):
        if(convertFile_name != None):
            try:
                with open('{}'.format(convertFile_name), 'r', encoding = encoding) as f:
                    convertFiledata = f.readlines()
                self.__convert_points = np.array([self.__str2floatList(line) for line in convertFiledata])
                self.dimension = self.__convert_points.shape[1]/2 # 当前模型坐标的维度
                self.__predict = self.define_model() # 根据输入的是XY还是BL动态定义正反算模型
            except IOError:
                print(IOError)
                print("Error: 没有找到文件或读取文件失败，请检查格式或路径是否正确")
                return None
        elif(convert_points != None ):
            self.__convert_points = np.array(convert_points)
            self.__predict = self.define_model()
        else:
            print("请检查输入参数是否正确")
            return None
        
    def __str2floatList(self,x):
        return list(map(float,x.strip().split(',')))      
    
    def define_model(self):
        '''根据数值的大小判断定义正算模型还是反算模型'''
        if(np.abs(self.__convert_points[0][0]) < 1000) :
            # 动态定义为BLH到XYZ转换模型
            print('根据数据，自动定义为BLH到XYZ转换模型')
            def predict(self, array = None):
                if(array != None):
                    self.__convert_points = array
                result = []
                for i in self.__convert_points:
                    B = i[0]
                    L = i[1]
                    H = i[2]
                    L = self.angle2rad(L)
                    B = self.angle2rad(B)
                    n = self.pram_n(self.ellipsoid,B)
                    c = self.pram_c(self.ellipsoid)
                    V = self.pram_V(n)
                    N = self.pram_N(c,V)
                    result.append(self.BLH2XYZ(B,L,H,N))
                return result    
        else:
            # 动态定义为XYZ到BLH转换模型
            print('根据数据，自动定义为XYZ到BLH转换模型')
            def predict(self, array = None):
                if(array != None):
                    self.__convert_points = array
                result = []
                for i in self.__convert_points:
                    X = i[0]
                    Y = i[1]
                    Z = i[2]
                    result.append(self.XYZ2BLH(X,Y,Z))
                return result     
        return predict
                
    def staticPrams_init(self,ellipsoid):
        self.e1 = ellipsoid['e1']
        self.e2 = ellipsoid['e2']
        self.a = ellipsoid['a']
        self.m0 = self.a*(1-self.e1)
        self.m2 = 3/2*self.e1*self.m0
        self.m4 = 5/4*self.e1*self.m2
        self.m6 = 7/6*self.e1*self.m4
        self.m8 = 9/8*self.e1*self.m6
        self.a0 = self.m0 + self.m2/2 + 3/8*self.m4 + 5/16*self.m6 + 35/128*self.m8
        self.a2 = self.m2/2 + self.m4/2 +15/32*self.m6 + 7/16*self.m8
        self.a4 = self.m4/8 + 3/16*self.m6 + 7/32*self.m8
        self.a6 = self.m6/32 + self.m8/16
        self.a8 = self.m8/128        
    
    def pram_X(self,a0,a2,a4,a6, B):
        sin2B = np.sin(2*B)
        sin4B = np.sin(4*B)
        sin6B = np.sin(6*B)
        return a0*B - a2/2*sin2B + a4/4*sin4B - a6/6*sin6B
    
    def predict(self,array = None):
        return self.__predict(self, array)
    
    def angle2rad(self,x):
        return x*np.pi/180.0
        
    def rad2angle(self,x):
        return x*180/np.pi
        
    def pram_V(self,pram_n):
        return np.sqrt(1 + pram_n**2)
    
    def pram_n(self,ellipsoid,B):
        return np.sqrt(ellipsoid['e2']) * np.cos(B) 
    
    def pram_V(self,pram_n):
        return np.sqrt(1 + pram_n**2)
    
    def pram_c(self,ellipsoid):
        return np.power(ellipsoid['a'],2)/ellipsoid['b']
    
    def pram_M(self,c,V):
        return c/np.power(V,3)
    
    def pram_N(self,c,V):
        return c/V
    
    def BLH2XYZ(self,B,L,H,N):
        cosB = np.cos(B)
        cosL = np.cos(L)
        sinB = np.sin(B)
        sinL = np.sin(L)
        X = (N+H)*cosB*cosL
        Y = (N+H)*cosB*sinL
        Z = (N*(1 - self.e1) + H)*sinB
        return (X,Y,Z)
    
    def XYZ2BLH(self,X,Y,Z):
        sqrt = np.sqrt
        sin = np.sin
        cos = np.cos
        atan = np.arctan
        e = sqrt(self.e1)
        if X == 0 and Y > 0:
            L = 90
        elif X == 0 and Y < 0:
            L = -90
        elif X < 0 and Y >= 0:
            L = atan(Y/X)
            L = self.rad2angle(L)
            L = L+180
        elif X < 0 and Y <= 0:
            L = atan(Y/X)
            L = self.rad2angle(L)
            L = L-180
        else:
            L = atan(Y / X)
            L = self.rad2angle(L)
            
        sqrtXY = sqrt(X**2+Y**2)
        b0 = atan(Z/sqrtXY)
        N = self.a/sqrt((1-e*e*sin(b0)*sin(b0)))

        H0 = 1e9
        H1 =  sqrtXY/cos(b0)-N
    
        while abs(H1-H0) > 0.0001:
            b0 = atan(Z / ((1 - self.e1*N/(N+H1))*sqrtXY))
            N = self.a / sqrt((1 - self.e1 * sin(b0) * sin(b0)))
            H0,H1 = H1,sqrt(X**2+Y**2)/cos(b0)-N

    
        B = self.rad2angle(b0)
        return B, L, H1   # 返回大地纬度B、经度L、海拔高度H (m)
        

def WarpPerspectiveMatrix(src, dst):
    assert src.shape[0] == dst.shape[0] and src.shape[0] >= 4
    
    nums = src.shape[0]
    A = np.zeros((2*nums, 8)) # A*warpMatrix=B
    B = np.zeros((2*nums, 1))
    for i in range(0, nums):
        A_i = src[i,:]
        B_i = dst[i,:]
        A[2*i, :] = [A_i[0], A_i[1], 1, 0, 0, 0,
                       -A_i[0]*B_i[0], -A_i[1]*B_i[0]]
        B[2*i] = B_i[0]
        
        A[2*i+1, :] = [0, 0, 0, A_i[0], A_i[1], 1,
                       -A_i[0]*B_i[1], -A_i[1]*B_i[1]]
        B[2*i+1] = B_i[1]
 
    A = np.mat(A)
    #用A.I求出A的逆矩阵，然后与B相乘，求出warpMatrix
    warpMatrix = A.I * B #求出a_11, a_12, a_13, a_21, a_22, a_23, a_31, a_32
    
    #之后为结果的后处理
    warpMatrix = np.array(warpMatrix).T[0]
    warpMatrix = np.insert(warpMatrix, warpMatrix.shape[0], values=1.0, axis=0) #插入a_33 = 1
    warpMatrix = warpMatrix.reshape((3, 3))
    return warpMatrix