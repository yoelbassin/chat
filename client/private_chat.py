from io import StringIO

import ui
import config
import const
import sys
from main import write_thread
import timeout


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
    config.lock = False
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
        elif not message:
            config.client.send((const.deny_private_chat_code + src_name).encode())
            config.active_requests.pop()
            return

        # The user must either accept or refuse to a private chat invitation
        message = '{}'.format(input(''))


def create_private_chat_request(name):
    """
    create a new private chat request by sending a request to the server for the specific user

    :param name:
    :return:
    """
    if not config.active_chat:
        config.active_requests.append(name)
        config.client.send((const.private_chat_request_code+name).encode())
        return True
    return False


def handle_chat(message):
    if message == 'Q':
        pass
    else:
        config.client.send((const.msg_code+message).encode())