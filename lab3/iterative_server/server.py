import socket, sys, json, select
import core, configs

CURRENT_CONNECTIONS = {}
INWARD_DESCRIPTORS = [sys.stdin]
SERVER_IS_RUNNING = True

def handle_connection_close(sock):
    del CURRENT_CONNECTIONS[sock]
    INWARD_DESCRIPTORS.remove(sock)
    sock.close()

def socket_setup(socket_tuple):
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
    print(f"Connection established to {CURRENT_CONNECTIONS[client_socket]}")
    
    file_name = client_socket.recv(1024)
    if not file_name:
        print(f"Connection closed by {CURRENT_CONNECTIONS[client_socket]}.")
        handle_connection_close(client_socket)
        return
    file_name = file_name.decode()
    print(f"File name received: {file_name}")
    
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
    server_socket = socket_setup(conn_tuple)
    with server_socket as server:
        INWARD_DESCRIPTORS.append(server)

        #main server loop
        while SERVER_IS_RUNNING:
            r_list, w_list, e_list = select.select(INWARD_DESCRIPTORS, [], [])
            for ready_sock in r_list:
                if ready_sock is sys.stdin:
                    command = input()
                    if command.upper() == "LEAVE":
                        if CURRENT_CONNECTIONS:
                            print("There are still clients being served:")
                            print("\n".join([addr for sock, addr in CURRENT_CONNECTIONS.items()]))
                        else:
                            SERVER_ON = False
                            break    
                elif ready_sock is server:
                    client_socket, remote_addr = server.accept()
                    INWARD_DESCRIPTORS.append(client_socket)
                    CURRENT_CONNECTIONS[client_socket] = remote_addr
                else:
                    handle_request(ready_sock)

def main():
    print("Starting server")
    addr = (configs.HOST, configs.PORT)
    start(addr)

if __name__ == "__main__":
    main()
