from config import *
import config
import const


def create_request(client_socket):
    """
    If a user wants to start a chat with another user, he will send "PRCRSuname1~msg" to the server,
    the server will save a request in its memory, and it will forward the message to the dst.
    if the dst will accept the request ("PRCACuname1" message), a connection will be established

    :param client_socket:
    :return:
    """
    data = client_socket.recv(config.MAX_MSG_LENGTH).decode()
    dst = data.split("~")[0]
    src = config.get_uname(client_socket)
    if src in config.active_private or src in config.active_private.values():
        client_socket.send(const.already_in_private_chat_error.encode())
        return
    if dst not in config.clients:
        client_socket.send(const.user_not_connected_error.encode())
        return
    config.clients[dst].send((const.private_chat_request_code + src + ' ').encode())  # TO DO - encrypt with dst
    # public key
    client_socket.send(const.private_chat_request_sent_code.encode())
    config.private_requests[src] = dst  # TO DO - encrypt with servers key
    return


def create_chat(client_socket):
    """


    :param client_socket:
    :return:
    """
    data = client_socket.recv(config.MAX_MSG_LENGTH).decode()
    dst = data.split("~")[0]
    src = config.get_uname(client_socket)
    if (src, dst) in config.private_requests.items() or (dst, src) in config.private_requests.items():
        if src in config.active_private or src in config.active_private.values():
            client_socket.send(const.already_in_private_chat_error.encode())
            return
        if dst not in config.clients:
            client_socket.send(const.user_not_connected_error.encode())
            return
        config.active_private[config.clients[src]] = config.clients[dst]
        return
    else:
        client_socket.send(const.chat_request_pair_error.encode())
        return


def handle_chat(client_socket):
    src = client_socket
    if src in config.active_private:
        dst = config.active_private[src]
    else:
        dst = config.get_by_value(src, config.active_private)
    dst.send(src.recv(1024))
