import os, sys
import json
import ast
import re
import base64
import uuid
import hashlib
import socket
import cloudpickle
import websocket
import subprocess, threading
from random import randint
import pandas as pd
from pathlib import Path
from cryptography.fernet import Fernet
from subprocess import PIPE
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings as conf_settings
from asgiref.sync import sync_to_async
import pytz
UTC = pytz.utc
from spartaqube_app.path_mapper_obf import sparta_2776c51607
from project.models import UserProfile, NewPlotApiVariables, NotebookShared, DashboardShared
from project.sparta_6b7c630ead.sparta_42b75ebdb3 import qube_eeee71e162 as qube_eeee71e162
from project.sparta_6b7c630ead.sparta_c4be29a36f import qube_f591de0f06 as qube_f591de0f06
from project.sparta_6b7c630ead.sparta_1e870ef5c3 import qube_26b766fee5 as qube_26b766fee5
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_538e75a6b0 import convert_to_dataframe, convert_dataframe_to_json, sparta_b58678b446
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_ca8023430e import sparta_b770ba5f34, sparta_bde78f492a
from project.logger_config import logger


def sparta_1e9554111f() ->str:
    """
    Get encryption key to ask to the master node token
    """
    keygen_fernet = 'spartaqube-api-key'
    key = keygen_fernet.encode('utf-8')
    key = hashlib.md5(key).hexdigest()
    key = base64.b64encode(key.encode('utf-8'))
    return key.decode('utf-8')


def sparta_a40ddce0b4() ->str:
    """
    Get encryption key to ask to the master node token
    """
    keygen_fernet = 'spartaqube-internal-decoder-api-key'
    key = keygen_fernet.encode('utf-8')
    key = hashlib.md5(key).hexdigest()
    key = base64.b64encode(key.encode('utf-8'))
    return key.decode('utf-8')


def sparta_2ede186145(f, str_to_encrypt):
    """
    
    """
    data_to_encrypt = str_to_encrypt.encode('utf-8')
    token = f.encrypt(data_to_encrypt).decode('utf-8')
    token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
    return token


def sparta_2baaac8a54(api_token_id):
    """
    This function decode and returns the api 
    """
    if api_token_id == 'public':
        try:
            return User.objects.filter(email='public@spartaqube.com').all()[0]
        except:
            return None
    try:
        f_private = Fernet(sparta_a40ddce0b4().encode('utf-8'))
        api_key = f_private.decrypt(base64.b64decode(api_token_id)).decode(
            'utf-8').split('@')[1]
        user_profile_set = UserProfile.objects.filter(api_key=api_key,
            is_banned=False).all()
        if user_profile_set.count() == 1:
            return user_profile_set[0].user
        return None
    except Exception as e:
        logger.debug('Could not authenticate api with error msg:')
        logger.debug(e)
        return None


def sparta_e00a19a2be(user_obj) ->str:
    """
    Returns the api_token
    """
    userprofile_obj = UserProfile.objects.get(user=user_obj)
    api_key = userprofile_obj.api_key
    if api_key is None:
        api_key = str(uuid.uuid4())
        userprofile_obj.api_key = api_key
        userprofile_obj.save()
    return api_key


async def get_api_key_async_DEPREC(user_obj) ->str:
    """
    Returns the api_token
    """
    userprofile_obj = await UserProfile.objects.aget(user=user_obj)
    api_key = userprofile_obj.api_key
    if api_key is None:
        api_key = str(uuid.uuid4())
        userprofile_obj.api_key = api_key
        await userprofile_obj.asave()
    return api_key


async def get_api_key_async(user_obj) ->str:
    """
    Returns the api_token
    """
    userprofile_obj = await sync_to_async(lambda : UserProfile.objects.get(
        user=user_obj), thread_sensitive=False)()
    if userprofile_obj.api_key is None:
        userprofile_obj.api_key = str(uuid.uuid4())
        await sync_to_async(userprofile_obj.save, thread_sensitive=False)()
    return userprofile_obj.api_key


