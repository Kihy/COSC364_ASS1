import sys
from util import *
from router import *


def main():
    """reads a config file and starts a router"""
    for filename in sys.argv[1:]:
        router_id, input_ports, output_ports = read_config(filename)
        router = Router(router_id)
        for p in input_ports:
            router.add_input_socket(p)
        for p in output_ports:
            router.add_port_dict(p[0], p[2])
            router.add_routing_table(p[1], p[2], p[2])
            router.add_original_routing_table(p[1], p[2], p[2])
            router.add_output_port(p[0])
        router.startRouter()


if __name__ == '__main__':
    main()
