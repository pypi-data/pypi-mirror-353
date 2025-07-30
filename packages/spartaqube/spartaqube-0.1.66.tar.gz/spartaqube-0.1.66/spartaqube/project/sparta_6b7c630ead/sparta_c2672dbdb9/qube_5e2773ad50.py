import re
import os
import json
import stat
import importlib
import io, sys
import subprocess
import platform
import base64
import traceback
import uuid
import shutil
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime, timedelta
import pytz
UTC = pytz.utc
from spartaqube_app.path_mapper_obf import sparta_2776c51607
from project.models_spartaqube import Developer, DeveloperShared
from project.models import ShareRights
from project.sparta_6b7c630ead.sparta_42b75ebdb3 import qube_eeee71e162 as qube_eeee71e162
from project.sparta_6b7c630ead.sparta_c4be29a36f import qube_5ea9d265a5 as qube_5ea9d265a5
from project.sparta_6b7c630ead.sparta_e12a2379ef.qube_5414460aa1 import Connector as Connector
from project.sparta_6b7c630ead.sparta_48648f141a import qube_444ab4dc41 as qube_444ab4dc41
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_538e75a6b0 import sparta_b58678b446
from project.sparta_6b7c630ead.sparta_aceca65940 import qube_1969b3f192 as qube_1969b3f192
from project.sparta_6b7c630ead.sparta_aceca65940 import qube_708c5472c6 as qube_708c5472c6
from project.sparta_6b7c630ead.sparta_5e49ed59d5.qube_3583d7aa1d import sparta_7d2b403019
from project.sparta_6b7c630ead.sparta_d1ec1080b8.qube_8008d24895 import sparta_827e9198b8, sparta_17f64e7001
from project.logger_config import logger


def sparta_775bae5204():
    binaries = ['esbuild-darwin-arm64', 'esbuild-darwin-x64',
        'esbuild-linux-x64', 'esbuild-windows-x64.exe']
    current_path = os.path.dirname(__file__)
    binaries = [os.path.join(current_path, 'esbuild', elem) for elem in
        binaries]

    def set_executable_permissions(file_path):
        if os.name == 'nt':
            try:
                subprocess.run(['icacls', file_path, '/grant',
                    '*S-1-1-0:(RX)'], check=True)
                logger.debug(
                    f'Executable permissions set for: {file_path} (Windows)')
            except subprocess.CalledProcessError as e:
                logger.debug(
                    f'Failed to set permissions for {file_path} on Windows: {e}'
                    )
        else:
            try:
                os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH |
                    stat.S_IXOTH)
                logger.debug(
                    f'Executable permissions set for: {file_path} (Unix/Linux/Mac)'
                    )
            except Exception as e:
                logger.debug(
                    f'Failed to set permissions for {file_path} on Unix/Linux: {e}'
                    )
    for binary in binaries:
        if os.path.exists(binary):
            set_executable_permissions(binary)
        else:
            logger.debug(f'File not found: {binary}')
    return {'res': 1}


def sparta_673391f9b6(user_obj) ->list:
    """
    
    """
    user_group_set = qube_eeee71e162.sparta_325a9ff1bc(user_obj)
    if len(user_group_set) > 0:
        user_groups = [this_obj.user_group for this_obj in user_group_set]
    else:
        user_groups = []
    return user_groups


def sparta_2589e08dd9(project_path) ->dict:
    """
    # TODO SPARTAQUBE to implement project template
    Create a new developer project
    """
    if not os.path.exists(project_path):
        os.makedirs(project_path)
    dest_folder = project_path
    current_path = os.path.dirname(__file__)
    src_folder = os.path.join(sparta_2776c51607()['django_app_template'],
        'developer', 'template')
    for item in os.listdir(src_folder):
        src_path = os.path.join(src_folder, item)
        dest_path = os.path.join(dest_folder, item)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dest_path)
    core_path = os.path.dirname(os.path.dirname(current_path))
    project_base_path = os.path.dirname(core_path)
    static_path = os.path.join(project_base_path, 'static')
    frontend_path = os.path.join(static_path, 'js', 'developer', 'template',
        'frontend')
    dest_path = os.path.join(dest_folder, 'frontend')
    shutil.copytree(frontend_path, dest_path, dirs_exist_ok=True)
    return {'project_path': project_path}


