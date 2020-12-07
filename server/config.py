import json

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = '0.0.0.0'
users = {}
client_sockets = []
clients = {}


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

