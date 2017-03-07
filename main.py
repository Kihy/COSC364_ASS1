import sys
from util import *
from router import *

def main():
    for filename in sys.argv[1:]:
        router_id, input_ports, output_ports=read_config(filename)
        print(router_id)
        router=Router(router_id)
        for p in input_ports:
            router.add_input_socket(p)
        for p in output_ports:
            router.add_routing_table(*p)
        router.start()

main()
