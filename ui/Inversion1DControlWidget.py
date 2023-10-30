from handlers.supportDialogs import choose_folder
from models.InversionModel import InversionModel

from ui.base_ui.Inversion1DControlWidget import Ui_Form
from ui.SimpleModelDialog import SimpleModelDialog

from PyQt5.QtWidgets import QWidget, QComboBox, qApp
from PyQt5 import QtWidgets


class Inversion1DControlWidget(QWidget):
    def __init__(self, parent=None, tree=None):
        super(Inversion1DControlWidget, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.parent = parent
        self.tree = tree

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
        # self.ui.saveFileBtn.setDisabled(True)

        for data in self.inversion_data:
            self.ui.inversionDataComboBox.addItem(data)

        self.ui.meshEdit_Btn.clicked.connect(self.create_simple_model)
        self.ui.goInversion_Btn.clicked.connect(self.get_inversion_data)

        self.ui.profileComboBox.showPopup = self.update_profile_combobox
        self.ui.ediComboBox.showPopup = self.update_edi_combobox

        self.ui.saveInvComboBox.showPopup = self.update_inversion_combobox
        self.ui.saveNormComboBox.showPopup = self.update_normalization_combobox
        self.ui.saveProfComboBox.showPopup = self.update_save_profile_combobox

        self.ui.saveFileBtn.clicked.connect(self.save_inversion)

    def create_simple_model(self):
        dialog = SimpleModelDialog(self.mesh_data)
        dialog.show()
        if dialog.exec_():
            self.mesh_data = dialog.data

    # end def create_simple_model

    def get_inversion_data(self):
        if self.mesh_data is None:
            self.create_simple_model()

        inversion_component = self.ui.inversionDataComboBox.currentText()
        try:
            n_iteration = int(self.ui.iterationLineEdit.text())
            min_res = float(self.ui.minInvertionLineEdit.text())
            max_res = float(self.ui.maxInvertionLineEdit.text())
        except ValueError:
            print('Error')
            return

        ro_init, h_init, is_fixed_ro, is_fixed_h = tuple(self.mesh_data.values())

        profile_label = self.ui.profileComboBox.currentText()

        self.parent.show_statusbar_msg('Расчет инверсии', 0)
        QtWidgets.qApp.processEvents()

        if profile_label:
            profile = list(filter(lambda pr: pr.tree_label == profile_label, self.tree.profiles))[0]
            edi_label = self.ui.ediComboBox.currentText()
            if edi_label:
                if edi_label == 'all':
                    n = len(profile.get_all_normalized_edi_files())

                    self.parent.show_statusbar_msg(f'Расчет продолжается... Расчитано 0 из {n} инверсий', 0)
                    QtWidgets.qApp.processEvents()

                    i = 0
                    for norm in profile.normalizations.values():
                        for edi_file in norm.result_edi_files:
                            inv = InversionModel(edi_file, ro_init, h_init, is_fixed_ro, is_fixed_h,
                                                 inversion_component,
                                                 n_iteration, min_res, max_res,
                                                 label=f'Inversion {len(self.tree.inversions) + 1}')
                            self.tree.add_inversion_model_to_normalized_profile(inv, profile, norm)
                            norm.add_inversion(inv)
                            i += 1

                            self.parent.show_statusbar_msg(f'Расчет продолжается... Раcчитано {i+1} из {n} инверсий', 0)
                            QtWidgets.qApp.processEvents()

                    self.parent.show_statusbar_msg(f'Расчет окончен', 2000)
                    QtWidgets.qApp.processEvents()
                else:
                    norm_id = int(edi_label.split('_')[1])
                    norm = profile.normalizations[norm_id]
                    edi_file = list(filter(lambda ed: ed.tree_label == edi_label, norm.result_edi_files))[0]
                    inv = InversionModel(edi_file, ro_init, h_init, is_fixed_ro, is_fixed_h, inversion_component,
                                         n_iteration, min_res, max_res,
                                         label=f'Inversion {len(self.tree.inversions) + 1}')
                    self.tree.add_inversion_model_to_normalized_profile(inv, profile, norm)
                    norm.add_inversion(inv)

                    self.parent.show_statusbar_msg(f'Расчет окончен', 2000)
                    QtWidgets.qApp.processEvents()
            else:
                self.parent.show_statusbar_msg('Ошибка - не выбран файл edi', 2000)
                QtWidgets.qApp.processEvents()
        else:
            edi_label = self.ui.ediComboBox.currentText()
            if edi_label:
                self.parent.show_statusbar_msg(f'Расчет инверсии...', 0)
                QtWidgets.qApp.processEvents()

                edi_file = list(filter(lambda ed: ed.tree_label == edi_label, self.tree.edi_files))[0]
                inv = InversionModel(edi_file, ro_init, h_init, is_fixed_ro, is_fixed_h, inversion_component,
                                     n_iteration, min_res, max_res,
                                     label=f'Inversion {len(self.tree.inversions) + 1}')
                self.tree.add_inversion_model(inv)

                self.parent.show_statusbar_msg(f'Расчет окончен', 2000)
                QtWidgets.qApp.processEvents()
            else:
                self.parent.show_statusbar_msg('Ошибка - не выбран файл edi или профиль', 2000)
                QtWidgets.qApp.processEvents()

    # def do_inversion(self):
    #     mesh_data, inversion_component, n_iteration, min_res, max_res = self.inversion_1d_control.get_inversion_data()
    #     ro_init, h_init, is_fixed_ro, is_fixed_h = tuple(mesh_data.values())
    #     edi_files = self.tree.get_checked_edi_file_paths()
    #     if edi_files:
    #         edi_file = edi_files[0]
    #     else:
    #         return
    #     inv = InversionModel(edi_file, ro_init, h_init, is_fixed_ro, is_fixed_h, inversion_component, n_iteration, min_res, max_res, label=f'Inversion {len(self.tree.inversions)+1}')
    #     self.tree.add_inversion_model(inv)

    def update_profile_combobox(self):
        self.ui.profileComboBox.clear()
        items = ['']
        items.extend([x.tree_label for x in self.tree.profiles])
        self.ui.profileComboBox.addItems(items)
        QComboBox.showPopup(self.ui.profileComboBox)

    def update_save_profile_combobox(self):
        self.ui.saveProfComboBox.clear()
        items = ['']
        items.extend([x.tree_label for x in self.tree.profiles])
        self.ui.saveProfComboBox.addItems(items)
        QComboBox.showPopup(self.ui.saveProfComboBox)

    def update_normalization_combobox(self):
        self.ui.saveNormComboBox.clear()
        profile_label = self.ui.saveProfComboBox.currentText()
        self.ui.saveNormComboBox.addItem('')
        if profile_label:
            profile = list(filter(lambda pr: pr.tree_label == profile_label, self.tree.profiles))[0]
            for norm in profile.normalizations.values():
                self.ui.saveNormComboBox.addItem(f'{norm.tree_label}')
        QComboBox.showPopup(self.ui.saveNormComboBox)

    def update_inversion_combobox(self):
        self.ui.saveInvComboBox.clear()
        self.ui.saveInvComboBox.addItem('')
        self.ui.saveInvComboBox.addItem('all')
        profile_label = self.ui.saveProfComboBox.currentText()
        norm_label = self.ui.saveNormComboBox.currentText()

        if not profile_label:
            if not norm_label:
                self.ui.saveInvComboBox.addItems([x.tree_label for x in self.tree.inversions])
        else:
            profile = list(filter(lambda pr: pr.tree_label == profile_label, self.tree.profiles))[0]
            if not norm_label:
                for norm in profile.normalizations.values():
                    index = self.ui.saveInvComboBox.count()
                    self.ui.saveInvComboBox.insertSeparator(index)
                    self.ui.saveInvComboBox.addItems([x.tree_label for x in norm.inversions])
            else:
                norm_id = int(norm_label.split()[-1])
                norm = profile.normalizations[norm_id]
                self.ui.saveInvComboBox.addItems([x.tree_label for x in norm.inversions])
        QComboBox.showPopup(self.ui.saveInvComboBox)

    def update_edi_combobox(self):
        self.ui.ediComboBox.clear()
        profile_label = self.ui.profileComboBox.currentText()
        self.ui.ediComboBox.addItem('')
        if profile_label:
            profile = list(filter(lambda pr: pr.tree_label == profile_label, self.tree.profiles))[0]
            if profile.normalizations:
                self.ui.ediComboBox.addItem('all')
                for norm in profile.normalizations.values():
                    index = self.ui.ediComboBox.count()
                    self.ui.ediComboBox.insertSeparator(index)
                    print(norm.result_edi_files)
                    self.ui.ediComboBox.addItems([x.tree_label for x in norm.result_edi_files])
        else:
            self.ui.ediComboBox.addItems([x.tree_label for x in self.tree.edi_files])

        QComboBox.showPopup(self.ui.ediComboBox)

    def save_inversion(self):
        profile_label = self.ui.saveProfComboBox.currentText()
        norm_label = self.ui.saveNormComboBox.currentText()
        inv_label = self.ui.saveInvComboBox.currentText()

        inversions = []

        if not inv_label:
            self.parent.show_statusbar_msg(f'Не выбрана инверсия', 5000)
            qApp.processEvents()
            return

        if inv_label == 'all':
            if profile_label:
                profile = list(filter(lambda pr: pr.tree_label == profile_label, self.tree.profiles))[0]
                if norm_label:
                    norm_id = int(norm_label.split()[-1])
                    norm = profile.normalizations[norm_id]
                    inversions.extend(norm.inversions)
                else:
                    for norm in profile.normalizations.values():
                        inversions.extend(norm.inversions)
            else:
                inversions.extend(self.tree.inversions)
        else:
            inversions.extend(list(filter(lambda inv: inv.tree_label == inv_label, self.tree.inversions)))

        folder_path = choose_folder()
        if folder_path is None:
            self.parent.show_statusbar_msg(f'Не выбрана директория', 5000)
            qApp.processEvents()
            return

        self.parent.show_statusbar_msg(f'Сохранение файлов')
        qApp.processEvents()

        for inv in inversions:
            inv.save_inversion(folder_path)

        self.parent.show_statusbar_msg(f'Файлы сохранены', 5000)
        qApp.processEvents()
