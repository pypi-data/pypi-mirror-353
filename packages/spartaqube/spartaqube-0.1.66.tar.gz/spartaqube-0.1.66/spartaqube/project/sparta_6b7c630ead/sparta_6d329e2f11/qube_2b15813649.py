import re
import os
import json
import io, sys
import base64
import traceback
import uuid
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime, timedelta
import pytz
UTC = pytz.utc
from project.models_spartaqube import Dashboard, DashboardShared, PlotDBChart, PlotDBPermission, DataFrameHistory, DataFrameShared, DataFrameModel, DataFramePermission
from project.models import ShareRights
from project.sparta_6b7c630ead.sparta_42b75ebdb3 import qube_eeee71e162 as qube_eeee71e162
from project.sparta_6b7c630ead.sparta_c4be29a36f import qube_5ea9d265a5 as qube_5ea9d265a5
from project.sparta_6b7c630ead.sparta_e12a2379ef.qube_5414460aa1 import Connector as Connector
from project.sparta_6b7c630ead.sparta_c4be29a36f.qube_f591de0f06 import sparta_4bdb4014f7
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_ca8023430e import sparta_b770ba5f34
from project.sparta_6b7c630ead.sparta_48648f141a import qube_444ab4dc41 as qube_444ab4dc41
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_538e75a6b0 import sparta_b58678b446
from project.sparta_6b7c630ead.sparta_aceca65940 import qube_1969b3f192 as qube_1969b3f192
from project.sparta_6b7c630ead.sparta_5e49ed59d5.qube_3583d7aa1d import sparta_7d2b403019
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


def sparta_47176edcb2(json_data, user_obj) ->dict:
    """
    Load dashboard library
    """
    user_groups = sparta_673391f9b6(user_obj)
    if len(user_groups) > 0:
        dashboard_shared_set = DashboardShared.objects.filter(Q(is_delete=0,
            user_group__in=user_groups, dashboard__is_delete=0) | Q(
            is_delete=0, user=user_obj, dashboard__is_delete=0))
    else:
        dashboard_shared_set = DashboardShared.objects.filter(is_delete=0,
            user=user_obj, dashboard__is_delete=0)
    if dashboard_shared_set.count() > 0:
        order_by_text = json_data.get('orderBy', 'Recently used')
        if order_by_text == 'Recently used':
            dashboard_shared_set = dashboard_shared_set.order_by(
                '-dashboard__last_date_used')
        elif order_by_text == 'Date desc':
            dashboard_shared_set = dashboard_shared_set.order_by(
                '-dashboard__last_update')
        elif order_by_text == 'Date asc':
            dashboard_shared_set = dashboard_shared_set.order_by(
                'dashboard__last_update')
        elif order_by_text == 'Name desc':
            dashboard_shared_set = dashboard_shared_set.order_by(
                '-dashboard__name')
        elif order_by_text == 'Name asc':
            dashboard_shared_set = dashboard_shared_set.order_by(
                'dashboard__name')
    dashboard_library_list = []
    for dashboard_shared_obj in dashboard_shared_set:
        dashboard_obj = dashboard_shared_obj.dashboard
        share_rights_obj = dashboard_shared_obj.share_rights
        last_update = None
        try:
            last_update = str(dashboard_obj.last_update.strftime('%Y-%m-%d'))
        except:
            pass
        date_created = None
        try:
            date_created = str(dashboard_obj.date_created.strftime('%Y-%m-%d'))
        except Exception as e:
            logger.debug(e)
        dashboard_library_list.append({'dashboard_id': dashboard_obj.dashboard_id, 'name': dashboard_obj.name, 'slug': dashboard_obj.slug, 'description': dashboard_obj.description,
            'is_expose_dashboard': dashboard_obj.is_expose_dashboard,
            'has_password': dashboard_obj.has_password,
            'is_public_dashboard': dashboard_obj.is_public_dashboard,
            'is_owner': dashboard_shared_obj.is_owner, 'has_write_rights':
            share_rights_obj.has_write_rights, 'last_update': last_update,
            'date_created': date_created})
    return {'res': 1, 'dashboard_library': dashboard_library_list}


