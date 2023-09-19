import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QTreeWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from ui.base_ui.TreeWidget import Ui_Form

from models.normalization_models import NormalizationProfileModel, Normalization
from models.inversionModel import InversionModel
from handlers.supportDialogs import choose_folder


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
                                'Invertions': QTreeWidgetItem([f'Invertions'])}

        # словарь файлов .EDI вида {filepath: QTreeWidgetItem}
        self.edi_files = {}

        # словарь файлов .txt вида {filepath: QTreeWidgetItem}
        self.txt_files = {}

        # словарь созданных профилей вида {NormalizationProfileModel: QTreeWidgetItem}
        self.profiles = {}

        # словарь инверсий {InversionModel: QTreeWidgetItem}
        self.invertions = {}

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
        model.normalizations[norm_id].save_results(dir_path)

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
            child = QTreeWidgetItem([f'{os.path.basename(path)}'])
            child.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.edi_files[path] = child
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
            child = QTreeWidgetItem([f'{os.path.basename(path)}'])
            child.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.txt_files[path] = child
            parent_item.addChild(child)

        parent_item.setExpanded(True)
    # end def add_edi_file

    def create_profile(self):
        paths = self.get_checked_edi_file_paths()
        self.clear_selection()
        self.add_normalization_profile(NormalizationProfileModel(paths))

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

        profile_item = QTreeWidgetItem([f'Profile {len(self.profiles) + 1}'])
        self.profiles[profile_model] = profile_item
        parent_item.addChild(profile_item)

        data_item = QTreeWidgetItem([f'Data'])
        profile_item.addChild(data_item)
        for path in profile_model.file_paths:
            data_item.addChild(QTreeWidgetItem([f'{os.path.basename(path)}']))

        for i, norm in profile_model.normalizations.items():
            self.parent.add_widget(norm.data_widget)
            norm = QTreeWidgetItem([f'Normalization {i}'])
            profile_item.addChild(norm)

        self.parent.show_widget(profile_model.data_widget)

    def add_inversion_model(self, invertion: InversionModel):
        parent_item = self.top_level_items['Invertions']

        profile_item = QTreeWidgetItem([f'Invertion {len(self.invertions) + 1}'])
        self.profiles[invertion] = profile_item
        parent_item.addChild(profile_item)

        self.parent.show_widget(invertion.data_widget)


    def add_normalization_to_profile(self, profile: NormalizationProfileModel, norma: Normalization):
        prof = self.profiles[profile]
        norm = QTreeWidgetItem([f'Normalization {len(profile.normalizations)}'])
        prof.addChild(norm)
        self.parent.show_widget(norma.data_widget)

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

    def remove_normalization_model(self):
        profile_model = self.get_selected_normalization_model()
        norm_item = self.ui.projectTreeWidget.currentItem()
        profile_item = norm_item.parent()
        norm_id = int(norm_item.text(0).split()[1])

        if profile_model:
            profile_item.removeChild(norm_item)
            widgets = [profile_model.normalizations[norm_id].data_widget]
            self.parent.remove_widgets(widgets)

    def find_model_by_widget(self, widget):
        for profile in self.profiles.keys():
            if profile.data_widget == widget:
                return profile
            for norm in profile.normalizations.values():
                if norm.data_widget == widget:
                    return norm
        return None