def sparta_7d51f1c6f1(json_data, user_obj) ->dict:
    """
    Validate project path 
    A valid project path is a folder that does not exists yet (and is valid in terms of expression)
    """
    is_plot_db = json_data.get('is_plot_db', False)
    project_path = json_data['projectPath']
    project_path = sparta_b58678b446(project_path)
    developer_set = Developer.objects.filter(project_path=project_path).all()
    if developer_set.count() > 0:
        developer_obj = developer_set[0]
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
        if not has_edit_rights:
            return {'res': -1, 'errorMsg':
                'Chose another path. A project already exists at this location'
                }
    if not isinstance(project_path, str):
        return {'res': -1, 'errorMsg': 'Project path must be a string.'}
    try:
        project_path = os.path.abspath(project_path)
    except Exception as e:
        return {'res': -1, 'errorMsg': f'Invalid project path: {str(e)}'}
    try:
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        developer_path_infos_dict = sparta_2589e08dd9(project_path
            )
        project_path = developer_path_infos_dict['project_path']
        developer_id = ''
        if is_plot_db:
            developer_obj = sparta_3f274f215b(user_obj, project_path)
            developer_id = developer_obj.developer_id
        return {'res': 1, 'project_path': project_path, 'developer_id':
            developer_id}
    except Exception as e:
        return {'res': -1, 'errorMsg': f'Failed to create folder: {str(e)}'}


def sparta_5b28431b04(json_data, user_obj) ->dict:
    """
    Validate project path init git
    """
    json_data['bAddGitignore'] = True
    json_data['bAddReadme'] = True
    return qube_708c5472c6.sparta_827e7d4274(json_data, user_obj)


def sparta_87003b454a(json_data, user_obj) ->dict:
    """
    Validate project path init npm
    """
    return sparta_2eed770d43(json_data, user_obj)


def sparta_0142b8d6b1(json_data, user_obj) ->dict:
    """
    Load developer library: all my developer view + the public (exposed) views
    """
    is_plot_db = json_data.get('is_plot_db', False)
    user_groups = sparta_673391f9b6(user_obj)
    if len(user_groups) > 0:
        developer_shared_set = DeveloperShared.objects.filter(Q(is_delete=0,
            user_group__in=user_groups, developer__is_delete=0,
            developer__is_plot_db=is_plot_db, developer__is_saved_confirmed
            =True) | Q(is_delete=0, user=user_obj, developer__is_delete=0,
            developer__is_plot_db=is_plot_db, developer__is_saved_confirmed
            =True) | Q(is_delete=0, developer__is_delete=0,
            developer__is_expose_developer=True,
            developer__is_public_developer=True, developer__is_plot_db=
            is_plot_db, developer__is_saved_confirmed=True))
    else:
        developer_shared_set = DeveloperShared.objects.filter(Q(is_delete=0,
            user=user_obj, developer__is_delete=0, developer__is_plot_db=
            is_plot_db, developer__is_saved_confirmed=True) | Q(is_delete=0,
            developer__is_delete=0, developer__is_expose_developer=True,
            developer__is_public_developer=True, developer__is_plot_db=
            is_plot_db, developer__is_saved_confirmed=True))
    if developer_shared_set.count() > 0:
        order_by_text = json_data.get('orderBy', 'Recently used')
        if order_by_text == 'Recently used':
            developer_shared_set = developer_shared_set.order_by(
                '-developer__last_date_used')
        elif order_by_text == 'Date desc':
            developer_shared_set = developer_shared_set.order_by(
                '-developer__last_update')
        elif order_by_text == 'Date asc':
            developer_shared_set = developer_shared_set.order_by(
                'developer__last_update')
        elif order_by_text == 'Name desc':
            developer_shared_set = developer_shared_set.order_by(
                '-developer__name')
        elif order_by_text == 'Name asc':
            developer_shared_set = developer_shared_set.order_by(
                'developer__name')
    developer_library_list = []
    for developer_shared_obj in developer_shared_set:
        developer_obj = developer_shared_obj.developer
        share_rights_obj = developer_shared_obj.share_rights
        last_update = None
        try:
            last_update = str(developer_obj.last_update.strftime('%Y-%m-%d'))
        except:
            pass
        date_created = None
        try:
            date_created = str(developer_obj.date_created.strftime('%Y-%m-%d'))
        except Exception as e:
            logger.debug(e)
        developer_library_list.append({'developer_id': developer_obj.developer_id, 'name': developer_obj.name, 'slug': developer_obj.slug, 'slugApi': developer_obj.slug, 'description':
            developer_obj.description, 'is_expose_developer': developer_obj.is_expose_developer, 'has_password': developer_obj.has_password, 'is_public_developer': developer_obj.is_public_developer, 'is_owner': developer_shared_obj.is_owner,
            'has_write_rights': share_rights_obj.has_write_rights,
            'last_update': last_update, 'date_created': date_created,
            'icon': {'type': 'icon', 'icon': 'fa-cube'}, 'category': [
            'developer'], 'typeChart': 'developer', 'type': 'developer',
            'typeId': developer_obj.developer_id, 'projectPath':
            developer_obj.project_path})
    return {'res': 1, 'developer_library': developer_library_list}


