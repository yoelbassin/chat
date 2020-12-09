import json

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'
users = {}  # all clients - {"uname":"pwd"}
client_sockets = []  # active connections - [client_socket]
clients = {}  # active clients - {"uname":client_socket}

private_requests = {}  # active requests - {"Uname1":"Uname2"}
active_private = {}  # active private chats - {"Uname1":"Uname2"}
socket_addresses = {}  # active sockets and their address - {socket, address}


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


def end_connection_with_socket(client_socket):
    uname = get_uname(client_socket)
    clients.pop(uname)
    print("connection with " + uname + ' have been interrupted')
    client_sockets.remove(client_socket)
    # if client in a private chat
    if client_socket in active_private:
        active_private.pop(client_socket)
    if client_socket in active_private.values():
        active_private.pop(get_by_value(client_socket, active_private))
    # if client in a request for a private chat
    if uname in private_requests:
        private_requests.pop(uname)
    if uname in private_requests.values():
        private_requests.pop(get_by_value(uname, private_requests))
    client_socket.close()
