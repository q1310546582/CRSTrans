import subprocess

from osgeo import gdal, gdalconst
from osgeo import osr
from osgeo.gdalconst import *
import struct
import os

class GDALRasDataConverter:
    fileformat = {'USGSDEM': '.dem', 'ENVI': '.dat', 'GTiff': '.tiff', 'PNG': '.png', 'HFA': '.img', 'AAIGrid': '.asc',
                  'JPEG': '.jpg'}
    def __init__(self, sourceFilename, sourceDriverName):
        """
        :param sourceFilename:
        :param sourceDriverName:
        """
        self.src_filename = sourceFilename
        self.src_driverName = sourceDriverName
        self.src_driver = gdal.GetDriverByName(sourceDriverName)
        self.src_driver.Register()
        self.src_ds = gdal.Open(sourceFilename, 0)
        self.src_srs = self.src_ds.GetSpatialRef()
        if (self.src_ds == None):
            print('could not open')
            return None

    def FormatTrans(self, targetDriverName, targetFilename, INTERLEAVE = "PIXEL"):
        """
        :param targetDriverName: str: the driver name to create target dataset
        :param targetFilename: str: the target dataset absolute filename
        :param INTERLEAVE: options of CreateCopy()
        :return: None
        """
        if targetDriverName not in self.fileformat.keys():
            print("Unsupported drivername")
            return -1
        tgt_driver = gdal.GetDriverByName(targetDriverName)
        tgt_driver.Register()
        metadata = tgt_driver.GetMetadata()

        # 保存副本到文件中
        if metadata.get(gdal.DCAP_CREATECOPY) == "YES" or metadata.get(gdal.DCAP_CREATE) == "YES":
            print("Driver {} supports CreateCopy() method.".format(targetDriverName))

            global dst_ds
            if (targetDriverName == 'JPEG' or targetDriverName == 'PNG'):
                '''
                利用GDAL库函数创建图像时，一般会用到GDALDriver类Create()函数，但是Create()函数不支持JPEG、PNG等格式，
                不过，CreateCopy()支持这些格式，所以根据已有的图像数据，不能直接创建jpg、png格式的图像，而要借助GDAL的MEM内存文件，来创建他们。
                '''
                # 把数据保存到临时文件MEM
                m_Width = self.src_ds.RasterXSize
                m_Height = self.src_ds.RasterYSize
                pDriverMEM = gdal.GetDriverByName("MEM");
                pOutMEMDataset = pDriverMEM.CreateCopy("", self.src_ds, strict=0);
                buffer = self.src_ds.ReadRaster(0, 0, m_Width, m_Height, m_Width, m_Height, gdal.GDT_Float32)
                if (buffer == None):
                    print('读取失败')
                err = pOutMEMDataset.WriteRaster(0, 0, m_Width, m_Height, buffer, m_Width, m_Height, gdal.GDT_Float32);

                if err != gdal.CE_None:
                    print("写图像数据失败！");

                # 以创建复制的方式，生成jpg/png文件，注意这里使用 源数据的deriver
                dgt_ds = self.src_driver.CreateCopy(targetFilename, pOutMEMDataset, strict=0, options=["INTERLEAVE=" + INTERLEAVE])
            else:
                dgt_ds = tgt_driver.CreateCopy(targetFilename, self.src_ds, strict=0, options=["INTERLEAVE=" + INTERLEAVE])

            if (dgt_ds == None):
                print('{} created failed!'.format(targetFilename))
            else:
                dgt_ds.FlushCache()
                dgt_ds = None
                print('{} created success!'.format(targetFilename))
        else:
            print("Driver {} not supports CreateCopy nad Create() method!.".format(targetDriverName))

    @staticmethod
    def CreateProjSpatialReference( EPSG, **kw):
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

    def SrsTransform(self, src_EPSG, tgt_EPSG, tgt_filename, format, outType = 'Float32', resampling_method = 'bilinear', multiThread = False, overwrite = True, **createOption):
        cmd = f'gdalwarp -ot {outType} -s_srs EPSG:{src_EPSG} -t_srs EPSG:{tgt_EPSG} -r {resampling_method} {"-m" if multiThread else ""} -q -of ' \
        f'{format} {"-overwrite" if overwrite else ""} {"".join([f"-co {k}={v} "for k,v in createOption.items()])} -wo OPTIMIZE_SIZE=TRUE ' \
        f'{self.src_filename} {tgt_filename}'
        print(cmd)
        self.execute(cmd)

    def GetEPSG(self):
        return self.src_srs.GetAttrValue('AUTHORITY',1)

    def GetSpatialReference(self):
        return self.src_srs

    def execute(self, cmd):
        '''
        :param cmd: str: CMD command execution, get pipeline content, Not called by the outside user
        :return: None
        '''
        p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # 标准输出
        print(p1.communicate()[1].decode('utf-8', 'ignore'))
        return p1.poll()

    def GeographicRegistration(self):
        pass

if __name__ == '__main__':
    dirname = os.path.split(os.path.abspath(__file__))[0]
    src_filename = dirname + r'\data2\dem.dat'
    gdalConverter = GDALRasDataConverter(src_filename, "ENVI")
    # for driver,extension in GDALRasDataConverter.fileformat.items():
    #     tgt_drivername = driver
    #     tgt_filename = dirname + r'\data2\demFromGDAL' + extension
    #     gdalConverter.FormatTrans(tgt_drivername, tgt_filename, "PIXEL")
    gdalConverter.SrsTransform(4326, 4214, ".\data2\dem_wgs84_to_beijing54.dat", 'ENVI', INTERLEAVE='BSQ', SUFFIX='REPLACE')