from urllib.parse import urlparse, urlunparse
from django.contrib.auth.decorators import login_required
from django.conf import settings as conf_settings
from django.shortcuts import render
import project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 as qube_d24f3eb337
from project.models import UserProfile
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_be7ed37fe1
from project.sparta_9161393429.sparta_16d55c1efd.qube_9ee5b172bb import sparta_42a4021aba


@sparta_be7ed37fe1
@login_required(redirect_field_name='login')
def sparta_062e9a04ce(request, idSection=1):
    """
    
    """
    user_profile_obj = UserProfile.objects.get(user=request.user)
    avatar_obj = user_profile_obj.avatar
    if avatar_obj is not None:
        avatar_obj = user_profile_obj.avatar.avatar
    url_terms = urlparse(conf_settings.URL_TERMS)
    if not url_terms.scheme:
        url_terms = urlunparse(url_terms._replace(scheme='http'))
    resDict = {'item': 1, 'idSection': idSection, 'userProfil':
        user_profile_obj, 'avatar': avatar_obj, 'url_terms': url_terms}
    dictVar = qube_d24f3eb337.sparta_589850e6e7(request)
    dictVar.update(qube_d24f3eb337.sparta_f9c2954c80(request.user))
    dictVar.update(resDict)
    accessKey = ''
    dictVar['accessKey'] = accessKey
    dictVar['menuBar'] = 4
    dictVar.update(sparta_42a4021aba())
    return render(request, 'dist/project/auth/settings.html', dictVar)

#END OF QUBE
