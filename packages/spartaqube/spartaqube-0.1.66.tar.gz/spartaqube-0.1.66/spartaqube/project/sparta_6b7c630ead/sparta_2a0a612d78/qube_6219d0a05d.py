import os, sys
import gc
import socket
import subprocess
import threading
import platform
import psutil
import zmq
import json
import base64
import shutil
import zipfile
import io
import uuid
import cloudpickle
from django.conf import settings
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime, timedelta
from pathlib import Path
from dateutil import parser
import pytz
UTC = pytz.utc
import concurrent.futures
from django.contrib.humanize.templatetags.humanize import naturalday
from project.models import KernelProcess
from project.sparta_6b7c630ead.sparta_e2518651f2.qube_be904e792d import sparta_e00a19a2be, sparta_91e532a07f, sparta_3f45882936
from project.sparta_6b7c630ead.sparta_2a0a612d78.qube_69c3b11034 import SenderKernel
from project.logger_config import logger


def sparta_f522ecd5b9():
    """Find an available port on the system."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


class SqKernelManager:

    def __init__(self, kernel_manager_uuid, type, name, user, user_kernel=
        None, project_folder=None, notebook_exec_id='-1', dashboard_exec_id
        ='-1', venv_name=None):
        """
        Type: 1:   plotDB (Transformation Step)
              2:   Dashboard
              3:   Developer App
              4:   Ipynb ide filetab (Notebook or Dashboard Ipynb with IDE)
              5:   Notebook exec
              10:  PythonChart
              30:  Developer Examples
              100: Kernel Notebook
        """
        self.kernel_manager_uuid = kernel_manager_uuid
        self.type = type
        self.name = name
        self.user = user
        self.kernel_user_logged = user
        self.project_folder = project_folder
        if user_kernel is None:
            user_kernel = user
        self.user_kernel = user_kernel
        self.venv_name = venv_name
        self.notebook_exec_id = notebook_exec_id
        self.dashboard_exec_id = dashboard_exec_id
        self.is_init = False
        self.created_time = datetime.now()

    def create_kernel(self, django_settings_module=None):
        """
        Create kernel
        """
        if self.notebook_exec_id != '-1':
            self.user_kernel = sparta_91e532a07f(self.notebook_exec_id)
        if self.dashboard_exec_id != '-1':
            self.user_kernel = sparta_3f45882936(self.dashboard_exec_id)
        current_path = os.path.dirname(__file__)
        api_key = sparta_e00a19a2be(self.user_kernel)
        kernel_process_port = sparta_f522ecd5b9()
        python_executable = sys.executable
        venv_str = self.venv_name if self.venv_name is not None else '-1'

        def read_output(pipe):
            """Reads output from the process and prints it line by line."""
            for line in iter(pipe.readline, ''):
                logger.debug(line, end='')
            pipe.close()
        env = os.environ.copy()
        env['ZMQ_PROCESS'] = '1'
        logger.debug(f'SPAWN PYTHON KERNEL {kernel_process_port}')
        process = subprocess.Popen([python_executable, 'spawnKernel.py',
            str(api_key), str(kernel_process_port), venv_str], stdout=
            subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=
            current_path, env=env)
        pid = process.pid
        date_now = datetime.now().astimezone(UTC)
        kernel_process_obj = sparta_cc49b572ef(self.user, self.kernel_manager_uuid)
        if kernel_process_obj is None:
            kernel_process_obj = KernelProcess.objects.create(
                kernel_manager_uuid=self.kernel_manager_uuid, port=
                kernel_process_port, pid=pid, date_created=date_now, user=
                self.user, name=self.name, type=self.type, notebook_exec_id
                =self.notebook_exec_id, dashboard_exec_id=self.dashboard_exec_id, venv_name=self.venv_name, project_folder
                =self.project_folder, last_update=date_now)
        else:
            kernel_process_obj.port = kernel_process_port
            kernel_process_obj.pid = pid
            kernel_process_obj.name = self.name
            kernel_process_obj.type = self.type
            kernel_process_obj.notebook_exec_id = self.notebook_exec_id
            kernel_process_obj.dashboard_exec_id = self.dashboard_exec_id
            kernel_process_obj.venv_name = self.venv_name
            kernel_process_obj.project_folder = self.project_folder
            kernel_process_obj.last_update = date_now
            kernel_process_obj.save()
        return {'res': 1, 'kernel_process_obj': kernel_process_obj}


def sparta_3acff16bf4(kernel_process_obj) ->float:
    """
    This function returns the size (in mb) of the kernel using ZMQ
    """
    sender_kernel_obj = SenderKernel(websocket=None, port=
        kernel_process_obj.port)
    return sender_kernel_obj.sync_get_kernel_size()


def sparta_f6acf7f512(kernel_process_obj) ->list:
    """
    This function returns the workspace variables list using ZMQ
    """
    sender_kernel_obj = SenderKernel(websocket=None, port=
        kernel_process_obj.port)
    return sender_kernel_obj.sync_get_kernel_workspace_variables()


def sparta_ff397fcdb1(kernel_process_obj, venv_name) ->list:
    """
    Activate venv in a kernel using ZMQ
    """
    sender_kernel_obj = SenderKernel(websocket=None, port=
        kernel_process_obj.port)
    return sender_kernel_obj.sync_activate_venv(venv_name)


def sparta_121abd608d(kernel_process_obj, kernel_varname) ->list:
    """
    Get kernel variable repr using ZMQ
    """
    sender_kernel_obj = SenderKernel(websocket=None, port=
        kernel_process_obj.port)
    return sender_kernel_obj.sync_get_kernel_variable_repr(kernel_varname)


def sparta_01768c0c93(kernel_process_obj, var_name, var_value) ->list:
    """
    Set variable kernel variable using ZMQ
    """
    sender_kernel_obj = SenderKernel(websocket=None, port=
        kernel_process_obj.port)
    return sender_kernel_obj.sync_set_workspace_variable(var_name, var_value)


def set_workspace_cloudpickle_variables(kernel_process_obj,
    cloudpickle_kernel_variables) ->list:
    """
    Set variable kernel variable using ZMQ
    """
    sender_kernel_obj = SenderKernel(websocket=None, port=
        kernel_process_obj.port)
    return sender_kernel_obj.sync_set_workspace_cloudpickle_variables(
        cloudpickle_kernel_variables)


def sparta_9f458922bf(kernel_process_obj) ->dict:
    """
    Get cloudpickle kernel variables using ZMQ (returns both the pickles variables and the list of unpickled variables)
    """
    sender_kernel_obj = SenderKernel(websocket=None, port=
        kernel_process_obj.port)
    return sender_kernel_obj.sync_get_cloudpickle_kernel_variables()


def sparta_c653ac3bb7(pid) ->list:
    """
    Forcefully kills a process
    """
    logger.debug('Force Kill Process now from kernel manager')
    if platform.system() == 'Windows':
        return sparta_dc3d17d56b(pid)
    else:
        return sparta_6cca09ee05(pid)


def sparta_dc3d17d56b(pid):
    """
    Forcefully kills a process using taskkill command."""
    try:
        subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        logger.debug(f'Failed to kill process {pid}. It may not exist.')


def sparta_6cca09ee05(pid):
    """
    Forcefully kills a process using the 'kill -9' command on Linux/macOS."""
    try:
        subprocess.run(['kill', '-9', str(pid)], check=True, stdout=
            subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        logger.debug(f'Failed to kill process {pid}. It may not exist.')


def sparta_369d63a5fa(kernel_process_obj):
    """
    Kill python process with PID
    """
    pid = kernel_process_obj.pid
    sparta_c653ac3bb7(pid)


def sparta_cc49b572ef(user_obj, kernel_manager_uuid) ->KernelProcess:
    """
    Return KernelProcess Model
    """
    kernel_process_set = KernelProcess.objects.filter(user=user_obj,
        kernel_manager_uuid=kernel_manager_uuid, is_delete=False)
    if kernel_process_set.count() > 0:
        return kernel_process_set[0]


def sparta_450631db33(json_data, user_obj, b_return_model=False) ->dict:
    """
    Create a new kernel
    """
    logger.debug('Create new kernel')
    logger.debug(json_data)
    kernel_manager_uuid = json_data['kernelManagerUUID']
    kernel_type = int(json_data['kernelType'])
    name = json_data.get('name', 'undefined')
    project_folder = json_data.get('fullpath', None)
    notebook_exec_id = json_data.get('notebookExecId', '-1')
    dashboard_exec_id = json_data.get('dashboardExecId', '-1')
    venv_name = json_data.get('venvName', '')
    if len(venv_name) == 0:
        venv_name = None
    if project_folder is not None:
        project_folder = os.path.dirname(project_folder)
    sq_kernel_manager_obj = SqKernelManager(kernel_manager_uuid,
        kernel_type, name, user_obj, user_kernel=user_obj, project_folder=
        project_folder, notebook_exec_id=notebook_exec_id,
        dashboard_exec_id=dashboard_exec_id, venv_name=venv_name)
    if kernel_type == 3 or kernel_type == 4 or kernel_type == 5:
        res_create_dict = sq_kernel_manager_obj.create_kernel(
            django_settings_module='app.settings')
    else:
        res_create_dict = sq_kernel_manager_obj.create_kernel()
    if b_return_model:
        return res_create_dict
    return {'res': 1}


def sparta_192bc84c86(json_data, user_obj) ->dict:
    """
    Restart kernel (recreate it from scratch)
    """
    kernel_manager_uuid = json_data['kernelManagerUUID']
    kernel_process_obj = sparta_cc49b572ef(user_obj, kernel_manager_uuid
        )
    if kernel_process_obj is not None:
        sparta_369d63a5fa(kernel_process_obj)
        kernel_type = kernel_process_obj.type
        name = kernel_process_obj.name
        project_folder = kernel_process_obj.project_folder
        notebook_exec_id = kernel_process_obj.notebook_exec_id
        dashboard_exec_id = kernel_process_obj.dashboard_exec_id
        user_kernel = kernel_process_obj.user_kernel
        venv_name = kernel_process_obj.venv_name
        sq_kernel_manager_obj = SqKernelManager(kernel_manager_uuid,
            kernel_type, name, user_obj, user_kernel=user_kernel,
            project_folder=project_folder, notebook_exec_id=
            notebook_exec_id, dashboard_exec_id=dashboard_exec_id,
            venv_name=venv_name)
        if kernel_type == 3 or kernel_type == 4 or kernel_type == 5:
            sq_kernel_manager_obj.create_kernel(django_settings_module=
                'app.settings')
        else:
            sq_kernel_manager_obj.create_kernel()
    return {'res': 1}


def sparta_00e3975dd3(json_data, user_obj) ->dict:
    """
    Activate a virtual environment
    """
    if 'kernelManagerUUID' in json_data:
        kernel_manager_uuid = json_data['kernelManagerUUID']
        venv_name = json_data['env_name']
        kernel_process_obj = sparta_cc49b572ef(user_obj,
            kernel_manager_uuid)
        if kernel_process_obj is not None:
            sparta_ff397fcdb1(kernel_process_obj, venv_name)
    return {'res': 1}


def sparta_5802517bbd(json_data, user_obj) ->dict:
    """
    Get kernel infos (like the name, size, uptime and workspace variables)
    """
    kernel_manager_uuid = json_data['kernelManagerUUID']
    kernel_process_obj = sparta_cc49b572ef(user_obj, kernel_manager_uuid
        )
    if kernel_process_obj is not None:
        kernel_size = sparta_3acff16bf4(kernel_process_obj)
        workspace_variables = sparta_f6acf7f512(kernel_process_obj
            )
        return {'res': 1, 'kernel': {'workspace_variables':
            workspace_variables, 'kernel_manager_uuid': kernel_manager_uuid,
            'kernel_size': kernel_size, 'type': kernel_process_obj.type,
            'name': kernel_process_obj.name, 'created_time_str': str(
            kernel_process_obj.date_created.strftime('%Y-%m-%d %H:%M:%S')),
            'created_time': naturalday(parser.parse(str(kernel_process_obj.date_created)))}}
    return {'res': -1}


def sparta_5672577480(json_data, user_obj) ->dict:
    """
    Get kernel variable from a kernel
    """
    kernel_manager_uuid = json_data['kernelManagerUUID']
    kernel_varname = json_data['varName']
    kernel_process_obj = sparta_cc49b572ef(user_obj, kernel_manager_uuid
        )
    if kernel_process_obj is not None:
        htmlReprDict = sparta_121abd608d(kernel_process_obj,
            kernel_varname)
        return {'res': 1, 'htmlReprDict': htmlReprDict}
    return {'res': -1}


def sparta_9c94ea658f(json_data, user_obj) ->dict:
    """
    Update kernel infos
    """
    kernel_manager_uuid = json_data['kernelManagerUUID']
    kernel_process_obj = sparta_cc49b572ef(user_obj, kernel_manager_uuid
        )
    if kernel_process_obj is not None:
        name = json_data.get('name', None)
        if name is not None:
            kernel_process_obj.name = name
            kernel_process_obj.save()
            sparta_01768c0c93(kernel_process_obj, 'name', name)
    return {'res': 1}


def sparta_c1cf15b750() ->list:
    if platform.system() == 'Windows':
        return sparta_7a3733e579()
    else:
        return sparta_3239d1dd27()


def sparta_40c3bf0f84(command: str) ->str:
    """Helper to run subprocess safely using concurrent.futures."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(subprocess.run, command, shell=True,
            capture_output=True, text=True)
        result = future.result()
        return result.stdout.strip()


