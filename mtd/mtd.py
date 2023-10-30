from math import pi, sqrt, degrees, atan, log10

import cmath


def MT1D(freq_data, N_layers: int, Ro_list=None, H_list=None):
    Rot_list = []
    Pht_list = []
    T_list = []

    m0 = 4 * pi * 10 ** -7

    if isinstance(freq_data, tuple):
        NT, T, Q = freq_data
        t_list = [T * Q ** i for i in range(int(NT))]
    else:
        t_list = freq_data

    for each_t in t_list:
        w = 2 * pi / each_t      # круговая частота
        R = complex(1, 0)
        for m in range(N_layers - 1, 0, -1):
            k = cmath.sqrt(-complex(0, 1) * w * m0 / Ro_list[m - 1])
            A = sqrt(Ro_list[m - 1] / Ro_list[m])
            B = cmath.exp(-2 * k * H_list[m - 1]) * (R - A) / (R + A)
            R = (1 + B) / (1 - B)
        Rot = Ro_list[0] * abs(R) ** 2                  # рассчет сопротивления
        Pht = degrees(atan(R.imag / R.real)) - 45       # рассчет фазы
        Rot_list.append(Rot)
        Pht_list.append(Pht)
        T_list.append(sqrt(each_t))
    logRot = [log10(i) for i in Rot_list]
    logT = [log10(i) for i in T_list]
    return {'T': T_list, 'logT': logT, 'RoT': Rot_list, 'logRoT': logRot, 'Pht': Pht_list}


def export_mtd(file_name: str, mtd_data: tuple):
    T_list, Rot_list, Pht_list, NT = mtd_data
    with open(file_name, 'w') as file:
        file.write('sqrtT  RoT  Pht \n')
        data = [' '.join([str(round(T_list[i], 2)), str(round(Rot_list[i], 2)), str(round(Pht_list[i], 2))]) for i in range(NT)]
        file.write('\n'.join(data))
    return