def sparta_8a1fb63372(user_obj, domain_name) ->str:
    """
    Returns the public api token (to pass in the Spartaqube api function)
    """
    api_key = sparta_e00a19a2be(user_obj)
    random_nb = str(randint(0, 1000))
    data_to_encrypt = f'apikey@{api_key}@{random_nb}'
    f_private = Fernet(sparta_a40ddce0b4().encode('utf-8'))
    private_encryption = sparta_2ede186145(f_private, data_to_encrypt)
    data_to_encrypt = f'apikey@{domain_name}@{private_encryption}'
    f_public = Fernet(sparta_1e9554111f().encode('utf-8'))
    public_encryption = sparta_2ede186145(f_public, data_to_encrypt)
    return public_encryption


def sparta_a831dcc459(json_data, user_obj) ->dict:
    """
    Get api token
    """
    api_key = sparta_e00a19a2be(user_obj)
    domain_name = json_data['domain']
    public_encryption = sparta_8a1fb63372(user_obj, domain_name)
    return {'res': 1, 'token': public_encryption}


def sparta_9f5aca7291(json_data, user_obj) ->dict:
    """
    Generate new api token
    """
    userprofile_obj = UserProfile.objects.get(user=user_obj)
    api_key = str(uuid.uuid4())
    userprofile_obj.api_key = api_key
    userprofile_obj.save()
    return {'res': 1}


def sparta_fe8360bf4b() ->dict:
    """
    Get list of plot types
    """
    plot_types: list = sparta_b770ba5f34()
    plot_types = sorted(plot_types, key=lambda x: x['Library'].lower(),
        reverse=False)
    return {'res': 1, 'plot_types': plot_types}


def sparta_3b0567d784(json_data) ->dict:
    """
    Get plot type API details (inputs and options)
    """
    logger.debug('DEBUG get_plot_options json_data')
    logger.debug(json_data)
    plot_type = json_data['plot_type']
    plot_input_options_dict = sparta_bde78f492a(plot_type)
    plot_input_options_dict['res'] = 1
    return plot_input_options_dict


def sparta_2e2b2c442f(code):
    tree = ast.parse(code)
    if isinstance(tree.body[-1], ast.Expr):
        last_expr_node = tree.body[-1].value
        last_expr_code = ast.unparse(last_expr_node)
        return last_expr_code
    else:
        return None


def sparta_6a4cc09a0c(json_data, user_obj) ->dict:
    """
    Execute api example user code
    """
    user_code_example = json_data['userCode']
    resp = None
    error_msg = ''
    try:
        logger.debug('EXECUTE API EXAMPLE DEBUG DEBUG DEBUG')
        api_key = sparta_e00a19a2be(user_obj)
        core_api_path = sparta_2776c51607()['project/core/api']
        ini_code = 'import os, sys\n'
        ini_code += f'sys.path.insert(0, r"{str(core_api_path)}")\n'
        ini_code += 'from spartaqube import Spartaqube as Spartaqube\n'
        ini_code += f"Spartaqube('{api_key}')\n"
        user_code_example = ini_code + '\n' + user_code_example
        exec(user_code_example, globals())
        last_expression_str = sparta_2e2b2c442f(user_code_example)
        if last_expression_str is not None:
            last_expression_output = eval(last_expression_str)
            if last_expression_output.__class__.__name__ == 'HTML':
                resp = last_expression_output.data
            else:
                resp = last_expression_output
            resp = json.dumps(resp)
            return {'res': 1, 'resp': resp, 'errorMsg': error_msg}
        return {'res': -1, 'errorMsg':
            'No output to display. You should put the variable to display as the last line of the code'
            }
    except Exception as e:
        return {'res': -1, 'errorMsg': str(e)}


def sparta_cffa3febce(json_data, user_obj) ->dict:
    """
    DEPRECATED
    Returns session variables (sent from the notebook and stored in the model NewPlotApiVariables)
    """
    session_id = json_data['session']
    new_plot_api_variables_set = NewPlotApiVariables.objects.filter(session_id
        =session_id).all()
    logger.debug(f'gui_plot_api_variables with session_id {session_id}')
    logger.debug(new_plot_api_variables_set)
    if new_plot_api_variables_set.count() > 0:
        new_plot_api_variables_obj = new_plot_api_variables_set[0]
        pickled_variables = new_plot_api_variables_obj.pickled_variables
        unpickled_data = cloudpickle.loads(pickled_variables.encode('latin1'))
        notebook_variables = []
        for notebook_variable in unpickled_data:
            notebook_variables_df = convert_to_dataframe(notebook_variable)
            if notebook_variables_df is not None:
                pass
            else:
                notebook_variables_df = pd.DataFrame()
            notebook_variables.append(convert_dataframe_to_json(
                notebook_variables_df))
        logger.debug(notebook_variables)
        return {'res': 1, 'notebook_variables': notebook_variables}
    return {'res': -1}


