import numpy as np
from numpy import pi
import matplotlib.pyplot as plt
import pandas as pd

from scipy.optimize import minimize
from scipy.optimize import basinhopping
from scipy.optimize import dual_annealing
import mtpy.core.edi as mtedi

mu0 = 4 * np.pi * 1e-7


def calc_effective_Z(z):
    return np.sqrt(z[:, 0, 0] * z[:, 1, 1] - z[:, 1, 0] * z[:, 0, 1])


def forward_1D_MT(rho, h, t):
    '''
    Функция для решения 1D прямой задачи МТЗ.
    На вход принимает массив сопротивлений слоев и их мощностей (мощностей должно быть на одну меньше, чем сопротивлений),
    а также периодов.
    На выходе возвращает массив комплексных значений импеданса
    '''

    w = 2 * np.pi / t  # круговая частота
    R = np.ones(len(t))

    mu0 = 4 * np.pi * 1e-7

    for m in range(len(h)-1, 0, -1):
        k = np.sqrt(-1j * w * mu0 / rho[m - 1])

        A = np.sqrt(rho[m - 1] / rho[m])
        B = np.exp(-2 * k * h[m - 1]) * (R - A) / (R + A)
        R = (1 + B) / (1 - B)

    k0 = np.sqrt(-1j * w * mu0 / rho[0])

    return -1j * w * mu0 * R / k0


def calc_app_rho(Z, w_list):
    '''
    Функция, вычисляющая кажущееся сопротивления по значениям импеданса и соответствующих круговых частот
    '''

    return np.abs(Z) ** 2 / 2 / np.pi / w_list / mu0


def calc_phase(Z):
    '''
    Функция, вычисляющая фазу по комплексным значениям импеданса
    '''

    return np.arctan2(np.imag(Z), np.real(Z)) * 180 / np.pi


def plot_rho(h, rho, max_depth=None):
    '''
    Функция, предназначенная для визуализации 1D разреза сопротивлений.
    На вход принимает мощности слоев и их сопротивления (мощностей, как всегда, на одну меньше, чем сопротивлений)
    На выходе рисует график, на котором по горизонтали откладывается глубина, а по вертикали сопротивления
    '''

    hp = np.zeros(len(rho) * 2)
    rhop = np.zeros(len(rho) * 2)

    hp[1:-1:2] = np.cumsum(h)
    hp[-1] = np.sum(h) * 1.1 if max_depth is None else max_depth
    hp[2::2] = np.cumsum(h)

    rhop[::2] = rho
    rhop[1::2] = rho

    plt.loglog(hp, rhop, linewidth=3)
    plt.grid(True)
    plt.xlabel('H')
    plt.ylabel(r'$\rho$')

    plt.xlim([10 ** np.floor(np.log10(hp[1]) - 1), 10 ** np.ceil(np.log10(hp[-1]))])
    plt.ylim([10 ** np.floor(np.log10(np.min(rho))), 10 ** np.ceil(np.log10(np.max(rho)))])


def export_z_rho(h, rho, fname, max_depth=None):
    '''
    Функция, предназначенная для визуализации 1D разреза сопротивлений.
    На вход принимает мощности слоев и их сопротивления (мощностей, как всегда, на одну меньше, чем сопротивлений)
    На выходе рисует график, на котором по горизонтали откладывается глубина, а по вертикали сопротивления
    '''

    hp = np.zeros(len(rho) * 2)
    rhop = np.zeros(len(rho) * 2)

    hp[1:-1:2] = np.cumsum(h)
    hp[-1] = np.sum(h) * 1.1 if max_depth is None else max_depth
    hp[2::2] = np.cumsum(h)

    rhop[::2] = rho
    rhop[1::2] = rho

    out_data = np.empty([len(hp), 2])
    out_data[:, 0] = hp
    out_data[:, 1] = rhop

    np.savetxt(fname, out_data, comments='', delimiter='\t', header='z\trho')