def sparta_7a3733e579() ->list:
    return sparta_5a0a6df74c()


def sparta_607f7bb03b() ->list:
    """Finds the parent process that started spawnKernel.py on Windows (fast + WMIC-free)."""
    import psutil
    kernel_processes = []
    try:
        for proc in psutil.process_iter(['pid', 'ppid', 'name', 'cmdline']):
            try:
                if not proc.info['name'] or 'python' not in proc.info['name'
                    ].lower():
                    continue
                cmdline = proc.info.get('cmdline') or []
                if any('spawnKernel.py' in part for part in cmdline):
                    port = cmdline[3] if len(cmdline) > 3 else None
                    kernel_processes.append({'PID': str(proc.info['pid']),
                        'PPID': str(proc.info['ppid']), 'CommandLine': ' '.join(cmdline), 'port': port})
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        logger.error(f'Unexpected error finding spawnKernel.py: {e}')
    return kernel_processes


def sparta_5a0a6df74c():
    """Finds the parent process that started spawnKernel.py on Windows (fast + WMIC-free)."""
    try:
        output = subprocess.check_output(['tasklist'], text=True)
        python_pids = []
        for line in output.splitlines():
            if 'python.exe' in line.lower():
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    python_pids.append(int(parts[1]))
        spawn_kernels = []
        for pid in python_pids:
            try:
                proc = psutil.Process(pid)
                cmdline = proc.cmdline()
                if any('spawnKernel.py' in arg for arg in cmdline):
                    port = cmdline[3] if len(cmdline) > 3 else None
                    spawn_kernels.append({'PID': str(proc.pid), 'PPID': str
                        (proc.ppid()), 'CommandLine': ' '.join(cmdline),
                        'port': port})
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return spawn_kernels
    except Exception as e:
        print(f'Error: {e}')
        return []


