import re
import os
import json
import math
import io, sys
import base64
import pickle
import asyncio
import subprocess
import traceback
import tinykernel
import cloudpickle
import uuid
import pandas as pd
from subprocess import PIPE
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime, timedelta
from pathlib import Path
import pytz
UTC = pytz.utc
from spartaqube_app.path_mapper_obf import sparta_2776c51607
from project.models_spartaqube import DBConnector, DBConnectorUserShared, PlotDBChart, PlotDBChartShared, PlotDBPermission, CodeEditorNotebook, NewPlotApiVariables
from project.models import ShareRights, UserProfile
from project.sparta_6b7c630ead.sparta_42b75ebdb3 import qube_eeee71e162 as qube_eeee71e162
from project.sparta_6b7c630ead.sparta_e12a2379ef import qube_8f7cdd24f3
from project.sparta_6b7c630ead.sparta_c4be29a36f import qube_5ea9d265a5 as qube_5ea9d265a5
from project.sparta_6b7c630ead.sparta_1e870ef5c3 import qube_26b766fee5 as qube_26b766fee5
from project.sparta_6b7c630ead.sparta_e12a2379ef.qube_5414460aa1 import Connector as Connector
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_538e75a6b0 import convert_to_dataframe, convert_dataframe_to_json, sparta_b58678b446, process_dataframe_components
from project.sparta_6b7c630ead.sparta_5e49ed59d5.qube_3583d7aa1d import sparta_7d2b403019
from project.logger_config import logger
INPUTS_KEYS = ['xAxisArr', 'yAxisArr', 'labelsArr', 'radiusBubbleArr',
    'rangesAxisArr', 'measuresAxisArr', 'markersAxisArr', 'ohlcvArr',
    'shadedBackgroundArr']


def sparta_a92982e325(user_obj):
    from project.sparta_6b7c630ead.sparta_e2518651f2.qube_be904e792d import sparta_e00a19a2be
    return sparta_e00a19a2be(user_obj)


def sparta_673391f9b6(user_obj) ->list:
    """
    
    """
    user_group_set = qube_eeee71e162.sparta_325a9ff1bc(user_obj)
    if len(user_group_set) > 0:
        user_groups = [this_obj.user_group for this_obj in user_group_set]
    else:
        user_groups = []
    return user_groups


def sparta_6f0d9491b6(json_data, user_obj) ->dict:
    """
    
    """
    user_groups = sparta_673391f9b6(user_obj)
    if len(user_groups) > 0:
        db_connector_user_shared_set = DBConnectorUserShared.objects.filter(
            Q(is_delete=0, user_group__in=user_groups,
            db_connector__is_delete=0) | Q(is_delete=0, user=user_obj,
            db_connector__is_delete=0))
    else:
        db_connector_user_shared_set = DBConnectorUserShared.objects.filter(
            is_delete=0, user=user_obj, db_connector__is_delete=0)
    db_connector_list = []
    if db_connector_user_shared_set.count() > 0:
        order_by_text = json_data.get('orderBy', 'Recently used')
        if order_by_text == 'Recently used':
            db_connector_user_shared_set = (db_connector_user_shared_set.order_by('-db_connector__last_date_used'))
        elif order_by_text == 'Date desc':
            db_connector_user_shared_set = (db_connector_user_shared_set.order_by('-db_connector__last_update'))
        elif order_by_text == 'Date asc':
            db_connector_user_shared_set = (db_connector_user_shared_set.order_by('db_connector__last_update'))
        elif order_by_text == 'Name desc':
            db_connector_user_shared_set = (db_connector_user_shared_set.order_by('-db_connector__name'))
        elif order_by_text == 'Name asc':
            db_connector_user_shared_set = (db_connector_user_shared_set.order_by('db_connector__name'))
        elif order_by_text == 'Type':
            db_connector_user_shared_set = (db_connector_user_shared_set.order_by('db_connector__db_engine'))
        for db_connector_user_shared_obj in db_connector_user_shared_set:
            db_connector_obj = db_connector_user_shared_obj.db_connector
            dynamic_inputs = []
            try:
                dynamic_inputs = json.loads(db_connector_obj.dynamic_inputs)
            except:
                pass
            db_connector_list.append({'connector_id': db_connector_obj.connector_id, 'host': db_connector_obj.host, 'port':
                db_connector_obj.port, 'user': db_connector_obj.user,
                'database': db_connector_obj.database, 'driver':
                db_connector_obj.driver, 'oracle_service_name':
                db_connector_obj.oracle_service_name, 'keyspace':
                db_connector_obj.keyspace, 'library_arctic':
                db_connector_obj.library_arctic, 'database_path':
                db_connector_obj.database_path, 'csv_path':
                db_connector_obj.csv_path, 'csv_delimiter':
                db_connector_obj.csv_delimiter, 'read_only':
                db_connector_obj.read_only, 'json_url': db_connector_obj.json_url, 'socket_url': db_connector_obj.socket_url,
                'redis_db': db_connector_obj.redis_db, 'dynamic_inputs':
                dynamic_inputs, 'py_code_processing': db_connector_obj.py_code_processing, 'db_engine': db_connector_obj.db_engine,
                'name': db_connector_obj.name, 'description':
                db_connector_obj.description, 'is_owner':
                db_connector_user_shared_obj.is_owner})
    return {'res': 1, 'db_connectors': db_connector_list}


def sparta_c79bcbb4f3() ->dict:
    """
    Returns the list of available db connectors
    """
    return {'res': 1, 'available_engines': qube_8f7cdd24f3.sparta_c79bcbb4f3()}


def sparta_e3f52af9fa(json_data, user_obj):
    """
    Store date last open connector
    """
    connector_id = json_data['connector_id']
    db_connector_set = DBConnector.objects.filter(connector_id=connector_id,
        is_delete=False).all()
    if db_connector_set.count() > 0:
        db_connector_obj = db_connector_set[db_connector_set.count() - 1]
        date_now = datetime.now().astimezone(UTC)
        db_connector_obj.last_date_used = date_now
        db_connector_obj.save()
    return {'res': 1}


def sparta_21c8092fd3(json_data) ->dict:
    """
    Test connector
    """
    errorMsg = ''
    connector_obj = Connector(db_engine=json_data['db_engine'])
    connector_obj.init_with_params(host=json_data['host'], port=json_data[
        'port'], user=json_data['user'], password=json_data['password'],
        database=json_data['database'], oracle_service_name=json_data[
        'oracle_service_name'], csv_path=json_data['csv_path'],
        csv_delimiter=json_data['csv_delimiter'], keyspace=json_data[
        'keyspace'], library_arctic=json_data['library_arctic'],
        database_path=json_data['database_path'], read_only=json_data[
        'read_only'], json_url=json_data['json_url'], socket_url=json_data[
        'socket_url'], redis_db=json_data.get('redis_db', None), token=
        json_data.get('token', None), organization=json_data.get(
        'organization', None), lib_dir=json_data.get('lib_dir', None),
        driver=json_data.get('driver', None), trusted_connection=json_data.get('trusted_connection', None), dynamic_inputs=json_data[
        'dynamic_inputs'], py_code_processing=json_data['py_code_processing'])
    is_connector_working = connector_obj.test_connection()
    if not is_connector_working:
        errorMsg = connector_obj.get_error_msg_test_connection()
    return {'res': 1, 'is_connector_working': is_connector_working,
        'errorMsg': errorMsg}


def sparta_1a39f76d64(json_data) ->dict:
    """
    Preview connector
    """
    res = 1
    errorMsg = ''
    print_buffer_content = ''
    output_content = None
    try:
        connector_obj = Connector(db_engine=json_data['db_engine'])
        connector_obj.init_with_params(host=json_data['host'], port=
            json_data['port'], user=json_data['user'], password=json_data[
            'password'], database=json_data['database'],
            oracle_service_name=json_data['oracle_service_name'], csv_path=
            json_data['csv_path'], csv_delimiter=json_data['csv_delimiter'],
            keyspace=json_data['keyspace'], library_arctic=json_data[
            'library_arctic'], database_path=json_data['database_path'],
            read_only=json_data['read_only'], json_url=json_data['json_url'
            ], socket_url=json_data['socket_url'], redis_db=json_data[
            'redis_db'], token=json_data.get('token', ''), organization=
            json_data.get('organization', ''), lib_dir=json_data.get(
            'lib_dir', ''), driver=json_data.get('driver', ''),
            trusted_connection=json_data.get('trusted_connection', True),
            dynamic_inputs=json_data['dynamic_inputs'], py_code_processing=
            json_data['py_code_processing'])
        preview_results, print_buffer_content = (connector_obj.preview_output_connector_bowler())
        stdout_buffer = io.StringIO()
        sys.stdout = stdout_buffer
        print(preview_results)
        output_content = stdout_buffer.getvalue()
        sys.stdout = sys.__stdout__
    except Exception as e:
        errorMsg = str(e)
        res = -1
    return {'res': res, 'preview_json': output_content,
        'print_buffer_content': print_buffer_content, 'errorMsg': errorMsg}


def sparta_b7032204e8(json_data, user_obj) ->dict:
    """
    
    """
    date_now = datetime.now().astimezone(UTC)
    connector_id = str(uuid.uuid4())
    db_connector_obj = DBConnector.objects.create(connector_id=connector_id,
        host=json_data['host'], port=json_data['port'], user=json_data[
        'user'], password_e=qube_8f7cdd24f3.sparta_3db41930e6(json_data[
        'password']), database=json_data['database'], oracle_service_name=
        json_data['oracle_service_name'], keyspace=json_data['keyspace'],
        library_arctic=json_data['library_arctic'], database_path=json_data
        ['database_path'], csv_path=json_data['csv_path'], csv_delimiter=
        json_data['csv_delimiter'], read_only=json_data['read_only'],
        json_url=json_data['json_url'], socket_url=json_data['socket_url'],
        redis_db=json_data['redis_db'], token=json_data['token'],
        organization=json_data['organization'], lib_dir=json_data['lib_dir'
        ], driver=json_data['driver'], trusted_connection=json_data[
        'trusted_connection'], dynamic_inputs=json.dumps(json_data[
        'dynamic_inputs']), py_code_processing=json_data[
        'py_code_processing'], db_engine=json_data['db_engine'], name=
        json_data['name'], description=json_data['description'],
        date_created=date_now, last_update=date_now, last_date_used=date_now)
    share_rights_obj = ShareRights.objects.create(is_admin=True,
        has_write_rights=True, has_reshare_rights=True, last_update=date_now)
    DBConnectorUserShared.objects.create(db_connector=db_connector_obj,
        user=user_obj, date_created=date_now, share_rights=share_rights_obj,
        is_owner=True)
    return {'res': 1}


def sparta_2a1f37c5e8(json_data, user_obj) ->dict:
    """
    Update a connector
    """
    logger.debug('update connector')
    logger.debug(json_data)
    connector_id = json_data['connector_id']
    db_connector_set = DBConnector.objects.filter(connector_id=connector_id,
        is_delete=False).all()
    if db_connector_set.count() > 0:
        db_connector_obj = db_connector_set[db_connector_set.count() - 1]
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            db_connector_user_shared_set = (DBConnectorUserShared.objects.filter(Q(is_delete=0, user_group__in=user_groups,
                db_connector__is_delete=0, db_connector=db_connector_obj) |
                Q(is_delete=0, user=user_obj, db_connector__is_delete=0,
                db_connector=db_connector_obj)))
        else:
            db_connector_user_shared_set = (DBConnectorUserShared.objects.filter(is_delete=0, user=user_obj, db_connector__is_delete=
                0, db_connector=db_connector_obj))
        if db_connector_user_shared_set.count() > 0:
            db_connector_user_shared_obj = db_connector_user_shared_set[0]
            share_rights_obj = db_connector_user_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                date_now = datetime.now().astimezone(UTC)
                db_connector_obj.host = json_data['host']
                db_connector_obj.port = json_data['port']
                db_connector_obj.user = json_data['user']
                db_connector_obj.password_e = (qube_8f7cdd24f3.sparta_3db41930e6(json_data['password']))
                db_connector_obj.database = json_data['database']
                db_connector_obj.oracle_service_name = json_data[
                    'oracle_service_name']
                db_connector_obj.keyspace = json_data['keyspace']
                db_connector_obj.library_arctic = json_data['library_arctic']
                db_connector_obj.database_path = json_data['database_path']
                db_connector_obj.csv_path = json_data['csv_path']
                db_connector_obj.csv_delimiter = json_data['csv_delimiter']
                db_connector_obj.read_only = json_data['read_only']
                db_connector_obj.json_url = json_data['json_url']
                db_connector_obj.socket_url = json_data['socket_url']
                db_connector_obj.redis_db = json_data['redis_db']
                db_connector_obj.token = json_data.get('token', '')
                db_connector_obj.organization = json_data.get('organization',
                    '')
                db_connector_obj.lib_dir = json_data.get('lib_dir', '')
                db_connector_obj.driver = json_data.get('driver', '')
                db_connector_obj.trusted_connection = json_data.get(
                    'trusted_connection', True)
                db_connector_obj.dynamic_inputs = json.dumps(json_data[
                    'dynamic_inputs'])
                db_connector_obj.py_code_processing = json_data[
                    'py_code_processing']
                db_connector_obj.db_engine = json_data['db_engine']
                db_connector_obj.name = json_data['name']
                db_connector_obj.description = json_data['description']
                db_connector_obj.last_update = date_now
                db_connector_obj.last_date_used = date_now
                db_connector_obj.save()
    return {'res': 1}


