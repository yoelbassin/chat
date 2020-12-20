import socket
import select

from config import *
from const import *
import const
import config
import establish_connection
import private_chat
import ssl


def main():
    open_db()

    print(config.users)
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="cert.pem", keyfile='key.pem')
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Listening for connections...")

    while True:
        read_list = config.client_sockets + [server_socket]
        ready_to_read, ready_to_write, in_error = select.select(read_list, [], [])
        # run on all the sockets with new data:
        for current_socket in ready_to_read:
            # new connection
            if current_socket is server_socket:
                establish_connection.connect(server_socket, context)
            elif current_socket not in config.clients.values():
                establish_connection.handle_user(current_socket)
            else:

                print("New data received: ")
                try:
                    msg = current_socket.recv(config.MAX_MSG_LENGTH).decode()
                # if an error has occurred, close the connection with the socket
                except ConnectionResetError:
                    config.end_connection_with_socket(current_socket)
                    continue

                code = msg[:5].upper()

                print(code)

                # if code is a private chat request
                if code == const.private_chat_request_code:
                    private_chat.create_request(current_socket, msg)

                # if code is accepted private chat request
                elif code == const.accept_private_chat_code:
                    private_chat.answer_chat_req(current_socket, msg)

                # if code was denial of a chat request
                elif code == const.deny_private_chat_code:
                    private_chat.answer_chat_req(current_socket, msg)

                # if code is close private chat request
                elif code == const.close_private_request_code:
                    private_chat.close_private_request(current_socket)

                # if code is close existing private chat
                elif code in [const.msg_code, const.exit_private]:
                    private_chat.handle_chat(current_socket, msg)

                # if the connection have been closed, close the connection with the socket
                elif code == '' or code == 'EXIT':
                    print("Connection Closed")
                    config.end_connection_with_socket(current_socket)

                else:
                    continue


if __name__ == "__main__":
    main()
