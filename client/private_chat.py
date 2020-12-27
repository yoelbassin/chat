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
import rsa
import cryptog


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
            config.active_chat = src_name
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
    # encrypted_message = rsa.encrypt(message.encode(), config.dst_pub)
    # print(encrypted_message)
    # config.client.send(const.msg_code.encode() + encrypted_message)
    encrypted_message = cryptog.encrypt_message(message)
    config.client.send(const.msg_code.encode() + encrypted_message)


def exit_private_chat():
    config.active_chat = ''
    config.in_chat = False
    config.client.send(const.exit_private.encode())


def wait_for_connection():
    """


    :return:
    """
    animation_c = 0
    animation = ['|', '/', '-', '\\']
    while True:  # making valid connection
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

            # if code is a private chat request code
            if code == const.private_chat_request_code:
                config.lock = True
                recv_private_chat_request(packet)

            # if code is accepted private chat code
            elif code == const.private_chat_accepted_code:
                name = config.rem_req(packet)
                print("chat with " + name + " started")
                config.active_chat = name
                config.in_chat = True
                cryptog.key_ex()
                return True

            elif code == const.private_chat_request_sent_code:
                src = packet[5:]
                print("Private chat request sent successfully to " + src)

            elif code == const.user_not_connected_error:
                print(config.rem_req(packet) + " not connected")
                return False

            elif code == const.private_chat_denied_code:
                print(config.rem_req(packet) + " refused your invite")
                return False

            elif code == const.chat_request_pair_error:
                print("Connection error: Cant connect with " + config.rem_req(
                    packet) + "\nRequest error or request is no longer active")
                return False

            elif code == const.already_has_private_chat_request_code:
                print("You already have an active request")
                config.rem_req(packet)
                return False

            elif code == const.already_in_private_chat_error:
                print("You still in a private chat!")
                config.rem_req(packet)
                return False

            else:
                print(code)  # for debugging purposes
                continue

        except Exception as e:
            print(str(e))
