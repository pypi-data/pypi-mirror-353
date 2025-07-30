from django.contrib import admin
from django.urls import path
from django.urls import path,re_path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import debug_toolbar
from.url_base import get_url_patterns as get_url_patterns_base
from.url_spartaqube import get_url_patterns as get_url_patterns_spartaqube
handler404='project.sparta_9161393429.sparta_c6df90ec8c.qube_21c86e4144.sparta_a024595252'
handler500='project.sparta_9161393429.sparta_c6df90ec8c.qube_21c86e4144.sparta_435ab2dd79'
handler403='project.sparta_9161393429.sparta_c6df90ec8c.qube_21c86e4144.sparta_cb4411eec8'
handler400='project.sparta_9161393429.sparta_c6df90ec8c.qube_21c86e4144.sparta_e6d9e99cfb'
urlpatterns=get_url_patterns_base()+get_url_patterns_spartaqube()
if settings.B_TOOLBAR:urlpatterns+=[path('__debug__/',include(debug_toolbar.urls))]