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
        self.exposed_successor = finger_table[0]["successor"]
        self.client_conn = None
        self.key_table = {}

    def start(self):
        server = ThreadedServer(self, port=self.exposed_port, protocol_config={"allow_public_attrs": True})
        server.start()
    
    def on_connect(self, conn):
        self.client_conn = conn.root

    def on_disconnect(self, conn):
        self.client_conn = None

    def closest_preceding_node(self, desired_id: int):
        for i in range(self.ft_length - 1, -1, -1):
            finger = self.finger_table[i]["finger"] 

            #modular arithmetic correction
            finger = finger if finger > self.exposed_node_id else finger + 2**self.ft_length
            if finger > self.exposed_node_id and finger < desired_id:
                return self.finger_table[i]["successor"]
        
        return NodeID(node_id=self.exposed_node_id, port=self.exposed_port)

    def exposed_find_successor(self, desired_id: int):
        print(f"id: {desired_id}, n: {self.exposed_node_id}, succ: {self.exposed_successor.node_id}")
        modular_congruent = desired_id

        #modular arithmetic correction
        if desired_id < self.exposed_node_id:
            modular_congruent += 2**self.ft_length
    
        if modular_congruent > self.exposed_node_id and modular_congruent <= self.exposed_successor.node_id:
            #return my successor
            print("it's my successor!")
            return self.exposed_successor
        else:
            pred = self.closest_preceding_node(modular_congruent)
            pred_conn = rpyc.connect("localhost", pred.port)
            return pred_conn.root.find_successor(desired_id)


    #called from outside the chord ring
    def exposed_insert(self, key, value):
        key_hash = sha(key) % 2**self.ft_length
        #FAZER ASYNC!!!
        self.exposed_insert_hash(key, key_hash, value)

    #for use exclusively within the chord ring
    def exposed_insert_hash(self, key, key_hash, value):    
        if key_hash == self.exposed_node_id:
            print(f"[Node {self.exposed_node_id}] Inserted ('{key}', '{value}') here!")
            self.key_table[key] = value
        elif key_hash == self.exposed_successor.node_id:
            s = rpyc.connect("localhost", port=self.exposed_successor.port)
            s.root.insert_hash(key, key_hash, value)
            s.close()
        else:
            succ_obj = self.exposed_find_successor(key_hash)
            s = rpyc.connect("localhost", port=succ_obj.port)
            s.root.insert_hash(key, key_hash, value)
            s.close()

    def exposed_lookup(self, key, search_id):
        key_hash = sha(key) % 2**self.ft_length
        #FAZER ASYNC!!!
        self.exposed_lookup_internal(self.client_conn, key, key_hash, search_id)

    def exposed_lookup_internal(self, client_ref, key, key_hash, search_id):
        if key_hash == self.exposed_node_id:
            value = self.key_table.get(key)

            #TODO: solve buggy connection. do it by passing port number as parameter if need be
            client_ref.lookup_response(key, value, search_id)
            
        elif key_hash == self.exposed_successor.node_id:
            s = rpyc.connect("localhost", port=self.exposed_successor.port)
            s.root.lookup_internal(client_ref, key, key_hash, search_id)
            s.close()
        else:
            succ_obj = self.exposed_find_successor(key_hash)
            s = rpyc.connect("localhost", port=succ_obj.port)
            s.root.lookup_internal(client_ref, key, key_hash, search_id)
            s.close()

    #for debugging
    def exposed_show_info(self):
        return (f"{{'node_id': {self.exposed_node_id},\n'finger_table': {self.finger_table}\n"
                f"'key_table': {self.key_table}}}")



    
            
