import time
from io import StringIO

import ui
import config
import const
import sys
import timeout
from termcolor import cprint
import keyboard
import threading


def recv_private_chat_request(packet):
    """
    receive the private chat invitation and update the user

    :return:
    """
    data = packet[5:]
    src_name = data.split("~")[0]
    # add the invitation the the invitation list
    config.active_requests.append(src_name)
    timeout.err = False

    answer_private_chat_request(ui.new_connection(src_name))
    return


def answer_private_chat_request(message):
    """
    answer a private chat invitation

    :param message:
    :return:
    """
    src_name = config.active_requests[0]
    while True:
        # If the invitation is accepted, send accept message to the server and remove it from the active requests
        # list and update the active chat field
        if message:
            config.client.send((const.accept_private_chat_code + src_name).encode())
            config.active_requests.pop()
            config.active_chat = '[' + src_name + ']$~'
            return

        # If the invitation is declined, send decline message to the server and remove it from the active requests list
        else:
            config.client.send((const.deny_private_chat_code + src_name).encode())
            config.active_requests.pop()
            return


def create_private_chat_request(name):
    """
    create a new private chat request by sending a request to the server for the specific user

    :param name:
    :return:
    """
    if not config.active_chat:
        config.active_requests.append(name)
        config.client.send((const.private_chat_request_code + name).encode())
        return True
    return False


def handle_chat(message):
    config.client.send((const.msg_code + message).encode())


def exit_private_chat():
    config.active_chat = ''
    config.flag = False
    config.client.send(const.exit_private.encode())


def wait_for_connection():
    """


    :return:
    """
    config.flag = True
    animation_c = 0
    animation = ['|', '/', '-', '\\']
    while config.flag:  # making valid connection
        try:
            if not config.incoming_que:
                sys.stdout.write('\rwaiting ' + animation[animation_c % 4])
                animation_c += 1
                sys.stdout.flush()
                time.sleep(0.1)
                if keyboard.is_pressed('q'):
                    print()
                    if config.active_requests:
                        config.active_requests.pop()
                    config.client.send(const.close_private_request_code.encode())
                    return False
                continue
            packet = config.incoming_que.popleft()
            code = packet[:5]

            print(code)

            # if code is a private chat request code
            if code == const.private_chat_request_code:
                config.lock = True
                recv_private_chat_request(packet)

            # if code is accepted private chat code
            elif code == const.private_chat_accepted_code:
                name = packet[5:].split('~')[0]
                print("private chat started with " + name)
                print('number of current threads is ', threading.active_count())
                if name in config.active_requests:
                    config.active_requests.remove(name)
                    config.active_chat = '[' + name + ']$~'
                return True

            elif code == const.private_chat_request_sent_code:
                src = packet[5:]
                print("Private chat request sent successfully to " + src)

            elif code == const.user_not_connected_error:
                print("destination not connected")
                if config.active_requests: config.active_requests.pop()
                config.client.send(const.close_private_request_code.encode())
                return False

            elif code == const.private_chat_denied_code:
                src = packet[5:]
                if src in config.active_requests:
                    config.active_requests.remove(src)
                    print(src + " refused your invite")

            else:
                continue

        except Exception as e:
            print(str(e))
