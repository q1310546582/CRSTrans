#_*_ coding: utf-8 _*_

from zope.interface import Interface, Attribute
from zope.interface.declarations import implementer
from enum import Enum

from CoordTransformAlgorithms.Parameters import GxEarthParams

class IGxCoordinatePoint(Interface):
    '''XorB:X坐标或B坐标, YorL:Y坐标或L坐标, ZorH:Z坐标或H坐标,Band:投影带号'''
    Attribute('XorB', 'YorL', 'ZorH','Band')

class IGxCoordinatePointPair(Interface):
    '''控制点坐标对，用于计算四参数或七参数
    GUID:唯一标识码, CoordinateType:坐标格式, SourceXorB:源X坐标或B纬度,SourceYorL:源Y坐标或L经度,
    SourceZorH:源大地高或者空间坐标Z,TargetXorB:目标X坐标或B纬度,TargetYorL:目标Y坐标或L经度,TargetZorH:
    目标大地高或者空间坐标Z, ResidualX,ResidualY,ResidualZ:残差X,Y,Z, MeadianError:中误差
    '''
    Attribute('GUID','CoordinateType','SourceXorB', 'SourceYorL', 'SourceZorH', 
              'TargetXorB', 'TargetYorL', 'TargetZorH', 'ResidualX', 'ResidualY', 
              'ResidualZ', 'MeadianError')

class IGxGaussTransferHelper(Interface):
    '''高斯变换计算类'''
    Attribute('EarthParams', 'CentralMeridian', 'FalseEasting')
    def GaussPositiveTransformer(self, coordinatePoint):
        '''高斯正算
        输入：CoordinatePoint,输入的坐标点,(B,L)格式坐标，单位:度
        输出：返回(X,Y)格式的坐标点IGxCoordinatePoint，单位:米
        '''
        pass
    
    def GaussNegativeTransformer(self, coordinatePoint):
        '''高斯反算
        输入：CoordinatePoint,输入的坐标点,(X,Y)格式坐标，单位:米
        输出：返回(B,L)格式的坐标点IGxCoordinatePoint，单位:度
        '''
        pass
    
    def TransToEllipseXYZFromProjectXYH(self, coordinatePoint):
        '''投影坐标转换为参心空间直角坐标
        输入：CoordinatePoint,输入的坐标点,(X,Y,H)格式坐标，单位:米
        输出：返回(X,Y,Z)格式的坐标点IGxCoordinatePoint，单位:米
        '''
        pass
    
    def TransToProjectXYHFromEllipseXYZ(self, coordinatePoint):
        '''参心空间直角坐标转换为投影坐标
        输入：CoordinatePoint,输入的坐标点,(X,Y,Z)格式坐标，单位:米
        输出：返回(X,Y,H)格式的坐标点IGxCoordinatePoint，单位:米
        '''
        pass
    
    def TransToEllipseBLHFromEllipseXYZ(self, coordinatePoint):
        '''参心空间直角坐标转换为空间大地坐标
        输入：CoordinatePoint,输入的坐标点,(X,Y,Z)格式坐标，单位:米
        输出：返回(B,L,H)格式的坐标点IGxCoordinatePoint，单位:度
        '''
        pass
    
    def TransToEllipseXYZFromEllipseBLH(self, coordinatePoint):
        '''空间大地坐标转换为参心空间直角坐标
        输入：CoordinatePoint,输入的坐标点,(B,L,H)格式坐标，单位:度
        输出：返回(X,Y,Z)格式的坐标点IGxCoordinatePoint，单位:米
        '''
        pass
    
class IGxCoordinateTransferHelper(Interface):
    '''坐标转换辅助类'''
    Attribute('TransformationType', 'TransformationMethod', 'TransformationParameters', 'SourceEarthParameters',
              'TargetEarthParameters', 'SourceCentralMeridian', 'TargetCentralMeridian', 'SourceFalseEasting',
              'TargetFalseEasting')
    
    def doTransform(points):
        '''坐标转换
        输入：points,源坐标点集合
        输出：返回坐标点集合
        '''
        pass

class CoordinateType(Enum):
    '''坐标类型'''
    XYZ = 0  #空间直角坐标XYZ
    XYH = 1  #空间直角坐标XYH
    BLH = 2  #空间大地坐标BLH,单位度
    BLH2 = 3 #空间大地坐标BLH,单位弧度
    BLH3 = 4 #空间大地坐标BLH,单位度分秒
    XY = 5   #平面直角坐标XY

