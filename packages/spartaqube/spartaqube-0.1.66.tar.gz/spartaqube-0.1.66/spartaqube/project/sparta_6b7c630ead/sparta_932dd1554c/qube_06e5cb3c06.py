import hashlib, re, uuid, json, requests, socket, base64, traceback, os
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings as conf_settings
from django.urls import reverse
from project.models import UserProfile, GuestCode, GuestCodeGlobal, LocalApp, SpartaQubeCode
from project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 import sparta_c358e28345
from project.sparta_6b7c630ead.sparta_25484865a6 import qube_4e47130212 as qube_4e47130212
from project.sparta_6b7c630ead.sparta_e2518651f2 import qube_be904e792d as qube_be904e792d
from project.sparta_6b7c630ead.sparta_c85162a299.qube_0d61b0bd36 import Email as Email
from project.logger_config import logger


def sparta_be7ed37fe1(function):
    """
    Decorator for all views
    """

    def wrapper(request, *args, **kw):
        b_is_logged = True
        if not request.user.is_active:
            b_is_logged = False
            logout(request)
        if not request.user.is_authenticated:
            b_is_logged = False
            logout(request)
        try:
            api_token_id = kw.get('api_token_id', None)
        except:
            api_token_id = None
        if not b_is_logged:
            if api_token_id is not None:
                user_obj = qube_be904e792d.sparta_2baaac8a54(api_token_id
                    )
                login(request, user_obj)
        else:
            pass
        return function(request, *args, **kw)
    return wrapper


def sparta_9080b99843(function):
    """
    Decorator for all web services
    """

    def wrapper(request, *args, **kw):
        if not request.user.is_active:
            return HttpResponseRedirect(reverse('notLoggerAPI'))
        if request.user.is_authenticated:
            return function(request, *args, **kw)
        else:
            return HttpResponseRedirect(reverse('notLoggerAPI'))
    return wrapper


def sparta_5cbc69940a(function):
    """
    Decorator for catching errors in wsXXX webservices
    """

    def wrapper(request, *args, **kw):
        try:
            return function(request, *args, **kw)
        except Exception as e:
            if conf_settings.DEBUG:
                logger.debug('Try catch exception with error:')
                logger.debug(e)
                logger.debug('traceback:')
                logger.debug(traceback.format_exc())
            res = {'res': -1, 'errorMsg': str(e)}
            resJson = json.dumps(res)
            return HttpResponse(resJson)
    return wrapper


def sparta_b470153937(function):
    """
    Login API from api_token
    """

    def wrapper(request, *args, **kw):
        is_valid = False
        try:
            json_data_ = json.loads(request.body)
            json_data = json.loads(json_data_['jsonData'])
            api_token_id = json_data['api_token_id']
            user_obj = qube_be904e792d.sparta_2baaac8a54(api_token_id)
            if user_obj is not None:
                is_valid = True
                request.user = user_obj
        except Exception as e:
            logger.debug('exception pip auth')
            logger.debug(e)
        if is_valid:
            return function(request, *args, **kw)
        else:
            email_public = 'public@spartaqube.com'
            user_obj = User.objects.filter(email=email_public).all()[0]
            request.user = user_obj
            return function(request, *args, **kw)
    return wrapper


def sparta_4cb830c888(code) ->bool:
    """
    spartaqube code create account
    """
    try:
        spartaqube_code_set = SpartaQubeCode.objects.all()
        if spartaqube_code_set.count() == 0:
            return code == 'admin'
        else:
            spartaqube_code = spartaqube_code_set[0].spartaqube_code
            key = hashlib.md5(code.encode('utf-8')).hexdigest()
            key = base64.b64encode(key.encode('utf-8'))
            key = key.decode('utf-8')
            return key == spartaqube_code
    except Exception as e:
        pass
    return False


def sparta_c3ea7ef12f() ->str:
    local_app_set = LocalApp.objects.all()
    if local_app_set.count() == 0:
        app_id = str(uuid.uuid4())
        LocalApp.objects.create(app_id=app_id, date_created=datetime.now())
        return app_id
    else:
        return local_app_set[0].app_id


def sparta_b6915ba284():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    return ip_address


