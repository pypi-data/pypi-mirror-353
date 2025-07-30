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
from project.sparta_6b7c630ead.sparta_ca926aa57d import qube_c9cafca741 as qube_c9cafca741
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_e260b12968 import sparta_3d02d75bc2


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_969c556f40(request):
    """
    Notebook main page
    """
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 13
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True

    def create_folder_if_not_exists(path):
        folder_path = Path(path)
        if not folder_path.exists():
            folder_path.mkdir(parents=True)
    spartaqube_volume_path = sparta_3d02d75bc2()
    default_project_path = os.path.join(spartaqube_volume_path, 'notebook')
    create_folder_if_not_exists(default_project_path)
    dict_var['default_project_path'] = default_project_path
    return render(request, 'dist/project/notebook/notebook.html', dict_var)


@csrf_exempt
def sparta_e2f9181527(request, id):
    """
    Notebook app exec
    """
    if id is None:
        notebook_id = request.GET.get('id')
    else:
        notebook_id = id
    b_redirect_notebook_db = False
    if notebook_id is None:
        b_redirect_notebook_db = True
    else:
        notebook_access_dict = qube_c9cafca741.sparta_e3d7e6224a(notebook_id,
            request.user)
        res_access = notebook_access_dict['res']
        if res_access == -1:
            b_redirect_notebook_db = True
    if b_redirect_notebook_db:
        return sparta_969c556f40(request)
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 12
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    notebook_obj = notebook_access_dict['notebook_obj']
    dict_var['default_project_path'] = notebook_obj.project_path
    dict_var['b_require_password'] = 0 if notebook_access_dict['res'
        ] == 1 else 1
    dict_var['notebook_id'] = notebook_obj.notebook_id
    dict_var['notebook_name'] = notebook_obj.name
    dict_var['bPublicUser'] = request.user.is_anonymous
    return render(request, 'dist/project/notebook/notebookRun.html', dict_var)


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_b648bc3354(request, id):
    if id is None:
        notebook_id = request.GET.get('id')
    else:
        notebook_id = id
    b_redirect_notebook_db = False
    if notebook_id is None:
        b_redirect_notebook_db = True
    else:
        notebook_access_dict = qube_c9cafca741.sparta_e3d7e6224a(notebook_id,
            request.user)
        res_access = notebook_access_dict['res']
        if res_access == -1:
            b_redirect_notebook_db = True
    if b_redirect_notebook_db:
        return sparta_969c556f40(request)
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 12
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    notebook_obj = notebook_access_dict['notebook_obj']
    dict_var['default_project_path'] = notebook_obj.project_path
    dict_var['b_require_password'] = 0 if notebook_access_dict['res'
        ] == 1 else 1
    dict_var['notebook_id'] = notebook_obj.notebook_id
    dict_var['notebook_name'] = notebook_obj.name
    dict_var['bPublicUser'] = request.user.is_anonymous
    return render(request, 'dist/project/notebook/notebookDetached.html',
        dict_var)

#END OF QUBE
