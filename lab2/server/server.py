import socket, sys, json, select
import core, configs

SOCK = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM)

def start(socket_tuple):
    with SOCK as s:
        s.bind(socket_tuple)
        if s is None:
            print("Error on socket binding")
            sys.exit(1)
        s.listen()
        print(f"Listening on port {socket_tuple[1]}...")

        #main server loop
        while True:
            conn, remote_addr = s.accept()
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