def sparta_29a008b1e1(json_data, user_obj) ->dict:
    """
    Load dashboard
    """
    logger.debug('json_data')
    logger.debug(json_data)
    dashboard_id = json_data['dashboardId']
    password_dashboard = json_data.get('modalPassword', None)
    if not user_obj.is_anonymous:
        dashboard_set = Dashboard.objects.filter(dashboard_id__startswith=
            dashboard_id, is_delete=False).all()
        if dashboard_set.count() == 1:
            dashboard_obj = dashboard_set[dashboard_set.count() - 1]
            dashboard_id = dashboard_obj.dashboard_id
            dashboard_access_dict = has_dashboard_access(dashboard_id,
                user_obj, password_dashboard=password_dashboard)
            if dashboard_access_dict['res'] != 1:
                return {'res': dashboard_access_dict['res'], 'errorMsg':
                    dashboard_access_dict['errorMsg']}
        else:
            return {'res': -1, 'errorMsg': 'Dashboard not found...'}
    else:
        dashboard_access_dict = has_dashboard_access(dashboard_id, user_obj,
            password_dashboard=password_dashboard)
        if dashboard_access_dict['res'] != 1:
            return {'res': dashboard_access_dict['res'], 'errorMsg':
                dashboard_access_dict.get('errorMsg',
                'You do not have access to this dashboard')}
        dashboard_obj = dashboard_access_dict['dashboard_obj']
    if not user_obj.is_anonymous:
        dashboard_shared_set = DashboardShared.objects.filter(is_owner=True,
            dashboard=dashboard_obj, user=user_obj)
        if dashboard_shared_set.count() > 0:
            date_now = datetime.now().astimezone(UTC)
            dashboard_obj.last_date_used = date_now
            dashboard_obj.save()
    plot_db_programmatic_attributes_dict = dict()
    if dashboard_obj.plot_db_programmatic_attributes is not None:
        plot_db_programmatic_attributes_dict = json.loads(dashboard_obj.plot_db_programmatic_attributes)
    return {'res': 1, 'dashboard': {'basic': {'dashboard_id': dashboard_obj.dashboard_id, 'name': dashboard_obj.name, 'slug': dashboard_obj.slug, 'description': dashboard_obj.description,
        'is_expose_dashboard': dashboard_obj.is_expose_dashboard,
        'is_public_dashboard': dashboard_obj.is_public_dashboard,
        'has_password': dashboard_obj.has_password, 'dashboard_venv':
        dashboard_obj.dashboard_venv, 'project_path': dashboard_obj.project_path}, 'lumino': {'main_ipynb_filename': os.path.basename(
        dashboard_obj.main_ipynb_fullpath), 'main_ipynb_fullpath':
        dashboard_obj.main_ipynb_fullpath, 'lumino_layout': dashboard_obj.lumino_layout, 'notebook_cells': qube_1969b3f192.sparta_34ed1219f5(dashboard_obj.main_ipynb_fullpath)}, 'grid_config': json.loads(dashboard_obj.grid_config), 'plot_db_programmatic_attributes':
        plot_db_programmatic_attributes_dict}}


