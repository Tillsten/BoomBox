# -*- coding: utf-8 -*-
"""
Created on Mon Jul 01 14:56:32 2013

@author: Tillsten
"""

from __future__ import print_function
from PyQt4 import QtGui, QtCore
from qt_helpers import FlowLayout, ImageLabel
Qt = QtCore.Qt
from boom_controller import Controller

controller = Controller()
controller.create_tab('Bar')



class Signals(QtCore.QObject):
    """Ui-signal registry"""
    update_tab = QtCore.pyqtSignal()
    update_client_list = QtCore.pyqtSignal()

sig = Signals()


class Tab_view(QtGui.QWidget):
    """View of single tab"""
    def __init__(self, parent=None):
        super(Tab_view, self).__init__(parent=parent)

        self._setup_table()
        self._setup_layout()

        self.table.selectionModel().selectionChanged.connect(
            self.selection_changed)

    def _setup_layout(self):
        """Setup the widget layout"""
        lay = QtGui.QVBoxLayout()
        self.setLayout(lay)

        title_font = QtGui.QFont()
        title_font.setPixelSize(40)
        title_font.setFamily('Humor Sans')
        self.title = QtGui.QLabel(None)
        self.title.setFont(title_font)

        sub_layout = QtGui.QHBoxLayout()
        self.total = QtGui.QLabel(u'Summe: 0,00 €')
        self.sub_total = QtGui.QLabel(u'Teilsumme: 0,00 €')
        sub_layout.addWidget(self.sub_total)
        sub_layout.addWidget(self.total)

        lay.addWidget(self.title)
        lay.addWidget(self.table)
        lay.addLayout(sub_layout)

        pay_button = QtGui.QPushButton('Bezahlen')
        pay_button.clicked.connect(self.paybut_clicked)
        lay.addWidget(pay_button)

        remove_button = QtGui.QPushButton('Entferne Posten')
        remove_button.clicked.connect(self.remove_clicked)
        lay.addWidget(remove_button)

        sig.update_tab.connect(self.update_tab)

    def _setup_table(self):
        """Setups and configures the QTableWidget"""

        table = QtGui.QTableWidget(5, 2)

        table.setHorizontalHeaderLabels(['Name', 'Preis'])
        table.setColumnWidth(1, 50)
        table.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
        table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        table.verticalHeader().hide()
        table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        table.setAutoFillBackground(True)
        self.table = table

    def render_tab(self, tab):
        """Render the tab-table."""
        self.title.setText(tab.name)
        self.table.setRowCount(len(tab.tab))

        for i, it in enumerate(tab.tab):
            self.table.setItem(i, 0, QtGui.QTableWidgetItem(it.name))
            self.table.setItem(i, 1,
                               QtGui.QTableWidgetItem(str(it.price) + u' €'))
            self.table.item(i, 0).setTextAlignment(Qt.AlignLeft)
            self.table.item(i, 1).setTextAlignment(Qt.AlignRight)

        self.total.setText('Summe: ' + str(tab.calc_total()) + u' €')

    def update_tab(self):
        """Method called if current_tab changed."""
        if controller.current_tab:
            self.render_tab(controller.current_tab)

    def selection_changed(self, sel):
        """Handler if selection in table changes, updates subtotal"""
        rows = self.table.selectionModel().selectedRows()
        tab = controller.current_tab
        sel = [tab.tab[i.row()] for i in rows]
        sub_total = (tab.calc_subtotal(sel))
        self.sub_total.setText('Teilsumme: ' + str(sub_total) + u' €')

    def paybut_clicked(self):
        """
        Calls msg-box if payment is made, if so process payment and
        deletes tab.
        """
        total = controller.current_tab.calc_total()
        ok = QtGui.QMessageBox.question(self, u'Bestätige Zahlung',
                                        u"{0} € vom Zettel bezahlt?".format(
                                            total),
                                        QtGui.QMessageBox.Yes,
                                        QtGui.QMessageBox.No)
        if ok:
            controller.pay_tab(controller.current_tab.name)
            sig.update_client_list.emit()
            sig.update_tab.emit()

    def remove_clicked(self):
        """Removes a item from the tab without payment."""
        self.table.selectedIndexes()
        row = self.table.currentRow()
        tab = controller.current_tab
        item_text = tab.tab[row].name
        reply = QtGui.QMessageBox.question(self, u'Bestätige löschen?',
                                           u"Lösche {0} vom Zettel?".format(
                                               item_text),
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if reply:
            tab.remove_from_tab(tab.tab[row])


class Clients_view(QtGui.QWidget):
    """Show all tabs/clients/tables and allows to chose one"""
    def __init__(self, parent=None):
        super(Clients_view, self).__init__(parent=parent)
        self._setup_layout()

    def _setup_layout(self):
        """Setup layout and connections"""
        self.setLayout(QtGui.QVBoxLayout())
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
                           QtGui.QSizePolicy.Minimum)

        self.layout().addWidget(QtGui.QLabel('Zettel'))
        self.list = QtGui.QListWidget()
        self.list.currentItemChanged.connect(self.selected_tab_changed)
        font = QtGui.QFont()
        font.setFamily('Humor Sans')
        font.setPixelSize(30)
        self.list.setFont(font)

        self.layout().addWidget(self.list)

        self.add_button = QtGui.QPushButton('Neuer Zettel')
        self.add_button.clicked.connect(self.add_user_clicked)
        self.layout().addWidget(self.add_button)

        sig.update_client_list.connect(self.render_view)
        self.render_view()

    def render_view(self):
        """Render the list"""
        self.list.clear()
        tab_list = sorted(controller.tabs)
        if tab_list.index('Bar') >= 0:
            tab_list.pop(tab_list.index('Bar'))
            tab_list.insert(0, 'Bar')

        for i, tab in enumerate(tab_list):
            self.list.addItem(tab)


    def selected_tab_changed(self, new_item):
        """
        Called if a list-item is clicked.
        """
        if new_item:
            controller.current_tab = controller.tabs[str(new_item.text())]
            sig.update_tab.emit()

    def add_user_clicked(self):
        """
        Add a new tab after clicking the button.
        """
        text, ok = QtGui.QInputDialog.getText(self, "Neuer Zettel",
                                              "Zettel Name:",
                                              QtGui.QLineEdit.Normal, '')
        if ok and text:
            try:
                controller.create_tab(str(text))
            except NameError:
                msgBox = QtGui.QMessageBox()
                msgBox.setText("The document has been modified.")
                msgBox.exec_()
            self.render_view()


class Itemlist_view(QtGui.QWidget):
    """
    Shows all the avaible items of the inventory. A click add them to the tab.
    """
    def __init__(self, parent=None):
        super(Itemlist_view, self).__init__(parent=parent)
        self.setMinimumSize(600, 100)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        lay = FlowLayout(self)
        self.img_to_item = {}
        self.setLayout(lay)

    def add_items(self, list_of_items):
        """
        Makes the list.
        """
        for item in list_of_items:
            il = ImageLabel(item.name, item.image_path, self)
            self.layout().addWidget(il)
            self.img_to_item[il] = item
            #self.layout().addItem(QtGui.QSpacerItem(100, 100))

    def item_clicked(self, sender):
        """
        If item is clicked, this function is called.
        """
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