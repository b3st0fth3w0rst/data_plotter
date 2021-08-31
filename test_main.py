import csv
import os
import pandas as pd
import pyqtgraph as pg
import sys

from test_plot import Plot
from PyQt5 import QtWidgets, QtCore, QtGui
from ui.test_window import Ui_MainWindow

CURRENT_FOCUSED_PLOT_ID = None
PREVIOUS_FOCUSED_PLOT_ID = None
CURRENT_EVENT = None
PLOT_EVENT_MAP = {}


class Connector:
    """
    Class that connects the compiled test_window.py to test_main.py.
    This class contains the modified code that does not get overridden by mod.py.
    """

    class MyPlotWidget(pg.PlotWidget):
        """
        Overridden PlotWidget class to add a mouseclick handler to each of the graphs created.
        """

        def __init__(self, connector):
            super().__init__()
            self.scene().sigMouseClicked.connect(self.mouse_clicked_event_handler)
            self.main_myplotwidget = connector

        def mouse_clicked_event_handler(self):
            """
            Mouse clicked event handler for graphs
            """

            global CURRENT_FOCUSED_PLOT_ID
            CURRENT_FOCUSED_PLOT_ID = id(self)

            if CURRENT_FOCUSED_PLOT_ID != PREVIOUS_FOCUSED_PLOT_ID:
                self.main_myplotwidget.update_graphs_checkboxes()

            mouse_point_x = self.main_myplotwidget.current_mouse_point[0]

        def mouseMoveEvent(self, ev):
            """
            Mouse movement on graph event handler

            :param ev: QMouseEvent - Event object for the graphs
            """

            try:
                if id(self) == CURRENT_FOCUSED_PLOT_ID:
                    mouse_point = self.main_myplotwidget.plot.mouse_moved(ev, self.main_myplotwidget.get_current_graph())

                    if 0 <= mouse_point[0] <= self.main_myplotwidget.x_range \
                            and 0 <= mouse_point[1] <= self.main_myplotwidget.y_range:
                        self.main_myplotwidget.ui.mouse_point_info_label.setText('Mouse Point: <span '
                                                                                 'style="font-size:10pt" '
                                                                                 'style="color:red">X={}</span>, Y={}'
                                                                                 .format(mouse_point[0], mouse_point[1])
                                                                                 )
                        self.main_myplotwidget.current_mouse_point = mouse_point
            except Exception as e:
                print(e)

    def __init__(self):
        self.model = QtGui.QStandardItemModel()
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow(self.main_window)

        self.csv_data = {}
        self.column_name_cb = {}
        self.graph_cb_data = {}
        self.plot_widgets = []
        self.x_range = 0
        self.y_range = 0
        self.current_mouse_point = (0, 0)

        self.ui_setup()
        self.plot = Plot(self.ui.mouse_point_info_label)

    def ui_setup(self):
        """
        Setups up the UI with additional/modified parameters that may or may not be available in test_window.py
        """

        self.ui.load_data_pb.clicked.connect(self.load_data)

        self.ui.plot_widget_1 = self.MyPlotWidget(self)
        self.ui.plot_widget_1.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.ui.plot_widget_1.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.ui.plot_widget_1.setObjectName("plot_widget_1")
        self.ui.gridLayout.addWidget(self.ui.plot_widget_1, 0, 0, 1, 1)

        self.ui.plot_widget_2 = self.MyPlotWidget(self)
        self.ui.plot_widget_2.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.ui.plot_widget_2.setStyleSheet("background-color: rgb(255, 255, 0);")
        self.ui.plot_widget_2.setObjectName("plot_widget_2")
        self.ui.gridLayout_7.addWidget(self.ui.plot_widget_2, 0, 0, 1, 1)

        self.ui.plot_widget_3 = self.MyPlotWidget(self)
        self.ui.plot_widget_3.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.ui.plot_widget_3.setStyleSheet("background-color: rgb(0, 85, 255);")
        self.ui.plot_widget_3.setObjectName("plot_widget_3")
        self.ui.gridLayout_8.addWidget(self.ui.plot_widget_3, 0, 0, 1, 1)

        self.plot_widgets.append(self.ui.plot_widget_1)
        self.plot_widgets.append(self.ui.plot_widget_2)
        self.plot_widgets.append(self.ui.plot_widget_3)

        # Set the default graph focused to the top graph
        global CURRENT_FOCUSED_PLOT_ID
        CURRENT_FOCUSED_PLOT_ID = id(self.ui.plot_widget_1)
        global PREVIOUS_FOCUSED_PLOT_ID
        PREVIOUS_FOCUSED_PLOT_ID = CURRENT_FOCUSED_PLOT_ID

    def get_current_graph(self):
        """
        Returns the currently focused graph object.

        :return: MyPlotWidget - The currently focused plot.
        """
        for graph in self.plot_widgets:
            if CURRENT_FOCUSED_PLOT_ID == id(graph):
                return graph

    def plot_data(self, graph, data):
        """
        Plots the given data on the given graph.

        :param graph: MyPlotWidget - PlotWidget object to plot data on.
        :param data: Dict - Dictionary containing the data name and data set.
        """

        self.plot.plot_values(graph, data, self.x_range, self.y_range)

    def load_data(self, file_path=None):
        """
        Handles opening a CSV file
        """

        # if not file_path:
        #     csv_file_name, _ = QFileDialog.getOpenFileName(self.main_window)
        # else:
        #     csv_file_name = file_path

        csv_file_name = 'resource\\test_data.csv'

        if os.path.exists(csv_file_name):
            for plot in self.plot_widgets:
                plot.clear()

            with open(csv_file_name, "r") as f:
                csv_reader = csv.reader(f, delimiter=',')
                columns = next(csv_reader)
                df = pd.read_csv(csv_file_name, usecols=columns)

                for item in columns:
                    if item != 'Name':
                        self.csv_data[item] = df[item]

                for row in csv.reader(f):
                    items = [QtGui.QStandardItem(field) for field in row]
                    self.model.appendRow(items)

            # Create Column checkboxes
            for column in self.csv_data.keys():
                self.column_name_cb['check_box_{}'.format(column)] = QtWidgets.QCheckBox(
                    self.ui.scrollAreaWidgetContents)
                self.column_name_cb.get('check_box_{}'.format(column)).setObjectName(
                    "check_box_{}".format(column))
                self.column_name_cb.get('check_box_{}'.format(column)).setText(column)
                self.column_name_cb.get('check_box_{}'.format(column)).stateChanged.connect(
                    self.checkbox_state_changed_csv)
                self.ui.verticalLayout_3.addWidget(self.column_name_cb.get('check_box_{}'.format(column)))

            self.x_range = len(self.csv_data.get(list(self.csv_data.keys())[0]))
            self.y_range = 150

            self.ui.plot_widget_1.setEnabled(True)
            self.ui.plot_widget_2.setEnabled(True)
            self.ui.plot_widget_3.setEnabled(True)

    def checkbox_state_changed_csv(self):
        """
        Handles when the checkboxes state change for the Pot tab.
        """

        columns_to_plot = []
        data_to_plot = {}

        for checkbox in self.column_name_cb.items():
            if checkbox[1].isChecked():
                columns_to_plot.append(checkbox[0])

        for item in columns_to_plot:
            item = item.split('_')[-1]
            data_to_plot[item] = self.csv_data.get(item).values

        if PREVIOUS_FOCUSED_PLOT_ID == CURRENT_FOCUSED_PLOT_ID and data_to_plot:
            self.graph_cb_data[CURRENT_FOCUSED_PLOT_ID] = data_to_plot
            self.plot_data(self.get_current_graph(), data_to_plot)
        elif PREVIOUS_FOCUSED_PLOT_ID != CURRENT_FOCUSED_PLOT_ID:
            self.plot_data(self.get_current_graph(), data_to_plot)
        else:
            self.plot.clear_plot_widget(self.get_current_graph())

    def update_graphs_checkboxes(self):
        """
        Updates the checkboxes in the CSV tab to match the currently focused graph.
        A mouse click on any particular graph will show the associated checkboxes.
        """

        for checkbox in self.column_name_cb.items():
            checkbox[1].setChecked(False)

        global PREVIOUS_FOCUSED_PLOT_ID
        if PREVIOUS_FOCUSED_PLOT_ID != CURRENT_FOCUSED_PLOT_ID and \
                CURRENT_FOCUSED_PLOT_ID not in self.graph_cb_data.keys():
            self.plot_data(self.get_current_graph(), {})

        for cb_data in self.graph_cb_data.items():
            if cb_data[0] == id(self.get_current_graph()):
                data_list = list(cb_data[1].keys())
                for checkbox in self.column_name_cb.items():
                    if checkbox[0].split('_')[-1] in data_list:
                        checkbox[1].setChecked(True)
                    else:
                        checkbox[1].setChecked(False)

        PREVIOUS_FOCUSED_PLOT_ID = CURRENT_FOCUSED_PLOT_ID


if __name__ == "__main__":
    a = Connector()
    a.main_window.show()
    sys.exit(a.app.exec_())