def sparta_9faccbd7c9(json_data, user_obj) ->dict:
    """
    Save dashboard
    """
    is_new_dashboard = json_data['isNewDashboard']
    if not is_new_dashboard:
        return sparta_d0f504cd2c(json_data, user_obj)
    date_now = datetime.now().astimezone(UTC)
    dashboard_id = str(uuid.uuid4())
    has_password = json_data['hasDashboardPassword']
    dashboard_password = None
    if has_password:
        dashboard_password = json_data['dashboardPassword']
        dashboard_password = qube_5ea9d265a5.sparta_4a523d889a(
            dashboard_password)
    lumino_layout_dump = json_data['luminoLayout']
    main_ipynb_fullpath = json_data['mainIpynbFullPath']
    dashboard_name = json_data['dashboardName']
    dashboard_description = json_data['dashboardDescription']
    project_path = json_data['projectPath']
    project_path = sparta_b58678b446(project_path)
    is_expose_dashboard = json_data['isDashboardExpose']
    is_public_dashboard = json_data['isDashboardPublic']
    has_password = json_data['hasDashboardPassword']
    dashboard_venv = json_data.get('dashboardVenv', None)
    slug = json_data['dashboardSlug']
    if len(slug) == 0:
        slug = json_data['dashboardName']
    base_slug = slugify(slug)
    slug = base_slug
    counter = 1
    while Dashboard.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1
    grid_config = json_data['gridConfig']
    plot_db_dependencies = []
    for key, grid_items in grid_config.items():
        for item_dict in grid_items:
            if item_dict['itemType'] == 1:
                plot_db_dependencies.append(item_dict['itemId'])
    plot_db_dependencies = list(set(plot_db_dependencies))
    plot_db_programmatic_attributes = json_data['plotDBProgrammaticAttributes']
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
                'thumbnail', 'dashboard')
            os.makedirs(thumbnail_path, exist_ok=True)
            thumbnail_id = str(uuid.uuid4())
            file_path = os.path.join(thumbnail_path, f'{thumbnail_id}.png')
            with open(file_path, 'wb') as f:
                f.write(image_binary)
        except:
            pass
    logger.debug('SAVE DASHBOARD dashboard_notebook')
    logger.debug('main_ipynb_fullpath')
    logger.debug(main_ipynb_fullpath)
    dashboard_obj = Dashboard.objects.create(dashboard_id=dashboard_id,
        name=dashboard_name, slug=slug, description=dashboard_description,
        is_expose_dashboard=is_expose_dashboard, is_public_dashboard=
        is_public_dashboard, has_password=has_password, password_e=
        dashboard_password, lumino_layout=lumino_layout_dump, project_path=
        project_path, dashboard_venv=dashboard_venv, main_ipynb_fullpath=
        main_ipynb_fullpath, grid_config=json.dumps(grid_config),
        plot_db_programmatic_attributes=json.dumps(
        plot_db_programmatic_attributes), plot_db_dependencies=json.dumps(
        plot_db_dependencies), thumbnail_path=thumbnail_id, date_created=
        date_now, last_update=date_now, last_date_used=date_now,
        spartaqube_version=sparta_7d2b403019())
    share_rights_obj = ShareRights.objects.create(is_admin=True,
        has_write_rights=True, has_reshare_rights=True, last_update=date_now)
    DashboardShared.objects.create(dashboard=dashboard_obj, user=user_obj,
        share_rights=share_rights_obj, is_owner=True, date_created=date_now)
    return {'res': 1, 'dashboard_id': dashboard_id}


def sparta_e5250e494b(lumino_dict, entrypoint_full_path) ->bool:
    """
    This function goes recursively in the lumino layout and look for the entrypoint_full_path.If it's not present, we must add it in order to force open it when the user is going to edit the dashboard."""
    layout_type = lumino_dict['type']
    if layout_type == 'split-area':
        children = lumino_dict['children']
        for this_children in children:
            return sparta_e5250e494b(this_children, entrypoint_full_path)
    else:
        widgets = lumino_dict['widgets']
        for widget_dict in widgets:
            if sparta_b58678b446(widget_dict['fullPath']) == entrypoint_full_path:
                return True
    return False


def sparta_d0f504cd2c(json_data, user_obj) ->dict:
    """
    Update existing dashboard
    """
    date_now = datetime.now().astimezone(UTC)
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
            lumino_layout_dump = json_data['luminoLayout']
            main_ipynb_fullpath = json_data['mainIpynbFullPath']
            dashboard_name = json_data['dashboardName']
            dashboard_description = json_data['dashboardDescription']
            is_expose_dashboard = json_data['isDashboardExpose']
            is_public_dashboard = json_data['isDashboardPublic']
            has_password = json_data['hasDashboardPassword']
            slug = json_data['dashboardSlug']
            if dashboard_obj.slug != slug:
                if len(slug) == 0:
                    slug = json_data['dashboardName']
                base_slug = slugify(slug)
                slug = base_slug
                counter = 1
                while Dashboard.objects.filter(slug=slug).exists():
                    slug = f'{base_slug}-{counter}'
                    counter += 1
            grid_config = json_data['gridConfig']
            plot_db_dependencies = []
            for key, grid_items in grid_config.items():
                for item_dict in grid_items:
                    if item_dict['itemType'] == 1:
                        plot_db_dependencies.append(item_dict['itemId'])
            plot_db_dependencies = list(set(plot_db_dependencies))
            thumbnail_id = None
            image_data = json_data.get('previewImage', None)
            if image_data is not None:
                image_data = image_data.split(',')[1]
                image_binary = base64.b64decode(image_data)
                try:
                    current_file = os.path.dirname(__file__)
                    project_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
                    thumbnail_path = os.path.join(project_path, 'static',
                        'thumbnail', 'dashboard')
                    os.makedirs(thumbnail_path, exist_ok=True)
                    if dashboard_obj.thumbnail_path is None:
                        thumbnail_id = str(uuid.uuid4())
                    else:
                        thumbnail_id = dashboard_obj.thumbnail_path
                    file_path = os.path.join(thumbnail_path,
                        f'{thumbnail_id}.png')
                    with open(file_path, 'wb') as f:
                        f.write(image_binary)
                except:
                    pass
            logger.debug('lumino_layout_dump')
            logger.debug(lumino_layout_dump)
            logger.debug(type(lumino_layout_dump))
            dashboard_obj.name = dashboard_name
            dashboard_obj.description = dashboard_description
            dashboard_obj.slug = slug
            dashboard_obj.is_expose_dashboard = is_expose_dashboard
            dashboard_obj.is_public_dashboard = is_public_dashboard
            dashboard_obj.thumbnail_path = thumbnail_id
            dashboard_obj.lumino_layout = lumino_layout_dump
            dashboard_obj.grid_config = json.dumps(grid_config)
            dashboard_obj.plot_db_programmatic_attributes = json.dumps(
                json_data['plotDBProgrammaticAttributes'])
            dashboard_obj.plot_db_dependencies = json.dumps(
                plot_db_dependencies)
            dashboard_obj.last_update = date_now
            dashboard_obj.last_date_used = date_now
            if has_password:
                dashboard_password = json_data['dashboardPassword']
                if len(dashboard_password) > 0:
                    dashboard_password = (qube_5ea9d265a5.sparta_4a523d889a(dashboard_password))
                    dashboard_obj.password_e = dashboard_password
                    dashboard_obj.has_password = True
            else:
                dashboard_obj.has_password = False
            dashboard_obj.save()
    return {'res': 1, 'dashboard_id': dashboard_id}


