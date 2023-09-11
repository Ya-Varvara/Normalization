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
        self.widget_parent_models = []

        self.mtComponentButtons = {
            self.ui.xyBtn_resultGB: 'Rho XY',
            self.ui.yxBtn_resultGB: 'Rho YX',
            self.ui.xyBtn_phaseGB: 'PHI XY',
            self.ui.yxBtn_phaseGB: 'PHI YX',
            self.ui.effBtn_resultGB: 'Rho Eff',
            self.ui.effBtn_phaseGB: 'PHI Eff'
        }

        self.ui.openFileBtn.clicked.connect(self.open_edi_files)
        self.ui.saveFileBtn.clicked.connect(self.tree.save_normalization)
        self.ui.goNormalizationBtn.clicked.connect(self.check_input)
        self.ui.xyBtn_resultGB.clicked.connect(self.change_visible)
        self.ui.yxBtn_resultGB.clicked.connect(self.change_visible)
        self.ui.effBtn_resultGB.clicked.connect(self.change_visible)
        self.ui.xyBtn_phaseGB.clicked.connect(self.change_visible)
        self.ui.yxBtn_phaseGB.clicked.connect(self.change_visible)
        self.ui.effBtn_phaseGB.clicked.connect(self.change_visible)

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

        model = self.tree.get_selected_normalization_model()
        self.tree.clear_selection()
        print(model)
        if model:
            self.tree.add_normalization_to_profile(model, model.add_normalization(period, mt_points))
            self.ui.mtPointLineEdit.clear()
            self.ui.periodLineEdit.clear()
        return

    def add_widget(self, widget):
        self.widgets.append(widget)
        self.ui.mainStackedWidget.addWidget(widget)

    def show_widget(self, widget):
        if widget not in self.widgets:
            self.add_widget(widget)
        self.ui.mainStackedWidget.setCurrentWidget(widget)
        self.set_visibility_buttons_checked(widget.visibility)

    def remove_widgets(self, widgets):
        for widget in widgets:
            self.ui.mainStackedWidget.removeWidget(widget)
        if self.ui.mainStackedWidget.count() > 2:
            current_widget = self.ui.mainStackedWidget.currentWidget()
            self.set_visibility_buttons_checked(current_widget.visibility)

    def change_visible(self):
        sender = self.sender()
        print(sender)
        model = self.tree.find_model_by_widget(self.ui.mainStackedWidget.currentWidget())
        model.data_widget.set_visible(self.mtComponentButtons[sender], sender.isChecked())

    def set_visibility_buttons_checked(self, visibility):
        for button, label in self.mtComponentButtons.items():
            button.setChecked(visibility[label])
