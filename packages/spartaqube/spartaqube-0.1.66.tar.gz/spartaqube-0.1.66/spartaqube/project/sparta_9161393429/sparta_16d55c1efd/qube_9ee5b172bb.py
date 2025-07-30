import json, hashlib, uuid
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.urls import reverse
import project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 as qube_d24f3eb337
from project.forms import ConnexionForm, RegistrationTestForm, RegistrationBaseForm, RegistrationForm, ResetPasswordForm, ResetPasswordChangeForm
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_be7ed37fe1
from project.sparta_6b7c630ead.sparta_932dd1554c import qube_06e5cb3c06 as qube_06e5cb3c06
from project.sparta_37eb369a45.sparta_1937c59e23 import qube_b39940b497 as qube_b39940b497
from project.models import LoginLocation, UserProfile
from project.logger_config import logger


def sparta_42a4021aba():
    """
        Footer parameter for EE version
    """
    return {'bHasCompanyEE': -1}


def sparta_6caebd9459(request):
    """
    Use was banned, redirect to banned page
    """
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['manifest'] = qube_d24f3eb337.sparta_8701d2f107()
    dict_var['forbiddenEmail'] = conf_settings.FORBIDDEN_EMAIL
    return render(request, 'dist/project/auth/banned.html', dict_var)


@sparta_be7ed37fe1
def sparta_68b57bd629(request):
    """
    
    """
    redirect_page = request.GET.get('login')
    if redirect_page is not None:
        arr_split = redirect_page.split('/')
        redirect_page = '/'.join(arr_split[1:])
        redirect_page = redirect_page.replace('/', '$@$')
    return sparta_829bc015c9(request, redirect_page)


def sparta_435fe74985(request, redirectUrl):
    """
    
    """
    return sparta_829bc015c9(request, redirectUrl)


def sparta_829bc015c9(request, redirectUrl):
    """
    
    """
    logger.debug('Welcome to loginRedirectFunc')
    if request.user.is_authenticated:
        return redirect('home')
    error = False
    error_msg = 'Email or password incorrect'
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(username=email, password=password)
            if user:
                if qube_06e5cb3c06.sparta_159663cfbb(user):
                    return sparta_6caebd9459(request)
                login(request, user)
                hostname, IPAddr = qube_d24f3eb337.sparta_bfd08e89fe()
                LoginLocation.objects.create(user=user, hostname=hostname,
                    ip=IPAddr, date_login=datetime.now())
                if redirectUrl is not None:
                    args_urls = redirectUrl.split('$@$')
                    args_urls = [elem for elem in args_urls if len(elem) > 0]
                    if len(args_urls) > 1:
                        this_path = args_urls[0]
                        return redirect(reverse(this_path, args=args_urls[1:]))
                    return redirect(redirectUrl)
                return redirect('home')
            else:
                error = True
        else:
            error = True
    form = ConnexionForm()
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var.update(qube_d24f3eb337.sparta_b973348881(request))
    dict_var['manifest'] = qube_d24f3eb337.sparta_8701d2f107()
    dict_var['form'] = form
    dict_var['error'] = error
    dict_var['redirectUrl'] = redirectUrl
    dict_var['errorMsg'] = error_msg
    dict_var.update(sparta_42a4021aba())
    return render(request, 'dist/project/auth/login.html', dict_var)


def sparta_ffc8de0499(request):
    """
    Sign in as guest (with public user)
    """
    email_public = 'public@spartaqube.com'
    user_set = User.objects.filter(email=email_public).all()
    if user_set.count() > 0:
        user_obj = user_set[0]
        login(request, user_obj)
    return redirect('home')


@sparta_be7ed37fe1
def sparta_dabbeac779(request):
    """
    Create a new user
    """
    if request.user.is_authenticated:
        return redirect('home')
    error_msg = ''
    b_error = False
    b_require_guest_code = qube_06e5cb3c06.sparta_8f957b3ecc()
    if request.method == 'POST':
        if b_require_guest_code:
            form = RegistrationForm(request.POST)
        else:
            form = RegistrationBaseForm(request.POST)
        if form.is_valid():
            json_data = form.cleaned_data
            guest_code = None
            if b_require_guest_code:
                guest_code = form.cleaned_data['code']
                if not qube_06e5cb3c06.sparta_8829439538(guest_code):
                    b_error = True
                    error_msg = 'Wrong guest code'
            if not b_error:
                base_url = request.META['HTTP_HOST']
                res_create_user = qube_06e5cb3c06.sparta_0834d17f00(json_data,
                    base_url)
                if int(res_create_user['res']) == 1:
                    user = res_create_user['userObj']
                    login(request, user)
                    return redirect('home')
                else:
                    b_error = True
                    error_msg = res_create_user['errorMsg']
        else:
            b_error = True
            error_msg = form.errors.as_data()
    if b_require_guest_code:
        form = RegistrationForm()
    else:
        form = RegistrationBaseForm()
    dictVar = qube_d24f3eb337.sparta_589850e6e7(request)
    dictVar.update(qube_d24f3eb337.sparta_b973348881(request))
    dictVar['manifest'] = qube_d24f3eb337.sparta_8701d2f107()
    dictVar['form'] = form
    dictVar['error'] = b_error
    dictVar['errorMsg'] = error_msg
    dictVar.update(sparta_42a4021aba())
    return render(request, 'dist/project/auth/registration.html', dictVar)


def sparta_5ae8c59845(request):
    """
    Waiting for validation link
    """
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['manifest'] = qube_d24f3eb337.sparta_8701d2f107()
    return render(request, 'dist/project/auth/registrationPending.html',
        dict_var)


