from util import *
import socket
import select
import time
import random

import threading

LOCALHOST = "127.0.0.1"
MINIMUM_TIME = 25
TIMER_RANGE = 10
INFINITY = 16


class Router(object):
    """docstring for Router."""

    def __init__(self, router_id):
        """initializes the router """
        self.router_id = router_id
        self.routing_table = {}
        self.input_sockets = []
        self.output_port = []
        self.portDict = {}
        self.lock = threading.Lock()

    def add_port_dict(self, port, router_id):
        """add a mapping from output port number to router id"""
        self.portDict[port] = router_id

    def add_input_socket(self, port_num):
        """create a input socket to the router"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((LOCALHOST, port_num))
        self.input_sockets.append(sock)

    def add_output_port(self, output_port_number):
        """add a output port number"""
        self.output_port.append(output_port_number)

    def add_routing_table(self, metric, dest_id, next_hop, timeout=0, firsttime=True):
        """add an entry to routing table, firsttime is a flag used for setting
        route's timeout value"""
        metric = min(INFINITY, metric)
        self.routing_table[dest_id] = [metric, next_hop, timeout, firsttime]

    def generate_packet(self, output_port):
        """generate a RIP packet from routing table, poisons the router to
        output_port"""
        # generate Rip_packet object
        # add each entry in routing table to packet
        # call dump in packet
        rip_packet = Rip_packet(self.router_id)

        # add information about it self
        rip_packet.add_entry([0, 0, self.router_id, 0, self.router_id, 0])

        for dest_id in self.routing_table.keys():
            try:
                metric, next_hop, timeout, _ = self.routing_table[dest_id]
            except ValueError as e:
                print(self.routing_table[dest_id])
                continue
            # if neighbour is next_hop to dest, split horizon
            if self.portDict[output_port] == next_hop:
                if dest_id != next_hop:  # ??
                    metric = INFINITY  # poision reverse
                    # print("implemented split horizon with poision reverse, current router is",
                    #       self.router_id, "next_hop is", next_hop, "dest is", dest_id)
            # print(metric, next_hop, timeout)
            entry = [0, 0, dest_id, 0, next_hop, metric]

            # print(entry)
            rip_packet.add_entry(entry)
            # print("command",rip_packet.command,"version",rip_packet.version,"entry table",rip_packet.entry_table)
        # print(rip_packet)
        # print("packet sent", self.portDict[output_port])
        # print(rip_packet)
        rip_packet = rip_packet.dump()
        # print("dumped pack",rip_packet)
        return rip_packet

    def periodic_update(self):
        """thread to update every 30+-5 seconds with uniform distribution"""
        wait_time = MINIMUM_TIME + random.uniform(0, TIMER_RANGE)
        self.send()
        threading.Timer(wait_time, self.periodic_update).start()

    def update_Timer(self):
        """increments the timeout field of each entry by 1 every second
        also checks for timeout and garbage collection"""
        self.lock.acquire()
        for dest in self.routing_table.keys():
            # increment timeout by 1
            self.routing_table[dest][2] += 1
            if self.routing_table[dest][2] == 180:
                self.set_infinity(dest)
            elif self.routing_table[dest][2] == 120 and self.routing_table[dest][0] == INFINITY:
                self.remove_entry(dest)
        self.lock.release()
        threading.Timer(1, self.update_Timer).start()

    def set_infinity(self, dest):
        """sets dest in routing table's value to inifinity"""
        self.routing_table[dest][0] = INFINITY
        self.routing_table[dest][2] = 0
        self.send()  # notify neighbours about the change

    def remove_entry(self, dest):
        """removes the entry with dest due to garbage collection"""
        self.routing_table.pop(dest)
        print("garbage expired, remove entry", dest)

    def disp(self):
        """displays the routing table every 10 seconds"""
        self.print_routing_table()
        threading.Timer(10, self.disp).start()

    def receive_data(self, socket):
        """receives data from socket and does validation check on header
        raises general exception if check doesnt pass"""
        data, addr = socket.recvfrom(1024)
        rip_packet = load(data)

        # validation checks
        if rip_packet.command != 2:
            raise Exception("Incorrect command in rip header: ",
                            rip_packet.command)

        if rip_packet.version != 2:
            raise Exception("Incorrect version in rip header: ",
                            rip_packet.version)

        # print("packet loaded")
        # print(rip_packet)

        # return the entry table
        return rip_packet.router_id, rip_packet.entry_table

    def updat_routing_table(self, dest, potential_metric, router_id):
        # if not in routing table
        if dest not in self.routing_table.keys():
            if potential_metric!= INFINITY:
                self.add_routing_table(potential_metric, dest, router_id)
        else:
            # if next hop comes from the current neighbour
            if self.routing_table[dest][1] == router_id:

                # update if values are different
                if potential_metric != self.routing_table[dest][0]:
                    self.routing_table[dest][0] = potential_metric
                    self.routing_table[dest][1] = router_id

                    # if it is not infinity reintialize timer and set
                    # firsttime flag to true
                    if potential_metric != INFINITY:
                        #  reinitialize timer
                        self.routing_table[dest][2] = 0
                        self.routing_table[dest][3] = True
                    # if new metric is infinity trigger an update
                    else:
                        # if it is the first time the entry being infinity
                        if self.routing_table[dest][3]:
                            self.send()
                            self.routing_table[dest][3] = False
                            self.routing_table[dest][2] = 0
                else:
                    # reinitialize timer if metric is the same
                    self.routing_table[dest][2] = 0

            elif potential_metric < self.routing_table[dest][0]:
                self.routing_table[dest][0] = potential_metric
                self.routing_table[dest][1] =  router_id
                self.routing_table[dest][2] =   0

    def startRouter(self):
        """start the router"""
        self.periodic_update()
        self.update_Timer()
        self.disp()

        while True:
            inputready, outputready, exceptrdy = select.select(
                self.input_sockets, [], [], 1)
            for s in inputready:
                self.lock.acquire()

                try:
                    router_id, entry_table = self.receive_data(s)
                except Exception as e:
                    print(e.message)
                    continue

                for entry in entry_table:
                    # print("Entry: " + str(entry))
                    # some entries are irrelevant for now
                    _, _, dest, _, next_hop, entry_metric = entry

                    if entry_metric > INFINITY or entry_metric < 0:
                        print("Incorrect metric received: ", entry_metric)
                        continue

                    # skip if entry is about it self
                    if dest == self.router_id:
                        continue

                    # cost from the current router to a potential dest router
                    # through next_hop
                    potential_metric = entry_metric + self.routing_table[router_id][0]
                    potential_metric = min(potential_metric, INFINITY)

                    self.updat_routing_table(dest, potential_metric, router_id)
                self.lock.release()

    def print_routing_table(self):
        """prints the current routing table"""
        print("Routing table for ",self.router_id)
        print("|{:^7}|{:^7}|{:^15}|{:^15}|{:^15}|".format(
            "dest id", "metric", "next hop id", "timeout","firsttime"))
        for key in self.routing_table.keys():
            row = self.routing_table[key]
            print("|{:^7}|{:^7}|{:^15}|{:^15}|{:^15}|".format(key, *row))

    def send(self):
        """send an rip packet to all neighbours of the router"""
        for port in self.output_port:
            message = self.generate_packet(port)
            # print("msg to send",message)
            self.input_sockets[0].sendto(message, (LOCALHOST, port))
            # print("sended")