class TransformationType(Enum):
    '''坐标变换类型'''
    BLtoXY = 0  #空间大地坐标转平面直角坐标
    XYtoBL = 1  #平面直角坐标转空间大地坐标
    XYtoXY = 2  #平面直角坐标转平面直角坐标
    BLHtoBLH = 3 #空间大地坐标转空间大地坐标
    BLHtoXYH = 4 #空间大地坐标转空间直角坐标
    XYHtoXYH = 5 #空间直角坐标转空间直角坐标
    XYHtoBLH = 6 #空间直角坐标转空间大地坐标

class TransformationMethods(Enum):
    '''坐标转换方法或模型'''
    Bursa = 0               #布尔莎七参数综合法转换模型
    Molodensky = 1          #莫洛金斯基七参数转换模型
    SevenParams2D = 2       #二维七参数转换模型
    SevenParams3D = 3       #三维七参数转换模型
    FourParams2D = 4        #平面四参数转换模型
    FourParams3D = 5        #三维四参数转换模型
    MapGridDelt = 6         #格网改正量转换模型
    QuadraticPolynomial = 7 #二次多项式转换模型
    AffineTrans = 8         #仿射变换转换模型
    

@implementer(IGxCoordinatePoint)
class GxCoordinatePoint:
    def __init__(self):
        self.__XorB = 0.0
        self.__YorL = 0.0
        self.__ZorH = 0.0
        self.__Band = 1
          
    def __init__(self, XorB, YorL, ZorH, Band):
        self.__XorB = XorB
        self.__YorL = YorL
        self.__ZorH = ZorH
        self.__Band = Band
    
    @property
    def XorB(self):
        return self.__XorB
    
    @XorB.setter
    def XorB(self, value):
        self.__XorB = value
    
    @property
    def YorL(self):
        return self.__YorL
    
    @YorL.setter
    def YorL(self, value):
        self.__YorL = value
    
    @property
    def ZorH(self):
        return self.__ZorH
    
    @ZorH.setter
    def ZorH(self, value):
        self.__ZorH = value
    
    @property
    def Band(self):
        return self.__Band
    
    @Band.setter
    def Band(self, value):
        self.__Band = value


@implementer(IGxCoordinatePointPair)
class GxCoordinatePointPair:
    def __init__(self):
        self.__GUID = ''
        self.__CoordinateType = None
        self.__SourceXorB = 0.0
        self.__SourceYorL = 0.0
        self.__SourceZorH = 0.0
        self.__TargetXorB = 0.0
        self.__TargetYorL = 0.0
        self.__TargetZorH = 0.0
        self.__ResidualX = 0.0
        self.__ResidualY = 0.0
        self.__ResidualZ = 0.0
        self.__MeadianError = 0.0
    
    def __init__(self, guid, coordinateType, sourceXorB, sourceYorL, sourceZorH, 
                 targetXorB, targetYorL, targetZorH):
        self.__GUID = guid
        self.__CoordinateType = coordinateType
        self.__SourceXorB = sourceXorB
        self.__SourceYorL = sourceYorL
        self.__SourceZorH = sourceZorH
        self.__TargetXorB = targetXorB
        self.__TargetYorL = targetYorL
        self.__TargetZorH = targetZorH
    
    @property
    def GUID(self):
        return self.___GUID
    
    @GUID.setter
    def GUID(self, value):
        self.___GUID = value
    
    @property
    def CoordinateType(self):
        return self.___CoordinateType
    
    @CoordinateType.setter
    def CoordinateType(self, value):
        self.___CoordinateType = value
    
    @property
    def SourceXorB(self):
        return self.___SourceXorB
    
    @SourceXorB.setter
    def SourceXorB(self, value):
        self.___SourceXorB = value
    
    @property
    def SourceYorL(self):
        return self.___SourceYorL
    
    @SourceYorL.setter
    def SourceYorL(self, value):
        self.___SourceYorL = value
    
    @property
    def SourceZorH(self):
        return self.___SourceZorH
    
    @SourceZorH.setter
    def SourceZorH(self, value):
        self.___SourceZorH = value
    
    @property
    def TargetXorB(self):
        return self.___TargetXorB
    
    @TargetXorB.setter
    def TargetXorB(self, value):
        self.___TargetXorB = value
    
    @property
    def TargetYorL(self):
        return self.___TargetYorL
    
    @TargetYorL.setter
    def TargetYorL(self, value):
        self.___TargetYorL = value
    
    @property
    def TargetZorH(self):
        return self.___TargetZorH
    
    @TargetZorH.setter
    def TargetZorH(self, value):
        self.___TargetZorH = value
    
    @property
    def ResidualX(self):
        return self.___ResidualX
    
    @ResidualX.setter
    def ResidualX(self, value):
        self.___ResidualX = value
    
    @property
    def ResidualY(self):
        return self.___ResidualY
    
    @ResidualY.setter
    def ResidualY(self, value):
        self.___ResidualY = value
    
    @property
    def ResidualZ(self):
        return self.___ResidualZ
    
    @ResidualZ.setter
    def ResidualZ(self, value):
        self.___ResidualZ = value
    
    @property
    def MeadianError(self):
        return self.___MeadianError
    
    @MeadianError.setter
    def MeadianError(self, value):
        self.___MeadianError = value
    

