import numpy as np
import matplotlib.pyplot as plt
import copy
import mtpy.core.edi as mtedi

import warnings
warnings.filterwarnings('ignore')


def edi_fill_nans(edi):
    """
    Функция заменяет нулевые значения сопротивлений и соответствующие им значения фазы на NaN
    """

    edi.Z.phase_xx[edi.Z.res_xx == 0] = np.nan
    edi.Z.res_xx[edi.Z.res_xx == 0] = np.nan
    edi.Z.phase_xy[edi.Z.res_xy == 0] = np.nan
    edi.Z.res_xy[edi.Z.res_xy == 0] = np.nan
    edi.Z.phase_yx[edi.Z.res_yx == 0] = np.nan
    edi.Z.res_yx[edi.Z.res_yx == 0] = np.nan
    edi.Z.phase_yy[edi.Z.res_yy == 0] = np.nan
    edi.Z.res_yy[edi.Z.res_yy == 0] = np.nan


def read_edi_files(fnames):
    """
    Функция читает файлы из путей, которые содержатся в списке fnames, и создает список объектов Edi
    """

    edis = []

    for fname in fnames:
        edi = mtedi.Edi()
        edi.read_edi_file(fname)
        edi_fill_nans(edi)
        edis.append(edi)

    return edis


def moving_avg_filter(x, data, width):
    """
    Функция для сглаживания скользящим средним
    """

    data_f = np.empty(len(data))

    for i in range(len(data)):
        data_f[i] = np.mean(data[np.logical_and(x >= x[i] - width / 2, x <= x[i] + width / 2)])

    return data_f


def plot_edi_rho(edis, figsize=(20, 20)):
    """
    Функция для визуализации сопротивлений и фазы для списка Edi
    """

    fig = plt.figure(figsize=figsize)

    lbls = [['Rho XX', 'PHI XX'], ['Rho XY', 'PHI XY'],
            ['Rho YX', 'PHI YX'], ['Rho YY', 'PHI YY']]

    axes = []
    for i in range(4):
        axes.append([])
        for j in range(2):
            axes[i].append(fig.add_subplot(4, 2, i * 2 + 1 + j))
            axes[i][j].grid(True)
            axes[i][j].set_title(lbls[i][j])
            axes[i][j].set_xlabel('t, sec')
            axes[i][j].set_ylabel('rho, Ohm*m' if j == 0 else 'phi, deg')

    for edi in edis:
        t = 1 / edi.Z.freq

        axes[0][0].loglog(t, edi.Z.res_xx)
        axes[0][1].semilogx(t, edi.Z.phase_xx)
        axes[1][0].loglog(t, edi.Z.res_xy)
        axes[1][1].semilogx(t, edi.Z.phase_xy)
        axes[2][0].loglog(t, edi.Z.res_yx)
        axes[2][1].semilogx(t, edi.Z.phase_yx)
        axes[3][0].loglog(t, edi.Z.res_yy)
        axes[3][1].semilogx(t, edi.Z.phase_yy)


def normalize_rho(edis, T, n_points):
    """
    Функция для нормализации набора Edi.

    :param edis: набор edi
    :param T: период в секундах, на котором происходит нормализация
    :param n_points: количество точек, по которым происходит осреднение
    """

    rhos_xy = np.empty(len(edis))
    rhos_yx = np.empty(len(edis))

    for i, edi in enumerate(edis):
        T_id = np.argmin(np.abs(1 / edi.Z.freq - T))

        if np.isnan(edi.Z.res_xy[T_id]):
            nans = np.isnan(edi.Z.res_xy)
            rhos_xy[i] = np.interp(T_id, np.arange(len(nans))[~nans], edi.Z.res_xy[~nans])
        else:
            rhos_xy[i] = edi.Z.res_xy[T_id]

        if np.isnan(edi.Z.res_yx[T_id]):
            nans = np.isnan(edi.Z.res_yx)
            rhos_yx[i] = np.interp(T_id, np.arange(len(nans))[~nans], edi.Z.res_yx[~nans])
        else:
            rhos_yx[i] = edi.Z.res_yx[T_id]

    rhos_xy_f = moving_avg_filter(np.arange(len(edis)), rhos_xy, n_points)
    rhos_yx_f = moving_avg_filter(np.arange(len(edis)), rhos_yx, n_points)

    new_edis = copy.deepcopy(edis)

    for i in range(len(edis)):
        res_array = np.empty([len(edis[i].Z.freq), 2, 2])
        phase_array = np.empty([len(edis[i].Z.freq), 2, 2])

        xy_c = rhos_xy_f[i] / edis[i].Z.res_xy[T_id]
        yx_c = rhos_yx_f[i] / edis[i].Z.res_yx[T_id]

        new_edis[i].Z.res_xy[:] = edis[i].Z.res_xy[:] * xy_c
        new_edis[i].Z.res_yx[:] = edis[i].Z.res_yx[:] * yx_c

        new_edis[i].Z.z[:, 0, 1] *= np.sqrt(xy_c)
        new_edis[i].Z.z[:, 1, 0] *= np.sqrt(yx_c)

        edi_fill_nans(new_edis[i])
    return new_edis
