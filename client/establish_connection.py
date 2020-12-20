import socket
import const
import config
import time
import ui


def login():
    code = const.login_code
    config.uname = ui.username()
    pwd = ui.pwd()  # TO DO - invisible password
    return code + config.uname + '~' + pwd


def register():
    code = const.register_code
    config.uname = ui.username()
    pwd = ui.pwd()  # TO DO - invisible password
    return code + config.uname + '~' + pwd


def establish_connection():
    while True:
        config.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket initialization
        config.client.connect(('127.0.0.1', 5555))  # connecting client to server
        code = input("Would you like to login or register? L/R (Q to exit)").upper()
        if code == 'L':
            data = login()
        elif code == 'R':
            data = register()
        elif code == 'Q':
            config.client.close()
            return False
        else:
            continue
        config.client.send(data.encode())
        time.sleep(1)
        data = config.client.recv(4096).decode()
        print(data)
        if 'Hello' in data:
            return True
        else:
            config.client.close()