def sparta_8617439062(json_data) ->dict:
    """
    Create website account and returns boolean True is success
    """
    del json_data['password']
    del json_data['password_confirmation']
    try:
        json_data['ip_addr'] = sparta_b6915ba284()
    except:
        json_data['ip_addr'] = -1
    json_data_post = dict()
    json_data_post['jsonData'] = json.dumps(json_data)
    proxies_dict = {'http': os.environ.get('http_proxy', None), 'https': os.environ.get('https_proxy', None)}
    response = requests.post(f'{conf_settings.SPARTAQUBE_WEBSITE}/create-user',
        data=json.dumps(json_data_post), proxies=proxies_dict)
    if response.status_code == 200:
        try:
            json_data = json.loads(response.text)
            if json_data['res'] == 1:
                return {'res': 1, 'is_created': True}
            else:
                json_data['is_created'] = False
                return json_data
        except Exception as e:
            return {'res': -1, 'is_created': False, 'errorMsg': str(e)}
    return {'res': 1, 'is_created': False, 'errorMsg':
        f'status code: {response.status_code}. Please check your internet connection'
        }


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


def sparta_0834d17f00(json_data, hostname_url) ->dict:
    """
        Create a new user
    """
    error_dict = {'passwordConfirm':
        'The two passwords must be the same...', 'email':
        'Email address is not valid...', 'form':
        'The form you sent is not valid...', 'emailExist':
        'This email is already registered...'}
    error = False
    firstName = json_data['firstName'].capitalize()
    lastName = json_data['lastName'].capitalize()
    email = json_data['email'].lower()
    password = json_data['password']
    password_confirmation = json_data['password_confirmation']
    spartaqube_code = json_data['code']
    captcha = json_data['captcha']
    json_data['app_id'] = sparta_c3ea7ef12f()
    if captcha == 'cypress' and email == 'cypress_tests@gmail.com':
        if int(os.environ.get('CYPRESS_TEST_APP', '0')) == 1:
            try:
                from project.sparta_9161393429.sparta_16d55c1efd.qube_9ee5b172bb import sparta_b28983b62c
                sparta_b28983b62c()
            except Exception as e:
                file_path = 'C:\\Users\\benme\\Desktop\\LOG_DEBUG_CYPRESS.txt'
                sparta_f66826e34d(file_path, str(e))
    else:
        captcha_validator_dict = sparta_c358e28345(captcha)
        if captcha_validator_dict['res'] != 1:
            return {'res': -1, 'errorMsg': 'Invalid captcha'}
    if not sparta_4cb830c888(spartaqube_code):
        return {'res': -1, 'errorMsg':
            'Invalid spartaqube code, please contact your administrator'}
    if password != password_confirmation:
        error = True
        error_msg = error_dict['passwordConfirm']
    if not re.match('[^@]+@[^@]+\\.[^@]+', email):
        error = True
        error_msg = error_dict['email']
    if User.objects.filter(username=email).exists():
        error = True
        error_msg = error_dict['emailExist']
    if not error:
        res_created_website_user: dict = sparta_8617439062(json_data)
        b_created_website = True
        is_user_created_on_website = res_created_website_user['is_created']
        if not is_user_created_on_website:
            b_created_website = False
        user_obj = User.objects.create_user(email, email, password)
        user_obj.is_staff = False
        user_obj.username = email
        user_obj.first_name = firstName
        user_obj.last_name = lastName
        user_obj.is_active = True
        user_obj.save()
        user_profile_obj = UserProfile(user=user_obj)
        idKeyTmp = str(user_obj.id) + '_' + str(user_obj.email)
        idKeyTmp = idKeyTmp.encode('utf-8')
        idKeyTmp1 = hashlib.md5(idKeyTmp).hexdigest() + str(datetime.now())
        idKeyTmp1 = idKeyTmp1.encode('utf-8')
        registration_token = str(uuid.uuid4())
        user_profile_obj.user_profile_id = hashlib.sha256(idKeyTmp1).hexdigest(
            )
        user_profile_obj.email = email
        user_profile_obj.api_key = str(uuid.uuid4())
        user_profile_obj.registration_token = registration_token
        user_profile_obj.b_created_website = b_created_website
        user_profile_obj.save()
        res = {'res': 1, 'userObj': user_obj}
        return res
    res = {'res': -1, 'errorMsg': error_msg}
    return res


