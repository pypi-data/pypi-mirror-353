from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings as conf_settings
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import hashlib
import project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 as qube_d24f3eb337
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_be7ed37fe1


@csrf_exempt
def sparta_aa96310e77(request):
    """
    View API
    """
    dictVar = qube_d24f3eb337.sparta_589850e6e7(request)
    dictVar['menuBar'] = 8
    dictVar['bCodeMirror'] = True
    userKeyDict = qube_d24f3eb337.sparta_f9c2954c80(request.user)
    dictVar.update(userKeyDict)
    return render(request, 'dist/project/api/api.html', dictVar)

#END OF QUBE
