import socket
import sys
import core
import json
import configs

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM)

def start(socket_tuple):
    with sock as s:
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
                        print("File name reception timed out.")
                        break
                    file_name = file_name.decode()
                    if file_name == "CLOSE":
                        print("CLOSE received.")
                        break
                    print(f"File name received: {file_name}")
                    
                    #invoking word counting method at core layer 
                    try:
                        word_count = core.count_words(file_name)
                    except OSError as e:
                        conn.sendall(b"ERRO")
                        print(f"DEBUG: {e}")
                        print("File access error. Resuming listening for more file names...")
                        continue
                    except Exception as e:
                        conn.sendall(b"ERRO")
                        print(f"Unexpected exception: {e.message}")
                        continue
                    else:
                        conn.sendall(json.dumps(word_count).encode('utf-8'))

                print(f"Ending connection to {remote_addr[0]}:{remote_addr[1]}")

def main():
    print("Starting server")
    addr = (configs.HOST, configs.PORT)
    start(addr)

if __name__ == "__main__":
    main()