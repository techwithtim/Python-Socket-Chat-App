import threading
import socket

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = set()
clients_lock = threading.Lock()


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} Connected")

    try:
        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            with clients_lock:
                for c in clients:
                    c.sendall(f"[{addr}] {msg}".encode(FORMAT))

    finally:
        with clients_lock:
            clients.remove(conn)

        conn.close()


def start():
    print('[SERVER STARTED]!')
    server.listen()
    while True:
        conn, addr = server.accept()
        with clients_lock:
            clients.add(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start()
