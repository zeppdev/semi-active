import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import connector.dummy_reader as dummy_reader
import activetwo_reader
import queue
import collections
import time

INPUT_RATE = 512.0  # plot once per second
DRAW_INTERVAL = 50
PLOT_SIZE = 10000  # in milliseconds
CHANNELS = 32

DUMMY = True  # use dummy reader producing random data


reader = dummy_reader if DUMMY else activetwo_reader
plot_deque = collections.deque([], PLOT_SIZE)

def update(frames, ax, signal_buffer):
    start = time.time();
    read_data(plot_deque, signal_buffer)
    print("reading data: "+str(time.time() - start))
    start = time.time();
    ax.clear()
    line,  = ax.plot(plot_deque)
    print("plotting data: "+str(time.time() - start))
    return line,

def read_data(plot_deque, signal_buffer):
    for i in range(int(INPUT_RATE * CHANNELS * DRAW_INTERVAL/1000.0)):
        plot_deque.append(signal_buffer.get())

def animate():
    fig, ax = plt.subplots()
    # x = np.linspace(0, 1, 512)
    # line, = ax.plot(x)
    signal_buffer = queue.Queue()
    reader.activetwo_reader(signal_buffer)
    # TODO - use read_data as a generator (yield data)
    ani = animation.FuncAnimation(fig, update, fargs=[ax, signal_buffer], blit=True, interval=DRAW_INTERVAL)
    plt.show()

if __name__ == '__main__':
    animate()

# Calculate DFT ("sp" stands for spectrum)
"""sp = np.fft.ifft(data)
sp[0] = 0  # eliminate DC component

plt.plot(sp.real)
plt.hold(True)
plt.show()"""
