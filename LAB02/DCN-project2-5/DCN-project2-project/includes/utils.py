import numpy as np
import matplotlib.pyplot as plt

from .model import Packet


def Second(time):
    return int(time) 

def mSecond(time):
    return time/1000 

def GBytes(bytes):
    return int(bytes*1024*1024)

def MBytes(bytes):
    return int(bytes*1024*1024)

def KBytes(bytes):
    return int(bytes*1024)

def bytes_to_bits(bytes):
    return bytes*8

class Plotter():
    def __init__(self, x_index, y_index, title, x, y, _y = 0):
        self.title = title
        self.x = x
        self.y = y
        self._y = _y
        self.x_index = x_index
        self.y_index = y_index

def graphPlot(cc, threshold, plot_list):
    _x = int(2)
    _y = int(3)
    figure, axis = plt.subplots(_x, _y, figsize =(15,10))
    
    for p in plot_list:
        if p.title == "network":
            axis[p.x_index, p.y_index].plot(p.x, p.y, label="uplink")
            axis[p.x_index, p.y_index].plot(p.x, p._y, label="downlink")
            axis[p.x_index, p.y_index].set_title(p.title)
            axis[p.x_index, p.y_index].legend()
            continue
        
        axis[p.x_index, p.y_index].plot(p.x, p.y, label=p.title)
        axis[p.x_index, p.y_index].set_title(p.title)
    
    if cc == False:
        plt.savefig("./without_CC_plot.png")
    if cc == True:
        plt.savefig("./with_CC_thresh_" + str(threshold) + "_plot")
    plt.show()

def PacketGenerator(num_packets, pkt_size):
    pkt_list = []
    
    for i in range(0,num_packets):
        pkt_list.append(Packet(i, pkt_size))

    return pkt_list
