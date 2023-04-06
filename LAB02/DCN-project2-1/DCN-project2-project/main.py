import sys
import numpy as np
import scipy.stats as stats 
import matplotlib.pyplot as plt

# import simulator
from includes.simulator import *

# note: start time should be zero do not change it!
START_TIME = 0 
END_TIME = 5

# bandwidth 
BW_HIGH = MBytes(5)  # 40M bit

# Default variables
PKT_SIZE = int(1450)
PKT_NUMS = int(2000)

######################## IMPLEMENT ###################
# problem 1: need to implement gamma function and plot
# hint: use `time_slice` variable
######################################################
def plot_gamma():
    time_scale = mSecond(1)  # 0.001sec or 1ms
    duration = END_TIME - START_TIME

    # given timeslice for x
    time_slice = np.linspace(START_TIME, END_TIME, int(duration / time_scale))
    uplink_band_width = stats.gamma.pdf(time_slice, a=3, scale=1)
    downlink_band_width = stats.gamma.pdf(time_slice, a=3.5, scale=0.5)

    labels = ["alpha=3, beta=1", "alpha=3.5, beta=2"]
    plt.plot(time_slice, uplink_band_width, label=labels[0])
    plt.plot(time_slice, downlink_band_width, label=labels[1])
    plt.legend()
    plt.show()

    
    # implement gamma function and plot!
    
def simulation():
    # packet generation with # of packets and size
    pkt_list = PacketGenerator(PKT_NUMS, PKT_SIZE)
    
    ############### IMPLEMENT ###########################
    # implement the base station's queue length threshold
    # default is max (length of packet_list)
    # case 1: unlimited threshold without congestion control
    # case 2: unlimited threshold with congestion control
    # case 3: limited threshold with congestion control
    #####################################################
    threshold_case_1 = len(pkt_list) # max
    threshold_case_2 =
    threshold_case_3 =

    # Case 1: simulator without congestion control with unlimited queue
    print("\nsimulation without congestion control")
    sim = Simulator(START_TIME, END_TIME, pkt_list, BW_HIGH, cc=False, threshold=threshold_case_1)
    sim.execute()

    # Case 2: simulator with congestion control with unlimited queue
    print("\nsimulation with congestion control, Case 2")
    sim_cc= Simulator(START_TIME, END_TIME, pkt_list, BW_HIGH, cc=True, threshold=threshold_case_2)
    sim_cc.execute()

    # Case 3: simulator with congestion control with queue length threshold
    print("\nsimulation with congestion control, Case 3")
    sim_cc= Simulator(START_TIME, END_TIME, pkt_list, BW_HIGH, cc=True, threshold=threshold_case_3)
    sim_cc.execute()


    return 0

if __name__ == "__main__":
    plot_gamma()
    # simulation()