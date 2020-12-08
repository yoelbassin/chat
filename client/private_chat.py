import config
import const


def recv_private_chat_request():
    """
    receive the private chat invitation and update the user

    :return:
    """
    data = config.client.recv(1024).decode()
    src_name = data.split("~")[0]
    # add the invitation the the invitation list
    config.active_requests.append(src_name)
    print(src_name + " sent you a private chat request, would you like to accept it? Y/N")
    return


def answer_private_chat_request(message):
    """
    answer a private chat invitation

    :param message:
    :return:
    """
    src_name = config.active_requests[-1]
    while True:
        # If the invitation is accepted, send accept message to the server and remove it from the active requests
        # list and update the active chat field
        if message.upper() == 'Y':
            config.client.send((const.accept_private_chat_code + src_name).encode())
            config.active_requests.pop()
            config.active_chat = '[' + src_name + ']$~'
            return

        # If the invitation is declined, send decline message to the server and remove it from the active requests list
        elif message.upper() == 'N':
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
    config.active_requests.append(name)
    config.client.send((const.private_chat_request_code+name).encode())


def handle_chat(message):
    if message == 'Q':
        pass
    else:
        config.client.send((const.msg_code+message).encode())