def sparta_220ba2adfa(json_data, user_obj) ->dict:
    """
    Load existing project for edit
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
        if developer_shared_set.count() == 0:
            return {'res': -1, 'errorMsg':
                'You do not have the rights to access this project'}
    else:
        return {'res': -1, 'errorMsg': 'Project not found...'}
    developer_shared_set = DeveloperShared.objects.filter(is_owner=True,
        developer=developer_obj, user=user_obj)
    if developer_shared_set.count() > 0:
        date_now = datetime.now().astimezone(UTC)
        developer_obj.last_date_used = date_now
        developer_obj.save()
    return {'res': 1, 'developer': {'basic': {'developer_id': developer_obj.developer_id, 'is_saved_confirmed': developer_obj.is_saved_confirmed, 'is_plot_db': developer_obj.is_plot_db, 'name':
        developer_obj.name, 'slug': developer_obj.slug, 'description':
        developer_obj.description, 'is_expose_developer': developer_obj.is_expose_developer, 'is_public_developer': developer_obj.is_public_developer, 'has_password': developer_obj.has_password,
        'developer_venv': developer_obj.developer_venv, 'project_path':
        developer_obj.project_path}, 'lumino': {'lumino_layout':
        developer_obj.lumino_layout}}}


def sparta_3b47ff5721(json_data, user_obj) ->dict:
    """
    Load existing project for run mode
    """
    developer_id = json_data['developerId']
    if not user_obj.is_anonymous:
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
                    developer=developer_obj) | Q(is_delete=0,
                    developer__is_delete=0, developer__is_expose_developer=
                    True, developer__is_public_developer=True))
            else:
                developer_shared_set = DeveloperShared.objects.filter(Q(
                    is_delete=0, user=user_obj, developer__is_delete=0,
                    developer=developer_obj) | Q(is_delete=0,
                    developer__is_delete=0, developer__is_expose_developer=
                    True, developer__is_public_developer=True))
            if developer_shared_set.count() == 0:
                return {'res': -1, 'errorMsg':
                    'You do not have the rights to access this project'}
        else:
            return {'res': -1, 'errorMsg': 'Project not found...'}
    else:
        password_developer = json_data.get('modalPassword', None)
        logger.debug(f'DEBUG DEVELOPER VIEW TEST >>> {password_developer}')
        developer_access_dict = has_developer_access(developer_id, user_obj,
            password_developer=password_developer)
        logger.debug('MODAL DEBUG DEBUG DEBUG developer_access_dict')
        logger.debug(developer_access_dict)
        if developer_access_dict['res'] != 1:
            return {'res': developer_access_dict['res'], 'errorMsg':
                developer_access_dict['errorMsg']}
        developer_obj = developer_access_dict['developer_obj']
    if not user_obj.is_anonymous:
        developer_shared_set = DeveloperShared.objects.filter(is_owner=True,
            developer=developer_obj, user=user_obj)
        if developer_shared_set.count() > 0:
            date_now = datetime.now().astimezone(UTC)
            developer_obj.last_date_used = date_now
            developer_obj.save()
    return {'res': 1, 'developer': {'basic': {'developer_id': developer_obj.developer_id, 'name': developer_obj.name, 'slug': developer_obj.slug, 'description': developer_obj.description,
        'is_expose_developer': developer_obj.is_expose_developer,
        'is_public_developer': developer_obj.is_public_developer,
        'has_password': developer_obj.has_password, 'developer_venv':
        developer_obj.developer_venv, 'project_path': developer_obj.project_path}, 'lumino': {'lumino_layout': developer_obj.lumino_layout}}}


def sparta_3f274f215b(user_obj, project_path) ->Developer:
    """
    Create empty models: Developer and DeveloperShared in order to load the developerDetached.html
    Then, when the user saves the Developer view, it update the model
    """
    date_now = datetime.now().astimezone(UTC)
    developer_id = str(uuid.uuid4())
    project_path = sparta_b58678b446(project_path)
    developer_obj = Developer.objects.create(developer_id=developer_id,
        project_path=project_path, date_created=date_now, last_update=
        date_now, last_date_used=date_now, spartaqube_version=
        sparta_7d2b403019())
    share_rights_obj = ShareRights.objects.create(is_admin=True,
        has_write_rights=True, has_reshare_rights=True, last_update=date_now)
    DeveloperShared.objects.create(developer=developer_obj, user=user_obj,
        share_rights=share_rights_obj, is_owner=True, date_created=date_now)
    return developer_obj


def sparta_ccdc2c7aee(json_data, user_obj) ->dict:
    """
    Save developer view
    """
    print('SAVE DEVELOPER NOW')
    print(json_data)
    is_new = json_data['isNew']
    if not is_new:
        return sparta_90f9170ec6(json_data, user_obj)
    project_path = json_data['projectPath']
    project_path = sparta_b58678b446(project_path)
    print('FUCK FUCK FUCK')
    print(project_path)
    developer_set = Developer.objects.filter(project_path=project_path,
        is_delete=False).all()
    print(developer_set.count())
    if developer_set.count() > 0:
        json_data['developerId'] = developer_set[0].developer_id
        slug = json_data['slug']
        if len(slug) == 0:
            slug = json_data['name']
        base_slug = slugify(slug)
        slug = base_slug
        counter = 1
        while Developer.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1
        json_data['slug'] = slug
        return sparta_90f9170ec6(json_data, user_obj)
    date_now = datetime.now().astimezone(UTC)
    developer_id = str(uuid.uuid4())
    has_password = json_data['hasPassword']
    developer_password = None
    if has_password:
        developer_password = json_data['password']
        developer_password = qube_5ea9d265a5.sparta_4a523d889a(
            developer_password)
    lumino_layout_dump = json_data['luminoLayout']
    developer_name = json_data['name']
    developer_description = json_data['description']
    project_path = json_data['projectPath']
    project_path = sparta_b58678b446(project_path)
    is_expose_developer = json_data['isExpose']
    is_public_developer = json_data['isPublic']
    has_password = json_data['hasPassword']
    developer_venv = json_data.get('developerVenv', None)
    slug = json_data['slug']
    if len(slug) == 0:
        slug = json_data['name']
    base_slug = slugify(slug)
    slug = base_slug
    counter = 1
    while Developer.objects.filter(slug=slug).exists():
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
                'thumbnail', 'developer')
            os.makedirs(thumbnail_path, exist_ok=True)
            thumbnail_id = str(uuid.uuid4())
            file_path = os.path.join(thumbnail_path, f'{thumbnail_id}.png')
            with open(file_path, 'wb') as f:
                f.write(image_binary)
        except:
            pass
    developer_obj = Developer.objects.create(developer_id=developer_id,
        name=developer_name, slug=slug, description=developer_description,
        is_expose_developer=is_expose_developer, is_public_developer=
        is_public_developer, has_password=has_password, password_e=
        developer_password, lumino_layout=lumino_layout_dump, project_path=
        project_path, developer_venv=developer_venv, thumbnail_path=
        thumbnail_id, date_created=date_now, last_update=date_now,
        last_date_used=date_now, spartaqube_version=sparta_7d2b403019())
    share_rights_obj = ShareRights.objects.create(is_admin=True,
        has_write_rights=True, has_reshare_rights=True, last_update=date_now)
    DeveloperShared.objects.create(developer=developer_obj, user=user_obj,
        share_rights=share_rights_obj, is_owner=True, date_created=date_now)
    return {'res': 1, 'developer_id': developer_id}


def sparta_90f9170ec6(json_data, user_obj) ->dict:
    """
    Update existing developer
    """
    date_now = datetime.now().astimezone(UTC)
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
            lumino_layout_dump = json_data['luminoLayout']
            developer_name = json_data['name']
            developer_description = json_data['description']
            is_expose_developer = json_data['isExpose']
            is_public_developer = json_data['isPublic']
            has_password = json_data['hasPassword']
            slug = json_data['slug']
            if developer_obj.slug != slug:
                if len(slug) == 0:
                    slug = json_data['name']
                base_slug = slugify(slug)
                slug = base_slug
                counter = 1
                while Developer.objects.filter(slug=slug).exists():
                    slug = f'{base_slug}-{counter}'
                    counter += 1
            thumbnail_id = None
            image_data = json_data.get('previewImage', None)
            if image_data is not None:
                image_data = image_data.split(',')[1]
                image_binary = base64.b64decode(image_data)
                try:
                    current_file = os.path.dirname(__file__)
                    project_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
                    thumbnail_path = os.path.join(project_path, 'static',
                        'thumbnail', 'developer')
                    os.makedirs(thumbnail_path, exist_ok=True)
                    if developer_obj.thumbnail_path is None:
                        thumbnail_id = str(uuid.uuid4())
                    else:
                        thumbnail_id = developer_obj.thumbnail_path
                    file_path = os.path.join(thumbnail_path,
                        f'{thumbnail_id}.png')
                    with open(file_path, 'wb') as f:
                        f.write(image_binary)
                except:
                    pass
            logger.debug('lumino_layout_dump')
            logger.debug(lumino_layout_dump)
            logger.debug(type(lumino_layout_dump))
            developer_obj.name = developer_name
            developer_obj.description = developer_description
            developer_obj.slug = slug
            developer_obj.is_saved_confirmed = True
            developer_obj.is_expose_developer = is_expose_developer
            developer_obj.is_public_developer = is_public_developer
            developer_obj.thumbnail_path = thumbnail_id
            developer_obj.lumino_layout = lumino_layout_dump
            developer_obj.last_update = date_now
            developer_obj.last_date_used = date_now
            if has_password:
                developer_password = json_data['password']
                if len(developer_password) > 0:
                    developer_password = (qube_5ea9d265a5.sparta_4a523d889a(developer_password))
                    developer_obj.password_e = developer_password
                    developer_obj.has_password = True
            else:
                developer_obj.has_password = False
            developer_obj.save()
    return {'res': 1, 'developer_id': developer_id}


def sparta_4c11d7b9d9(json_data, user_obj) ->dict:
    """
    This function saves the lumino layout
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
            lumino_layout_dump = json_data['luminoLayout']
            developer_obj.lumino_layout = lumino_layout_dump
            developer_obj.save()
    return {'res': 1}