def sparta_fe7ce3ad7e(json_data, user_obj) ->dict:
    """
    Delete a connector
    """
    connector_id = json_data['connector_id']
    db_connector_set = DBConnector.objects.filter(connector_id=connector_id,
        is_delete=False).all()
    if db_connector_set.count() > 0:
        db_connector_obj = db_connector_set[db_connector_set.count() - 1]
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            db_connector_user_shared_set = (DBConnectorUserShared.objects.filter(Q(is_delete=0, user_group__in=user_groups,
                db_connector__is_delete=0, db_connector=db_connector_obj) |
                Q(is_delete=0, user=user_obj, db_connector__is_delete=0,
                db_connector=db_connector_obj)))
        else:
            db_connector_user_shared_set = (DBConnectorUserShared.objects.filter(is_delete=0, user=user_obj, db_connector__is_delete=
                0, db_connector=db_connector_obj))
        if db_connector_user_shared_set.count() > 0:
            db_connector_user_shared_obj = db_connector_user_shared_set[0]
            share_rights_obj = db_connector_user_shared_obj.share_rights
            if share_rights_obj.is_admin:
                db_connector_obj.is_delete = True
                db_connector_obj.save()
    return {'res': 1}


def sparta_2f23cdc4fb(package_name):
    """ Installs a package within the current virtual environment """
    process = subprocess.Popen([sys.executable, '-m', 'pip', 'install',
        package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text
        =True)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        return {'success': True, 'output': stdout}
    else:
        return {'success': False, 'error': stderr}


def sparta_56b09b5a01(json_data, user_obj) ->dict:
    """
    Pip install connector
    """
    has_error = False
    errors = []
    pip_cmds: list = json_data['pip_cmds']
    for cmd in pip_cmds:
        result = sparta_2f23cdc4fb(cmd)
        if result['success']:
            logger.debug('Installation succeeded:', result['output'])
        else:
            logger.debug('Installation failed:', result['error'])
            has_error = True
            errors.append(result['error'])
    return {'res': 1, 'has_error': has_error, 'errors': errors}


def sparta_6a9452af0d(connector_id, user_obj):
    """
    This function returns the DBConnector model
    """
    db_connector_set = DBConnector.objects.filter(connector_id__startswith=
        connector_id, is_delete=False).all()
    if db_connector_set.count() == 1:
        db_connector_obj = db_connector_set[0]
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            db_connector_user_shared_set = (DBConnectorUserShared.objects.filter(Q(is_delete=0, user_group__in=user_groups,
                db_connector__is_delete=0, db_connector=db_connector_obj) |
                Q(is_delete=0, user=user_obj, db_connector__is_delete=0,
                db_connector=db_connector_obj)))
        else:
            db_connector_user_shared_set = (DBConnectorUserShared.objects.filter(is_delete=0, user=user_obj, db_connector__is_delete=
                0, db_connector=db_connector_obj))
        if db_connector_user_shared_set.count() > 0:
            return db_connector_obj


class DotDict(dict):
    """
    A dictionary subclass that supports attribute-style access.If an attribute is not present, it returns None by default."""

    def __getattr__(self, name):
        return self.get(name, None)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]


def sparta_18191d36c9(obj):
    """
    Recursively convert all dictionaries in `obj` to DotDict."""
    if isinstance(obj, dict):
        new_dotdict = DotDict()
        for key, value in obj.items():
            new_dotdict[key] = sparta_18191d36c9(value)
        return new_dotdict
    elif isinstance(obj, list):
        return [sparta_18191d36c9(item) for item in obj]
    else:
        return obj


def sparta_7be26e6e4e(json_data, user_obj) ->dict:
    """
    Load tables explorer
    """
    is_create_connector = json_data.get('is_create_connector', False)
    if is_create_connector:
        db_connector_obj = sparta_18191d36c9(json_data)
    else:
        connector_id = json_data['connector_id']
        db_connector_obj = sparta_6a9452af0d(connector_id, user_obj)
        if db_connector_obj is None:
            return {'res': -1, 'errorMsg':
                'You do not have the rights to access this connector'}
    connector_obj = Connector(db_engine=db_connector_obj.db_engine)
    connector_obj.init_with_model(db_connector_obj)
    tables_explorer_list = connector_obj.get_available_tables()
    views_explorer_list = connector_obj.get_available_views()
    return {'res': 1, 'tables_explorer': tables_explorer_list,
        'views_explorer': views_explorer_list}


def sparta_9e304acc9b(json_data, user_obj) ->dict:
    """
    Load all columns and types for a specific table
    """
    connector_id = json_data['connector_id']
    table_name = json_data['table_name']
    b_apply_filter = int(json_data.get('bApplyFilter', '0')) == 1
    column_info_list = []
    db_connector_obj = sparta_6a9452af0d(connector_id, user_obj)
    if db_connector_obj is None:
        return {'res': -1, 'errorMsg':
            'You do not have the rights to access this connector'}
    connector_obj = Connector(db_engine=db_connector_obj.db_engine)
    connector_obj.init_with_model(db_connector_obj)
    if b_apply_filter:
        sql_query = json_data['query_filter']
        try:
            data_table_df: pd.DataFrame = connector_obj.get_data_table_query(
                sql_query, table_name)
        except Exception as e:
            logger.debug(traceback.format_exc())
            return {'res': -1, 'errorMsg': str(e)}
        table_columns = list(table_columns.columns)
        for column_name, column_type in zip(data_table_df.columns,
            data_table_df.dtypes):
            column_info = {'name': column_name, 'type': str(column_type)}
            column_info_list.append(column_info)
    else:
        column_info_list = connector_obj.get_table_columns(table_name)
    return {'res': 1, 'table_columns': column_info_list}


def sparta_5717c7d91b(json_data, db_connector_obj):
    """
    This objective of this function is to override dynamic inputs (defined by the user)
    """
    if db_connector_obj.db_engine is not None:
        if db_connector_obj.db_engine in ['json_api', 'python', 'wss_api']:
            db_dynamic_inputs = db_connector_obj.dynamic_inputs
            if db_dynamic_inputs is not None:
                try:
                    db_dynamic_inputs = json.loads(db_dynamic_inputs)
                except:
                    db_dynamic_inputs = []
            user_dynamic_inputs = json_data.get('dynamic_inputs', [])
            db_dynamic_inputs_name_list = [elem['input'] for elem in
                db_dynamic_inputs]
            for input_dict in db_dynamic_inputs:
                if input_dict['input'] not in db_dynamic_inputs_name_list:
                    user_dynamic_inputs.append(input_dict)
            db_connector_obj.dynamic_inputs = json.dumps(user_dynamic_inputs)


def sparta_6f3b7f8353(json_data, user_obj) ->dict:
    """
    Load data (preview)
    """
    print('json_data load_table_preview_explorer')
    print(json_data)
    db_engine = json_data['db_engine']
    print('db_engine >> ' + str(db_engine))
    if db_engine == 'spartaqube-data-store':
        json_data['slug'] = json_data['connector_id']
        json_data['table_name'] = json_data['connector_name']
        if json_data.get('bApplyFilter', False):
            json_data['dispo'] = sparta_afa62d9c58(json_data['query_filter'])
        res_dict = qube_26b766fee5.sparta_d18f1a4b48(json_data, user_obj)
        if res_dict['res'] == 1:
            try:
                if res_dict['is_encoded_blob']:
                    data_list = pickle.loads(base64.b64decode(res_dict[
                        'encoded_blob'].encode('utf-8')))
                    data_df_list = [pickle.loads(elem_dict['df_blob']).assign(dispo=elem_dict['dispo']) for elem_dict in
                        data_list]
                    data_table_df = pd.concat(data_df_list)
                    df_all = df_all.sort_index(ascending=False)
                    data_table_df.sort_values(by='dispo', inplace=True)
                else:
                    data_table_df = res_dict['data_preview_df']
                return {'res': 1, 'data': convert_dataframe_to_json(
                    data_table_df)}
            except Exception as e:
                print('Error load dataframe')
                print(e)
        return {'res': -1, 'errorMsg': 'Error loading this dataframe...'}
    if db_engine == 'clipboard_paste':
        data_dict = json.loads(json_data['data'])
        data_table_df = pd.DataFrame(data_dict['data'], columns=data_dict[
            'columns'], index=data_dict['index'])
        return {'res': 1, 'data': convert_dataframe_to_json(data_table_df)}
    connector_id = json_data['connector_id']
    is_create_connector = json_data.get('is_create_connector', False)
    table_name = json_data.get('table_name', None)
    b_apply_filter = int(json_data.get('bApplyFilter', '0')) == 1
    b_top_100 = int(json_data.get('previewTopMod', '0')) == 0
    if is_create_connector:
        db_connector_obj = sparta_18191d36c9(json_data)
    else:
        db_connector_obj = sparta_6a9452af0d(connector_id, user_obj)
        if db_connector_obj is None:
            return {'res': -1, 'errorMsg':
                'You do not have the rights to access this connector'}
    sparta_5717c7d91b(json_data, db_connector_obj)
    connector_obj = Connector(db_engine=db_connector_obj.db_engine)
    connector_obj.init_with_model(db_connector_obj)
    if b_apply_filter is not None:
        if b_apply_filter:
            sql_query = json_data['query_filter']
            try:
                data_table_df: pd.DataFrame = (connector_obj.get_data_table_query(sql_query, table_name))
            except Exception as e:
                logger.debug(traceback.format_exc())
                return {'res': -1, 'errorMsg': str(e)}
        elif b_top_100:
            data_table_df: pd.DataFrame = connector_obj.get_data_table_top(
                table_name)
        else:
            data_table_df: pd.DataFrame = connector_obj.get_data_table(
                table_name)
    elif b_top_100:
        data_table_df: pd.DataFrame = connector_obj.get_data_table_top(
            table_name)
    else:
        data_table_df: pd.DataFrame = connector_obj.get_data_table(table_name)
    return {'res': 1, 'data': convert_dataframe_to_json(data_table_df)}


def sparta_6cd0478f9a(json_data, user_obj) ->dict:
    """
    Load spartaqube dataframes explorer (Available dataframes list)
    """
    available_df_dict = qube_26b766fee5.sparta_cb2adf63c0({}, user_obj)
    dataframes_explorer = []
    if available_df_dict['res'] == 1:
        dataframes_explorer = available_df_dict['available_df']
    return {'res': 1, 'dataframes_explorer': dataframes_explorer,
        'dataframes_explorer_name': [elem['name'] for elem in
        dataframes_explorer]}


