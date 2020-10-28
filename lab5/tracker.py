import multiprocessing as mp
import sys, rpyc, socket, time, threading
from chord_node import ChordNodeService
from utils import sha, NodeID
from rpyc.utils.server import ThreadedServer
from rpyc.utils.helpers import classpartial
import random

PORT = 10000

class TrackerService(rpyc.Service):
    

    def __init__(self, n: int, debug: bool):
        #will contain a mapping like: (ID, port) -> running_process_object
        self.running_nodes = {}
        self.DEBUG = debug
        self.start_nodes(n)
        
    def start_nodes(self, n: int):
    
        ports = {i: PORT + i + 1 for i in range(2**n)}
        
        for i in range(2**n):
        
            finger_table = []

            for j in range(n):
                finger = (i + 2**j) % 2**n
                entry = {
                    "finger": finger, 
                    #since we are sure to have a running node for each 0 <= id < 2^n
                    #the closest preceding node to any id is id-1, making any id's successor
                    #equal to the id itself
                    "successor": NodeID(node_id=finger, port=ports[finger])
                }
                finger_table.append(entry)

            node = ChordNodeService(node_id=i, port=ports[i], finger_table=finger_table, debug=self.DEBUG)
            p = mp.Process(target=node.start)
            p.start()
            self.running_nodes[(i, ports[i])] = p

        print("Running Chord nodes:")
        [print(f"localhost:{port}") for node_id, port in self.running_nodes.keys()]

    def exposed_get_random_node(self):
        return random.choice(list(self.running_nodes.keys()))[1]

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[2] == "debug":
        server = ThreadedServer(TrackerService(int(sys.argv[1]), debug=True), port=PORT)
        server.start()
    else:
        server = ThreadedServer(TrackerService(int(sys.argv[1]), debug=False), port=PORT)
        server.start()