@implementer(IGxGaussTransferHelper)
class GxGaussTransferHelper:
    def __init__(self):
        self.__EarthParams = GxEarthParams()
        self.__EarthParams.Name = 'Xian 1980'
        self.__EarthParams.A = 6378140.0
        self.__EarthParams.B = 6356755.288
        self.__EarthParams.F = 1.0 / 298.257
        
        self.__CentralMeridian = 102.0
        self.__FalseEasting = 500000.0
    
    def __init__(self, earthParams, centralMeridian, falseEasting):
        self.__EarthParams = earthParams
        self.__CentralMeridian = centralMeridian
        self.__FalseEasting = falseEasting
    
    @property
    def EarthParams(self):
        return self.__EarthParams
    
    @EarthParams.setter
    def EarthParams(self, value):
        self.__EarthParams = value
    
    @property
    def CentralMeridian(self):
        return self.__CentralMeridian
    
    @CentralMeridian.setter
    def CentralMeridian(self, value):
        self.__CentralMeridian = value
    
    @property
    def FalseEasting(self):
        return self.__FalseEasting
    
    @FalseEasting.setter
    def FalseEasting(self, value):
        self.__FalseEasting = value
    
    def GaussPositiveTransformer(self, coordinatePoint):
        '''高斯正算
        输入：CoordinatePoint,输入的坐标点,(B,L)格式坐标，单位:度
        输出：返回(X,Y)格式的坐标点IGxCoordinatePoint，单位:米
        '''
        if self.__EarthParams is None or self.__CentralMeridian == 0.0 or self.__FalseEasting == 0.0:
            return None
        
        dResult = GxCoordinatePoint()
        
        return dResult
        
    
    def GaussNegativeTransformer(self, coordinatePoint):
        '''高斯反算
        输入：CoordinatePoint,输入的坐标点,(X,Y)格式坐标，单位:米
        输出：返回(B,L)格式的坐标点IGxCoordinatePoint，单位:度
        '''
        pass
    
    def TransToEllipseXYZFromProjectXYH(self, coordinatePoint):
        '''投影坐标转换为参心空间直角坐标
        输入：CoordinatePoint,输入的坐标点,(X,Y,H)格式坐标，单位:米
        输出：返回(X,Y,Z)格式的坐标点IGxCoordinatePoint，单位:米
        '''
        pass
    
    def TransToProjectXYHFromEllipseXYZ(self, coordinatePoint):
        '''参心空间直角坐标转换为投影坐标
        输入：CoordinatePoint,输入的坐标点,(X,Y,Z)格式坐标，单位:米
        输出：返回(X,Y,H)格式的坐标点IGxCoordinatePoint，单位:米
        '''
        pass
    
    def TransToEllipseBLHFromEllipseXYZ(self, coordinatePoint):
        '''参心空间直角坐标转换为空间大地坐标
        输入：CoordinatePoint,输入的坐标点,(X,Y,Z)格式坐标，单位:米
        输出：返回(B,L,H)格式的坐标点IGxCoordinatePoint，单位:度
        '''
        pass
    
    def TransToEllipseXYZFromEllipseBLH(self, coordinatePoint):
        '''空间大地坐标转换为参心空间直角坐标
        输入：CoordinatePoint,输入的坐标点,(B,L,H)格式坐标，单位:度
        输出：返回(X,Y,Z)格式的坐标点IGxCoordinatePoint，单位:米
        '''
        pass
    
    
        

    

