from ui.base_ui.InvertionWidget import Ui_Form

from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QAbstractItemView, QGridLayout

from calculations.inversion import calc_phase

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm, ticker

from numpy import log, abs, real, imag, zeros, cumsum, sum, floor, ceil, log10, min, max


class InversionWidget(QWidget):
    def __init__(self, inversion):
        super(InversionWidget, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.inversion = inversion
        self.parent = inversion

        self.inv_plot = InversionPlot(self.inversion, self)
        self.ui.stackedWidget.addWidget(self.inv_plot)
        self.ui.stackedWidget.setCurrentWidget(self.inv_plot)

        self.ui.tableWidget.setColumnCount(2)
        self.ui.tableWidget.setRowCount(len(self.inversion.ro_out))
        self.ui.tableWidget.setHorizontalHeaderLabels(['Res', 'H'])
        print(self.inversion.ro_out)

        for row in range(len(self.inversion.ro_out)):
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(self.inversion.ro_out[row])))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(self.inversion.h_out[row])))

        self.ui.plainTextEdit.setReadOnly(True)
        self.ui.plainTextEdit.appendPlainText(f'|Z| error = {self.inversion.Z_error} %\nRe(Z) error = {self.inversion.Z_Re_error} %\nIm(Z) error = {self.inversion.Z_Im_error} %')


class InversionPlot(QWidget):
    def __init__(self, inversion, parent=None, width=10, height=4):
        super(InversionPlot, self).__init__()

        self.inver = inversion
        self.parent = parent

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.figure = Figure(figsize=(width, height), dpi=100, layout="constrained")
        self.canvas = FigureCanvas(self.figure)

        self.layout.addWidget(self.canvas)

        self.axes = []
        self.contours = {}

        self.gs = self.figure.add_gridspec(2, 2)

        ax1 = self.figure.add_subplot(self.gs[0, 0])
        ax1.loglog(self.inver.t_list, abs(self.inver.Z), 'g')
        ax1.loglog(self.inver.t_list, abs(self.inver.Z_inv), 'r')
        ax1.grid(True)
        ax1.legend(['|Z| True', '|Z| Inversion', 'Re(Z) True', 'Re(Z) Inversion', 'Im(Z) True', 'Im(Z) Inversion'])
        ax1.set_title('|Z|')

        ax2 = self.figure.add_subplot(self.gs[0, 1])
        ax2.semilogx(self.inver.t_list, calc_phase(self.inver.Z), 'g')
        ax2.semilogx(self.inver.t_list, calc_phase(self.inver.Z_inv), 'r')
        ax2.grid(True)
        ax2.legend([r'$\phi$ True', r'$\phi$ Inversion'])
        ax2.set_title(r'$\phi$')

        ax5 = self.figure.add_subplot(self.gs[1, :])
        self.plot_rho(ax5, self.inver.h_out[0:len(self.inver.h_out)-1], self.inver.ro_out)
        self.plot_rho(ax5, self.inver.h_init[0:len(self.inver.h_out)-1], self.inver.ro_init)
        self.plot_rho(ax5, self.inver.h_out[0:len(self.inver.h_out)-1], self.inver.ro_out)
        ax5.grid(True)
        ax5.legend(['Inversion'])
        ax5.set_title(r'$\rho$')
        self.canvas.draw()

    def plot_rho(self, ax, h, rho, max_depth=None):
        """
        Функция, предназначенная для визуализации 1D разреза сопротивлений.
        На вход принимает мощности слоев и их сопротивления (мощностей, как всегда, на одну меньше, чем сопротивлений)
        На выходе рисует график, на котором по горизонтали откладывается глубина, а по вертикали сопротивления
        """
        hp = zeros(len(rho) * 2)
        rhop = zeros(len(rho) * 2)

        hp[1:-1:2] = cumsum(h)
        hp[-1] = sum(h) * 1.1 if max_depth is None else max_depth
        hp[2::2] = cumsum(h)

        rhop[::2] = rho
        rhop[1::2] = rho

        ax.loglog(hp, rhop, linewidth=1)
        ax.grid(True)
        ax.set_xlabel('H')
        ax.set_ylabel(r'$\rho$')

        ax.set_xlim([10 ** floor(log10(hp[1]) - 1), 10 ** ceil(log10(hp[-1]))])
        ax.set_ylim([10 ** floor(log10(min(rho))), 10 ** ceil(log10(max(rho)))])
