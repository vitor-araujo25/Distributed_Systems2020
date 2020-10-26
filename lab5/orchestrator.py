import multiprocessing as mp
import sys, rpyc, socket, time, threading
from rpyc.utils.server import ThreadedServer
from typing import Tuple
from chord_node import ChordNodeService
from utils import hash

running_nodes = {}

def start_nodes(n: int):
    free_ports = []

    #finding free ports in the system
    for i in range(2**n):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('', 0))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            free_ports.append(sock.getsockname()[1])

    # # maps chord id's to localhost ports
    # ids_to_ports = {hash(port): port for port in free_ports}
    # ring = list(ids_to_ports.items())
    # ring.sort(key=lambda x: x[0])

    # initial_finger_tables = {}
    # for idx, elem in enumerate(ring):
    #     node_id, node_addr = elem
   
    #     finger = (node_id + 1) % 2**HASH_SIZE
    #     if idx == len(ring)-1:
    #         successor = ring[0]
    #     else:
    #         successor = ring[idx + 1]

    #     initial_finger_tables[node_addr] = [(finger, successor)]

    
    # addr, finger_table = list(initial_finger_tables.items())[0]

    bootstrap_addr = free_ports[0]

    # for addr, finger_table in list(initial_finger_tables.items()):
    p = mp.Process(target=chord_node_main, args=(bootstrap_addr, free_ports[1]))
    p.start()
    running_nodes[bootstrap_addr] = p

    for addr in free_ports[1:]:
        p = mp.Process(target=chord_node_main, args=(addr, bootstrap_addr))
        p.start()
        running_nodes[addr] = p

def chord_node_main(port_no: int, bootstrap_port_no: int = None):
    server = ThreadedServer(ChordNodeService(port=port_no, bootstrap_node=bootstrap_port_no), port=port_no)
    server.start()

class OrchestratorService(rpyc.Service):
    pass


if __name__ == "__main__":
    start_nodes(int(sys.argv[1]))
    print("Running Chord nodes:")
    [print(f"localhost:{port}") for port in running_nodes.keys()]
    # server = ThreadedServer(OrchestratorService, port=9000)
    # server.start()