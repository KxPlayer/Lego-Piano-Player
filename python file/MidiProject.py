import socket

HOST = 'localhost'
PORT = 5000

server = socket.socket()
server.bind((HOST, PORT))
server.listen(1)
print("Waiting for connection...")
conn, addr = server.accept()
print("Connected by", addr)

while True:
    data = conn.recv(1024)
    if not data:
        break
    print("Received:", data.decode().strip())

conn.close()
