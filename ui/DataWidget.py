import numpy as np

from PyQt5.QtWidgets import QWidget, QGridLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm, ticker


def calc_effective_Z(z):
    return np.sqrt(z[:, 0, 0] * z[:, 1, 1] - z[:, 1, 0] * z[:, 0, 1])


def calc_log_levels(data, levels):
    ticks = np.arange(np.floor(np.log10(np.nanmin(data))),
                      np.ceil(np.log10(np.nanmax(data))))

    lvls_exp = np.linspace(np.floor(np.log10(np.nanmin(data))),
                           np.ceil(np.log10(np.nanmax(data))), levels)

    return 10 ** lvls_exp, 10 ** ticks


class MTComponent(QWidget):
    def __init__(self, normalization, edis, width=10, height=4, plot_type='maps', cmap=cm.jet, levels=50, parent=None):
        super(MTComponent, self).__init__()

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.parent = parent
        self.normalization = normalization
        self.edis = edis

        self.figure = Figure(figsize=(width, height), dpi=100, layout="constrained")
        self.canvas = FigureCanvas(self.figure)

        self.layout.addWidget(self.canvas)

        # self.lbls = [['Rho XX', 'PHI XX'], ['Rho XY', 'PHI XY'],
        #              ['Rho YX', 'PHI YX'], ['Rho YY', 'PHI YY'],
        #              ['Rho Eff', 'PHI Eff']]

        self.lbls = [['Rho XY', 'PHI XY'],
                     ['Rho YX', 'PHI YX'],
                     ['Rho Eff', 'PHI Eff']]

        self.visibility = {'Rho XY': True,
                           'Rho YX': True,
                           'PHI XY': True,
                           'PHI YX': True,
                           'Rho Eff': True,
                           'PHI Eff': True}

        self.axes = {}
        self.colorbars = {}
        self.contours = {}

        mu0 = 4 * np.pi * 1e-7

        for i in range(3):
            for j in range(2):
                self.axes[self.lbls[i][j]] = self.figure.add_subplot(3, 2, i * 2 + 1 + j)
                self.axes[self.lbls[i][j]].grid(True)
                self.axes[self.lbls[i][j]].set_title(self.lbls[i][j])

                if plot_type == 'maps':
                    self.axes[self.lbls[i][j]].set_ylabel('t, sec')
                else:
                    self.axes[self.lbls[i][j]].set_xlabel('t, sec')
                    self.axes[self.lbls[i][j]].set_ylabel('rho, Ohm*m' if j == 0 else 'phi, deg')

        if plot_type == 'maps':
            unique_freqs = set()
            for edi in self.edis:
                for f in edi.Z.freq:
                    unique_freqs.add(f)

            unique_freqs = np.sort(np.array(list(unique_freqs)))[::-1]

            times = 1 / unique_freqs
            x = np.arange(len(self.edis))

            res_xx_section = np.zeros([len(times), len(x)]) + np.nan
            res_xy_section = np.zeros([len(times), len(x)]) + np.nan
            res_yx_section = np.zeros([len(times), len(x)]) + np.nan
            res_yy_section = np.zeros([len(times), len(x)]) + np.nan
            phase_xx_section = np.zeros([len(times), len(x)]) + np.nan
            phase_xy_section = np.zeros([len(times), len(x)]) + np.nan
            phase_yx_section = np.zeros([len(times), len(x)]) + np.nan
            phase_yy_section = np.zeros([len(times), len(x)]) + np.nan

            rho_eff_section_real = np.zeros([len(times), len(x)]) + np.nan
            rho_eff_section_imag = np.zeros([len(times), len(x)]) + np.nan

            for i, edi in enumerate(self.edis):
                res_xx_section[:, i] = np.interp(times, 1 / edi.Z.freq, edi.Z.res_xx)
                res_xy_section[:, i] = np.interp(times, 1 / edi.Z.freq, edi.Z.res_xy)
                res_yx_section[:, i] = np.interp(times, 1 / edi.Z.freq, edi.Z.res_yx)
                res_yy_section[:, i] = np.interp(times, 1 / edi.Z.freq, edi.Z.res_yy)

                phase_xx_section[:, i] = np.interp(times, 1 / edi.Z.freq, edi.Z.phase_xx)
                phase_xy_section[:, i] = np.interp(times, 1 / edi.Z.freq, edi.Z.phase_xy)
                phase_yx_section[:, i] = np.interp(times, 1 / edi.Z.freq, edi.Z.phase_yx)
                phase_yy_section[:, i] = np.interp(times, 1 / edi.Z.freq, edi.Z.phase_yy)

                z_eff = np.interp(times, 1 / edi.Z.freq, calc_effective_Z(edi.Z.z))

                r_eff = (z_eff ** 2) * times / 2 / np.pi * (mu0 * 1e6)  # МНОЖИТЕЛЬ КОСТЫЛЬНЫЙ
                rho_eff_section_real[:, i] = np.real(r_eff)
                rho_eff_section_imag[:, i] = np.imag(r_eff)

            phase_eff_section = np.arctan2(rho_eff_section_imag, rho_eff_section_real) * 180 / np.pi
            rho_eff_section = np.sqrt(rho_eff_section_imag ** 2 + rho_eff_section_real ** 2)

            phase_eff_section[rho_eff_section == 0] = np.nan
            rho_eff_section[rho_eff_section == 0] = np.nan

            # res_list = [res_xx_section, res_xy_section, res_yx_section, res_yy_section, rho_eff_section]
            # phase_list = [phase_xx_section, phase_xy_section, phase_yx_section, phase_yy_section, phase_eff_section]

            res_list = [res_xy_section, res_yx_section, rho_eff_section]
            phase_list = [phase_xy_section, phase_yx_section, phase_eff_section]

            for i in range(3):
                lvls, ticks = calc_log_levels(res_list[i], levels)

                self.contours[self.lbls[i][0]] = self.axes[self.lbls[i][0]].contourf(x, times, res_list[i], levels=lvls,
                                                                                     locator=ticker.LogLocator(),
                                                                                     cmap=cmap)
                self.colorbars[self.lbls[i][0]] = self.figure.colorbar(self.contours[self.lbls[i][0]], ticks=ticks)

                self.contours[self.lbls[i][1]] = self.axes[self.lbls[i][1]].contourf(x, times, phase_list[i], cmap=cmap,
                                                                                     levels=levels)
                self.colorbars[self.lbls[i][1]] = self.figure.colorbar(self.contours[self.lbls[i][1]])

            for ax in self.axes.values():
                ax.set_ylim([times[0], times[-1]])
                ax.set_yscale('log')
                ax.invert_yaxis()

        else:
            for edi in self.edis:
                t = 1 / edi.Z.freq

                # self.axes[self.lbls[0][0]].loglog(t, edi.Z.res_xx)
                # self.axes[self.lbls[0][1]].semilogx(t, edi.Z.phase_xx)
                # self.axes[self.lbls[1][0]].loglog(t, edi.Z.res_xy)
                # self.axes[self.lbls[1][1]].semilogx(t, edi.Z.phase_xy)
                # self.axes[self.lbls[2][0]].loglog(t, edi.Z.res_yx)
                # self.axes[self.lbls[2][1]].semilogx(t, edi.Z.phase_yx)
                # self.axes[self.lbls[3][0]].loglog(t, edi.Z.res_yy)
                # self.axes[self.lbls[3][1]].semilogx(t, edi.Z.phase_yy)

                self.axes[self.lbls[0][0]].loglog(t, edi.Z.res_xy)
                self.axes[self.lbls[0][1]].semilogx(t, edi.Z.phase_xy)
                self.axes[self.lbls[1][0]].loglog(t, edi.Z.res_yx)
                self.axes[self.lbls[1][1]].semilogx(t, edi.Z.phase_yx)

                z_eff = calc_effective_Z(edi.Z.z)
                rho_eff = z_eff ** 2 * t / 2 / np.pi / mu0
                phase_eff = np.angle(rho_eff, deg=True)

                # self.axes[self.lbls[4][0]].loglog(t, np.abs(rho_eff))
                # self.axes[self.lbls[4][1]].semilogx(t, phase_eff)

                self.axes[self.lbls[2][0]].loglog(t, np.abs(rho_eff))
                self.axes[self.lbls[2][1]].semilogx(t, phase_eff)

    def set_visible(self, label: str, visible: bool):
        print(label, visible)
        self.axes[label].set_visible(visible)
        self.visibility[label] = visible
        if visible:
            self.colorbars[label] = self.figure.colorbar(self.contours[label])
        else:
            self.colorbars[label].remove()
        self.canvas.draw()
