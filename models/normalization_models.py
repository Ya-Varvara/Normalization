import os

from normalization.EDI import read_edi_files, mtedi, normalize_rho
from ui.DataWidget import MTComponent


class NormalizationProfileModel:
    """
    Класс профиля

    Инициализация -> дается список путей к файлам EDI, внутри это читается и сохраняется
    """

    def __init__(self, file_paths: list[str]):
        self.file_paths = file_paths
        self.edis = read_edi_files(self.file_paths)

        self.normalizations = {}
        self.data_widget = None
        self.create_widget()

    def add_normalization(self, period, mt_points):
        if len(self.normalizations):
            norm_id = list(self.normalizations.keys())[-1] + 1
        else:
            norm_id = 1
        norm = Normalization(self.edis, mt_points, period, file_paths=self.file_paths)
        self.normalizations[norm_id] = norm

        return norm

    def add_edi(self, file_path: list[str]):
        self.file_paths.extend(file_path)
        self.edis.extend(read_edi_files(file_path))

    def delete_edi(self, file_name):
        for file in self.file_paths:
            if file_name == os.path.basename(file):
                self.file_paths.remove(file)
                break

    def delete_normalization(self, norm_id):
        del self.normalizations[norm_id]

    def create_widget(self):
        self.data_widget = MTComponent(self, self.edis)


class Normalization:
    def __init__(self, edis: list[mtedi.Edi], mt_points: int, period: float, file_paths: list = None):
        self.edis = edis
        self.mt_points = mt_points
        self.period = period

        self.result_edis = None
        self.data_widget = None
        self.file_paths = file_paths

        periods = self.edis[0].Z.res_xy
        if periods[0] >= period:
            self.period_index = 0
        elif periods[-1] <= period:
            self.period_index = len(periods) - 1
        else:
            self.period_index = 0
            for i, x in enumerate(periods):
                if x <= period:
                    self.period_index = i
                else:
                    break
        self.normalize()

    def normalize(self):
        self.result_edis = normalize_rho(self.edis, self.period_index, self.mt_points)
        self.data_widget = MTComponent(self, self.result_edis)
        print(self.edis)
        print(self.result_edis)
        return self.result_edis

    def save_results(self, dir_path):
        names = [os.path.splitext(os.path.basename(i))[0] for i in self.file_paths]
        if self.result_edis is None:
            self.normalize()
        for i, edi in enumerate(self.result_edis):
            edi.write_edi_file(f'{dir_path}/{names[i]}.edi')

    def return_parameters(self):
        return self.edis, self.mt_points, self.period
