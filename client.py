from colorama import Fore, Style, init  
import socket
import time
import threading
import sys

PORT = 5050
HEADER = 1024
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"


def connect():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        print(f"Connected to server at {ADDR}")
        return client
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
        return None


def send(client, msg):
    try:
        message = msg.encode(FORMAT)
        client.send(message)
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")

def receive(client):
    """Receives messages from the server in a loop."""
    while True:
        try:
            message = client.recv(HEADER).decode()
            if message:
                sys.stdout.write("\033[K")  # Clear the line
                sys.stdout.write(f"\r{Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}\n")  # Print received message

                # Reprint the input prompt without causing duplicate "You:"
                sys.stdout.write("You: ")
                sys.stdout.flush()
            else:
                break
        except Exception:
            break    
        
def send_username(client, username):
    """Sends the username to the server."""
    send(client, username)  # Send the username as the first message to the server

   
    
def handle_input(connection, username):
    """Handles user input in a separate thread."""

    send_username(connection, username)  # Send username when the client joins
    
    while True:
        sys.stdout.write("You: ")
        sys.stdout.flush()
        msg = input("")

        if msg.lower() == 'q':
            break
                
        full_msg = f"{Fore.BLUE}{username}: {msg}{Style.RESET_ALL}"
        send(connection, full_msg)

def start():
    init()
    
    answer = input('Would you like to connect (yes/no)? ')
    if answer.lower() != 'yes':
        print("Exiting program.")
        return

    connection = connect()
    
    if not connection:
        return
    
    username = input("Enter your username: ")
    
    # Start the thread for receiving messages from the server
    receiver_thread = threading.Thread(target=receive, args=(connection,))
    receiver_thread.daemon = True  # Ensure this thread exits when the main thread does
    receiver_thread.start()
     
    try:
        # Handle user input on the main thread
        handle_input(connection, username)
        
    except KeyboardInterrupt:
        print(f"\n{username} has been Disconnected!")
    finally:
        send(connection, DISCONNECT_MESSAGE)
        time.sleep(1)
        connection.close()
        print('Disconnected')


start()