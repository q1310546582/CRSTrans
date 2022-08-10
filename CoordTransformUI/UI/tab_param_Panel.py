from PyQt5.Qt import *
from PyQt5 import QtGui, QtWidgets
import typing
import xml.dom.minidom

from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.GxEllipsoidEnum import GxEllipsoidEnum
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.TransToEllipseAsPublicClass import TransToEllipseAsPublicClass
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.Gx3DThreeParamsTrans import XYZ_3p
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.Gx2DFourParamsTrans import XY_4p
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.Gx3DFourParamsTrans import XYZ_4p
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.Gx3DBrusa_Wolf import Brusa_Wolf
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.Gx3DMolokinsky import Molokinsky
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.Gx3DSevenParamsTrans import Gx3DSevenParamsTrans
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.Gx2DSevenParamsTrans import Gx2DSevenParamsTrans
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.Gx2DPolynomialFitTrans import Poly_fit
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.Gx2DAffineTrans import Gx2DAffineTrans
from CRSTrans_GitHub.CoordTransformAlgorithms.Helper import *
from tab_param import Ui_ParameterEstimationForm
import numpy as np
import pandas as pd
from tab_param_dialogs.Dialog_TXTPanel import Dialog_txt
from tab_param_dialogs.FourParametersPanel import FourParametersForm
from tab_param_dialogs.ThreeParametersPanel import ThreeParametersForm
from tab_param_dialogs.SevenParametersPanel import SevenParametersForm
from tab_param_dialogs.PolyfitPanel import PolyfitForm
from tab_param_dialogs.AffinePanel import AffineTransForm


