# Serial Plotter Application

from pyqtgraph.Qt import QtCore, QtGui
from threading import Thread
import pyqtgraph as pg
import numpy as np
import serial
import random
import sys
import time

"""Scrolling Plot Widget Example"""

# Scrolling plot widget with adjustable X-axis and dynamic Y-axis
class ScrollingPlot(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ScrollingPlot, self).__init__(parent)

        # Desired Frequency (Hz) = 1 / self.FREQUENCY
        # USE FOR TIME.SLEEP (s)
        self.FREQUENCY = .100

        # Frequency to update plot (ms)
        # USE FOR TIMER.TIMER (ms)
        self.TIMER_FREQUENCY = self.FREQUENCY * 1000

        # Set X Axis range. If desired is [-10,0] then set LEFT_X = -10 and RIGHT_X = 0
        self.LEFT_X = -10
        self.RIGHT_X = 0
        self.X_Axis = np.arange(self.LEFT_X, self.RIGHT_X, self.FREQUENCY)
        self.buffer = int((abs(self.LEFT_X) + abs(self.RIGHT_X))/self.FREQUENCY)
        self.timeData = [] 
        self.data = []
        # Create Plot Widget 
        self.scrolling_plot_widget = pg.PlotWidget()

        # Enable/disable plot squeeze (Fixed axis movement)
        self.scrolling_plot_widget.plotItem.setMouseEnabled(x=False, y=False)
        # self.scrolling_plot_widget.setXRange(self.LEFT_X, self.RIGHT_X)
        self.scrolling_plot_widget.setTitle('Scrolling Plot Example')
        self.scrolling_plot_widget.setLabel('left', 'Value')
        self.scrolling_plot_widget.setLabel('bottom', 'Time (s)')

        self.scrolling_plot = self.scrolling_plot_widget.plot()
        self.scrolling_plot.setPen(197,235,255)

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.scrolling_plot_widget)

        self.read_position_thread()
        self.start()

    # Update plot
    def start(self):
        self.position_update_timer = QtCore.QTimer()
        self.position_update_timer.timeout.connect(self.plot_updater)
        self.position_update_timer.start(self.get_scrolling_plot_timer_frequency())

    # Read in data using a thread
    def read_position_thread(self):
        self.current_position_value = 0
        self.old_current_position_value = 0
        self.position_update_thread = Thread(target=self.read_position, args=())
        self.position_update_thread.daemon = True
        self.position_update_thread.start()

    def read_position(self):
        frequency = self.get_scrolling_plot_frequency()
        self.new_data = []
        self.new_time = []
        prev_time = time.monotonic_ns()
        with serial.Serial('COM4', 115200, timeout = 1) as ser:
            ser.reset_input_buffer()
            while True:
                line = ser.readline().strip()
                s = line.decode('ascii')

                if s:
                    curr_time = time.monotonic_ns()
                    self.new_data.append(int(s))
                    self.new_time.append((curr_time - prev_time)*1e-9)
                    prev_time = curr_time


    def plot_updater(self):

        # if len(self.data) >= self.buffer:
        #     del self.data[:1]
        self.data     += self.new_data
        self.timeData += self.new_time
        self.new_data.clear()
        self.new_time.clear()

        self.scrolling_plot.setData(self.timeData, self.data)

    def clear_scrolling_plot(self):
        self.data[:] = []

    def get_scrolling_plot_frequency(self):
        return self.FREQUENCY

    def get_scrolling_plot_timer_frequency(self):
        return self.TIMER_FREQUENCY

    def get_scrolling_plot_layout(self):
        return self.layout

    def get_current_position_value(self):
        return self.current_position_value

    def get_scrolling_plot_widget(self):
        return self.scrolling_plot_widget

if __name__ == '__main__':
    # Create main application window
    app = QtGui.QApplication([])
    app.setStyle(QtGui.QStyleFactory.create("Cleanlooks"))
    mw = QtGui.QMainWindow()
    mw.setWindowTitle('Scrolling Plot Example')

    # Create scrolling plot
    scrolling_plot_widget = ScrollingPlot()

    # Create and set widget layout
    # Main widget container
    cw = QtGui.QWidget()
    ml = QtGui.QGridLayout()
    cw.setLayout(ml)
    mw.setCentralWidget(cw)

    # Can use either to add plot to main layout
    #ml.addWidget(scrolling_plot_widget.get_scrolling_plot_widget(),0,0)
    ml.addLayout(scrolling_plot_widget.get_scrolling_plot_layout(),0,0)
    mw.show()

    # Start Qt event loop unless running in interactive mode or using pyside
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()