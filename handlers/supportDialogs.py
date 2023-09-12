from PyQt5.QtWidgets import QFileDialog


def open_file_dialog(file_filter='EDI (*.edi);; txt (*.txt)'):
    """
    Открывает окно для выбора файлов в файловой системе

    :return: Список путей к файлам или None, в случае закрытия окна
    """
    response = QFileDialog.getOpenFileNames(
        caption='Открыть файл',
        filter=file_filter,
        initialFilter='EDI (*.edi)'
    )
    if response[0]:
        return response[0]
    else:
        return None


def save_file_dialog(file_filter=None):
    if file_filter is None:
        file_filter = 'Text File (*.txt)'
    response = QFileDialog.getSaveFileName(
        caption='Сохранить файл',
        filter=file_filter,
        initialFilter=file_filter,
        directory='data_file.txt'
    )
    if response[0]:
        return response[0]
    else:
        return None


def choose_folder():
    response = QFileDialog.getExistingDirectory(
        caption='Выбор директории',
        # filter=file_filter,
        # initialFilter=file_filter,
        # directory='data_file.txt'
    )
    if response:
        return response
    else:
        return None
