import os
import sys
import subprocess
import shutil
import getpass
import platform
import json
import base64
import zipfile
import io
import uuid
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime, timedelta
from pathlib import Path
import pytz
UTC = pytz.utc
from project.models_spartaqube import Dashboard, DashboardShared, Developer, DeveloperShared, Notebook, NotebookShared, Kernel, KernelShared
from project.models import ShareRights
from project.sparta_6b7c630ead.sparta_42b75ebdb3 import qube_eeee71e162 as qube_eeee71e162
from project.sparta_6b7c630ead.sparta_48648f141a import qube_444ab4dc41 as qube_444ab4dc41
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_538e75a6b0 import sparta_b58678b446, sparta_42433255e6
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_e260b12968 import sparta_3d02d75bc2
from project.sparta_6b7c630ead.sparta_2a0a612d78 import qube_6219d0a05d as qube_6219d0a05d
from project.logger_config import logger


def sparta_673391f9b6(user_obj) ->list:
    """
    
    """
    user_group_set = qube_eeee71e162.sparta_325a9ff1bc(user_obj)
    if len(user_group_set) > 0:
        user_groups = [this_obj.user_group for this_obj in user_group_set]
    else:
        user_groups = []
    return user_groups


def sparta_8f7ff4ab5a():
    """
    This function returns the folder path for the venv
    """
    spartaqube_volume_path = sparta_3d02d75bc2()
    default_project_path = os.path.join(spartaqube_volume_path, 'sq_venv')
    os.makedirs(default_project_path, exist_ok=True)
    return default_project_path


def sparta_6dd9319d8c(env_name):
    """Gets the path to the pip executable in a platform-independent way."""
    env_path = sparta_8f7ff4ab5a()
    if sys.platform == 'win32':
        pip_path = os.path.join(env_path, env_name, 'Scripts', 'pip.exe')
    else:
        pip_path = os.path.join(env_path, env_name, 'bin', 'pip')
    return pip_path


def sparta_1c640a449f(json_data, user_obj) ->dict:
    """
    This function returns the list of available venv 
    """
    base_path = sparta_8f7ff4ab5a()
    available_venvs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    return {'res': 1, 'available_venvs': available_venvs}


def sparta_d6d12313ae(json_data, user_obj) ->dict:
    """
    This function creates a venv 
    """
    base_path = sparta_8f7ff4ab5a()
    env_name = json_data['env_name']
    env_path = os.path.join(base_path, env_name)
    try:
        subprocess.run([sys.executable, '-m', 'venv', env_path], check=True)
        MANDATORY_LIB_TO_INSTALL = ['cloudpickle']
        for lib in MANDATORY_LIB_TO_INSTALL:
            pip_path = sparta_6dd9319d8c(env_name)
            pip_cmd_input = f'pip install {lib}'
            pip_cmd = pip_cmd_input.replace('pip', pip_path)
            process = subprocess.Popen(pip_cmd, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True)
            for line in process.stdout:
                logger.debug(line)
        return {'res': 1}
    except Exception as e:
        return {'res': -1, 'errorMsg':
            f'Failed to create virtual environment with error {str(e)}'}


def sparta_0827fadfcc(json_data, user_obj) ->dict:
    """
    This function set a venv 
    """
    dashboard_id = json_data['dashboardId']
    dashboard_set = Dashboard.objects.filter(dashboard_id__startswith=
        dashboard_id, is_delete=False).all()
    if dashboard_set.count() == 1:
        dashboard_obj = dashboard_set[dashboard_set.count() - 1]
        dashboard_id = dashboard_obj.dashboard_id
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            dashboard_shared_set = DashboardShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                dashboard__is_delete=0, dashboard=dashboard_obj) | Q(
                is_delete=0, user=user_obj, dashboard__is_delete=0,
                dashboard=dashboard_obj))
        else:
            dashboard_shared_set = DashboardShared.objects.filter(is_delete
                =0, user=user_obj, dashboard__is_delete=0, dashboard=
                dashboard_obj)
        has_edit_rights = False
        if dashboard_shared_set.count() > 0:
            dashboard_shared_obj = dashboard_shared_set[0]
            share_rights_obj = dashboard_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_edit_rights = True
        if has_edit_rights:
            env_name = json_data['env_name']
            dashboard_obj.dashboard_venv = env_name
            dashboard_obj.save()
    res_kernel_activate_venv = qube_6219d0a05d.sparta_00e3975dd3(
        json_data, user_obj)
    return {'res': 1}


