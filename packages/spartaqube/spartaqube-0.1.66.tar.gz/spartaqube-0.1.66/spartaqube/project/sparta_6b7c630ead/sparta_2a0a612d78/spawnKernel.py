import zmq
import zmq.asyncio
import json
import sys
import os, sys
import asyncio
current_path = os.path.dirname(__file__)
core_path = os.path.dirname(current_path)
project_path = os.path.dirname(core_path)
main_path = os.path.dirname(project_path)
sys.path.insert(0, main_path)
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
os.chdir(main_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'spartaqube_app.settings'
from project.sparta_6b7c630ead.sparta_24d6941379.qube_d24a333a34 import IPythonKernel
from project.sparta_6b7c630ead.sparta_2a0a612d78.qube_dc84cbd2ea import ReceiverKernel
from project.logger_config import logger


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


async def start_worker(api_key, worker_port, venv_str):
    """
    Worker process that holds the IPythonKernel and listens for execution requests."""
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.ROUTER)
    socket.bind(f'tcp://127.0.0.1:{worker_port}')
    ipython_kernel = IPythonKernel(api_key)
    await ipython_kernel.initialize()
    if venv_str != '-1':
        await ipython_kernel.activate_venv(venv_str)
    receiver_kernel_obj = ReceiverKernel(ipython_kernel, socket)
    while True:
        identity, message = await socket.recv_multipart()
        request = json.loads(message)
        await receiver_kernel_obj.process_request(identity, request)


if __name__ == '__main__':
    api_key = sys.argv[1]
    worker_port = sys.argv[2]
    venv_str = sys.argv[3]
    asyncio.run(start_worker(api_key, worker_port, venv_str))

#END OF QUBE
