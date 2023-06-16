#!/usr/bin/python3

import binascii
import hashlib
import os

password = input()
salt = os.urandom(32)
key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
print(binascii.hexlify(key + salt).decode("ascii"))