def sparta_3a3f3f9e4a(json_data, user_obj) ->dict:
    """
    Get template from widget_id to plot data with the correct template
    """
    widget_id = json_data['widgetId']
    return qube_f591de0f06.sparta_3a3f3f9e4a(user_obj, widget_id)


def sparta_1ec144fd55(json_data, user_obj) ->dict:
    """
    Call the appropriate web service
    """
    api_service = json_data['api_service']
    if api_service == 'get_status':
        output = sparta_547c1be9ab()
    elif api_service == 'get_status_ws':
        return sparta_aa843bbf3a()
    elif api_service == 'get_connectors':
        return sparta_cebc06c679(json_data, user_obj)
    elif api_service == 'get_connector_tables':
        return sparta_460652c33a(json_data, user_obj)
    elif api_service == 'get_data_from_connector':
        return sparta_ecfb099284(json_data, user_obj)
    elif api_service == 'get_widgets':
        output = sparta_db75005676(user_obj)
    elif api_service == 'has_widget_id':
        return sparta_e5f6ea73f6(json_data, user_obj)
    elif api_service == 'get_widget_data':
        return sparta_72023528b8(json_data, user_obj)
    elif api_service == 'get_plot_types':
        return sparta_b770ba5f34()
    elif api_service == 'put_df':
        return sparta_14eab753ce(json_data, user_obj)
    elif api_service == 'drop_df':
        return sparta_00cc520003(json_data, user_obj)
    elif api_service == 'drop_dispo_df':
        return sparta_8396ccdcac(json_data, user_obj)
    elif api_service == 'get_available_df':
        return sparta_411311430a(json_data, user_obj)
    elif api_service == 'get_df':
        return sparta_b47f501f17(json_data, user_obj)
    elif api_service == 'has_dataframe_slug':
        return sparta_8b773e1854(json_data, user_obj)
    return {'res': 1, 'output': output}


def sparta_547c1be9ab():
    return 1


def sparta_cebc06c679(json_data, user_obj):
    """
    Return the list of connectors
    """
    keys_to_retain = ['connector_id', 'name', 'db_engine']
    res_dict = qube_f591de0f06.sparta_6f0d9491b6(json_data, user_obj)
    if res_dict['res'] == 1:
        res_dict['db_connectors'] = [{k: d[k] for k in keys_to_retain if k in
            d} for d in res_dict['db_connectors']]
    return res_dict


def sparta_460652c33a(json_data, user_obj):
    """
    Return list of available table
    """
    res_dict = qube_f591de0f06.sparta_7be26e6e4e(json_data, user_obj)
    return res_dict


def sparta_ecfb099284(json_data, user_obj):
    """
    Return preview data from connector
    """
    res_dict = qube_f591de0f06.sparta_6f3b7f8353(json_data, user_obj)
    return res_dict


def sparta_db75005676(user_obj) ->list:
    """
    Return list of widgets
    """
    return qube_f591de0f06.sparta_db3e1a37d5(user_obj)


def sparta_e5f6ea73f6(json_data, user_obj) ->bool:
    """
    Check if widget_id
    """
    return qube_f591de0f06.sparta_a9fb9a422b(json_data, user_obj)


def sparta_72023528b8(json_data, user_obj) ->dict:
    """
    Returns widget raw data
    """
    return qube_f591de0f06.sparta_7f02866b93(json_data, user_obj)


def sparta_14eab753ce(json_data, user_obj) ->dict:
    """
    Insert dataframe
    """
    return qube_26b766fee5.sparta_f82e3ab30c(json_data, user_obj)


