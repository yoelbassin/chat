import socket
import select

from Chat.server.utils import *
from Chat.server.establish_connection import handle_user


def main():
    global client_sockets, clients, users

    users = open_db()

    print(users)

    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Listening for connections...")

    while True:
        read_list = client_sockets + [server_socket]
        ready_to_read, ready_to_write, in_error = select.select(read_list, [], [])
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                handle_user(server_socket)
            else:
                print("New data received: ")
                data = current_socket.recv(MAX_MSG_LENGTH).decode()
                print(data)
                for client in client_sockets:
                    if client != current_socket:
                        client.send(data.encode())
                if data == "":
                    print("Connection Closed")
                    client_sockets.remove(current_socket)
                    current_socket.close()


if __name__ == "__main__":
    main()
