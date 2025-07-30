import os, sys
import uuid
import zmq
import zmq.asyncio
import json
import base64
import cloudpickle
import asyncio
import concurrent.futures
from project.logger_config import logger


def sparta_f8452b9cfe(func):
    """Decorator to handle ZMQ connection setup and teardown."""

    async def wrapper(self, *args, **kwargs):
        self.zmq_connect()
        try:
            return await func(self, *args, **kwargs)
        finally:
            self.zmq_close()
    return wrapper


def sparta_19f9a5b2b4(func):
    """Decorator to handle ZMQ connection setup and teardown."""

    async def wrapper(self, *args, **kwargs):
        self.zmq_connect_sync()
        try:
            return await func(self, *args, **kwargs)
        finally:
            self.zmq_close()
    return wrapper


class SenderKernel:

    def __init__(self, websocket, port):
        self.websocket = websocket
        self.port = port
        self.zmq_context = None
        self.zmq_socket = None

    def zmq_connect(self):
        """
        Default behavior (async conect within websocket due to AsyncWebsocketConsumer)
        """
        logger.debug('ZMQ connect now')
        if self.zmq_socket is None:
            identity = str(uuid.uuid4())
            logger.debug(f'Async Identity: {identity} on port {self.port}')
            self.zmq_context = zmq.asyncio.Context()
            self.zmq_socket = self.zmq_context.socket(zmq.DEALER)
            self.zmq_socket.setsockopt_string(zmq.IDENTITY, identity)
            self.zmq_socket.connect(f'tcp://127.0.0.1:{self.port}')
        elif not self.zmq_socket.getsockopt(zmq.LAST_ENDPOINT):
            self.zmq_socket.connect(f'tcp://127.0.0.1:{self.port}')
        logger.debug('ZMQ is connected')

    def zmq_connect_sync(self):
        """
        Sync connection (when we use it without async context, like normal wsService http queries)
        """
        if self.zmq_socket is None:
            identity = str(uuid.uuid4())
            logger.debug(f'Sync Identity: {identity} on port {self.port}')
            self.zmq_context = zmq.Context()
            self.zmq_socket = self.zmq_context.socket(zmq.DEALER)
            self.zmq_socket.setsockopt_string(zmq.IDENTITY, identity)
            self.zmq_socket.connect(f'tcp://127.0.0.1:{self.port}')
        elif not self.zmq_socket.getsockopt(zmq.LAST_ENDPOINT):
            self.zmq_socket.connect(f'tcp://127.0.0.1:{self.port}')
        logger.debug('ZMQ is connected')

    def zmq_close(self):
        """
        Close zmq connection
        """
        self.zmq_socket.close(linger=0)
        self.zmq_context.term()

    async def send_zmq_request(self, sender_dict: dict,
        b_send_websocket_msg=True):
        """
        Internal async function to send a ZMQ request."""
        await self.zmq_socket.send_string(json.dumps(sender_dict))
        print('ZMQ sent...')
        while True:
            response_dict = json.loads(await self.zmq_socket.recv_string())
            service = response_dict['service']
            logger.debug(f'service >>> {service}')
            if service in ['exec', 'execute_code', 'execute_shell',
                'execute', 'activate_venv', 'deactivate_venv',
                'reset_kernel_workspace', 'set_workspace_variable',
                'set_workspace_variables',
                'set_workspace_variable_from_datasource',
                'set_workspace_variable_from_paste_modal']:
                if b_send_websocket_msg:
                    await self.websocket.send(json.dumps(response_dict))
            elif service in ['get_kernel_variable_repr',
                'list_workspace_variables']:
                return response_dict['response']
            elif service in ['get_workspace_variable']:
                encoded_kernel_variables = base64.b64decode(response_dict[
                    'response'])
                kernel_variables = cloudpickle.loads(encoded_kernel_variables)
                return kernel_variables
            if response_dict['is_terminated']:
                return

    def sync_request(self, sender_dict, timeout=3000) ->float:
        """
        Sync query
        """
        self.zmq_connect_sync()
        self.zmq_socket.send_string(json.dumps(sender_dict))
        logger.debug('Sync request sent')
        poller = zmq.Poller()
        poller.register(self.zmq_socket, zmq.POLLIN)
        if poller.poll(timeout):
            res_dict = self.zmq_socket.recv_json()
            res = res_dict['response']
        else:
            res = -1
        logger.debug(f"SERVICE SYNC REQUEST {sender_dict['service']}")
        logger.debug(res)
        self.zmq_close()
        return res

    def sync_create_kernel(self, api_key, venv) ->float:
        """Calls async create a new kernel () in a synchronous way."""
        sender_dict = {'service': 'create_kernel', 'api_key': api_key,
            'venv': venv}
        return self.sync_request(sender_dict)

    def sync_list_available_kernels(self) ->float:
        """Calls async to list available (live) kernels in a synchronous way."""
        sender_dict = {'service': 'list_available_kernels'}
        return self.sync_request(sender_dict)

    def sync_kill_kernel(self) ->float:
        """Calls async to kill a kernel in a synchronous way."""
        sender_dict = {'service': 'kill_kernel'}
        return self.sync_request(sender_dict)

    def sync_get_kernel_size(self) ->float:
        """Calls async get_kernel_size() in a synchronous way."""
        sender_dict = {'service': 'get_kernel_memory_size'}
        return self.sync_request(sender_dict)

    def sync_get_kernel_workspace_variables(self) ->list:
        """Calls get_kernel_workspace_variables() in a synchronous way."""
        sender_dict = {'service': 'list_workspace_variables'}
        return self.sync_request(sender_dict)

    def sync_activate_venv(self, venv_name) ->list:
        """Calls activate_venv() in a synchronous way."""
        sender_dict = {'service': 'activate_venv', 'venv_name': venv_name}
        return self.sync_request(sender_dict)

    def sync_get_kernel_variable_repr(self, kernel_variable) ->list:
        """Calls get_kernel_variable_repr() in a synchronous way."""
        sender_dict = {'service': 'get_kernel_variable_repr',
            'kernel_variable': kernel_variable}
        return self.sync_request(sender_dict)

    def sync_set_workspace_variable(self, var_name, var_value) ->list:
        """Calls set_workspace_variable() in a synchronous way."""
        sender_dict = {'service': 'set_workspace_variable', 'json_data':
            json.dumps({'name': var_name, 'value': json.dumps(var_value)})}
        return self.sync_request(sender_dict)

    def sync_set_workspace_cloudpickle_variables(self,
        cloudpickle_kernel_variables) ->list:
        """Calls set_workspace_cloudpickle_variable() in a synchronous way."""
        sender_dict = {'service': 'set_workspace_cloudpickle_variable',
            'cloudpickle_kernel_variables': base64.b64encode(
            cloudpickle_kernel_variables).decode('utf-8')}
        return self.sync_request(sender_dict)

    def sync_get_cloudpickle_kernel_variables(self) ->dict:
        """
        Get cloudpickle kernel variables
        """
        sender_dict = {'service': 'get_cloudpickle_kernel_all_variables'}
        res_dict = self.sync_request(sender_dict)
        if isinstance(res_dict, int):
            return None
        else:
            response_dict = json.loads(res_dict)
            response_dict['picklable'] = base64.b64decode(response_dict[
                'picklable'])
            response_dict['unpicklable'] = base64.b64decode(response_dict[
                'unpicklable'])
            return response_dict

#END OF QUBE
