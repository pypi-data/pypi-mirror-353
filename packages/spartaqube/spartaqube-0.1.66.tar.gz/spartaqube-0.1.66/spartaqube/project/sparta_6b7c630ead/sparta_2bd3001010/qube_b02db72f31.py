import os
import zipfile
import pytz
UTC = pytz.utc
from django.conf import settings as conf_settings


def sparta_26c8aa863c():
    """
        Get main notebook folder
    """
    if conf_settings.PLATFORMS_NFS:
        notebookFolder = '/var/nfs/notebooks/'
        if not os.path.exists(notebookFolder):
            os.makedirs(notebookFolder)
        return notebookFolder
    if (conf_settings.PLATFORM == 'LOCAL_DESKTOP' or conf_settings.IS_LOCAL_PLATFORM):
        if conf_settings.PLATFORM_DEBUG == 'DEBUG-CLIENT-2':
            return os.path.join(os.environ['APPDATA'], 'SpartaQuantNB/CLIENT2')
        return os.path.join(os.environ['APPDATA'], 'SpartaQuantNB')
    if conf_settings.PLATFORM == 'LOCAL_CE':
        return '/app/notebooks/'


def sparta_6faf8d59d6(userId):
    """
        Get user notebook folder
    """
    main_notebook_folder_path = sparta_26c8aa863c()
    user_notebook_folder = os.path.join(main_notebook_folder_path, userId)
    return user_notebook_folder


def sparta_15634e8922(notebookProjectId, userId):
    """
        Get final notebook folder
    """
    user_notebook_folder_path = sparta_6faf8d59d6(userId)
    notebook_folder = os.path.join(user_notebook_folder_path, notebookProjectId
        )
    return notebook_folder


def sparta_5604e741cf(notebookProjectId, userId):
    """
        Check if sq folder created
    """
    user_notebook_folder = sparta_6faf8d59d6(userId)
    notebook_folder = os.path.join(user_notebook_folder, notebookProjectId)
    return os.path.exists(notebook_folder)


def sparta_f62a158b90(notebookProjectId, userId, ipynbFileName):
    """
        Check if ipynb exists
    """
    user_notebook_folder = sparta_6faf8d59d6(userId)
    notebook_folder = os.path.join(user_notebook_folder, notebookProjectId)
    return os.path.isfile(os.path.join(notebook_folder, ipynbFileName))


def sparta_588bf02880(notebookProjectId, userId):
    """
        This function returns a zip of the notebookProject (folder with all its contents, sub folders etc...)
    """
    folder_notebook_path = sparta_15634e8922(notebookProjectId, userId)
    user_notebook_folder = sparta_6faf8d59d6(userId)
    zip_path = f'{user_notebook_folder}/zipTmp/'
    if not os.path.exists(zip_path):
        os.makedirs(zip_path)
    test_files = f'{zip_path}/{notebookProjectId}.zip'
    zipobj = zipfile.ZipFile(test_files, 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(folder_notebook_path) + 1
    for base, dirs, files in os.walk(folder_notebook_path):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])
    return zipobj


def sparta_dd51e1d85b(notebookProjectId, userId):
    """
    
    """
    sparta_588bf02880(notebookProjectId, userId)
    zipName = f'{notebookProjectId}.zip'
    user_notebook_folder = sparta_6faf8d59d6(userId)
    zip_path = f'{user_notebook_folder}/zipTmp/{notebookProjectId}.zip'
    zipObj = open(zip_path, 'rb')
    return {'zipName': zipName, 'zipObj': zipObj}

#END OF QUBE