def sparta_26a4e2180a(json_data, user_obj) ->dict:
    """
    This function saves the lumino layout
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
            lumino_layout_dump = json_data['luminoLayout']
            dashboard_obj.lumino_layout = lumino_layout_dump
            dashboard_obj.save()
    return {'res': 1}


def sparta_ac3b3f9d21(json_data, user_obj) ->dict:
    """
    Change dashboard entrypoint (ipynb)
    """
    logger.debug('json_data')
    logger.debug(json_data)
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
            main_ipynb_fullpath = sparta_b58678b446(json_data['fullPath'])
            dashboard_obj.main_ipynb_fullpath = main_ipynb_fullpath
            dashboard_obj.save()
    return {'res': 1}


def sparta_b7de14519b(json_data, user_obj) ->dict:
    """
    Delete dashboard
    """
    dashboard_id = json_data['dashboardId']
    dashboard_set = Dashboard.objects.filter(dashboard_id=dashboard_id,
        is_delete=False).all()
    if dashboard_set.count() > 0:
        dashboard_obj = dashboard_set[dashboard_set.count() - 1]
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
        if dashboard_shared_set.count() > 0:
            dashboard_shared_obj = dashboard_shared_set[0]
            dashboard_shared_obj.is_delete = True
            dashboard_shared_obj.save()
    return {'res': 1}


def has_dashboard_access(dashboard_id, user_obj, password_dashboard=None
    ) ->dict:
    """
    Check if user can access dashboard (read only). This is used at the view level (see def dashboard_exec in viewDashboard.py)
    res: 
        1  Can access dashboard
        2  No access, require password (missing password)
        3  No access, wrong password
       -1  Not allowed, redirect to login   
    """
    logger.debug('dashboard_id > ' + str(dashboard_id))
    logger.debug('password_dashboard > ' + str(password_dashboard))
    dashboard_set = Dashboard.objects.filter(dashboard_id__startswith=
        dashboard_id, is_delete=False).all()
    b_found = False
    if dashboard_set.count() == 1:
        b_found = True
    else:
        this_slug = dashboard_id
        dashboard_set = Dashboard.objects.filter(slug__startswith=this_slug,
            is_delete=False).all()
        if dashboard_set.count() == 1:
            b_found = True
    if b_found:
        dashboard_obj = dashboard_set[dashboard_set.count() - 1]
        if not user_obj.is_anonymous:
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
            if dashboard_shared_set.count() > 0:
                return {'res': 1, 'dashboard_obj': dashboard_obj}
        has_password = dashboard_obj.has_password
        if dashboard_obj.is_expose_dashboard:
            if dashboard_obj.is_public_dashboard:
                if not has_password:
                    return {'res': 1, 'dashboard_obj': dashboard_obj}
                elif password_dashboard is None:
                    return {'res': 2, 'errorMsg': 'Require password',
                        'dashboard_obj': dashboard_obj}
                else:
                    try:
                        if qube_5ea9d265a5.sparta_8588885027(
                            dashboard_obj.password_e) == password_dashboard:
                            return {'res': 1, 'dashboard_obj': dashboard_obj}
                        else:
                            return {'res': 3, 'errorMsg':
                                'Invalid password', 'dashboard_obj':
                                dashboard_obj}
                    except Exception as e:
                        return {'res': 3, 'errorMsg': 'Invalid password',
                            'dashboard_obj': dashboard_obj}
            elif user_obj.is_authenticated:
                user_groups = sparta_673391f9b6(user_obj)
                if len(user_groups) > 0:
                    dashboard_shared_set = DashboardShared.objects.filter(Q
                        (is_delete=0, user_group__in=user_groups,
                        dashboard__is_delete=0, dashboard=dashboard_obj) |
                        Q(is_delete=0, user=user_obj, dashboard__is_delete=
                        0, dashboard=dashboard_obj))
                else:
                    dashboard_shared_set = DashboardShared.objects.filter(
                        is_delete=0, user=user_obj, dashboard__is_delete=0,
                        dashboard=dashboard_obj)
                if dashboard_shared_set.count() > 0:
                    return {'res': 1, 'dashboard_obj': dashboard_obj}
            else:
                return {'res': -1}
    return {'res': -1}


def sparta_d1cb0aeb94(json_data, user_obj):
    """
    Load plotDB to display the available components to drag&drop in the gridstack
    """
    plot_library_dict = sparta_4bdb4014f7(json_data, user_obj)
    return plot_library_dict


def has_plot_db_access(dashboard_id, plot_db_id, user_obj, dashboard_password
    ) ->dict:
    """
    This function checks if we are allowed to access the plot_db_id in a dashboard.For instance, if the dashboard is public (if we have valid password or not password defined), we should be able
    to access this plotDB widget. OF if we have access to the dashboard and the dashboard has this widget, we should 
    be able to access it. So the logic is to simply check if we have access to the dashboard first, and then check
    if this widget if used in the dashboard (plot_db_dependencies)
    """
    dashboard_access_dict = has_dashboard_access(dashboard_id, user_obj,
        password_dashboard=dashboard_password)
    if dashboard_access_dict['res'] == 1:
        dashboard_obj = dashboard_access_dict['dashboard_obj']
        plot_db_dependencies = json.loads(dashboard_obj.plot_db_dependencies)
        if plot_db_id in plot_db_dependencies:
            plot_db_chart_set = PlotDBChart.objects.filter(
                plot_chart_id__startswith=plot_db_id, is_delete=False).all()
            if plot_db_chart_set.count() > 0:
                plot_db_chart_obj = plot_db_chart_set[0]
                token = str(uuid.uuid4())
                date_now = datetime.now().astimezone(UTC)
                PlotDBPermission.objects.create(plot_db_chart=
                    plot_db_chart_obj, token=token, date_created=date_now)
                return {'res': 1, 'plot_db_chart_obj': plot_db_chart_obj,
                    'token_permission': token}
    return {'res': -1}


def has_dataframe_access(dashboard_id, slug, user_obj, dashboard_password
    ) ->dict:
    """
    TODO SPARTAQUBE TO IMPLEMENT
    This function checks if we are allowed to access the plot_db_id in a dashboard.For instance, if the dashboard is public (if we have valid password or not password defined), we should be able
    to access this plotDB widget. OF if we have access to the dashboard and the dashboard has this widget, we should 
    be able to access it. So the logic is to simply check if we have access to the dashboard first, and then check
    if this widget if used in the dashboard (plot_db_dependencies)
    """
    dashboard_access_dict = has_dashboard_access(dashboard_id, user_obj,
        password_dashboard=dashboard_password)
    if dashboard_access_dict['res'] == 1:
        dashboard_obj = dashboard_access_dict['dashboard_obj']
        plot_db_dependencies = json.loads(dashboard_obj.plot_db_dependencies)
        if plot_db_id in plot_db_dependencies:
            plot_db_chart_set = PlotDBChart.objects.filter(slug=slug,
                is_delete=False).all()
            if plot_db_chart_set.count() > 0:
                plot_db_chart_obj = plot_db_chart_set[0]
                token = str(uuid.uuid4())
                date_now = datetime.now().astimezone(UTC)
                PlotDBPermission.objects.create(plot_db_chart=
                    plot_db_chart_obj, token=token, date_created=date_now)
                return {'res': 1, 'plot_db_chart_obj': plot_db_chart_obj,
                    'token_permission': token}
    return {'res': -1}

#END OF QUBE
