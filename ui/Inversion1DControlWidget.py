from ui.base_ui.Inversion1DControlWidget import Ui_Form
from PyQt5.QtWidgets import QWidget

from ui.SimpleModelDialog import SimpleModelDialog


class Inversion1DControlWidget(QWidget):
    def __init__(self, parent=None, tree=None):
        super(Inversion1DControlWidget, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.parent = parent

        self.ui.invertionType_Btn.setDisabled(True)
        self.ui.smoothingLineEdit.setDisabled(True)
        self.ui.stopInversion_Btn.setDisabled(True)
        self.ui.bodyCheckBox.setDisabled(True)
        self.ui.boreholeCheckBox.setDisabled(True)
        self.ui.boundaryCheckBox.setDisabled(True)
        self.ui.sourceModel_Btn.setDisabled(True)
        self.ui.addData_Btn.setDisabled(True)
        self.ui.equation_Btn.setDisabled(True)
        self.ui.saveFileBtn.setDisabled(True)

        self.ui.meshEdit_Btn.clicked.connect(self.create_simple_model)

    def create_simple_model(self):
        print('Clicked')
        dialog = SimpleModelDialog()
        dialog.show()
        if dialog.exec_():
            data = dialog.data
            file_path = dialog.file_name
            print(data, file_path)  
    # end def create_simple_model
