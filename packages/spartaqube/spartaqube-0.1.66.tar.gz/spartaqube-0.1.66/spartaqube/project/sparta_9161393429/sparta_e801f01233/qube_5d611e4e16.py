import os
import json
import getpass
import platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 as qube_d24f3eb337
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_be7ed37fe1
from project.sparta_6b7c630ead.sparta_c4be29a36f import qube_f591de0f06 as qube_f591de0f06
from project.sparta_6b7c630ead.sparta_6d329e2f11 import qube_2b15813649 as qube_2b15813649
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_e260b12968 import sparta_3d02d75bc2


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_03867d7fc6(request):
    """
    Dashboard main page
    """
    edit_chart_id = request.GET.get('edit')
    if edit_chart_id is None:
        edit_chart_id = '-1'
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 9
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    dict_var['edit_chart_id'] = edit_chart_id

    def create_folder_if_not_exists(path):
        folder_path = Path(path)
        if not folder_path.exists():
            folder_path.mkdir(parents=True)
    spartaqube_volume_path = sparta_3d02d75bc2()
    default_project_path = os.path.join(spartaqube_volume_path, 'dashboard')
    create_folder_if_not_exists(default_project_path)
    dict_var['default_project_path'] = default_project_path
    return render(request, 'dist/project/dashboard/dashboard.html', dict_var)


@csrf_exempt
def sparta_14bd1a279b(request, id):
    """
    Dashboard Run Mode
    """
    if id is None:
        dashboard_id = request.GET.get('id')
    else:
        dashboard_id = id
    return sparta_8e2f48cf94(request, dashboard_id)


def sparta_8e2f48cf94(request, dashboard_id, session='-1'):
    """
    
    """
    b_redirect_dashboard_db = False
    if dashboard_id is None:
        b_redirect_dashboard_db = True
    else:
        dashboard_access_dict = qube_2b15813649.has_dashboard_access(
            dashboard_id, request.user)
        res_access = dashboard_access_dict['res']
        if res_access == -1:
            b_redirect_dashboard_db = True
    if b_redirect_dashboard_db:
        return sparta_03867d7fc6(request)
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 9
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    dashboard_obj = dashboard_access_dict['dashboard_obj']
    dict_var['b_require_password'] = 0 if dashboard_access_dict['res'
        ] == 1 else 1
    dict_var['dashboard_id'] = dashboard_obj.dashboard_id
    dict_var['dashboard_name'] = dashboard_obj.name
    dict_var['bPublicUser'] = request.user.is_anonymous
    dict_var['session'] = str(session)
    return render(request, 'dist/project/dashboard/dashboardRun.html', dict_var
        )

#END OF QUBE
