from PyQt5.QtWidgets import QWidget, QComboBox, qApp

from handlers.supportDialogs import save_file_dialog, choose_folder
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

        # self.ui.saveFileBtn.setDisabled(True)

        self.ui.goNormalizationBtn.clicked.connect(self.check_input)
        self.ui.xyBtn_resultGB.clicked.connect(self.change_visible)
        self.ui.yxBtn_resultGB.clicked.connect(self.change_visible)
        self.ui.effBtn_resultGB.clicked.connect(self.change_visible)
        self.ui.xyBtn_phaseGB.clicked.connect(self.change_visible)
        self.ui.yxBtn_phaseGB.clicked.connect(self.change_visible)
        self.ui.effBtn_phaseGB.clicked.connect(self.change_visible)

        self.ui.saveFileBtn.clicked.connect(self.save_normalization)

        self.ui.profileComboBox.showPopup = self.update_combobox
        self.ui.saveNormComboBox.showPopup = self.update_save_norm_combobox
        self.ui.saveProfComboBox.showPopup = self.update_save_prof_combobox


    def check_input(self):
        try:
            mt_points = int(self.ui.mtPointLineEdit.text())
            period = float(self.ui.periodLineEdit.text())
        except ValueError:
            self.parent.show_statusbar_msg('Ошибка - введите mt_points, period', 10000)
            qApp.processEvents()
            return

        profile_label = self.ui.profileComboBox.currentText()
        if profile_label:
            model = list(filter(lambda pr: pr.tree_label == profile_label, self.tree.profiles))[0]
        else:
            self.parent.show_statusbar_msg('Ошибка - не выбран профиль', 10000)
            qApp.processEvents()
            return
        # self.tree.clear_selection()
        # print(model)
        if model:
            self.parent.show_statusbar_msg('Вычисление нормализации')
            qApp.processEvents()

            self.tree.add_normalization_to_profile(model, model.add_normalization(period, mt_points))
            self.ui.mtPointLineEdit.clear()
            self.ui.periodLineEdit.clear()

            self.parent.show_statusbar_msg('Расчет окончен', 2000)
            qApp.processEvents()
        return

    def set_visibility_buttons_checked(self, visibility):
        for button, label in self.mtComponentButtons.items():
            button.setChecked(visibility[label])

    def change_visible(self):
        sender = self.sender()
        print(sender)
        model = self.tree.find_model_by_widget(self.parent.ui.mainStackedWidget.currentWidget())
        model.data_widget.set_visible(self.mtComponentButtons[sender], sender.isChecked())

    def update_combobox(self):
        self.ui.profileComboBox.clear()
        items = ['']
        items.extend([x.tree_label for x in self.tree.profiles])
        self.ui.profileComboBox.addItems(items)
        QComboBox.showPopup(self.ui.profileComboBox)

    def update_save_prof_combobox(self):
        self.ui.saveProfComboBox.clear()
        items = ['']
        items.extend([x.tree_label for x in self.tree.profiles])
        self.ui.saveProfComboBox.addItems(items)
        QComboBox.showPopup(self.ui.saveProfComboBox)

    def update_save_norm_combobox(self):
        self.ui.saveNormComboBox.clear()
        profile_label = self.ui.saveProfComboBox.currentText()
        self.ui.saveNormComboBox.addItem('')
        self.ui.saveNormComboBox.addItem('all')
        if profile_label:
            profile = list(filter(lambda pr: pr.tree_label == profile_label, self.tree.profiles))[0]
            if profile.normalizations:
                for norm in profile.normalizations.values():
                    index = self.ui.saveNormComboBox.count()
                    self.ui.saveNormComboBox.insertSeparator(index)
                    print(norm.result_edi_files)
                    self.ui.saveNormComboBox.addItems([x.tree_label for x in norm.result_edi_files])
        else:
            for profile in self.tree.profiles:
                index = self.ui.saveNormComboBox.count()
                self.ui.saveNormComboBox.insertSeparator(index)
                self.ui.saveNormComboBox.addItems([x.tree_label for x in profile.get_all_normalized_edi_files()])

        QComboBox.showPopup(self.ui.saveNormComboBox)

    def save_normalization(self):
        profile_label = self.ui.saveProfComboBox.currentText()
        if not profile_label:
            self.parent.show_statusbar_msg(f'Не выбран профиль', 5000)
            qApp.processEvents()
            return

        profile = list(filter(lambda pr: pr.tree_label == profile_label, self.tree.profiles))[0]

        norm_label = self.ui.saveNormComboBox.currentText()
        if not norm_label:
            self.parent.show_statusbar_msg(f'Не выбрана нормализация', 5000)
            qApp.processEvents()
            return

        folder_path = choose_folder()
        if folder_path is None:
            self.parent.show_statusbar_msg(f'Не выбрана директория', 5000)
            qApp.processEvents()
            return

        self.parent.show_statusbar_msg(f'Сохранение файлов')
        qApp.processEvents()

        for norm in profile.normalizations.values():
            norm.export_edi(folder_path, norm_label)

        self.parent.show_statusbar_msg(f'Файлы сохранены')
        qApp.processEvents()