def sparta_00cc520003(json_data, user_obj) ->dict:
    """
    Drop dataframe
    """
    return qube_26b766fee5.sparta_a1e2c4b8ab(json_data, user_obj)


def sparta_8396ccdcac(json_data, user_obj) ->dict:
    """
    Drop specific dispo date
    """
    return qube_26b766fee5.sparta_17a70345b4(json_data, user_obj)


def sparta_411311430a(json_data, user_obj) ->dict:
    """
    Get available dataframes
    """
    return qube_26b766fee5.sparta_cb2adf63c0(json_data, user_obj)


def sparta_b47f501f17(json_data, user_obj) ->dict:
    """
    Get dataframe
    """
    return qube_26b766fee5.sparta_d18f1a4b48(json_data, user_obj)


def sparta_8b773e1854(json_data, user_obj) ->dict:
    """
    Get dataframe
    """
    return qube_26b766fee5.sparta_98d6a7675d(json_data, user_obj)


def sparta_b141926eb4(json_data, user_obj) ->dict:
    """
    DEPRECATED -> MOVED TO CACHE
    Send data from the notebook and store it temporarily in the NewPlotApiVariables model
    """
    date_now = datetime.now().astimezone(UTC)
    session_id = str(uuid.uuid4())
    pickled_data = json_data['data']
    NewPlotApiVariables.objects.create(user=user_obj, session_id=session_id,
        pickled_variables=pickled_data, date_created=date_now, last_update=
        date_now)
    return {'res': 1, 'session_id': session_id}


def sparta_3bebc6bc28():
    return sparta_b770ba5f34()


def sparta_77cee9abd8():
    """
    Clear cache plot variables stored in mem 
    """
    cache.clear()
    return {'res': 1}


def sparta_aa843bbf3a() ->dict:
    """
    Check it the websocket connection can be established on the ASGI port
    """
    global is_wss_valid
    is_wss_valid = False
    try:
        api_path = sparta_2776c51607()['api']
        with open(os.path.join(api_path, 'app_data_asgi.json'), 'r'
            ) as json_file:
            loaded_data_dict = json.load(json_file)
        ASGI_PORT = int(loaded_data_dict['default_port'])
    except:
        ASGI_PORT = 5664
    logger.debug('ASGI_PORT')
    logger.debug(ASGI_PORT)

    def on_open(ws):
        global is_wss_valid
        is_wss_valid = True
        ws.close()

    def on_error(ws, error):
        global is_wss_valid
        is_wss_valid = False
        ws.close()

    def on_close(ws, close_status_code, close_msg):
        try:
            logger.debug(
                f'Connection closed with code: {close_status_code}, message: {close_msg}'
                )
            ws.close()
        except Exception as e:
            logger.debug(f'Except: {e}')
    ws = websocket.WebSocketApp(f'ws://127.0.0.1:{ASGI_PORT}/ws/statusWS',
        on_open=on_open, on_close=on_close)
    ws.run_forever()
    if ws.sock and ws.sock.connected:
        logger.debug('WebSocket is still connected. Attempting to close again.'
            )
        ws.close()
    else:
        logger.debug('WebSocket is properly closed.')
    return {'res': 1, 'output': is_wss_valid}


