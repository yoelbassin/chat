import socket
import select

from config import *
from const import *
import const
import config
from establish_connection import *
import private_chat


def main():
    open_db()

    print(config.users)

    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Listening for connections...")

    while True:
        read_list = config.client_sockets + [server_socket]
        ready_to_read, ready_to_write, in_error = select.select(read_list, [], [])
        for current_socket in ready_to_read:
            # new connection
            if current_socket is server_socket:
                handle_user(server_socket)
            else:
                if current_socket in config.active_private or current_socket in config.active_private.values():
                    private_chat.handle_chat(current_socket)
                    return
                print("New data received: ")
                code = current_socket.recv(const.CODE_LEN).decode().upper()
                print(code)
                if code == const.private_chat_request_code:
                    private_chat.create_request(current_socket)
                elif code == const.accept_private_chat_code:
                    private_chat.create_chat(current_socket)
                elif code == "EXIT":
                    print("Connection Closed")
                    config.client_sockets.remove(current_socket)
                    current_socket.close()
                else:
                    # empty socket
                    current_socket.recv(1024)


if __name__ == "__main__":
    main()
