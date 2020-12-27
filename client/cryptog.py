import const
import config
import rsa
from cryptography.fernet import Fernet


def key_ex():
    config.client.send((const.public_key + str(config.public_key.n) + ' ' + str(config.public_key.e)).encode())


def send_symmetric_key():
    self_id = int(''.join([str(ord(c)) for c in config.uname]))
    dst_id = int(''.join([str(ord(c)) for c in config.active_chat]))
    if dst_id > self_id:
        generate_key()
        encrypted_message = rsa.encrypt(config.chat_key, config.dst_pub)
        config.client.send(const.symmetric_key.encode() + encrypted_message)
        config.chat_key = Fernet(config.chat_key)


def get_key(key):
    key = key[5:].split(' ')
    config.dst_pub = rsa.PublicKey(int(key[0]), int(key[1]))


def get_symmetric_key(key):
    key = key.encode()
    self_id = int(''.join([str(ord(c)) for c in config.uname]))
    dst_id = int(''.join([str(ord(c)) for c in config.active_chat]))
    if dst_id < self_id:
        config.chat_key = Fernet(key)


def get_message_rsa(message):
    code = message[:const.CODE_LEN].decode()
    message = rsa.decrypt(message[const.CODE_LEN:], config.private_key)
    message = code + message.decode()
    return message


def get_enc_message(message):
    code = message[:const.CODE_LEN].decode()
    if code == const.msg_code:
        message = decrypt_message(message[const.CODE_LEN:])
    else:
        message = rsa.decrypt(message[const.CODE_LEN:], config.private_key)
    return code + message.decode()


def generate_key():
    """
    Generates a key and save it into a file
    """
    config.chat_key = Fernet.generate_key()



def encrypt_message(message):
    """
    Encrypts a message
    """
    encoded_message = message.encode()
    return config.chat_key.encrypt(encoded_message)


def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    return config.chat_key.decrypt(encrypted_message)
