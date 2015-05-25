import random
import time
import threading
import math

PERIOD_OF_INPUT = 1.0 / 512
CHANNEL_NUMBER = 32
def activetwo_reader(queue):
    readerThread = threading.Thread(target=reader, args=[queue])
    readerThread.start()

def reader(queue):
    # TEST
    a = 2
    f = 50
    f2 = 100
    f3 = 150
    pi2 = math.pi * 2.0
    n = 0
    count = 0;
    print("frequencies = " , f , f2 , f3)
    print("amplitude = " + str(a))
    while True:
        sample = [None] * CHANNEL_NUMBER
        start = time.time();
        n = (n + 1) % 512
        count = (count + 1) % 2048
        for i in range(CHANNEL_NUMBER):
            t = float(n) / 512 * pi2
            channel_bias = 1  # (i % CHANNEL_NUMBER) * 0.05
            fn = a * math.sin(f * t) * channel_bias
            fn2 = a * math.sin(f2 * t) * channel_bias
            fn3 = a * math.sin(f3 * t) * channel_bias

            if count / 1024 < 1:
                fn *= 2
            else:
                fn2 *= 2

            if i != CHANNEL_NUMBER:
                sample[i] = fn + fn2 + fn3  # + random.gauss(2, 0.25)
            else:
                sample[i] = random.gauss(2, 0.25)

        queue.put(sample)
        diff = time.time() - start
        # print("writing data: "+ str(diff))
        if(diff < PERIOD_OF_INPUT):
            time.sleep(PERIOD_OF_INPUT - diff)
