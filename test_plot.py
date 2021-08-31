import numpy as np
import random
import pyqtgraph as pg

from PyQt5 import QtCore


class Plot:

    def __init__(self, mouse_point_info_label):
        self.widget = None
        self.data = None
        self.x_range = None
        self.y_range = None
        self.color_map = []
        self.vb = None
        self.hLine = None
        self.vLine = None
        self.event_graph_map = {}
        self.mouse_point_info_label = mouse_point_info_label

    def get_color(self, item_to_color):
        """
        Returns a random color.

        :param item_to_color: Specific data item to color. self.color_map keep track of colors used for items. If an
                              item has already been colored we'll reuse the same color, otherwise pick a new color.
        :return: Tuple - RGB values representing a color (255,255,255).
        """

        color = (255, 255, 255)
        for item in self.data.items():
            if item[0] == item_to_color:
                existing_color = [i for i, v in enumerate(self.color_map) if v[0] == item[0]]
                if existing_color is not None and existing_color:
                    return self.color_map[existing_color[0]][1]
                else:
                    r = random.randint(0, 255)
                    g = random.randint(0, 255)
                    b = random.randint(0, 255)
                    color = (r, g, b)
                    self.color_map.append((item[0], color))
                    return color
        self.color_map.append((item_to_color, color))
        return color

    def mouse_moved(self, evt, current_graph, x=None, y=None):
        self.widget = current_graph
        mouse_point_x = 0
        mouse_point_y = 0

        if x is not None:
            self.vLine.setPos(x)

            if y is not None:
                self.hLine.setPos(y)
            else:
                self.hLine.setPos(0)

            return x, y
        else:
            x = evt.x()
            y = evt.y()

        pos = QtCore.QPointF(x, y)

        if self.widget.sceneBoundingRect().contains(pos):
            try:
                mouse_point = self.vb.mapSceneToView(pos)
                mouse_point_x = int(mouse_point.x())
                mouse_point_y = int(mouse_point.y())

                if 0 <= mouse_point_x <= self.x_range and 0 <= mouse_point_y <= self.y_range:
                    self.vLine.setPos(mouse_point.x())
                    self.hLine.setPos(mouse_point.y())
            except Exception as e:
                pass

            return mouse_point_x, mouse_point_y

    def plot_values(self, plot_widget, data, x_range, y_range):
        """
        Plots the given values on the given graph.

        :param plot_widget: MyPlotWidget - Overridden PlotWidget method in main.Connector() class. Graph object.
        :param data: Dict - Containing the name of the data to plot and the data itself.
        :param x_range: Int - Max x-axis value.
        :param y_range: Int - Max y-axis value.
        """

        self.widget = plot_widget
        self.data = data
        self.x_range = x_range
        self.y_range = y_range

        self.widget.setXRange(0, self.x_range)
        self.widget.setYRange(0, self.y_range)
        self.widget.showGrid(x=True, y=True)
        self.widget.addLegend()
        # self.widget.setLabel('left', 'Value', units='y')
        self.widget.setLabel('bottom', 'Frames')
        self.widget.clear()

        for item in self.data.items():
            line = self.widget.plot(np.insert(item[1], 0, item[1][0]), pen=self.get_color(item[0]),
                                    symbolPen=self.get_color(item[0]), symbol='o', symbolSize=1, name=item[0])
        self.marker(self.widget)

    def marker(self, plot_widget):
        # Crosshair
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        plot_widget.addItem(self.vLine, ignoreBounds=True)
        plot_widget.addItem(self.hLine, ignoreBounds=True)

        self.vb = plot_widget.plotItem.vb
        proxy = pg.SignalProxy(plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)
        plot_widget.scene().sigMouseMoved.connect(self.mouse_moved)

    def clear_plot_widget(self, plot_widget):
        plot_widget.clear()
