from PyQt5.QtWidgets import QDialog, QFileDialog, QTableWidgetItem
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
from numpy import loadtxt

from ui.base_ui.SimpleModelDialog import Ui_Dialog

class SimpleModelDialog(QDialog):
    def __init__(self):
        super(SimpleModelDialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        int_validator = QRegExpValidator(QRegExp(r'[0-9]+'))

        self.data = None
        self.freq = None
        self.file_name = None
        self.freq_file_name = None

        self.ui.buttonBox.accepted.connect(self.accept_data)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.ui.addRowButton.clicked.connect(self.add_table_row)
        self.ui.deleteRowButton.clicked.connect(self.delete_table_row)

        self.ui.modelFileButton.clicked.connect(self.open_model_file)
        self.ui.freqFileButton.clicked.connect(self.open_freq_file)

    def accept_data(self):
        self.get_data()
        self.accept()

    def open_model_file(self):
        self.file_name = self.open_dialog()
        if self.file_name == 0:
            return
        self.ui.modelFileName.clear()
        self.ui.modelFileName.setText(self.file_name)
        self.ui.modelTableWidget.clear()
        self.ui.modelTableWidget.setHorizontalHeaderLabels(['Ro', 'H'])

        with open(self.file_name, 'r') as f:
            # file_data = f.read()
            NT, T, Q = (float(x) for x in f.readline().split(' '))  # NT, T, Q
            N = int(f.readline().strip())
            Ro_list = [float(i) for i in f.readline().split()]
            H_list = [float(i) for i in f.readline().split()]
            H_list.append(' ')

        self.ui.modelTableWidget.setRowCount(len(Ro_list))
        for row in range(self.ui.modelTableWidget.rowCount()):
            self.ui.modelTableWidget.setItem(row, 0, QTableWidgetItem(str(Ro_list[row])))
            self.ui.modelTableWidget.setItem(row, 1, QTableWidgetItem(str(H_list[row])))
        self.ui.NT_lineEdit.setText(str(NT))
        self.ui.T_lineEdit.setText(str(T))
        self.ui.Q_lineEdit.setText(str(Q))
        # self.ui.modelEdit.setText(file_data)

    def open_freq_file(self):
        self.freq_file_name = self.open_dialog()
        if self.freq_file_name == 0:
            return
        self.ui.freqFileName.clear()
        self.ui.freqFileName.setText(self.freq_file_name)
        self.freq = loadtxt(self.freq_file_name)
        self.ui.NT_lineEdit.setText(str(len(self.freq)))
        self.ui.T_lineEdit.setText(str(self.freq[0]))
        self.ui.Q_lineEdit.clear()

    def get_data(self):
        Ro_list = []
        H_list = []
        i = 0
        for row in range(self.ui.modelTableWidget.rowCount()-1):
            if self.ui.modelTableWidget.item(row, 0) and self.ui.modelTableWidget.item(row, 1):
                Ro_list.append(float(self.ui.modelTableWidget.item(row, 0).text()))
                H_list.append(float(self.ui.modelTableWidget.item(row, 1).text()))
            elif self.ui.modelTableWidget.item(row, 0):
                Ro_list.append(float(self.ui.modelTableWidget.item(row, 0).text()))
            i += 1
        # Ro_list.append(float(self.ui.modelTableWidget.item(i, 0).text()))
        if self.freq is None:
            if self.ui.NT_lineEdit.text() and self.ui.T_lineEdit.text() and self.ui.Q_lineEdit.text():
                NT = int(float(self.ui.NT_lineEdit.text()))
                T = float(self.ui.T_lineEdit.text())
                Q = float(self.ui.Q_lineEdit.text())
                self.data = Ro_list, H_list, (NT, T, Q)
            else:
                self.data = Ro_list, H_list, None
        else:
            self.data = Ro_list, H_list, self.freq

    def add_table_row(self):
        self.ui.modelTableWidget.insertRow(self.ui.modelTableWidget.rowCount())

    def delete_table_row(self):
        self.ui.modelTableWidget.removeRow(self.ui.modelTableWidget.rowCount()-1)

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


