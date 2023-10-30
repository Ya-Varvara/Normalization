from mtd.mtd import MT1D

# from ui.ModelPlotWidget import MTDPlotWidget, ModelPlotWidget
# from ui.SimpleModelWidget import SimpleModelWidget

from models.ediFileClass import FrequencyMT1DFileData
# ============ Parent Classes ====================================
class Method:
    def __init__(self):
        self.result_data = None
        self.graph = None

    def save_results_in_file(self):
        pass


class OneColumnModel:
    def __init__(self, Ro=None, H=None, freq=None):
        self.Ro = Ro
        self.H = H
        self.freq_data = FrequencyMT1DFileData(data=freq)
        self.methods = {}
        self.tree_label = None

    def calculate_mt1d(self):
        self.methods['mt1d'] = mtdMethod((self.freq_data, self.Ro, self.H))

    def save_methods_result(self, method_type=None):
        def create_string(t):
            result_data_array.append(t)
            result_data_array.append(self.methods[t].save_results_in_file())

        result_data_array = []

        if method_type is None:
            for each_type in self.methods.keys():
                create_string(each_type)
        else:
            for each_type in method_type:
                if each_type in self.methods.keys():
                    create_string(each_type)
        return '\n'.join(result_data_array)


# ============ Child Classes ======================================

# ======== Methods
class mtdMethod(Method):
    def __init__(self, data):
        super(mtdMethod, self).__init__()
        freq, Ro, H = data
        self.result_data = MT1D(freq, len(Ro), Ro, H)
        self.data_widget = MTDPlotWidget()
        self.data_widget.draw_mtd_graph(self.result_data)
        self.tree_label = None

    def save_results_in_file(self):
        head = 'sqrtT\tRoT\tPht\n'
        data = ['\t'.join([str(round(self.result_data['T'][i], 4)),
                           str(round(self.result_data['RoT'][i], 2)),
                           str(round(self.result_data['Pht'][i], 2))]) for i in range(len(self.result_data['T']))]
        return head + '\n'.join(data)


# ======== Models
class GridModel:
    def __init__(self, file_path, file_data):
        self.file_path = file_path
        self.file_type, self.x, self.y, self.Vp, self.x_min, self.x_max, self.y_min, self.y_max, self.Vp_min, self.Vp_max, self.Nx, self.Ny = file_data
        self.points = []
        self.freq_data = None
        self.data_widget = None
        self.init_widget()

    # end def __init__

    def init_widget(self):
        self.data_widget = ModelPlotWidget(width=5, height=4, dpi=100)
        self.data_widget.draw_model(self)
        self.data_widget.axes.set_xlabel('meters')
        self.data_widget.axes.set_ylabel('meters')

    def get_points(self):
        return self.points

    def find_point(self, x, y):
        for point in self.points:
            if point.x == x and point.y == y and point.is_alive:
                return point
        return None

    # end def find_point

    def get_data_for_mt1d(self, point):
        if point.Ro is None or point.H is None:
            all_data = self.Vp[:, point.x // 10 - 1]
            Ro_list = []
            H_list = []
            for value in all_data:
                if not Ro_list or Ro_list[-1] != value:
                    Ro_list.append(value)
                    H_list.append(1)
                else:
                    H_list[-1] += 1
            k = abs(self.y_max - self.y_min) / self.Ny
            point.Ro, point.H = Ro_list, [round(x * k) for x in H_list]
        return

    # end def get_data_for_mt1d

    def add_point(self, xy):
        point = Point(self, xy[0], xy[1])
        self.get_data_for_mt1d(point)
        self.points.append(point)

    # end def add_point

    def delete_point(self, xy):
        for each in self.points:
            if each.x == xy[0] and each.y == xy[1] and each.is_alive:
                each.is_alive = False
                return
        return
    # end def add_point


# end class GridModel

class Point(OneColumnModel):
    def __init__(self, parent, x, y):
        super(Point, self).__init__()
        self.parent = parent
        self.x = x
        self.y = y
        self.is_alive = True
        self.tree_label = f'Точка ({self.x},{self.y})'

    # end def __init__

    def calculate_mt1d(self):
        self.methods['mt1d'] = mtdMethod((self.parent.freq_data, self.Ro, self.H))
# end class Point


class SimpleModel(OneColumnModel):
    def __init__(self, model_file_path, Ro, H, freq_data=None):
        super(SimpleModel, self).__init__(Ro, H, freq_data)
        self.file_path = model_file_path
        self.data_widget = None
        self.parent = None
        self.init_widget()

    # end def __init__

    def init_widget(self):
        self.data_widget = SimpleModelWidget(self)
# end class SimpleModel

