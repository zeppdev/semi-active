import random
import time
import threading

PERIOD_OF_INPUT = 1.0 / 512
CHANNELS = 32
def activetwo_reader(queue):
    readerThread = threading.Thread(target=reader, args=[queue])
    readerThread.start()

def reader(queue):
    while True:
        start = time.time();
        for i in range(CHANNELS):
            queue.put(random.uniform(0.0, 1.5))
        diff = time.time() - start
        print("writing data: "+ str(diff))
        if(diff < PERIOD_OF_INPUT):
            time.sleep(PERIOD_OF_INPUT - diff)
