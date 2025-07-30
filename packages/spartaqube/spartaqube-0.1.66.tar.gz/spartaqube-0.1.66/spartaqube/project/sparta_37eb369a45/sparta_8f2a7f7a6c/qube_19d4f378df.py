_I='error.txt'
_H='zipName'
_G='utf-8'
_F='attachment; filename={0}'
_E='appId'
_D='res'
_C='Content-Disposition'
_B='projectPath'
_A='jsonData'
import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_6b7c630ead.sparta_2bd3001010 import qube_16967e2df7 as qube_16967e2df7
from project.sparta_6b7c630ead.sparta_2bd3001010 import qube_64a88f3431 as qube_64a88f3431
from project.sparta_6b7c630ead.sparta_d1ec1080b8 import qube_538e75a6b0 as qube_538e75a6b0
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_9080b99843
@csrf_exempt
@sparta_9080b99843
def sparta_eedb889aff(request):
	D='files[]';A=request;E=A.POST.dict();B=A.FILES
	if D in B:C=qube_16967e2df7.sparta_1f4d9ef47c(E,A.user,B[D])
	else:C={_D:1}
	F=json.dumps(C);return HttpResponse(F)
@csrf_exempt
@sparta_9080b99843
def sparta_8e959f41ab(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_16967e2df7.sparta_e2701edae8(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_330df53ef4(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_16967e2df7.sparta_473faab195(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_9165831cc9(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_16967e2df7.sparta_74a0f4f5d5(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_596756d6cd(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_64a88f3431.sparta_e9a7fef488(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_d32e112b97(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_16967e2df7.sparta_4b69607b51(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_62f5419545(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_16967e2df7.sparta_ca253580e7(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_373414ba06(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_16967e2df7.sparta_4ca1a6ce6f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_99efe64be8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_16967e2df7.sparta_82c9941c85(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_371d636958(request):
	F='filePath';E='fileName';A=request;B=A.GET[E];G=A.GET[F];H=A.GET[_B];I=A.GET[_E];J={E:B,F:G,_E:I,_B:base64.b64decode(H).decode(_G)};C=qube_16967e2df7.sparta_dcfb1ef135(J,A.user)
	if C[_D]==1:
		try:
			with open(C['fullPath'],'rb')as K:D=HttpResponse(K.read(),content_type='application/force-download');D[_C]='attachment; filename='+str(B);return D
		except Exception as L:pass
	raise Http404
@csrf_exempt
@sparta_9080b99843
def sparta_3aeaef2c49(request):
	E='folderName';B=request;F=B.GET[_B];D=B.GET[E];G={_B:base64.b64decode(F).decode(_G),E:D};C=qube_16967e2df7.sparta_94f7c034fa(G,B.user)
	if C[_D]==1:H=C['zip'];I=C[_H];A=HttpResponse();A.write(H.getvalue());A[_C]=_F.format(f"{I}.zip")
	else:A=HttpResponse();J=f"Could not download the folder {D}, please try again";K=_I;A.write(J);A[_C]=_F.format(K)
	return A
@csrf_exempt
@sparta_9080b99843
def sparta_f125078727(request):
	B=request;D=B.GET[_E];E=B.GET[_B];F={_E:D,_B:base64.b64decode(E).decode(_G)};C=qube_16967e2df7.sparta_7655cbb739(F,B.user)
	if C[_D]==1:G=C['zip'];H=C[_H];A=HttpResponse();A.write(G.getvalue());A[_C]=_F.format(f"{H}.zip")
	else:A=HttpResponse();I='Could not download the application, please try again';J=_I;A.write(I);A[_C]=_F.format(J)
	return A