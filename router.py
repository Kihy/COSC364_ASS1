import socket
import select
import time
import random
import threading

LOCALHOST="127.0.0.1"
MINIMUM_TIME=25
TIMER_RANGE=10

#class Entry(object):
    #def __init__(self, dest, metric, ):

class Router(object):
    """docstring for Router."""
    def __init__(self, router_id):
        self.router_id=router_id
        self.routing_table=[]
        self.input_sockets=[]

    def add_input_socket(self, port_num):
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.bind((LOCALHOST,port_num))
        self.input_sockets.append(sock)

    def add_routing_table(self, port,metric,router_id):
        self.routing_table.append([port,metric,router_id])

    def periodic_update(self):
        wait_time=MINIMUM_TIME+random.uniform(0,TIMER_RANGE)
        self.send(12)
        threading.Timer(wait_time, self.periodic_update).start()

    def start(self):
        self.periodic_update()
        while True:
            inputready, outputready,exceptrdy = select.select(self.input_sockets, [],[],0.5)
            for s in inputready:
                data,addr=s.recvfrom(1024)
                print(data)

    def send(self, port_num):
        self.input_sockets[0].sendto(b"hello",(LOCALHOST,self.routing_table[0][0]))
        print("send")
