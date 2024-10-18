from colorama import Fore, Style, init
import threading
import socket
import time
import sys

PORT = 5050
HEADER = 1024
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
clients_lock = threading.Lock()

def remove_client(username, conn):
    """Remove client from the clients dictionary and close the connection."""
    with clients_lock:
        if username in clients:
            del clients[username]
            conn.close()

def broadcast(message, sender = None, recipient = None):
    """Broadcasts a message to all connected clients except the sender.
    If a recipient is specified, only send it to that recipient."""
    with clients_lock:
        if recipient:  # Send message to a specific user
            if recipient in clients:
                try:
                    clients[recipient].send(message)
                except Exception as e:
                    print(f"[ERROR] Could not send message to {recipient}: {e}")
                    remove_client(recipient, clients[recipient])
        else:  # Broadcast message to all users except sender
            for username, client in clients.items():
                if client != sender:
                    try:
                        client.send(message)
                    except Exception as e:
                        print(f"[ERROR] Could not send message to {username}: {e}")
                        remove_client(username, client)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} Connected")
    
    try:
        # The first message received from the client should be the username
        username = conn.recv(HEADER).decode(FORMAT)
        with clients_lock:
            clients[username] = conn
        print(f"[NEW USER] {username} connected.")  

        # Announce the new client connection
        join_message = f"{Fore.GREEN}{username} has joined the chat.{Style.RESET_ALL}".encode(FORMAT)
        broadcast(join_message, conn)
        
        connected = True
        while connected:
            msg = conn.recv(HEADER).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False
                break

            # Check if the message contains an @name (mention)
            if "@" in msg:
                mentioned_user = msg.split('@')[1].split()[0]  # Get the username after '@'
                if mentioned_user in clients:
                    private_msg = f"{Fore.MAGENTA}[PRIVATE] {msg}{Style.RESET_ALL}".encode(FORMAT)
                    broadcast(private_msg, conn, recipient = mentioned_user)  # Send only to the mentioned user
                    print(f"[PRIVATE] {msg}")
                else:
                    error_msg = f"{Fore.RED}User @{mentioned_user} not found.{Style.RESET_ALL}".encode(FORMAT)
                    conn.send(error_msg)  # Notify the sender that the user was not found
            else:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                formatted_msg = f"[{timestamp}] {msg}".encode(FORMAT)
                broadcast(formatted_msg, conn)
                print(f"[{timestamp}] {msg}")
                
                sys.stdout.write("Server: ")
                sys.stdout.flush()
            
    except Exception as e:
        print(f"[ERROR] {e}")
    
    finally:
        remove_client(username, conn)
        leave_message = f"{Fore.RED}{username} has left the chat.{Style.RESET_ALL}".encode(FORMAT)
        broadcast(leave_message)
        print(f"[DISCONNECTED] {username} has left.")

def server_broadcast_input():
    """Handles server-side input to send messages to all connected clients."""
    while True:
        sys.stdout.write("Server: ")
        sys.stdout.flush()
        msg = input("")

        if msg:
            formatted_msg = f"{Fore.YELLOW}[SERVER]: {msg}{Style.RESET_ALL}".encode(FORMAT)
            broadcast(formatted_msg)
            # print(f"[SERVER]: {msg}")

def start():
    init()
        
    print(f"[LISTENING] Server is listening on {SERVER}")
    server.listen()
    
    # Start a thread to handle server input for broadcasting
    input_thread = threading.Thread(target=server_broadcast_input, daemon=True)
    input_thread.start()
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[Active Connections] {threading.active_count() - 1}")

print("[STARTING] Server is starting ...")
start()