import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QTreeWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from ui.base_ui.TreeWidget import Ui_Form

from models.NormalizationModel import NormalizationProfileModel, Normalization
from models.InversionModel import InversionModel
from handlers.supportDialogs import choose_folder

from models.ImportFileModels import EdiFileData, FrequencyMT1DFileData


class TreeWidget(QWidget):
    def __init__(self, parent=None):
        super(TreeWidget, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.parent = parent

        self.files_popMenu = QMenu()
        self.init_popMenu_for_files()
        self.profiles_popMenu = QMenu()
        self.init_popMenu_for_profiles()
        self.normalization_popMenu = QMenu()
        self.init_popMenu_for_normalizations()

        self.top_level_items = {'EDI files': QTreeWidgetItem([f'EDI files']),
                                'TXT files': QTreeWidgetItem([f'TXT files']),
                                'Profiles': QTreeWidgetItem([f'Profiles']),
                                'Inversions': QTreeWidgetItem([f'Inversions']),
                                'MTD': QTreeWidgetItem([f'MTD'])}

        # словарь файлов .EDI вида {FileData: QTreeWidgetItem}
        self.edi_files = {}

        # словарь файлов .txt вида {FileData: QTreeWidgetItem}
        self.txt_files = {}

        # словарь созданных профилей вида {NormalizationProfileModel: QTreeWidgetItem}
        self.profiles = {}
        self.profile_id = 1

        # словарь инверсий {InversionModel: QTreeWidgetItem}
        self.inversions = {}

        # словарь моделей mtd {[GridModel, SimpleModel]: QTreeWidgetItem}
        self.mtd_models = {}

        # словарь частот для моделей мтд {FreqData: QTreeWidgetItem}
        self.mtd_freq = {}

        self.ui.projectTreeWidget.setHeaderLabel('Дерево проекта')
        self.ui.projectTreeWidget.setSelectionMode(QAbstractItemView.MultiSelection)

        for item in self.top_level_items.values():
            self.ui.projectTreeWidget.addTopLevelItem(item)
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)

        self.ui.projectTreeWidget.itemClicked.connect(self.tree_item_clicked)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_popMenu)
    # end def __init__

    def init_popMenu_for_profiles(self):
        showProfileAction = QAction('Show profile', self)
        showProfileAction.triggered.connect(self.show_profile)
        self.profiles_popMenu.addAction(showProfileAction)

        deleteProfileAction = QAction('Delete profile', self)
        deleteProfileAction.triggered.connect(self.remove_profile_model)
        self.profiles_popMenu.addAction(deleteProfileAction)
    # end def init_popMenu_for_profiles

    def init_popMenu_for_normalizations(self):
        saveNormalizationAction = QAction('Save normalization', self)
        saveNormalizationAction.triggered.connect(self.save_normalization)
        self.normalization_popMenu.addAction(saveNormalizationAction)

        showNormalizationAction = QAction('Show normalization', self)
        showNormalizationAction.triggered.connect(self.show_normalization)
        self.normalization_popMenu.addAction(showNormalizationAction)

        deleteNormalizationAction = QAction('Delete normalization', self)
        deleteNormalizationAction.triggered.connect(self.remove_normalization_model)
        self.normalization_popMenu.addAction(deleteNormalizationAction)

    def init_popMenu_for_files(self):
        createProfileAction = QAction('Create profile', self)
        createProfileAction.triggered.connect(self.create_profile)
        self.files_popMenu.addAction(createProfileAction)
    # end def init_popMenu_for_files

    def show_popMenu(self):
        item = self.ui.projectTreeWidget.currentItem()
        if item.parent() == self.top_level_items['EDI files']:
            cursor = QCursor()
            self.files_popMenu.popup(cursor.pos())
        elif 'Normalization' in item.text(0):
            cursor = QCursor()
            self.normalization_popMenu.popup(cursor.pos())
        elif item.parent() == self.top_level_items['Profiles']:
            cursor = QCursor()
            self.profiles_popMenu.popup(cursor.pos())

    def save_normalization(self):
        item = self.ui.projectTreeWidget.currentItem()
        if item is None:
            return
        parent_item = item
        while parent_item not in self.profiles.values():
            parent_item = parent_item.parent()

        model = list(self.profiles.keys())[list(self.profiles.values()).index(parent_item)]
        dir_path = choose_folder()

        if dir_path is None:
            return

        norm_id = int(item.text(0).split(' ')[1])
        model.normalizations[norm_id].export_edi(dir_path)

    def show_normalization(self, item=None):
        if item is None:
            item = self.ui.projectTreeWidget.currentItem()
        norm_id = int(item.text(0).split()[1])
        profile_item = None
        for i, prof in self.profiles.items():
            if item.parent() == prof:
                profile_item = i
                break
        if profile_item is None:
            return

        self.parent.show_widget(profile_item.normalizations[norm_id].data_widget)

    def show_profile(self, item=None):
        if item is None:
            item = self.ui.projectTreeWidget.currentItem()
        profile_item = None
        for i, prof in self.profiles.items():
            if item == prof:
                profile_item = i
                break
        if profile_item is None:
            return

        self.parent.show_widget(profile_item.data_widget)

    def show_inversion(self, item=None):
        if item is None:
            item = self.ui.projectTreeWidget.currentItem()
        inv_item = None
        for i, inv in self.inversions.items():
            if item == inv:
                inv_item = i
                break
        if inv_item is None:
            return

        self.parent.show_widget(inv_item.data_widget)

    def tree_item_clicked(self):
        current_item = self.ui.projectTreeWidget.currentItem()
        print(current_item.text(0))
        if current_item.parent() != self.top_level_items['EDI files']:
            self.ui.projectTreeWidget.clearSelection()
            current_item.setSelected(True)
            if 'Profile' in current_item.text(0):
                self.show_profile(current_item)
            elif 'Normalization' in current_item.text(0):
                self.show_normalization(current_item)
            elif 'Data' in current_item.text(0):
                self.show_profile(current_item.parent())
            elif 'Inversion' in current_item.text(0):
                self.show_inversion(current_item)
        else:
            for item in self.ui.projectTreeWidget.selectedItems():
                if item.parent() != self.top_level_items['EDI files']:
                    self.ui.projectTreeWidget.clearSelection()
                    current_item.setSelected(True)
                    break

    # end def tree_item_clicked

    def add_edi_file(self, file_paths: list[str]):
        """
        Добавляет в дерево проекта файлы данных с расширением .EDI

        :param file_paths: Список путей к файлу
        """
        parent_item = self.top_level_items['EDI files']

        for path in file_paths:
            edi_file = EdiFileData(path)
            child = QTreeWidgetItem([edi_file.tree_label])
            child.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.edi_files[edi_file] = child
            parent_item.addChild(child)

        parent_item.setExpanded(True)

    # end def add_edi_file

    def add_txt_file(self, file_paths: list[str]):
        """
        Добавляет в дерево проекта файлы данных с расширением .txt

        :param file_paths: Список путей к файлу
        """
        parent_item = self.top_level_items['TXT files']

        for path in file_paths:
            txt_file = FrequencyMT1DFileData(path)
            child = QTreeWidgetItem([txt_file.tree_label])
            child.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.txt_files[txt_file] = child
            parent_item.addChild(child)

        parent_item.setExpanded(True)

    # end def add_edi_file

    def create_profile(self):
        paths = self.get_checked_edi_file_paths()
        self.clear_selection()
        self.add_normalization_profile(NormalizationProfileModel(paths, label=f'Profile {self.profile_id}'))
        self.profile_id += 1

    # end def create_profile

    def add_normalization_profile(self, profile_model: NormalizationProfileModel):
        """
        Функция добавляет в дерево проекта профиль с данными.

        :param profile_model: Класс модели профиля
        """
        parent_item = self.top_level_items['Profiles']
        if not len(self.profiles):
            self.ui.projectTreeWidget.addTopLevelItem(parent_item)
            parent_item.setExpanded(True)

        profile_item = QTreeWidgetItem([profile_model.tree_label])
        self.profiles[profile_model] = profile_item
        parent_item.addChild(profile_item)

        data_item = QTreeWidgetItem([f'Data'])
        profile_item.addChild(data_item)
        for edi_file in profile_model.edi_files:
            data_item.addChild(QTreeWidgetItem([edi_file.tree_label]))

        for norm in profile_model.normalizations.values():
            self.parent.add_widget(norm.data_widget)
            norm = QTreeWidgetItem([norm.tree_label])
            profile_item.addChild(norm)

        self.parent.show_widget(profile_model.data_widget)

    def add_inversion_model(self, inversion: InversionModel):
        parent_item = self.top_level_items['Inversions']

        profile_item = QTreeWidgetItem([inversion.tree_label])
        self.inversions[inversion] = profile_item
        parent_item.addChild(profile_item)
        parent_item.setExpanded(True)

        self.parent.show_widget(inversion.data_widget)

    def add_inversion_model_to_normalized_profile(self,
                                                  inversion: InversionModel = None,
                                                  profile: NormalizationProfileModel = None,
                                                  norma: Normalization = None,
                                                  edi_file: EdiFileData = None):
        parent_item = self.profiles[profile]
        profile_children = [parent_item.child(x) for x in range(parent_item.childCount())]
        norma_item = list(filter(lambda child: child.text(0) == norma.tree_label, profile_children))[0]
        print(norma_item.text(0))
        inv_item = QTreeWidgetItem([inversion.tree_label])
        self.inversions[inversion] = inv_item
        norma_item.addChild(inv_item)
        norma_item.setExpanded(True)

        self.parent.show_widget(inversion.data_widget)

    def add_normalization_to_profile(self, profile: NormalizationProfileModel, norma: Normalization):
        prof = self.profiles[profile]
        norm = QTreeWidgetItem([norma.tree_label])
        prof.addChild(norm)
        self.parent.show_widget(norma.data_widget)

    def add_mtd_model(self, mtd_model):
        if mtd_model.file_path is None:
            child = QTreeWidgetItem([mtd_model.tree_label])
        else:
            child = QTreeWidgetItem([os.path.basename(mtd_model.file_path)])
        child.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self.mtd_models[mtd_model] = child
        parent_item = self.top_level_items['MTD']

        parent_item.addChild(child)
        parent_item.setExpanded(True)

    # end def add_mtd_model

    def add_point_to_mtd_model(self, point, mtd_model):
        child = QTreeWidgetItem([point.tree_label])
        self.top_level_items['MTD'].child(self.mtd_models[mtd_model]).addChild(child)

    # end def add_point_to_mtd_model

    def get_checked_edi_file_paths(self) -> list:
        """
        Возвращает список путей выбранных файлов

        :return: List с путями к файлам
        """
        paths = []
        items = self.ui.projectTreeWidget.selectedItems()
        if len(items):
            for item in items:
                paths.append(list(self.edi_files.keys())[list(self.edi_files.values()).index(item)])
            self.clear_selection()
            return paths

    def get_selected_normalization_model(self) -> [NormalizationProfileModel | None]:
        """
        Возвращает выбранный профиль нормализации. Если профиль не выбран возвращает None

        :return: Профиль нормализации
        """
        item = self.ui.projectTreeWidget.currentItem()

        while item.parent() and item.parent() != self.top_level_items['Profiles']:
            item = item.parent()

        if 'Profile' in item.text(0).split():
            return list(self.profiles.keys())[list(self.profiles.values()).index(item)]
        return None

    def get_selected_inversion_model(self) -> [InversionModel | None]:
        """
        Возвращает выбранную модель инверсии. Если модель не выбрана, возвращает None

        :return: Модель инверсии
        """
        item = self.ui.projectTreeWidget.currentItem()

        while item.parent() and item.parent() != self.top_level_items['Inversions']:
            item = item.parent()

        if 'Inversion' in item.text(0).split():
            return list(self.inversions.keys())[list(self.inversions.values()).index(item)]
        return None

    def clear_selection(self):
        """
        Очищает выделение файлов.
        """
        self.ui.projectTreeWidget.clearSelection()

    def get_current_normalization(self) -> [Normalization | None]:
        item = self.ui.projectTreeWidget.currentItem()
        norm_id = int(item.text(0).split()[1])
        profile_item = None
        for i, prof in self.profiles.items():
            if item.parent() == prof:
                profile_item = i
                return profile_item.normalizations[norm_id]
        if profile_item is None:
            return None

    def remove_profile_model(self):
        profile_model = self.get_selected_normalization_model()
        item = self.ui.projectTreeWidget.currentItem()
        if profile_model:
            self.top_level_items['Profiles'].removeChild(item)

            widgets = [profile_model.data_widget]
            for norm in profile_model.normalizations.values():
                widgets.append(norm.data_widget)
            self.parent.remove_widgets(widgets)
        del self.profiles[profile_model]

    def remove_normalization_model(self):
        profile_model = self.get_selected_normalization_model()
        norm_item = self.ui.projectTreeWidget.currentItem()
        profile_item = norm_item.parent()
        norm_id = int(norm_item.text(0).split()[1])

        if profile_model:
            profile_item.removeChild(norm_item)
            widgets = [profile_model.normalizations[norm_id].data_widget]
            self.parent.remove_widgets(widgets)

        profile_model.delete_normalization(norm_id)

    def find_model_by_widget(self, widget):
        # if isinstance()
        for profile in self.profiles.keys():
            if profile.data_widget == widget:
                return profile
            for norm in profile.normalizations.values():
                if norm.data_widget == widget:
                    return norm
        return None
