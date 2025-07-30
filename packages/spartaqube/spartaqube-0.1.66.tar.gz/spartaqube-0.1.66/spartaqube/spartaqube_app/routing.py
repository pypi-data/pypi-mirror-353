import pkg_resources
from channels.routing import ProtocolTypeRouter,URLRouter
from django.urls import re_path as url
from django.conf import settings
from project.sparta_25bf7ff8a2.sparta_717dafe2ed import qube_838a16f200,qube_ff48621cde,qube_0ea6b395e8,qube_8d939539eb,qube_03f5cc7ce9,qube_63b68513d8,qube_fc3d9763d5,qube_914104f37c,qube_b392e2b0e5
from channels.auth import AuthMiddlewareStack
import channels
channels_ver=pkg_resources.get_distribution('channels').version
channels_major=int(channels_ver.split('.')[0])
def sparta_0ec2abe76e(this_class):
	A=this_class
	if channels_major<=2:return A
	else:return A.as_asgi()
urlpatterns=[url('ws/statusWS',sparta_0ec2abe76e(qube_838a16f200.StatusWS)),url('ws/notebookWS',sparta_0ec2abe76e(qube_ff48621cde.NotebookWS)),url('ws/wssConnectorWS',sparta_0ec2abe76e(qube_0ea6b395e8.WssConnectorWS)),url('ws/pipInstallWS',sparta_0ec2abe76e(qube_8d939539eb.PipInstallWS)),url('ws/gitNotebookWS',sparta_0ec2abe76e(qube_03f5cc7ce9.GitNotebookWS)),url('ws/xtermGitWS',sparta_0ec2abe76e(qube_63b68513d8.XtermGitWS)),url('ws/hotReloadLivePreviewWS',sparta_0ec2abe76e(qube_fc3d9763d5.HotReloadLivePreviewWS)),url('ws/apiWebserviceWS',sparta_0ec2abe76e(qube_914104f37c.ApiWebserviceWS)),url('ws/apiWebsocketWS',sparta_0ec2abe76e(qube_b392e2b0e5.ApiWebsocketWS))]
application=ProtocolTypeRouter({'websocket':AuthMiddlewareStack(URLRouter(urlpatterns))})
for thisUrlPattern in urlpatterns:
	try:
		if len(settings.DAPHNE_PREFIX)>0:thisUrlPattern.pattern._regex='^'+settings.DAPHNE_PREFIX+'/'+thisUrlPattern.pattern._regex
	except Exception as e:print(e)