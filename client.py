import socket

remote_addr = ("127.0.0.1", 9000)

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM | socket.SOCK_NONBLOCK
)

with sock as s:
    s.connect(remote_addr)
    while True: 
        print("Digite a mensagem: ")
        msg = input()
        
        s.sendall(msg.encode())
        echo = s.recv(1024)
        print(echo)