def sparta_b8a3e2ba47(json_data, user_obj) ->dict:
    """
    Load spartaqube data store explorer preview
    """
    print('load_spartaqube_data_store_preview_explorer json_data')
    print(json_data)
    if json_data.get('password', None) is not None:
        res_dict = qube_26b766fee5.sparta_7c5d16bd4f(json_data, user_obj)
    else:
        json_data['table_name'] = json_data.get('name', None)
        res_dict = qube_26b766fee5.sparta_d18f1a4b48(json_data, user_obj)
    if res_dict['res'] == 1:
        dataframe_model_obj = qube_26b766fee5.sparta_7ea285c282(json_data,
            user_obj)
        config_dataframe = dict()
        plot_chart_id = '-1'
        data_source_list = None
        chart_params = None
        chart_config = None
        if dataframe_model_obj is not None:
            config_dataframe = dataframe_model_obj.dataframe_config
            plot_db_chart_obj = dataframe_model_obj.plot_db_chart
            if plot_db_chart_obj is not None:
                plot_chart_id = plot_db_chart_obj.plot_chart_id
                data_source_list = plot_db_chart_obj.data_source_list,
                chart_params = plot_db_chart_obj.chart_params,
                chart_config = plot_db_chart_obj.chart_config,
        if res_dict['is_dataframe_connector']:
            df_all = res_dict['data_preview_df']
            dispo = datetime.now().strftime('%Y-%m-%d')
            df_all['dispo'] = dispo
            dataframe_model_name = res_dict['dataframe_model_name']
            df_all = process_dataframe_components(df_all)
            return {'res': 1, 'name': dataframe_model_name, 'data':
                convert_dataframe_to_json(df_all), 'dispos': [dispo],
                'config': config_dataframe, 'plot_chart_id': plot_chart_id,
                'data_source_list': data_source_list, 'chart_params':
                chart_params, 'chart_config': chart_config}
        else:
            try:
                dataframe_model_name = res_dict['dataframe_model_name']
                data_list = pickle.loads(base64.b64decode(res_dict[
                    'encoded_blob'].encode('utf-8')))
                data_df_list = [pickle.loads(elem_dict['df_blob']).assign(
                    dispo=elem_dict['dispo']) for elem_dict in data_list]
                available_dispos = sorted(list(set([str(elem_dict['dispo']) for
                    elem_dict in data_list])))
                try:
                    df_all = pd.concat(data_df_list)
                    df_all = process_dataframe_components(df_all)
                    return {'res': 1, 'name': dataframe_model_name, 'data':
                        convert_dataframe_to_json(df_all), 'dispos':
                        available_dispos, 'config': config_dataframe,
                        'plot_chart_id': plot_chart_id, 'data_source_list':
                        data_source_list, 'chart_params': chart_params,
                        'chart_config': chart_config}
                except Exception as e:
                    return {'res': -1, 'errorMsg': str(e), 'bRequireDispo':
                        1, 'dispos': available_dispos}
            except Exception as e:
                print('Except')
                print(e)
                return {'res': -1, 'errorMsg': str(e)}
    if res_dict['res'] == 3:
        import time
        time.sleep(2)
        return {'res': -1, 'password': 'Invalid password', 'errorMsg':
            'Invalid password'}
    return {'res': -1, 'errorMsg':
        'Could not retrieve the dataframe, make sure you have the appropriate rights and try again'
        }


def sparta_afa62d9c58(dispo) ->str:
    dispo_blob = pickle.dumps(dispo)
    return base64.b64encode(dispo_blob).decode('utf-8')


def sparta_88454154a1(json_data, user_obj
    ) ->dict:
    """
    Load spartaqube data store explorer preview for a specific dispo date
    """
    print('load_spartaqube_data_store_preview_explorer json_data 123')
    print(json_data)
    json_data['dispo'] = sparta_afa62d9c58(json_data['dispo'])
    if json_data.get('password', None) is not None:
        res_dict = qube_26b766fee5.sparta_7c5d16bd4f(json_data, user_obj)
    else:
        json_data['table_name'] = json_data.get('name', None)
        res_dict = qube_26b766fee5.sparta_d18f1a4b48(json_data, user_obj)
    if res_dict['res'] == 1:
        try:
            if res_dict['is_dataframe_connector']:
                df_all = res_dict['data_preview_df']
                dispo = datetime.now().strftime('%Y-%m-%d')
                df_all['dispo'] = dispo
                df_all = process_dataframe_components(df_all)
                return {'res': 1, 'data': convert_dataframe_to_json(df_all)}
            else:
                data_list = pickle.loads(base64.b64decode(res_dict[
                    'encoded_blob'].encode('utf-8')))
                data_df_list = [pickle.loads(elem_dict['df_blob']).assign(
                    dispo=elem_dict['dispo']) for elem_dict in data_list]
                try:
                    df_all = pd.concat(data_df_list, ignore_index=True)
                    df_all = df_all.sort_index(ascending=False)
                    return {'res': 1, 'data': convert_dataframe_to_json(df_all)
                        }
                except Exception as e:
                    return {'res': -1, 'errorMsg': str(e)}
        except Exception as e:
            return {'res': -1, 'errorMsg': str(e)}
    return {'res': -1, 'errorMsg':
        'Could not retrieve the dataframe, make sure you have the appropriate rights and try again'
        }


def sparta_1754a195fc(json_data, user_obj) ->dict:
    """
    
    """
    connector_id = json_data['connector_id']
    table_name = json_data.get('table_name', '')
    b_apply_filter = int(json_data.get('bApplyFilter', '0')) == 1
    db_engine = json_data.get('db_engine', None)
    db_connector_obj = sparta_6a9452af0d(connector_id, user_obj)
    if db_connector_obj is None:
        return {'res': -1, 'errorMsg':
            'You do not have the rights to access this connector'}
    sparta_5717c7d91b(json_data, db_connector_obj)
    connector_obj = Connector(db_engine=db_connector_obj.db_engine)
    connector_obj.init_with_model(db_connector_obj)
    if b_apply_filter:
        sql_query = json_data['query_filter']
        try:
            data_table_df: pd.DataFrame = connector_obj.get_data_table_query(
                sql_query, table_name)
        except Exception as e:
            logger.debug(traceback.format_exc())
            return {'res': -1, 'errorMsg': str(e)}
    else:
        data_table_df: pd.DataFrame = connector_obj.get_data_table(table_name)
    data_table_stats_df = data_table_df.describe()
    return {'res': 1, 'data': data_table_stats_df.to_json(orient='split')}


def sparta_f04f3dd2bc(json_data, user_obj) ->dict:
    """
    Compute infos and statistics from data source data explorer
    """

    def get_dataframe_info(df):
        """

        """
        return pd.DataFrame({'name': df.columns, 'non-nulls': len(df) - df.isnull().sum().values, 'nulls': df.isnull().sum().values,
            'type': df.dtypes.values})
    data_dict = json.loads(json_data['data'])
    mode_ = int(json_data['mode'])
    columns_raw = data_dict['columns']
    if isinstance(columns_raw[0], list) or isinstance(columns_raw[0], tuple):
        columns = [tuple(col) for col in columns_raw]
        data_df = pd.DataFrame(data=data_dict['data'], columns=pd.MultiIndex.from_tuples(columns), index=data_dict['index'])
    else:
        data_df = pd.DataFrame(data=data_dict['data'], columns=columns_raw,
            index=data_dict['index'])
    table = ''
    if mode_ == 1:
        infos_df = get_dataframe_info(data_df)
        table = infos_df.to_html()
    else:
        descriptions_df = data_df.describe()
        table = descriptions_df.to_html()
    return {'res': 1, 'table': table}


def sparta_c4be3a8ceb(json_data, user_obj) ->dict:
    """
    
    """
    connector_id = json_data['connector_id']
    table_name = json_data.get('table_name', None)
    b_apply_filter = int(json_data.get('bApplyFilter', '0')) == 1
    db_connector_obj = sparta_6a9452af0d(connector_id, user_obj)
    if db_connector_obj is None:
        return {'res': -1, 'errorMsg':
            'You do not have the rights to access this connector'}
    sparta_5717c7d91b(json_data, db_connector_obj)
    connector_obj = Connector(db_engine=db_connector_obj.db_engine)
    connector_obj.init_with_model(db_connector_obj)
    wss_structure_df: pd.DataFrame = connector_obj.get_db_connector(
        ).get_wss_structure()
    return {'res': 1, 'data': convert_dataframe_to_json(wss_structure_df)}


def sparta_06d06b0c5a(json_data, user_obj, b_return_model=False) ->dict:
    """
    Save plot
    """
    print('save_plot')
    has_widget_password = json_data['bWidgetPassword']
    widget_password = None
    if has_widget_password:
        widget_password = json_data['widgetPassword']
        widget_password = qube_5ea9d265a5.sparta_4a523d889a(
            widget_password)
    code_editor_notebook_cells: str = json_data['codeEditorNotebookCells']
    notebook_id = str(uuid.uuid4())
    date_now = datetime.now().astimezone(UTC)
    code_editor_notebook_obj = CodeEditorNotebook.objects.create(notebook_id
        =notebook_id, cells=code_editor_notebook_cells, date_created=
        date_now, last_update=date_now)
    plot_chart_id = str(uuid.uuid4())
    is_static_data = json_data['bStaticDataPlot']
    is_gui_plot = json_data['is_gui_plot']
    if is_gui_plot:
        is_static_data = True
    is_created_from_dataframe = json_data.get('is_created_from_dataframe', 
        False)
    slug = json_data['plotSlug']
    if len(slug) == 0:
        slug = json_data['plotName']
    base_slug = slugify(slug)
    slug = base_slug
    counter = 1
    while PlotDBChart.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1
    thumbnail_id = None
    image_data = json_data.get('previewImage', None)
    if image_data is not None:
        try:
            image_data = image_data.split(',')[1]
            image_binary = base64.b64decode(image_data)
            current_file = os.path.dirname(__file__)
            project_path = os.path.dirname(os.path.dirname(os.path.dirname(
                current_file)))
            thumbnail_path = os.path.join(project_path, 'static',
                'thumbnail', 'widget')
            os.makedirs(thumbnail_path, exist_ok=True)
            thumbnail_id = str(uuid.uuid4())
            file_path = os.path.join(thumbnail_path, f'{thumbnail_id}.png')
            with open(file_path, 'wb') as f:
                f.write(image_binary)
        except:
            pass
    print('CREATE plotDBChart')
    plot_db_chart_obj = PlotDBChart.objects.create(plot_chart_id=
        plot_chart_id, type_chart=json_data['typeChart'], name=json_data[
        'plotName'], slug=slug, description=json_data['plotDes'],
        is_expose_widget=json_data['bExposeAsWidget'], is_public_widget=
        json_data['bPublicWidget'], is_static_data=is_static_data,
        has_widget_password=json_data['bWidgetPassword'], widget_password_e
        =widget_password, data_source_list=json_data['dataSourceArr'],
        chart_params=json_data['chartParams'], chart_config=json_data[
        'chartConfigDict'], code_editor_notebook=code_editor_notebook_obj,
        state_params=json_data.get('stateParamsDict', None),
        is_created_from_api=is_gui_plot, is_created_from_dataframe=
        is_created_from_dataframe, thumbnail_path=thumbnail_id,
        date_created=date_now, last_update=date_now, last_date_used=
        date_now, spartaqube_version=sparta_7d2b403019())
    share_rights_obj = ShareRights.objects.create(is_admin=True,
        has_write_rights=True, has_reshare_rights=True, last_update=date_now)
    PlotDBChartShared.objects.create(plot_db_chart=plot_db_chart_obj, user=
        user_obj, share_rights=share_rights_obj, is_owner=True,
        date_created=date_now)
    res_dict = {'res': 1, 'plot_chart_id': plot_chart_id}
    if b_return_model:
        res_dict['plot_db_chart_obj'] = plot_db_chart_obj
    return res_dict


