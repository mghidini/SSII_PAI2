# clientsocket.py
import hashlib
import hmac
import json
import socket
import uuid


def hash_msg(message, key=8888): # different key!
    try:
        byte_key = bytes(key)
        message = message.encode()
        hashed = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
        is_hashed = True
    except Exception:
        print('exception')
        is_hashed = False

    if is_hashed:
        return hashed
    else:
        return None


# HOST = "127.0.0.1"
HOST = "25.35.53.183"  # SERVER: Gabriele - Hamachi IPV4
PORT = 3030  # The port used by the server

print('insert amount')

sender = "1234"
receiver = "5678"
amount = input()  # str type
nonce = str(uuid.uuid4())
message = sender + receiver + amount + nonce
hashed_message = hash_msg(message)

# print(nonce)
# print(hashed_message)

mydict = {
    "sender": sender,
    "receiver": receiver,
    "amount": amount,
    "nonce": nonce,
    "hmac": hashed_message}

serialized = json.dumps(mydict)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(bytes(serialized, "utf-8"))
    data = s.recv(1024)
    print(data)

