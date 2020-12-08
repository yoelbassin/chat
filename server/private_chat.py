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
    # get the destination user name
    dst = data.split("~")[0]
    # get the source user name
    src = config.get_uname(client_socket)

    # if the client already has an active request for a private chat - error
    if src in config.private_requests or src in config.private_requests.values():
        client_socket.send(const.already_has_private_chat_request_code.encode())
        return

    # if the client is already in a private chat - error
    if src in config.active_private or src in config.active_private.values():
        client_socket.send(const.already_in_private_chat_error.encode())
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


def create_chat(client_socket):
    """


    :param client_socket:
    :return:
    """
    data = client_socket.recv(config.MAX_MSG_LENGTH).decode()
    print(data)
    # get the destination user name
    dst = data.split("~")[0]
    # get the source user name
    src = config.get_uname(client_socket)
    print(config.private_requests)
    print(src, dst)
    # if there exists a request for a private chat for dst and src
    if (src, dst) in config.private_requests.items() or (dst, src) in config.private_requests.items():
        # the source already in a private chat - error
        """
        if src in config.active_private or src in config.active_private.values():
            client_socket.send(const.already_in_private_chat_error.encode())
            print("already in private chat")
            return"""
        # if the destination user is not connected - error
        if dst not in config.clients:
            client_socket.send(const.user_not_connected_error.encode())
            print("user not connected")
            return

        # if everything is ok, create a chat room
        config.active_private[config.clients[src]] = config.clients[dst]

        config.clients[src].send((const.private_chat_accepted_code + dst).encode())
        config.clients[dst].send((const.private_chat_accepted_code + src).encode())

        print("chat created")
        return
    # if there isn't a request for a private chat for dst and src - error
    else:
        client_socket.send(const.chat_request_pair_error.encode())
        print("request error")
        return


def decline_chat(client_socket):
    """


    :param client_socket:
    :return:
    """
    data = client_socket.recv(config.MAX_MSG_LENGTH).decode()
    # get the destination user name
    dst = data.split("~")[0]
    # get the source user name
    src = config.get_uname(client_socket)
    print(config.private_requests)
    print(src, dst)
    # if there exists a request for a private chat for dst and src
    if (src, dst) in config.private_requests.items() or (dst, src) in config.private_requests.items():
        if src in config.private_requests:
            config.private_requests.pop(src)
        else:
            config.private_requests.pop(dst)
        config.clients[src].send((const.private_chat_denied_code + dst).encode())
        config.clients[dst].send((const.private_chat_denied_code + src).encode())


def handle_chat(client_socket):
    """
    handle an active chat

    :param client_socket:
    :return:
    """
    # get the destination socket
    if client_socket in config.active_private:
        dst = config.active_private[client_socket]
    else:
        dst = config.get_by_value(client_socket, config.active_private)

    try:
        code = client_socket.recv(5).decode()
    except ConnectionResetError:
        # If the client disconnected, return false
        return False

    # if the code type is 'EXIT', end the private chat connection and update the destination
    # TO DO

    # if the data type is a message, forward it to the destination
    if code == const.msg_code:
        data = const.msg_code

    elif code == const.accept_private_chat_code:
        end_chat(client_socket)
        create_chat(client_socket)
        return True

    # if code was denial of a chat request
    elif code == const.deny_private_chat_code:
        decline_chat(client_socket)
        return True
    else:
        data = code

    # forward the data to the destination
    data += client_socket.recv(1024).decode()
    dst.send(data.encode())
    # return that everything is ok
    return True


def end_chat(client_socket):
    # get the destination socket
    if client_socket in config.active_private:
        dst = config.active_private[client_socket]
    else:
        dst = config.get_by_value(client_socket, config.active_private)
    dst.send(const.end_chat_code.encode())
    if dst in config.active_private:
        config.active_private.pop(dst)
    else:
        config.active_private.pop(client_socket)