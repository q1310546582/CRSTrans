import subprocess
import os
import sys


sitePackageFilename = sys.path[-1] + r'\osgeo\ogr2ogr'
p = subprocess.Popen(sitePackageFilename + r' -f DXF E:/NoteBook/坐标转换算法/ConvertPolygonsFromGDAL.dxf E:/NoteBook/坐标转换算法/transFile.shp', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# # 标准输出
print(sitePackageFilename + r' -f DXF E:/NoteBook/坐标转换算法/ConvertPolygonsFromGDAL.dxf E:/NoteBook/坐标转换算法/transFile.shp')
print(p.communicate()[1])
