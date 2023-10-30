from normalization.EDI import mtedi, normalize_rho
from ui.DataWidget import MTComponent

from models.ImportFileModels import EdiFileData


class NormalizationProfileModel:
    """
    Класс профиля

    Инициализация -> дается список объектов EdiFileData внутри это читается и сохраняется
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

    def add_edi(self, files: list[EdiFileData]):
        """
        Добавление файла Edi к профилю
        :param files:
        :return:
        """
        for edi_file in files:
            self.edi_files.append(edi_file)
            self.edis.append(edi_file.edi)

    def delete_normalization(self, norm_id):
        del self.normalizations[norm_id]

    def create_widget(self):
        self.data_widget = MTComponent(self, self.edis)

    def get_all_normalized_edi_files(self) -> [EdiFileData]:
        """
        Возвращает все Edi объекты для всех нормализаций
        :return: список EdiFileData
        """
        edi_files = []
        for norm in self.normalizations.values():
            edi_files.extend(norm.result_edi_files)
        return edi_files


class Normalization:
    """
    Класс нормализации профиля
    """
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
        self.period_index = None

        self.result_edis = None
        self.result_edi_files = []

        self.data_widget = None

        self.inversions = []

        self.normalize()

    def normalize(self):
        periods = self.edis[0].Z.res_xy
        if periods[0] >= self.period:
            self.period_index = 0
        elif periods[-1] <= self.period:
            self.period_index = len(periods) - 1
        else:
            self.period_index = 0
            for i, x in enumerate(periods):
                if x <= self.period:
                    self.period_index = i
                else:
                    break

        self.result_edis = normalize_rho(self.edis, self.period_index, self.mt_points)
        norm_id = self.tree_label.split()[-1]

        for i, edi in enumerate(self.result_edis):
            edi_file_data = EdiFileData()
            edi_file_data.edi = edi
            edi_file_data.tree_label = f'norm_{norm_id}_{self.edi_files[i].tree_label}'
            edi_file_data.file_path = self.edi_files[i].file_path
            self.result_edi_files.append(edi_file_data)

        self.data_widget = MTComponent(self, self.result_edis)

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