def sparta_dce2d87c8e() ->list:
    """Finds the parent process that started spawnKernel.py on Windows."""
    try:
        command = (
            'wmic process where "name=\'python.exe\'" get ProcessId,ParentProcessId,CommandLine /FORMAT:CSV'
            )
        result = sparta_40c3bf0f84(command)
        kernel_processes = []
        lines = result.splitlines()
        for line in lines[2:]:
            parts = [part.strip() for part in line.split(',')]
            if len(parts) < 4:
                continue
            command_line = parts[1]
            process_id = parts[2]
            parent_process_id = parts[3]
            if 'spawnKernel.py' in command_line:
                command_line_list = command_line.split()
                port = command_line_list[3] if len(command_line_list
                    ) > 3 else None
                kernel_processes.append({'PID': process_id, 'PPID':
                    parent_process_id, 'CommandLine': command_line, 'port':
                    port})
        return kernel_processes
    except Exception as e:
        logger.error(f'Unexpected error finding spawnKernel.py: {e}')
        return []


def sparta_3239d1dd27() ->list:
    """Finds the parent process that started spawnKernel.py on Linux/macOS."""
    try:
        result = sparta_40c3bf0f84(
            "ps -eo pid,ppid,command | grep '[s]pawnKernel.py'")
        kernel_processes = []
        lines = result.split('\n')
        for line in lines:
            parts = line.strip().split(maxsplit=2)
            if len(parts) < 3:
                continue
            process_id, parent_process_id, command_line = parts
            command_line_list = command_line.split()
            port = command_line_list[3] if len(command_line_list) > 3 else None
            kernel_processes.append({'PID': process_id, 'PPID': process_id,
                'CommandLine': command_line, 'port': port})
        return kernel_processes
    except Exception as e:
        logger.error(f'Unexpected error finding spawnKernel.py: {e}')
        return []


