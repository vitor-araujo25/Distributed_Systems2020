import socket
import sys

PORT = 9000
HOST = ""
addr = (HOST, PORT)

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM)

#ao terminar o loop, fecha automaticamente a conexão
with sock as s:
    s.bind(addr)
    s.listen()
    if s is None:
        print("Erro ao abrir socket")
        sys.exit(1)
    print(f"Escutando por conexões na porta {PORT}")
    conn, remote_addr = s.accept()
    with conn:
        print(f"Conexão com {remote_addr[0]}:{remote_addr[1]} estabelecida")
        while True:
            msg = conn.recv(1024)
            print(f"Recebi: {msg.decode()}")
            if msg.decode() == "CLOSE":
                break
            conn.sendall(msg)