def sparta_6f08884a9f(json_data, user_obj) ->dict:
    """
    This function remove a virtual env from a dashboard project
    """
    dashboard_id = json_data['dashboardId']
    dashboard_set = Dashboard.objects.filter(dashboard_id__startswith=
        dashboard_id, is_delete=False).all()
    if dashboard_set.count() == 1:
        dashboard_obj = dashboard_set[dashboard_set.count() - 1]
        dashboard_id = dashboard_obj.dashboard_id
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            dashboard_shared_set = DashboardShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                dashboard__is_delete=0, dashboard=dashboard_obj) | Q(
                is_delete=0, user=user_obj, dashboard__is_delete=0,
                dashboard=dashboard_obj))
        else:
            dashboard_shared_set = DashboardShared.objects.filter(is_delete
                =0, user=user_obj, dashboard__is_delete=0, dashboard=
                dashboard_obj)
        has_edit_rights = False
        if dashboard_shared_set.count() > 0:
            dashboard_shared_obj = dashboard_shared_set[0]
            share_rights_obj = dashboard_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_edit_rights = True
        if has_edit_rights:
            env_name = None
            dashboard_obj.dashboard_venv = env_name
            dashboard_obj.save()
    return {'res': 1}


def sparta_7fb588a1f8(json_data, user_obj) ->dict:
    """
    This function deletes a venv 
    """
    dashboard_id = json_data['dashboardId']
    developer_id = json_data['developerId']
    if str(dashboard_id) != '-1':
        sparta_6f08884a9f(json_data, user_obj)
    if str(developer_id) != '-1':
        sparta_c820e0f614(json_data, user_obj)
    base_path = sparta_8f7ff4ab5a()
    env_name = json_data['env_name']
    env_path = os.path.join(base_path, env_name)
    try:
        shutil.rmtree(env_path)
        return {'res': 1}
    except FileNotFoundError as e:
        return {'res': -1, 'errorMsg': str(e)}
    except Exception as e:
        return {'res': -1, 'errorMsg': str(e)}


def sparta_f995be22ca(json_data, user_obj) ->dict:
    """
    Get the output of pip list for a specific virtual environment
    """
    env_name = json_data['env_name']
    pip_path = sparta_6dd9319d8c(env_name)
    libraries = []
    try:
        result = subprocess.run([pip_path, 'list'], capture_output=True,
            text=True, check=True)
        lines = result.stdout.strip().splitlines()[2:]
        for line in lines:
            package, version = line.split()[:2]
            libraries.append({'name': package, 'version': version})
        return {'res': 1, 'libraries': libraries}
    except Exception as e:
        return {'res': -1, 'errorMsg': str(e)}


def sparta_7200ccd349(env_name, project_path) ->dict:
    """
    Get the output of pip list for a specific virtual environment
    """
    requirements_file_path = os.path.join(project_path, 'requirements.txt')
    pip_path = sparta_6dd9319d8c(env_name)
    try:
        with open(requirements_file_path, 'w') as requirements_file:
            subprocess.run([pip_path, 'freeze'], stdout=requirements_file)
        return {'res': 1}
    except Exception as e:
        return {'res': -1, 'errorMsg': str(e)}


def sparta_40d93ba17d(json_data, user_obj) ->dict:
    """
    Set venv for developer mode
    """
    logger.debug('SET VENV DEVELOPER DEBUG > set_venv_developer')
    logger.debug(json_data)
    developer_id = json_data['developerId']
    developer_set = Developer.objects.filter(developer_id__startswith=
        developer_id, is_delete=False).all()
    if developer_set.count() == 1:
        developer_obj = developer_set[developer_set.count() - 1]
        developer_id = developer_obj.developer_id
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            developer_shared_set = DeveloperShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                developer__is_delete=0, developer=developer_obj) | Q(
                is_delete=0, user=user_obj, developer__is_delete=0,
                developer=developer_obj))
        else:
            developer_shared_set = DeveloperShared.objects.filter(is_delete
                =0, user=user_obj, developer__is_delete=0, developer=
                developer_obj)
        has_edit_rights = False
        if developer_shared_set.count() > 0:
            developer_shared_obj = developer_shared_set[0]
            share_rights_obj = developer_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_edit_rights = True
        if has_edit_rights:
            env_name = json_data['env_name']
            developer_obj.developer_venv = env_name
            developer_obj.save()
    res_kernel_activate_venv = qube_6219d0a05d.sparta_00e3975dd3(
        json_data, user_obj)
    return {'res': 1}