def sparta_c36875fcb4(json_data, user_obj) ->dict:
    """
    
    """
    b_require_size = json_data.get('b_require_size', False)
    b_require_workspace_variables = json_data.get(
        'b_require_workspace_variables', False)
    b_require_offline_kernels = json_data.get('b_require_offline_kernels', 
        False)
    stored_uuids = []
    if b_require_offline_kernels:
        from project.sparta_6b7c630ead.sparta_3f2c129899 import qube_f4326e0ae5 as qube_f4326e0ae5
        stored_uuids = qube_f4326e0ae5.sparta_fae8e0a98c(user_obj)
    zmq_processes = sparta_c1cf15b750()
    my_kernels_list = []
    pid_port_pairs = [(proc['PPID'], proc['port']) for proc in zmq_processes]
    if len(pid_port_pairs) > 0:
        matching_processes = KernelProcess.objects.filter(pid__in=[p[0] for
            p in pid_port_pairs], port__in=[p[1] for p in pid_port_pairs],
            user=user_obj).distinct()
        for kernel_process_obj in matching_processes:
            size = None
            if b_require_size:
                size = sparta_3acff16bf4(kernel_process_obj)
            workspace_variables = []
            if b_require_workspace_variables:
                workspace_variables = sparta_f6acf7f512(
                    kernel_process_obj)
            my_kernels_list.append({'kernel_manager_uuid':
                kernel_process_obj.kernel_manager_uuid,
                'workspace_variables': workspace_variables, 'type':
                kernel_process_obj.type, 'name': kernel_process_obj.name,
                'created_time_str': str(kernel_process_obj.date_created.strftime('%Y-%m-%d %H:%M:%S')), 'created_time': naturalday(
                parser.parse(str(kernel_process_obj.date_created))), 'size':
                size, 'isStored': True if kernel_process_obj.kernel_manager_uuid in stored_uuids else False})
    return {'res': 1, 'kernels': my_kernels_list}


