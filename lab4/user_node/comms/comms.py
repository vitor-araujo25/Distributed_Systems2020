import socket
import configs

class Comms(object):
    
    def __init__(self):
        self.__inbound_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__outbound_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(socket_tuple)
        if sock is None:
            print("Error on socket binding")
            sys.exit(1)
        sock.listen()
        print(f"Listening on port {socket_tuple[1]}...")
        sock.setblocking(False)
        return sock