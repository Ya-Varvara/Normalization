from PyQt5.QtWidgets import QMainWindow

from ui.base_ui.MainWindow import Ui_MainWindow
from ui.TreeWidget import TreeWidget

from normalization.EDI import NormalizationProfileModel

from handlers.supportDialogs import save_file_dialog, open_file_dialog, choose_folder


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.tree = TreeWidget(self)
        self.ui.treeDock.setWidget(self.tree)

        self.ui.openFileBtn.clicked.connect(self.open_edi_files)
        self.ui.saveFileBtn.clicked.connect(self.save_normalization)
        self.ui.goNormalizationBtn.clicked.connect(self.check_input)

    def open_edi_files(self):
        file_paths = open_file_dialog()
        if file_paths is None:
            return
        self.tree.add_edi_file(file_paths)

    def check_input(self):
        try:
            mt_points = int(self.ui.mtPointLineEdit.text())
            sigma = float(self.ui.sigmaLineEdit.text())
            period = int(self.ui.periodLineEdit.text())
        except ValueError:
            print('Error')
            return

        paths = self.tree.get_checked_edi_file_paths()
        self.tree.clear_selection()

        print(mt_points, sigma, period, paths)

        norm = NormalizationProfileModel(paths)
        self.tree.add_normalization_profile(norm)

    def save_normalization(self):
        dir_path = choose_folder()
        print(dir_path)
