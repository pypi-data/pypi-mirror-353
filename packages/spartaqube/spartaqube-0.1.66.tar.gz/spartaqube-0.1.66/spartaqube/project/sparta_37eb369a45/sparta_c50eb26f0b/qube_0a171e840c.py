_E='Content-Disposition'
_D='utf-8'
_C='dashboardId'
_B='projectPath'
_A='jsonData'
import os,json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_6b7c630ead.sparta_aceca65940 import qube_4912c09cb6 as qube_4912c09cb6
from project.sparta_6b7c630ead.sparta_aceca65940 import qube_8f5bff304e as qube_8f5bff304e
from project.sparta_6b7c630ead.sparta_6d329e2f11 import qube_2b15813649 as qube_2b15813649
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_9080b99843,sparta_5cbc69940a
@csrf_exempt
def sparta_67b3a19337(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4912c09cb6.sparta_67b3a19337(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_ba6cfe8d47(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4912c09cb6.sparta_ba6cfe8d47(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_480e076867(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4912c09cb6.sparta_480e076867(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_9450ea2a61(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4912c09cb6.sparta_9450ea2a61(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_8829fbc1d0(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4912c09cb6.sparta_8829fbc1d0(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_3dcc69ad9c(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4912c09cb6.sparta_3dcc69ad9c(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_f047c1580f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4912c09cb6.sparta_f047c1580f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_a338970f0b(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4912c09cb6.sparta_a338970f0b(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_17d81a1d22(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4912c09cb6.sparta_17d81a1d22(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_d40a86d9a7(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4912c09cb6.sparta_d40a86d9a7(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_e620bf213a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4912c09cb6.dashboard_project_explorer_delete_multiple_resources(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
def sparta_1cc9c79627(request):A=request;B=A.POST.dict();C=A.FILES;D=qube_4912c09cb6.sparta_1cc9c79627(B,A.user,C['files[]']);E=json.dumps(D);return HttpResponse(E)
def sparta_16f9a3c4ef(path):
	A=path;A=os.path.normpath(A)
	if os.path.isfile(A):A=os.path.dirname(A)
	return os.path.basename(A)
def sparta_cf17a1f005(path):A=path;A=os.path.normpath(A);return os.path.basename(A)
@csrf_exempt
@sparta_9080b99843
def sparta_a68bed755b(request):
	E='pathResource';A=request;B=A.GET[E];B=base64.b64decode(B).decode(_D);F=A.GET[_B];G=A.GET[_C];H=sparta_cf17a1f005(B);I={E:B,_C:G,_B:base64.b64decode(F).decode(_D)};C=qube_4912c09cb6.sparta_dcfb1ef135(I,A.user)
	if C['res']==1:
		try:
			with open(C['fullPath'],'rb')as J:D=HttpResponse(J.read(),content_type='application/force-download');D[_E]='attachment; filename='+str(H);return D
		except Exception as K:pass
	raise Http404
@csrf_exempt
@sparta_9080b99843
def sparta_6d952202b1(request):
	D='attachment; filename={0}';B=request;E=B.GET[_C];F=B.GET[_B];G={_C:E,_B:base64.b64decode(F).decode(_D)};C=qube_4912c09cb6.sparta_7655cbb739(G,B.user)
	if C['res']==1:H=C['zip'];I=C['zipName'];A=HttpResponse();A.write(H.getvalue());A[_E]=D.format(f"{I}.zip")
	else:A=HttpResponse();J='Could not download the application, please try again';K='error.txt';A.write(J);A[_E]=D.format(K)
	return A
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_1c640a449f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_1c640a449f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_d6d12313ae(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_d6d12313ae(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_0827fadfcc(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_0827fadfcc(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_71ee68ef24(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_71ee68ef24(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_141eb632fb(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_141eb632fb(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_40d93ba17d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_40d93ba17d(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_6f08884a9f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_6f08884a9f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_3c5cc8f511(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_3c5cc8f511(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_a65929b4e6(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_a65929b4e6(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_c820e0f614(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_c820e0f614(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_7fb588a1f8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_7fb588a1f8(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_f995be22ca(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_f995be22ca(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_b21d863ad8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_b21d863ad8(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_9080b99843
@sparta_5cbc69940a
def sparta_67a7172edf(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8f5bff304e.sparta_67a7172edf(C,A.user);E=json.dumps(D);return HttpResponse(E)