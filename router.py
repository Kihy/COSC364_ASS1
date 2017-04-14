from util import *
import socket
import select
import time
import random

import threading

LOCALHOST = "127.0.0.1"
MINIMUM_TIME = 30
TIMER_RANGE = 10
INFINITY = 17


# class Entry(object):
#     def __init__(self,dest,next_hop,metric):
#         self.time = time.time()
#         self.dest = dest
#         self.next_hop = next_hop
#         self.metric = metric

class Router(object):
    """docstring for Router."""

    def __init__(self, router_id):
        self.time = time.time()
        self.router_id = router_id
        self.routing_table = {}
        self.input_sockets = []
        self.output_port = []
        self.portDict = {}

    def add_port_dict(self, port, router_id):
        self.portDict[port] = router_id

    def add_input_socket(self, port_num):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((LOCALHOST, port_num))
        self.input_sockets.append(sock)

    def add_output_port(self, output_port_number):
        self.output_port.append(output_port_number)

    def add_routing_table(self, metric, dest_id, next_hop, timeout=0):
        metric=min(INFINITY,metric)
        self.routing_table[dest_id] = [metric, next_hop, timeout]

    def generate_packet(self, output_port):
        """generate a RIP packet from routing table"""
        # generate Rip_packet object
        # add each entry in routing table to packet
        # call dump in packet
        rip_packet = Rip_packet(self.router_id)

        #add information about it self
        rip_packet.add_entry([0,0,self.router_id,0,self.router_id,0])

        for dest_id in self.routing_table.keys():
            metric, next_hop, timeout = self.routing_table[dest_id]

            if self.portDict[output_port] == next_hop:
                if dest_id != next_hop:
                    metric = INFINITY
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
        wait_time = MINIMUM_TIME + random.uniform(0, TIMER_RANGE)
        self.send()
        threading.Timer(wait_time, self.periodic_update).start()

    def update_Timer(self):
        for key in self.routing_table.keys():
            self.routing_table[key][2] += 1
            if self.routing_table[key][2] == 180:
                self.routing_table[key][0] = INFINITY
                self.routing_table[key][2] = 0
                self.send()  # notify neighbours about the change
            elif self.routing_table[key][2] == 120 and self.routing_table[key][0] == INFINITY:
                self.routing_table.pop(key)
                print("garbage expired, remove entry", key)
        threading.Timer(1,self.update_Timer).start()

    def disp(self):
        self.print_routing_table()
        threading.Timer(10, self.disp).start()

    def startRouter(self):
        self.periodic_update()
        self.update_Timer()
        self.disp()
        while True:
            inputready, outputready, exceptrdy = select.select(
                self.input_sockets, [], [], 0.5)
            for s in inputready:
                data, addr = s.recvfrom(1024)
                rip_packet = load(data)

                # validation check
                # check whether the response is from one of the router's own
                # addresses
                if rip_packet.router_id == self.router_id:
                    break

                elif rip_packet.router_id not in self.portDict.values():  # If not a directly connected network
                    break

                print("Packet Received")
                print(rip_packet)
                for entry in rip_packet.entry_table:
                    # print("Entry: " + str(entry))
                    _, _, dest, _, next_hop, entry_metric = entry

                    # if entry is about it self and not inifinity, clear timeout for that router
                    if dest == self.router_id:
                        continue

                    # cost from the current router to a potential dest router
                    # through next_hop
                    potential_metric = entry_metric + \
                        self.routing_table[rip_packet.router_id][0]
                    potential_metric = min(potential_metric, INFINITY)
                    # if not in routing table
                    if dest not in self.routing_table.keys():
                        self.add_routing_table(
                            potential_metric, dest, rip_packet.router_id)
                    else:
                        # if next hop comes from the current neighbour
                        if self.routing_table[dest][1] == rip_packet.router_id:

                            # update if values are different
                            if potential_metric != self.routing_table[dest][0]:
                                self.routing_table[dest][0] = potential_metric
                                self.routing_table[dest][
                                    1] = rip_packet.router_id

                                # if new metric is infinity trigger an update
                                if potential_metric != INFINITY:
                                    #  reinitialize timer
                                    self.routing_table[dest][2] = 0
                                else:
                                    self.send()
                            else:
                                self.routing_table[dest][2] = 0

                        elif potential_metric < self.routing_table[dest][0]:
                            self.routing_table[dest] = [
                                potential_metric, rip_packet.router_id, 0]

    def print_routing_table(self):
        print("Routing table")
        print("|{:^7}|{:^7}|{:^15}|{:^15}|".format(
            "dest id", "metric", "next hop id", "timeout"))
        for key in self.routing_table.keys():
            row = self.routing_table[key]
            print("|{:^7}|{:^7}|{:^15}|{:^15}|".format(key, *row))

    def send(self):

        for port in self.output_port:
            message = self.generate_packet(port)

            # print("msg to send",message)
            self.input_sockets[0].sendto(message, (LOCALHOST, port))
            # print("sended")
