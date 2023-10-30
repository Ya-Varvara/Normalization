from PyQt5.QtWidgets import QAction, QMenu, QWidget, QVBoxLayout
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure


class ModelPlotWidget(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, graphs_cols=1, graphs_rows=1):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(graphs_rows, graphs_cols, 1)
        super().__init__(self.fig)

        self.parent = parent
        self.current_model = None

        self.popMenu = QMenu(self)
        self.init_popMenu()

        self.cidmove = self.fig.canvas.mpl_connect('motion_notify_event', self.on_move)
        self.cidclick = self.fig.canvas.mpl_connect('button_press_event', self.mouse_left_btn_clicked)

        self.fig.canvas.mpl_connect('key_press_event', self.on_shift_press)
        self.fig.canvas.mpl_connect('key_release_event', self.on_shift_release)

        self.shift_is_held = None

    # end def __init__

    def init_popMenu(self):
        addPointAction = QAction('Добавить точку', self)
        addPointAction.triggered.connect(self.add_point)
        self.popMenu.addAction(addPointAction)

        deletePointAction = QAction('Удалить точку', self)
        deletePointAction.triggered.connect(self.delete_point)
        self.popMenu.addAction(deletePointAction)

    # end def init_popMenu

    def draw_model(self, model=None):
        self.current_model = model
        self.axes.contourf(model.x, model.y, model.Vp)

    # end def model

    def on_move(self, event):
        if event.xdata and event.ydata:
            self.parent.ui.statusbar.showMessage(f'x = {round(event.xdata)}, y = {round(event.ydata)}', 1000)

    # end def on_move

    def mouse_left_btn_clicked(self, event):
        if event.button == MouseButton.RIGHT:
            cursor = QCursor()
            self.popMenu.popup(cursor.pos())

    # end def mouse_left_btn_clicked

    def on_shift_press(self, event):
        if event.key == 'shift':
            self.shift_is_held = True

    def on_shift_release(self, event):
        if event.key == 'shift':
            self.shift_is_held = False

    def add_point(self):
        def draw_point(event):
            if event.xdata and event.ydata:
                self.axes.scatter(event.xdata, event.ydata, edgecolor='white')
                self.current_model.add_point((round(event.xdata), round(event.ydata)))
                self.figure.canvas.draw()

                if not self.shift_is_held:
                    self.fig.canvas.mpl_disconnect(ciddraw)
                    self.parent.setCursor(Qt.ArrowCursor)
            return

        self.parent.setCursor(Qt.CrossCursor)
        ciddraw = self.fig.canvas.mpl_connect('button_press_event', draw_point)

    # end def on_move

    def delete_point(self):
        pass

    # end def delete_point

    def get_points(self):
        return self.points
    # end def get_points


# end class ModelPlotWidget

class MTDPlotWidget2(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100, graphs_cols=2, graphs_rows=1):
        self.fig1 = Figure(figsize=(width, height), dpi=dpi)
        self.axes1 = self.fig1.add_subplot(graphs_rows, graphs_cols, 1)
        self.axes2 = self.fig1.add_subplot(graphs_rows, graphs_cols, 2)
        super().__init__(self.fig1)

        self.parent = parent

    # end def __init__

    def draw_mtd_graph(self, mtd_result):
        self.axes1.plot(mtd_result['T'], mtd_result['RoT'])
        self.axes1.set_xlabel('X')
        self.axes1.set_ylabel('Y')
        self.axes1.set_xscale('log')
        self.axes1.set_yscale('log')
        self.axes2.plot(mtd_result['T'], mtd_result['Pht'])
        self.axes2.set_xlabel('X')
        self.axes2.set_ylabel('Y')
        self.axes2.set_xscale('log')
        # self.axes2.set_yscale('log')

    # end def draw_mtd_graph


# end class MTDPlotWidget

class MTDPlotWidget(QWidget):
    def __init__(self, parent=None, width=5, height=5, dpi=100, graphs_cols=2, graphs_rows=1):
        super(MTDPlotWidget, self).__init__()
        self.fig1 = Figure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvas(self.fig1)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.axes1 = self.fig1.add_subplot(graphs_rows, graphs_cols, 1)
        self.axes2 = self.fig1.add_subplot(graphs_rows, graphs_cols, 2)
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.parent = parent

    # end def __init__

    def draw_mtd_graph(self, mtd_result):
        self.axes1.plot(mtd_result['T'], mtd_result['RoT'])
        self.axes1.set_xlabel('T')
        self.axes1.set_ylabel('Ro')
        self.axes1.set_xscale('log')
        self.axes1.set_yscale('log')
        self.axes1.title.set_text('Кривые кажущегося сопротивления')
        self.axes2.plot(mtd_result['T'], mtd_result['Pht'])
        self.axes2.set_xlabel('T')
        self.axes2.set_ylabel('Ph')
        self.axes2.set_xscale('log')
        self.axes2.title.set_text('Кривые фазы импеданса')

        self.axes1.grid()
        self.axes2.grid()
        # self.axes2.set_yscale('log')

    # end def draw_mtd_graph
# end class MTDPlotWidget