def sparta_2ae5526088(request, token):
    """
    Validation token
    """
    res_dict = qube_06e5cb3c06.sparta_e5c4a00143(token)
    if int(res_dict['res']) == 1:
        user_obj = res_dict['user']
        login(request, user_obj)
        return redirect('home')
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['manifest'] = qube_d24f3eb337.sparta_8701d2f107()
    return redirect('login')


def sparta_7ab83e54a6(request):
    """
    
    """
    logout(request)
    return redirect('login')


def sparta_b28983b62c():
    """
    Destroy cypress models
    """
    from project.models import PlotDBChartShared, PlotDBChart, DashboardShared, NotebookShared, KernelShared, DBConnectorUserShared
    cypress_user_email = 'cypress_tests@gmail.com'
    print('Destroy cypress user')
    plot_chart_shared_set = PlotDBChartShared.objects.filter(user__email=
        cypress_user_email).all()
    for plot_chart_shared_obj in plot_chart_shared_set:
        plot_chart_shared_obj.delete()
    dashboard_shared_set = DashboardShared.objects.filter(user__email=
        cypress_user_email).all()
    for dashboard_shared_obj in dashboard_shared_set:
        dashboard_shared_obj.delete()
    notebook_shared_set = NotebookShared.objects.filter(user__email=
        cypress_user_email).all()
    for notebook_shared_obj in notebook_shared_set:
        notebook_shared_obj.delete()
    kernel_shared_set = KernelShared.objects.filter(user__email=
        cypress_user_email).all()
    for kernel_shared_obj in kernel_shared_set:
        kernel_shared_obj.delete()
    connectors_user_set = DBConnectorUserShared.objects.filter(user__email=
        cypress_user_email).all()
    for connectors_user_obj in connectors_user_set:
        connectors_user_obj.delete()


def sparta_277e966933(request):
    """
    Destroy cypress user and models
    """
    cypress_user_email = 'cypress_tests@gmail.com'
    sparta_b28983b62c()
    from project.sparta_6b7c630ead.sparta_2a0a612d78.qube_6219d0a05d import sparta_5fe81eedfb
    sparta_5fe81eedfb()
    if request.user.is_authenticated:
        if request.user.email == cypress_user_email:
            request.user.delete()
    logout(request)
    return redirect('login')


def sparta_7c59bd0305(request):
    """
    
    """
    res = {'res': -100, 'errorMsg': 'You are not logged...'}
    res_json = json.dumps(res)
    return HttpResponse(res_json)


@csrf_exempt
def sparta_264d6fca66(request):
    """
    
    """
    errorMsg = ''
    error = False
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            captcha = form.cleaned_data['captcha']
            res_reset_password = qube_06e5cb3c06.sparta_264d6fca66(email.lower(
                ), captcha)
            try:
                if int(res_reset_password['res']) == 1:
                    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
                    dict_var.update(qube_d24f3eb337.sparta_b973348881(request))
                    form = ResetPasswordChangeForm(request.POST)
                    dict_var['manifest'] = qube_d24f3eb337.sparta_8701d2f107()
                    dict_var['form'] = form
                    dict_var['email'] = email
                    dict_var['error'] = error
                    dict_var['errorMsg'] = errorMsg
                    return render(request,
                        'dist/project/auth/resetPasswordChange.html', dict_var)
                elif int(res_reset_password['res']) == -1:
                    errorMsg = res_reset_password['errorMsg']
                    error = True
            except Exception as e:
                logger.debug('exception ')
                logger.debug(e)
                errorMsg = 'Could not send reset email, please try again'
                error = True
        else:
            errorMsg = 'Please send valid data'
            error = True
    else:
        form = ResetPasswordForm()
    dictVar = qube_d24f3eb337.sparta_589850e6e7(request)
    dictVar.update(qube_d24f3eb337.sparta_b973348881(request))
    dictVar['manifest'] = qube_d24f3eb337.sparta_8701d2f107()
    dictVar['form'] = form
    dictVar['error'] = error
    dictVar['errorMsg'] = errorMsg
    dictVar.update(sparta_42a4021aba())
    return render(request, 'dist/project/auth/resetPassword.html', dictVar)


@csrf_exempt
def sparta_1e943f9e0a(request):
    """
    
    """
    error_msg = ''
    error = False
    if request.method == 'POST':
        form = ResetPasswordChangeForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            password = form.cleaned_data['password']
            password_confirmation = form.cleaned_data['password_confirmation']
            captcha = form.cleaned_data['captcha']
            email = form.cleaned_data['email'].lower()
            if len(password) < 6:
                error_msg = 'Your password must be at least 6 characters'
                error = True
            if password != password_confirmation:
                error_msg = 'The two passwords must be identical...'
                error = True
            if not error:
                res_reset_password_change = (qube_06e5cb3c06.sparta_1e943f9e0a(captcha, token, email.lower(),
                    password))
                try:
                    if int(res_reset_password_change['res']) == 1:
                        user_obj = User.objects.get(username=email)
                        login(request, user_obj)
                        return redirect('home')
                    else:
                        error_msg = res_reset_password_change['errorMsg']
                        error = True
                except Exception as e:
                    error_msg = (
                        'Could not change your password, please try again')
                    error = True
        else:
            error_msg = 'Please send valid data'
            error = True
    else:
        return redirect('reset-password')
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var.update(qube_d24f3eb337.sparta_b973348881(request))
    dict_var['manifest'] = qube_d24f3eb337.sparta_8701d2f107()
    dict_var['form'] = form
    dict_var['error'] = error
    dict_var['errorMsg'] = error_msg
    dict_var['email'] = email
    dict_var.update(sparta_42a4021aba())
    return render(request, 'dist/project/auth/resetPasswordChange.html',
        dict_var)

#END OF QUBE