def sparta_8ed818beb5(json_data, user_obj) ->dict:
    """
    Update existing plot
    """
    plot_chart_id = json_data['plot_chart_id']
    plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id=
        plot_chart_id, is_delete=False).all()
    if plot_db_chart_set.count() > 0:
        plot_db_chart_obj = plot_db_chart_set[plot_db_chart_set.count() - 1]
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                plot_db_chart__is_delete=0, plot_db_chart=plot_db_chart_obj
                ) | Q(is_delete=0, user=user_obj, plot_db_chart__is_delete=
                0, plot_db_chart=plot_db_chart_obj))
        else:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                is_delete=0, user=user_obj, plot_db_chart__is_delete=0,
                plot_db_chart=plot_db_chart_obj)
        if plot_db_chart_shared_set.count() > 0:
            plot_db_shared_shared_obj = plot_db_chart_shared_set[0]
            share_rights_obj = plot_db_shared_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_widget_password = json_data.get('bWidgetPassword', False)
                widget_password = None
                if has_widget_password:
                    widget_password = json_data['widgetPassword']
                    widget_password = qube_5ea9d265a5.sparta_4a523d889a(
                        widget_password)
                thumbnail_id = None
                image_data = json_data.get('previewImage', None)
                if image_data is not None:
                    image_data = image_data.split(',')[1]
                    image_binary = base64.b64decode(image_data)
                    try:
                        current_file = os.path.dirname(__file__)
                        project_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
                        thumbnail_path = os.path.join(project_path,
                            'static', 'thumbnail', 'widget')
                        os.makedirs(thumbnail_path, exist_ok=True)
                        if plot_db_chart_obj.thumbnail_path is None:
                            thumbnail_id = str(uuid.uuid4())
                        else:
                            thumbnail_id = plot_db_chart_obj.thumbnail_path
                        file_path = os.path.join(thumbnail_path,
                            f'{thumbnail_id}.png')
                        with open(file_path, 'wb') as f:
                            f.write(image_binary)
                    except:
                        pass
                date_now = datetime.now().astimezone(UTC)
                plot_db_chart_obj.type_chart = json_data['typeChart']
                plot_db_chart_obj.name = json_data['plotName']
                if 'plotDes' in json_data:
                    plot_db_chart_obj.description = json_data['plotDes']
                if 'bExposeAsWidget' in json_data:
                    plot_db_chart_obj.is_expose_widget = json_data[
                        'bExposeAsWidget']
                if 'bStaticDataPlot' in json_data:
                    plot_db_chart_obj.is_static_data = json_data[
                        'bStaticDataPlot']
                if 'bWidgetPassword' in json_data:
                    plot_db_chart_obj.has_widget_password = json_data[
                        'bWidgetPassword']
                    plot_db_chart_obj.widget_password_e = widget_password
                if 'bPublicWidget' in json_data:
                    plot_db_chart_obj.is_public_widget = json_data[
                        'bPublicWidget']
                plot_db_chart_obj.data_source_list = json_data['dataSourceArr']
                plot_db_chart_obj.chart_params = json_data['chartParams']
                plot_db_chart_obj.chart_config = json_data['chartConfigDict']
                plot_db_chart_obj.thumbnail_path = thumbnail_id
                plot_db_chart_obj.last_update = date_now
                plot_db_chart_obj.last_date_used = date_now
                plot_db_chart_obj.save()
                code_editor_notebook_obj = (plot_db_chart_obj.code_editor_notebook)
                if code_editor_notebook_obj is not None:
                    if 'codeEditorNotebookCells' in json_data:
                        code_editor_notebook_obj.cells = json_data[
                            'codeEditorNotebookCells']
                        code_editor_notebook_obj.last_update = date_now
                        code_editor_notebook_obj.save()
    return {'res': 1, 'plot_chart_id': plot_chart_id}


def sparta_0ee33c99f8(json_data, user_obj) ->dict:
    """
    Save plot template
    """
    pass


def sparta_4bdb4014f7(json_data, user_obj) ->dict:
    """
    Load plots library
    """
    user_groups = sparta_673391f9b6(user_obj)
    if len(user_groups) > 0:
        plot_db_chart_shared_set = PlotDBChartShared.objects.filter(Q(
            is_delete=0, user_group__in=user_groups,
            plot_db_chart__is_delete=0) | Q(is_delete=0, user=user_obj,
            plot_db_chart__is_delete=0))
    else:
        plot_db_chart_shared_set = PlotDBChartShared.objects.filter(is_delete
            =0, user=user_obj, plot_db_chart__is_delete=0)
    if plot_db_chart_shared_set.count() > 0:
        order_by_text = json_data.get('orderBy', 'Recently used')
        if order_by_text == 'Recently used':
            plot_db_chart_shared_set = plot_db_chart_shared_set.order_by(
                '-plot_db_chart__last_date_used')
        elif order_by_text == 'Date desc':
            plot_db_chart_shared_set = plot_db_chart_shared_set.order_by(
                '-plot_db_chart__last_update')
        elif order_by_text == 'Date asc':
            plot_db_chart_shared_set = plot_db_chart_shared_set.order_by(
                'plot_db_chart__last_update')
        elif order_by_text == 'Name desc':
            plot_db_chart_shared_set = plot_db_chart_shared_set.order_by(
                '-plot_db_chart__name')
        elif order_by_text == 'Name asc':
            plot_db_chart_shared_set = plot_db_chart_shared_set.order_by(
                'plot_db_chart__name')
        elif order_by_text == 'Type':
            plot_db_chart_shared_set = plot_db_chart_shared_set.order_by(
                'plot_db_chart__type_chart')
    plot_library_list = []
    for plot_db_shared_obj in plot_db_chart_shared_set:
        plot_db_chart_obj = plot_db_shared_obj.plot_db_chart
        share_rights_obj = plot_db_shared_obj.share_rights
        last_update = None
        try:
            last_update = str(plot_db_chart_obj.last_update.strftime(
                '%Y-%m-%d'))
        except:
            pass
        date_created = None
        try:
            date_created = str(plot_db_chart_obj.date_created.strftime(
                '%Y-%m-%d'))
        except Exception as e:
            logger.debug(e)

        def is_number(x):
            try:
                float(x)
                return True
            except ValueError:
                return False
        plot_library_list.append({'plot_chart_id': plot_db_chart_obj.plot_chart_id, 'type_chart': plot_db_chart_obj.type_chart,
            'name': plot_db_chart_obj.name, 'slug': plot_db_chart_obj.slug,
            'description': plot_db_chart_obj.description,
            'is_expose_widget': plot_db_chart_obj.is_expose_widget,
            'is_static_data': plot_db_chart_obj.is_static_data,
            'has_widget_password': plot_db_chart_obj.has_widget_password,
            'is_public_widget': plot_db_chart_obj.is_public_widget,
            'is_owner': plot_db_shared_obj.is_owner, 'has_write_rights':
            share_rights_obj.has_write_rights, 'thumbnail_path':
            plot_db_chart_obj.thumbnail_path, 'last_update': last_update,
            'date_created': date_created, 'is_developer_plot_db': not
            is_number(plot_db_chart_obj.type_chart)})
    return {'res': 1, 'plot_library': plot_library_list}


def exec_notebook_and_get_workspace_variables(full_code,
    data_source_variables: dict, workspace_variables: list, api_key: str
    ) ->dict:
    """
    This function execute codes (from notebook cells), using some already computed data sources (from the connectors),
    injected as DataFrames, and returns all the required workspace variables, used in the plotDB we want to display
    """
    project_path = sparta_2776c51607()['project']
    core_api_path = sparta_2776c51607()['project/core/api']
    ini_code = 'import sys, os\n'
    ini_code += f'sys.path.insert(0, r"{str(project_path)}")\n'
    ini_code += f'sys.path.insert(0, r"{str(core_api_path)}")\n'
    ini_code += f'os.environ["api_key"] = "{api_key}"\n'
    full_code = ini_code + '\n' + full_code
    workspace_variables_dict = dict()
    tiny_kernel_obj = tinykernel.TinyKernel()
    for name, data_frame in data_source_variables.items():
        tiny_kernel_obj.glb[name] = data_frame
    tiny_kernel_obj(full_code)
    for workspace_var in workspace_variables:
        workspace_variables_dict[workspace_var] = tiny_kernel_obj(workspace_var
            )
    return workspace_variables_dict


def sparta_0c4b3509b3(json_data, user_obj) ->dict:
    """
    Open a plot (in the plot library section)
    """
    token_permission = json_data.get('token_permission', '')
    if len(token_permission) == 0:
        token_permission = None
    plot_chart_id = json_data['plot_chart_id']
    password_widget = None
    if 'password_widget' in json_data:
        password_widget = json_data['password_widget']
    data_source_list_override_dynamic_inputs = json_data.get(
        'dataSourceListOverride', [])
    plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id__startswith
        =plot_chart_id, is_delete=False).all()
    if plot_db_chart_set.count() == 1:
        plot_db_chart_obj = plot_db_chart_set[plot_db_chart_set.count() - 1]
        plot_chart_id = plot_db_chart_obj.plot_chart_id
        b_has_access = False
        if token_permission is not None:
            widget_access_dict = sparta_f01fda9284(
                token_permission)
            if widget_access_dict['res'] == 1:
                b_has_access = True
        if not b_has_access:
            if has_permission_widget_or_shared_rights(plot_db_chart_obj,
                user_obj, password_widget=password_widget):
                b_has_access = True
        if b_has_access:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                is_delete=0, plot_db_chart__is_delete=0, plot_db_chart=
                plot_db_chart_obj)
            if plot_db_chart_shared_set.count() > 0:
                plot_db_shared_obj = plot_db_chart_shared_set[0]
                user_owner = plot_db_shared_obj.user
                api_key = sparta_a92982e325(user_owner)
                user_loader_obj = plot_db_shared_obj.user
                data_to_load_from_notebook = []
                plot_db_chart_obj = plot_db_shared_obj.plot_db_chart
                is_static_data = plot_db_chart_obj.is_static_data
                if is_static_data:
                    pass
                else:
                    for data_source_dict in plot_db_chart_obj.data_source_list:
                        is_notebook_source = data_source_dict.get('isNotebook',
                            False)
                        if is_notebook_source:
                            data_to_load_from_notebook.append(data_source_dict
                                ['kernelVariableName'])
                        else:
                            if 'dynamic_inputs' in data_source_dict:
                                connector_id = data_source_dict['connector_id']
                                connector_obj = sparta_6a9452af0d(connector_id,
                                    user_loader_obj)
                                db_dynamic_inputs = []
                                if connector_obj.dynamic_inputs is not None:
                                    try:
                                        db_dynamic_inputs = json.loads(
                                            connector_obj.dynamic_inputs)
                                    except:
                                        pass
                                plot_dynamic_inputs = data_source_dict[
                                    'dynamic_inputs']
                                plot_dynamic_inputs_name_list = [elem[
                                    'input'] for elem in plot_dynamic_inputs]
                                for input_dict in db_dynamic_inputs:
                                    this_input_name = input_dict['input']
                                    if (this_input_name not in
                                        plot_dynamic_inputs_name_list):
                                        plot_dynamic_inputs.append(input_dict)
                                data_source_dict['dynamic_inputs'
                                    ] = plot_dynamic_inputs
                                for overridden_input_dict in data_source_list_override_dynamic_inputs:
                                    if 'connector_id' in overridden_input_dict:
                                        if overridden_input_dict['connector_id'
                                            ] == data_source_dict['connector_id']:
                                            if overridden_input_dict['table_name'
                                                ] == data_source_dict['table_name']:
                                                data_source_dict['dynamic_inputs'
                                                    ] = overridden_input_dict[
                                                    'dynamic_inputs']
                            data_source_dict['previewTopMod'] = 1
                            res_data_source_dict = sparta_6f3b7f8353(
                                data_source_dict, user_loader_obj)
                            if res_data_source_dict['res'] == 1:
                                data_json = res_data_source_dict['data']
                                data_source_dict['data'] = data_json
                code_editor_notebook_obj = (plot_db_chart_obj.code_editor_notebook)
                if code_editor_notebook_obj is not None:
                    code_editor_notebook_cells: str = (code_editor_notebook_obj.cells)
                else:
                    code_editor_notebook_cells = None
                if len(data_to_load_from_notebook) > 0:
                    if code_editor_notebook_cells is not None:
                        full_code_notebook = '\n'.join([this_cell_dict[
                            'code'] for this_cell_dict in json.loads(
                            code_editor_notebook_cells)])
                        data_source_variables_dict = dict()
                        for this_dict in plot_db_chart_obj.data_source_list:
                            if this_dict.get('isDataSource', False
                                ) or this_dict.get('isClipboardPaste', False):
                                data_dict = json.loads(this_dict['data'])
                                data_source_variables_dict[this_dict[
                                    'table_name_workspace']] = pd.DataFrame(
                                    data_dict['data'], index=data_dict[
                                    'index'], columns=data_dict['columns'])
                        workspace_variables_computed: dict = (
                            exec_notebook_and_get_workspace_variables(
                            full_code_notebook, data_source_variables_dict,
                            data_to_load_from_notebook, api_key))
                        for data_source_dict in plot_db_chart_obj.data_source_list:
                            is_notebook_source = data_source_dict['isNotebook']
                            if is_notebook_source:
                                variable_name = data_source_dict[
                                    'kernelVariableName']
                                this_workspace_var_df = (
                                    workspace_variables_computed[variable_name]
                                    )
                                data_source_dict['data'
                                    ] = convert_dataframe_to_json(
                                    convert_to_dataframe(
                                    this_workspace_var_df, variable_name=
                                    variable_name))

                def make_valid_filename(s):
                    s = s.lower()
                    valid_chars = '-_.() %s%s' % (re.escape('/'), re.escape
                        ('\\'))
                    filename = re.sub('[^A-Za-z0-9%s]' % valid_chars, '_', s)
                    return filename
                return {'res': 1, 'plot_chart_id': plot_chart_id,
                    'type_chart': plot_db_chart_obj.type_chart, 'name':
                    plot_db_chart_obj.name, 'slug': plot_db_chart_obj.slug,
                    'name_file': make_valid_filename(plot_db_chart_obj.name
                    ), 'description': plot_db_chart_obj.description,
                    'is_expose_widget': plot_db_chart_obj.is_expose_widget,
                    'is_static_data': plot_db_chart_obj.is_static_data,
                    'has_widget_password': plot_db_chart_obj.has_widget_password, 'is_public_widget':
                    plot_db_chart_obj.is_public_widget, 'data_source_list':
                    plot_db_chart_obj.data_source_list, 'chart_params':
                    plot_db_chart_obj.chart_params, 'chart_config':
                    plot_db_chart_obj.chart_config,
                    'code_editor_notebook_cells':
                    code_editor_notebook_cells, 'state_params':
                    plot_db_chart_obj.state_params}
        else:
            return {'res': -1, 'errorMsg': 'Invalid password'}
    return {'res': -1, 'errorMsg': 'Unexpected error, please try again'}