def sparta_62eacfb5f0(json_data, user_obj) ->dict:
    """
    Delete developer
    """
    developer_id = json_data['developerId']
    developer_set = Developer.objects.filter(developer_id=developer_id,
        is_delete=False).all()
    if developer_set.count() > 0:
        developer_obj = developer_set[developer_set.count() - 1]
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
        if developer_shared_set.count() > 0:
            developer_shared_obj = developer_shared_set[0]
            developer_shared_obj.is_delete = True
            developer_shared_obj.save()
    return {'res': 1}


def has_developer_access(developer_id, user_obj, password_developer=None
    ) ->dict:
    """
    Check if user can access develoepr view (read only).res: 
        1  Can access developer view
        2  No access, require password (missing password)
        3  No access, wrong password
       -1  Not allowed, redirect to login   
    """
    logger.debug('developer_id')
    logger.debug(developer_id)
    developer_set = Developer.objects.filter(developer_id__startswith=
        developer_id, is_delete=False).all()
    b_found = False
    if developer_set.count() == 1:
        b_found = True
    else:
        this_slug = developer_id
        developer_set = Developer.objects.filter(slug__startswith=this_slug,
            is_delete=False).all()
        if developer_set.count() == 1:
            b_found = True
    logger.debug('b_found')
    logger.debug(b_found)
    if b_found:
        developer_obj = developer_set[developer_set.count() - 1]
        has_password = developer_obj.has_password
        if (developer_obj.is_expose_developer or not developer_obj.is_saved_confirmed):
            logger.debug('is exposed')
            if developer_obj.is_public_developer:
                logger.debug('is public')
                if not has_password:
                    logger.debug('no password')
                    return {'res': 1, 'developer_obj': developer_obj}
                else:
                    logger.debug('hass password')
                    if password_developer is None:
                        logger.debug('empty password provided')
                        return {'res': 2, 'errorMsg': 'Require password',
                            'developer_obj': developer_obj}
                    else:
                        try:
                            if qube_5ea9d265a5.sparta_8588885027(
                                developer_obj.password_e
                                ) == password_developer:
                                return {'res': 1, 'developer_obj':
                                    developer_obj}
                            else:
                                return {'res': 3, 'errorMsg':
                                    'Invalid password', 'developer_obj':
                                    developer_obj}
                        except Exception as e:
                            return {'res': 3, 'errorMsg':
                                'Invalid password', 'developer_obj':
                                developer_obj}
            elif user_obj.is_authenticated:
                user_groups = sparta_673391f9b6(user_obj)
                if len(user_groups) > 0:
                    developer_shared_set = DeveloperShared.objects.filter(Q
                        (is_delete=0, user_group__in=user_groups,
                        developer__is_delete=0, developer=developer_obj) |
                        Q(is_delete=0, user=user_obj, developer__is_delete=
                        0, developer=developer_obj))
                else:
                    developer_shared_set = DeveloperShared.objects.filter(
                        is_delete=0, user=user_obj, developer__is_delete=0,
                        developer=developer_obj)
                if developer_shared_set.count() > 0:
                    return {'res': 1, 'developer_obj': developer_obj}
            else:
                return {'res': -1, 'debug': 1}
    return {'res': -1, 'debug': 2}


