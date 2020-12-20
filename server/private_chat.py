from config import *
import config
import const


def create_request(client_socket, msg):
    """
    If a user wants to start a chat with another user, he will send "PRCRSuname1~msg" to the server,
    the server will save a request in its memory, and it will forward the message to the dst.
    if the dst will accept the request ("PRCACuname1" message), a connection will be established

    :param msg:
    :param client_socket:
    :return:
    """
    data = msg[const.CODE_LEN:]
    print(data)
    # get the destination user name
    dst = data.split("~")[0]
    # get the source user name
    src = config.get_uname(client_socket)

    if src == dst:
        client_socket.send((const.chat_request_pair_error+src).encode())
        return

    # if the client (source) already has an active request for a private chat - error
    if src in config.private_requests.values():
        client_socket.send((const.already_has_private_chat_request_code+dst).encode())
        return

    # if the client sent a request for a private chat (TO DO - 10 seconds countdown)
    if src in config.private_requests:
        client_socket.send((const.already_has_private_chat_request_code+dst).encode())
        return

    # if the client is already in a private chat - error
    if src in config.active_private or src in config.active_private.values():
        client_socket.send((const.already_in_private_chat_error+dst).encode())
        return

    # if the destination user is not connected to the server
    if dst not in config.clients:
        client_socket.send(const.user_not_connected_error.encode())
        return

    # if the client is connected to the server and everything is ok
    config.clients[dst].send((const.private_chat_request_code + src).encode())  # TO DO - encrypt with dst
    # public key
    client_socket.send((const.private_chat_request_sent_code + dst).encode())
    config.private_requests[src] = dst  # TO DO - encrypt with servers key
    return


def answer_chat_req(client_socket, msg):
    """


    :param msg:
    :param client_socket:
    :return:
    """

    def accept_chat():
        # the source already in a private chat - error
        """
        if src in config.active_private or src in config.active_private.values():
            client_socket.send(const.already_in_private_chat_error.encode())
            print("already in private chat")
            return"""
        # if the destination user is not connected - error
        if dst not in config.clients:
            config.clients[src].send(const.user_not_connected_error.encode())
            print("user not connected")
            return

        # if the client is already in a private chat - error
        end_chat(client_socket)

        # if everything is ok, create a chat room
        config.active_private[config.clients[src]] = config.clients[dst]
        # send to the source that the request was accepted
        config.clients[src].send((const.private_chat_accepted_code + dst).encode())
        # send to the destination that the request was accepted
        config.clients[dst].send((const.private_chat_accepted_code + src).encode())

        print("chat created")
        return

    def decline_chat():
        """


        :return:
        """
        config.clients[dst].send((const.private_chat_denied_code + src).encode())
        # config.clients[dst].send((const.private_chat_denied_code + src).encode())

    data = msg[const.CODE_LEN:]
    code = msg[:const.CODE_LEN].upper()
    print(data)
    # get the destination user name
    dst = data.split("~")[0]
    # get the source user name
    src = config.get_uname(client_socket)
    print(config.private_requests)
    print(src, dst)
    # if there exists a request for a private chat for dst and src
    if (src, dst) in config.private_requests.items() or (dst, src) in config.private_requests.items():
        if code == const.deny_private_chat_code:
            decline_chat()
        elif code == const.accept_private_chat_code:
            accept_chat()
        if src in config.private_requests:
            config.private_requests.pop(src)
        else:
            config.private_requests.pop(dst)
    # if there isn't a request for a private chat for dst and src - error
    else:
        client_socket.send((const.chat_request_pair_error+dst).encode())
        print("request error or request is no longer active")
        return


def handle_chat(client_socket, msg):
    """
    handle an active chat

    :param msg:
    :param client_socket:
    :return:
    """
    code = msg[:const.CODE_LEN].upper()

    # get the destination socket
    if client_socket in config.active_private:
        dst = config.active_private[client_socket]
    elif client_socket in config.active_private.values():
        dst = config.get_by_value(client_socket, config.active_private)
    else:
        return const.private_chat_not_exist

    # if the code type is 'EXITP', end the private chat connection and update the destination
    if code == const.exit_private:
        end_chat(client_socket)
        return const.exit_private

    # if the data type is a message, forward it to the destination
    if code == const.msg_code:
        data = const.msg_code
    else:
        data = code

    # forward the data to the destination
    try:
        data += msg[const.CODE_LEN:]
    except ConnectionResetError:
        return const.disconnected
    dst.send(data.encode())
    # return that everything is ok
    return const.success


def end_chat(client_socket):
    # get the destination socket
    if client_socket in config.active_private:
        dst = config.active_private[client_socket]
    elif client_socket in config.active_private.values():
        dst = config.get_by_value(client_socket, config.active_private)
    else:
        return False
    dst.send(const.end_chat_code.encode())
    if dst in config.active_private:
        config.active_private.pop(dst)
    else:
        config.active_private.pop(client_socket)


def close_private_request(client_socket):
    name = config.get_uname(client_socket)
    if name in config.private_requests:
        config.private_requests.pop(name)
