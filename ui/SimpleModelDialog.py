from PyQt5.QtWidgets import QDialog, QFileDialog, QTableWidgetItem, QAbstractItemView
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
from numpy import loadtxt, append as npappend

from ui.base_ui.SimpleModelDialog import Ui_Dialog


class SimpleModelDialog(QDialog):
    def __init__(self, mesh_data=None):
        super(SimpleModelDialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        int_validator = QRegExpValidator(QRegExp(r'[0-9]+'))

        if mesh_data:
            self.data = mesh_data
            self.fill_table()
        else:
            self.data = {'ro_init': [0]*self.ui.modelTableWidget.rowCount(),
                         'h_init': [0]*self.ui.modelTableWidget.rowCount(),
                         'is_fixed_ro': [0]*self.ui.modelTableWidget.rowCount(),
                         'is_fixed_h': [0]*self.ui.modelTableWidget.rowCount()}
        self.file_name = None

        self.ui.modelFileName.setReadOnly(True)
        self.ui.modelFileName.setFocus(False)

        self.ui.modelTableWidget.setSelectionMode(QAbstractItemView.NoSelection)

        self.ui.buttonBox.accepted.connect(self.accept_data)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.ui.addRowButton.clicked.connect(self.add_table_row)
        self.ui.deleteRowButton.clicked.connect(self.delete_table_row)

        self.ui.modelFileButton.clicked.connect(self.open_model_file)

        self.ui.modelTableWidget.itemClicked.connect(self.fix_ro_h)
        self.ui.modelTableWidget.itemChanged.connect(self.change_data)

    def accept_data(self):
        # self.get_data()
        self.accept()

    def change_data(self, item):
        column, row = item.column(), item.row()
        column_name = 'h_init' if column else 'ro_init'
        if item.text():
            self.data[column_name][row] = float(item.text())
        # print(self.data)

    def fix_ro_h(self):
        item = self.ui.modelTableWidget.model().data(self.ui.modelTableWidget.currentIndex())
        column, row = self.ui.modelTableWidget.currentColumn(), self.ui.modelTableWidget.currentRow()
        column_name = 'is_fixed_h' if column else 'is_fixed_ro'
        if item:
            if sum(self.data[column_name]):
                old_row = self.data[column_name].index(1)
                self.ui.modelTableWidget.item(old_row, column).setSelected(False)
                self.data[column_name] = [0]*len(self.data[column_name])
                if old_row == row:
                    # print(self.data['is_fixed_h'], self.data['is_fixed_ro'])
                    return
            self.data[column_name][row] = 1
            self.ui.modelTableWidget.item(row, column).setSelected(True)
        # print(self.data['is_fixed_h'], self.data['is_fixed_ro'])

    def open_model_file(self):
        self.file_name = self.open_dialog()
        if self.file_name == 0:
            return
        
        self.ui.modelFileName.clear()
        self.ui.modelFileName.setText(self.file_name)
        self.ui.modelTableWidget.clear()
        self.ui.modelTableWidget.setHorizontalHeaderLabels(['Ro', 'H'])

        mod = loadtxt(self.file_name, skiprows=2)
        ro_init = list(mod[:, 0])
        h_init = list(mod[:, 1])

        self.data['ro_init'] = ro_init
        self.data['h_init'] = h_init
        self.data['is_fixed_ro'] = [0]*len(ro_init)
        self.data['is_fixed_h'] = [0]*len(h_init)

        # print(len(ro_init), ro_init, len(h_init), h_init)

        self.ui.modelTableWidget.setRowCount(len(ro_init))
        for row in range(self.ui.modelTableWidget.rowCount()):
            self.ui.modelTableWidget.setItem(row, 0, QTableWidgetItem(str(ro_init[row])))
            self.ui.modelTableWidget.setItem(row, 1, QTableWidgetItem(str(h_init[row])))

    def fill_table(self):
        ro_init = self.data['ro_init']
        h_init = self.data['h_init']
        is_fixed_ro = self.data['is_fixed_ro']
        is_fixed_h = self.data['is_fixed_h']
        self.ui.modelTableWidget.setRowCount(len(ro_init))
        for row in range(self.ui.modelTableWidget.rowCount()):
            self.ui.modelTableWidget.setItem(row, 0, QTableWidgetItem(str(ro_init[row])))
            self.ui.modelTableWidget.item(row, 0).setSelected(is_fixed_ro[row])
            self.ui.modelTableWidget.setItem(row, 1, QTableWidgetItem(str(h_init[row])))
            self.ui.modelTableWidget.item(row, 1).setSelected(is_fixed_h[row])

    def add_table_row(self):
        self.ui.modelTableWidget.insertRow(self.ui.modelTableWidget.rowCount())
        self.data['ro_init'].append(0)
        self.data['h_init'].append(0)
        self.data['is_fixed_ro'].append(0)
        self.data['is_fixed_h'].append(0)
        # print(self.data)

    def delete_table_row(self):
        self.ui.modelTableWidget.removeRow(self.ui.modelTableWidget.rowCount()-1)
        self.data['ro_init'] = self.data['ro_init'][:-1]
        self.data['h_init'] = self.data['h_init'][:-1]
        self.data['is_fixed_ro'] = self.data['is_fixed_ro'][:-1]
        self.data['is_fixed_h'] = self.data['is_fixed_h'][:-1]
        # print(self.data)

    def open_dialog(self):
        file_filter = 'Data File (*.txt)'
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Открыть файл',
            filter=file_filter,
            initialFilter='Data File (*.txt)'
        )
        if response[0]:
            return response[0]
        else:
            return 0