def sparta_c820e0f614(json_data, user_obj) ->dict:
    """
    This function remove a virtual env from a developer project
    """
    developer_id = json_data['developerId']
    developer_set = Developer.objects.filter(developer_id__startswith=
        developer_id, is_delete=False).all()
    if developer_set.count() == 1:
        developer_obj = developer_set[developer_set.count() - 1]
        developer_id = developer_obj.developer_id
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            developer_shared_set = DeveloperShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                developer__is_delete=0, developer=developer_obj) | Q(
                is_delete=0, user=user_obj, developer__is_delete=0,
                developer=developer_obj))
        else:
            developer_shared_set = DeveloperShared.objects.filter(is_delete
                =0, user=user_obj, developer__is_delete=0, developer=
                developer_obj)
        has_edit_rights = False
        if developer_shared_set.count() > 0:
            developer_shared_obj = developer_shared_set[0]
            share_rights_obj = developer_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_edit_rights = True
        if has_edit_rights:
            env_name = None
            developer_obj.developer_venv = env_name
            developer_obj.save()
    return {'res': 1}


def sparta_71ee68ef24(json_data, user_obj) ->dict:
    """
    Set venv for notebook
    """
    logger.debug('SET VENV DEVELOPER DEBUG > set_venv_developer')
    logger.debug(json_data)
    notebook_id = json_data['notebookId']
    notebook_set = Notebook.objects.filter(notebook_id__startswith=
        notebook_id, is_delete=False).all()
    if notebook_set.count() == 1:
        notebook_obj = notebook_set[notebook_set.count() - 1]
        notebook_id = notebook_obj.notebook_id
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            notebook_shared_set = NotebookShared.objects.filter(Q(is_delete
                =0, user_group__in=user_groups, notebook__is_delete=0,
                notebook=notebook_obj) | Q(is_delete=0, user=user_obj,
                notebook__is_delete=0, notebook=notebook_obj))
        else:
            notebook_shared_set = NotebookShared.objects.filter(is_delete=0,
                user=user_obj, notebook__is_delete=0, notebook=notebook_obj)
        has_edit_rights = False
        if notebook_shared_set.count() > 0:
            notebook_shared_obj = notebook_shared_set[0]
            share_rights_obj = notebook_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_edit_rights = True
        if has_edit_rights:
            env_name = json_data['env_name']
            notebook_obj.notebook_venv = env_name
            notebook_obj.save()
    res_kernel_activate_venv = qube_6219d0a05d.sparta_00e3975dd3(
        json_data, user_obj)
    return {'res': 1}


def sparta_3c5cc8f511(json_data, user_obj) ->dict:
    """
    This function remove a virtual env from a notebook project
    """
    notebook_id = json_data['notebookId']
    notebook_set = Notebook.objects.filter(notebook_id__startswith=
        notebook_id, is_delete=False).all()
    if notebook_set.count() == 1:
        notebook_obj = notebook_set[notebook_set.count() - 1]
        notebook_id = notebook_obj.notebook_id
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            notebook_shared_set = NotebookShared.objects.filter(Q(is_delete
                =0, user_group__in=user_groups, notebook__is_delete=0,
                notebook=notebook_obj) | Q(is_delete=0, user=user_obj,
                notebook__is_delete=0, notebook=notebook_obj))
        else:
            notebook_shared_set = NotebookShared.objects.filter(is_delete=0,
                user=user_obj, notebook__is_delete=0, notebook=notebook_obj)
        has_edit_rights = False
        if notebook_shared_set.count() > 0:
            notebook_shared_obj = notebook_shared_set[0]
            share_rights_obj = notebook_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_edit_rights = True
        if has_edit_rights:
            env_name = None
            notebook_obj.notebook_venv = env_name
            notebook_obj.save()
    return {'res': 1}


def sparta_141eb632fb(json_data, user_obj) ->dict:
    """
    Set kernel venv
    """
    from project.sparta_6b7c630ead.sparta_2a0a612d78 import qube_6219d0a05d as qube_6219d0a05d
    kernel_manager_uuid = json_data['kernelManagerUUID']
    kernel_set = Kernel.objects.filter(kernel_manager_uuid__startswith=
        kernel_manager_uuid, is_delete=False).all()
    if kernel_set.count() == 1:
        kernel_obj = kernel_set[kernel_set.count() - 1]
        kernel_manager_uuid = kernel_obj.kernel_manager_uuid
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            kernel_shared_set = KernelShared.objects.filter(Q(is_delete=0,
                user_group__in=user_groups, kernel__is_delete=0, kernel=
                kernel_obj) | Q(is_delete=0, user=user_obj,
                kernel__is_delete=0, kernel=kernel_obj))
        else:
            kernel_shared_set = KernelShared.objects.filter(is_delete=0,
                user=user_obj, kernel__is_delete=0, kernel=kernel_obj)
        has_edit_rights = False
        if kernel_shared_set.count() > 0:
            kernel_shared_obj = kernel_shared_set[0]
            share_rights_obj = kernel_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_edit_rights = True
        if has_edit_rights:
            env_name = json_data['env_name']
            kernel_obj.kernel_venv = env_name
            kernel_obj.save()
    res_kernel_activate_venv = qube_6219d0a05d.sparta_00e3975dd3(
        json_data, user_obj)
    return {'res': 1}


