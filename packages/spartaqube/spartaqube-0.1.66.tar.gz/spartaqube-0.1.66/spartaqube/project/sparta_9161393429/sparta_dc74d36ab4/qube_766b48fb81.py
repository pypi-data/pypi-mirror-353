import os
import json
import getpass
import platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
import project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 as qube_d24f3eb337
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_be7ed37fe1
from project.sparta_6b7c630ead.sparta_c4be29a36f import qube_f591de0f06 as qube_f591de0f06
from project.sparta_6b7c630ead.sparta_6d329e2f11 import qube_2b15813649 as qube_2b15813649


def sparta_023802df5e() ->str:
    system = platform.system()
    if system == 'Windows':
        return 'windows'
    elif system == 'Linux':
        return 'linux'
    elif system == 'Darwin':
        return 'mac'
    else:
        return None


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_7437b34782(request):
    """
    Developer examples main page
    """
    if not conf_settings.IS_DEV_VIEW_ENABLED:
        dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
        return render(request, 'dist/project/homepage/homepage.html', dict_var)
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 12
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    current_path = os.path.dirname(__file__)
    project_path = os.path.dirname(os.path.dirname(current_path))
    static_path = os.path.join(project_path, 'static')
    frontend_path = os.path.join(static_path, 'js', 'developer', 'template',
        'frontend')
    dict_var['frontend_path'] = frontend_path
    spartaqube_path = os.path.dirname(project_path)
    backend_path = os.path.join(spartaqube_path, 'django_app_template',
        'developer', 'template', 'backend')
    dict_var['backend_path'] = backend_path
    return render(request, 'dist/project/developer/developerExamples.html',
        dict_var)

#END OF QUBE
