import os
import base64
HANDLED_TYPES = ['pdf', 'png', 'jpg', 'jpeg']


def sparta_a722086cec(fileName):
    extension = fileName.split('.')[-1].lower()
    if extension in HANDLED_TYPES:
        return True
    return False


def sparta_6f4bb6d094(filePath, fileName):
    """
    
    """
    resDict = dict()
    extension = fileName.split('.')[-1].lower()
    if extension in ['pdf', 'png', 'jpg', 'jpeg']:
        with open(os.path.join(filePath, fileName), 'rb') as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read()).decode()
            resDict['data'] = encoded_string
    return resDict

#END OF QUBE
