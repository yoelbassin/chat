from PyInquirer import prompt, style_from_dict, Token
import time
from termcolor import colored, cprint
import sys
import establish_connection
import config
import socket
import const
import os
import private_chat
import main
import chat_IO

style = style_from_dict({
    Token.QuestionMark: '#E91E63 bold',
    Token.Selected: '#00FFFF',
    Token.Instruction: '',
    Token.Answer: '#2196f3 bold',
    Token.Question: '#7FFF00 bold',
})


def welcome():
    os.system('cls')
    # using termcolor for coloring output text
    cprint("Welcome!", 'green', attrs=['bold'], file=sys.stderr)


def username():
    questions = [
        {
            'type': 'input',
            'name': 'uname',
            'message': 'Username: ',
        }
    ]
    return prompt(questions, style=style)['uname']


def pwd():
    questions = [
        {
            'type': 'password',
            'name': 'pwd',
            'message': 'Password: ',
        }
    ]
    return prompt(questions, style=style)['pwd']



def log_screen():
    # Using PyInquirer for Dropdown menu interface
    questions = [
        {
            'type': 'list',
            'name': 'log',
            'message': 'enter your credentials:',
            'choices': ['login', 'registration'],
            'default': 'login'
        }
    ]

    while True:
        config.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket initialization
        config.client.connect(('127.0.0.1', 5555))  # connecting client to server
        answers = prompt(questions, style=style)

        print(answers['log'])

        if answers['log'] == 'login':
            data = establish_connection.login()

        # For user registration
        elif answers["log"] == "registration":
            data = establish_connection.register()
        else:
            continue
        config.client.send(data.encode())
        data = config.client.recv(1024).decode()

        if data == const.login_successfully_code:
            os.system("cls")
            print("")
            cprint("logged in successfully", "cyan")
            print("")
            return True

        else:
            config.client.close()
            cprint("incorrect credentials", "red")
            print(" ")


def new_connection(uname):
    questions = [
        {
            'type': 'confirm',
            'message': uname + ' invited you to a private chat, accept invitation?',
            'name': 'private_request',
            'default': True
        }
    ]
    ans = prompt(questions, style=style)['private_request']
    config.lock = False
    return ans


def menu():
    questions = [
        {
            'type': 'list',
            'name': 'start',
            'message': 'MENU:',
            'choices': ['create private chat', 'wait for a request', 'exit'],
        }
    ]
    ans = prompt(questions, style=style)
    if ans['start'] == 'create private chat':
        questions2 = [
            {
                'type': 'input',
                'name': 'user',
                'message': 'Destination user: '
            }
        ]
        ans2 = prompt(questions2, style=style)

        if private_chat.create_private_chat_request(ans2['user']):
            if private_chat.wait_for_connection():
                chat_IO.write_thread.start()
                chat_IO.print_thread.start()
    elif ans['start'] == 'wait for a request':
        if private_chat.wait_for_connection():
            chat_IO.write_thread.start()
            chat_IO.print_thread.start()
    elif ans['start'] == 'exit':
        config.running = False
