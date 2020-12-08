# Coded by Yashraj Singh Chouhan
import socket
import threading
import time
import const
import config
import private_chat
import sys
import establish_connection


def receive():
    while True:  # making valid connection
        try:
            code = config.client.recv(5).decode()
            if code != '':
                print(code)

            # if code is a private chat request code
            if code == const.private_chat_request_code and not config.active_chat:
                private_chat.recv_private_chat_request()

            # if code is accepted private chat code
            elif code == const.private_chat_accepted_code:
                config.active_chat = '[' + config.active_chat + ']$~'

            # if code is message code
            elif code == const.msg_code:
                message = config.client.recv(1024).decode()
                if message != '':
                    print(config.active_chat + message)
            else:
                config.client.recv(1024)

        except Exception as e:  # case on wrong ip/port details
            print("An error occurred: " + str(e))
            config.client.close()
            break


def write():
    while True:  # message layout
        # message = '{}: {}'.format(uname, input(''))
        message = '{}'.format(input(''))
        if len(config.active_requests) > 0:
            private_chat.answer_private_chat_request(message)
        elif 'send private to' in message and not config.active_chat:
            private_chat.create_private_chat_request(input('uname: '))
        else:
            config.client.send(message.encode())


receive_thread = threading.Thread(target=receive)  # receiving multiple messages
write_thread = threading.Thread(target=write)  # sending messages


def main():
    if not establish_connection.establish_connection():
        print("Exiting program")
        return
    receive_thread.start()
    write_thread.start()


if __name__ == "__main__":
    main()
