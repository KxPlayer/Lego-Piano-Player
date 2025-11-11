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
    values = [int(value) for value in data.decode().split("\n") if value]
    print("Received:", values)

# to do:
'''
initialize all motors w/ motor objects
each motor has:
designated value -> check if received value is relevant (absolute value)
receive function
key press counter
up function -> choose angle to reset to
down function -> choose angle to press down
'''
conn.close()
