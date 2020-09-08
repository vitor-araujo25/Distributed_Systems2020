import socket

def start(remote_addr):
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM)

    with sock as s:
        try:
            s.connect(remote_addr)
            conn = s.getpeername()
            print(f"Connected to {conn[0]}:{conn[1]} successfully.")
            while True: 
                msg = input("Type the file name: ")
                if msg == "":
                    print("\nEnding connection...")
                    s.sendall(b"CLOSE")
                    break
                s.sendall(msg.encode())
                echo = s.recv(1024)
                print(f"Answer: {echo.decode()}")
        except (KeyboardInterrupt, SystemExit):
            print("\nEncerrando conexão...")
            s.sendall(b"CLOSE")