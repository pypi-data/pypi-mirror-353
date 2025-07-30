import json, base64
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 as qube_d24f3eb337
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_be7ed37fe1
from project.sparta_6b7c630ead.sparta_c4be29a36f import qube_f591de0f06 as qube_f591de0f06
from project.sparta_6b7c630ead.sparta_6d329e2f11 import qube_2b15813649 as qube_2b15813649


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_86ec20eaae(request):
    """
    Plot DB
    """
    edit_chart_id = request.GET.get('edit')
    if edit_chart_id is None:
        edit_chart_id = '-1'
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 7
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    dict_var['edit_chart_id'] = edit_chart_id
    return render(request, 'dist/project/plot-db/plotDB.html', dict_var)


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_952be19ad7(request):
    """
    Connectors
    """
    edit_chart_id = request.GET.get('edit')
    if edit_chart_id is None:
        edit_chart_id = '-1'
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 10
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    dict_var['edit_chart_id'] = edit_chart_id
    return render(request, 'dist/project/plot-db/plotDB.html', dict_var)


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_501d542364(request):
    """
    Widgets
    """
    edit_chart_id = request.GET.get('edit')
    if edit_chart_id is None:
        edit_chart_id = '-1'
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 11
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    dict_var['edit_chart_id'] = edit_chart_id
    return render(request, 'dist/project/plot-db/plotDB.html', dict_var)


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_fd754dfa03(request):
    """
    DataFrames
    """
    edit_chart_id = request.GET.get('edit')
    if edit_chart_id is None:
        edit_chart_id = '-1'
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 15
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    dict_var['edit_chart_id'] = edit_chart_id
    return render(request, 'dist/project/plot-db/plotDB.html', dict_var)


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_f21ef4e8f0(request):
    """
    DEPRECATED
    Plot Chart Full Screen
    """
    plot_chart_id = request.GET.get('id')
    b_redirect_plot_db = False
    if plot_chart_id is None:
        b_redirect_plot_db = True
    else:
        has_access_dict = qube_f591de0f06.sparta_e66eaadb2d(plot_chart_id,
            request.user)
        b_redirect_plot_db = not has_access_dict['has_access']
    if b_redirect_plot_db:
        return sparta_86ec20eaae(request)
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 7
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    dict_var['plot_chart_id'] = plot_chart_id
    plot_db_chart_obj = has_access_dict['plot_db_chart_obj']
    dict_var['plot_name'] = plot_db_chart_obj.name
    return render(request, 'dist/project/plot-db/plotFull.html', dict_var)


@csrf_exempt
@sparta_be7ed37fe1
def sparta_3c7b94798e(request, id, api_token_id=None):
    """
    Plot Widget
    Do not need to @sparta_be7ed37fe1 as we can query public widget. The method has_widget_access will test if 
    user has rights to access the widget 
    """
    if id is None:
        plot_chart_id = request.GET.get('id')
    else:
        plot_chart_id = id
    return plot_widget_func(request, plot_chart_id)


@csrf_exempt
@sparta_be7ed37fe1
def sparta_521ef9d463(request, dashboard_id, id, password):
    """
    Plot Widget
    Do not need to @sparta_be7ed37fe1 as we can query public widget. The method has_widget_access will test if 
    user has rights to access the widget 
    """
    if id is None:
        plot_chart_id = request.GET.get('id')
    else:
        plot_chart_id = id
    dashboard_password = base64.b64decode(password).decode()
    return plot_widget_func(request, plot_chart_id, dashboard_id=
        dashboard_id, dashboard_password=dashboard_password)


@csrf_exempt
@sparta_be7ed37fe1
def sparta_c9c3dfc5e6(request, widget_id, session_id, api_token_id):
    """
    Plot Template Widget
    Do not need to @sparta_be7ed37fe1 as we can query public widget. The method has_widget_access will test if 
    user has rights to access the widget 
    """
    return plot_widget_func(request, widget_id, session_id)


