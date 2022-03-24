#_*_ coding: utf-8 _*_

from zope.interface import Interface, Attribute
from zope.interface.declarations import implementer

#定义IGx2DFourParams接口，定义了一个二维四参数的转换接口
class IGx2DFourParams(Interface):
    ##定义属性DX:平移量X，DY:平移量Y，Angle:X轴旋转角，ScaleK:尺度因子K
    Attribute('DX', 'DY', 'Angle', 'ScaleK')

#定义IGx3DFourParams接口，定义了一个三维四参数的转换接口
class IGx3DFourParams(Interface):
    ##定义属性DX:平移量X, DY:平移量Y, DZ:平移量Z, Angle:X轴旋转角，B0:区域中心点纬度B0, L0:区域中心点经度L0
    Attribute('DX', 'DY', 'DZ', 'Angle', 'B0', 'L0')

#定义IGxSevenParams接口，定义了一个七参数的转换接口
class IGxSevenParams(Interface):
    ##定义属性DX:平移量X, DY:平移量Y, DZ:平移量Z, AngleX:X轴旋转角，AngleY:Y轴旋转角,AngleZ:Z轴旋转角, ScaleK:尺度因子K
    Attribute('DX', 'DY', 'DZ', 'AngleX', 'AngleY', 'AngleZ','ScaleK')

#定义IGxMolodenskyParams接口，定义了一个Molodensky变换的转换接口
class IGxMolodenskyParams(IGxSevenParams):
    ##定义属性X0:中心点X坐标, Y0:中心点Y坐标, Z0:中心点Z坐标
    Attribute('X0', 'Y0', 'Z0')

#定义IGxAffineParams接口，定义了一个仿射变换的转换接口
class IGxAffineParams(Interface):
    Attribute('A1', 'A2', 'A3', 'A4', 'Tx', 'Ty')

#定义IGxQuadraticPolynomialParams接口，定义了一个二次多项式变换的转换接口
class IGxQuadraticPolynomialParams(Interface):
    Attribute('A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5')

#定义IGxEarthParams接口，定义了一个地球椭球参数信息接口
class IGxEarthParams(Interface):
    ##定义属性A:椭球长半轴, B:椭球短半轴, F:椭球扁率, ProjectType:投影类型, ProjectSurfaceHeight:投影面高
    Attribute('Name', 'A', 'B','F', 'ProjectType','ProjectSurfaceHeight')


##实现IGx2DFourParams接口,二维四参数转换类
@implementer(IGx2DFourParams)
class Gx2DFourParams:
    def __init__(self):
        self.__DX = 0.0
        self.__DY = 0.0
        self.__Angle = 0.0
        self.__ScaleK = 0.0
        
    def __init__(self, dx, dy, angle, scaleK):
        self.__DX = dx
        self.__DY = dy
        self.__Angle = angle
        self.__ScaleK = scaleK
    
    @property
    def DX(self):
        return self.__DX
    
    @DX.setter 
    def DX(self, dx):
        self.__DX = dx
    
    @property
    def DY(self):
        return self.__DY
    
    @DY.setter 
    def DY(self, dy):
        self.__DY = dy
    
    @property
    def Angle(self):
        return self.__Angle
    
    @Angle.setter
    def Angle(self, angle):
        self.__Angle = angle
    
    @property
    def ScaleK(self):
        return self.__ScaleK
    
    @ScaleK.setter
    def ScaleK(self, scaleK):
        self.__ScaleK = scaleK
    
    
#实现IGx3DFourParams接口,三维四参数转换类
@implementer(IGx3DFourParams)
class Gx3DFourParams:
    def __init__(self):
        self.__DX = 0.0
        self.__DY = 0.0
        self.__DZ = 0.0
        self.__Angle = 0.0
        self.__B0 = 0.0
        self.__L0 = 0.0
    
    def __init__(self, dx, dy, dz, angle, b0, l0):
        self.__DX = dx
        self.__DY = dy
        self.__DZ = dz
        self.__Angle = angle
        self.__B0 = b0
        self.__L0 = l0
    
    @property
    def DX(self):
        return self.__DX
    
    @DX.setter
    def DX(self, dx):
        self.__DX = dx
    
    @property
    def DY(self):
        return self.__DY
    
    @DY.setter
    def DY(self, dy):
        self.__DY = dy
    
    @property
    def DZ(self):
        return self.__DZ
    
    @DZ.setter
    def DZ(self, dz):
        self.__DZ = dz
    
    @property
    def Angle(self):
        return self.__Angle
    
    @Angle.setter
    def Angle(self, angle):
        self.__Angle = angle
    
    @property
    def B0(self):
        return self.__B0
    
    @B0.setter
    def B0(self, b0):
        self.__B0 = b0
    
    @property
    def L0(self):
        return self.__L0
    
    @L0.setter
    def L0(self, l0):
        self.__L0 = l0


