import threading
import time

import const
import config
import private_chat
from timeout import inputimeout, TimeoutOccurred
from termcolor import colored, cprint


def write():
    """
    get input from the user and send it to the server

    :return:
    """
    config.flag = True
    while config.flag:  # message layout
        time.sleep(0.2)
        try:
            config.lock = False
            message = inputimeout(timeout=5)
            cprint('[' + config.uname + ']$~', 'magenta', end='')
            cprint(message, 'white')
            if message == '\x1b':
                private_chat.exit_private_chat()
                break
        except TimeoutOccurred:
            continue
        if len(config.active_requests) > 0:
            config.lock = False

        elif config.active_chat:
            private_chat.handle_chat(message)
        else:
            config.client.send(message.encode())


def print_incoming():
    config.flag = True
    while config.flag:
        time.sleep(0.2)
        if config.lock:
            continue
        try:
            if not config.incoming_que:
                continue
            packet = config.incoming_que.popleft()
            code = packet[:5]

            # if code is a private chat request code
            if code == const.private_chat_request_code:
                config.lock = True
                private_chat.recv_private_chat_request(packet)

            # if code is accepted private chat code
            elif code == const.private_chat_accepted_code:
                name = packet[5:].split('~')[0]
                print("private chat started with " + name)
                if name in config.active_requests:
                    config.active_requests.remove(name)
                    config.active_chat = '[' + name + ']$~'

            # if code is message code
            elif code == const.msg_code:
                message = packet[5:]
                if message != '':
                    cprint(config.active_chat, 'blue', end='')
                    cprint(message, 'white')

            elif code == const.private_chat_request_sent_code:
                src = packet[5:]
                print("Private chat request sent successfully to " + src)

            elif code == const.end_chat_code:
                print("Chat with " + config.active_chat + " ended")

            elif code == const.private_chat_denied_code:
                src = packet[5:]
                print(src + " refused your invitation")
                if src in config.active_requests:
                    config.active_requests.remove(src)

        except Exception as e:
            print("An error has occurred: " + str(e))
            config.client.close()
            break


print_thread = threading.Thread(target=print_incoming)  # printing the packets received
write_thread = threading.Thread(target=write)  # sending messages