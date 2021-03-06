import socket
import collections
import const
import rsa

uname = ''

client = socket.socket()  # socket place holder
active_requests = []

incoming_que = collections.deque()

lock = False

active_chat = ''

in_chat = True  #

running = True


def rem_req(packet):
    code = packet[:const.CODE_LEN]
    name = packet[5:]
    if name in active_requests:
        active_requests.remove(name)
        client.send(const.close_private_request_code.encode())
    return name


public_key, private_key = rsa.newkeys(1024)
dst_pub = None
chat_key = None