class ParameterEstimationForm(QWidget, Ui_ParameterEstimationForm):
    transMehtodMap = {'Gx3DThreeParamsTrans': TransformationMethods.ThreeParams3D, 'Gx2DFourParamsTrans':TransformationMethods.FourParams2D,
                      'Gx3DFourParamsTrans': TransformationMethods.FourParams3D, 'Gx3DBrusa_Wolf': TransformationMethods.Bursa,
                      'Gx3DMolokinsky': TransformationMethods.Molodensky, 'Gx3DSevenParamsTrans': TransformationMethods.SevenParams3D,
                      'Gx2DSevenParamsTrans': TransformationMethods.SevenParams2D, 'Gx2DPolynomialFitTrans': TransformationMethods.Polynomial,
                      'Gx2DAffineTrans': TransformationMethods.AffineTrans}
    coordinateTypeMap = {'XYZ': CoordinateType.XYZ, 'XY': CoordinateType.XY, 'BLH': CoordinateType.BLH, 'BL': CoordinateType.BL}

    def __init__(self, parent = None, title='Window', size=(500, 500), position=(300, 200), *args, **kw):
        """
        :param parent: QObject: deafualt:None
        :param title: String
        :param size: tuple(width,height)
        :param position: tuple(X,Y)
        :param args:
        :param kw:
        """
        super(ParameterEstimationForm, self).__init__(parent, *args, **kw)
        self.move(500, 500)
        self.setWindowTitle(title)
        self.resize(size[0], size[1])
        self.move(position[0], position[1])
        self.init_ui()

    def init_ui(self):
        """
        TODO: generate control for Window here
        """
        pass
        # Set Set UI interface of window according to Ui_Window.init_ui method
        self.setupUi(self)
        self.setControlDraggable()
        self.setTableWidgetContextMenuUI()
        self.setButtonsShorCut()
        self.registEventSlot()


    # In order to make the three widgets (left, middle and right) in the widgetcontent can be dragged to change the size,
    # a splitter control is created here to replace the container widgetcontent
    def setControlDraggable(self):
        mainSplitter = QSplitter(Qt.Horizontal)
        # The color of the split line
        style = "QSplitter::handle { background-color: rgb(25,35,45); }"

        mainSplitter.setStyleSheet(style)
        mainSplitter.setHandleWidth(1)

        # it is not allowed to drag the divided sub window to 0.
        # The minimum value is limited to sizehint or maxsize/ minsize
        mainSplitter.setChildrenCollapsible(False)
        mainSplitter.setLayout(self.widgetContent.layout())
        # Take away the controls dragged out of the UI and put them into the splitter
        mainSplitter.addWidget(self.widgetContentLeft)
        mainSplitter.addWidget(self.widgetContentCenter)
        mainSplitter.addWidget(self.widgetContentRight)
        mainSplitter.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        # Replace the container QWidget dragged out of the UI with a splitter
        self.layout().replaceWidget(self.widgetContent, mainSplitter)
        # Clear the replaced control
        self.widgetContent.setParent(None)
        self.widgetContent = mainSplitter

        secondSplitter = QSplitter(Qt.Vertical)
        secondSplitter.setStyleSheet(style)
        secondSplitter.setHandleWidth(1)
        secondSplitter.setChildrenCollapsible(False)
        secondSplitter.setLayout(self.frame_ContentCenter.layout())
        secondSplitter.addWidget(self.widget_top_Centerframe)
        secondSplitter.addWidget(self.widget_bottom_Centerframe)
        self.widgetContentCenter.layout().replaceWidget(self.frame_ContentCenter, secondSplitter)
        self.frame_ContentCenter.setParent(None)
        self.frame_ContentCenter = secondSplitter

    def setTableWidgetContextMenuUI(self):
        self.tableWidget_ControlPoints.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidgetContextMenu = QMenu(self.tableWidget_ControlPoints)
        pDeleteAct = QAction('Delete', self.tableWidgetContextMenu)
        self.tableWidgetContextMenu.addAction(pDeleteAct)
        self.tableWidgetContextMenu.triggered.connect(self.eventDeleteTableWidgetRows)

    def registEventSlot(self):

        self.pushButton_Add.clicked.connect(self.eventAddControlPoint)
        self.pushButton_Delete.clicked.connect(self.eventDeleteControlPoint)
        self.pushButton_Modify.clicked.connect(self.eventModifyControlPoint)
        self.pushButton_Import.clicked.connect(self.eventImportControlPoitns)
        self.pushButton_Export.clicked.connect(self.eventExportControlPoints)
        self.pushButton_Start.clicked.connect(self.eventStart)
        self.pushButton_SaveParameters.clicked.connect(self.eventSaveParameters)

        self.tableWidget_ControlPoints.customContextMenuRequested.connect(self.eventTableWidgetContextMenu)
        self.tableWidget_ControlPoints.currentCellChanged.connect(self.eventTableWidgetCurrentCellChanged)

        self.eventShowIntrodcution(self.comboBox_Model.currentText())

    def setButtonsShorCut(self):
        self.pushButton_Add.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_A))
        self.pushButton_Delete.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_D))
        self.pushButton_Modify.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_M))
        self.pushButton_Import.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_I))
        self.pushButton_Export.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_E))
        self.pushButton_Start.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))

    # if combobox_model's current text change, create a thread to read the model introduction html
    def eventShowIntrodcution(self, text):

        thread = IO_Thread(text, self.textBrowser_Introduction)
        thread.io_finished.connect(self.ShowIntrodcution)
        thread.start()
        del thread


    def ShowIntrodcution(self, html):
        self.textBrowser_Introduction.setHtml(html)

    def eventAddControlPoint(self):
        try:
            sourceX = float(self.lineEdit_SourceX.text().strip())
            sourceY = float(self.lineEdit_SourceY.text().strip())
            sourceZ = float(self.lineEdit_SourceZ.text().strip())
            targetX = float(self.lineEdit_TargetX.text().strip())
            targetY = float(self.lineEdit_TargetY.text().strip())
            targetZ = float(self.lineEdit_TargetZ.text().strip())
            L = [sourceX, sourceY, sourceZ, targetX, targetY, targetZ, 0.0, 0.0, 0.0]
            self.insertRowToPublicArray(L)
            self.insertRowToTabWidgtet(L)
        except Exception as e:
            return QMessageBox.information(self, '', str(e), QMessageBox.Yes)

    def insertRowToTabWidgtet(self, rowList):
        rownum = self.tableWidget_ControlPoints.rowCount()
        self.tableWidget_ControlPoints.insertRow(rownum)
        try:
            for colnum in range(self.tableWidget_ControlPoints.columnCount()):
                self.tableWidget_ControlPoints.setItem(rownum, colnum, QTableWidgetItem("%.7f"%rowList[colnum]))
        except Exception as e:
            QMessageBox.information(self, '', str(e), QMessageBox.Yes)
            return -1

    def insertRowToPublicArray(self, rowList):
        if self.tableWidget_ControlPoints.rowCount() == 0:
            self.__public_points = np.array([rowList])
        else:
            self.__public_points = np.concatenate((self.__public_points, np.array([rowList])), axis= 0)

    def eventImportControlPoitns(self):
        [fielName, fileFormat] = QFileDialog.getOpenFileName(self, "Import Control Points", "./", "TXT(*.txt);;CSV(*.csv)", "TXT(*.txt)")
        if(fielName != ''):

            if self.tableWidget_ControlPoints.rowCount() != 0:
                rr = QMessageBox.warning(self, "Information", "Confirm delete？", QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
                if rr == QMessageBox.Yes:
                    self.eventDeleteTableWidgetRows(None, True)
                else:
                    return

            # open fileDialog for *.txt format
            if fileFormat == 'TXT(*.txt)':
                # open modal dialog, user need to input Encoding and Separator
                Dialog_TXT = Dialog_txt(self, 'configuration')
                if Dialog_TXT.exec_() == 0:
                    return
                else:
                    spliter = Dialog_TXT.lineEdit.text()
                    encoding = Dialog_TXT.lineEdit_2.text()
                try:
                    with open('{}'.format(fielName), 'r', encoding=encoding) as f:
                        publicFiledata = f.readlines()
                    self.__public_points = self.expandDimension(np.array([self.__str2floatList(line, spliter) for line in publicFiledata]))
                    for row in self.__public_points:
                        if self.insertRowToTabWidgtet(row) == -1:
                            self.eventDeleteTableWidgetRows(None, True)
                            break
                except Exception as e:
                    message = 'File failed to read. Please check whether the format or path is correct'
                    return QMessageBox.information(self, 'IOError', str(e) + '\n' + message, QMessageBox.Yes)
            # open fileDialog for *.csv format
            else:
                try:
                    publicFiledata = pd.read_csv(fielName, header=None)
                    self.__public_points = publicFiledata.astype('float32').values
                    self.__public_points = self.expandDimension(np.concatenate((self.__public_points,np.zeros((publicFiledata.shape[0], 3))), axis=1))
                    for row in self.__public_points:
                        if self.insertRowToTabWidgtet(row) == -1:
                            self.eventDeleteTableWidgetRows(None, True)
                            break
                except Exception as e:
                    message = 'File failed to read. Please check whether the format or path is correct'
                    return QMessageBox.information(self, 'IOError', str(e) + '\n' + message, QMessageBox.Yes)

    # Expand the dimension of the array to 9 dimensions
    def expandDimension(self, array):
        rowcount, colcount = array.shape[0], array.shape[1]
        if colcount == 7:
            return np.insert(np.insert(array, 2, np.zeros(rowcount), axis=1), 5, np.zeros(rowcount), axis=1)
        else:
            return array

    # a list of str type is converted to list of float type
    def __str2floatList(self, x, spliter):
        try:
            # return [sourceX,Y,Z,targetX,Y,Z,residualX,Y,Z]
            return list(map(float, x.strip().split(spliter))) + [0.0, 0.0, 0.0]
        except Exception as e:
            return QMessageBox.information(self, '', str(e), QMessageBox.Yes)

    def eventExportControlPoints(self):
        if self.tableWidget_ControlPoints.rowCount() == 0: return
        [fielName, fileFormat] = QFileDialog.getSaveFileName(self, "Save Control Points", "./","TXT(*.txt);;CSV(*.csv)", "TXT(*.txt)")
        if(fielName != ''):
            # open fileDialog for *.txt format
            if fileFormat == 'TXT(*.txt)':
                # open modal dialog, user need to input Encoding and Separator
                Dialog_TXT = Dialog_txt(self, 'configuration')
                if Dialog_TXT.exec_() == 0:
                    return
                else:
                    spliter = Dialog_TXT.lineEdit.text()
                    encoding = Dialog_TXT.lineEdit_2.text()
                try:
                    wdata = [self.__float2strList(line, spliter) for line in self.__public_points[:, :6]]
                    with open('{}'.format(fielName), 'w+', encoding=encoding) as f:
                        f.writelines(wdata)
                    QMessageBox.information(self,'', 'Success!')
                except IOError:
                    message = 'File failed to open'
                    return QMessageBox.information(self, 'IOError', str(IOError) + '\n' + message, QMessageBox.Yes)
            # open fileDialog for *.csv format
            else:
                try:
                    pd.DataFrame(self.__public_points[:, :6]).to_csv(fielName, index=None, header= None)
                    QMessageBox.information(self, '', 'Success!')
                except IOError:
                    message = 'File failed to read. Please check whether the format or path is correct'
                    return QMessageBox.information(self, 'IOError', str(IOError) + '\n' + message, QMessageBox.Yes)

    def __float2strList(self, x, spliter):
        try:
            return spliter.join(list(map(str, x))) + '\n'
        except Exception as e:
            return QMessageBox.information(self, '', str(e), QMessageBox.Yes)

    def eventDeleteControlPoint(self):
        self.eventDeleteTableWidgetRows(None)

    def eventModifyControlPoint(self):
        try:
            currow = self.tableWidget_ControlPoints.currentRow()
            if currow == -1: return
            sourceX = float(self.lineEdit_SourceX.text().strip())
            sourceY = float(self.lineEdit_SourceY.text().strip())
            sourceZ = float(self.lineEdit_SourceZ.text().strip())
            targetX = float(self.lineEdit_TargetX.text().strip())
            targetY = float(self.lineEdit_TargetY.text().strip())
            targetZ = float(self.lineEdit_TargetZ.text().strip())
            if sourceX=='' or sourceY=='' or sourceZ=='' or targetX == '' or targetY == '' or targetZ == '':
                QMessageBox.information(self, '', 'Please enter complete information', QMessageBox.ButtonRole.YesRole)
            else:
                L = [sourceX, sourceY, sourceZ, targetX, targetY, targetZ, 0.0, 0.0, 0.0]

                self.modifyRowToTabWidgtet(L, currow)
        except Exception as e:
            return QMessageBox.information(self, '', str(e), QMessageBox.Yes)

    def modifyRowToTabWidgtet(self, rowList, currow):
        try:
            for colnum in range(self.tableWidget_ControlPoints.columnCount()):
                self.tableWidget_ControlPoints.setItem(currow, colnum, QTableWidgetItem(str(rowList[colnum])))
                self.__public_points[currow, colnum] = rowList[colnum]
        except Exception as e:
            return QMessageBox.information(self, '', str(e), QMessageBox.Yes)

    def eventTableWidgetContextMenu(self, pos):
        self.tableWidgetContextMenu.exec(QCursor.pos())

    def eventDeleteTableWidgetRows(self, action, clear = False):
        rows = []
        curow = self.tableWidget_ControlPoints.currentRow()
        if curow == -1 and clear == False: return
        if curow != -1 and clear == False:
            rr = QMessageBox.warning(self, "Information", "Confirm delete？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            rr = QMessageBox.Yes

        if rr == QMessageBox.Yes:
            if clear == True:
                for i in range(self.tableWidget_ControlPoints.rowCount()):
                    rows.append(i)
                rows.reverse()
                for i in rows:
                    self.tableWidget_ControlPoints.removeRow(i)
                    np.delete(self.__public_points, (i), axis=0)
            else:
                # get the current selection model
                selections = self.tableWidget_ControlPoints.selectionModel()
                # the selected rows of the model
                selectedsList = selections.selectedRows()

                for r in selectedsList:
                    rows.append(r.row())
                if len(rows) == 0:
                    # When we click only a cell, its row is not selected, so we append the current rownum to the rows list, and delete it
                    rows.append(curow)
                # a row or multirows are selected, and delete them,
                rows.reverse()
                # Delete rows from back to front. Ohterwise, some unkown errors may occur.
                for i in rows:
                    self.tableWidget_ControlPoints.removeRow(i)
                    self.__public_points = np.delete(self.__public_points, (i), axis=0)

    # When click a cell in distinct rows, its information will be showed in ControlPointsGroupBox
    def eventTableWidgetCurrentCellChanged(self, currentRow, currentColumn, previousRow, previousColumn):
        if currentRow == previousRow or currentRow == -1:
            return
        self.lineEdit_SourceX.setText(self.tableWidget_ControlPoints.item(currentRow, 0).text())
        self.lineEdit_SourceY.setText(self.tableWidget_ControlPoints.item(currentRow, 1).text())
        self.lineEdit_SourceZ.setText(self.tableWidget_ControlPoints.item(currentRow, 2).text())
        self.lineEdit_TargetX.setText(self.tableWidget_ControlPoints.item(currentRow, 3).text())
        self.lineEdit_TargetY.setText(self.tableWidget_ControlPoints.item(currentRow, 4).text())
        self.lineEdit_TargetZ.setText(self.tableWidget_ControlPoints.item(currentRow, 5).text())

    def eventStart(self):
        if self.tableWidget_ControlPoints.rowCount() == 0: return;
        self.treeWidget_Parameters.clear()
        self.treeWidget_Accuracy.clear()
        if self.comboBox_Model.currentText() == 'Gx3DThreeParamsTrans':
            self.result = self.doTrans(self.transMehtodMap['Gx3DThreeParamsTrans'], TransformationType.XYZ2XYZ, CoordinateType.XYZ, self.__public_points)
        elif self.comboBox_Model.currentText() == 'Gx2DFourParamsTrans':
            self.result = self.doTrans(self.transMehtodMap['Gx2DFourParamsTrans'], TransformationType.XY2XY, self.coordinateTypeMap[self.comboBox_CoordType.currentText()], self.__public_points)
        elif self.comboBox_Model.currentText() == 'Gx3DFourParamsTrans':
            self.result = self.doTrans(self.transMehtodMap['Gx3DFourParamsTrans'], TransformationType.XYZ2XYZ, self.coordinateTypeMap[self.comboBox_CoordType.currentText()], self.__public_points)
        elif self.comboBox_Model.currentText() == 'Gx3DBrusa_Wolf':
            self.result = self.doTrans(self.transMehtodMap['Gx3DBrusa_Wolf'], TransformationType.XYZ2XYZ, self.coordinateTypeMap[self.comboBox_CoordType.currentText()], self.__public_points)
        elif self.comboBox_Model.currentText() == 'Gx3DMolokinsky':
            self.result = self.doTrans(self.transMehtodMap['Gx3DMolokinsky'], TransformationType.XYZ2XYZ, self.coordinateTypeMap[self.comboBox_CoordType.currentText()], self.__public_points)
        elif self.comboBox_Model.currentText() == 'Gx3DSevenParamsTrans':
            self.result = self.doTrans(self.transMehtodMap['Gx3DSevenParamsTrans'], TransformationType.BLH2BLH, self.coordinateTypeMap[self.comboBox_CoordType.currentText()], self.__public_points)
        elif self.comboBox_Model.currentText() == 'Gx2DSevenParamsTrans':
            self.result = self.doTrans(self.transMehtodMap['Gx2DSevenParamsTrans'], TransformationType.BL2BL, self.coordinateTypeMap[self.comboBox_CoordType.currentText()], self.__public_points)
        elif self.comboBox_Model.currentText() == 'Gx2DPolynomialFitTrans':
            self.result = self.doTrans(self.transMehtodMap['Gx2DPolynomialFitTrans'], self.coordinateTypeMap[self.comboBox_CoordType.currentText()], self.coordinateTypeMap[self.comboBox_CoordType.currentText()], self.__public_points)
        elif self.comboBox_Model.currentText() == 'Gx2DAffineTrans':
            self.result = self.doTrans(self.transMehtodMap['Gx2DAffineTrans'], self.coordinateTypeMap[self.comboBox_CoordType.currentText()], self.coordinateTypeMap[self.comboBox_CoordType.currentText()], self.__public_points)
        else:
            return
        if self.result == QMessageBox.Yes or self.result == None:
            return
        self.showOutput()
        self.showResidualToTableWidget()
        self.showParametersAndAccuarcyToTreeWidget()

    def doTrans(self, transMethod, transType, coordinateType, publicPoints, **kwargs):
        """
        :param transMethod: TransformationMethods
        :param transType: TransformationType
        :param coordinateType: CoordinateType
        :param publicPoints: numpy.array
        :param kwargs:
        """
        if transMethod == TransformationMethods.ThreeParams3D and transType == TransformationType.XYZ2XYZ and coordinateType == CoordinateType.XYZ:
            try:
                L = [GxCoordinatePointPair(idx, CoordinateType.XYZ, item[0], item[1], item[2], item[3], item[4], item[5])
                     for idx, item in enumerate(publicPoints)]
                CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.XYZ)
                public_array = CoordinatePointPairArray.ToNumpyArray(3)
                self.model = XYZ_3p(public_array)
                dic = self.model.fit()
                return dic
            except Exception as e:
                return QMessageBox.information(self, '', str(e), QMessageBox.Yes)
        elif transMethod == TransformationMethods.FourParams2D and transType == TransformationType.XY2XY:
            try:
                L = [GxCoordinatePointPair(idx, CoordinateType.XYZ, item[0], item[1], item[2], item[3], item[4], item[5])
                    for idx, item in enumerate(publicPoints)]
                CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.XYZ)
                public_array = CoordinatePointPairArray.ToNumpyArray(2)
                self.model = XY_4p(public_array)
                dic = self.model.fit()
                return dic
            except Exception as e:
                return QMessageBox.information(self, '', str(e), QMessageBox.Yes)
        elif transMethod == TransformationMethods.FourParams3D and transType == TransformationType.XYZ2XYZ:
            try:
                lat = float(self.groupBox_Congfiguation.findChild(QLineEdit, 'lineEdit_latitude').text())
                long = float(self.groupBox_Congfiguation.findChild(QLineEdit, 'lineEdit_longitude').text())
                centry_point = [lat, long]
                L = [GxCoordinatePointPair(idx, CoordinateType.XYZ, item[0], item[1], item[2], item[3], item[4], item[5])
                     for idx, item in enumerate(publicPoints)]
                CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.XYZ)
                public_array = CoordinatePointPairArray.ToNumpyArray(3)
                self.model = XYZ_4p(centry_point, public_array)
                dic = self.model.fit()
                return dic
            except Exception as e:
                return QMessageBox.information(self, '', str(e), QMessageBox.Yes)
        elif transMethod == TransformationMethods.Bursa and transType == TransformationType.XYZ2XYZ:
            try:
                L = [GxCoordinatePointPair(idx, CoordinateType.XYZ, item[0], item[1], item[2], item[3], item[4], item[5])
                     for idx, item in enumerate(publicPoints)]
                CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.XYZ)
                public_array = CoordinatePointPairArray.ToNumpyArray(3)
                self.model = Brusa_Wolf( public_array)
                dic = self.model.fit()
                return dic
            except Exception as e:
                return QMessageBox.information(self, '', str(e), QMessageBox.Yes)
        elif transMethod == TransformationMethods.Molodensky and transType == TransformationType.XYZ2XYZ:
            try:
                transitionX = float(self.groupBox_Congfiguation.findChild(QLineEdit, 'lineEdit_TransitionX').text())
                transitionY = float(self.groupBox_Congfiguation.findChild(QLineEdit, 'lineEdit_TransitionY').text())
                transitionZ = float(self.groupBox_Congfiguation.findChild(QLineEdit, 'lineEdit_TransitionZ').text())
                L = [GxCoordinatePointPair(idx, CoordinateType.XYZ, item[0], item[1], item[2], item[3], item[4], item[5])
                     for idx, item in enumerate(publicPoints)]
                CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.XYZ)
                public_array = CoordinatePointPairArray.ToNumpyArray(3)
                self.model = Molokinsky((transitionX, transitionY, transitionZ), public_array)
                dic = self.model.fit()
                return dic
            except Exception as e:
                return QMessageBox.information(self, '', str(e), QMessageBox.Yes)
        elif transMethod == TransformationMethods.SevenParams3D and transType == TransformationType.BLH2BLH:
            try:
                sourceEPSGTxt = self.groupBox_Congfiguation.findChild(QLineEdit, 'lineEdit_SourceEPSG').text().strip()
                targetEPSGTxt = self.groupBox_Congfiguation.findChild(QLineEdit, 'lineEdit_TargetEPSG').text().strip()
                if  sourceEPSGTxt == '' or targetEPSGTxt == '':
                    QMessageBox.information(self,'', 'Please Input EPSG')
                    return None
                srcEPSG = int(sourceEPSGTxt)
                tgtEPSG = int(targetEPSGTxt)
                srcEllipsoid = TransToEllipseAsPublicClass.EPSGToEllipsoid(srcEPSG)
                tgtEllipsoid = TransToEllipseAsPublicClass.EPSGToEllipsoid(tgtEPSG)
                L = [GxCoordinatePointPair(idx, CoordinateType.BLH, item[0], item[1], item[2], item[3], item[4], item[5])
                     for idx, item in enumerate(publicPoints)]
                CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.BLH)
                public_array = CoordinatePointPairArray.ToNumpyArray(3)
                self.model = Gx3DSevenParamsTrans(source_ellipsoid=srcEllipsoid, target_ellipsoid=tgtEllipsoid,
                                      public_points=public_array)
                dic = self.model.fit()
                return dic
            except Exception as e:
                return QMessageBox.information(self, '', str(e), QMessageBox.Yes)
        elif transMethod == TransformationMethods.SevenParams2D and transType == TransformationType.BL2BL:
            try:
                sourceEPSGTxt = self.groupBox_Congfiguation.findChild(QLineEdit, 'lineEdit_SourceEPSG').text().strip()
                targetEPSGTxt = self.groupBox_Congfiguation.findChild(QLineEdit, 'lineEdit_TargetEPSG').text().strip()
                if  sourceEPSGTxt == '' or targetEPSGTxt == '':
                    QMessageBox.information(self,'', 'Please Input EPSG')
                    return None
                srcEPSG = int(sourceEPSGTxt)
                tgtEPSG = int(targetEPSGTxt)
                srcEllipsoid = TransToEllipseAsPublicClass.EPSGToEllipsoid(srcEPSG)
                tgtEllipsoid = TransToEllipseAsPublicClass.EPSGToEllipsoid(tgtEPSG)
                L = [GxCoordinatePointPair(idx, CoordinateType.BL, item[0], item[1], 0, item[3], item[4], 0) for idx, item
                     in enumerate(publicPoints)]
                CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.BL)
                public_array = CoordinatePointPairArray.ToNumpyArray(2)
                self.model = Gx2DSevenParamsTrans(source_ellipsoid=srcEllipsoid, target_ellipsoid=tgtEllipsoid,
                                      public_points=public_array)
                dic = self.model.fit()
                return dic
            except Exception as e:
                return QMessageBox.information(self, '', str(e), QMessageBox.Yes)
        elif transMethod == TransformationMethods.Polynomial:
            try:
                L = [GxCoordinatePointPair(idx, CoordinateType.XYZ, item[0], item[1], 0, item[3], item[4], 0)
                     for idx, item in enumerate(publicPoints)]
                CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.XY)
                public_array = CoordinatePointPairArray.ToNumpyArray(2)
                orderText = self.groupBox_Congfiguation.findChild(QComboBox, 'comboBox_Order').currentText()
                if orderText == 'Quadratic polynomial':
                    order = 2
                elif orderText == 'Cubic polynomial':
                    order = 3
                self.model = Poly_fit(public_array, coordinateType, order)
                dic = self.model.fit()
                return dic
            except Exception as e:
                return QMessageBox.information(self, '', str(e), QMessageBox.Yes)
        elif transMethod == TransformationMethods.AffineTrans:
            try:
                L = [GxCoordinatePointPair(idx, CoordinateType.XYZ, item[0], item[1], 0, item[3], item[4], 0)
                     for idx, item in enumerate(publicPoints)]
                CoordinatePointPairArray = GxCoordinatePointPairArray(L, CoordinateType.XY)
                public_array = CoordinatePointPairArray.ToNumpyArray(2)
                self.model = Gx2DAffineTrans(public_array)
                dic = self.model.fit()
                return dic
            except Exception as e:
                return QMessageBox.information(self, '', str(e), QMessageBox.Yes)
        else:
            return None


    def showOutput(self):
        cursor = self.textEdit_Output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)
        blockformat = cursor.blockFormat()
        blockformat.setAlignment(Qt.AlignLeft)
        cursor.setBlockFormat(blockformat)
        cursor.insertText("{} control points participate in the calculation\n".format(self.__public_points.shape[0]))
        cursor.insertText("Predict:\n")

        # insert a table of m rows and n columns
        ttf = QTextTableFormat()
        ttf.setAlignment(Qt.AlignCenter)
        # padding and margin pixels of table
        ttf.setCellPadding(2)
        ttf.setCellSpacing(0)
        # 15% width of every column of output panel width
        ttf.setColumnWidthConstraints((QTextLength(QTextLength.PercentageLength, 15),
                                       QTextLength(QTextLength.PercentageLength, 15),
                                       QTextLength(QTextLength.PercentageLength, 15),)
                                      )
        ttf.setHeaderRowCount(1)
        textTable = cursor.insertTable(self.__public_points.shape[0]+1, self.model.dimension, ttf)

        # fill the header row and set header format
        tcf = QTextCharFormat()
        font = QFont("Microsoft YaHei", 9 )
        font.setBold(True)
        tcf.setFont(font)
        header = ['predicX','predictY', 'predictZ']
        for col in range(textTable.columns()):
            cell = textTable.cellAt(0, col)
            cursorCell =cell.firstCursorPosition()
            blockFormat = cursorCell.blockFormat()
            blockFormat.setAlignment(Qt.AlignCenter)
            blockFormat.setBackground(QColor(69, 83, 100))
            cursorCell.setBlockFormat(blockFormat)
            cursorCell.setBlockCharFormat(tcf)
            cursorCell.insertText(header[col])
        # fill the content
        for row in range(1, textTable.rows()):
            for col in range(textTable.columns()):
                cell = textTable.cellAt(row, col)
                cursorCell = cell.firstCursorPosition()
                blockFormat = cursorCell.blockFormat()
                blockFormat.setAlignment(Qt.AlignCenter)
                cursorCell.setBlockFormat(blockFormat)
                cursorCell.insertText("%.7f"%self.model.Predict_points[row-1, col])

        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)
        blockFormat = cursor.blockFormat()
        blockFormat.setAlignment(Qt.AlignHCenter)
        blockFormat.setLineHeight(120, QTextBlockFormat.LineHeightTypes.ProportionalHeight)
        cursor.setBlockFormat(blockFormat)
        params = [f"{value}"  for value in self.result['x'].values()]
        cursor.insertText(f"\n\nmodel name：{self.result['model']}\n"
                          f"parameters：[{' '.join(params)}]\n"
                          f"MSE of coordinate component：[{''.join([f'{value} ' for value in self.result['axisMSE']])}]\n"
                          f"MSE of mean point：{self.result['MSE']}\n\n")

    def showResidualToTableWidget(self):
        residual = self.result['residual_array']
        self.__public_points[:, 6:6+residual.shape[1]] = residual
        for row in range(self.__public_points.shape[0]):
            for col in range(6, residual.shape[1] + 6):
                self.tableWidget_ControlPoints.setItem(row, col, QTableWidgetItem("%.7f"%residual[row][col-6]))

    def showParametersAndAccuarcyToTreeWidget(self):
        self.treeWidget_Parameters.clear()
        self.treeWidget_Accuracy.clear()
        params_num = self.result['x']
        for key,value in params_num.items():
            parameter = QTreeWidgetItem(["{}".format(key), "%.12f"%value])
            self.treeWidget_Parameters.addTopLevelItem(parameter)

        label = ['axisXorB_MSE', 'axisYorL_MSE', 'axisZorH_MSE']
        for i in range(len(self.result['axisMSE'])):
            axisMSE = QTreeWidgetItem([label[i], "%.12f"%self.result['axisMSE'][i]])
            self.treeWidget_Accuracy.addTopLevelItem(axisMSE)
        meanMSE = QTreeWidgetItem(["MSE_Mean_Point", "%.12f" % self.result['MSE']])
        self.treeWidget_Accuracy.addTopLevelItem(meanMSE)

    def eventSaveParameters(self):
        if self.treeWidget_Parameters.topLevelItemCount() == 0: return
        [fielName, fileFormat] = QFileDialog.getSaveFileName(self, "Save Summary", "./", "XML(*.xml)", "XML(*.xml)")
        if(fielName != ''):
            try:
                doc = xml.dom.minidom.Document()
                root = doc.createElement('Summary')
                doc.appendChild(root)

                parameters = doc.createElement('Parameters')
                root.appendChild(parameters)
                for i in range(self.treeWidget_Parameters.topLevelItemCount()):
                    attr = self.treeWidget_Parameters.topLevelItem(i).text(0)
                    value = self.treeWidget_Parameters.topLevelItem(i).text(1)
                    parameter = doc.createElement(attr)
                    parameter.appendChild(doc.createTextNode(value))
                    parameters.appendChild(parameter)

                accuracy = doc.createElement('Accuracy')
                root.appendChild(accuracy)
                for i in range(self.treeWidget_Accuracy.topLevelItemCount()):
                    attr = self.treeWidget_Accuracy.topLevelItem(i).text(0)
                    value = self.treeWidget_Accuracy.topLevelItem(i).text(1)
                    node = doc.createElement(attr)
                    node.appendChild(doc.createTextNode(value))
                    accuracy.appendChild(node)
                # Start writing XML documents
                with open(fielName, 'w') as f:
                    doc.writexml(f, indent='\t', addindent='\t', newl='\n', encoding="utf-8")
                QMessageBox.information(self, '', 'Success!')
            except IOError:
                message = 'File failed to open'

                return QMessageBox.information(self, 'IOError', str(IOError) + '\n' + message, QMessageBox.Yes)

    def eventSwitchGroupbox(self, action):
        if self.currentActivatedAction == action: return

        if action.objectName() == 'actionThree_Parameter':
            threeParametersGroupBox = ThreeParametersForm(self)
            self.switchGroupbox(threeParametersGroupBox)
        elif action.objectName() == 'actionFour_Parameter':
            fourParametersGroupBox = FourParametersForm(self)
            self.switchGroupbox(fourParametersGroupBox)
        elif action.objectName() == 'actionSeven_Parameter':
            sevenParametersForm = SevenParametersForm(self)
            self.switchGroupbox(sevenParametersForm)
        elif action.objectName() == 'actionPolynomial':
            polyfitForm = PolyfitForm(self)
            self.switchGroupbox(polyfitForm)
        elif action.objectName() == 'actionAffine':
            affineTransForm = AffineTransForm(self)
            self.switchGroupbox(affineTransForm)

        self.currentActivatedAction = action

    def switchGroupbox(self, widget):
        layout = self.frameTop_groupBox_frameInput.layout()
        layout.replaceWidget(self.groupBox_Congfiguation, widget.groupBox_Congfiguation)
        self.groupBox_Congfiguation.setParent(None)
        self.groupBox_Congfiguation = widget.groupBox_Congfiguation
        self.comboBox_Model = widget.comboBox_Model
        self.comboBox_CoordType = widget.comboBox_CoordType
        self.comboBox_Model.currentTextChanged.connect(self.eventShowIntrodcution)
        self.eventShowIntrodcution(widget.comboBox_Model.currentText())


