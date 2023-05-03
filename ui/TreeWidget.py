import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QTreeWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from ui.base_ui.TreeWidget import Ui_Form

from normalization.EDI import NormalizationProfileModel
from handlers.supportDialogs import save_file_dialog, open_file_dialog, choose_folder

class TreeWidget(QWidget):
    def __init__(self, parent=None):
        super(TreeWidget, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.parent = parent

        self.popMenu = QMenu()
        self.init_popMenu()

        self.files = {}
        self.profiles = {}

        self.ui.projectTreeWidget.setHeaderLabel('Дерево проекта')
        self.ui.projectTreeWidget.setSelectionMode(QAbstractItemView.MultiSelection)

        self.ui.projectTreeWidget.itemClicked.connect(self.tree_item_clicked)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_popMenu)
    # end def __init__

    def init_popMenu(self):
        showModelAction = QAction('Save normalization', self)
        showModelAction.triggered.connect(self.save_normalization)
        self.popMenu.addAction(showModelAction)
    # end def init_popMenu

    def show_popMenu(self):
        item = self.ui.projectTreeWidget.currentItem()
        if item in self.files.values():
            return
        cursor = QCursor()
        self.popMenu.popup(cursor.pos())

    def save_normalization(self):
        item = self.ui.projectTreeWidget.currentItem()
        while item not in self.profiles.values():
            item = item.parent()

        model = list(self.profiles.keys())[list(self.profiles.values()).index(item)]
        dir_path = choose_folder()
        model.save_results(dir_path)

    def tree_item_clicked(self):
        def has_different_types():
            for i in self.ui.projectTreeWidget.selectedItems():
                if i not in self.files.values():
                    return True
            return False

        item = self.ui.projectTreeWidget.currentItem()
        if item not in self.files.values() or has_different_types():
            self.ui.projectTreeWidget.clearSelection()
            item.setSelected(True)
        print(item.text(0))
    # end def tree_item_clicked

    def add_edi_file(self, file_paths: list):
        """
        Добавляет в дерево проекта файлы данных с расширением .EDI

        :param file_paths: Список путей к файлу
        """
        for path in file_paths:
            child = QTreeWidgetItem([f'{os.path.basename(path)}'])
            child.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.files[path] = child
            self.ui.projectTreeWidget.addTopLevelItem(child)
    # end def add_edi_file

    def add_normalization_profile(self, profile_model: NormalizationProfileModel):
        """
        Функция добавляет в дерево проекта профиль с данными.

        :param profile_model: Класс модели профиля
        """
        item = QTreeWidgetItem([f'Profile {len(self.profiles)+1}'])
        self.profiles[profile_model] = item
        self.ui.projectTreeWidget.addTopLevelItem(item)

        data_item = QTreeWidgetItem([f'Data'])
        self.profiles[profile_model].addChild(data_item)
        for path in profile_model.file_paths:
            data_item.addChild(QTreeWidgetItem([f'{os.path.basename(path)}']))
        self.profiles[profile_model].addChild(QTreeWidgetItem([f'Normalization 1']))

    def get_checked_edi_file_paths(self):
        """
        Возвращает список путей выбранных файлов. Если ничего не выбрано, возвращает все файлы

        :return: List с путями к файлам
        """
        paths = []
        for item in self.ui.projectTreeWidget.selectedItems():
            paths.append(list(self.files.keys())[list(self.files.values()).index(item)])

        if paths:
            return paths
        else:
            return list(self.files.keys())

    def clear_selection(self):
        """
        Очищает выделение файлов.
        """
        self.ui.projectTreeWidget.clearSelection()

