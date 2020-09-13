import socket, sys, json
import core, configs

def socket_setup(socket_tuple):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(socket_tuple)
    if sock is None:
        print("Error on socket binding")
        sys.exit(1)
    sock.listen()
    print(f"Listening on port {socket_tuple[1]}...")
    return sock

def start(conn_tuple):
    server_socket = socket_setup(conn_tuple)
    with server_socket as server:
        #main server loop
        while True:
            conn, remote_addr = server.accept()
            with conn:
                print(f"Connection established to {remote_addr[0]}:{remote_addr[1]}")

                #client connection loop
                while True:
                    file_name = conn.recv(1024)
                    if not file_name:
                        print("Connection closed by client.")
                        break
                    file_name = file_name.decode()
                    print(f"File name received: {file_name}")
                    
                    #invoking word counting method at core layer 
                    try:
                        word_count = core.count_words(file_name)
                    except OSError as e:
                        conn.sendall(b"ERROR")
                        print("File access error. Resuming listening for more file names...")
                        continue
                    except Exception as e:
                        conn.sendall(b"ERROR")
                        print(f"Unexpected exception: {e}")
                        continue
                    else:
                        conn.sendall(json.dumps(word_count).encode('utf-8'))

def main():
    print("Starting server")
    addr = (configs.HOST, configs.PORT)
    start(addr)

if __name__ == "__main__":
    main()
