from osgeo import ogr
import os
from osgeo import osr
from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.GxEllipsoidEnum import *
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.Gx3DBrusa_Wolf import *
import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear
import subprocess

os.chdir(r"E:\NoteBook\坐标转换算法\data")


class OSGVecDataConverter(object):
    FormatDic = {"ESRI Shapefile": ".shp", "DXF": ".dxf", "GPKG": ".gpkg", "GeoJSON": ".json", "MITAB": ".mif",
                 "CSV": ".csv", "XLSX": ".xlsx"}

    def __init__(self, sourceFilename, sourceDriverName):
        '''
        :param sourceFilename: str: file path to be converted, should be absolute path
        :param sourceDriverName: str: fie driver to be converted
        :return: OSGVecDataConverter
        '''
        self.src_driverName = sourceDriverName
        # read source filename
        self.src_driver = ogr.GetDriverByName(self.src_driverName)

        self.src_ds = self.src_driver.Open(sourceFilename, 0)
        if (self.src_ds == None):
            print('could not open')
            return None
        self.src_layer = self.src_ds.GetLayer(0)

    # 返回包含各图层坐标对的数组，
    def GetXYZ(self):
        """
        return a multidimensional array containing the coordinates of each layer,
        such as a LineString Feature, it returns as [[(X,Y,Z)]],
        The dimensions from outside to inside are represented respectively as Layers,Features,Points
        """
        self.lyrArray = []
        for i in range(self.src_ds.GetLayerCount()):
            layer = self.src_ds.GetLayer(i)  # 得到当前图层
            self.feaArray = []  # 用于存储所有要素，这是个多维数组
            layer_defn = layer.GetLayerDefn()  # 图层的定义对象，包含了图层的一些属性
            geom_type = layer_defn.GetGeomType()  # 获取几何体的类型

            # 如果图层是多边形，那么一个多边形可能由多个环构成
            if (geom_type == ogr.wkbPolygon or geom_type == ogr.wkbPolygon25D or
                    geom_type == ogr.wkbPolygonM or geom_type == ogr.wkbPolygonZM):
                self.readPolygonFeature(layer)

            elif (geom_type == ogr.wkbLineString or geom_type == ogr.wkbLineString25D):
                self.readLineFeature(layer)

            elif (geom_type == ogr.wkbPoint or geom_type == ogr.wkbPoint25D):
                self.readPointFeature(layer)

            self.lyrArray.append(self.feaArray)

        return self.lyrArray

    @staticmethod
    def CreateProjSpatialReference(EPSG, **kw):
        """
        :param EPSG: int: EPSG number used to specify the ProjSpatial coordinate system according to TM projection
        :param kw: Dict[str, Any]: You can set some params according to  kw['CenterLat'], kw['FalseEasting']...
        :return: SpatialReference
        """
        # 建立投影坐标系
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(EPSG)

        if (len(kw.keys()) != 0):
            print(kw)
            if (kw['Projection'] == 'TM'):
                srs.SetProjCS(f"TM {kw['Zone']} ({srs.GetName()})");
                srs.SetTM(kw['CenterLat'], kw['CenterLong'], kw['Scale'], kw['FalseEasting'], kw['FalseNorthing']);
        return srs

    @staticmethod
    def CreateGeoSpatialReference(EPSG, **kw):
        """
        :param EPSG: int: EPSG number used to set the geoSpatial coordinate system，
        :param kw: Dict[str, Any]: You can set some params according to  kw['CenterLat'], kw['FalseEasting']...
        :return: SpatialReference
        """
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(EPSG)
        return srs

    def CreateTransFile(self, transFilename = os.path.split(os.path.abspath(__file__))[0] + r"\transFile.shp", tgt_srs=None, CopyDataSource=False):
        """
        :param tgt_srs: SpatialReference: the spatialref of target dataset
        :param CopyDataSource: bool: if True, copy layers from source to target dataset
        :return: None
        """
        # 建立新的图层
        tgt_driver = ogr.GetDriverByName("ESRI Shapefile")
        self.transFilename = transFilename
        print(transFilename)

        if (os.path.exists(transFilename)):
            if (tgt_driver.DeleteDataSource(transFilename) != 0):
                print("{0} existed! But Driver delete it failed!".format(transFilename))
                return

        # 复制数据集
        if CopyDataSource:
            trans_ds = tgt_driver.CopyDataSource(self.src_ds, transFilename)

        # 创建新数据集
        else:
            trans_ds = tgt_driver.CreateDataSource(transFilename)
            for i in range(self.src_ds.GetLayerCount()):
                src_layer = self.src_ds.GetLayer(i)  # 得到当前源图层
                src_layer_defn = src_layer.GetLayerDefn()  # 图层的定义对象，包含了图层的一些属性
                geom_type = src_layer_defn.GetGeomType()  # 获取几何体的类型
                # 如果没有赋予坐标系，则默认使用原图层的坐标系
                if tgt_srs is not None:
                    tgt_layer = trans_ds.CreateLayer(src_layer.GetName(), tgt_srs, geom_type)
                else:
                    tgt_layer = trans_ds.CreateLayer(src_layer.GetName(), src_layer.GetSpatialRef(), geom_type)

                if (tgt_layer == None):
                    print('Create layer failed! '.format(transFilename))
                    return

        if (trans_ds == None):
            print('Create {0} failed! '.format(transFilename))
            return None
        else:
            print('Create a transition file {0}, it can be deleted while the program finished.'.format(transFilename))

        # 为了将数据写入磁盘，必须使用Release()方法释放此数据。
        trans_ds.Release()

    # 将源数据集的各图层字段添加到目标数据集中，要求目标数据集支持字段创建和图层数量相等
    def CreateFields(self, tgt_ds):
        """
        :param tgt_ds:  DataSource: copy fields from source to target data source
        :return: None
        """
        for i in range(self.src_ds.GetLayerCount()):
            src_layer = self.src_ds.GetLayer(i)  # 得到当前源图层
            tgt_layer = tgt_ds.GetLayer(i)  # 得到目标图层

            # 根据源图层定义新图层的字段
            srcLyr_Defn = src_layer.GetLayerDefn()
            tgt_layer_Defn = tgt_layer.GetLayerDefn()

            for i in range(srcLyr_Defn.GetFieldCount()):
                field_defn = srcLyr_Defn.GetFieldDefn(i)
                if tgt_layer.CreateField(field_defn) != 0:
                    print("create Field{} failed!".format(field_defn.GetName()))

            tgt_layer = tgt_ds.GetLayer(i)
            # 输出字段名、类型、长度、精度
            for i in range(tgt_layer_Defn.GetFieldCount()):
                field_defn = tgt_layer_Defn.GetFieldDefn(i)
                print('Filed:' + field_defn.GetName(), 'Type:' + field_defn.GetTypeName())
                print('Width:' + str(field_defn.GetWidth()), 'Precision:' + str(field_defn.GetPrecision()))

    # 根据源图层的要素添加至新图层，并修改他们的坐标
    def CreateFeatures(self, tgt_ds, newpoints=None, isCopyFeature=True):
        """
        :param tgt_ds: DataSource
        :param newpoints: list: if not None, You can modify the coordinates for all features in case of one-to-one correspondence between list and feature coordinates
        :param isCopyFeature: bool: whether to copy source features to tgt_ds
        :return: None
        """
        if isCopyFeature:  # 如果需要复制源要素，则先将字段复制过来
            self.CreateFields(tgt_ds)

        for i in range(self.src_ds.GetLayerCount()):
            src_layer = self.src_ds.GetLayer(i)  # 得到当前源图层
            src_layer_defn = src_layer.GetLayerDefn()  # 图层的定义对象，包含了图层的一些属性
            geom_type = src_layer_defn.GetGeomType()  # 获取几何体的类型
            tgt_layer = tgt_ds.GetLayer(i)

            # 赋予polygon图层features
            if (geom_type == ogr.wkbPolygon or geom_type == ogr.wkbPolygon25D or
                    geom_type == ogr.wkbPolygonM or geom_type == ogr.wkbPolygonZM):
                if newpoints == None:  # 当图层是空的，仅仅将要素复制到各图层中
                    self.writePolygonFeature(src_layer, tgt_layer, None, True, geom_type)
                else:  # 当图层是空的，可以填充包含属性的新坐标要素和不包含其他属性的新坐标要素
                    self.writePolygonFeature(src_layer, tgt_layer, newpoints[i], isCopyFeature, geom_type)
            # 赋予line图层features
            elif (geom_type == ogr.wkbLineString or geom_type == ogr.wkbLineString25D or
                  geom_type == ogr.wkbLineStringM or geom_type == ogr.wkbLineStringZM):
                if newpoints == None:  # 当图层是空的，仅仅将要素复制到各图层中
                    self.writeLineFeature(src_layer, tgt_layer, None, True, geom_type)
                else:  # 当图层是空的，可以填充包含属性的新坐标要素和不包含其他属性的新坐标要素
                    self.writeLineFeature(src_layer, tgt_layer, newpoints[i], isCopyFeature, geom_type)
            elif (geom_type == ogr.wkbPoint or geom_type == ogr.wkbPoint25D or
                  geom_type == ogr.wkbPointM or geom_type == ogr.wkbPointZM):
                if newpoints == None:  # 当图层是空的，仅仅将要素复制到各图层中
                    self.writePointFeature(src_layer, tgt_layer, None, True, geom_type)
                else:  # 当图层是空的，可以填充包含属性的新坐标要素和不包含其他属性的新坐标要素
                    self.writePointFeature(src_layer, tgt_layer, newpoints[i], isCopyFeature, geom_type)
            else:
                return None
            src_layer.ResetReading()
        return 1

    def FeaturesRavel(self, features, geom_type=ogr.wkbPoint):
        """
        :param features: list: the return value of GetXYZ() needs to be converted to 1-d list, it is a parameter of coordinate transformation algorithm
        :param geom_type: int: default:ogr.wkbPoint
        :return: numpy.array
        """
        # 将features平铺为1维数组
        convert_points = []
        if geom_type == ogr.wkbPolygon:
            # 遍历图层
            for layer in features:
                # 遍历要素
                for fea in layer:
                    # 遍历环
                    for ring in fea:
                        # 遍历点
                        for point in ring:
                            convert_points.append(point)
        elif geom_type == ogr.wkbLineString:
            for layer in features:
                for fea in layer:
                    for point in fea:
                        convert_points.append(point)
        else:
            convert_points = []
            for layer in features:
                for point in layer:
                    convert_points.append(point)
        return np.array(convert_points)

    def FeatureNdaaray(self, features, predict_points, geom_type=ogr.wkbPoint):
        """
        :param predict_points: list: predict_points to be converted N-d list
        :param geom_type: int: default:ogr.wkbPoint
        :return: numpy.array
        """
        features_copy = copy.deepcopy(features)  # 深拷贝
        n = 0
        if geom_type == ogr.wkbPolygon:
            # 将新坐标还原到原来的图层中
            # 遍历图层
            for layer in features_copy:
                # 遍历要素
                for fea in layer:
                    # 遍历环
                    for ring in fea:
                        # 遍历点
                        for point_idx in range(len(ring)):
                            ring[point_idx] = predict_points[n]
                            n += 1
        elif geom_type == ogr.wkbLineString:
            for layer in features_copy:
                for fea in layer:
                    for point_idx in range(len(fea)):
                        fea[point_idx] = predict_points[n]
                        n += 1
        else:
            for layer in features_copy:
                for point_idx in range(len(layer)):
                    layer[point_idx] = predict_points[n]
                    n += 1
        return features_copy

    def FormatTrans(self, targetDriverName, targetFilename, isDeleteTransFile=True):
        cmd = 'ogr2ogr'
        if (targetDriverName == "ESRI Shapefile"):
            cmd = cmd + ' ' + targetFilename + ' ' + self.transFilename
            self.execute(cmd)
        else:
            cmd = cmd + ' -f' + ' ' + targetDriverName + ' ' + targetFilename + ' ' + self.transFilename
            self.execute(cmd)
        self.deleteTransFile(isDeleteTransFile)
        print('Success!')

    def execute(self, cmd):
        '''
        :param cmd: str: CMD command execution, get pipeline content, Not called by the outside user
        :return: None
        '''
        p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # 标准输出
        print(p1.communicate()[1].decode('utf-8', 'ignore'))
        p1.wait()
        return p1.poll()

    def deleteTransFile(self, isDeleteTransFile):
        """
        :param isDeleteTransFile: bool: if True, the transfile will be deleted when CMD command execution finished
        :return: None
        """
        if (isDeleteTransFile == True):
            if (os.path.exists(self.transFilename)):
                if (self.src_driver.DeleteDataSource(self.transFilename) != 0):
                    print("{0} existed! But Driver deleted it failed!".format(self.transFilename))
                    return None

    def readPolygonFeature(self, layer):
        self.feaArray = []  # 用于存储所有要素，这是个多维数组
        # 遍历每个要素
        for feat in layer:
            geom_poly = []  # 存储要素的各个环的数组
            geoms = feat.GetGeometryRef()

            for geom_idx in range(geoms.GetGeometryCount()):
                geom_ring = []  # 存储环的坐标对
                ring = geoms.GetGeometryRef(geom_idx)
                # 遍历每个环下的所有点
                for point_idx in range(ring.GetPointCount()):
                    # 将每个坐标对加入到geom_ring中
                    geom_ring.append((ring.GetX(point_idx), ring.GetY(point_idx), ring.GetZ(point_idx)))
                # 将ring加入到geom_poly
                geom_poly.append(geom_ring)
            # 将polygon加入到feaArray中
            self.feaArray.append(geom_poly)

    def writePolygonFeature(self, src_layer, tgt_layer, newpoints, isCopyFeature, geom_type):
        poly_idx = 0
        tgt_layer_Defn = tgt_layer.GetLayerDefn()
        for feature in src_layer:
            # 复制源要素
            if isCopyFeature:
                newFeature = feature.Clone()
                # 并且赋予新坐标
                if newpoints is not None:
                    polygon = newFeature.GetGeometryRef()  # 得到feature中的polygon
                    polygon_rings = newpoints[poly_idx]  # 得到polygon中的ring的列表
                    # 遍历每个环
                    for ring_idx in range(polygon.GetGeometryCount()):
                        ring = polygon.GetGeometryRef(ring_idx)  # 得到某个ring
                        ring_points = polygon_rings[ring_idx]  # 得到ring中的point的列表
                        # 遍历每个环下的所有点
                        for point_idx in range(ring.GetPointCount()):
                            # 设置各个点的坐标
                            point = ring_points[point_idx]
                            ring.SetPoint(point_idx, point[0], point[1], point[2])
            # 创建空要素
            else:
                # 为空要素添加几何体
                if newpoints is not None:
                    polygon_rings = newpoints[poly_idx]
                    newFeature = ogr.Feature(tgt_layer_Defn)
                    polygon = ogr.Geometry(geom_type)  # 创建一个polygon
                    for ring_poitns in polygon_rings:
                        ring = ogr.Geometry(ogr.wkbLinearRing)  # 为polygon创建ring
                        for point in ring_poitns:
                            ring.AddPoint(point[0], point[1], point[2])
                            # 将ring添加到polygon中
                        polygon.AddGeometry(ring)
                    newFeature.SetGeometry(polygon)
                else:
                    return None

            if tgt_layer.CreateFeature(newFeature) != 0:
                print(f"Feature {poly_idx} create failed!")
            poly_idx += 1

    def readLineFeature(self, layer):
        # 遍历每个线要素
        for feat in layer:
            line = feat.GetGeometryRef()
            geom_line = []  # 存储坐标对的线要素
            for point_idx in range(line.GetPointCount()):
                geom_line.append((line.GetX(point_idx), line.GetY(point_idx), line.GetZ(point_idx)))

            self.feaArray.append(geom_line)

    def writeLineFeature(self, src_layer, tgt_layer, newpoints, isCopyFeature, geom_type):
        line_idx = 0
        tgt_layer_Defn = tgt_layer.GetLayerDefn()
        for feature in src_layer:
            # 复制源要素
            if isCopyFeature:
                newFeature = feature.Clone()
                # 并且赋予新坐标
                if newpoints is not None:
                    line = newFeature.GetGeometryRef()  # 得到feature中的创建一个lineString
                    line_points = newpoints[line_idx]  # 得到polyline中的point的列表
                    for point_idx in range(line.GetPointCount()):
                        # 设置各个点的坐标
                        point = line_points[point_idx]
                        line.SetPoint(point_idx, point[0], point[1], point[2])
            # 创建空要素
            else:
                # 为空要素添加几何体
                if newpoints is not None:
                    line_points = newpoints[line_idx]
                    newFeature = ogr.Feature(tgt_layer_Defn)
                    line = ogr.Geometry(geom_type)  # 创建一个lineString
                    for point in line_points:
                        line.AddPoint(point[0], point[1], point[2])

                    newFeature.SetGeometry(line)
                else:
                    return None

            if tgt_layer.CreateFeature(newFeature) != 0:
                print(f"Feature {line_idx} create failed!")
            line_idx += 1

    def readPointFeature(self, layer):
        # 遍历每个点要素
        for feat in layer:
            point = feat.GetGeometryRef()
            self.feaArray.append((point.GetX(0), point.GetY(0), point.GetZ(0)))

    def writePointFeature(self, src_layer, tgt_layer, newpoints, isCopyFeature, geom_type):
        point_idx = 0
        tgt_layer_Defn = tgt_layer.GetLayerDefn()
        for feature in src_layer:
            # 复制源要素
            if isCopyFeature:
                newFeature = feature.Clone()
                # 并且赋予新坐标
                if newpoints is not None:
                    point = newFeature.GetGeometryRef()  # 得到feature中的创建一个point
                    location = newpoints[point_idx]  # 得到point的坐标
                    point.SetPoint(0, location[0], location[1], location[2])
            # 创建空要素
            else:
                # 为空要素添加几何体
                if newpoints is not None:
                    location = newpoints[point_idx]
                    newFeature = ogr.Feature(tgt_layer_Defn)
                    point = ogr.Geometry(geom_type)  # 创建一个point
                    point.AddPoint(location[0], location[1], location[2])

                    newFeature.SetGeometry(point)
                else:
                    return None

            if tgt_layer.CreateFeature(newFeature) != 0:
                print(f"Feature {point_idx} create failed!")
            point_idx += 1


