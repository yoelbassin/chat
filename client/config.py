import socket
import collections

uname = ''

client = socket.socket()  # socket place holder
active_requests = []

incoming_que = collections.deque()

lock = False

active_chat = ''



