from ui.base_ui.Inversion1DControlWidget import Ui_Form
from PyQt5.QtWidgets import QWidget

from ui.SimpleModelDialog import SimpleModelDialog


class Inversion1DControlWidget(QWidget):
    def __init__(self, parent=None, tree=None):
        super(Inversion1DControlWidget, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.parent = parent

        self.inversion_data = ['xy', 'yx', 'eff']
        self.mesh_data = None

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

        for data in self.inversion_data:
            self.ui.inversionDataComboBox.addItem(data)

        self.ui.meshEdit_Btn.clicked.connect(self.create_simple_model)

    def create_simple_model(self):
        print('Clicked')
        dialog = SimpleModelDialog()
        dialog.show()
        if dialog.exec_():
            self.mesh_data = dialog.data
    # end def create_simple_model

    def get_inversion_data(self) -> tuple():
        if self.mesh_data is None:
            self.create_simple_model()
        
        inversion_data = self.ui.inversionDataComboBox.currentText()

        n_iteration = int(self.ui.iterationLineEdit.text())
        min_res = float(self.ui.minInvertionLineEdit.text())
        max_res = float(self.ui.maxInvertionLineEdit.text())

        return self.mesh_data, inversion_data, n_iteration, min_res, max_res
