import random
import time
import threading

PERIOD_OF_INPUT = 1.0 / 512
CHANNEL_NUMBER = 32
def activetwo_reader(queue):
    readerThread = threading.Thread(target=reader, args=[queue])
    readerThread.start()

def reader(queue):
    while True:
        start = time.time();
        for i in range(CHANNEL_NUMBER):
            # simulate periodicity, ought to be a (reverse?) sawtooth
            periodic_bias = (64 - (i / CHANNEL_NUMBER) % 64) * 0.02

            # should show up in power spectrum
            if (i / CHANNEL_NUMBER % 5000 < 1000):
                periodic_bias *= 0.1
            # simulate higher channels having stronger signal
            channel_bias = (i % CHANNEL_NUMBER) * 0.05
            queue.put(random.gauss(0.75 + channel_bias + periodic_bias, 0.25))
        diff = time.time() - start
        # print("writing data: "+ str(diff))
        if(diff < PERIOD_OF_INPUT):
            time.sleep(PERIOD_OF_INPUT - diff)