def sparta_293f1e7541(json_data, user_obj):
    """
    Store date last open connector
    """
    logger.debug('json_data')
    logger.debug(json_data)
    plot_chart_id = json_data['plot_chart_id']
    plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id=
        plot_chart_id, is_delete=False).all()
    if plot_db_chart_set.count() > 0:
        plot_db_obj = plot_db_chart_set[plot_db_chart_set.count() - 1]
        date_now = datetime.now().astimezone(UTC)
        plot_db_obj.last_date_used = date_now
        plot_db_obj.save()
    return {'res': 1}


def sparta_3a3f3f9e4a(user_obj, widget_id) ->dict:
    """
    Get template information to plot data with the correct templatae
    """
    b_has_access = False
    plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id__startswith
        =widget_id, is_delete=False).all()
    if plot_db_chart_set.count() > 0:
        plot_db_chart_obj = plot_db_chart_set[plot_db_chart_set.count() - 1]
        if plot_db_chart_obj.is_expose_widget:
            if plot_db_chart_obj.is_public_widget:
                b_has_access = True
        if not b_has_access:
            user_groups = sparta_673391f9b6(user_obj)
            if len(user_groups) > 0:
                plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                    Q(is_delete=0, user_group__in=user_groups,
                    plot_db_chart__is_delete=0, plot_db_chart=
                    plot_db_chart_obj) | Q(is_delete=0, user=user_obj,
                    plot_db_chart__is_delete=0, plot_db_chart=
                    plot_db_chart_obj))
            else:
                plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                    is_delete=0, user=user_obj, plot_db_chart__is_delete=0,
                    plot_db_chart=plot_db_chart_obj)
            if plot_db_chart_shared_set.count() > 0:
                b_has_access = True
    if b_has_access:
        chart_params_dict = plot_db_chart_obj.chart_params
        if 'options' in chart_params_dict:
            chart_params_dict['options'] = json.loads(chart_params_dict[
                'options'])
        if 'data' in chart_params_dict:
            chart_params_dict['datasets'] = json.loads(chart_params_dict[
                'data'])['datasets']
        type_chart = plot_db_chart_obj.type_chart
        return {'res': 1, 'override_options': chart_params_dict,
            'type_chart': type_chart}
    else:
        return {'res': -1, 'errorMsg':
            'You do not have the rights to access this template'}


def sparta_4f99e44f55(json_data, user_obj) ->dict:
    """
    DEPRECATED
    Plot widget data (use a widget and plot it with other inputs data sent from a Jupyter notebook for instance)
    Explanation of the script below: We are going to replicate the same data structure than the default case.There are three important variables: 
            1. chart_config (dict)
            2. data_source_list (list of dictionaries)
            3. inputs_widget (dict), pickled and stored temporarily in NewPlotApiVariables model (inputs data sent from the user Jupyter Notebook)

        1. chart_config gives us the information to use for the different field: xAxis, yAxisArr, radiusBubbleArr etc...chart_config = {
                "titleChart":"",
                "description":"",
                "xAxis": {
                        "uuid":"a355a3e7-4173-482c-9a6b-02bc2ad3257c",
                        "connector_id":"notebook",
                        "is_index":false,
                        "column":"id"
                },
                "yAxisArr":[
                    {
                        "uuid":"a355a3e7-4173-482c-9a6b-02bc2ad3257c",
                        "connector_id":"notebook",
                        "is_index":false,
                        "column":"id"
                    }
                ],... other fields,
                "labelsArr":[null],
                "radiusBubbleArr":[null],
            }
        2. The mapping is done on the uuid with the data source we use (remind that the datasource are coming from dataframes
            where the user has selected specific columns for the inputs of the plot with drag&drop)
            So we must reconstruct the dataframes using the input data, with the same columns id thant the chart config
            data_source_list = [
                {
                    'uuid': '458e9a25-452e-48c4-b1b9-cb12e1483cd8', ... other fields,
                    'data': '{"columns":[0],"index":[0],"data":[["test"]]}'
                },
                {
                    'uuid': 'a355a3e7-4173-482c-9a6b-02bc2ad3257c', ... other fields,
                    'data': '{"columns":["id"],"index":[0,1,2],"data":[[1],[2],[3]]}'
                }
            ]
        3. inputs_widget = {
                'xAxis': RangeIndex(start=0, stop=17, step=1), 
                'yAxisArr': [..., ... , ...], 
                'labelsArr': None, 
                'radiusBubbleArr': None, ... other fields,
            }

        The objective is to transform the data_source_list to the following:
        data_source_list = [
            {
                'uuid': '458e9a25-452e-48c4-b1b9-cb12e1483cd8', ... other fields,
                'data': '{"columns":[0],"index":[0],"data":[["test"]]}'
            }, # We do not need to change this first dictionary as it is not used (uuid) in the chart_config
            {
                'uuid': 'a355a3e7-4173-482c-9a6b-02bc2ad3257c', ... other fields,
                'data': '{"columns":["id"],"index":RangeIndex(start=0, stop=17, step=1),"data":[..., ... , ...]}' # Use the widget inputs
            }
        ]
    """
    try:
        plot_chart_id = json_data['plot_chart_id']
        session_id = json_data['session_id']
        plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id=
            plot_chart_id, is_delete=False).all()
        if plot_db_chart_set.count() > 0:
            plot_db_chart_obj = plot_db_chart_set[plot_db_chart_set.count() - 1
                ]
            user_groups = sparta_673391f9b6(user_obj)
            if len(user_groups) > 0:
                plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                    Q(is_delete=0, user_group__in=user_groups,
                    plot_db_chart__is_delete=0, plot_db_chart=
                    plot_db_chart_obj) | Q(is_delete=0, user=user_obj,
                    plot_db_chart__is_delete=0, plot_db_chart=
                    plot_db_chart_obj))
            else:
                plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                    is_delete=0, user=user_obj, plot_db_chart__is_delete=0,
                    plot_db_chart=plot_db_chart_obj)
            if plot_db_chart_shared_set.count() > 0:
                plot_db_shared_obj = plot_db_chart_shared_set[0]
                plot_db_chart_obj = plot_db_shared_obj.plot_db_chart
                new_plot_api_variables_set = (NewPlotApiVariables.objects.filter(session_id=session_id).all())
                if new_plot_api_variables_set.count() > 0:
                    new_plot_api_variables_obj = new_plot_api_variables_set[0]
                    pickled_variables = (new_plot_api_variables_obj.pickled_variables)
                    inputs_widget: dict = cloudpickle.loads(pickled_variables.encode('latin1'))
                    data_source_uuid_df_dict: dict = dict()
                    for data_source_dict in plot_db_chart_obj.data_source_list:
                        this_uuid = data_source_dict['uuid']
                        data_source_uuid_df_dict[this_uuid] = pd.DataFrame()
                    chart_config = json.loads(plot_db_chart_obj.chart_config)
                    for key in chart_config.keys():
                        if key in INPUTS_KEYS:
                            if key == 'xAxis':
                                xAxis_dict = chart_config[key]
                                this_uuid = xAxis_dict['uuid']
                                is_index = xAxis_dict['is_index']
                                columns_name = xAxis_dict['column']
                                this_df = data_source_uuid_df_dict[this_uuid]
                                if is_index:
                                    this_df.index = inputs_widget[key]
                                else:
                                    this_df[columns_name] = inputs_widget[key]
                            elif chart_config[key] is not None:
                                attributes_arr = chart_config[key]
                                for idx, attribute_dict in enumerate(
                                    attributes_arr):
                                    if attribute_dict is not None:
                                        this_uuid = attribute_dict['uuid']
                                        is_index = attribute_dict['is_index']
                                        columns_name = attribute_dict['column']
                                        this_df = data_source_uuid_df_dict[
                                            this_uuid]
                                        if is_index:
                                            this_df.index = inputs_widget[key][idx]
                                        else:
                                            this_df[columns_name] = inputs_widget[key][
                                                idx]
                    for data_source_dict in plot_db_chart_obj.data_source_list:
                        this_uuid = data_source_dict['uuid']
                        data_source_dict['data'] = data_source_uuid_df_dict[
                            this_uuid].to_json(orient='split')
                return {'res': 1, 'plot_chart_id': plot_chart_id,
                    'type_chart': plot_db_chart_obj.type_chart, 'name':
                    plot_db_chart_obj.name, 'description':
                    plot_db_chart_obj.description, 'is_expose_widget':
                    plot_db_chart_obj.is_expose_widget, 'is_static_data':
                    plot_db_chart_obj.is_static_data, 'has_widget_password':
                    plot_db_chart_obj.has_widget_password,
                    'is_public_widget': plot_db_chart_obj.is_public_widget,
                    'data_source_list': plot_db_chart_obj.data_source_list,
                    'chart_params': plot_db_chart_obj.chart_params,
                    'chart_config': plot_db_chart_obj.chart_config,
                    'code_editor_notebook_cells': None}
    except Exception as e:
        logger.debug('Error exception > ' + str(e))
        return {'res': -1, 'errorMsg': str(e)}


def sparta_9de8d4efa7(json_data, user_obj) ->dict:
    """
    Delete plot
    """
    plot_chart_id = json_data['plot_chart_id']
    plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id=
        plot_chart_id, is_delete=False).all()
    if plot_db_chart_set.count() > 0:
        plot_db_chart_obj = plot_db_chart_set[plot_db_chart_set.count() - 1]
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                plot_db_chart__is_delete=0, plot_db_chart=plot_db_chart_obj
                ) | Q(is_delete=0, user=user_obj, plot_db_chart__is_delete=
                0, plot_db_chart=plot_db_chart_obj))
        else:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                is_delete=0, user=user_obj, plot_db_chart__is_delete=0,
                plot_db_chart=plot_db_chart_obj)
        if plot_db_chart_shared_set.count() > 0:
            plot_db_chart_shared_obj = plot_db_chart_shared_set[0]
            plot_db_chart_shared_obj.is_delete = True
            plot_db_chart_shared_obj.save()
            print('Deleted plotDB')
    return {'res': 1}


