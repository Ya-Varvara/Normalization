from ui.base_ui.InversionTypeWidget import Ui_Form
from PyQt5.QtWidgets import QWidget


class InversionTypeWidget(QWidget):
    def __init__(self, control_widgets):
        super(InversionTypeWidget, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.control_widgets = control_widgets

        for widget in self.control_widgets:
            self.ui.stackedWidget.addWidget(widget)
            self.ui.stackedWidget.setCurrentWidget(widget)

        self.ui.type_2D_Btn.setDisabled(True)
        self.ui.type_3D_Btn.setDisabled(True)

        # self.ui.type_1D_Btn.clicked.connect(self.change_control_widget)

