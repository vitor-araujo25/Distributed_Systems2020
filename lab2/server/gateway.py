import socket
import sys
import core

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
                    if file_name.decode() == "CLOSE":
                        print("CLOSE received.")
                        break
                    print(f"File name received: {file_name.decode()}")
                    
                    #invoking word processing method at core layer 
                    try:
                        word_count = core.count_words(file_name)
                    except OSError:
                        conn.sendall(b"ERRO")
                        print("File access error. Resuming listening for more file names...")
                        continue
                    except Exception as e:
                        print(f"Unexpected exception: {e.message}")
                        break
                    else:
                        conn.sendall(b"Processed")

                print(f"Ending connection to {remote_addr[0]}:{remote_addr[1]}")


def partition_message(full_dict):
    pass