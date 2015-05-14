import dummy_reader
import activetwo_reader
import collections
import queue

INPUT_RATE = 512.0
DRAW_INTERVAL = 50
PLOT_SIZE = 500  # in milliseconds
CHANNELS = 32

DUMMY = True  # use dummy reader producing random data


reader = dummy_reader if DUMMY else activetwo_reader
plot_deque = collections.deque([], PLOT_SIZE)


from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

# QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
# mw = QtGui.QMainWindow()
# mw.resize(800,800)

win = pg.GraphicsWindow(title="Plot ActiveTwo input")
win.resize(1000, 600)
win.setWindowTitle('pyqtgraph example: Plotting')
pg.setConfigOptions(antialias=True)

plot = win.addPlot(title="Updating plot")
curve = plot.plot(pen='y')
ptr = 0

def update():
    read_data(plot_deque, signal_buffer)
    # power spectrum
    sp = np.abs(np.fft.fft(plot_deque)) ** 2
    sp[0] = 0  # eliminate DC component
    curve.setData(sp)
signal_buffer = queue.Queue()
reader.activetwo_reader(signal_buffer)
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(DRAW_INTERVAL)

def read_data(plot_deque, signal_buffer):
    for i in range(int(INPUT_RATE * CHANNELS * DRAW_INTERVAL / 1000.0)):
        data = signal_buffer.get()
        if i % 32 == 0:
            plot_deque.append(data)

# # Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    QtGui.QApplication.instance().exec_()
#=======================================================================================================================================================================================================
# def update(frames, line, signal_buffer):
#     start = time.time();
#     read_data(plot_deque, signal_buffer)
#     line.set_ydata(np.append(line.get_ydata(), plot_deque))
#     # print("reading data: " + str(time.time() - start))
#     start = time.time();
#     # print("plotting data: " + str(time.time() - start))
#     return line,
#=======================================================================================================================================================================================================


# if __name__ == '__main__':
#    animate()
# def animate():
