_A='jsonData'
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from project.models import UserProfile
from project.sparta_6b7c630ead.sparta_cb9b6f5e71 import qube_9af41f857a as qube_9af41f857a
from project.sparta_6b7c630ead.sparta_f168051694 import qube_c7898e0b67 as qube_c7898e0b67
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_9080b99843
@csrf_exempt
@sparta_9080b99843
def sparta_5551a1616d(request):
	B=request;I=json.loads(B.body);C=json.loads(I[_A]);A=B.user;D=0;E=UserProfile.objects.filter(user=A)
	if E.count()>0:
		F=E[0]
		if F.has_open_tickets:
			C['userId']=F.user_profile_id;G=qube_c7898e0b67.sparta_a920f456b5(A)
			if G['res']==1:D=int(G['nbNotifications'])
	H=qube_9af41f857a.sparta_5551a1616d(C,A);H['nbNotificationsHelpCenter']=D;J=json.dumps(H);return HttpResponse(J)
@csrf_exempt
@sparta_9080b99843
def sparta_66430e19c8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9af41f857a.sparta_410755ca3f(C,A.user);E=json.dumps(D);return HttpResponse(E)