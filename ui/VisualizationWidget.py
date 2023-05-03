from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QGridLayout, QFormLayout

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class VisualizationWidget(QWidget):
    def __init__(self):
        super(VisualizationWidget, self).__init__()

        self.layout = QFormLayout()
        self.setLayout(self.layout)
