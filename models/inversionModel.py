from inversion.inversion import fit_1d_model


class InversionModel:
    def __init__(self, ro_init, h_init, is_fixed_ro, is_fixed_h, Z, t_list, N_iter = 10, method='CG',
                             min_res=0.1, max_res=10000):
        self.data_widget = None
        self.ro_init = ro_init
        self.h_init = h_init
        self.is_fixed_ro = is_fixed_ro
        self.is_fixed_h = is_fixed_h
        self.Z_obs = Z
        self.t_list = t_list
        self.N_iter = N_iter
        self.method = method
        self.min_res = min_res
        self.max_res = max_res

        self.ro_out, self.h_out = fit_1d_model(ro_init, h_init, is_fixed_ro, is_fixed_h, Z, t_list, N_iter = 10, method='CG',
                             min_res=0.1, max_res=10000)
