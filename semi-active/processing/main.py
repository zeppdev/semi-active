import collections

from PyQt4 import QtCore, QtGui
import numpy as np
import pyqtgraph as pg

import sys
from connector import activetwo_reader, dummy_reader
from ui import PlotWindow
from ui.PlotWindow import Ui_MainWindow
import queue
from PyQt4.QtCore import SIGNAL

class MyPlot(QtGui.QMainWindow, PlotWindow.Ui_MainWindow):
    INPUT_RATE = 512.0
    DRAW_INTERVAL = 1000
    NR_OF_CHANNELS = 32
    PLOT_SIZE = 1000  # in milliseconds

    DUMMY = True  # use dummy reader producing random data
    CHANNEL_SELECTIONS = np.ones(NR_OF_CHANNELS)
    NR_OF_CHANNELS_SELECTED = 32
    reader = dummy_reader if DUMMY else activetwo_reader
    plot_deque = collections.deque([], PLOT_SIZE)


    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        PlotWindow.Ui_MainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initCheckBoxes()

        #===============================================================================================================================================================================================
        # win = pg.GraphicsWindow(title="Plot ActiveTwo input")
        # win.resize(1000, 600)
        # win.setWindowTitle('pyqtgraph example: Plotting')
        pg.setConfigOptions(antialias=True)
        plot = pg.PlotWidget(self.ui.graphicsView, name='Plot1')
        plot.resize(1000, 540)
        # plot = self.tab.addPlot(title="Updating plot")

        self.curve = plot.plot(pen='y')
        self.signal_buffer = queue.Queue()
        self.reader.activetwo_reader(self.signal_buffer)
        timer = QtCore.QTimer(self)
        self.connect(timer, SIGNAL("timeout()"), self.update)
        timer.start(self.DRAW_INTERVAL)

    def initCheckBoxes(self):
        for i in range(self.NR_OF_CHANNELS):
            checkbox = QtGui.QCheckBox(self.ui.gridLayoutWidget)
            checkbox.setObjectName("checkBox_" + str(i))
            checkbox.setText(str(i + 1))
            checkbox.clicked.connect(self.setChannel)
            checkbox.setChecked(True)
            self.ui.gridLayout.addWidget(checkbox, i / 8, i % 8, 1, 1)

    def setChannel(self):
        checkbox = self.sender()
        channel = int(checkbox.text()) - 1
        checked = checkbox.isChecked()
        self.CHANNEL_SELECTIONS[channel] = checked
        if checked:
            self.NR_OF_CHANNELS_SELECTED += 1
        else:
            self.NR_OF_CHANNELS_SELECTED -= 1

    def update(self):
        self.read_data(self.plot_deque, self.signal_buffer)
        if(len(self.plot_deque) > 0):
            # power spectrum
            sp = np.abs(np.fft.rfft(self.plot_deque)) ** 2
            time_step = 1 / self.INPUT_RATE
            freqs = np.fft.fftfreq(len(self.plot_deque), time_step)
            # print(freqs)
            idx = np.argsort(freqs)
            # print(idx)
            self.curve.setData(freqs[idx], sp[idx])

    def read_data(self, plot_deque, signal_buffer):
        for _ in range(int(self.INPUT_RATE * self.DRAW_INTERVAL / 1000.0)):
            total = 0.0
            for j in range(self.NR_OF_CHANNELS):
                data = signal_buffer.get()
                if self.CHANNEL_SELECTIONS[j] == 1:
                    total += data
            if(self.NR_OF_CHANNELS_SELECTED > 0):
                plot_deque.append(total / self.NR_OF_CHANNELS_SELECTED)

# # Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mw = MyPlot()
    mw.show()
    sys.exit(app.exec_())
    # QtGui.QApplication.instance().exec_()

