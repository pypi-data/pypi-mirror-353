_A='jsonData'
import json,inspect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from project.sparta_6b7c630ead.sparta_47aacac1bb import qube_a0ea37d6c9 as qube_a0ea37d6c9
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_9080b99843
def sparta_86cbebb547(request):A={'res':1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
@sparta_9080b99843
def sparta_a209f1bd41(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a0ea37d6c9.sparta_a209f1bd41(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_6d54219445(request):
	C='userObj';B=request;D=json.loads(B.body);E=json.loads(D[_A]);F=B.user;A=qube_a0ea37d6c9.sparta_6d54219445(E,F)
	if A['res']==1:
		if C in list(A.keys()):login(B,A[C]);A.pop(C,None)
	G=json.dumps(A);return HttpResponse(G)
@csrf_exempt
@sparta_9080b99843
def sparta_ee3c24a33b(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=A.user;E=qube_a0ea37d6c9.sparta_ee3c24a33b(C,D);F=json.dumps(E);return HttpResponse(F)
@csrf_exempt
@sparta_9080b99843
def sparta_09c6e22969(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a0ea37d6c9.sparta_09c6e22969(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_e671291706(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a0ea37d6c9.sparta_e671291706(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_cc3d243797(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a0ea37d6c9.sparta_cc3d243797(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_8ca84382dd(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_a0ea37d6c9.token_reset_password_worker(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
@sparta_9080b99843
def sparta_4b39b107b3(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a0ea37d6c9.network_master_reset_password(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_80941ad394(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_a0ea37d6c9.sparta_80941ad394(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
def sparta_b8a5855064(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_a0ea37d6c9.sparta_b8a5855064(A,C);E=json.dumps(D);return HttpResponse(E)