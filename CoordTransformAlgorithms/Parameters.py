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


##实现IGx2DFourParams接口,二维四参数转换类
@implementer(IGx2DFourParams)
class Gx2DFourParams:
    def __init__(self):
        self.DX = 0.0
        self.DY = 0.0
        self.Angle = 0.0
        self.ScaleK = 0.0
        
    def __init__(self, dx, dy, angle, scaleK):
        self.DX = dx
        self.DY = dy
        self.Angle = angle
        self.ScaleK = scaleK
    
    @property
    def DX(self):
        return self.DX
    
    @DX.setter 
    def DX(self, dx):
        self.DX = dx
    
    @property
    def DY(self):
        return self.DY
    
    @DY.setter 
    def DY(self, dy):
        self.DY = dy
    
    @property
    def Angle(self):
        return self.Angle
    
    @Angle.setter
    def Angle(self, angle):
        self.Angle = angle
    
    @property
    def ScaleK(self):
        return self.ScaleK
    
    @ScaleK.setter
    def ScaleK(self, scaleK):
        self.ScaleK = scaleK
    
    
#实现IGx3DFourParams接口,三维四参数转换类
@implementer(IGx3DFourParams)
class Gx3DFourParams:
    def __init__(self):
        self.DX = 0.0
        self.DY = 0.0
        self.DZ = 0.0
        self.Angle = 0.0
        self.B0 = 0.0
        self.L0 = 0.0
    
    def __init__(self, dx, dy, dz, angle, b0, l0):
        self.DX = dx
        self.DY = dy
        self.DZ = dz
        self.Angle = angle
        self.B0 = b0
        self.L0 = l0
    
    @property
    def DX(self):
        return self.DX
    
    @DX.setter
    def DX(self, dx):
        self.DX = dx
    
    @property
    def DY(self):
        return self.DY
    
    @DY.setter
    def DY(self, dy):
        self.DY = dy
    
    @property
    def DZ(self):
        return self.DZ
    
    @DZ.setter
    def DZ(self, dz):
        self.DZ = dz
    
    @property
    def Angle(self):
        return self.Angle
    
    @Angle.setter
    def Angle(self, angle):
        self.Angle = angle
    
    @property
    def B0(self):
        return self.B0
    
    @B0.setter
    def B0(self, b0):
        self.B0 = b0
    
    @property
    def L0(self):
        return self.L0
    
    @L0.setter
    def L0(self, l0):
        self.L0 = l0


#实现IGxSevenParams接口,七参数转换类
@implementer(IGxSevenParams)
class GxSevenParams:
    def __init__(self):
        self.DX = 0.0
        self.DY = 0.0
        self.DZ = 0.0
        self.AngleX = 0.0
        self.AngleY = 0.0
        self.AngleZ = 0.0
        self.ScaleK = 0.0
    
    def __init__(self, dx, dy, dz, angleX, angleY, angleZ, scaleK):
        self.DX = dx
        self.DY = dy
        self.DZ = dz
        self.AngleX = angleX
        self.AngleY = angleY
        self.AngleZ = angleZ
        self.ScaleK = scaleK
    
    @property
    def DX(self):
        return self.DX
    
    @DX.setter
    def DX(self, dx):
        self.DX = dx
    
    @property
    def DY(self):
        return self.DY
    
    @DY.setter
    def DY(self, dy):
        self.DY = dy
    
    @property
    def DZ(self):
        return self.DZ
    
    @DZ.setter
    def DZ(self, dz):
        self.DZ = dz
    
    @property
    def AngleX(self):
        return self.AngleX
    
    @AngleX.setter
    def AngleX(self, angleX):
        self.AngleX = angleX
    
    @property
    def AngleY(self):
        return self.AngleY
    
    @AngleY.setter
    def AngleY(self, angleY):
        self.AngleY = angleY
    
    @property
    def AngleZ(self):
        return self.AngleZ
    
    @AngleZ.setter
    def AngleZ(self, angleZ):
        self.AngleZ = angleZ
    
    @property
    def ScaleK(self):
        return self.ScaleK
    
    @ScaleK.setter
    def ScaleK(self, scaleK):
        self.ScaleK = scaleK