def sparta_26237857b5(json_data, user_obj) ->dict:
    """
    List offline kernels
    """
    from project.sparta_6b7c630ead.sparta_3f2c129899 import qube_f4326e0ae5 as qube_f4326e0ae5
    kernel_library_list = qube_f4326e0ae5.sparta_d9c6c0daf0(user_obj
        )
    kernel_list_live_dict = sparta_c36875fcb4(json_data, user_obj)
    if kernel_list_live_dict['res'] == 1:
        kernel_list_live = kernel_list_live_dict['kernels']
        kernel_manager_uuid_live = [elem['kernel_manager_uuid'] for elem in
            kernel_list_live]
        kernel_library_list = [elem for elem in kernel_library_list if elem
            ['kernel_manager_uuid'] not in kernel_manager_uuid_live]
        return {'res': 1, 'kernel_library': kernel_library_list}
    return {'res': -1}


def sparta_4550e1bc0a(json_data, user_obj) ->dict:
    """
    Kill a specific kernel
    """
    kernel_manager_uuid = json_data['kernelManagerUUID']
    kernel_process_obj = sparta_cc49b572ef(user_obj, kernel_manager_uuid
        )
    if kernel_process_obj is not None:
        sparta_369d63a5fa(kernel_process_obj)
    return {'res': 1}


