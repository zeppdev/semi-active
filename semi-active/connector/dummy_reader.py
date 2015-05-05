import random
import time
import threading

PERIOD_OF_INPUT = 1.0 / 512;  # 1 / data rate
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