def sparta_f01fda9284(token_permission) ->dict:
    """
    Check if has plotDB access using token (PlotDBPermission model)
    This is used to access plotDB from the API from dashboard/notebook without authenticating user (or owner user)
    """
    plot_db_permission_set = PlotDBPermission.objects.filter(token=
        token_permission)
    if plot_db_permission_set.count() > 0:
        plot_db_permission_obj = plot_db_permission_set[
            plot_db_permission_set.count() - 1]
        return {'res': 1, 'plot_db_chart_obj': plot_db_permission_obj.plot_db_chart}
    return {'res': -1}


def has_permission_widget_or_shared_rights(plot_db_chart_obj, user_obj,
    password_widget=None) ->bool:
    """
    This function returns True if the user has the permission to read the widget and False otherwise
    Used in def open_plot
    """
    has_widget_password = plot_db_chart_obj.has_widget_password
    has_shared_right = False
    if user_obj.is_authenticated:
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                plot_db_chart__is_delete=0, plot_db_chart=plot_db_chart_obj
                ) | Q(is_delete=0, user=user_obj, plot_db_chart__is_delete=
                0, plot_db_chart=plot_db_chart_obj))
        else:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                is_delete=0, user=user_obj, plot_db_chart__is_delete=0,
                plot_db_chart=plot_db_chart_obj)
        if plot_db_chart_shared_set.count() > 0:
            has_shared_right = True
    if has_shared_right:
        return True
    if plot_db_chart_obj.is_expose_widget:
        if plot_db_chart_obj.is_public_widget:
            if not has_widget_password:
                return True
            else:
                try:
                    if qube_5ea9d265a5.sparta_8588885027(
                        plot_db_chart_obj.widget_password_e
                        ) == password_widget:
                        return True
                    else:
                        return False
                except:
                    return False
        else:
            return False
    return False


def sparta_7bdcdc52d9(plot_chart_id, user_obj, password_widget=None) ->dict:
    """
    Check if user can access widget (read only). This is used at the view level (see def plot_widget in viewPlotDB.py)
    res: 
        1  Can access widget
        2  No access, require password (missing password)
        3  No access, wrong password
       -1  Not allowed, redirect to login   
    """
    logger.debug('CHECK NOW has_widget_access:')
    plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id__startswith
        =plot_chart_id, is_delete=False).all()
    b_found = False
    if plot_db_chart_set.count() == 1:
        b_found = True
    else:
        this_slug = plot_chart_id
        plot_db_chart_set = PlotDBChart.objects.filter(slug__startswith=
            this_slug, is_delete=False).all()
        if plot_db_chart_set.count() == 1:
            b_found = True
    if b_found:
        plot_db_chart_obj = plot_db_chart_set[plot_db_chart_set.count() - 1]
        has_widget_password = plot_db_chart_obj.has_widget_password
        if plot_db_chart_obj.is_expose_widget:
            if plot_db_chart_obj.is_public_widget:
                if not has_widget_password:
                    return {'res': 1, 'plot_db_chart_obj': plot_db_chart_obj}
                elif password_widget is None:
                    return {'res': 2, 'errorMsg': 'Require password',
                        'plot_db_chart_obj': plot_db_chart_obj}
                else:
                    try:
                        if qube_5ea9d265a5.sparta_8588885027(
                            plot_db_chart_obj.widget_password_e
                            ) == password_widget:
                            return {'res': 1, 'plot_db_chart_obj':
                                plot_db_chart_obj}
                        else:
                            return {'res': 3, 'errorMsg':
                                'Invalid password', 'plot_db_chart_obj':
                                plot_db_chart_obj}
                    except:
                        return {'res': 3, 'errorMsg': 'Invalid password',
                            'plot_db_chart_obj': plot_db_chart_obj}
            elif user_obj.is_authenticated:
                user_groups = sparta_673391f9b6(user_obj)
                if len(user_groups) > 0:
                    plot_db_chart_shared_set = (PlotDBChartShared.objects.filter(Q(is_delete=0, user_group__in=user_groups,
                        plot_db_chart__is_delete=0, plot_db_chart=
                        plot_db_chart_obj) | Q(is_delete=0, user=user_obj,
                        plot_db_chart__is_delete=0, plot_db_chart=
                        plot_db_chart_obj)))
                else:
                    plot_db_chart_shared_set = (PlotDBChartShared.objects.filter(is_delete=0, user=user_obj,
                        plot_db_chart__is_delete=0, plot_db_chart=
                        plot_db_chart_obj))
                if plot_db_chart_shared_set.count() > 0:
                    return {'res': 1, 'plot_db_chart_obj': plot_db_chart_obj}
            else:
                return {'res': -1}
    return {'res': -1}


def sparta_e66eaadb2d(plot_chart_id, user_obj) ->dict:
    """
    Check if user can access to plot (read only)
    We only check if we have shared rights (or owner)
    """
    plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id__startswith
        =plot_chart_id, is_delete=False).all()
    b_found = False
    if plot_db_chart_set.count() == 1:
        b_found = True
    else:
        this_slug = plot_chart_id
        plot_db_chart_set = PlotDBChart.objects.filter(slug__startswith=
            this_slug, is_delete=False).all()
        if plot_db_chart_set.count() == 1:
            b_found = True
    if b_found:
        plot_db_chart_obj = plot_db_chart_set[plot_db_chart_set.count() - 1]
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                plot_db_chart__is_delete=0, plot_db_chart=plot_db_chart_obj
                ) | Q(is_delete=0, user=user_obj, plot_db_chart__is_delete=
                0, plot_db_chart=plot_db_chart_obj))
        else:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                is_delete=0, user=user_obj, plot_db_chart__is_delete=0,
                plot_db_chart=plot_db_chart_obj)
        if plot_db_chart_shared_set.count() > 0:
            plot_db_shared_obj = plot_db_chart_shared_set[0]
            plot_db_chart_obj = plot_db_shared_obj.plot_db_chart
            return {'res': 1, 'has_access': True, 'plot_db_chart_obj':
                plot_db_chart_obj}
    return {'res': 1, 'has_access': False}


def sparta_a703d18f1e(plot_db_chart_obj: PlotDBChart) ->dict:
    """
    This function returns the number of inputs to pass for a specific plot object
    """
    chart_config = json.loads(plot_db_chart_obj.chart_config)
    inputs_dict = dict()
    INPUTS_KEYS_MAPPER = {'xAxisArr': 'x', 'yAxisArr': 'y',
        'radiusBubbleArr': 'r', 'labelsArr': 'labels', 'ohlcvArr': 'ohlcv',
        'shadedBackgroundArr': 'shaded_background'}
    for key in chart_config.keys():
        if key in INPUTS_KEYS:
            try:
                key_api = INPUTS_KEYS_MAPPER[key]
                if chart_config[key] is not None:
                    inputs_len = len([elem for elem in chart_config[key] if
                        elem is not None])
                    if inputs_len > 0:
                        inputs_dict[key_api] = inputs_len
            except Exception as e:
                logger.debug('Except input struct')
                logger.debug(e)
    return inputs_dict


def sparta_84fdf8fb8c(json_data, user_obj):
    """
    Load plots library widgets
    """
    user_groups = sparta_673391f9b6(user_obj)
    if len(user_groups) > 0:
        plot_db_chart_shared_set = PlotDBChartShared.objects.filter(Q(
            is_delete=0, user_group__in=user_groups,
            plot_db_chart__is_delete=0, plot_db_chart=plot_db_chart_obj,
            plot_db_chart__is_expose_widget=True) | Q(is_delete=0, user=
            user_obj, plot_db_chart__is_delete=0,
            plot_db_chart__is_expose_widget=True))
    else:
        plot_db_chart_shared_set = PlotDBChartShared.objects.filter(is_delete
            =0, user=user_obj, plot_db_chart__is_delete=0,
            plot_db_chart__is_expose_widget=True)
    plot_library_list = []
    for plot_db_shared_obj in plot_db_chart_shared_set:
        plot_db_chart_obj = plot_db_shared_obj.plot_db_chart
        share_rights_obj = plot_db_shared_obj.share_rights
        last_update = None
        try:
            last_update = str(plot_db_chart_obj.last_update.strftime(
                '%Y-%m-%d'))
        except:
            pass
        date_created = None
        try:
            date_created = str(plot_db_chart_obj.date_created.strftime(
                '%Y-%m-%d'))
        except Exception as e:
            logger.debug(e)
        plot_library_list.append({'plot_chart_id': plot_db_chart_obj.plot_chart_id, 'type_chart': plot_db_chart_obj.type_chart,
            'has_widget_password': plot_db_chart_obj.has_widget_password,
            'is_public_widget': plot_db_chart_obj.is_public_widget, 'name':
            plot_db_chart_obj.name, 'slug': plot_db_chart_obj.slug,
            'description': plot_db_chart_obj.description, 'is_owner':
            plot_db_shared_obj.is_owner, 'has_write_rights':
            share_rights_obj.has_write_rights, 'last_update': last_update,
            'date_created': date_created})
    return {'res': 1, 'plot_library': plot_library_list}


def sparta_747f15e466(json_data, user_obj) ->dict:
    """
    Update plot config from the library view
    """
    plot_chart_id = json_data['plot_chart_id']
    is_update_config_from_library = json_data['isCalledFromLibrary']
    plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id=
        plot_chart_id, is_delete=False).all()
    if plot_db_chart_set.count() > 0:
        plot_db_chart_obj = plot_db_chart_set[plot_db_chart_set.count() - 1]
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                plot_db_chart__is_delete=0, plot_db_chart=plot_db_chart_obj
                ) | Q(is_delete=0, user=user_obj, plot_db_chart__is_delete=
                0, plot_db_chart=plot_db_chart_obj))
        else:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                is_delete=0, user=user_obj, plot_db_chart__is_delete=0,
                plot_db_chart=plot_db_chart_obj)
        if plot_db_chart_shared_set.count() > 0:
            plot_db_shared_shared_obj = plot_db_chart_shared_set[0]
            share_rights_obj = plot_db_shared_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_widget_password = json_data['bWidgetPassword']
                widget_password = None
                if has_widget_password:
                    widget_password = json_data['widgetPassword']
                    widget_password = qube_5ea9d265a5.sparta_4a523d889a(
                        widget_password)
                date_now = datetime.now().astimezone(UTC)
                plot_db_chart_obj.has_widget_password = json_data[
                    'bWidgetPassword']
                plot_db_chart_obj.widget_password_e = widget_password
                plot_db_chart_obj.name = json_data['plotName']
                plot_db_chart_obj.plotDes = json_data['plotDes']
                plot_db_chart_obj.is_expose_widget = json_data[
                    'bExposeAsWidget']
                plot_db_chart_obj.is_public_widget = json_data['bPublicWidget']
                plot_db_chart_obj.is_static_data = json_data['bStaticDataPlot']
                plot_db_chart_obj.last_update = date_now
                plot_db_chart_obj.save()
                if is_update_config_from_library:
                    pass
                else:
                    code_editor_notebook_obj = (plot_db_chart_obj.code_editor_notebook)
                    if code_editor_notebook_obj is not None:
                        code_editor_notebook_obj.cells = json_data[
                            'codeEditorNotebookCells']
                        code_editor_notebook_obj.last_update = date_now
                        code_editor_notebook_obj.save()
    return {'res': 1}