class IO_Thread(QThread):
    io_finished = pyqtSignal(str)
    def __init__(self, text, widget):
        super(IO_Thread, self).__init__()
        self.text = text
        self.widget = widget

    def run(self):
        if self.text == 'Gx3DThreeParamsTrans':
            with open("introductionTXT/Gx3DThreeParamsModel.txt", 'r', encoding='utf-8') as f:
                self.io_finished.emit(''.join(f.readlines()))
        elif self.text == 'Gx2DFourParamsTrans':
            with open("introductionTXT/Gx2DFourParamsModel.txt", 'r', encoding='utf-8') as f:
                self.io_finished.emit(''.join(f.readlines()))
        elif self.text == 'Gx3DBrusa_Wolf':
            with open("introductionTXT/Gx3DBrusa_WolfModel.TXT", 'r', encoding='utf-8') as f:
                self.io_finished.emit(''.join(f.readlines()))
        elif self.text == 'Gx3DMolokinsky':
            with open("introductionTXT/Gx3DMolokinskyModel.TXT", 'r', encoding='utf-8') as f:
                self.io_finished.emit(''.join(f.readlines()))
        elif self.text == 'Gx3DSevenParamsTrans':
            with open("introductionTXT/Gx3DSevenParamsModel.TXT", 'r', encoding='utf-8') as f:
                self.io_finished.emit(''.join(f.readlines()))
        elif self.text == 'Gx2DSevenParamsTrans':
            with open("introductionTXT/Gx2DSevenParamsModel.TXT", 'r', encoding='utf-8') as f:
                self.io_finished.emit(''.join(f.readlines()))
        elif self.text == 'Gx2DPolynomialFitTrans':
            with open("introductionTXT/Gx2DPolyfitModel.TXT", 'r', encoding='utf-8') as f:
                self.io_finished.emit(''.join(f.readlines()))
        elif self.text == 'Gx2DAffineTrans':
            with open("introductionTXT/Gx2DAffineTransModel.TXT", 'r', encoding='utf-8') as f:
                self.io_finished.emit(''.join(f.readlines()))
        else:
            self.io_finished.emit('')

    def __del__(self):
        self.wait()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    window = ParameterEstimationForm()
    window.show()
    sys.exit(app.exec_())

