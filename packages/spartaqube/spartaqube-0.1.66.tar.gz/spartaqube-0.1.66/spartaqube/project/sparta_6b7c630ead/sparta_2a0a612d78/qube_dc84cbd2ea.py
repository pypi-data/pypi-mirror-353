import json, io, base64, os, sys
import cloudpickle
import pandas as pd
from project.logger_config import logger
from project.sparta_6b7c630ead.sparta_24d6941379.qube_d24a333a34 import IPythonKernel


def sparta_f66826e34d(file_path, text):
    """
    For debugging purpose only
    """
    try:
        mode = 'a' if os.path.exists(file_path) and os.path.getsize(file_path
            ) > 0 else 'w'
        with open(file_path, mode, encoding='utf-8') as file:
            if mode == 'a':
                file.write('\n')
            file.write(text)
        logger.debug(f'Successfully wrote/appended to {file_path}')
    except Exception as e:
        logger.debug(f'Error writing to file: {e}')


class ReceiverKernel:

    def __init__(self, ipython_kernel, socket_zmq):
        self.ipython_kernel = ipython_kernel
        self.socket_zmq = socket_zmq

    async def send_response(self, identity, response_dict, request_dict=None):
        """
        Send response (using ZMQ)
        """
        final_dict = response_dict
        if request_dict is not None:
            final_dict.update(request_dict)
        final_dict['is_terminated'] = True
        await self.socket_zmq.send_multipart([identity, json.dumps(
            final_dict).encode()])

    async def terminate(self, identity):
        """
        
        """
        response_dict = {'res': 1, 'service': 'break-loop', 'is_terminated':
            True, 'response': 1}
        await self.send_response(identity, response_dict)

    async def create_new_ipython_kernel(self, api_key, venv):
        """
        Create a new ipython_kernel
        """
        ipython_kernel = IPythonKernel(api_key)
        await ipython_kernel.initialize()
        if venv != '-1':
            await ipython_kernel.activate_venv(venv)
        self.ipython_kernel = ipython_kernel

    async def process_request(self, identity, request_dict: dict):
        """
        
        """
        service = request_dict['service']
        ipython_kernel = self.ipython_kernel
        ipython_kernel.set_zmq_identity(identity)
        ipython_kernel.set_zmq_request(request_dict)
        if service == 'execute_code':
            cmd = request_dict['cmd']
            await ipython_kernel.execute_code(cmd, websocket=self.socket_zmq)
        elif service == 'execute_shell':
            cmd = request_dict['cmd']
            json_data = json.loads(request_dict['json_data'])
            await ipython_kernel.execute_shell(cmd, websocket=self.socket_zmq, cell_id=json_data['cellId'])
        elif service == 'execute':
            cmd = request_dict['cmd']
            json_data = json.loads(request_dict['json_data'])
            await ipython_kernel.execute(cmd, websocket=self.socket_zmq,
                cell_id=json_data['cellId'])
        elif service == 'activate_venv':
            venv_name = request_dict['venv_name']
            await ipython_kernel.activate_venv(venv_name)
            await self.terminate(identity)
        elif service == 'deactivate_venv':
            await ipython_kernel.deactivate_venv()
            await self.terminate(identity)
        elif service == 'get_kernel_variable_repr':
            kernel_variable = request_dict['kernel_variable']
            workspace_variable_repr = (ipython_kernel._method_get_kernel_variable_repr(kernel_variable=
                kernel_variable))
            response_dict = {'res': 1, 'response': workspace_variable_repr}
            await self.send_response(identity, response_dict, request_dict)
        elif service == 'get_workspace_variable':
            kernel_variable = request_dict['kernel_variable']
            workspace_variable = (await ipython_kernel._method_get_workspace_variable(kernel_variable=kernel_variable)
                )
            encoded_workspace_variable = base64.b64encode(cloudpickle.dumps
                (workspace_variable)).decode('utf-8')
            response_dict = {'res': 1, 'response': encoded_workspace_variable}
            await self.send_response(identity, response_dict, request_dict)
        elif service == 'reset_kernel_workspace':
            ipython_kernel.reset_kernel_workspace()
            await self.terminate(identity)
        elif service == 'list_workspace_variables':
            workspace_variables = (await ipython_kernel.list_workspace_variables())
            response_dict = {'res': 1, 'response': workspace_variables}
            await self.send_response(identity, response_dict, request_dict)
        elif service == 'set_workspace_variable':
            json_data = json.loads(request_dict['json_data'])
            await ipython_kernel._method_set_workspace_variable(name=
                json_data['name'], value=json.loads(json_data['value']))
            await self.terminate(identity)
        elif service == 'set_workspace_variables':
            data_dict = cloudpickle.loads(base64.b64decode(request_dict[
                'encoded_dict']))
            for var_name, var_value in data_dict.items():
                await ipython_kernel._method_set_workspace_variable(var_name,
                    var_value)
            await self.terminate(identity)
        elif service == 'set_workspace_variable_from_datasource':
            json_data = json.loads(request_dict['json_data'])
            data_dict = json.loads(json_data['value'])
            datasource_df = pd.DataFrame(data_dict['data'], columns=
                data_dict['columns'], index=data_dict['index'])
            await ipython_kernel._method_set_workspace_variable(name=
                json_data['name'], value=datasource_df)
            await self.terminate(identity)
        elif service == 'get_kernel_memory_size':
            size_in_bytes = await ipython_kernel.get_kernel_memory_size()
            response_dict = {'res': 1, 'response': size_in_bytes}
            await self.send_response(identity, response_dict, request_dict)
        elif service == 'set_workspace_cloudpickle_variable':
            kernel_variables = base64.b64decode(request_dict[
                'cloudpickle_kernel_variables'])
            kernel_variables = cloudpickle.loads(kernel_variables)
            for var_name, var_value in kernel_variables.items():
                buffer = io.BytesIO(var_value)
                restored_var = cloudpickle.load(buffer)
                await ipython_kernel._method_set_workspace_variable(var_name,
                    restored_var)
            await self.terminate(identity)
        elif service == 'set_workspace_variable_from_paste_modal':
            json_data = json.loads(request_dict['json_data'])
            await ipython_kernel._method_set_workspace_variable_from_paste_modal(
                name=json_data['name'], value=json_data['df_json'])
            await self.terminate(identity)
        elif service == 'get_cloudpickle_kernel_all_variables':
            kernel_cpkl_picklable, kernel_cpkl_unpicklable = (await
                ipython_kernel.cloudpickle_kernel_variables())
            response_dict = {'res': 1, 'response': json.dumps({'picklable':
                base64.b64encode(cloudpickle.dumps(kernel_cpkl_picklable)).decode('utf-8'), 'unpicklable': base64.b64encode(
                cloudpickle.dumps(kernel_cpkl_unpicklable)).decode('utf-8')})}
            await self.send_response(identity, response_dict, request_dict)

#END OF QUBE
