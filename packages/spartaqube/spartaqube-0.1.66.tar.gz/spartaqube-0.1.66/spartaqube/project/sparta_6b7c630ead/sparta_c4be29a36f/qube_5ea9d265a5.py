import base64
import hashlib
from cryptography.fernet import Fernet


def sparta_7207ef767d() ->str:
    """
    Get encryption key
    """
    keygen_fernet = 'widget-plot-db'
    key = keygen_fernet.encode('utf-8')
    key = hashlib.md5(key).hexdigest()
    key = base64.b64encode(key.encode('utf-8'))
    return key.decode('utf-8')


def sparta_4a523d889a(password_to_encrypt) ->str:
    password_to_encrypt = password_to_encrypt.encode('utf-8')
    f = Fernet(sparta_7207ef767d().encode('utf-8'))
    password_e = f.encrypt(password_to_encrypt).decode('utf-8')
    password_e = base64.b64encode(password_e.encode('utf-8')).decode('utf-8')
    return password_e


def sparta_8588885027(password_e) ->str:
    f = Fernet(sparta_7207ef767d().encode('utf-8'))
    password = base64.b64decode(password_e)
    password = f.decrypt(password).decode('utf-8')
    return password

#END OF QUBE
