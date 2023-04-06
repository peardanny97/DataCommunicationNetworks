import scipy.stats as stats
import scipy.stats as stats

# Default variables
PKT_SIZE = int(1450)
PKT_NUMS = int(2000)
PROP_TIME = int(10)
START_TIME = 0
END_TIME = 5

# for Debug
SILENT_MODE = True


def transmit(t, size, channel, remained):
    # current available bandwidth (remained bw from prev time + current bw)
    pkt_size = size; time = t
    bw = remained + channel.bw[time]
    num_packets = 0

    # get the number of packets that can be transmitted at time t and remained bw at time t
    num_packets += int(bw / pkt_size)
    remained_bw = int(bw % pkt_size)

    # if current bw is not sufficient
    while num_packets < 1:
        if time == int(END_TIME*1000) - 1: # ms
            break
        time += 1
        bw = remained_bw + channel.bw[time]
        num_packets += int(bw / pkt_size)
        remained_bw = int(bw % pkt_size)

    return time - t + 1, num_packets, remained_bw

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
        self.remained_bw = 0 # available bw from prev timestep

    def admit(self, t, pkts, downlink):
        loss = []; admit = []

        if self.next_available != 0 and self.next_available > t:
            # drop or queue
            for p in pkts:
                if len(self.queued) >= self.queue_length:
                    loss.append(p)
                else:
                    self.queued.append(p)

            return admit, loss

        # downlink admit or not
        if len(self.queued) > 0:
            tx_time, num_packets, remained_bw = transmit(t, PKT_SIZE, downlink, self.remained_bw)
            self.remained_bw = remained_bw
            self.next_available = t + tx_time

            for i in range(0, num_packets):
                p = self.queued.pop(0)
                p.recv_arrival = t + tx_time + PROP_TIME
                admit.append(p)
                # exit if list is empty
                if len(self.queued) == 0:
                    break

        # drop or queue
        for p in pkts:
            if len(self.queued) >=  self.queue_length:
                loss.append(p)
            else:
                self.queued.append(p)


        return admit, loss

class Client():
    def __init__(self, src, dst, bandwidth, pkt_list=[], cc=False):
        self.src = src; self.dst = dst; self.cc = cc

        # variables for senders
        self.pkt_list = pkt_list # packet list for sending
        self.tx_start = 0; # pointer for first transmitted packet (tx_window)
        self.seq = 0 # pointer for next packet sequence (tx_window)
        self.next_available = 0
        self.remained_bw = 0

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
        self.cwnd = 10 # init value
        self.prev_ack = -1 # variable to check dup ack
        self.conservative = False # variable to make congestion control conservative
        self.aggressive = True # variable to make congestion control aggressive
        self.con_cnt = 0
        self.EXP_increase = 1
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
            tx_time, num_packets, remained_bw = transmit(t, PKT_SIZE, self.channel, self.remained_bw)
            self.remained_bw = remained_bw
            for i in range(0, num_packets):
                self.pkt_list[self.seq].start_time = t
                self.pkt_list[self.seq].bs_arrival = t + tx_time + PROP_TIME
                pkts.append(self.pkt_list[self.seq])
                self.seq += 1
                if self.seq == PKT_NUMS:
                    break

            # next available transmit
            self.next_available = t + tx_time # ms
        ############### IMPLEMENT #####################################
        # with congestion control: send packets with cwnd
        # implement your send function with congestion control! (cwnd)
        ###############################################################
        if (self.cc == True):
            tx_time, num_packets, remained_bw = transmit(t, PKT_SIZE, self.channel, self.remained_bw)
            self.remained_bw = remained_bw

            if self.ack_sequence == self.tx_start:  # send complete, increase tx_start
                self.tx_start += 1

            for i in range(0, num_packets):
                if self.seq < self.tx_start + self.cwnd:
                    self.pkt_list[self.seq].start_time = t
                    self.pkt_list[self.seq].bs_arrival = t + tx_time + PROP_TIME

                    if not SILENT_MODE:
                        print("[SEND]: tx start is {} seq is {} cwnd is {}".format(self.tx_start, self. seq, self.cwnd))
                    # for debug

                    pkts.append(self.pkt_list[self.seq])
                    self.seq += 1
                    if self.seq == PKT_NUMS:
                        break
                else:
                    break
            # next available transmit
            self.next_available = t + tx_time  # ms


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
        ack = Packet(0, PKT_SIZE)

        # implement here #
        for p in pkts:
            if not SILENT_MODE:
                print("[RCV]: self.ack is  {} and p.seq is {}".format(self.ack_sequence, p.seq))
                # for debug
            if self.ack_sequence == p.seq - 1:
                self.ack_sequence += 1
                ack.start_time = p.start_time
            # if ack_seq hasn't changed, this means retransmission has occurred
            else:
                self.retx += 1
                if not SILENT_MODE:
                    print("[RETX]: retx is {}".format(self.retx))
                    # for debug



        # ack sequence is receiver's expected packet's num
        ack.ack_seq = self.ack_sequence + 1
        ack.ack_arrival = t + 20


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
            MAX_CWND = 64

            # get acknowledge packets
            next_tx_seq = self.seq
            ack_seq = ack.ack_seq

            if not SILENT_MODE:
                print("[CC]: next sequnce of sender is {}, ack's seq is {}, prev seq is {}".format(next_tx_seq, ack_seq, self.prev_ack))
                # for debug

            if self.conservative:
                if next_tx_seq > ack_seq and next_tx_seq - ack_seq < self.cwnd:  # no need to hurry
                    self.con_cnt += 1
                    if self.prev_ack < ack_seq:
                        self.prev_ack = ack_seq
                        return False

                if not SILENT_MODE:
                    print("[CC]: cwnd is {}, con cnt is {}".format(self.cwnd, self.con_cnt))
                    # for debug
                if self.con_cnt > self.cwnd/2:
                    loss = True

                if loss == True:
                    self.con_cnt = 0
                    self.cwnd = int(max(2, int(self.cwnd / AIMD_decrease)))
                    self.EXP_increase = 1
                else:
                    self.cwnd += 2**self.EXP_increase
                    self.EXP_increase += 1

                # remove ack packets from tx_window
                # restart from unacked packets
                self.tx_start = ack_seq
                self.seq = ack_seq

            elif self.aggressive:
                if self.prev_ack < ack_seq:
                    self.prev_ack = ack_seq
                elif self.prev_ack == ack_seq:  # this means duplicated ack, just ignore it
                    return False

                if next_tx_seq != ack_seq:
                    loss = True

                # AIMD congestion control
                if loss == True:
                    self.cwnd = int(max(4, int(self.cwnd / AIMD_decrease)))
                    self.EXP_increase = 1

                else:
                    self.cwnd = int(min(MAX_CWND, self.cwnd * (2**self.EXP_increase)))
                    self.EXP_increase += 1

                # remove ack packets from tx_window
                # restart from unacked packets
                self.tx_start = ack_seq
                self.seq = ack_seq

            else:

                if next_tx_seq != ack_seq:
                    loss = True

                # AIMD congestion control
                if loss == True:
                    self.cwnd = int(max(2, int(self.cwnd / AIMD_decrease)))

                else:
                    self.cwnd += AIMD_increase

                # remove ack packets from tx_window
                # restart from unacked packets
                self.tx_start = ack_seq
                self.seq = ack_seq

        return False