def sparta_33be590818(json_data, user_obj) ->dict:
    """
    Kills all kernels
    """
    available_kernels_dict = sparta_c36875fcb4(json_data, user_obj)
    if available_kernels_dict['res'] == 1:
        kernels_list = available_kernels_dict['kernels']
        for kernel_dict in kernels_list:
            json_data_dict = {'kernelManagerUUID': kernel_dict[
                'kernel_manager_uuid']}
            sparta_4550e1bc0a(json_data_dict, user_obj)
    return {'res': 1}


def sparta_5fe81eedfb():
    """
    Kill all existing kernels
    """
    cypress_user_email = 'cypress_tests@gmail.com'
    kernel_process_set = KernelProcess.objects.filter(user__email=
        cypress_user_email, is_delete=False)
    for kernel_process_obj in kernel_process_set:
        print(f'Kill kernel: {kernel_process_obj}')
        sparta_369d63a5fa(kernel_process_obj)
    return {'res': 1}


def sparta_ce3851a62f(json_data, user_obj) ->dict:
    """
    Start offline kernel
    """
    kernel_manager_uuid = json_data['kernelManagerUUID']
    from project.sparta_6b7c630ead.sparta_3f2c129899 import qube_f4326e0ae5 as qube_f4326e0ae5
    kernel_obj = qube_f4326e0ae5.sparta_fc1b2b73bb(user_obj, kernel_manager_uuid
        )
    kernel_process_obj = sparta_cc49b572ef(user_obj, kernel_manager_uuid
        )
    if kernel_process_obj is not None:
        venv_name = kernel_process_obj.venv_name
        if venv_name is None:
            venv_name = ''
        json_data = {'kernelType': 100, 'kernelManagerUUID':
            kernel_manager_uuid, 'name': kernel_process_obj.name,
            'venvName': venv_name}
        create_res_dict = sparta_450631db33(json_data, user_obj, True)
        if create_res_dict['res'] == 1:
            kernel_process_obj = create_res_dict['kernel_process_obj']
            if kernel_obj.is_static_variables:
                kernel_variables = kernel_obj.kernel_variables
                if kernel_variables is not None:
                    set_workspace_cloudpickle_variables(kernel_process_obj,
                        kernel_variables)
        return {'res': create_res_dict['res']}
    return {'res': -1}


def sparta_bd85cb9771(json_data, user_obj) ->dict:
    """
    Search variable across all active kernels
    """
    return {'res': 1}

#END OF QUBE
