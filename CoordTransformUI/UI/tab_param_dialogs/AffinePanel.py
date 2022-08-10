from PyQt5.Qt import *
from PyQt5 import QtGui
from CRSTrans_GitHub.CoordTransformAlgorithms.Algorithms.GxEllipsoidEnum import *
from CRSTrans_GitHub.CoordTransformUI.UI.tab_param_dialogs.AffineGroupbox import Ui_AffineTransForm

class AffineTransForm(QDialog, Ui_AffineTransForm):

    def __init__(self, parent = None, title='Window', size=(500, 500), position=(300, 200), *args, **kw):
        """
        :param parent: QObject: deafualt:None
        :param title: String
        :param size: tuple(width,height)
        :param position: tuple(X,Y)
        :param args:
        :param kw:
        """
        super(AffineTransForm, self).__init__(parent, *args, **kw)
        self.init_ui()

    def init_ui(self):
        """
        TODO: generate control for Window here
        """
        pass
        # Set UI interface of window according to Ui_Window.init_ui method
        self.setupUi(self)



if __name__ == '__main__':
    import sys
    from PyQt5.Qt import *
    from Window import *

    app = QApplication(sys.argv)

    # 创建第一个窗口控件
    window = AffineTransForm()
    window.show()
    sys.exit(app.exec_())