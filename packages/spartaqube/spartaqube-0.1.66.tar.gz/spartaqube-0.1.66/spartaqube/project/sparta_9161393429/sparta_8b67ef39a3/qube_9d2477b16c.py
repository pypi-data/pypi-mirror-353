from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 as qube_d24f3eb337
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_be7ed37fe1


@csrf_exempt
@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_d1e2723885(request):
    """
    View Homepage Welcome back
    """
    dict_var = qube_d24f3eb337.sparta_589850e6e7(request)
    dict_var['menuBar'] = -1
    user_infos = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dict_var.update(user_infos)
    return render(request, 'dist/project/homepage/homepage.html', dict_var)

#END OF QUBE
