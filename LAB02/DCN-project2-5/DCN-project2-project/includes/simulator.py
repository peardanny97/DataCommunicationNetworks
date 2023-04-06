import numpy as np
import matplotlib.pyplot as plt

from .model import *
from .utils import *

# note: start time should be zero do not change it!
START_TIME = 0 
END_TIME = 5

class Simulator():
    def __init__(self, start_time, end_time, packet_list, BW, cc, threshold):
        self.global_time = start_time
        self.global_end = end_time * 1000 # ms
        self.cc = cc
        self.threshold = threshold
        _duration = end_time - start_time
        
        # time slice for x
        _time_slice = np.linspace(start_time, end_time, int(_duration/mSecond(1)))
        
        ###################### IMPLEMENT #############################
        # implement bandwidth with gamma distribution
        # hint 1: use gamma distribution method in problem 1
        # hint 2: using _time_slice, alpha, beta and also argument BW
        ##############################################################
        uplink_alpha = 3; uplink_beta =1
        downlink_alpha = 3.5; downlink_beta = 2
        uplink = stats.gamma.pdf(_time_slice, a=uplink_alpha, scale=uplink_beta)
        downlink = stats.gamma.pdf(_time_slice, a=downlink_alpha, scale=downlink_beta)
        self.uplink_bw = [x * BW for x in uplink]
        self.downlink_bw = [x * BW for x in downlink]


        # define sender, receiver, and base station for simulation
        self.bs = BaseStation("bs", self.threshold)
        self.senders = Client(src = "send", dst="recv", bandwidth = self.uplink_bw, pkt_list = packet_list, cc=cc)
        self.receivers = Client(src = "recv", dst="send", bandwidth = self.downlink_bw, cc=cc)
        
        # member variables for logging
        self.queue_length = []
        self.avgRTT = []
        self.cwnd = []
        self.loss = []
        self.retx = []

        # member variable for uplink & downlink simulation
        self.up_ongoing = []
        self.down_ongoing = [] 
        self.ack_ongoing = []

    def timer(self):
        self.global_time += int(1) # ms
    
    def execute(self):
        while (self.global_time < self.global_end):
            # 1. sender send pkts to bs at time t
            pkts = self.senders.send(self.global_time)

            # 2. return the pkts to bs when bs_arrival time == t
            uplink_arrivals = self.uplink_ongoing(self.global_time, pkts)
            
            # 3. bs admit packets from sender and send pkts to receiver  
            admit, loss = self.bs.admit(self.global_time, uplink_arrivals, self.receivers.channel)
            
            # 4. return the admitted pkts to receiver when recv_arrival == t
            downlink_arrivals = self.downlink_ongoing(self.global_time, admit)
            
            # 3. receiver receives pkts from bs and send acks to sender
            acks = self.receivers.recv(self.global_time, downlink_arrivals)

            # 4. sender get acks from receiver 
            ack_arrivals = self.acknowledge_ongoing(self.global_time, acks)

            # 5. sender process's congestion control
            done = self.senders.congestion_control(self.global_time, ack_arrivals)
            
            if done == True:
                print("simulation done at time: ", mSecond(self.global_time))
            
            # logging
            self.logging("Loss", len(loss))
            self.logging("RTT", self.senders.avgRTT)
            self.logging("CWND", self.senders.cwnd)
            self.logging("Queue Length", len(self.bs.queued))
            self.logging("retx", self.receivers.retx)
            
            # global timer
            self.timer()
        
        print("# of transmitted packets: ", self.receivers.ack_sequence + 1)

        
        _duration = END_TIME - START_TIME
        _time_slice = np.linspace(START_TIME, END_TIME, int(_duration/mSecond(1)))
        
        plot_list= []
        plot_list.append(Plotter(0, 0, "Loss", _time_slice, self.loss))
        plot_list.append(Plotter(0, 1, "Queue Length", _time_slice, self.queue_length))
        plot_list.append(Plotter(0, 2, "avgRTT", _time_slice, self.avgRTT))
        plot_list.append(Plotter(1, 0, "retx_cdf", _time_slice, self.retx))
        plot_list.append(Plotter(1, 1, "network", _time_slice, self.uplink_bw, self.downlink_bw))
        plot_list.append(Plotter(1, 2, "CWND", _time_slice, self.cwnd))
        
        graphPlot(self.cc, self.threshold, plot_list)

        return
    
    def uplink_ongoing(self, t, pkts):
        arrival_list = []
        
        for u in pkts:
            self.up_ongoing.append(u)
        
        tmp = self.up_ongoing.copy()

        for p in self.up_ongoing:
            if p.bs_arrival == t:
                arrival_list.append(p)
                tmp.remove(p)
            else:
                continue
        
        self.up_ongoing = tmp

        return arrival_list
    
    def downlink_ongoing(self, t, pkts):
        arrival_list = []

        for d in pkts:
            self.down_ongoing.append(d)
        
        tmp = self.down_ongoing.copy()

        for p in self.down_ongoing:
            if p.recv_arrival == t:
                arrival_list.append(p)
                tmp.remove(p)
            else:
                continue
        self.down_ongoing = tmp

        return arrival_list
    
    def acknowledge_ongoing(self, t, ack):
        if ack == False and len(self.ack_ongoing) == 0:
            return False

        if ack != False:
            self.ack_ongoing.append(ack)
        
        ack = False
        
        for p in self.ack_ongoing:
            if p.ack_arrival == t:
                ack = p
            else:
                continue
        
        return ack

    def logging(self, x, data):
        if x == "Loss":
            self.loss.append(data)
        if x == "Queue Length":
            self.queue_length.append(data)
        if x == "RTT":
            self.avgRTT.append(data)
        if x == "CWND":
            self.cwnd.append(data)
        if x == "retx":
            self.retx.append(data)