#实现IGxSevenParams接口,七参数转换类
@implementer(IGxSevenParams)
class GxSevenParams:
    def __init__(self):
        self.__DX = 0.0
        self.__DY = 0.0
        self.__DZ = 0.0
        self.__AngleX = 0.0
        self.__AngleY = 0.0
        self.__AngleZ = 0.0
        self.__ScaleK = 0.0
    
    def __init__(self, dx, dy, dz, angleX, angleY, angleZ, scaleK):
        self.__DX = dx
        self.__DY = dy
        self.__DZ = dz
        self.__AngleX = angleX
        self.__AngleY = angleY
        self.__AngleZ = angleZ
        self.__ScaleK = scaleK
    
    @property
    def DX(self):
        return self.__DX
    
    @DX.setter
    def DX(self, dx):
        self.__DX = dx
    
    @property
    def DY(self):
        return self.__DY
    
    @DY.setter
    def DY(self, dy):
        self.__DY = dy
    
    @property
    def DZ(self):
        return self.__DZ
    
    @DZ.setter
    def DZ(self, dz):
        self.__DZ = dz
    
    @property
    def AngleX(self):
        return self.__AngleX
    
    @AngleX.setter
    def AngleX(self, angleX):
        self.__AngleX = angleX
    
    @property
    def AngleY(self):
        return self.__AngleY
    
    @AngleY.setter
    def AngleY(self, angleY):
        self.__AngleY = angleY
    
    @property
    def AngleZ(self):
        return self.__AngleZ
    
    @AngleZ.setter
    def AngleZ(self, angleZ):
        self.__AngleZ = angleZ
    
    @property
    def ScaleK(self):
        return self.__ScaleK
    
    @ScaleK.setter
    def ScaleK(self, scaleK):
        self.__ScaleK = scaleK


#实现IGxMolodenskyParams接口,Molodensky转换类
@implementer(IGxMolodenskyParams)
class GxMolodenskyParams:
    def __init__(self):
        self.__DX = 0.0
        self.__DY = 0.0
        self.__DZ = 0.0
        self.__AngleX = 0.0
        self.__AngleY = 0.0
        self.__AngleZ = 0.0
        self.__ScaleK = 0.0
        self.__X0 = 0.0
        self.__Y0 = 0.0
        self.__Z0 = 0.0
    
    def __init__(self, dx, dy, dz, angleX, angleY, angleZ, scaleK, x0, y0, z0):
        self.__DX = dx
        self.__DY = dy
        self.__DZ = dz
        self.__AngleX = angleX
        self.__AngleY = angleY
        self.__AngleZ = angleZ
        self.__ScaleK = scaleK
        self.__X0 = x0
        self.__Y0 = y0
        self.__Z0 = z0
    
    @property
    def DX(self):
        return self.__DX
    
    @DX.setter
    def DX(self, dx):
        self.__DX = dx
    
    @property
    def DY(self):
        return self.__DY
    
    @DY.setter
    def DY(self, dy):
        self.__DY = dy
    
    @property
    def DZ(self):
        return self.__DZ
    
    @DZ.setter
    def DZ(self, dz):
        self.__DZ = dz
    
    @property
    def AngleX(self):
        return self.__AngleX
    
    @AngleX.setter
    def AngleX(self, angleX):
        self.__AngleX = angleX
    
    @property
    def AngleY(self):
        return self.__AngleY
    
    @AngleY.setter
    def AngleY(self, angleY):
        self.__AngleY = angleY
    
    @property
    def AngleZ(self):
        return self.__AngleZ
    
    @AngleZ.setter
    def AngleZ(self, angleZ):
        self.__AngleZ = angleZ
    
    @property
    def ScaleK(self):
        return self.__ScaleK
    
    @ScaleK.setter
    def ScaleK(self, scaleK):
        self.__ScaleK = scaleK
      
    @property
    def X0(self):
        return self.__X0
    
    @X0.setter
    def X0(self, x0):
        self.__X0 = x0
    
    @property
    def Y0(self):
        return self.__Y0
    @Y0.setter
    def Y0(self, y0):
        self.__Y0 = y0
    
    @property
    def Z0(self):
        return self.__Z0
    
    @Z0.setter
    def Z0(self, z0):
        self.__Z0 = z0
    

