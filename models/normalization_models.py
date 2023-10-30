import os

from normalization.EDI import read_edi_files, mtedi, normalize_rho
from ui.DataWidget import MTComponent

from models.ediFileClass import EdiFileData


class NormalizationProfileModel:
    """
    Класс профиля

    Инициализация -> дается список путей к файлам EDI, внутри это читается и сохраняется
    """

    def __init__(self, edi_files: list[EdiFileData], label=None):
        self.edi_files = edi_files
        self.edis = [x.edi for x in edi_files]

        self.normalizations = {}
        self.norm_id = 1
        self.data_widget = None
        self.tree_label = label
        self.create_widget()

    def add_normalization(self, period, mt_points):
        norm = Normalization(self.edis, mt_points, period, edi_files=self.edi_files, label=f'Normalization {self.norm_id}')
        self.normalizations[self.norm_id] = norm
        self.norm_id += 1
        return norm

    def add_edi(self, file_path: list[str]):
        for path in file_path:
            edi_file = EdiFileData(path)
            self.edi_files.append(edi_file)
            self.edis.append(edi_file.edi)

    # def delete_edi(self, file_name):
    #     for file in self.file_paths:
    #         if file_name == os.path.basename(file):
    #             self.file_paths.remove(file)
    #             break

    def delete_normalization(self, norm_id):
        del self.normalizations[norm_id]

    def create_widget(self):
        self.data_widget = MTComponent(self, self.edis)

    def get_all_normalized_edi_files(self):
        edi_files = []
        for norm in self.normalizations.values():
            edi_files.extend(norm.result_edi_files)
        return edi_files


class Normalization:
    def __init__(self,
                 edis: list[mtedi.Edi],
                 mt_points: int,
                 period: float,
                 edi_files: list[EdiFileData] = None,
                 label: str = None):
        self.edis = edis
        self.mt_points = mt_points
        self.period = period
        self.edi_files = edi_files
        self.tree_label = label

        self.inversions = []

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

        self.result_edis = normalize_rho(self.edis, self.period_index, self.mt_points)
        label = self.tree_label.split()[-1]
        self.result_edi_files = []
        for i, edi in enumerate(self.result_edis):
            edi_file_data = EdiFileData()
            edi_file_data.edi = edi
            edi_file_data.tree_label = f'norm_{label}_{self.edi_files[i].tree_label}'
            edi_file_data.file_path = self.edi_files[i].file_path
            self.result_edi_files.append(edi_file_data)
        self.data_widget = MTComponent(self, self.result_edis)

    # def save_results(self, dir_path):
    #     for i, edi_file in enumerate(self.result_edi_files):
    #         edi_file.edi.write_edi_file(f'{dir_path}/{edi_file.tree_label}.edi')

    def add_inversion(self, inv):
        self.inversions.append(inv)

    def export_edi(self, target_folder_path, edi_label):
        exp_edis = []
        if edi_label == 'all':
            exp_edis = self.result_edi_files
        else:
            exp_edis.append(list(filter(lambda ef: ef.tree_label == edi_label, self.result_edi_files))[0])

        for edi_file in exp_edis:
            target_file_path = f'{target_folder_path}/{edi_file.tree_label}.edi'
            source_file_path = edi_file.file_path
            edi_file.edi.write_edi_file(target_file_path)


            with open(source_file_path, 'r') as source_file:
                source_lines = source_file.readlines()[:15]

            with open(target_file_path, 'r') as target_file:
                target_lines = target_file.readlines()

            with open(target_file_path, 'w') as output_file:
                output_file.writelines(source_lines + target_lines[20:])

    def return_parameters(self):
        return self.edis, self.mt_points, self.period
