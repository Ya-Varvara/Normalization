from inversion.inversion import fit_1d_model, get_z_from_edi, forward_1D_MT, calc_phase, export_z_rho
from normalization.EDI import mtedi
from ui.InvertionWidget import InversionWidget

from sklearn.metrics import mean_absolute_percentage_error as mape 
from numpy import log, abs, real, imag


class InversionModel:
    def __init__(self,
                 edi_file, ro_init, h_init,
                 is_fixed_ro, is_fixed_h, component,
                 N_iter = 10,
                 min_res=0.1,
                 max_res=10000,
                 label=None):
        self.edi_file = edi_file

        self.edi = self.edi_file.edi
        self.tree_label = label
        # print(self.edi)

        self.ro_init = ro_init
        self.h_init = h_init
        self.is_fixed_ro = is_fixed_ro
        self.is_fixed_h = is_fixed_h
        self.component = component
        self.N_iter = N_iter
        self.min_res = min_res
        self.max_res = max_res

        self.t_list, self.Z = get_z_from_edi(self.edi, self.component)

        self.ro_out, self.h_out = fit_1d_model(ro_init, h_init, is_fixed_ro, is_fixed_h, self.Z, self.t_list,
                                               self.N_iter, method='CG', min_res=self.min_res, max_res=self.max_res)
        self.Z_inv = forward_1D_MT(self.ro_out, self.h_out, self.t_list)
        
        # self.Z_error = mape(log(abs(self.Z)), log(abs(self.Z_inv))) * 100
        # self.Z_Re_error = mape(log(real(self.Z)), log(real(self.Z_inv))) * 100
        # self.Z_Im_error = mape(log(-imag(self.Z)), log(-imag(self.Z_inv))) * 100

        self.Z_error = 1
        self.Z_Re_error = 2
        self.Z_Im_error = 3

        self.data_widget = InversionWidget(self)

    def save_inversion(self, folder_path):
        file_path = f'{folder_path}/{self.tree_label}'
        export_z_rho(self.h_out[:-1], self.ro_out, file_path)