#实现IGxMolodenskyParams接口,Molodensky转换类
@implementer(IGxMolodenskyParams)
class GxMolodenskyParams:
    def __init__(self):
        self.DX = 0.0
        self.DY = 0.0
        self.DZ = 0.0
        self.AngleX = 0.0
        self.AngleY = 0.0
        self.AngleZ = 0.0
        self.ScaleK = 0.0
        self.X0 = 0.0
        self.Y0 = 0.0
        self.Z0 = 0.0
    
    def __init__(self, dx, dy, dz, angleX, angleY, angleZ, scaleK, x0, y0, z0):
        self.DX = dx
        self.DY = dy
        self.DZ = dz
        self.AngleX = angleX
        self.AngleY = angleY
        self.AngleZ = angleZ
        self.ScaleK = scaleK
        self.X0 = x0
        self.Y0 = y0
        self.Z0 = z0
    
    @property
    def DX(self):
        return self.DX
    
    @DX.setter
    def DX(self, dx):
        self.DX = dx
    
    @property
    def DY(self):
        return self.DY
    
    @DY.setter
    def DY(self, dy):
        self.DY = dy
    
    @property
    def DZ(self):
        return self.DZ
    
    @DZ.setter
    def DZ(self, dz):
        self.DZ = dz
    
    @property
    def AngleX(self):
        return self.AngleX
    
    @AngleX.setter
    def AngleX(self, angleX):
        self.AngleX = angleX
    
    @property
    def AngleY(self):
        return self.AngleY
    
    @AngleY.setter
    def AngleY(self, angleY):
        self.AngleY = angleY
    
    @property
    def AngleZ(self):
        return self.AngleZ
    
    @AngleZ.setter
    def AngleZ(self, angleZ):
        self.AngleZ = angleZ
    
    @property
    def ScaleK(self):
        return self.ScaleK
    
    @ScaleK.setter
    def ScaleK(self, scaleK):
        self.ScaleK = scaleK
      
    @property
    def X0(self):
        return self.X0
    
    @X0.setter
    def X0(self, x0):
        self.X0 = x0
    
    @property
    def Y0(self):
        return self.Y0
    @Y0.setter
    def Y0(self, y0):
        self.Y0 = y0
    
    @property
    def Z0(self):
        return self.Z0
    
    @Z0.setter
    def Z0(self, z0):
        self.Z0 = z0
    

#实现IGxAffineParams接口,仿射变换转换类
@implementer(IGxAffineParams)
class GxAffineParams:
    def __init__(self):
        self.A1 = 0.0
        self.A2 = 0.0
        self.A3 = 0.0
        self.A4 = 0.0
        self.Tx = 0.0
        self.Ty = 0.0
        
    def __init__(self, a1, a2, a3, a4, tx, ty):
        self.A1 = a1
        self.A2 = a2
        self.A3 = a3
        self.A4 = a4
        self.Tx = tx
        self.Ty = ty
    
    @property
    def A1(self):
        return self.A1
    
    @A1.setter
    def A1(self, a1):
        self.A1 = a1
    
    @property
    def A2(self):
        return self.A2
    
    @A2.setter
    def A2(self, a2):
        self.A2 = a2
    
    @property
    def A3(self):
        return self.A3
    
    @A3.setter
    def A3(self, a3):
        self.A3 = a3
    
    @property
    def A4(self):
        return self.A4
    
    @A4.setter
    def A4(self, a4):
        self.A4 = a4
    
    @property
    def Tx(self):
        return self.Tx
    
    @Tx.setter
    def Tx(self, tx):
        self.Tx = tx
    
    @property
    def Ty(self):
        return self.Ty
    
    @Ty.setter
    def Ty(self, ty):
        self.Ty = ty
    

#实现IGxQuadraticPolynomialParams接口,二次多项式变换转换类
@implementer(IGxQuadraticPolynomialParams)
class GxQuadraticPolynomialParams:
    def __init__(self):
        self.A1 = 0.0
        self.A2 = 0.0
        self.A3 = 0.0
        self.A4 = 0.0
        self.A5 = 0.0
        self.B1 = 0.0
        self.B2 = 0.0
        self.B3 = 0.0
        self.B4 = 0.0
        self.B5 = 0.0
        
    def __init__(self, a1, a2, a3, a4, a5, b1, b2, b3, b4, b5):
        self.A1 = a1
        self.A2 = a2
        self.A3 = a3
        self.A4 = a4
        self.A5 = a5
        self.B1 = b1
        self.B2 = b2
        self.B3 = b3
        self.B4 = b4
        self.B5 = b5
    
    @property
    def A1(self):
        return self.A1
    
    @A1.setter
    def A1(self, a1):
        self.A1 = a1
    
    @property
    def A2(self):
        return self.A2
    
    @A2.setter
    def A2(self, a2):
        self.A2 = a2
    
    @property
    def A3(self):
        return self.A3
    
    @A3.setter
    def A3(self, a3):
        self.A3 = a3
    
    @property
    def A4(self):
        return self.A4
    
    @A4.setter
    def A4(self, a4):
        self.A4 = a4
    
    @property
    def A5(self):
        return self.A5
    
    @A5.setter
    def A5(self, a5):
        self.A5 = a5
    
    @property
    def B1(self):
        return self.B1
    
    @B1.setter
    def B1(self, b1):
        self.B1 = b1
    
    @property
    def B2(self):
        return self.B2
    
    @B2.setter
    def B2(self, b2):
        self.B2 = b2
    
    @property
    def B3(self):
        return self.B3
    
    @B3.setter
    def B3(self, b3):
        self.B3 = b3
    
    @property
    def B4(self):
        return self.B4
    
    @B4.setter
    def B4(self, b4):
        self.B4 = b4
    
    @property
    def B5(self):
        return self.B5
    @B5.setter
    def B5(self, b5):
        self.B5 = b5
