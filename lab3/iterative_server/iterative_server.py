import socket, sys, json, select
import core, configs

#keeps track of all the active connections in the format of
#a key that is the socket object and the value that is the address
#of the client the socket connects to
CURRENT_CONNECTIONS = {}

#manages all inputs the server is interested in listening to
INWARD_DESCRIPTORS = [sys.stdin]

def handle_connection_close(sock):
    '''
    Performs cleaning of the connection managing data structures and closes 
    the client socket.
    '''
    conn_string = f"{CURRENT_CONNECTIONS[sock][0]}:{CURRENT_CONNECTIONS[sock][1]}"
    del CURRENT_CONNECTIONS[sock]
    INWARD_DESCRIPTORS.remove(sock)
    sock.close()
    print(f"Connection to {conn_string} closed.")

def socket_setup(socket_tuple):
    '''
    Opens a non-blocking TCP socket for listening and returns it.
    If any error occurs in the socket binding. the program terminates.
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(socket_tuple)
    if sock is None:
        print("Error on socket binding")
        sys.exit(1)
    sock.listen()
    print(f"Listening on port {socket_tuple[1]}...")
    sock.setblocking(False)
    return sock

def handle_request(client_socket):
    '''
    Handles single request from client
    '''
    file_name = client_socket.recv(1024)
    if not file_name:
        handle_connection_close(client_socket)
        return
    file_name = file_name.decode()
    print(f"{CURRENT_CONNECTIONS[client_socket][0]}:{CURRENT_CONNECTIONS[client_socket][1]} asked for file --> '{file_name}'")
    
    #invoking word counting method at core layer 
    try:
        word_count = core.count_words(file_name)
    except OSError as e:
        client_socket.sendall(b"ERROR")
        print("File access error. Resuming listening for more file names...")
    except Exception as e:
        client_socket.sendall(b"ERROR")
        print(f"Unexpected exception: {e}")
    else:
        client_socket.sendall(json.dumps(word_count).encode('utf-8'))

def start(conn_tuple):
    SERVER_IS_RUNNING = True
    
    server_socket = socket_setup(conn_tuple)
    with server_socket as server:
        #registers the main server socket as one of the file descriptors the OS
        #should notify the server program about
        INWARD_DESCRIPTORS.append(server)

        #main server loop
        while SERVER_IS_RUNNING:
            r_list, w_list, e_list = select.select(INWARD_DESCRIPTORS, [], [])

            #select handling loop
            for ready_sock in r_list:

                if ready_sock is sys.stdin:
                    command = input()
                    if command.upper() == "LEAVE":
                        if CURRENT_CONNECTIONS:
                            print("There are still clients being served:")
                            print("\n".join([f"{addr[0]}:{addr[1]}" for sock, addr in CURRENT_CONNECTIONS.items()]))
                        else:
                            SERVER_IS_RUNNING = False
                            break    
                    else:
                        print("Unknown command.")

                elif ready_sock is server:
                    client_socket, remote_addr = server.accept()

                    #when new client connects, the created socket is inserted into INWARD_DESCRIPTORS list
                    #so that the select call also notifies the server when the client socket receives any messages.
                    INWARD_DESCRIPTORS.append(client_socket)
                    CURRENT_CONNECTIONS[client_socket] = remote_addr
                    print(f"Connection established to {remote_addr[0]}:{remote_addr[1]}")

                else:
                    handle_request(ready_sock)

def main():
    print("Starting iterative server")
    addr = (configs.HOST, configs.PORT)
    start(addr)

if __name__ == "__main__":
    main()
