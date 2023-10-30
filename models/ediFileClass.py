import os
from normalization.EDI import read_edi_files


class FileData:
    def __init__(self, file_path=None, data=None):
        self.file_path = file_path
        if file_path:
            self.tree_label = f'{os.path.basename(file_path)}'
        else:
            self.tree_label = None
        self.data = data


class EdiFileData(FileData):
    def __init__(self, file_path=None, data=None):
        super(EdiFileData, self).__init__(file_path, data)
        if file_path:
            self.edi = read_edi_files([self.file_path])[0]
        else:
            self.edi = None


class FrequencyMT1DFileData(FileData):
    def __init__(self, file_path=None, data=None):
        super(FrequencyMT1DFileData, self).__init__(file_path, data)


