import binascii
#
import hmac
import hashlib

def hash_msg(message, key=1234):
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
