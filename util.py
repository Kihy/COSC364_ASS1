import sys
import struct

HEADER_FORMAT = "BBH"
ENTRY_FORMAT = "HHIIII"
LINE = "-" * 33 + "\n"


class Rip_packet:
    """a rip v2 packet, this class handles turning itself into a byte array"""

    def __init__(self, router_id):
        self.command = 2
        self.version = 2
        self.router_id = router_id
        self.entry_table = []

    def add_entry(self, entry):
        """adds an entry to the entry table"""
        self.entry_table.append(entry)

    def dump(self):
        """turns the packet it self into a bytearclass Entry(object)for transfer"""
        # header
        packet = struct.pack(HEADER_FORMAT, self.command,
                             self.version, self.router_id)
        # add entry_table
        for row in self.entry_table:
            packet += struct.pack(ENTRY_FORMAT, *row)
        return packet

    def __str__(self):
        """string representation of the packet"""
        string = LINE
        string += "|{:^7}|{:^7}|{:^15}|\n".format(
            self.command, self.version, self.router_id)
        string += LINE
        for entry in self.entry_table:
            string += "|{:^15}|{:^15}|\n|{:^31}|\n|{:^31}|\n|{:^31}|\n|{:^31}|\n".format(
                *entry)
            string += LINE
        return string

        # def __repr__(self):
        #     return self.__str__()


def load(byte_stream):
    """loads the packet bytestream into a packet object"""
    num_entry = (len(byte_stream) - 4) // 20
    start, end = 0, 4
    command, version, router_id = struct.unpack(
        HEADER_FORMAT, byte_stream[start:end])
    rip = Rip_packet(router_id)
    for i in range(num_entry):
        start, end = end, end + 20
        entry = struct.unpack(ENTRY_FORMAT, byte_stream[start:end])
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
    """check router id"""
    if router_id > 64000 or router_id < 1:
        raise ValueError("Router ID out of bounds.")


def check_port(port_num):
    """check port number"""
    if port_num < 1024 or port_num > 64000:
        raise ValueError("port number out of bounds.")


def read_config(filename):
    """parse the config file """
    router_id = None
    input_ports = []
    output_ports = []
    conf = open(filename)
    for line in conf.readlines():
        line = line.rstrip()
        if line.startswith("//") or line == "":
            continue
        try:
            if line.startswith("router-id"):
                router_id = int(line.split()[1])
                check_id(router_id)

            if line.startswith("input-ports"):
                input_ports = list(map(int, line.split()[1].split(",")))
                for port in input_ports:
                    check_port(port)
            if line.startswith("outputs"):
                output_port = line.split()[1].split(",")
                for port in output_port:
                    output_port_list = list(map(int, port.split("-")))
                    check_port(output_port_list[0])
                    check_id(output_port_list[2])
                    output_ports.append(output_port_list)
        except ValueError as e:
            print(e.args[0])
            sys.exit()
        except IndexError as e:
            print("missing inputs")
            sys.exit()
    try:
        if router_id == None:
            raise ValueError("Router ID not set")
    except ValueError as e:
        print(e.args[0])
        sys.exit()
    return router_id, input_ports, output_ports
