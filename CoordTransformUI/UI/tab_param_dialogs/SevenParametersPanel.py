from PyQt5.Qt import *
from PyQt5 import QtGui
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.GxEllipsoidEnum import *
from CRSTrans_GitHub.CoordTransformUI.UI.tab_param_dialogs.SevenParametersGroupbox import Ui_SevenParametersGroupbox

class SevenParametersForm(QDialog, Ui_SevenParametersGroupbox):
    m_Drag = False

    def __init__(self, parent = None, title='Window', size=(500, 500), position=(300, 200), *args, **kw):
        """
        :param parent: QObject: deafualt:None
        :param title: String
        :param size: tuple(width,height)
        :param position: tuple(X,Y)
        :param args:
        :param kw:
        """
        super(SevenParametersForm, self).__init__(parent, *args, **kw)
        self.init_ui()

    def init_ui(self):
        """
        TODO: generate control for Window here
        """
        pass
        # Set UI interface of window according to Ui_Window.init_ui method
        self.setupUi(self)
        self.comboBox_Model.currentIndexChanged.connect(self.setConfigurationGroupBox)

    def setConfigurationGroupBox(self, index):
        if index == 0:
            self.comboBox_CoordType.setCurrentIndex(0)
        if index == 1:
            self.lineEdit_TransitionX.setEnabled(True)
            self.lineEdit_TransitionY.setEnabled(True)
            self.lineEdit_TransitionZ.setEnabled(True)
            self.comboBox_CoordType.setCurrentIndex(0)
        else:
            self.lineEdit_TransitionX.setEnabled(False)
            self.lineEdit_TransitionY.setEnabled(False)
            self.lineEdit_TransitionZ.setEnabled(False)

        if index == 2 or index == 3:
            self.lineEdit_SourceEPSG.setEnabled(True)
            self.lineEdit_TargetEPSG.setEnabled(True)
            self.comboBox_CoordType.setCurrentIndex(1)
        else:
            self.lineEdit_SourceEPSG.setEnabled(False)
            self.lineEdit_TargetEPSG.setEnabled(False)

if __name__ == '__main__':
    import sys
    from PyQt5.Qt import *
    from Window import *

    app = QApplication(sys.argv)

    # 创建第一个窗口控件
    window = SevenParametersForm()
    window.show()
    sys.exit(app.exec_())