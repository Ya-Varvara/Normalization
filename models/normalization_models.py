import os

from normalization.EDI import read_edi_files, mtedi, normalize_rho


class NormalizationProfileModel:
    """
    Класс профиля

    Инициализация -> дается список путей к файлам EDI, внутри это читается и сохраняется
    """
    def __init__(self, file_paths: list[str]):
        self.file_paths = file_paths
        self.edis = read_edi_files(self.file_paths)

        self.normalizations = {}

    def add_normalization(self, period, mt_points):
        if len(self.normalizations):
            norm_id = list(self.normalizations.keys())[-1] + 1
        else:
            norm_id = 1
        norm = Normalization(self.edis, mt_points, period)
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

class Normalization:
    def __init__(self, edis: list[mtedi.Edi], mt_points: int, period: float):
        self.edis = edis
        self.mt_points = mt_points
        self.period = period

        self.result_edis = None

        periods = self.edis[0].Z.res_xy
        if periods[0] >= period:
            self.period_index = 0
        elif periods[-1] <= period:
            self.period_index = len(periods)-1
        else:
            self.period_index = 0
            for i, x in enumerate(periods):
                if x <= period:
                    self.period_index = i
                else:
                    break

    def normalize(self):
        self.result_edis = normalize_rho(self.edis, self.period_index, self.mt_points)
        return self.result_edis

    def save_results(self, dir_path):
        if self.result_edis is None:
            self.normalize()
        for i, edi in enumerate(self.result_edis):
            edi.write_edi_file(f'{dir_path}/{i+1}.edi')

    def return_parameters(self):
        return self.edis, self.mt_points, self.period