def sparta_41a97d41f6(json_data, user_obj) ->dict:
    """
    Update existing plot widget
    """
    plot_chart_id = json_data['plot_chart_id']
    plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id=
        plot_chart_id, is_delete=False).all()
    if plot_db_chart_set.count() > 0:
        plot_db_chart_obj = plot_db_chart_set[plot_db_chart_set.count() - 1]
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                plot_db_chart__is_delete=0, plot_db_chart=plot_db_chart_obj
                ) | Q(is_delete=0, user=user_obj, plot_db_chart__is_delete=
                0, plot_db_chart=plot_db_chart_obj))
        else:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                is_delete=0, user=user_obj, plot_db_chart__is_delete=0,
                plot_db_chart=plot_db_chart_obj)
        if plot_db_chart_shared_set.count() > 0:
            plot_db_shared_shared_obj = plot_db_chart_shared_set[0]
            share_rights_obj = plot_db_shared_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                has_widget_password = json_data['bWidgetPassword']
                widget_password = None
                if has_widget_password:
                    widget_password = json_data['widgetPassword']
                    widget_password = qube_5ea9d265a5.sparta_4a523d889a(
                        widget_password)
                date_now = datetime.now().astimezone(UTC)
                plot_db_chart_obj.has_widget_password = json_data[
                    'bWidgetPassword']
                plot_db_chart_obj.is_public_widget = json_data['bPublicWidget']
                plot_db_chart_obj.widget_password_e = widget_password
                plot_db_chart_obj.last_update = date_now
                plot_db_chart_obj.save()
    return {'res': 1}


def sparta_bc5781c007(json_data, user_obj) ->dict:
    """
    Return title
    """
    plot_chart_id = json_data['plotDBId']
    plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id=
        plot_chart_id, is_delete=False).all()
    if plot_db_chart_set.count() > 0:
        plot_db_chart_obj = plot_db_chart_set[plot_db_chart_set.count() - 1]
        return {'res': 1, 'name': plot_db_chart_obj.name}
    return {'res': -1, 'errorMsg': 'Widget not found'}


def sparta_ae6e8c9a64(json_data, user_obj) ->dict:
    """
    Unexpose widget
    """
    plot_chart_id = json_data['plot_chart_id']
    plot_db_chart_set = PlotDBChart.objects.filter(plot_chart_id=
        plot_chart_id, is_delete=False).all()
    if plot_db_chart_set.count() > 0:
        plot_db_chart_obj = plot_db_chart_set[plot_db_chart_set.count() - 1]
        user_groups = sparta_673391f9b6(user_obj)
        if len(user_groups) > 0:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(Q(
                is_delete=0, user_group__in=user_groups,
                plot_db_chart__is_delete=0, plot_db_chart=plot_db_chart_obj
                ) | Q(is_delete=0, user=user_obj, plot_db_chart__is_delete=
                0, plot_db_chart=plot_db_chart_obj))
        else:
            plot_db_chart_shared_set = PlotDBChartShared.objects.filter(
                is_delete=0, user=user_obj, plot_db_chart__is_delete=0,
                plot_db_chart=plot_db_chart_obj)
        if plot_db_chart_shared_set.count() > 0:
            plot_db_shared_shared_obj = plot_db_chart_shared_set[0]
            share_rights_obj = plot_db_shared_shared_obj.share_rights
            if share_rights_obj.is_admin or share_rights_obj.has_write_rights:
                date_now = datetime.now().astimezone(UTC)
                plot_db_chart_obj.is_expose_widget = False
                plot_db_chart_obj.last_update = date_now
                plot_db_chart_obj.save()
    return {'res': 1}


def sparta_db3e1a37d5(user_obj) ->list:
    """
    Load plots library
    """
    user_groups = sparta_673391f9b6(user_obj)
    if len(user_groups) > 0:
        plot_db_chart_shared_set = PlotDBChartShared.objects.filter(Q(
            is_delete=0, user_group__in=user_groups,
            plot_db_chart__is_delete=0, plot_db_chart=plot_db_chart_obj,
            plot_db_chart__is_expose_widget=True) | Q(is_delete=0, user=
            user_obj, plot_db_chart__is_delete=0,
            plot_db_chart__is_expose_widget=True))
    else:
        plot_db_chart_shared_set = PlotDBChartShared.objects.filter(is_delete
            =0, user=user_obj, plot_db_chart__is_delete=0,
            plot_db_chart__is_expose_widget=True)
    plot_library_list = []
    for plot_db_shared_obj in plot_db_chart_shared_set:
        plot_db_chart_obj = plot_db_shared_obj.plot_db_chart
        share_rights_obj = plot_db_shared_obj.share_rights
        last_update = None
        try:
            last_update = str(plot_db_chart_obj.last_update.strftime(
                '%Y-%m-%d'))
        except:
            pass
        date_created = None
        try:
            date_created = str(plot_db_chart_obj.date_created.strftime(
                '%Y-%m-%d'))
        except Exception as e:
            logger.debug(e)
        plot_library_list.append({'id': plot_db_chart_obj.plot_chart_id,
            'name': plot_db_chart_obj.name, 'description':
            plot_db_chart_obj.description, 'last_update': last_update,
            'date_created': date_created})
    return plot_library_list


def sparta_a9fb9a422b(json_data, user_obj) ->list:
    """
    Check if has widget id
    """
    try:
        has_access_dict = sparta_e66eaadb2d(json_data['widget_id'], user_obj
            )
        b_has_access = has_access_dict['has_access']
        return {'res': 1, 'has_access': b_has_access}
    except:
        pass
    return {'res': -1}


def sparta_7f02866b93(json_data, user_obj) ->list:
    """
    Load plots library
    """
    has_access_dict = sparta_e66eaadb2d(json_data['widget_id'], user_obj)
    b_has_access = has_access_dict['has_access']
    if b_has_access:
        plot_db_chart_obj = has_access_dict['plot_db_chart_obj']
        json_data['plot_chart_id'] = plot_db_chart_obj.plot_chart_id
        res_dict = sparta_0c4b3509b3(json_data, user_obj)
        return {'res': 1, 'data': [elem_dict['data'] for elem_dict in
            res_dict['data_source_list']]}
    return {'res': -1}


def sparta_a53c56e642(data_df, json_data) ->pd.DataFrame:
    """
    
    """
    if 'logTransformationDict' in json_data:
        for key, val in json_data['logTransformationDict'].items():
            if val:
                data_df[key] = data_df[key].apply(lambda x: math.log(x))
    if 'differencingDict' in json_data:
        for key, val in json_data['differencingDict'].items():
            if val:
                differencing_dict = json_data.get('differencingDict', None)
                if differencing_dict is not None:
                    offset = differencing_dict.get(key, 0)
                    if offset != 0:
                        data_df[key] = data_df[key] - data_df[key].shift(offset
                            )
    return data_df


def sparta_4092aad8f8(json_data):
    """
    Returns the dataframe sent from the user to display the plotDB component
    """
    x_data_arr = json.loads(json_data['xAxisDataArr'])
    y_data_arr = json.loads(json_data['yAxisDataArr'])
    chart_params_editor_dict = json.loads(json_data['chartParamsEditorDict'])
    data_df = pd.DataFrame(y_data_arr).T
    user_input_y_columns = []
    try:
        for elem in chart_params_editor_dict['yAxisArr']:
            column_renamed = elem.get('column_renamed', None)
            if column_renamed is None:
                column_renamed = elem.get('column', None)
            user_input_y_columns.append(column_renamed)
        data_df.columns = user_input_y_columns
    except:
        pass
    user_input_x_columns = []
    try:
        for elem in chart_params_editor_dict['xAxisArr']:
            column_renamed = elem.get('column_renamed', None)
            if column_renamed is None:
                column_renamed = elem.get('column', None)
            data_df_cols = list(data_df.columns)
            if column_renamed in data_df_cols:
                cnt = len([elem for elem in data_df_cols if elem ==
                    column_renamed]) + 1
                column_renamed = f'{column_renamed}_{cnt}'
            elif column_renamed in user_input_x_columns:
                cnt = len([elem for elem in user_input_x_columns if elem ==
                    column_renamed]) + 1
                column_renamed = f'{column_renamed}_{cnt}'
            user_input_x_columns.append(column_renamed)
    except:
        pass
    for idx, this_x_data_arr in enumerate(x_data_arr):
        data_df[user_input_x_columns[idx]] = this_x_data_arr
    data_df = sparta_a53c56e642(data_df, json_data)
    return data_df, user_input_x_columns, user_input_y_columns


