from ui.base_ui.mt1dControlWidget import Ui_Form
from PyQt5.QtWidgets import QWidget

from ui.SimpleModelDialog import SimpleModelDialog
from handlers.supportDialogs import open_file_dialog
from models.mtdModel import GridModel, SimpleModel
from mtd.importFileHandlers import import_model

from ui.TreeWidget import TreeWidget
from ui.mtdInputDialog import mtdInputDialog


class MT1DControlWidget(QWidget):
    def __init__(self, parent=None, tree: TreeWidget = None):
        super(MT1DControlWidget, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.parent = parent
        self.tree = tree

        self.ui.openModelFileBtn.clicked.connect(self.open_model)
        self.ui.createModelFileBtn.clicked.connect(self.create_model)
        self.ui.openPeriodFileBtn.clicked.connect(self.open_period)
        self.ui.createPeriodFileBtn.clicked.connect(self.create_period)

        self.ui.modelComboBox.addItems([x.tree_label for x in self.tree.mtd_models])
        self.ui.periodComboCox.addItems([x.tree_label for x in self.tree.mtd_freq])

    def open_model(self):
        file_path = open_file_dialog()

        if not file_path:
            print("Error")
            return

        data = import_model(file_path)

        if data[0] == 'dsaa':
            model = GridModel(file_path, data)
        elif data[0] == 'one row':
            model = SimpleModel(file_path, data[1], data[2])
        elif data[0] == 'one row with freq':
            model = SimpleModel(file_path, data[1], data[2], data[3])
        else:
            model = None
            print('[ERROR] Unknown type of file')

        if model:
            self.tree.add_mtd_model(model)

    def create_model(self):
        dialog = SimpleModelDialog()
        dialog.show()
        if dialog.exec_():
            data = dialog.data
            file_path = dialog.file_name
            model = SimpleModel(file_path, data[0], data[1], data[2])
            self.tree.add_mtd_model(model)

    def open_period(self):
        dialog = mtdInputDialog()
        dialog.show()
        if dialog.exec_():
            self.models[self.current_model_id].freq_data = dialog.data

    def create_period(self):
        pass
