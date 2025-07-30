import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_6b7c630ead.sparta_598720ddc6 import qube_12ef2ba9ab as qube_12ef2ba9ab
from project.sparta_6b7c630ead.sparta_932dd1554c.qube_06e5cb3c06 import sparta_9080b99843
@csrf_exempt
@sparta_9080b99843
def sparta_e7f0d9c961(request):G='api_func';F='key';E='utf-8';A=request;C=A.body.decode(E);C=A.POST.get(F);D=A.body.decode(E);D=A.POST.get(G);B=dict();B[F]=C;B[G]=D;H=qube_12ef2ba9ab.sparta_e7f0d9c961(B,A.user);I=json.dumps(H);return HttpResponse(I)