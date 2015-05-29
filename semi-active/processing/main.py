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
from functools import partial


class MyPlot(QtGui.QMainWindow, PlotWindow.Ui_MainWindow):
    CHECKBOX_TOGGLE = True
    INPUT_RATE = 512
    DRAW_INTERVAL = 25
    NR_OF_CHANNELS = 32
    TIME_PLOT_SIZE = 128  # in milliseconds

    DUMMY = True  # use dummy reader
    reader = dummy_reader if DUMMY else activetwo_reader


    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        PlotWindow.Ui_MainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        pg.setConfigOptions(antialias=True)

        # init UI
        self.initTab(self.ui.tab, self.ui.gridLayout, self.ui.allButton)
        self.initTab(self.ui.tab_2, self.ui.gridLayout_2, self.ui.allButton_2)
        self.initSpinBoxes()

        self.ui.tab.plot = pg.PlotWidget(self.ui.graphicsView, name='Plot1')
        self.ui.tab_2.plot = pg.PlotWidget(self.ui.graphicsView_2, name='Plot2')
        self.ui.tab.plot.resize(950, 540)
        self.ui.tab_2.plot.resize(950, 540)
        self.ui.tab.plot.curve = self.ui.tab.plot.plot(pen='y')
        self.ui.tab_2.plot.curve = self.ui.tab_2.plot.plot(pen='y', y=[0] * self.TIME_PLOT_SIZE)

        # init buffers
        self.ui.tab.CHANNEL_DEQUES = [None] * self.NR_OF_CHANNELS
        for i in range(self.NR_OF_CHANNELS):
            self.ui.tab.CHANNEL_DEQUES[i] = collections.deque([], self.INPUT_RATE)

        self.ui.tab_2.CHANNEL_DEQUES = [None] * self.NR_OF_CHANNELS
        for i in range(self.NR_OF_CHANNELS):
            self.ui.tab_2.CHANNEL_DEQUES[i] = collections.deque([], self.TIME_PLOT_SIZE)

        # init timer and signals
        self.signal_buffer = queue.Queue(maxsize=1000)
        self.reader.activetwo_reader(self.signal_buffer)
        timer = QtCore.QTimer(self)

        self.connect(timer, SIGNAL("timeout()"), partial(self.update, [self.updatePlot1, self.updatePlot2]))

        timer.start(self.DRAW_INTERVAL)

    def initTab(self, tab, layout, button):
        tab.CHANNEL_SELECTIONS = np.ones(self.NR_OF_CHANNELS)
        tab.CHECKBOXES = [None] * self.NR_OF_CHANNELS
        tab.NR_OF_CHANNELS_SELECTED = self.NR_OF_CHANNELS
        tab.CHECKBOX_TOGGLE = self.CHECKBOX_TOGGLE
        self.initCheckBoxes(tab, layout, button)

    def initCheckBoxes(self, tab, layout, button):
        for i in range(self.NR_OF_CHANNELS):
            checkbox = QtGui.QCheckBox(tab)
            checkbox.setObjectName("checkBox_" + str(tab) + "_" + str(i))
            checkbox.setText(str(i + 1))
            checkbox.clicked.connect(partial(self.checkBoxClickedCallback, tab))
            checkbox.setChecked(tab.CHECKBOX_TOGGLE)
            tab.CHECKBOXES[i] = checkbox
            layout.addWidget(checkbox, i / 8, i % 8, 1, 1)
        button.clicked.connect(partial(self.setAllChannels, tab))

    def initSpinBoxes(self):
        self.ui.spinBox.setRange(1, 255)
        self.ui.spinBox_2.setRange(1, 255)
        self.ui.spinBox.setValue(1)
        self.ui.spinBox_2.setValue(255)
        self.ui.spinBox.valueChanged.connect(self.spinBoxCallback)
        self.ui.spinBox_2.valueChanged.connect(self.spinBox2Callback)

    def spinBoxCallback(self):
        self.ui.spinBox_2.setMinimum(self.sender().value() + 1)

    def spinBox2Callback(self):
        self.ui.spinBox.setMaximum(self.sender().value() - 1)

    def setAllChannels(self, tab):
        tab.CHECKBOX_TOGGLE = not tab.CHECKBOX_TOGGLE
        for i in range(len(tab.CHECKBOXES)):
            tab.CHECKBOXES[i].setChecked(tab.CHECKBOX_TOGGLE)
            self.setChannel(tab, i, tab.CHECKBOX_TOGGLE)

    # TODO - get tab from checkbox itself
    def checkBoxClickedCallback(self, tab):
        checkbox = self.sender()
        channel = int(checkbox.text()) - 1
        checked = checkbox.isChecked()
        self.setChannel(tab, channel, checked)

    def setChannel(self, tab, channel, checked):
        tab.CHANNEL_SELECTIONS[channel] = checked
        tab.NR_OF_CHANNELS_SELECTED = np.count_nonzero(tab.CHANNEL_SELECTIONS)
        
        size = len(tab.CHANNEL_DEQUES[0])
        for i in range(len(tab.CHANNEL_DEQUES)):
            tab.CHANNEL_DEQUES[i] = collections.deque([], size)

    def update(self, functions):
        idx = self.ui.tabWidget.currentIndex()
        tab = self.ui.tabWidget.currentWidget()
            # power spectrum
        self.read_data(tab.CHANNEL_DEQUES, self.signal_buffer)
        if tab.NR_OF_CHANNELS_SELECTED > 0:
            functions[idx](tab)

            # sp = np.abs(np.fft.fft(self.plot_deque)) ** 2
            # time_step = 1 / self.INPUT_RATE
            # freqs = np.fft.fftfreq(len(self.plot_deque), time_step)
            # idx = np.argsort(freqs)
            # self.curve.setData(freqs[idx], sp[idx])

    def updatePlot1(self, tab):
        fft_powers = self.fftByChannel(tab)
        average = np.average(fft_powers, 0)
        tab.plot.curve.setData(average)


    def updatePlot2(self, tab):
        fft_powers = self.fftByChannel(tab)
        _, yData = tab.plot.curve.getData()
        averages = np.average(fft_powers, 0)
        # print(np.shape(averages))
        top = self.ui.spinBox.value()
        bottom = self.ui.spinBox_2.value()
        yData = np.append(yData, np.average(averages[top:bottom]))
        # print(np.average(fft_powers[top:bottom]))
        tab.plot.curve.setData(y=yData[-self.TIME_PLOT_SIZE:])

    def read_data(self, plot_deque, signal_buffer):
        for _ in range(int(self.INPUT_RATE * self.DRAW_INTERVAL / 1000.0)):
            data = signal_buffer.get()
            for j in range(self.NR_OF_CHANNELS):
                plot_deque[j].append(data[j])
    
    def fftByChannel(self, tab):
        fft_powers = np.ndarray((self.NR_OF_CHANNELS, self.INPUT_RATE / 2 - 1))
        for j in range(self.NR_OF_CHANNELS):
            if tab.CHANNEL_SELECTIONS[j] == 1:
                sp = np.abs(np.fft.fft(detrend(tab.CHANNEL_DEQUES[j]), 512))
                sp = sp[1:256]
                sp_real = sp.real
                fft_powers[j] = 10*np.log10(sp_real.clip(min=0.000001))
                #fft_powers[j] = sp_real.clip(min=0.000001)
            else:
                # TODO - this is a hack to not get all-zero arrays in the result
                fft_powers[j] = [0.0000001]*255
        return fft_powers
# helpers
def reject_outliers(data, m=2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / mdev if mdev else 0.
    return data[s < m]

# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mw = MyPlot()
    mw.show()
    sys.exit(app.exec_())