def forward_rmse(section, is_fixed,
                 section_copy,
                 times, obs_Z):
    '''
    Вспомогательная функция для инверсии с помощью оптимизаторов из scipy.
    На вход принимает:
    - массив свойств разреза [сопротивление1, мощность1, сопротивление2, мощность2 ...],
    - массив с флагами фиксации того же размера. Если свойство фиксировано, то оно не будет меняться при
    подборе, если не фиксировано, то меняться будет.
    - копия массива свойств разреза (нужно для того, чтобы реализовать фиксацию, иначе scipy будет подбирать
    все без разбора)
    - периоды
    - наблюденные значения импеданса

    '''

    rho = section_copy[0::2]
    h = section_copy[1::2]

    for i, (r, fixed) in enumerate(zip(section[::2], is_fixed[::2])):
        if not fixed:
            rho[i] = r

    for i, (h_layer, fixed) in enumerate(zip(section[1::2], is_fixed[1::2])):
        if not fixed:
            h[i] = h_layer

    Z = forward_1D_MT(rho, h, times)

    delta_real = np.log(np.abs(np.real(obs_Z))) - np.log(np.abs(np.real(Z)))
    delta_imag = np.log(np.abs(np.imag(obs_Z))) - np.log(np.abs(np.imag(Z)))
    delta = (np.sum(delta_real ** 2) + np.sum(delta_imag ** 2)) / len(Z)
    # delta = np.sum((np.abs(Z) - np.abs(obs_Z)) ** 2)

    return delta


def get_z_from_edi(edi, component='eff'):
    z = []

    if component == 'eff':
        z = calc_effective_Z(edi.Z.z) * (mu0 * np.sqrt(1e6))
    elif component == 'xy':
        z = edi.Z.z[:, 0, 1] * (mu0 * np.sqrt(1e6))
    elif component == 'yx':
        z = edi.Z.z[:, 1, 0] * (mu0 * np.sqrt(1e6))

    if len(z):
        z = np.conjugate(z)
        t_list = 1 / edi.Z.freq

        t_list = t_list[np.logical_and(np.abs(z) > 0, np.imag(z) < 0)]
        z = z[np.logical_and(np.abs(z) > 0, np.imag(z) < 0)]

        return t_list, z


def fit_1d_model(ro_init, h_init, is_fixed_rho, is_fixed_h, Z_obs, t_list,
                 N_iter=10, method='CG', min_res=1e-9, max_res=1e50, min_h=1e-9, max_h=1e50):
    '''
    Функция для автоматического подбора (инверсии) 1D разреза сопротивлений.
    На вход принимает:
    - массив стартовых значений сопротивлений
    - массив стартовых значений мощностей (как и всегда, их должно быть на одно меньше, чем сопротивлений)
    - массив с флагами фиксации сопротивлений (True - сопротивление фиксировано и не должно меняться, False - нужно подбирать)
    - массив с флагами фиксации мощностей (аналогично сопротивлению)
    - массив наблюденных значений импеданса
    - массив периодов
    - количество итераций
    - метод оптимизации (см scipy.optimize.minimize)

    На выходе выдает массив подобранных сопротивлений и массив подобранных мощностей
    '''
    # print(ro_init, h_init, is_fixed_rho, is_fixed_h, Z_obs, t_list, N_iter, method, min_res, max_res, min_h, max_h)

    sect = np.empty(len(ro_init) + len(h_init))
    sect[::2] = ro_init
    sect[1::2] = h_init

    is_fixed = np.zeros(len(sect))
    is_fixed[::2] = is_fixed_rho
    is_fixed[1::2] = is_fixed_h
    is_fixed = is_fixed.astype('bool')

    init_sect = sect.copy()

    for n in range(N_iter):
        res = minimize(forward_rmse, sect, args=(is_fixed, init_sect, t_list, Z_obs),
                       method=method, options={'maxiter': 100})
        print(res)

        out_sect = res.x
        new_sect = sect.copy()
        new_sect[~is_fixed] = out_sect[~is_fixed]

        sect = new_sect.copy()

        for i in range(1, len(sect), 2):
            if sect[i] < min_h:
                sect[i] = min_h
            elif sect[i] > max_h:
                sect[i] = max_h

        for i in range(0, len(sect), 2):
            if sect[i] < min_res:
                sect[i] = min_res
            elif sect[i] > max_res:
                sect[i] = max_res

    new_sect = init_sect.copy()
    new_sect[~is_fixed] = sect[~is_fixed]

    h_out = new_sect[1::2]
    rho_out = new_sect[::2]

    return rho_out, h_out
