#_*_ coding: utf-8 _*_

from zope.interface import Interface, Attribute
from zope.interface.declarations import implementer

class IGxCoordinatePoint(Interface):
    '''XorB:X坐标或B坐标, YorL:Y坐标或L坐标, ZorH:Z坐标或H坐标,Band:投影带号'''
    Attribute('XorB', 'YorL', 'ZorH','Band')
