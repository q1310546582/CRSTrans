from PyQt5.Qt import *
from PyQt5 import QtGui
import typing
from Window import Ui_CRSTransWindow
from tab_param_Panel import ParameterEstimationForm
import qdarkstyle

class CRSTrans(QWidget, Ui_CRSTransWindow):
    m_Drag = False

    def __init__(self, parent = None, title='Window', size=(500, 500), position=(200, 150), *args, **kw):
        """
        :param parent: QObject: deafualt:None
        :param title: String
        :param size: tuple(width,height)
        :param position: tuple(X,Y)
        :param args:
        :param kw:
        """
        super(CRSTrans, self).__init__(parent, *args, **kw)
        self.setWindowTitle(title)
        self.resize(size[0], size[1])
        self.move(position[0], position[1])
        self.init_ui()
        self.registSlot()

    def init_ui(self):
        """
        TODO: generate control for Window here
        """
        pass
        # Set UI interface of window according to Ui_Window.init_ui method
        self.setupUi(self)
        self.setContentControls()
        self.setToolbarsExclusive()
        self.setFrame()

    def setContentControls(self):
        if self.actionThree_Parameter.isChecked() :
            parameterEstimationForm = ParameterEstimationForm()
            layout = self.verticalLayout_tab_Params
            layout.replaceWidget(self.widgetContent, parameterEstimationForm.widgetContent)
            self.widgetContent.setParent(None)
            self.widgetContent = parameterEstimationForm

    # Set the mutually exclusive actions of all toolbars under the tab bar
    def setToolbarsExclusive(self):
        act_group = QActionGroup(self.toolbarParam)
        for i in self.toolbarParam.actions():
            act_group.addAction(i)
        act_group.setExclusive(True)

    # FramelessWindow
    def setFrame(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        # 边框阴影
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 设置具体阴影
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setOffset(0, 0);
        # 阴影颜色QColor(130,130,130, 127)
        shadow_effect.setColor(QColor(0, 0, 0, 255))
        # 阴影半径
        shadow_effect.setBlurRadius(10)
        self.frameTab.setGraphicsEffect(shadow_effect)

    def registSlot(self):
        self.BtnMaximize.clicked.connect(self.eventWindowMaxiMize)
        self.BtnMinimize.clicked.connect(self.eventWindowMiniMize)
        self.BtnCloseWindow.clicked.connect(self.eventWindowClose)

        # when the activated action changed, switch the config groupbox
        self.toolbarParam.actionTriggered.connect(self.widgetContent.eventSwitchGroupbox)
        self.widgetContent.currentActivatedAction = self.toolbarParam.actions()[0]

    def eventWindowMaxiMize(self):

        if QApplication.desktop().width() != self.width():
            self.showMaximized()
        else:
            self.showNormal()

    def eventWindowMiniMize(self):
        self.showMinimized()

    def eventWindowClose(self):
        self.close()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        # Set mouse drag window
        if (event.button() == Qt.LeftButton) :
            CRSTrans.m_Drag = True
            CRSTrans.m_DragPosition = event.globalPos() - self.pos()
        event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:

        if (event.buttons() & Qt.LeftButton & CRSTrans.m_Drag):
            self.move(event.globalPos() - CRSTrans.m_DragPosition)
        event.accept()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        CRSTrans.m_Drag = False
        event.accept()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    #设置样式表
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    window = CRSTrans()
    window.show()
    sys.exit(app.exec_())

