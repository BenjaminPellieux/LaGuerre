import socket

def build_message(key, params):
    return f"{key}|{'|'.join(map(str, params))}".encode()

host = "localhost"
port = 5000

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))
print(f"Connection on {port}")
socket.send("JOIN|EKIP".encode())
while True:
    msg_serv=socket.recv(255).decode()
    print(f"RECU: {msg_serv=}  ")
    socket.send(build_message("MOVE", [1, "N"]))

print("Close")
socket.close()