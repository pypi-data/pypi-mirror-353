import os
import json
import base64
import hashlib
import random
from cryptography.fernet import Fernet


def sparta_721aed39fd():
    key = '__API_AUTH__'
    key = key.encode('utf-8')
    key = hashlib.md5(key).hexdigest()
    key = base64.b64encode(key.encode('utf-8'))
    return key


def sparta_841044e64b(objectToCrypt):
    key = sparta_721aed39fd()
    f = Fernet(key)
    objectToCrypt = objectToCrypt.encode('utf-8')
    objectCrypt = f.encrypt(objectToCrypt).decode('utf-8')
    objectCrypt = base64.b64encode(objectCrypt.encode('utf-8')).decode('utf-8')
    return objectCrypt


def sparta_d9e75a12b3(apiAuth):
    """
        Decrypt formula (stored in the dataQuantDB object)
    """
    key = sparta_721aed39fd()
    f = Fernet(key)
    apiAuth = base64.b64decode(apiAuth)
    return f.decrypt(apiAuth).decode('utf-8')


def sparta_bc59428632(kCrypt):
    key = '__SQ_AUTH__' + str(kCrypt)
    key = key.encode('utf-8')
    key = hashlib.md5(key).hexdigest()
    key = base64.b64encode(key.encode('utf-8'))
    return key


def sparta_9e6df61ce3(objectToCrypt, kCrypt):
    key = sparta_bc59428632(kCrypt)
    f = Fernet(key)
    objectToCrypt = objectToCrypt.encode('utf-8')
    objectCrypt = f.encrypt(objectToCrypt).decode('utf-8')
    objectCrypt = base64.b64encode(objectCrypt.encode('utf-8')).decode('utf-8')
    return objectCrypt


def sparta_174fd574c9(objectToDecrypt, kCrypt):
    """
        Decrypt auth login
    """
    key = sparta_bc59428632(kCrypt)
    f = Fernet(key)
    objectToDecrypt = base64.b64decode(objectToDecrypt)
    return f.decrypt(objectToDecrypt).decode('utf-8')


def sparta_bb36d140ae(kCrypt):
    key = '__SQ_EMAIL__' + str(kCrypt)
    key = key.encode('utf-8')
    key = hashlib.md5(key).hexdigest()
    key = base64.b64encode(key.encode('utf-8'))
    return key


def sparta_db61b9f4f5(objectToCrypt, kCrypt):
    key = sparta_bb36d140ae(kCrypt)
    f = Fernet(key)
    objectToCrypt = objectToCrypt.encode('utf-8')
    objectCrypt = f.encrypt(objectToCrypt).decode('utf-8')
    objectCrypt = base64.b64encode(objectCrypt.encode('utf-8')).decode('utf-8')
    return objectCrypt


def sparta_131f3594da(objectToDecrypt, kCrypt):
    """
        Decrypt notebook cells
    """
    key = sparta_bb36d140ae(kCrypt)
    f = Fernet(key)
    objectToDecrypt = base64.b64decode(objectToDecrypt)
    return f.decrypt(objectToDecrypt).decode('utf-8')


def sparta_8063019c41(kCrypt):
    key = '__SQ_KEY_SSO_CRYPT__' + str(kCrypt)
    key = key.encode('utf-8')
    key = hashlib.md5(key).hexdigest()
    key = base64.b64encode(key.encode('utf-8'))
    return key


def sparta_492a7b56cb(objectToCrypt, kCrypt):
    key = sparta_8063019c41(kCrypt)
    f = Fernet(key)
    objectToCrypt = objectToCrypt.encode('utf-8')
    objectCrypt = f.encrypt(objectToCrypt).decode('utf-8')
    objectCrypt = base64.b64encode(objectCrypt.encode('utf-8')).decode('utf-8')
    return objectCrypt


def sparta_9b6e6519db(objectToDecrypt, kCrypt):
    """
        Decrypt Code Exec (stored in the execMonitoring object)
    """
    key = sparta_8063019c41(kCrypt)
    f = Fernet(key)
    objectToDecrypt = base64.b64decode(objectToDecrypt)
    return f.decrypt(objectToDecrypt).decode('utf-8')


def sparta_59542bdf1e():
    key = '__SQ_IPYNB_SQ_METADATA__'
    key = key.encode('utf-8')
    key = hashlib.md5(key).hexdigest()
    key = base64.b64encode(key.encode('utf-8'))
    return key


def sparta_e887295181(objectToCrypt):
    key = sparta_59542bdf1e()
    f = Fernet(key)
    objectToCrypt = objectToCrypt.encode('utf-8')
    objectCrypt = f.encrypt(objectToCrypt).decode('utf-8')
    objectCrypt = base64.b64encode(objectCrypt.encode('utf-8')).decode('utf-8')
    return objectCrypt


def sparta_60402d686c(objectToDecrypt):
    """
        Decrypt ipnyb metadata
    """
    key = sparta_59542bdf1e()
    f = Fernet(key)
    objectToDecrypt = base64.b64decode(objectToDecrypt)
    return f.decrypt(objectToDecrypt).decode('utf-8')

#END OF QUBE
