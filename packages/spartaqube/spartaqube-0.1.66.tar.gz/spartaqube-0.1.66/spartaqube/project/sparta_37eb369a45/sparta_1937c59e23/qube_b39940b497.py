_C='isAuth'
_B='jsonData'
_A='res'
import json
from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from project.sparta_6b7c630ead.sparta_932dd1554c import qube_06e5cb3c06 as qube_06e5cb3c06
from project.sparta_25bf7ff8a2.sparta_97f62436eb.qube_d24f3eb337 import sparta_c358e28345
from project.logger_config import logger
@csrf_exempt
def sparta_0834d17f00(request):A=json.loads(request.body);B=json.loads(A[_B]);return qube_06e5cb3c06.sparta_0834d17f00(B)
@csrf_exempt
def sparta_36f77d8e1a(request):logout(request);A={_A:1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_d3f7266584(request):
	if request.user.is_authenticated:A=1
	else:A=0
	B={_A:1,_C:A};C=json.dumps(B);return HttpResponse(C)
def sparta_3fc5e09847(request):
	B=request;from django.contrib.auth import authenticate as F,login;from django.contrib.auth.models import User as C;G=json.loads(B.body);D=json.loads(G[_B]);H=D['email'];I=D['password'];E=0
	try:
		A=C.objects.get(email=H);A=F(B,username=A.username,password=I)
		if A is not None:login(B,A);E=1
	except C.DoesNotExist:pass
	J={_A:1,_C:E};K=json.dumps(J);return HttpResponse(K)