def sparta_a65929b4e6(json_data, user_obj) ->dict:
    """
    Deactivate venv inside kernel
    """
    kernel_manager_uuid = json_data['kernelManagerUUID']
    kernel_set = Kernel.objects.filter(kernel_manager_uuid__startswith=
        kernel_manager_uuid, is_delete=False).all()
    if kernel_set.count() == 1:
        kernel_obj = kernel_set[kernel_set.count() - 1]
        kernel_manager_uuid = kernel_obj.kernel_manager_uuid
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            kernel_shared_set = KernelShared.objects.filter(Q(is_delete=0,
                user_group__in=user_groups, kernel__is_delete=0, kernel=
                kernel_obj) | Q(is_delete=0, user=user_obj,
                kernel__is_delete=0, kernel=kernel_obj))
        else:
            kernel_shared_set = KernelShared.objects.filter(is_delete=0,
                user=user_obj, kernel__is_delete=0, kernel=kernel_obj)
        has_edit_rights = False
        if kernel_shared_set.count() > 0:
            kernel_shared_obj = kernel_shared_set[0]
            share_rights_obj = kernel_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_edit_rights = True
        if has_edit_rights:
            env_name = None
            kernel_obj.kernel_venv = env_name
            kernel_obj.save()
    return {'res': 1}


def sparta_b21d863ad8(json_data, user_obj) ->dict:
    """
    Export venv libraries to requirements.txt
    """
    logger.debug('json_data')
    logger.debug(json_data)
    dashboard_id = json_data['dashboardId']
    developer_id = json_data['developerId']
    notebook_id = json_data['notebookId']
    kernelManagerUUID = json_data['kernelManagerUUID']
    if str(dashboard_id) != '-1':
        return sparta_142e4ebcd7(json_data, user_obj)
    if str(developer_id) != '-1':
        return sparta_2d796fad8d(json_data, user_obj)
    if str(notebook_id) != '-1':
        return sparta_92212982f0(json_data, user_obj)
    if str(kernelManagerUUID) != '-1':
        return sparta_a124eaa32e(json_data, user_obj)
    env_name = json_data['env_name']
    project_path = json_data['projectPath']
    if json_data['is_spartaqube_developer_mode']:
        project_path = os.path.join(project_path, 'backend')
    return sparta_7200ccd349(env_name, project_path)


def sparta_142e4ebcd7(json_data, user_obj) ->dict:
    """
    Export venv libraries to requirements.txt (dashboard mode)
    """
    dashboard_id = json_data['dashboardId']
    env_name = json_data['env_name']
    project_path = json_data['projectPath']
    dashboard_set = Dashboard.objects.filter(dashboard_id__startswith=
        dashboard_id, is_delete=False).all()
    if dashboard_set.count() == 1:
        dashboard_obj = dashboard_set[dashboard_set.count() - 1]
        dashboard_id = dashboard_obj.dashboard_id
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            dashboard_shared_set = DashboardShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                dashboard__is_delete=0, dashboard=dashboard_obj) | Q(
                is_delete=0, user=user_obj, dashboard__is_delete=0,
                dashboard=dashboard_obj))
        else:
            dashboard_shared_set = DashboardShared.objects.filter(is_delete
                =0, user=user_obj, dashboard__is_delete=0, dashboard=
                dashboard_obj)
        has_edit_rights = False
        if dashboard_shared_set.count() > 0:
            dashboard_shared_obj = dashboard_shared_set[0]
            share_rights_obj = dashboard_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_edit_rights = True
        if has_edit_rights:
            return sparta_7200ccd349(env_name, project_path)
    return {'res': 1}


