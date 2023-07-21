from PyQt5.QtWidgets import QMainWindow

from ui.base_ui.MainWindow import Ui_MainWindow
from ui.TreeWidget import TreeWidget

from models.normalization_models import NormalizationProfileModel

from handlers.supportDialogs import open_file_dialog


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.tree = TreeWidget(self)
        self.ui.treeDock.setWidget(self.tree)
        self.widgets = []

        self.ui.openFileBtn.clicked.connect(self.open_edi_files)
        self.ui.saveFileBtn.clicked.connect(self.tree.save_normalization)
        self.ui.goNormalizationBtn.clicked.connect(self.check_input)

    def open_edi_files(self):
        file_paths = open_file_dialog()
        if file_paths is None:
            return
        self.tree.add_edi_file(file_paths)

    def check_input(self):
        try:
            mt_points = int(self.ui.mtPointLineEdit.text())
            period = float(self.ui.periodLineEdit.text())
        except ValueError:
            print('Error')
            return

        paths = self.tree.get_checked_edi_file_paths()
        self.tree.clear_selection()

        if isinstance(paths, NormalizationProfileModel):
            self.tree.add_normalization_to_profile(paths, paths.add_normalization(period, mt_points))
            return
        else:
            profile = NormalizationProfileModel(paths)
            profile.add_normalization(period, mt_points)
            self.tree.add_normalization_profile(profile)

    def add_widget(self, widget):
        self.widgets.append(widget)
        self.ui.mainStackedWidget.addWidget(widget)

    def show_widget(self, widget):
        if widget not in self.widgets:
            self.add_widget(widget)
        self.ui.mainStackedWidget.setCurrentWidget(widget)