def plot_widget_func(request, plot_chart_id, session='-1', dashboard_id=
    '-1', token_permission='', dashboard_password=None):
    """
    
    """
    b_redirect_plot_db = False
    if plot_chart_id is None:
        b_redirect_plot_db = True
    else:
        widget_access_dict = qube_f591de0f06.sparta_7bdcdc52d9(plot_chart_id,
            request.user)
        res_access = widget_access_dict['res']
        if res_access == -1:
            b_redirect_plot_db = True
    if b_redirect_plot_db:
        if dashboard_id != '-1':
            widget_access_dict = qube_2b15813649.has_plot_db_access(
                dashboard_id, plot_chart_id, request.user, dashboard_password)
            res_access = widget_access_dict['res']
            if res_access == 1:
                token_permission = widget_access_dict['token_permission']
                b_redirect_plot_db = False
    if b_redirect_plot_db:
        if len(token_permission) > 0:
            widget_access_dict = (qube_f591de0f06.sparta_f01fda9284(token_permission))
            res_access = widget_access_dict['res']
            if res_access == 1:
                b_redirect_plot_db = False
    if b_redirect_plot_db:
        return sparta_86ec20eaae(request)
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 7
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    plot_db_chart_obj = widget_access_dict['plot_db_chart_obj']
    dict_var['b_require_password'] = 0 if widget_access_dict['res'] == 1 else 1
    dict_var['plot_chart_id'] = plot_db_chart_obj.plot_chart_id
    dict_var['plot_name'] = plot_db_chart_obj.name
    dict_var['session'] = str(session)
    dict_var['is_dashboard_widget'] = 1 if dashboard_id != '-1' else 0
    dict_var['is_token'] = 1 if len(token_permission) > 0 else 0
    dict_var['token_permission'] = str(token_permission)
    return render(request, 'dist/project/plot-db/widgets.html', dict_var)


@csrf_exempt
def sparta_44f9700263(request, token):
    """
    Plot Widget using token (This is required for the internal API (or dashboard/notebook) when user runs get_widget('...')
    within the kernel). Why is it needed ?
    If the user share a notebook (public w/o password or to a user), the execution of the kernel code is done as the owner.But for the iframe, we must connect (logged) as the user owner which is problematic. Instead, we are using this token valid 
    for couple of minutes to access the widget."""
    return plot_widget_func(request, plot_chart_id=None, token_permission=token
        )


@csrf_exempt
@sparta_be7ed37fe1
def sparta_d66ab44453(request):
    """
    Start new SpartaQube interactive plot session
    """
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 7
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    dict_var['serialized_data'] = request.POST.get('data')
    return render(request, 'dist/project/plot-db/plotGUI.html', dict_var)


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_5029de2696(request, id):
    """
    Plot Widget
    """
    plot_chart_id = id
    b_redirect_plot_db = False
    if plot_chart_id is None:
        b_redirect_plot_db = True
    else:
        has_access_dict = qube_f591de0f06.sparta_e66eaadb2d(plot_chart_id,
            request.user)
        b_redirect_plot_db = not has_access_dict['has_access']
    if b_redirect_plot_db:
        return sparta_86ec20eaae(request)
    inputs_dict: int = qube_f591de0f06.sparta_a703d18f1e(
        has_access_dict['plot_db_chart_obj'])
    inputs_structure_cmd = ''
    cnt = 0
    for key, val in inputs_dict.items():
        if cnt > 0:
            inputs_structure_cmd += ',\n    '
        if val == 1:
            inputs_structure_cmd += f'{key}=input_{key}'
        else:
            list_elem = str(',\n    '.join([f'input_{key}_{elem}' for elem in
                range(val)]))
            inputs_structure_cmd += f'{key}=[{list_elem}]'
        cnt += 1
    plot_chart_id_with_quote = f"'{plot_chart_id}'"
    get_widget_input_text = f"""
    {plot_chart_id_with_quote}
"""
    plot_data_cmd = f'Spartaqube().get_widget({get_widget_input_text})'
    plot_input_text = f"""
    {plot_chart_id_with_quote},
    {inputs_structure_cmd}
"""
    plot_data_cmd_inputs = f'Spartaqube().plot({plot_input_text})'
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 7
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    dict_var['plot_chart_id'] = plot_chart_id
    plot_db_chart_obj = has_access_dict['plot_db_chart_obj']
    dict_var['plot_name'] = plot_db_chart_obj.name
    dict_var['plot_data_cmd'] = plot_data_cmd
    dict_var['plot_data_cmd_inputs'] = plot_data_cmd_inputs
    return render(request, 'dist/project/plot-db/plotGUISaved.html', dict_var)


@csrf_exempt
@sparta_be7ed37fe1
def sparta_32f0ff9d5d(request, json_vars_html):
    """
    Plot API (iframe)
    """
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = 7
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    dict_var['bCodeMirror'] = True
    dict_var.update(json.loads(json_vars_html))
    dict_var['serialized_data'] = request.POST.get('data')
    return render(request, 'dist/project/plot-db/plotAPI.html', dict_var)


@csrf_exempt
@sparta_be7ed37fe1
def sparta_e5e9047ba9(request):
    """
    Luckysheet (iframe)
    """
    dict_var = {}
    return render(request,
        'dist/project/luckysheetIframe/luckysheet-frame.html', dict_var)

#END OF QUBE
