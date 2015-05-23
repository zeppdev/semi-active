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
from scipy.signal.signaltools import detrend

class MyPlot(QtGui.QMainWindow, PlotWindow.Ui_MainWindow):

    ALL_STATE = True
    INPUT_RATE = 512.0
    DRAW_INTERVAL = 25
    NR_OF_CHANNELS = 32
    PLOT_SIZE = 512  # in milliseconds

    DUMMY = True  # use dummy reader producing random data
    CHANNEL_SELECTIONS = np.ones(NR_OF_CHANNELS)
    NR_OF_CHANNELS_SELECTED = 32
    reader = dummy_reader if DUMMY else activetwo_reader

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        PlotWindow.Ui_MainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initCheckBoxes()
        
        allButton = QtGui.QPushButton(self.ui.gridLayoutWidget)
        allButton.setObjectName("allButton")
        allButton.setText("All")
        allButton.clicked.connect(self.setAllChannels)
        

        #===============================================================================================================================================================================================
        # win = pg.GraphicsWindow(title="Plot ActiveTwo input")
        # win.resize(1000, 600)
        # win.setWindowTitle('pyqtgraph example: Plotting')
        pg.setConfigOptions(antialias=True)
        plot = pg.PlotWidget(self.ui.graphicsView, name='Plot1')
        plot.resize(950, 540)
        # plot = self.tab.addPlot(title="Updating plot")

        self.curve = plot.plot(pen='y')
        self.signal_buffer = queue.Queue(maxsize = 1)
        self.reader.activetwo_reader(self.signal_buffer)
        timer = QtCore.QTimer(self)
        self.connect(timer, SIGNAL("timeout()"), self.update)
        timer.start(self.DRAW_INTERVAL)
        self.CHANNEL_DEQUES = [None] * self.NR_OF_CHANNELS
        for i in range(self.NR_OF_CHANNELS):
            self.CHANNEL_DEQUES[i] = collections.deque([], self.PLOT_SIZE)
            
    def initCheckBoxes(self):
        for i in range(self.NR_OF_CHANNELS):
            checkbox = QtGui.QCheckBox(self.ui.gridLayoutWidget)
            checkbox.setObjectName("checkBox_" + str(i))
            checkbox.setText(str(i + 1))
            checkbox.clicked.connect(self.setChannel)
            checkbox.setChecked(True)
            self.ui.gridLayout.addWidget(checkbox, i / 8, i % 8, 1, 1)
            
    def setAllChannels(self):
        
        self.ALL_STATE = not self.ALL_STATE

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
        self.read_data(self.CHANNEL_DEQUES, self.signal_buffer)
        #=======================================================================
        # print(self.CHANNEL_DEQUES[0][0])
        # self.curve.setData(self.CHANNEL_DEQUES[0])
        #=======================================================================
        total = np.ndarray((self.NR_OF_CHANNELS, self.INPUT_RATE))
        # power spectrum
        for j in range(self.NR_OF_CHANNELS):
            if self.CHANNEL_SELECTIONS[j] == 1:
                sp = np.abs(np.fft.fft(detrend(self.CHANNEL_DEQUES[j]), 512))
                total[j] = sp.real
        self.curve.setData(np.average(total, 0))
            
            #sp = np.abs(np.fft.fft(self.plot_deque)) ** 2
            #time_step = 1 / self.INPUT_RATE
            #freqs = np.fft.fftfreq(len(self.plot_deque), time_step)
            #idx = np.argsort(freqs)
            #self.curve.setData(freqs[idx], sp[idx])

    def read_data(self, plot_deque, signal_buffer):
        for _ in range(int(self.INPUT_RATE * self.DRAW_INTERVAL / 1000.0)):
            total = 0.0
            data = signal_buffer.get()
            for j in range(self.NR_OF_CHANNELS):
                plot_deque[j].append(data[j])

# # Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mw = MyPlot()
    mw.show()
    sys.exit(app.exec_())
    # QtGui.QApplication.instance().exec_()