if __name__ == '__main__':
    import copy

    dirname = os.path.split(os.path.abspath(__file__))[0]
    os.chdir(dirname)
    osgConverter = OSGVecDataConverter(dirname + r"\data\ControlPolygons.shp", "ESRI Shapefile")
    # osgConverter = OSGVecDataConverter(r".\data\ControlPoints.shp", "ESRI Shapefile")
    # osgConverter = OSGVecDataConverter(r".\data\ControlLines.shp", "ESRI Shapefile")
    features = osgConverter.GetXYZ()
    # 训练一个坐标转换算法
    np.set_printoptions(suppress=True)
    L = [[3391528.524, 483058.025, 212.191, 3391480.452, 483007.7061, 212.191],
         [3397833.33, 503800.445, 16.058, 3397785.261, 503750.1382, 16.154],
         [3397832.012, 522616.596, 136.225, 3397783.94, 522566.2938, 136.225],
         [3372118.452, 518833.498, 18.755, 3372070.366, 518783.1979, 18.755],
         [3370410.392, 497127.368, 19.814, 3370362.308, 497077.0512, 19.814],
         [3368398.831, 487063.781, 20.342, 3368350.746, 487013.4587, 20.342],
         [3377215.451, 482559.198, 38.342, 3377167.373, 482508.8726, 38.342]]

    brs = Brusa_Wolf(np.array(L))
    dic = brs.fit()
    print(brs.Predict_points)

    predict_points = brs.predict(np.array(osgConverter.FeaturesRavel(features, ogr.wkbPolygon)))
    newpoints = osgConverter.FeatureNdaaray(features, predict_points, ogr.wkbPolygon)

    # 开始坐标转换
    srs = OSGVecDataConverter.CreateProjSpatialReference(2378)
    print(srs.GetName())

    # 创建一个中间空文件，然后创建新要素，并且赋予新坐标
    target_filename = dirname + r"\data\ControlPolygonsFromGDAL.dxf"
    trans_filename = dirname + r"\data\transFile.shp"
    osgConverter.CreateTransFile(trans_filename, srs, False)
    driver = ogr.GetDriverByName("ESRI Shapefile")
    trans_ds = driver.Open(trans_filename, 1)
    osgConverter.CreateFeatures(trans_ds, newpoints, False)
    trans_ds.Destroy()
    osgConverter.FormatTrans("DXF", target_filename, True)
