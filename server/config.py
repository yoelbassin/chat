import json

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'
users = {}  # all clients - {"uname":"pwd"}
client_sockets = []  # active connections - [client_socket]
clients = {}  # active clients - {"uname":client_socket}

private_requests = {}  # active requests - {"Uname1":"Uname2"}
active_private = {}  # active private chats - {"Uname1":"Uname2"}


def open_db():
    global users
    infile = open('users.json', 'r')
    users = json.loads(infile.read())
    infile.close()
    print(users)
    return users


def update_db():
    filename = 'users.json'
    outfile = open(filename, 'w')
    json.dump(users, outfile)
    print(users)
    outfile.close()


def get_uname(client_socket):
    for uname, socket_ in clients.items():
        if socket_ == client_socket:
            return uname


def get_by_value(value, dic):
    for key, val in dic.items():
        if val == value:
            return key
