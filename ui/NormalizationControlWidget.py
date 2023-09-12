from PyQt5.QtWidgets import QWidget

from ui.base_ui.NormalizationControlWidget import Ui_Form
from ui.TreeWidget import TreeWidget


class NormalizationControlWidget(QWidget):
    def __init__(self, parent=None, tree: TreeWidget = None):
        super(NormalizationControlWidget, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.parent = parent
        self.tree = tree

        self.mtComponentButtons = {
            self.ui.xyBtn_resultGB: 'Rho XY',
            self.ui.yxBtn_resultGB: 'Rho YX',
            self.ui.xyBtn_phaseGB: 'PHI XY',
            self.ui.yxBtn_phaseGB: 'PHI YX',
            self.ui.effBtn_resultGB: 'Rho Eff',
            self.ui.effBtn_phaseGB: 'PHI Eff'
        }

        self.ui.saveFileBtn.setDisabled(True)

        self.ui.goNormalizationBtn.clicked.connect(self.check_input)
        self.ui.xyBtn_resultGB.clicked.connect(self.change_visible)
        self.ui.yxBtn_resultGB.clicked.connect(self.change_visible)
        self.ui.effBtn_resultGB.clicked.connect(self.change_visible)
        self.ui.xyBtn_phaseGB.clicked.connect(self.change_visible)
        self.ui.yxBtn_phaseGB.clicked.connect(self.change_visible)
        self.ui.effBtn_phaseGB.clicked.connect(self.change_visible)

    def check_input(self):
        try:
            mt_points = int(self.ui.mtPointLineEdit.text())
            period = float(self.ui.periodLineEdit.text())
        except ValueError:
            print('Error')
            return

        model = self.tree.get_selected_normalization_model()
        self.tree.clear_selection()
        # print(model)
        if model:
            self.tree.add_normalization_to_profile(model, model.add_normalization(period, mt_points))
            self.ui.mtPointLineEdit.clear()
            self.ui.periodLineEdit.clear()
        return

    def set_visibility_buttons_checked(self, visibility):
        for button, label in self.mtComponentButtons.items():
            button.setChecked(visibility[label])

    def change_visible(self):
        sender = self.sender()
        print(sender)
        model = self.tree.find_model_by_widget(self.parent.ui.mainStackedWidget.currentWidget())
        model.data_widget.set_visible(self.mtComponentButtons[sender], sender.isChecked())