def sparta_2859c38545(json_data, user_obj):
    """
    Backend to prepare or load component's output
    """
    from project.sparta_6b7c630ead.sparta_c4be29a36f import qube_5baa163408 as qube_5baa163408
    service = json_data['service']
    if service == 'quantstats':
        try:
            return qube_5baa163408.sparta_a1578b82c2(json_data, user_obj)
        except Exception as e:
            logger.debug('Error quantstats')
            logger.debug(traceback.format_exc())
            logger.debug('Error quantstats')
            return {'res': -1, 'errorMsg': str(e)}
    elif service == 'matplotlib':
        try:
            return qube_5baa163408.sparta_2a4f3d80a5(json_data, user_obj)
        except Exception as e:
            logger.debug('Error matpltlib')
            logger.debug(traceback.format_exc())
            return {'res': -1, 'errorMsg': str(e)}
    elif service == 'matplotlib':
        try:
            return qube_5baa163408.sparta_2a4f3d80a5(json_data, user_obj)
        except Exception as e:
            logger.debug('Error matpltlib')
            logger.debug(traceback.format_exc())
            return {'res': -1, 'errorMsg': str(e)}
    elif service == 'relationshipsExplorer':
        model = json_data['model']
        data_df, x_col_list, y_cols_list = sparta_4092aad8f8(json_data)
        print('Relationships explorer data_df')
        print(data_df)
        print('json_data')
        print(json_data)
        print(json_data.keys())
        x_col_str = None
        if len(x_col_list) > 0:
            x_col_str = x_col_list[0]
        if model == 'LinearRegression':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_1d2bd3df26
            target_y_str = x_col_str
            x_features_list = y_cols_list
            print(f'target_y_str > {target_y_str}')
            print(f'x_features_list > {x_features_list}')
            res_dict = sparta_1d2bd3df26(data_df, target_y_str,
                x_features_list, int(json_data.get('rw_beta', 30)), int(
                json_data.get('rw_corr', 30)), B_DARK_THEME=json_data.get(
                'B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'PolynomialRegression':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_eb782e89d0
            target_y_str = x_col_str
            x_features_list = y_cols_list
            res_dict = sparta_eb782e89d0(data_df, target_y_str,
                x_features_list, degree=int(json_data.get('degree', 2)),
                standardize=bool(json_data.get('standardize', True)),
                in_sample=bool(json_data.get('bInSample', True)), test_size
                =float(json_data.get('test_size', 0.2)), B_DARK_THEME=
                json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'DecisionTreeRegression':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_8f1450fbe3
            target_y_str = x_col_str
            x_features_list = y_cols_list
            max_depth = json_data.get('maxDepth', -1)
            if str(max_depth) == '-1':
                max_depth = None
            else:
                max_depth = int(max_depth)
            res_dict = sparta_8f1450fbe3(data_df, target_y_str,
                x_features_list, max_depth=max_depth, in_sample=json_data.get('bInSample', False), standardize=bool(json_data.get(
                'bNormalizeDecisionTree', True)), test_size=1 - float(
                json_data.get('trainTest', 80)) / 100, B_DARK_THEME=
                json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'DecisionTreeRegressionGridCV':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_56dd567bfb
            target_y_str = x_col_str
            x_features_list = y_cols_list
            print(f'target_y_str > {target_y_str}')
            print(f'x_features_list > {x_features_list}')
            max_depth = json_data.get('maxDepth', -1)
            if str(max_depth) == '-1':
                max_depth = None
            else:
                max_depth = int(max_depth)
            res_dict = sparta_56dd567bfb(data_df,
                target_y_str, x_features_list, max_depth=max_depth,
                in_sample=json_data.get('bInSample', False), standardize=
                bool(json_data.get('bNormalizeDecisionTree', True)),
                test_size=1 - float(json_data.get('trainTest', 80)) / 100,
                B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'RandomForestRegression':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_bc85cc60c8
            target_y_str = x_col_str
            x_features_list = y_cols_list
            print(f'target_y_str > {target_y_str}')
            print(f'x_features_list > {x_features_list}')
            max_depth = json_data.get('maxDepth', -1)
            if str(max_depth) == '-1':
                max_depth = None
            else:
                max_depth = int(max_depth)
            res_dict = sparta_bc85cc60c8(data_df, target_y_str,
                x_features_list, n_estimators=json_data.get('n_estimators',
                100), max_depth=max_depth, in_sample=json_data.get(
                'bInSample', False), standardize=bool(json_data.get(
                'bNormalizeDecisionTree', True)), test_size=1 - float(
                json_data.get('trainTest', 80)) / 100, B_DARK_THEME=
                json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'RandomForestRegressionGridCV':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_b810af5e74
            target_y_str = x_col_str
            x_features_list = y_cols_list
            max_depth = json_data.get('maxDepth', -1)
            if str(max_depth) == '-1':
                max_depth = None
            else:
                max_depth = int(max_depth)
            res_dict = sparta_b810af5e74(data_df,
                target_y_str, x_features_list, n_estimators=json_data.get(
                'n_estimators', 100), max_depth=max_depth, in_sample=
                json_data.get('bInSample', False), standardize=bool(
                json_data.get('bNormalizeDecisionTree', True)), test_size=1 -
                float(json_data.get('trainTest', 80)) / 100, B_DARK_THEME=
                json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'clustering':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_f9eb0f17cc, sparta_cbdfcd0d76
            target_y_str = x_col_str
            x_features_list = y_cols_list
            if json_data.get('clusteringModel', 'Kmean') == 'Kmean':
                n_clusters = int(json_data.get('nbComponents', 3))
                if len(x_features_list) < 2:
                    return {'res': -1, 'errorMsg':
                        'You must select at least 2 columns'}
                res_dict = sparta_f9eb0f17cc(data_df, x_features_list,
                    n_clusters, B_DARK_THEME=json_data.get('B_DARK_THEME', 
                    False))
            else:
                res_dict = sparta_cbdfcd0d76(data_df, x_features_list,
                    float(json_data.get('epsilon', 0.5)), int(json_data.get
                    ('minSamples', 5)), B_DARK_THEME=json_data.get(
                    'B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'correlation_network':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_b1ac48fbfa
            target_y_str = x_col_str
            x_features_list = y_cols_list
            res_dict = sparta_b1ac48fbfa(data_df, x_features_list,
                float(json_data.get('threshold', 0.5)), B_DARK_THEME=
                json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'pca':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_b8435ce258
            target_y_str = x_col_str
            x_features_list = y_cols_list
            n_components = int(json_data.get('nbComponents', 3))
            n_components = min(n_components, len(x_features_list))
            if n_components == 1:
                return {'res': -1, 'errorMsg':
                    'You must add at least two series'}
            res_dict = sparta_b8435ce258(data_df, x_features_list, n_components,
                float(json_data.get('nbComponentsVariance', 90)), bool(
                json_data.get('bScalePCA', True)), int(json_data.get(
                'pcaComponentsMode', 1)), B_DARK_THEME=json_data.get(
                'B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'tsne':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_24301b3a53
            target_y_str = x_col_str
            x_features_list = y_cols_list
            if len(x_features_list) < 2:
                return {'res': -1, 'errorMsg':
                    'You must add at least two series'}
            res_dict = sparta_24301b3a53(data_df, x_features_list, int(json_data.get
                ('nbComponents', 2)), int(json_data.get('perplexity', 30)),
                B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'features_importance':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_2ff03ff133
            target_y_str = x_col_str
            x_features_list = y_cols_list
            res_dict = sparta_2ff03ff133(data_df,
                target_y_str, x_features_list, B_DARK_THEME=json_data.get(
                'B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'mutual_information':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_31cba5670f
            target_y_str = x_col_str
            x_features_list = y_cols_list
            res_dict = sparta_31cba5670f(data_df, target_y_str,
                x_features_list, B_DARK_THEME=json_data.get('B_DARK_THEME',
                False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'QuantileRegression':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_4f5d56cf42
            target_y_str = x_col_str
            x_features_list = y_cols_list
            res_dict = sparta_4f5d56cf42(data_df, target_y_str,
                x_features_list, quantiles=json_data.get(
                'selectedQuantiles', [0.1, 0.5, 0.9]), standardize=bool(
                json_data.get('bNormalizeQuantileReg', True)), in_sample=
                bool(json_data.get('bInSample', True)), test_size=1 - float
                (json_data.get('trainTest', 80)) / 100, B_DARK_THEME=
                json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'RollingRegression':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_e570f9940c
            target_y_str = x_col_str
            x_features_list = y_cols_list
            res_dict = sparta_e570f9940c(data_df, target_y_str,
                x_features_list, json_data.get('window', 20), bool(
                json_data.get('bNormalizeRollingReg', True)), B_DARK_THEME=
                json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'RecursiveRegression':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_fa7052b0b7
            target_y_str = x_col_str
            x_features_list = y_cols_list
            res_dict = sparta_fa7052b0b7(data_df, target_y_str,
                x_features_list, standardize=bool(json_data.get(
                'bNormalizeRecursiveReg', True)), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'statisticsSummary':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_fb86963d08 import sparta_8596303abb
            selected_columns = y_cols_list
            print('selected_columns')
            print(selected_columns)
            res_dict = sparta_8596303abb(data_df, selected_columns,
                B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict),
                'data_df_json': data_df[[col for col in list(data_df.columns) if col != '__sq_index__']].to_json(orient='split')}
    elif service == 'tsa':
        model = json_data['model']
        data_df, x_col_list, y_cols_list = sparta_4092aad8f8(json_data)
        x_col_str = x_col_list[0]
        dates_col_str = x_col_str
        variables_list = y_cols_list
        print('Relationships explorer data_df')
        print(data_df)
        print(f'dates_col_str > {dates_col_str}')
        print(f'variables_list > {variables_list}')
        print(f'x_col_list > {x_col_list}')
        print(json_data.get('B_DARK_THEME', 'NOT DEFINED'))
        if model == 'STL':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_1c1713fdd7
            res_dict = sparta_1c1713fdd7(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'wavelet':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_c5907331fd
            res_dict = sparta_c5907331fd(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'hmm':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_586dc04d8d
            res_dict = sparta_586dc04d8d(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'ruptures':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_d7637099db
            res_dict = sparta_d7637099db(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'cusum':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_b8ba683b7a
            res_dict = sparta_b8ba683b7a(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'cusum':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_b8ba683b7a
            res_dict = sparta_b8ba683b7a(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'zscore':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_6e9384a64b
            res_dict = sparta_6e9384a64b(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'isolation_forest':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_7877634d6d
            res_dict = sparta_7877634d6d(data_df[variables_list],
                data_df[dates_col_str], params_dict=json_data.get(
                'paramsDict', None), B_DARK_THEME=json_data.get(
                'B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'mad':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_cfa919eec7
            res_dict = sparta_cfa919eec7(data_df[variables_list],
                data_df[dates_col_str], params_dict=json_data.get(
                'paramsDict', None), B_DARK_THEME=json_data.get(
                'B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'prophet_outlier':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_1416c95027
            res_dict = sparta_1416c95027(data_df[variables_list], data_df
                [dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'granger':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_127ae71cc2
            res_dict = sparta_127ae71cc2(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'cointegration':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_746df5a10b
            res_dict = sparta_746df5a10b(data_df[variables_list],
                data_df[dates_col_str], params_dict=json_data.get(
                'paramsDict', None), B_DARK_THEME=json_data.get(
                'B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'canonical_correlation':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_83cb7fbe9c
            print('X data_df[x_col_list]')
            print(data_df[x_col_list])
            print('Y data_df[variables_list]')
            print(data_df[variables_list])
            res_dict = sparta_83cb7fbe9c(data_df[variables_list],
                data_df[x_col_list], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'sarima':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_ade1045520
            res_dict = sparta_ade1045520(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'ets':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_f428ed357b
            res_dict = sparta_f428ed357b(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'prophet_forecast':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_6a2e602704
            res_dict = sparta_6a2e602704(data_df[variables_list],
                data_df[dates_col_str], params_dict=json_data.get(
                'paramsDict', None), B_DARK_THEME=json_data.get(
                'B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'var':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_c8e18d1dd1
            res_dict = sparta_c8e18d1dd1(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'adf':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_fe6cdc9940
            res_dict = sparta_fe6cdc9940(data_df[variables_list], params_dict=
                json_data.get('paramsDict', None))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'kpss':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_dd01e47a73
            res_dict = sparta_dd01e47a73(data_df[variables_list], params_dict=
                json_data.get('paramsDict', None))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'perron':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_3b00c62e5d
            res_dict = sparta_3b00c62e5d(data_df[variables_list], params_dict
                =json_data.get('paramsDict', None))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
        elif model == 'za':
            from project.sparta_6b7c630ead.sparta_1e870ef5c3.qube_d0ea3747f9 import sparta_7f674ce369
            res_dict = sparta_7f674ce369(data_df[variables_list], data_df[
                dates_col_str], params_dict=json_data.get('paramsDict',
                None), B_DARK_THEME=json_data.get('B_DARK_THEME', False))
            return {'res': 1, 'relationship_explorer': json.dumps(res_dict)}
    return {'res': 1}


def sparta_ed3b8baeaf(json_data, user_obj):
    """
    Compute statistics modal
    """
    import quantstats as qs
    json_data = json_data['data']
    xAxisDataArr = json_data['xAxisDataArr']
    yAxisDataArr = json_data['yAxisDataArr']
    columnsX = json_data['columnsX']
    columnsY = json_data['columns']
    data = yAxisDataArr
    final_cols = columnsY
    if len(columnsX) > 1:
        final_cols = columnsX[1:] + columnsY
        data = xAxisDataArr[1:] + data
    data_df = pd.DataFrame(data).T
    data_df.index = pd.to_datetime(xAxisDataArr[0])
    data_df.columns = final_cols
    try:
        data_df.index = data_df.index.tz_localize('UTC')
    except:
        pass
    for col in final_cols:
        try:
            data_df[col] = data_df[col].astype(float)
        except:
            pass
    returns_series_df = data_df.pct_change()
    res_metrics_df = pd.DataFrame()
    for idx, col in enumerate(final_cols):
        metrics_basic = qs.reports.metrics(returns_series_df[col], mode=
            'basic', display=False)
        if idx == 0:
            res_metrics_df = metrics_basic
        else:
            res_metrics_df = pd.concat([res_metrics_df, metrics_basic], axis=1)
    res_metrics_df.columns = final_cols
    return {'res': 1, 'metrics': res_metrics_df.to_json(orient='split')}


def sparta_88c59fe4fc(json_data, user_obj):
    """
    Groupby input data
    """
    json_data = json_data['data']
    xAxisDataArr = json_data['xAxisDataArr']
    yAxisDataArr = json_data['yAxisDataArr']
    columnsX = json_data['columnsX']
    columnsY = json_data['columns']
    data = yAxisDataArr
    final_cols = columnsY
    if len(columnsX) > 1:
        final_cols = columnsX + columnsY
        data = xAxisDataArr + data
    data_df = pd.DataFrame(data).T
    data_df.columns = final_cols
    groupby_field = ['Country', 'City']
    output_cols = ['Salary', 'Rent']
    output_cols = ['Salary']
    data_df.set_index(groupby_field, inplace=True)
    res_group_by_df = data_df.groupby(groupby_field).mean()
    logger.debug('res_group_by_df')
    logger.debug(res_group_by_df)
    levels = groupby_field
    nb_index = len(res_group_by_df.index[0])
    labels = sorted(list(set(res_group_by_df.index.get_level_values(
        nb_index - 2))))
    datasets = []

    def process_datasets(this_df: pd.DataFrame, level: int=0,
        previous_index_list=None):
        if level == nb_index - 1:
            for output_col in output_cols:
                datasets.append({'data': [0] * len(labels), 'data': this_df
                    [output_col].tolist(), 'labels': list(this_df.index.get_level_values(level)), 'hierarchy':
                    previous_index_list, 'column': output_col, 'label':
                    previous_index_list[-1]})
        elif level < nb_index - 1:
            this_index_data = sorted(list(set(res_group_by_df.index.get_level_values(level))))
            for elem in this_index_data:
                if previous_index_list is None:
                    tmp_list = [elem]
                else:
                    tmp_list = previous_index_list.copy()
                    tmp_list.append(elem)
                process_datasets(this_df[this_df.index.get_level_values(
                    level) == elem], level + 1, tmp_list)
    process_datasets(res_group_by_df)
    logger.debug('chart_data')
    return {'res': 1, 'datasets': datasets, 'labels': labels}

#END OF QUBE
