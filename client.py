import socket
import time

remote_addr = ("127.0.0.1", 9000)

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM)

with sock as s:
    s.connect(remote_addr)
    while True: 
        print("Digite a mensagem: ")
        msg = input()
        if msg == "CLOSE":
            print("Encerrando conexão...")
            s.sendall(b"CLOSE")
            break
        s.sendall(msg.encode())
        echo = s.recv(1024)
        print(f"Resposta enviada: {echo.decode()}")
