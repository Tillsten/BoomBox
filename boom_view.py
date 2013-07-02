# -*- coding: utf-8 -*-
"""
Created on Mon Jul 01 14:56:32 2013

@author: Tillsten
"""



from __future__ import print_function

from PyQt4 import QtGui, QtCore
from qt_helpers import FlowLayout
Qt = QtCore.Qt
from boom_controller import Controller
controller = Controller()
controller.create_tab('Till')
controller.add_to_tab('Till', controller.inv[0])

class Signals(QtCore.QObject):
    update_tab = QtCore.pyqtSignal()

sig = Signals()

class ImageLabel(QtGui.QWidget):
    def __init__(self, text, image_path, parent=None):
        QtGui.QWidget.__init__(self, parent=parent)

        lay = QtGui.QVBoxLayout()

        self.setLayout(lay)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)

        self.pic = QtGui.QLabel()
        self.pixmap = QtGui.QPixmap(image_path)
        mode = QtCore.Qt.KeepAspectRatio
        self.pic.setPixmap(self.pixmap.scaled(100, 100, mode))
        self.pic.setStyleSheet( "margin:5px; border:1px solid rgb(0, 0, 0); ")
        lay.addWidget(self.pic)

        self.label = QtGui.QLabel(text)
        lay.addWidget(self.label)

    def mouseReleaseEvent(self, event):
        self.parent().item_clicked(self)

class Tab_view(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Tab_view, self).__init__(parent=parent)
        lay = QtGui.QVBoxLayout()
        self.setLayout(lay)
        title_font = QtGui.QFont()
        title_font.setPixelSize(30)
        self.title = QtGui.QLabel(None)
        self.title.setFont(title_font)
        lay.addWidget(self.title)

        self.table = QtGui.QTableWidget(5, 2)
        self.table.setHorizontalHeaderLabels(['Name', 'Preis'])
        self.table.setColumnWidth(1, 50)
        self.table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setAutoFillBackground(True)

        lay.addWidget(self.table)

        hsublay = QtGui.QHBoxLayout()
        self.total = QtGui.QLabel(u'Summe: 0,00 €')
        self.sub_total = QtGui.QLabel(u'Teilsumme: 0,00 €')
        hsublay.addWidget(self.total)
        hsublay.addWidget(self.sub_total)
        lay.addLayout(hsublay)


        pay_button = QtGui.QPushButton('Bezahlt!')
        pay_button.clicked.connect(self.paybut_clicked)
        lay.addWidget(pay_button)

        remove_button = QtGui.QPushButton('Entfern Posten')
        remove_button.clicked.connect(self.remove_clicked)
        lay.addWidget(remove_button)

        sig.update_tab.connect(self.update_tab)


    def set_tab(self, tab):
        self.title.setText(tab.name)
        self.table.setRowCount(len(tab.tab))

        for i, it in enumerate(tab.tab):
            self.table.setItem(i, 0, QtGui.QTableWidgetItem(it.name))
            self.table.setItem(i, 1, QtGui.QTableWidgetItem(str(it.price) + u' €'))
            self.table.item(i, 0).setTextAlignment(Qt.AlignLeft)
            self.table.item(i, 1).setTextAlignment(Qt.AlignRight)

        self.total.setText('Summe: ' +  str(tab.calc_total()) + u' €')

    def update_tab(self):
        self.set_tab(controller.current_tab)

    def paybut_clicked(self):
        controller.pay_tab(controller.current_tab.name)

    def remove_clicked(self):
        row = self.table.currentRow()
        tab = controller.current_tab
        item_text = tab.tab[row].name
        reply = QtGui.QMessageBox.question(self, u'Bestätige löschen?',
                                           u"Lösche {0} vom Zettel?".format(item_text),
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if reply:
            tab.remove_from_tab(tab.tab[row])


class Clients_view(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Clients_view, self).__init__(parent=parent)
        self.setLayout(QtGui.QVBoxLayout())
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Minimum)

        self.layout().addWidget(QtGui.QLabel('Zettel'))
        self.list = QtGui.QListWidget()
        self.list.currentItemChanged.connect(self.selected_tab_changed)
        self.layout().addWidget(self.list)

        self.add_button = QtGui.QPushButton('Neuer Zettel')
        self.add_button.clicked.connect(self.add_user_clicked)
        self.layout().addWidget(self.add_button)
        self.update_view()

    def update_view(self):
        self.list.clear()
        font = QtGui.QFont()
        font.setPixelSize(30)
        self.list.setFont(font)
        for i, tab in enumerate(controller.tabs):
            self.list.addItem(tab)

    def selected_tab_changed(self, new_item):
        if new_item:
            self.parent().parent().selected_tab_changed(new_item.text())

    def add_user_clicked(self):
        """
        Add a new tab after clicking the button.
        """
        text, ok = QtGui.QInputDialog.getText(self, "Neuer Zettel", "Zettel Name:",
                                          QtGui.QLineEdit.Normal,    '')
        if ok and text:
            try:
                controller.create_tab(str(text))
            except NameError:
                msgBox = QtGui.QMessageBox()
                msgBox.setText("The document has been modified.")
                msgBox.exec_()
            self.update_view()

class Itemlist_view(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Itemlist_view, self).__init__(parent=parent)
        self.setMinimumSize(600, 100)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        lay = FlowLayout(self)
        self.img_to_item = {}
        self.setLayout(lay)

    def add_items(self, list_of_items):
        for item in list_of_items:
            il = ImageLabel(item.name, item.image_path, self)
            self.layout().addWidget(il)
            self.img_to_item[il] = item
        #self.layout().addItem(QtGui.QSpacerItem(100, 100))

    def item_clicked(self, sender):
        item = self.img_to_item[sender]
        if controller.current_tab:
            controller.add_to_tab(controller.current_tab.name, item)
            sig.update_tab.emit()

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumSize(1000, 800)
        self.setWindowTitle("Boombox-Kasse!")
        wid = QtGui.QWidget()
        self.item_view = Itemlist_view(wid)
        self.tab_view = Tab_view(wid)
        self.client_view = Clients_view(self)
        lay = QtGui.QHBoxLayout(wid)
        lay.addWidget(self.item_view)
        lay.addWidget(self.client_view)
        lay.addWidget(self.tab_view)
        self.setCentralWidget(wid)

    def selected_tab_changed(self, name):
        controller.current_tab = controller.tabs[str(name)]
        self.tab_view.set_tab(controller.current_tab)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    sty = QtGui.QStyleFactory.create('cleanlooks')
    app.setStyle(sty)
    font = QtGui.QFont()
    font.setFamily('Calibri')
    font.setPixelSize(16)

    app.setFont(font)
    mw = MainWindow()
    mw.item_view.add_items(controller.inv)
    mw.show()
    app.exec_()