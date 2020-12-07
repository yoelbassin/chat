# Coded by Yashraj Singh Chouhan
import socket
import threading
import time

uname = ''

client = socket.socket()  # socket place holder


def login():
    global uname
    code = 'LOGIN'
    uname = input('Username: ')
    pwd = input('Password: ')  # TO DO - invisible password
    return code + uname + '~' + pwd


def register():
    global uname
    code = 'RGSTR'
    uname = input('Username: ')
    pwd = input('Password: ')  # TO DO - invisible password
    return code + uname + '~' + pwd


def establish_connection():
    global client
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket initialization
        client.connect(('127.0.0.1', 5555))  # connecting client to server
        code = input("Would you like to login or register? L/R (Q to exit)").upper()
        if code == 'L':
            data = login()
        elif code == 'R':
            data = register()
        elif code == 'Q':
            client.close()
            return False
        else:
            continue
        client.send(data.encode())
        time.sleep(1)
        data = client.recv(1024).decode()
        print(data)
        if 'Hello' in data:
            return True
        else:
            client.close()


def receive():
    while True:  # making valid connection
        try:
            message = client.recv(1024).decode()
            if message != '':
                print(message)
        except Exception as e:  # case on wrong ip/port details
            print("An error occurred: " + str(e))
            client.close()
            break


def write():
    while True:  # message layout
        # message = '{}: {}'.format(uname, input(''))
        message = '{}'.format(input(''))
        client.send(message.encode())


def main():
    if not establish_connection():
        print("Exiting program")
        return
    receive_thread = threading.Thread(target=receive)  # receiving multiple messages
    receive_thread.start()
    write_thread = threading.Thread(target=write)  # sending messages
    write_thread.start()


if __name__ == "__main__":
    main()



