import select
import config
from config import *
import const
import ssl


def connect(server_socket, context):
    client_socket, client_address = server_socket.accept()
    client_socket = context.wrap_socket(client_socket, server_side=True)
    print("New connection: ", client_address)
    config.client_sockets.append(client_socket)
    config.socket_addresses[client_socket] = client_address


def handle_user(client_socket):
    try:
        code = client_socket.recv(const.CODE_LEN).decode().upper()
        data = client_socket.recv(4096).decode()
    except ConnectionResetError:
        print(config.socket_addresses[client_socket], ' disconnected')
        config.client_sockets.remove(client_socket)
        config.socket_addresses.pop(client_socket)
        return
    print(data)
    print(config.users)
    if code == const.login_code:
        if len(data.split("~")) != 2:
            client_socket.send("Please enter your credentials".encode())
            return
        uname = data.split("~")[0]
        pwd = data.split("~")[1]
        if uname in config.clients:
            client_socket.send("User already connected".encode())
            return
        if uname in config.users:
            salt = config.users[uname][0]
            pwd = bcrypt.hashpw(pwd.encode(), salt.encode()).decode()
            if config.users[uname][1] == pwd:
                print(uname + ' connected')
                client_socket.send(const.login_successfully_code.encode())
                config.clients[uname] = client_socket
        else:
            client_socket.send("wrong credentials".encode())
            return
    if code == const.register_code:
        print(data)
        if len(data.split("~")) != 2:
            client_socket.send("Please enter your registration credentials".encode())
            return
        uname = data.split("~")[0]
        pwd = data.split("~")[1]
        # TO DO - password confirmation
        if uname in config.users:
            client_socket.send("Users already exists".encode())
            return
        else:
            salt = bcrypt.gensalt()
            print(salt)
            print(pwd)
            pwd = bcrypt.hashpw(pwd.encode(), salt)
            config.users[uname] = (salt.decode(), pwd.decode())
            print("New user joined\nnickname: " + uname)
            client_socket.send(const.login_successfully_code.encode())
            config.clients[uname] = client_socket
            update_db()
            print("updated")
