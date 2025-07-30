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
from django.conf import settings as conf_settings
import project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 as qube_d24f3eb337
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_be7ed37fe1
from project.sparta_6b7c630ead.sparta_c2672dbdb9 import qube_5e2773ad50 as qube_5e2773ad50
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_e260b12968 import sparta_3d02d75bc2


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_21cdd035a8(request):
    """
    Developer main page
    """
    if not conf_settings.IS_DEV_VIEW_ENABLED:
        dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
        return render(request, 'dist/project/homepage/homepage.html', dict_var)
    qube_5e2773ad50.sparta_775bae5204()
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 12
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True

    def create_folder_if_not_exists(path):
        folder_path = Path(path)
        if not folder_path.exists():
            folder_path.mkdir(parents=True)
    spartaqube_volume_path = sparta_3d02d75bc2()
    default_project_path = os.path.join(spartaqube_volume_path, 'developer')
    create_folder_if_not_exists(default_project_path)
    dict_var['default_project_path'] = default_project_path
    return render(request, 'dist/project/developer/developer.html', dict_var)


@csrf_exempt
def sparta_026b52e7e5(request, id):
    """
    Developer app exec
    """
    if not conf_settings.IS_DEV_VIEW_ENABLED:
        dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
        return render(request, 'dist/project/homepage/homepage.html', dict_var)
    if id is None:
        developer_id = request.GET.get('id')
    else:
        developer_id = id
    b_redirect_developer_db = False
    if developer_id is None:
        b_redirect_developer_db = True
    else:
        developer_access_dict = qube_5e2773ad50.has_developer_access(
            developer_id, request.user)
        res_access = developer_access_dict['res']
        if res_access == -1:
            b_redirect_developer_db = True
    if b_redirect_developer_db:
        return sparta_21cdd035a8(request)
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 12
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    developer_obj = developer_access_dict['developer_obj']
    dict_var['default_project_path'] = developer_obj.project_path
    dict_var['b_require_password'] = 0 if developer_access_dict['res'
        ] == 1 else 1
    dict_var['developer_id'] = developer_obj.developer_id
    dict_var['developer_name'] = developer_obj.name
    dict_var['bPublicUser'] = request.user.is_anonymous
    return render(request, 'dist/project/developer/developerRun.html', dict_var
        )


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_43c2780a20(request, id):
    """
    
    """
    print('OPEN DEVELOPER DETACHED')
    if id is None:
        developer_id = request.GET.get('id')
    else:
        developer_id = id
    print('developer_id')
    print(developer_id)
    b_redirect_developer_db = False
    if developer_id is None:
        b_redirect_developer_db = True
    else:
        developer_access_dict = qube_5e2773ad50.has_developer_access(
            developer_id, request.user)
        res_access = developer_access_dict['res']
        if res_access == -1:
            b_redirect_developer_db = True
    print('b_redirect_developer_db')
    print(b_redirect_developer_db)
    if b_redirect_developer_db:
        return sparta_21cdd035a8(request)
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 12
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    developer_obj = developer_access_dict['developer_obj']
    dict_var['default_project_path'] = developer_obj.project_path
    dict_var['b_require_password'] = 0 if developer_access_dict['res'
        ] == 1 else 1
    dict_var['developer_id'] = developer_obj.developer_id
    dict_var['developer_name'] = developer_obj.name
    dict_var['bPublicUser'] = request.user.is_anonymous
    return render(request, 'dist/project/developer/developerDetached.html',
        dict_var)


def sparta_8bd9cafe2f(request, project_path, file_name):
    """
    Server IFRAME mode (DEPRECATED)
    """
    project_path = unquote(project_path)
    return serve(request, file_name, document_root=project_path)

#END OF QUBE
