import sys
import struct

HEADER_FORMAT="BBH"
ENTRY_FORMAT="HHIIII"
LINE="-"*33+"\n"

class Rip_packet:
    """a rip v2 packet"""
    def __init__(self, router_id):
        self.command=2
        self.version=2
        self.router_id=router_id
        self.entry_table=[]

    def add_entry(self,entry):
        self.entry_table.append(entry)

    def dump(self):
        #header
        packet=struct.pack(HEADER_FORMAT,self.command,self.version,self.router_id)
        #add entry_table
        for row in self.entry_table:
            packet+=struct.pack(ENTRY_FORMAT,*row)
        return packet

    def __str__(self):
        string=LINE
        string+="|{:^7}|{:^7}|{:^15}|\n".format(self.command,self.version,self.router_id)
        string+=LINE
        for entry in self.entry_table:
            string+="|{:^15}|{:^15}|\n|{:^31}|\n|{:^31}|\n|{:^31}|\n|{:^31}|\n".format(*entry)
            string+=LINE
        return string

def load(packet):
    num_entry=(len(packet)-4)//20
    command,version,router_id=struct.unpack(HEADER_FORMAT,packet[0:4])
    rip=Rip_packet(router_id)
    for i in range(num_entry):
        entry=struct.unpack(ENTRY_FORMAT,packet[4+i*20:4+(i+1)*20])
        rip.add_entry(entry)
    return rip
# # test packet load and dump functions
# p=Rip_packet(1)
# p.add_entry((1,1,1,1,1,1))
# p.add_entry((2,2,2,2,2,2))
# byte_stream=p.dump()
# p2=load(byte_stream)
# print(p2)

def check_id(router_id):
    if router_id > 64000 or router_id<1:
        raise ValueError("Router ID out of bounds.")

def check_port(port_num):
    if port_num <1024 or port_num>64000:
        raise ValueError("port number out of bounds.")

def read_config(filename):
    router_id=None
    input_ports=[]
    output_ports=[]
    conf=open(filename)
    for line in conf.readlines():
        line=line.rstrip()
        if line.startswith("//") or line=="":
            continue
        try:
            if line.startswith("router-id"):
                router_id=int(line.split()[1])

            if line.startswith("input-ports"):
                input_ports=list(map(int,line.split()[1].split(",")))

            if line.startswith("outputs"):
                output_port=line.split()[1].split(",")
                for port in output_port:
                    output_ports.append(list(map(int,port.split("-"))))
        except ValueError as e:
            print(e.args[0])
            sys.exit()
        except IndexError as e:
            print("missing inputs")
            sys.exit()
    try:
        if router_id==None:
            raise ValueError("Router ID not set")
    except ValueError as e:
        print(e.args[0])
        sys.exit()
    return router_id, input_ports, output_ports
