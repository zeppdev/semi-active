import collections

from PyQt4 import QtCore, QtGui
import numpy as np
import pyqtgraph as pg

import sys
from connector import activetwo_reader, dummy_reader
from ui import PlotWindow
from ui.PlotWindow import Ui_MainWindow
import queue
from IPython.html.widgets.widget_bool import Checkbox
from PyQt4.QtCore import SIGNAL

class MyPlot(QtGui.QMainWindow, PlotWindow.Ui_MainWindow):
    INPUT_RATE = 512.0
    DRAW_INTERVAL = 50
    PLOT_SIZE = 5000  # in milliseconds
    CHANNEL_NUMBER = 32

    DUMMY = True  # use dummy reader producing random data
    CHANNELS = np.zeros(32)
    reader = dummy_reader if DUMMY else activetwo_reader
    plot_deque = collections.deque([], PLOT_SIZE)

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        PlotWindow.Ui_MainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.checkBox.clicked.connect(self.setChannel)
        #===============================================================================================================================================================================================
        # win = pg.GraphicsWindow(title="Plot ActiveTwo input")
        # win.resize(1000, 600)
        # win.setWindowTitle('pyqtgraph example: Plotting')
        pg.setConfigOptions(antialias=True)
        #===============================================================================================================================================================================================
        # TODO better do this in QtDesigner
        # l = QtGui.QVBoxLayout()
        # self.ui.tab.setLayout(l)
        plot = pg.PlotWidget(self.ui.graphicsView, name='Plot1')
        plot.resize(800, 540)
        # plot = self.tab.addPlot(title="Updating plot")

        self.curve = plot.plot(pen='y')
        self.signal_buffer = queue.Queue()
        self.reader.activetwo_reader(self.signal_buffer)
        timer = QtCore.QTimer(self)
        self.connect(timer, SIGNAL("timeout()"), self.update)
        timer.start(self.DRAW_INTERVAL)

    def setChannel(self):
        checkbox = self.sender()
        nr = int(checkbox.text()) - 1
        self.CHANNELS[nr] = checkbox.isChecked()

    def update(self):
        self.read_data(self.plot_deque, self.signal_buffer)
        if(len(self.plot_deque) > 0):
            # power spectrum
            sp = np.abs(np.fft.fft(self.plot_deque)) ** 2
            sp[0] = 0  # eliminate DC component
            self.curve.setData(sp)

    def read_data(self, plot_deque, signal_buffer):
        for i in range(int(self.INPUT_RATE * self.CHANNEL_NUMBER * self.DRAW_INTERVAL / 1000.0)):
            data = signal_buffer.get()
            if self.CHANNELS[i % len(self.CHANNELS)] == 1:
                plot_deque.append(data)

# # Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mw = MyPlot()
    mw.show()
    sys.exit(app.exec_())
    # QtGui.QApplication.instance().exec_()

