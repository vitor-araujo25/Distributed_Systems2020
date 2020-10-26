import time, rpyc
from typing import Tuple

class ChordNodeService(rpyc.Service):
    
    FT_LENGTH = 20
    HASH_SIZE = 160

    def __init__(self, port, bootstrap_node):
        super().__init__()
        #array containing objects of the format (finger, (id_successor, port_successor))
        print(f"starting on port: {port}, bootstrap: {bootstrap_node}")
        self.exposed_id = hash(port)
        self.exposed_port = port
        self.next_finger = 0
        
        #creating chord ring from scratch
        if bootstrap_node is None:
            self.exposed_successor = (self.exposed_id, self.exposed_port) #NÃO FAZ SENTIDO!!!
        
        #joining chord ring from a known bootstrap node
        else:    
            entry_node = rpyc.connect("localhost", bootstrap_node)
            self.exposed_successor = entry_node.root.find_successor(self.exposed_id)

        self.exposed_predecessor = None
        self.finger_table = [None]*self.FT_LENGTH
        self.finger_table[0] = {"finger": (self.exposed_id+1) % 2**self.HASH_SIZE, "successor": self.exposed_successor}

        # threading.Thread(target=self.housekeeping).start()

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def housekeeping(self):
        while True:
            time.sleep(0.25)
            # with self.lock:
            self.fix_fingers()
            self.stabilize()

    def stabilize(self):
        conn = rpyc.connect("localhost", self.exposed_successor[1])
        x: Tuple[int, int] = conn.root.predecessor
        if x is not None and (x[0] > self.exposed_id and x[0] < self.exposed_successor[0]):
            self.exposed_successor = x

        #repetition is necessary, as the previous step could have changed the successor, invalidating the connection
        conn = rpyc.connect("localhost", self.exposed_successor[1])
        conn.root.notify((self.exposed_id, self.exposed_port))

    def fix_fingers(self):
        self.next_finger += 1
        if self.next_finger >= self.FT_LENGTH:
            self.next_finger = 0
        finger = (self.exposed_id + 2**self.next_finger) % 2**self.HASH_SIZE
        print(f"next finger: {self.next_finger}")
        successor = self.exposed_find_successor(finger)
        # with self.lock:
        self.finger_table[self.next_finger] = {
            "finger": finger, 
            "successor": successor
        }
    
    def exposed_notify(self, node: Tuple[int, int]):
        if self.exposed_predecessor is None or (node[0] > self.exposed_predecessor[0] and node[0] < self.exposed_id):
            self.exposed_predecessor = node

    # def expand_finger_table(self):
    #     peer = rpyc.connect("localhost", self.exposed_successor[1])
    #     for i in range(1, self.FT_LENGTH):
    #         finger = (self.exposed_id + 2**i) % 2**HASH_SIZE
    #         ith_finger_successor = peer.root.find_successor(finger)
    #         self.finger_table.append((finger, ith_finger_successor))
    #     self.stable = True

    def closest_preceding_node(self, id: int) -> Tuple[int, int]:
        for i in range(self.FT_LENGTH - 1, -1, -1):
            if self.finger_table[i] is None: continue
            if self.finger_table[i]["finger"] > self.exposed_id and self.finger_table[i]["finger"] < id:
                return self.finger_table[i]["successor"]
        
        return (self.exposed_id, self.exposed_port)

    def exposed_find_successor(self, id: int) -> Tuple[int, int]:
        # with self.lock:
        print(f"id: {id}, n: {self.exposed_id}, succ: {self.exposed_successor}")
    
        if id > self.exposed_id and id <= self.exposed_successor[0]:
            return self.exposed_successor
        else:
            pred = self.closest_preceding_node(id)
            peer = rpyc.connect("localhost", pred[1])
            return peer.root.find_successor(id)
            

    def exposed_test(self):
        return "hey"
        