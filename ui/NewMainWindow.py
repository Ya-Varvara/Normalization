import os

from PyQt5.QtWidgets import QMainWindow

from ui.base_ui.NewMainWindow import Ui_MainWindow
from ui.TreeWidget import TreeWidget
from ui.NormalizationControlWidget import NormalizationControlWidget
from ui.Inversion1DControlWidget import Inversion1DControlWidget
from ui.InversionTypeWidget import InversionTypeWidget

from models.normalization_models import NormalizationProfileModel

from handlers.supportDialogs import open_file_dialog


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.widgets = []

        self.tree = TreeWidget(self)
        self.ui.treeDock.setWidget(self.tree)

        self.normalization_control = NormalizationControlWidget(self, self.tree)
        self.inversion_1d_control = Inversion1DControlWidget(self, self.tree)
        self.inversion_type = InversionTypeWidget([self.inversion_1d_control])

        self.ui.tabWidget.addTab(self.normalization_control, 'Normalization')
        self.ui.tabWidget.addTab(self.inversion_type, 'Inversion')

        self.normalization_control.ui.openFileBtn.clicked.connect(self.open_files)
        self.inversion_1d_control.ui.openFileBtn.clicked.connect(self.open_files)

        self.inversion_1d_control.ui.goInversion_Btn.clicked.connect(self.do_inversion)

    def open_files(self):
        file_paths = open_file_dialog()
        if file_paths is None:
            return
        edi_files = []
        txt_files = []
        for path in file_paths:
            if path.endswith(".edi"):
                edi_files.append(path)
            elif path.endswith(".txt"):
                txt_files.append(path)

        self.tree.add_edi_file(edi_files)
        self.tree.add_txt_file(txt_files)
    
    def do_inversion(self):
        mesh_data, inversion_component, n_iteration, min_res, max_res = self.inversion_1d_control.get_inversion_data()
        ro_init, h_init, is_fixed_ro, is_fixed_h = tuple(mesh_data.values())
        edi_file = self.tree.get_checked_edi_file_paths()[0]
        print('invertion')
        print(inversion_component, n_iteration, min_res, max_res, ro_init, h_init, is_fixed_ro, is_fixed_h)


    def open_edi_files(self, file_paths):
        self.tree.add_edi_file(file_paths)

    def open_txt_files(self, file_paths):
        self.tree.add_txt_file(file_paths)

    def add_widget(self, widget):
        self.widgets.append(widget)
        self.ui.mainStackedWidget.addWidget(widget)

    def show_widget(self, widget):
        if widget not in self.widgets:
            self.add_widget(widget)
        self.ui.mainStackedWidget.setCurrentWidget(widget)
        self.normalization_control.set_visibility_buttons_checked(widget.visibility)

