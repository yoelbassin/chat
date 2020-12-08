import config
import const


def recv_private_chat_request():
    data = config.client.recv(1024).decode()
    src_name = data.split("~")[0]
    config.active_requests.append(src_name)
    print(src_name + " sent you a private chat request, would you like to accept it? Y/N")
    return


def answer_private_chat_request(message):
    src_name = config.active_requests[-1]
    while True:
        if message.upper() == 'Y':
            config.client.send((const.accept_private_chat_code + src_name).encode())
            config.active_requests.pop()
            config.active_chat = '[' + src_name + ']$~'
            return
        elif message.upper() == 'N':
            config.client.send((const.deny_private_chat_code + src_name).encode())
            config.active_requests.pop()
            return
        message = '{}'.format(input(''))


def create_private_chat_request(name):
    config.active_requests.append(name)
    config.client.send((const.private_chat_request_code+name).encode())


def handle_chat(message):
    if message == 'Q':
        pass
    else:
        config.client.send((const.msg_code+message).encode())