def sparta_83ae62700a(user_obj, hostname_url, registration_token):
    """
    Validation Registration
    """
    email_obj = Email(user_obj.username, [user_obj.email],
        f'Welcome to {conf_settings.PROJECT_NAME}', 'Validate your account')
    email_obj.addOneRow('Validate your account')
    email_obj.addSpaceSeparator()
    email_obj.addOneRow('Click on the link below to validate your account')
    urlButton = (
        f"{hostname_url.rstrip('/')}/registration-validation/{registration_token}"
        )
    email_obj.addOneCenteredButton('Validate', urlButton)
    email_obj.send()


def sparta_e5c4a00143(token):
    """
    
    """
    user_profile_set = UserProfile.objects.filter(registration_token=token)
    if user_profile_set.count() > 0:
        user_profile_obj = user_profile_set[0]
        user_profile_obj.registration_token = ''
        user_profile_obj.is_account_validated = True
        user_profile_obj.save()
        user_obj = user_profile_obj.user
        user_obj.is_active = True
        user_obj.save()
        return {'res': 1, 'user': user_obj}
    return {'res': -1, 'errorMsg': 'Invalid registration token'}


def sparta_8f957b3ecc():
    """
    Check if a guest code is required to create a new account
    """
    return conf_settings.IS_GUEST_CODE_REQUIRED


def sparta_8829439538(guest_code) ->bool:
    """
    If a global guest code if defined, we validate it directly
    """
    if GuestCodeGlobal.objects.filter(guest_id=guest_code, is_active=True
        ).count() > 0:
        return True
    return False


def sparta_c835c51363(guest_code, user_obj):
    """
    If a global guest code if defined, we validate it directly
    If guest code per user is activated, we check for that
    """
    if GuestCodeGlobal.objects.filter(guest_id=guest_code, is_active=True
        ).count() > 0:
        return True
    guest_code_set = GuestCode.objects.filter(user=user_obj)
    if guest_code_set.count() > 0:
        return True
    else:
        guest_code_set = GuestCode.objects.filter(guest_id=guest_code,
            is_used=False)
        if guest_code_set.count() > 0:
            guest_code_obj = guest_code_set[0]
            guest_code_obj.user = user_obj
            guest_code_obj.is_used = True
            guest_code_obj.save()
            return True
    return False


def sparta_159663cfbb(user):
    """
    Test if a user is banned
    """
    user_profile_set = UserProfile.objects.filter(user=user)
    if user_profile_set.count() == 1:
        return user_profile_set[0].is_banned
    else:
        return False


def sparta_264d6fca66(email, captcha):
    """
    
    """
    captcha_validator_dict = sparta_c358e28345(captcha)
    if captcha_validator_dict['res'] != 1:
        return {'res': -1, 'errorMsg': 'Invalid captcha'}
    user_profile_set = UserProfile.objects.filter(user__username=email)
    if user_profile_set.count() == 0:
        return {'res': -1, 'errorMsg': 'An error occurred, please try again'}
    user_profile_obj = user_profile_set[0]
    token_reset_password = str(uuid.uuid4())
    user_profile_obj.token_reset_password = token_reset_password
    user_profile_obj.save()
    sparta_882b525214(user_profile_obj.user, token_reset_password)
    return {'res': 1}


def sparta_882b525214(user_obj, token_reset_password):
    """
    
    """
    email_obj = Email(user_obj.username, [user_obj.email], 'Reset Password',
        'Reset Password Message')
    email_obj.addOneRow('Reset code',
        'Copy the following code to reset your password')
    email_obj.addSpaceSeparator()
    email_obj.addOneRow(token_reset_password)
    email_obj.send()


def sparta_1e943f9e0a(captcha, token, email, password):
    """
    Change password
    """
    captcha_validator_dict = sparta_c358e28345(captcha)
    if captcha_validator_dict['res'] != 1:
        return {'res': -1, 'errorMsg': 'Invalid captcha'}
    user_profile_set = UserProfile.objects.filter(user__username=email)
    if user_profile_set.count() == 0:
        return {'res': -1, 'errorMsg': 'An error occurred, please try again'}
    user_profile_obj = user_profile_set[0]
    if not token == user_profile_obj.token_reset_password:
        return {'res': -1, 'errorMsg': 'Invalid token..., please try again'}
    user_profile_obj.token_reset_password = ''
    user_profile_obj.save()
    user_obj = user_profile_obj.user
    user_obj.set_password(password)
    user_obj.save()
    return {'res': 1}

#END OF QUBE
