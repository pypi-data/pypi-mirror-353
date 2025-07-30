import re
import os
import json
import stat
import importlib
import io, sys
import subprocess
import platform
import base64
import traceback
import uuid
import shutil
from pathlib import Path
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime, timedelta
import pytz
UTC = pytz.utc
from spartaqube_app.path_mapper_obf import sparta_2776c51607
from project.models import ShareRights
from project.sparta_6b7c630ead.sparta_42b75ebdb3 import qube_eeee71e162 as qube_eeee71e162
from project.sparta_6b7c630ead.sparta_c4be29a36f import qube_5ea9d265a5 as qube_5ea9d265a5
from project.sparta_6b7c630ead.sparta_e12a2379ef.qube_5414460aa1 import Connector as Connector
from project.sparta_6b7c630ead.sparta_48648f141a import qube_444ab4dc41 as qube_444ab4dc41
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_538e75a6b0 import sparta_b58678b446
from project.sparta_6b7c630ead.sparta_aceca65940 import qube_1969b3f192 as qube_1969b3f192
from project.sparta_6b7c630ead.sparta_aceca65940 import qube_708c5472c6 as qube_708c5472c6
from project.sparta_6b7c630ead.sparta_5e49ed59d5.qube_3583d7aa1d import sparta_7d2b403019
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_8008d24895 import sparta_827e9198b8, sparta_17f64e7001
from project.logger_config import logger
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_e260b12968 import sparta_3d02d75bc2
from project.sparta_6b7c630ead.sparta_c2672dbdb9 import qube_5e2773ad50 as qube_5e2773ad50


def sparta_673391f9b6(user_obj) ->list:
    """
    
    """
    user_group_set = qube_eeee71e162.sparta_325a9ff1bc(user_obj)
    if len(user_group_set) > 0:
        user_groups = [this_obj.user_group for this_obj in user_group_set]
    else:
        user_groups = []
    return user_groups


def sparta_9c8d90c079(json_data, user_obj) ->dict:
    """
    Load developer library: all my developer view + the public (exposed) views
    """
    json_data['is_plot_db'] = True
    return qube_5e2773ad50.sparta_0142b8d6b1(json_data, user_obj)


def sparta_c8af11b409() ->str:
    """
    Get default plotDB developer project path
    """
    spartaqube_volume_path = sparta_3d02d75bc2()
    default_plot_db_project_path = os.path.join(spartaqube_volume_path,
        'plot_db_developer')

    def create_folder_if_not_exists(path):
        folder_path = Path(path)
        if not folder_path.exists():
            folder_path.mkdir(parents=True)
    create_folder_if_not_exists(default_plot_db_project_path)
    return {'res': 1, 'path': default_plot_db_project_path}

#END OF QUBE
