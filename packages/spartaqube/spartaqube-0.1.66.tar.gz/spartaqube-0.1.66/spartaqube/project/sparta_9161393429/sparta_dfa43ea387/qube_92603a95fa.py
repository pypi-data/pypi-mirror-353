import os
import json
import getpass
import platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from django.http import FileResponse, Http404
from urllib.parse import unquote
import project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 as qube_d24f3eb337
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_be7ed37fe1
from project.sparta_6b7c630ead.sparta_2a0a612d78 import qube_6219d0a05d as qube_6219d0a05d
from project.sparta_6b7c630ead.sparta_aceca65940 import qube_1969b3f192 as qube_1969b3f192
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_e260b12968 import sparta_3d02d75bc2


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_d1e2723885(request):
    """
    View Homepage Welcome back
    """
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = -1
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    return render(request, 'dist/project/homepage/homepage.html', dict_var)


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_6813572989(request, kernel_manager_uuid):
    b_redirect_homepage = False
    if kernel_manager_uuid is None:
        b_redirect_homepage = True
    else:
        kernel_process_obj = qube_6219d0a05d.sparta_cc49b572ef(request.user, kernel_manager_uuid)
        if kernel_process_obj is None:
            b_redirect_homepage = True
    if b_redirect_homepage:
        return sparta_d1e2723885(request)

    def create_folder_if_not_exists(path):
        folder_path = Path(path)
        if not folder_path.exists():
            folder_path.mkdir(parents=True)
    spartaqube_volume_path = sparta_3d02d75bc2()
    default_project_path = os.path.join(spartaqube_volume_path, 'kernel')
    create_folder_if_not_exists(default_project_path)
    kernel_path = os.path.join(default_project_path, kernel_manager_uuid)
    create_folder_if_not_exists(kernel_path)
    filename = os.path.join(kernel_path, 'main.ipynb')
    if not os.path.exists(filename):
        empty_notebook_dict = qube_1969b3f192.sparta_c617b12a8e()
        with open(filename, 'w') as file:
            file.write(json.dumps(empty_notebook_dict))
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['default_project_path'] = default_project_path
    dict_var['menuBar'] = -1
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['kernel_name'] = kernel_process_obj.name
    dict_var['kernelManagerUUID'] = kernel_process_obj.kernel_manager_uuid
    dict_var['bCodeMirror'] = True
    dict_var['bPublicUser'] = request.user.is_anonymous
    return render(request,
        'dist/project/sqKernelNotebook/sqKernelNotebook.html', dict_var)

#END OF QUBE
