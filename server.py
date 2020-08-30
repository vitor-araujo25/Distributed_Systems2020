import socket

addr = ("", 9000)

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM | socket.SOCK_NONBLOCK
)

#ao terminar o loop, fecha automaticamente a conexão
with sock as s:
    s.bind(addr)
    s.listen()
    conn, addr = s.accept()
    with conn:
        msg = conn.recv(2**10)
        while True:
            if msg == "CLOSE":
                conn.sendall(b"'CLOSE' enviado. Encerrando conexão...")
                break
            conn.sendall(msg)  