def sparta_c15380e702(json_data, user_obj) ->dict:
    """
    Open a folder in VSCode."""
    folder_path = sparta_b58678b446(json_data['projectPath'])
    return sparta_827e9198b8(folder_path)


def sparta_b0dd4efb6c(json_data, user_obj) ->dict:
    """
    Open terminal
    """
    path = sparta_b58678b446(json_data['projectPath'])
    return sparta_17f64e7001(path)


def sparta_0293a74675() ->bool:
    """
    Checks if npm is installed on the system.Returns:
        True if npm is installed, False otherwise."""
    try:
        if platform.system() == 'Windows':
            subprocess.run(['where', 'npm'], capture_output=True, check=True)
        else:
            subprocess.run(['command', '-v', 'npm'], capture_output=True,
                check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def sparta_1f5011fc4f() ->str:
    """
    Gets the installed npm version if available.Returns:
        The npm version string if found, None otherwise."""
    try:
        result = subprocess.run('npm -v', shell=True, capture_output=True,
            text=True, check=True)
        return result.stdout
    except:
        try:
            result = subprocess.run(['npm', '-v'], capture_output=True,
                text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            logger.debug(e)
            return None


def sparta_9e0264c0dc() ->str:
    """
    Gets the installed node version if available.Returns:
        The node version string if found, None otherwise."""
    try:
        result = subprocess.run('node -v', shell=True, capture_output=True,
            text=True, check=True)
        return result.stdout
    except:
        try:
            result = subprocess.run(['node', '-v'], capture_output=True,
                text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            logger.debug(e)
            return None


def sparta_6794978552(json_data, user_obj) ->dict:
    """
    
    """
    path = sparta_b58678b446(json_data['projectPath'])
    path = os.path.join(path, 'frontend')
    if not os.path.isdir(path):
        return {'res': -1, 'errorMsg':
            f"The provided path '{path}' is not a valid directory."}
    package_json_path = os.path.join(path, 'package.json')
    is_init = os.path.exists(package_json_path)
    is_npm_available = sparta_0293a74675()
    return {'res': 1, 'is_init': is_init, 'is_npm_installed':
        is_npm_available, 'npm_version': sparta_1f5011fc4f(), 'node_version':
        sparta_9e0264c0dc()}


def sparta_2eed770d43(json_data, user_obj) ->dict:
    """
    Init node npm project
    """
    path = sparta_b58678b446(json_data['projectPath'])
    path = os.path.join(path, 'frontend')
    try:
        result = subprocess.run('npm init -y', shell=True, capture_output=
            True, text=True, check=True, cwd=path)
        logger.debug(result.stdout)
        return {'res': 1}
    except Exception as e:
        logger.debug('Error node npm init')
        logger.debug(e)
        return {'res': -1, 'errorMsg': str(e)}


def sparta_77a32e2aff(json_data, user_obj) ->dict:
    """
    Node list libraries
    """
    logger.debug('NODE LIS LIBS')
    logger.debug(json_data)
    path = sparta_b58678b446(json_data['projectPath'])
    try:
        result = subprocess.run('npm list', shell=True, capture_output=True,
            text=True, check=True, cwd=path)
        logger.debug(result.stdout)
        return {'res': 1, 'stdout': result.stdout}
    except Exception as e:
        logger.debug('Exception')
        logger.debug(e)
        return {'res': -1, 'errorMsg': str(e)}


from django.core.management import call_command
from io import StringIO


def sparta_4961ff006a(project_path, python_executable='python'):
    """
    Checks for pending migrations by running the manage.py makemigrations command
    in a separate subprocess.Args:
        project_path (str): The path to the Django project directory.python_executable (str): The Python executable to use (default: "python").Returns:
        tuple: (bool, str)
            - bool: True if migrations are needed, False otherwise.- str: The combined stdout and stderr from the makemigrations command."""
    has_error = False
    try:
        manage_py_path = os.path.join(project_path, 'manage.py')
        if not os.path.exists(manage_py_path):
            has_error = True
            return (False, f'Error: manage.py not found in {project_path}',
                has_error)
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'app.settings'
        python_executable = sys.executable
        command = [python_executable, 'manage.py', 'makemigrations',
            '--dry-run']
        result = subprocess.run(command, cwd=project_path, text=True,
            capture_output=True, env=env)
        if result.returncode != 0:
            has_error = True
            return False, f'Error: {result.stderr}', has_error
        stdout = result.stdout
        is_migration_needed = 'No changes detected' not in stdout
        return is_migration_needed, stdout, has_error
    except FileNotFoundError as e:
        has_error = True
        return (False,
            f'Error: {e}. Ensure the correct Python executable and project path.'
            , has_error)
    except Exception as e:
        has_error = True
        return False, str(e), has_error


def sparta_c712a44f1b():
    virtual_env = os.environ.get('VIRTUAL_ENV')
    if virtual_env:
        return virtual_env
    else:
        return sys.prefix


def sparta_7638c0ed9c():
    """Gets the path to the pip executable in a platform-independent way."""
    env_path = sparta_c712a44f1b()
    if sys.platform == 'win32':
        pip_path = os.path.join(env_path, 'Scripts', 'pip.exe')
    else:
        pip_path = os.path.join(env_path, 'bin', 'pip')
    return pip_path


def sparta_d780954bc0(json_data, user_obj) ->dict:
    """
    Return if there are pending model migrations
    """
    path = sparta_b58678b446(json_data['projectPath'])
    path = os.path.join(path, 'backend', 'app')
    is_migration_needed, stdout, has_error = sparta_4961ff006a(path)
    res = 1
    error_msg = ''
    if has_error:
        res = -1
        error_msg = stdout
    return {'res': res, 'has_error': has_error, 'has_pending_migrations':
        is_migration_needed, 'stdout': stdout, 'errorMsg': error_msg}


def sparta_18247b35fe(project_path, python_executable='python'):
    """
    Makes and applies migrations in a Django project by running the manage.py makemigrations
    and migrate commands in subprocesses.Args:
        project_path (str): Path to the target Django project directory.settings_module (str): The settings module for the target Django project.python_executable (str): Path to the Python executable for the target project.Returns:
        tuple: (bool, str)
            - bool: True if migrations were made and applied successfully, False otherwise.- str: The combined stdout and stderr from the commands."""
    try:
        manage_py_path = os.path.join(project_path, 'manage.py')
        if not os.path.exists(manage_py_path):
            return False, f'Error: manage.py not found in {project_path}'
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'app.settings'
        python_executable = sys.executable
        commands = [[python_executable, 'manage.py', 'makemigrations'], [
            python_executable, 'manage.py', 'migrate']]
        logger.debug('commands')
        logger.debug(commands)
        output = []
        for command in commands:
            result = subprocess.run(command, cwd=project_path, text=True,
                capture_output=True, env=env)
            if result.stdout is not None:
                if len(str(result.stdout)) > 0:
                    output.append(result.stdout)
            if result.stderr is not None:
                if len(str(result.stderr)) > 0:
                    output.append(
                        f"<span style='color:red'>Stderr:\n{result.stderr}</span>"
                        )
            if result.returncode != 0:
                return False, '\n'.join(output)
        return True, '\n'.join(output)
    except FileNotFoundError as e:
        return (False,
            f'Error: {e}. Ensure the correct Python executable and project path.'
            )
    except Exception as e:
        return False, str(e)


def sparta_688bb9c21a(json_data, user_obj) ->dict:
    """
    Migrate (apply makemigrations and migrate) django migrations
    """
    path = sparta_b58678b446(json_data['projectPath'])
    path = os.path.join(path, 'backend', 'app')
    res_migration, stdout = sparta_18247b35fe(path)
    res = 1
    errorMsg = ''
    if not res_migration:
        res = -1
        errorMsg = stdout
    return {'res': res, 'res_migration': res_migration, 'stdout': stdout,
        'errorMsg': errorMsg}


def sparta_bec36b20ec(json_data, user_obj) ->dict:
    """
    
    """
    return {'res': 1}


def sparta_f213160708(json_data, user_obj) ->dict:
    """
    
    """
    return {'res': 1}


def sparta_a05cfb2620(json_data, user_obj) ->dict:
    """
    
    """
    return {'res': 1}


def sparta_975c8eca81(json_data, user_obj) ->dict:
    """
    Hot reload preview. Check if new changes triggered to refresh the preview
    (DEPRECATED) hot reload is handled using the websocket
    """
    logger.debug('developer_hot_reload_preview json_data')
    logger.debug(json_data)
    return {'res': 1}


def sparta_2212a10872(json_data, user_obj) ->dict:
    """
    Execute the user's api code from the user's project (webservices)
    (DEPRECATED) WE ARE NOW RUNNING THIS WITH A WEBSOCKET
    """
    user_probject_path = sparta_b58678b446(json_data['baseProjectPath'])
    user_backend_path = os.path.join(os.path.dirname(user_probject_path),
        'backend')
    sys.path.insert(0, user_backend_path)
    import webservices
    importlib.reload(webservices)
    service_name = json_data['service']
    post_data: dict = json_data.copy()
    del json_data['baseProjectPath']
    try:
        return webservices.sparta_d0bf0e38a6(service_name, post_data, user_obj)
    except Exception as e:
        return {'res': -1, 'errorMsg': str(e)}

#END OF QUBE
