import sys
from PyQt5.Qt import *


class QCustomTableWidget(QTableWidget):
    def __init__(self, parent = None):
        super(QCustomTableWidget, self).__init__(parent)

    # 快捷菜单
    def contextMenuEvent(self, event):
        pmenu = QMenu(self)
        pDeleteAct = QAction('删除行', self)
        pmenu.addAction(pDeleteAct)
        pDeleteAct.triggered.connect(self.deleterows)
        pmenu.popup(self.mapToGlobal(event.pos()))
        event.accept()

    # 确认删除按钮的槽函数
    def deleterows(self):
        rr = QMessageBox.warning(self, "注意", "确认删除？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if rr == QMessageBox.Yes:
            curow = self.tableWidget.currentRow()

            # 我们取得当前表格的返回当前的选择模型selections。selectionModel()方法来源于QTableWidget类的父父类QAbstractItemView。
            selections = self.tableWidget.selectionModel()
            # 然后我们返回选择模型中被选中的所有行的索引selectedsList。
            selectedsList = selections.selectedRows()
            rows = []
            # 当我们选中一个单元格的时候，其实行是没有选中的，所以我们给rows列表增加当前行。否则就增加我们选中的行。然后就可以删除了。。。
            for r in selectedsList:
                rows.append(r.row())
            if len(rows) == 0:
                rows.append(curow)
                self.removeRows(rows, isdel_list=1)
            else:
                self.removeRows(rows, isdel_list=1)

    # 移除前n行或者选中的n个行的函数
    def removeRows(self, rows, isdel_list=0):
        if isdel_list != 0:
            rows.reverse()
            for i in rows:
                # 我们先把得到rows（行）列表倒序排列一下。
                # 从后往前删除行。否则会出现一些未知错误
                self.tableWidget.removeRow(i)
                del self.booklist[i]
            self.bookdb.save_db(self.booklist)
        else:
            # 倒序删除前n行，此时rows为一个整数
            for i in range(rows - 1, -1, -1):
                self.tableWidget.removeRow(i)
