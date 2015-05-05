import numpy as np
import socket

def activetwo_reader(queue):
    """
    Self-contained function to read BioSemi ActiveTwo device
    Is run as separate process using multiprocessing module
    Thanks: https://batchloaf.wordpress.com/2014/01/17/real-time-analysis-of-data-from-biosemi-activetwo-via-tcpip-using-python/
    """

    # TCP/IP setup
    TCP_IP = '127.0.0.1'  # ActiView is running on the same PC
    TCP_PORT = 778  # This is the port ActiView listens on
    DRAW_BUFFER_SIZE = 1536  # Data packet size (32 channels @ 512Hz)

    # Open socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    print 'BioSemi ActiveTwo reader process is running'

    # The reader process will run until the main process kills it
    while True:

        # Create a 16-sample signal_buffer
        signal_buffer = np.zeros((32, 16))

        # Read the next packet from the network
        # sometimes there is an error and packet is smaller than needed, read until get a good one
        data = []
        while len(data) != DRAW_BUFFER_SIZE:
            data = s.recv(DRAW_BUFFER_SIZE)

        # Extract 16 samples from the packet (ActiView sends them in 16-sample chunks)
        for m in range(16):

            # extract samples for each channel
            for ch in range(32):
                offset = m * 3 * 32 + (ch * 3)

                # The 3 bytes of each sample arrive in reverse order
                sample = (ord(data[offset + 2]) << 16)
                sample += (ord(data[offset + 1]) << 8)
                sample += ord(data[offset])

                # Store sample to signal buffer
                signal_buffer[ch, m] = sample

        signal_buffer = np.transpose(signal_buffer)
        for sample in signal_buffer:
            queue.put(sample)

    print 'BioSemi ActiveTwo reader process has stopped'
