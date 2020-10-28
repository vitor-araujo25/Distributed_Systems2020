import time, rpyc
from typing import Tuple
from rpyc.utils.server import ThreadedServer
from utils import sha, NodeID

class ChordNodeService(rpyc.Service):
    
    def __init__(self, port, node_id, finger_table):
        super().__init__()
        print(f"starting node [{node_id}] on port: {port}\nfinger_table: {finger_table}")
        self.exposed_node_id = node_id
        self.exposed_port = port
        self.finger_table = finger_table
        self.ft_length = len(finger_table)
        self.successor = finger_table[0]["successor"]
        self.peer = None
        self.key_table = {}

    def start(self):
        server = ThreadedServer(self, port=self.exposed_port, protocol_config={"allow_public_attrs": True})
        server.start()
    
    def on_connect(self, conn):
        self.peer = conn

    def on_disconnect(self, conn):
        # self.peer = None
        pass

    def closest_preceding_node(self, desired_id: int):
        for i in range(self.ft_length - 1, -1, -1):
            if self.finger_table[i]["finger"] > self.exposed_node_id and self.finger_table[i]["finger"] < desired_id:
                return self.finger_table[i]["successor"]
        
        return NodeID(node_id=self.exposed_node_id, port=self.exposed_port)

    def exposed_find_successor(self, desired_id: int):
        print(f"id: {desired_id}, n: {self.exposed_node_id}, succ: {self.successor.node_id}")
    
        if desired_id > self.exposed_node_id and desired_id <= self.successor.node_id:
            #return my successor
            print("it's my successor!")
            return self.successor
        else:
            pred = self.closest_preceding_node(desired_id)
            pred_conn = rpyc.connect("localhost", pred.port)
            return pred_conn.root.find_successor(desired_id)

    #called from outside the chord ring
    def exposed_insert_key(self, key, value):
        key_hash = sha(key) % 2**self.ft_length
        self.exposed_insert_hash(key_hash)

    #for use exclusively within the chord ring
    def exposed_insert_hash(self, key_hash, value):    
        if key_hash == self.exposed_node_id:
            self.key_table[key_hash] = value
        else:
            succ_obj = self.exposed_find_successor(key_hash)
            s = rpyc.connect("localhost", port=succ_obj.port)
            s.root.insert_hash(key_hash, value)
        


    
            
