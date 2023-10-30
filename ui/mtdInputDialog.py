from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

from numpy import loadtxt

from ui.base_ui.mtdInputDialog import Ui_Dialog

class mtdInputDialog(QDialog):
    def __init__(self):
        super(mtdInputDialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.data = None
        self.freq = None

        self.ui.buttonBox.accepted.connect(self.accept_data)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.freqFileButton.clicked.connect(self.open_freq_file)

        int_validator = QRegExpValidator(QRegExp(r'[0-9]+'))

        # self.ui.NT_lineEdit.setValidator(int_validator)
        # self.ui.Q_lineEdit.setValidator(int_validator)
        # self.ui.T_lineEdit.setValidator(int_validator)

    def accept_data(self):
        if self.ui.Q_lineEdit.text():
            self.data = int(self.ui.NT_lineEdit.text()), float(self.ui.T_lineEdit.text()), float(self.ui.Q_lineEdit.text())
        else:
            self.data = self.freq
        self.accept()

    def open_freq_file(self):
        freq_file_name = self.open_dialog()
        if freq_file_name == 0:
            return
        self.ui.freqFileName.clear()
        self.ui.freqFileName.setText(freq_file_name)
        self.freq = loadtxt(freq_file_name)
        self.ui.NT_lineEdit.setText(str(len(self.freq)))
        self.ui.T_lineEdit.setText(str(self.freq[0]))
        self.ui.Q_lineEdit.clear()

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
