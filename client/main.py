import select
import config
import ui
import threading
import sys
import chat_IO
import time
import timeout
import const
import rsa
import cryptog


def receive():
    """
    receive packets and send them to the que for analyzing

    :return:
    """
    while config.running:  # making valid connection
        ready = select.select([config.client], [], [])
        if ready:
            try:
                message = config.client.recv(4096)
                code = message[:const.CODE_LEN].decode()
                if code in [const.msg_code, const.symmetric_key]:
                    message = cryptog.get_enc_message(message)
                else:
                    message = message.decode()
            except ConnectionResetError:
                config.running = False
                break
            if message != '':
                # send the message to the que
                config.incoming_que.append(message)
        time.sleep(0.2)


def main():
    # if not establish_connection.establish_connection():
    #   print("Exiting program")
    #    return
    ui.welcome()
    if not ui.log_screen():
        print("exiting")
        return
    receive_thread.start()
    timeout.err = False
    config.in_chat = False
    ui.menu()
    chat_IO.write_thread.start()
    chat_IO.print_thread.start()
    while config.running:
        if not config.in_chat:
            timeout.err = False
            ui.menu()
        time.sleep(1)


receive_thread = threading.Thread(target=receive, daemon=True)  # receiving multiple messages


if __name__ == "__main__":
    main()
