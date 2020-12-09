import threading
import const
import config
import private_chat
import establish_connection
import ui
from timeout import inputimeout, TimeoutOccurred


def receive():
    """
    receive packets and send them to the que for analyzing

    :return:
    """
    while True:  # making valid connection

        # get the message from the server
        message = config.client.recv(1024).decode()
        if message != '':
            # send the message to the que
            config.incoming_que.append(message)


def write():
    """
    get input from the user and send it to the server

    :return:
    """
    while True:  # message layout
        try:
            config.lock = False
            message = inputimeout(timeout=5)
            print('[' + config.uname + ']$~' + message)
        except TimeoutOccurred:
            continue
        if len(config.active_requests) > 0:
            config.lock = False
        elif config.active_chat:
            private_chat.handle_chat(message)
        elif 'send private to' in message and not config.active_chat:
            private_chat.create_private_chat_request(input('uname: '))
        else:
            config.client.send(message.encode())


def print_incoming():
    while True:
        if config.lock:
            continue
        try:
            if not config.incoming_que:
                continue
            packet = config.incoming_que.popleft()
            code = packet[:5]

            # if code is a private chat request code
            if code == const.private_chat_request_code:
                config.lock = True
                private_chat.recv_private_chat_request(packet)

            # if code is accepted private chat code
            elif code == const.private_chat_accepted_code:
                name = packet[5:].split('~')[0]
                print("private chat started with " + name)
                if name in config.active_requests:
                    config.active_requests.remove(name)
                    config.active_chat = '[' + name + ']$~'

            # if code is message code
            elif code == const.msg_code:
                message = packet[5:]
                if message != '':
                    print(config.active_chat + message)

            elif code == const.private_chat_request_sent_code:
                src = packet[5:]
                print("Private chat request sent successfully to " + src)

            elif code == const.end_chat_code:
                print("Chat with " + config.active_chat + " ended")

            elif code == const.private_chat_denied_code:
                src = packet[5:]
                print(src + " refused your invitation")
                if src in config.active_requests:
                    config.active_requests.remove(src)

        except Exception as e:
            print("An error has occurred: " + str(e))
            config.client.close()
            break


receive_thread = threading.Thread(target=receive)  # receiving multiple messages
print_thread = threading.Thread(target=print_incoming)  # printing the packets received
write_thread = threading.Thread(target=write)  # sending messages


def main():
    # if not establish_connection.establish_connection():
    #   print("Exiting program")
    #    return
    ui.welcome()
    if not ui.log_screen():
        print("exiting")
        return
    ui.menu()
    receive_thread.start()
    write_thread.start()
    print_thread.start()


if __name__ == "__main__":
    main()
