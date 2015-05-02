import random
import numpy as np
import matplotlib.pyplot as plt
from threading import Timer
import time
import threading

import Queue

PERIOD_OF_INPUT = 1 / 512;  # 512 Hz
def activetwo_reader(queue):
    readerThread = threading.Thread(target=reader, args=[queue]);
    readerThread.start()

def reader(queue):
    while True:
        start = time.time();
        queue.put(random.getrandbits(24))
        diff = time.time() - start
        if(diff < PERIOD_OF_INPUT):
            time.sleep(PERIOD_OF_INPUT - diff)

BUFFER_SIZE = 512  # plot once per second

signal_buffer = Queue.Queue()
activetwo_reader(signal_buffer)

for i in range(1):
    data = []
    while len(data) != BUFFER_SIZE:
        data.append(signal_buffer.get())

    # Calculate DFT ("sp" stands for spectrum)
    sp = np.fft.fft(data)
    sp[0] = 0  # eliminate DC component

    # Plot spectrum
    print("Plotting data")
    plt.plot(sp.real)
    plt.hold(True)
    plt.show()
