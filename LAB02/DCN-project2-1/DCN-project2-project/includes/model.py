import scipy.stats as stats 

# Default variables
PKT_SIZE = int(1450)
PKT_NUMS = int(2000)
PROP_TIME = int(10)

def transmit(t, seq_start, size, channel):
    start = seq_start; pkt_size = size; time = t

    while pkt_size > 0:
        pkt_size -= channel.bw[time]
        time += 1
    
    # return tx time for a packet and next sequence of packets to send next
    return time - t, start + 1

class Channel():
    def __init__(self, bandwidth):
        self.bw = bandwidth
        self.prop = PROP_TIME # ms

class Packet():
    def __init__(self, seq, size):
        # TCP header used in this simulation
        self.src = ""
        self.dst = ""
        self.seq = seq # sequence number of this packets
        self.ack_seq = 0 # ack sequence
        
        # used for only simulation, not offical header
        self.start_time = 0 # send start time 
        self.ack_arrival = 0 # ack arrival time
        self.bs_arrival = 0 # bs arrival time
        self.recv_arrival = 0 # receiver arrival time

        ################ IMPLEMENT ##################### 
        # define your own observed data here if needed #

        ################################################

class BaseStation():
    def __init__(self, name, threshold):
        self.name = name
        self.queue_length = threshold
        self.queued = []
        self.next_available = 0

    def admit(self, t, pkts, downlink):
        loss = []; admit = []

        # if bs transmission is busy, only queue packets (not transmit)
        if t < self.next_available:
            # drop or queue
            for p in pkts:
                if len(self.queued) >= self.queue_length:
                    loss.append(p)
                else:
                    self.queued.append(p)

            return admit, loss

        # downlink admit or not
        if len(self.queued) > 0:
            p = self.queued.pop(0)
            tx_time, _ = transmit(t, p.seq, PKT_SIZE, downlink)
            p.recv_arrival = t + tx_time + PROP_TIME
            admit.append(p)

            # next available time
            self.next_available = t + tx_time
        
        # drop or queue
        for p in pkts:
            if len(self.queued) >=  self.queue_length:
                loss.append(p)
            else:
                self.queued.append(p)
        
        # return transmit list and dropped packet
        return admit, loss

class Client():
    def __init__(self, src, dst, bandwidth, pkt_list=[], cc=False):
        self.src = src; self.dst = dst; self.cc = cc

        # variables for senders
        self.pkt_list = pkt_list # packet list for sending
        self.tx_start = 0; # pointer for first transmitted packet (tx_window)
        self.seq = 0 # pointer for next packet sequence (tx_window)
        self.next_available = 0

        # variables for clients
        self.channel = Channel(bandwidth)
        
        # variables for receivers
        self.ack_sequence = -1 # init
        self.retx = 0
        
        ############################### IMPLEMENT ##############################################
        # implement your own congestion control with parameters!
        # note 1: you can use any variable from Packet() class
        # note 2: you may add additional variable into PACKET() class
        # note 3: you can use any additional parameter for congestion control e.g. avgRTT, etc.
        # note 4: you can adjust the current init values 
        ########################################################################################
        self.avgRTT = 4 * PROP_TIME # RTT for 2 * (uplink.prop + downlink.prop) 
        self.cwnd = 4 # init value
        # self.estimatedRTT = 0
    

    ############## IMPLEMENT ###############################
    # implement the send function of sender!
    # your job is to send the packets in terms of cwnd
    # note 1: sending without congestion control is provided
    #########################################################
    def send(self, t):
        # transmission is busy
        if t < self.next_available:
            return [] # empty list
        
        # transmission done
        if self.seq == PKT_NUMS:
            return [] # empty list
        
        # packets to transmit
        pkts = []

        # next packet pointer init
        next_seq = 0
        
        # without congestion control: send packets with max bandwidth
        if (self.cc == False):
            tx_time, next_seq = transmit(t, self.seq, PKT_SIZE, self.channel)
            self.pkt_list[self.seq].start_time = t
            self.pkt_list[self.seq].bs_arrival = t + tx_time + PROP_TIME
            pkts.append(self.pkt_list[self.seq])
            
            # next available transmit
            self.next_available = t + tx_time # ms

            # point next sequence
            self.seq = next_seq
        
        ############### IMPLEMENT #####################################
        # with congestion control: send packets with cwnd
        # implement your send function with congestion control! (cwnd)
        ###############################################################
        # if (self.cc == True):
        
        
        
        ###############################################################




        # return packet lists
        return pkts


    #################### IMPLEMENT recv() #######################
    # naive TCP ack generation is followed  
    # implement your own ack generation
    # note 1: you can add additional variables from observed data
    # note 2: you can generate advanced ack
    # note 3: please refer chapter 9. Transport Layer
    #############################################################
    def recv(self, t, pkts):
        if len(pkts) == 0:
            return False # no acks
        
        # generate ack packet
        # cumulative ack send only one acknowledgement
        ack = Packet()

        # implement here #


        # return ack
        return ack

    ################## IMPLEMENT congestion control #################
    # naive congestion control is followed
    # implement your own congestion control using the ack packet!
    ###################################################################
    def congestion_control(self, t, ack):
        loss = False

        if ack == False:
            return False
        
        # return true if all the packets are transmitted to receiver
        if ack.ack_seq == PKT_NUMS:
            return True
        
        # without congestion control, simply measure avgRTT
        if self.cc == False:
            ack_seq = ack.ack_seq
            sum = 0
            for i in range(self.tx_start, ack_seq):
                sum += ack.ack_arrival - ack.start_time

            acked_packets = ack_seq - self.tx_start

            if acked_packets:
                self.avgRTT = int(sum / acked_packets)
            
            self.tx_start = ack_seq
            
            return False

        ########## IMPLEMENT ####################
        # naive congestion control are following
        # implement your own congestion control
        #########################################
        if self.cc == True:
            ack_seq = ack.ack_seq
            sum = 0
            for i in range(self.tx_start, ack_seq):
                sum += ack.ack_arrival - ack.start_time
                
            acked_packets = ack_seq - self.tx_start
            
            if acked_packets:
                self.avgRTT = int(sum / acked_packets)
            
            # parameter for cwnd
            AIMD_increase = 2
            AIMD_decrease = 4

            # get acknowledge packets
            next_tx_seq = self.seq
            ack_seq = ack.ack_seq
        
            if next_tx_seq != ack_seq:
                loss = True
            
            # AIMD congestion control
            if loss == True:
                self.cwnd = int(max(2, int(self.cwnd/AIMD_decrease)))
            else:
                self.cwnd += AIMD_increase

            # remove ack packets from tx_window
            # restart from unacked packets
            self.tx_start = ack_seq
            self.seq = ack_seq

        return False