def sparta_2d796fad8d(json_data, user_obj) ->dict:
    """
    Export venv libraries to requirements.txt (developer mode)
    """
    developer_id = json_data['developerId']
    env_name = json_data['env_name']
    project_path = json_data['projectPath']
    project_path = os.path.join(project_path, 'backend')
    developer_set = Developer.objects.filter(developer_id__startswith=
        developer_id, is_delete=False).all()
    if developer_set.count() == 1:
        developer_obj = developer_set[developer_set.count() - 1]
        developer_id = developer_obj.developer_id
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            developer_shared_set = DeveloperShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                developer__is_delete=0, developer=developer_obj) | Q(
                is_delete=0, user=user_obj, developer__is_delete=0,
                developer=developer_obj))
        else:
            developer_shared_set = DeveloperShared.objects.filter(is_delete
                =0, user=user_obj, developer__is_delete=0, developer=
                developer_obj)
        has_edit_rights = False
        if developer_shared_set.count() > 0:
            developer_shared_obj = developer_shared_set[0]
            share_rights_obj = developer_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_edit_rights = True
        if has_edit_rights:
            return sparta_7200ccd349(env_name, project_path)
    return {'res': 1}


def sparta_92212982f0(json_data, user_obj) ->dict:
    """
    Export venv libraries to requirements.txt (notebook mode)
    """
    notebook_id = json_data['notebookId']
    env_name = json_data['env_name']
    project_path = json_data['projectPath']
    notebook_set = Notebook.objects.filter(notebook_id__startswith=
        notebook_id, is_delete=False).all()
    if notebook_set.count() == 1:
        notebook_obj = notebook_set[notebook_set.count() - 1]
        notebook_id = notebook_obj.developer_id
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            notebook_shared_set = NotebookShared.objects.filter(Q(is_delete
                =0, user_group__in=user_groups, notebook__is_delete=0,
                notebook=notebook_obj) | Q(is_delete=0, user=user_obj,
                notebook__is_delete=0, notebook=notebook_obj))
        else:
            notebook_shared_set = NotebookShared.objects.filter(is_delete=0,
                user=user_obj, notebook__is_delete=0, notebook=notebook_obj)
        has_edit_rights = False
        if notebook_shared_set.count() > 0:
            notebook_shared_obj = notebook_shared_set[0]
            share_rights_obj = notebook_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_edit_rights = True
        if has_edit_rights:
            return sparta_7200ccd349(env_name, project_path)
    return {'res': 1}


def sparta_a124eaa32e(json_data, user_obj) ->dict:
    """
    Export venv libraries to requirements.txt (kernel notebook mode)
    """
    from project.sparta_6b7c630ead.sparta_2a0a612d78 import qube_6219d0a05d as qube_6219d0a05d
    kernel_manager_uuid = json_data['kernelManagerUUID']
    env_name = json_data['env_name']
    project_path = json_data['projectPath']
    kernel_process_obj = qube_6219d0a05d.sparta_cc49b572ef(user_obj,
        kernel_manager_uuid)
    if kernel_process_obj is None:
        return sparta_7200ccd349(env_name, project_path)
    return {'res': 1}


def sparta_67a7172edf(json_data, user_obj) ->dict:
    """
    Open terminal with venv activated
    """
    logger.debug('json_data')
    logger.debug(json_data)
    env_name = json_data['env_name']
    venv_path = os.path.join(sparta_8f7ff4ab5a(), env_name)
    logger.debug('venv_path')
    logger.debug(venv_path)
    path = sparta_b58678b446(json_data['projectPath'])
    if json_data['is_spartaqube_developer_mode']:
        path = os.path.join(path, 'backend')
    if not os.path.isdir(path):
        return {'res': -1, 'errorMsg':
            f"The provided path '{path}' is not a valid directory."}
    system = platform.system()
    try:
        if system == 'Windows':
            os.system(
                f'start cmd /K "cd /d {path} && {venv_path}\\Scripts\\activate.bat"'
                )
        elif system == 'Linux':
            subprocess.run(['x-terminal-emulator', '-e',
                f'bash -c "cd {path} && source {venv_path}/bin/activate && exec bash"'
                ], check=True)
        elif system == 'Darwin':
            script = f"""
            tell application "Terminal"
                do script "cd {path} && source {venv_path}/bin/activate"
                activate
            end tell
            """
            subprocess.run(['osascript', '-e', script], check=True)
        else:
            return {'res': -1, 'errorMsg': 'Unsupported operating system.'}
    except Exception as e:
        return {'res': -1, 'errorMsg':
            f"Failed to open terminal and activate venv at '{path}': {e}"}
    return {'res': 1}

#END OF QUBE
