import socket, sys, json, select, threading
import core, configs

def handle_connection_close(sock, addr):
    conn_string = f"{addr[0]}:{addr[1]}"
    sock.close()
    print(f"[{threading.current_thread().name}] Connection to {conn_string} closed.")

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

def client_loop(client_socket, addr):
    print(f"[{threading.current_thread().name}] Connection established to {addr[0]}:{addr[1]}")
    while True:
        file_name = client_socket.recv(1024)
        if not file_name:
            handle_connection_close(client_socket, addr)
            break
        file_name = file_name.decode()
        print(f"[{threading.current_thread().name}] {addr[0]}:{addr[1]} asked for file --> '{file_name}'")
        
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
    RUNNING_THREADS = []
    
    server_socket = socket_setup(conn_tuple)
    with server_socket as server:
        #main server loop
        while SERVER_IS_RUNNING:
            r_list, w_list, e_list = select.select([sys.stdin, server], [], [])
            for ready_sock in r_list:
                
                if ready_sock is sys.stdin:
                    command = input()
                    if command.upper() == "LEAVE":
                        if RUNNING_THREADS:
                            print("There are still clients being served:")
                            print("\n".join([f"{addr[0]}:{addr[1]}" for _, addr in RUNNING_THREADS]))
                            for client in RUNNING_THREADS:
                                client[0].join()
                        SERVER_IS_RUNNING = False
                        break   
                    else:
                        print("Unknown command.")
                
                elif ready_sock is server:
                    client_socket, remote_addr = server.accept()
                    client_thread = threading.Thread(target=client_loop, args=(client_socket, remote_addr))
                    RUNNING_THREADS.append((client_thread, remote_addr))
                    client_thread.start()                   

def main():
    print("Starting concurrent server")
    addr = (configs.HOST, configs.PORT)
    start(addr)

if __name__ == "__main__":
    main()
