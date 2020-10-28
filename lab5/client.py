import rpyc
from rpyc.utils.server import ThreadedServer
import multiprocessing as mp
import uuid

TRACKER_PORT = 10000
CLIENT_PORT = 5000

class ClientService(rpyc.Service):
    
    def __init__(self, tracker_port):
        super().__init__()
        self.TRACKER_PORT = tracker_port
        self.tracker = rpyc.connect("localhost", port=tracker_port)

    def get_chord_node_addr(self):
        return self.tracker.root.get_random_node()

    def exposed_insert_key(self, key, value):
        origin_node_port = self.get_chord_node_addr()
        print(f"Using node at localhost:{origin_node_port}")
        chord_connection = rpyc.connect("localhost", port=origin_node_port)
        chord_connection.root.insert(key, value)

    def exposed_lookup_key(self, key):
        origin_node_port = self.get_chord_node_addr()
        print(f"Using node at localhost:{origin_node_port}")
        chord_connection = rpyc.connect("localhost", port=origin_node_port)
        chord_connection.root.lookup(key, search_id=uuid.uuid4().hex)

    def exposed_lookup_response(self, key, value, search_id):
        if value:
            print(f"Search for key '{key}' with ID [{search_id}] returned value: {value}")
        else:
            print(f"Search for key '{key}' with ID [{search_id}] did not find any result.")

    #for debugging
    def exposed_reconnect_to_tracker(self):
        self.tracker = rpyc.connect("localhost", port=self.TRACKER_PORT)


def start_client_service():
    client = ThreadedServer(ClientService(TRACKER_PORT), port=CLIENT_PORT, protocol_config={"allow_public_attrs": True})
    client.start()


if __name__ == "__main__":
    #start client RPC instance
    p = mp.Process(target=start_client_service)
    p.start()

    #CLIENT INTERACTION LOOP

    p.join()