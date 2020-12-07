import config
from config import *


def handle_user(server_socket):
    client_socket, client_address = server_socket.accept()
    code = client_socket.recv(3).decode().lower()
    data = client_socket.recv(1024).decode()
    print(config.users)
    if code == 'lgn':
        if len(data.split("~")) != 2:
            client_socket.send("Please enter your credentials".encode())
            return
        uname = data.split("~")[0]
        pwd = data.split("~")[1]
        if uname in config.clients:
            client_socket.send("User already connected".encode())
            return
        if uname in config.users and config.users[uname] == pwd:
            print("New connection: ", client_address, " nickname: " + uname)
            client_socket.send(("Hello " + uname + "!").encode())
            for client in config.client_sockets:
                client.send((uname + " connected!").encode())
            config.client_sockets.append(client_socket)
            config.clients[uname] = client_socket
        else:
            client_socket.send("wrong credentials".encode())
            return
    if code == 'rgs':
        print(data)
        if len(data.split("~")) != 2:
            client_socket.send("Please enter your registration credentials".encode())
            return
        uname = data.split("~")[0]
        pwd = data.split("~")[1]
        # TO DO - password confirmation
        if uname in users:
            client_socket.send("Users already exists".encode())
            return
        else:
            config.users[uname] = pwd
            print("New user joined\nconnection: ", client_address, " nickname: " + uname)
            client_socket.send(("Hello " + uname + "!").encode())
            for client in config.client_sockets:
                client.send((uname + " connected!").encode())
            config.client_sockets.append(client_socket)
            config.clients[uname] = client_socket
            update_db()
            print("updated")