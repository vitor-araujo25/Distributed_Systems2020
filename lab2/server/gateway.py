import socket
import sys
from . import core

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM)

def start(socket_tuple):
    with sock as s:
        s.bind(socket_tuple)
        s.listen()
        if s is None:
            print("Error on socket binding")
            sys.exit(1)
        print(f"Listening on port {PORT}...")
        conn, remote_addr = s.accept()
        with conn:
            print(f"Connection established to {remote_addr[0]}:{remote_addr[1]}")
            while True:
                file_name = conn.recv(1024)
                print(f"File name received: {file_name.decode()}")
                if file_name.decode() == "CLOSE":
                    break
                try:
                    word_count = core.count_words(file_name)
                except OSError:
                    conn.sendall(b"ERRO")
                    continue
                except Exception as e:
                    print(f"Unexpected exception: {e.message}")
                    sys.exit(1)