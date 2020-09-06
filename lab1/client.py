import socket

HOST = "127.0.0.1"
PORT = 9000
remote_addr = (HOST, PORT)

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM)

with sock as s:
    try:
        s.connect(remote_addr)
        conn = s.getpeername()
        print(f"Conectado a {conn[0]}:{conn[1]}")
        while True: 
            msg = input("Digite a mensagem: ")
            if msg == "CLOSE":
                print("\nEncerrando conexão...")
                s.sendall(b"CLOSE")
                break
            s.sendall(msg.encode())
            echo = s.recv(1024)
            print(f"Resposta recebida: {echo.decode()}")
    except (KeyboardInterrupt, SystemExit):
        print("\nEncerrando conexão...")
        s.sendall(b"CLOSE")
        
