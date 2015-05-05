import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import dummy_reader
import activetwo_reader
import Queue
import collections

DRAW_BUFFER_SIZE = 512  # plot once per second
PLOT_SIZE = 10000  # in milliseconds

DUMMY = True  # use dummy reader producing random data

reader = dummy_reader if DUMMY else activetwo_reader
plot_deque = collections.deque([], PLOT_SIZE)

def update(frames, ax, signal_buffer):
    read_data(plot_deque, signal_buffer)
    ax.clear()
    ax.plot(plot_deque)

def read_data(plot_deque, signal_buffer):
    for i in xrange(DRAW_BUFFER_SIZE):
        plot_deque.append(signal_buffer.get())

def animate():
    fig, ax = plt.subplots()
    # x = np.linspace(0, 1, 512)
    # line, = ax.plot(x)
    signal_buffer = Queue.Queue()
    reader.activetwo_reader(signal_buffer)
    # TODO - use read_data as a generator (yield data)
    ani = animation.FuncAnimation(fig, update, fargs=[ax, signal_buffer], blit=False, interval=100000)
    plt.show()

if __name__ == '__main__':
    animate()

# Calculate DFT ("sp" stands for spectrum)
"""sp = np.fft.ifft(data)
sp[0] = 0  # eliminate DC component

plt.plot(sp.real)
plt.hold(True)
plt.show()"""
