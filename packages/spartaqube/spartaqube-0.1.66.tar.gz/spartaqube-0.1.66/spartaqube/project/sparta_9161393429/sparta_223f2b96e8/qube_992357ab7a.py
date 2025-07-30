from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_be7ed37fe1
from project.sparta_6b7c630ead.sparta_f168051694 import qube_c7898e0b67 as qube_c7898e0b67
from project.models import UserProfile
import project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 as qube_d24f3eb337


@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_a9ae039870(request):
    """
        View help center
    """
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = -1
    user_infos_dict = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos_dict)
    dict_var['avatarImg'] = ''
    user_profile_set = UserProfile.objects.filter(user=request.user)
    if user_profile_set.count() > 0:
        user_profile_obj = user_profile_set[0]
        avatar_obj = user_profile_obj.avatar
        if avatar_obj is not None:
            image64 = user_profile_obj.avatar.image64
            dict_var['avatarImg'] = image64
    dict_var['bInvertIcon'] = 0
    return render(request, 'dist/project/helpCenter/helpCenter.html', dict_var)


@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_dac7f6b652(request):
    """
    Click on the notification
    """
    user_profile_set = UserProfile.objects.filter(user=request.user)
    if user_profile_set.count() > 0:
        user_profile_obj = user_profile_set[0]
        user_profile_obj.has_open_tickets = False
        user_profile_obj.save()
    return sparta_a9ae039870(request)

#END OF QUBE
