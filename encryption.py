import os

from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    with open("secrete.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    with open("secrete.key", "r") as f:
        content = f.read()
    return content

def encrypt_message(message, key):
    encoeded_message = message.encode('utf-8')
    f = Fernet(key)
    encrypted_message = f.encrypt(encoeded_message)
    return encrypted_message

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message.decode('utf-8')