def sparta_5e13e67ede(json_data, user_obj):
    """
    API autocomplete suggestions
    """
    api_methods = [{'name': 'Spartaqube().get_connectors()', 'type': 1,
        'popType': 'dict', 'preview': '', 'other': '', 'popTitle':
        'Get Connectors'}, {'name':
        'Spartaqube().get_connector_tables("connector_id")', 'type': 1,
        'popType': 'dict', 'preview': '', 'other': '', 'popTitle':
        'Get Connector Tables'}, {'name':
        'Spartaqube().get_data_from_connector("connector_id", table=None, sql_query=None, output_format=None)'
        , 'type': 1, 'popType': 'dict', 'preview': '', 'other': '',
        'popTitle': 'Get Connector Data'}, {'name':
        'Spartaqube().get_plot_types()', 'type': 1, 'popType': 'list',
        'preview': '', 'other': '', 'popTitle': 'Get Plot Type'}, {'name':
        'Spartaqube().get_widgets()', 'type': 1, 'popType': 'dict',
        'preview': '', 'other': '', 'popTitle': 'Get Widgets list'}, {
        'name':
        'Spartaqube().iplot([var1, var2], width="100%", height=750)',
        'type': 1, 'popType': 'Plot', 'preview': '', 'other': '-1',
        'popTitle': 'Interactive plot'}, {'name':
        """Spartaqube().plot(
    x:list=None, y:list=None, r:list=None, legend:list=None, labels:list=None, ohlcv:list=None, shaded_background:list=None, 
    datalabels:list=None, border:list=None, background:list=None, border_style:list=None, tooltips_title:list=None, tooltips_label:list=None,
    chart_type="line", interactive=True, widget_id=None, title=None, title_css:dict=None, stacked:bool=False, date_format:str=None, time_range:bool=False,
    gauge:dict=None, gauge_zones:list=None, gauge_zones_labels:list=None, gauge_zones_height:list=None,
    dataframe:pd.DataFrame=None, dates:list=None, returns:list=None, returns_bmk:list=None,
    options:dict=None, width='100%', height=750
)"""
        , 'type': 1, 'popType': 'Plot', 'preview': '', 'other': '-1',
        'displayText': 'Spartaqube().plot(...)', 'popTitle':
        'Programmatic plot'}, {'name': 'Spartaqube().get_available_df()',
        'type': 1, 'popType': 'List', 'preview': '', 'other': '-1',
        'popTitle': 'Get available dataframes'}, {'name':
        'Spartaqube().get_df(table_name, dispo=None, slug=None)', 'type': 1,
        'popType': 'pd.DataFrame', 'preview': '', 'other': '-1', 'popTitle':
        'Get dataframe'}, {'name':
        'Spartaqube().put_df(df:pd.DataFrame, table_name:str, dispo=None, mode="append")'
        , 'type': 1, 'popType': 'dict', 'preview': '', 'other': '-1',
        'popTitle': 'Insert a dataframe'}, {'name':
        'Spartaqube().drop_df(table_name, slug=None)', 'type': 1, 'popType':
        'dict', 'preview': '', 'other': '-1', 'popTitle': 'Drop dataframe'},
        {'name': 'Spartaqube().drop_df_by_id(id=id)', 'type': 1, 'popType':
        'dict', 'preview': '', 'other': '-1', 'popTitle':
        'Drop dataframe (by id)'}, {'name':
        'Spartaqube().drop_dispo_df(table_name, dispo, slug=None)', 'type':
        1, 'popType': 'dict', 'preview': '', 'other': '-1', 'popTitle':
        'Drop dataframe for dispo date'}]
    api_widgets_suggestions = []
    if not user_obj.is_anonymous:
        api_get_widgets = sparta_db75005676(user_obj)
        for widget_dict in api_get_widgets:
            widget_id_with_quote = "'" + str(widget_dict['id']) + "'"
            widget_cmd = f'Spartaqube().get_widget({widget_id_with_quote})'
            api_widgets_suggestions.append({'name': widget_cmd,
                'displayText': widget_dict['name'], 'popTitle': widget_dict
                ['name'], 'type': 2, 'popType': 'Widget', 'preview':
                widget_cmd, 'other': widget_dict['id']})
    autocomplete_suggestions_arr = api_methods + api_widgets_suggestions
    return {'res': 1, 'suggestions': autocomplete_suggestions_arr}


def sparta_91e532a07f(notebook_id):
    """
    Returns owner of notebook by notebook_id (in order to log the kernel with that user for exec mode)
    """
    notebook_shared_set = NotebookShared.objects.filter(is_delete=0,
        notebook__is_delete=0, notebook__notebook_id=notebook_id)
    if notebook_shared_set.count() > 0:
        return notebook_shared_set[0].user
    return None


def sparta_3f45882936(dashboard_id):
    """
    Returns owner of dashboard by dashboard_id (in order to log the kernel with that user for exec mode)
    """
    dashboard_shared_set = DashboardShared.objects.filter(is_delete=0,
        dashboard__is_delete=0, dashboard__dashboard_id=dashboard_id)
    if dashboard_shared_set.count() > 0:
        return dashboard_shared_set[0].user
    return None

#END OF QUBE
