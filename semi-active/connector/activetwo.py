#
# test_plot.py - Written by Jack Keegan
# Last updated 16-1-2014
#
# This short Python program receives data from the
# BioSemi ActiveTwo acquisition system via TCP/IP.
#
# Each packet received contains 16 3-byte samples
# for each of 8 channels. The 3 bytes in each sample
# arrive in reverse order (least significant byte first)
#
# Samples for all 8 channels are interleaved in the packet.
# For example, the first 24 bytes in the packet store
# the first 3-byte sample for all 8 channels. Only channel
# 1 is used here - all other channels are discarded.
#
# The total packet size is 8 x 16 x 3 = 384.
# (That's channels x samples x bytes-per-sample)
#
# 512 samples are accumulated from 32 packets.
# A DFT is calculated using numpy's fft function.
# the first DFT sample is set to 0 because the DC
# component will otherwise dominates the plot.
# The real part of the DFT (all 512 samples) is plotted.
# That process is repeated 50 times - the same
# matplotlib window is updated each time.
#

import numpy  # Used to calculate DFT
import matplotlib.pyplot as plt  # Used to plot DFT
import socket  # used for TCP/IP communication
import random

# TCP/IP setup
TCP_IP = '127.0.0.1'  # ActiView is running on the same PC
TCP_PORT = 778  # This is the port ActiView listens on
DRAW_BUFFER_SIZE = 384  # Data packet size (depends on ActiView settings)

# Open socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((TCP_IP, TCP_PORT))

# Create a 512-sample signal_buffer (arange fills the array with
# values, but these will be overwritten; We're just using arange
# to give us an array of the right size and type).
signal_buffer = numpy.arange(512)

# Calculate spectrum 50 times
for i in range(50):
    # Parse incoming frame data
    print("Parsing data")

    # Data buffer index (counts from 0 up to 512)
    buffer_idx = 0

    # collect 32 packets to fill the window
    for n in range(32):
        # Read the next packet from the network
        data = random.getrandbits(24)

        # Extract 16 channel 1 samples from the packet
        for m in range(16):
            offset = m * 3 * 8
            # The 3 bytes of each sample arrive in reverse order
            sample = (ord(data[offset + 2]) << 16)
            sample += (ord(data[offset + 1]) << 8)
            sample += ord(data[offset])
            # Store sample to signal buffer
            signal_buffer[buffer_idx] = sample
            buffer_idx += 1

    # Calculate DFT ("sp" stands for spectrum)
    sp = numpy.fft.fft(signal_buffer)
    sp[0] = 0  # eliminate DC component

    # Plot spectrum
    print("Plotting data")
    plt.plot(sp.real)
    plt.hold(False)
    plt.show()

# Close socket
s.close()