#实现IGxAffineParams接口,仿射变换转换类
@implementer(IGxAffineParams)
class GxAffineParams:
    def __init__(self):
        self.__A1 = 0.0
        self.__A2 = 0.0
        self.__A3 = 0.0
        self.__A4 = 0.0
        self.__Tx = 0.0
        self.__Ty = 0.0
        
    def __init__(self, a1, a2, a3, a4, tx, ty):
        self.__A1 = a1
        self.__A2 = a2
        self.__A3 = a3
        self.__A4 = a4
        self.__Tx = tx
        self.__Ty = ty
    
    @property
    def A1(self):
        return self.__A1
    
    @A1.setter
    def A1(self, a1):
        self.__A1 = a1
    
    @property
    def A2(self):
        return self.__A2
    
    @A2.setter
    def A2(self, a2):
        self.__A2 = a2
    
    @property
    def A3(self):
        return self.__A3
    
    @A3.setter
    def A3(self, a3):
        self.__A3 = a3
    
    @property
    def A4(self):
        return self.__A4
    
    @A4.setter
    def A4(self, a4):
        self.__A4 = a4
    
    @property
    def Tx(self):
        return self.__Tx
    
    @Tx.setter
    def Tx(self, tx):
        self.__Tx = tx
    
    @property
    def Ty(self):
        return self.__Ty
    
    @Ty.setter
    def Ty(self, ty):
        self.__Ty = ty
    

#实现IGxQuadraticPolynomialParams接口,二次多项式变换转换类
@implementer(IGxQuadraticPolynomialParams)
class GxQuadraticPolynomialParams:
    def __init__(self):
        self.__A1 = 0.0
        self.__A2 = 0.0
        self.__A3 = 0.0
        self.__A4 = 0.0
        self.__A5 = 0.0
        self.__B1 = 0.0
        self.__B2 = 0.0
        self.__B3 = 0.0
        self.__B4 = 0.0
        self.__B5 = 0.0
        
    def __init__(self, a1, a2, a3, a4, a5, b1, b2, b3, b4, b5):
        self.__A1 = a1
        self.__A2 = a2
        self.__A3 = a3
        self.__A4 = a4
        self.__A5 = a5
        self.__B1 = b1
        self.__B2 = b2
        self.__B3 = b3
        self.__B4 = b4
        self.__B5 = b5
    
    @property
    def A1(self):
        return self.__A1
    
    @A1.setter
    def A1(self, a1):
        self.__A1 = a1
    
    @property
    def A2(self):
        return self.__A2
    
    @A2.setter
    def A2(self, a2):
        self.__A2 = a2
    
    @property
    def A3(self):
        return self.__A3
    
    @A3.setter
    def A3(self, a3):
        self.__A3 = a3
    
    @property
    def A4(self):
        return self.__A4
    
    @A4.setter
    def A4(self, a4):
        self.__A4 = a4
    
    @property
    def A5(self):
        return self.__A5
    
    @A5.setter
    def A5(self, a5):
        self.__A5 = a5
    
    @property
    def B1(self):
        return self.__B1
    
    @B1.setter
    def B1(self, b1):
        self.__B1 = b1
    
    @property
    def B2(self):
        return self.__B2
    
    @B2.setter
    def B2(self, b2):
        self.__B2 = b2
    
    @property
    def B3(self):
        return self.__B3
    
    @B3.setter
    def B3(self, b3):
        self.__B3 = b3
    
    @property
    def B4(self):
        return self.__B4
    
    @B4.setter
    def B4(self, b4):
        self.__B4 = b4
    
    @property
    def B5(self):
        return self.__B5
    @B5.setter
    def B5(self, b5):
        self.__B5 = b5
    
    
@implementer(IGxEarthParams)
class GxEarthParams:
    def __init__(self):
        self.__Name = 'BJ54'
        self.__A = 6378245.0
        self.__F = 1.0 / 298.3
        self.__B = 6356863.0188
        self.__ProjectType = ''
        self.__ProjectSurfaceHeight = 0.0
    
    def __init__(self, name, a, f, b, projectType, projectSurfaceHeight):
        self.__Name = name
        self.__A = a
        self.__F = f
        self.__B = b
        self.__ProjectType = projectType
        self.__ProjectSurfaceHeight = projectSurfaceHeight
    
    @property
    def Name(self):
        return self.__Name
    
    @Name.setter
    def Name(self, name):
        self.__Name = name
    
    @property
    def A(self):
        return self.__A
    
    @A.setter
    def A(self, a):
        self.__A = a
    
    @property
    def F(self):
        return self.__F
    
    @F.setter
    def F(self, f):
        self.__F = f
    
    @property
    def B(self):
        return self.__B
    
    @B.setter
    def B(self, b):
        self.__B = b
    
    @property
    def ProjectType(self):
        return self.__ProjectType
    
    @ProjectType.setter
    def ProjectType(self, projectType):
        self.__ProjectType = projectType
    
    @property
    def ProjectSurfaceHeight(self):
        return self.__ProjectSurfaceHeight
    
    @ProjectSurfaceHeight.setter
    def ProjectSurfaceHeight(self, projectSurfaceHeight):
        self.__ProjectSurfaceHeight = projectSurfaceHeight
