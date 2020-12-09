import select
import config
import ui
import threading
import sys
import chat_IO
import time
import timeout


def receive():
    """
    receive packets and send them to the que for analyzing

    :return:
    """
    while config.running:  # making valid connection
        ready = select.select([config.client], [], [])
        if ready:
            try:
                message = config.client.recv(1024).decode()
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
    ui.menu()
    while config.running:
        if not config.flag:
            timeout.err = False
            print(chat_IO.write_thread.is_alive())
            print(chat_IO.print_thread.is_alive())
            if not chat_IO.print_thread.is_alive() and not chat_IO.write_thread.is_alive():
                ui.menu()
        time.sleep(1)


receive_thread = threading.Thread(target=receive, daemon=True)  # receiving multiple messages


if __name__ == "__main__":
    main()
