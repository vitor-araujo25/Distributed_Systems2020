import rpyc
from rpyc.utils.server import ThreadedServer
import multiprocessing as mp
import uuid
import time
import sys

TRACKER_PORT = 10000
CLIENT_PORT = 5000

class InvalidCommandException(Exception):
    pass

class ClientService(rpyc.Service):
    
    def __init__(self, tracker_port, client_port):
        super().__init__()
        self.TRACKER_PORT = tracker_port
        self.PORT = client_port
        self.tracker = rpyc.connect("localhost", port=tracker_port)
        self.ongoing_lookups = {}

    def start(self):
        client = ThreadedServer(self, port=self.PORT, protocol_config={"allow_public_attrs": True})
        client.start()

    def get_chord_node_addr(self):
        return self.tracker.root.get_random_node()

    def exposed_insert_key(self, key, value):
        origin_node_port = self.get_chord_node_addr()
        # print(f"Using node at localhost:{origin_node_port}")
        chord_connection = rpyc.connect("localhost", port=origin_node_port)
        chord_connection.root.insert(key, value)

    def exposed_lookup_key(self, key):
        origin_node_port = self.get_chord_node_addr()
        # print(f"Using node at localhost:{origin_node_port}")
        chord_connection = rpyc.connect("localhost", port=origin_node_port)
        search_id = uuid.uuid4().hex
        self.ongoing_lookups[search_id] = key
        print(f"SearchID: {search_id}")
        chord_connection.root.lookup(key, search_id=search_id, client_port=self.PORT)

    def exposed_lookup_response(self, value, search_id):
        if value:
            print(f"Search for key '{self.ongoing_lookups[search_id]}' with SearchID [{search_id}] returned value: {value}")
        else:
            print(f"Search for key '{self.ongoing_lookups[search_id]}' with SearchID [{search_id}] did not find any result.")
        del self.ongoing_lookups[search_id]

    #for debugging
    def exposed_reconnect_to_tracker(self):
        self.tracker = rpyc.connect("localhost", port=self.TRACKER_PORT)


def usage_instructions():
    print("insert <key> <value> \n\ttype(key): int|float|string|tuple, type(value): any \n\tReturn: None. \n\tInserts the pair (key, value) into the DHT.\n")
    print("lookup <key> \n\ttype(key): int|float|string|tuple \n\tReturn: SearchID. \n\tAsync Response: Resolved lookup. \n\tSearches the DHT for the specified key.\n")
    print("help \n\tReturn: None \n\tPrints these instructions.\n")
    print("quit \n\tReturn: None \n\tFinishes the application.")

if __name__ == "__main__":
    #start client RPC instance
    client = ClientService(TRACKER_PORT, CLIENT_PORT)
    p = mp.Process(target=client.start)
    p.start()

    time.sleep(0.25) #small delay for the client RPC instance to start
    CLIENT_CONNECTION = rpyc.connect("localhost", port=CLIENT_PORT)

    #CLIENT INTERACTION LOOP
    while True:
        print("> ", end="")
        user_input = input()
        user_input = user_input.split(' ')
        command = user_input[0]
        params = user_input[1:]
        param_count = len(params)

        try:
            if command == "insert":
                assert param_count == 2
                CLIENT_CONNECTION.root.insert_key(key=params[0], value=params[1])

            elif command == "lookup":
                assert param_count == 1
                CLIENT_CONNECTION.root.lookup_key(key=params[0])

            elif command == "help":
                assert param_count == 0
                usage_instructions()

            elif command == "quit":
                assert param_count == 0
                print("Quitting...")
                sys.exit()
                break

            else:
                raise InvalidCommandException

        except AssertionError:
            print(f"Wrong parameters for '{command}' operation.")
        except InvalidCommandException:
            print(f"Command '{command}' is unknown.")

    # CLIENT_CONNECTION.close()
