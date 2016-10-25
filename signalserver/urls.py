"""signalserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from fileuploads.views import list_file
from fileuploads.views import register
from fileuploads.views import custom_login
from fileuploads.views import custom_logout
from fileuploads.forms import UserForm
from django.contrib.auth import views


urlpatterns = [
    url(r'^$', list_file, name='list'),
    url(r'^register/', register, name='register'),
    url(r'^redirect', custom_login,
        name='redirect'),
    url(r'^logout', custom_logout, name='logout'),
    url(r'^password_reset/$', views.password_reset,
        {'template_name': 'registration/password_reset.html',
         'from_email': 'bavc.signalserver@gmail.com'},
        name='password_reset'),
    url(r'^password_reset/done/$', views.password_reset_done,
        {'template_name': 'registration/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm,
        {'template_name': 'registration/reset.html'},
        name='password_reset_confirm'),
    url(r'^reset/done/$',
        views.password_reset_complete,
        {'template_name': 'registration/password_reset_complete.html'},
        name='password_reset_complete'),
    url(r'^fileuploads/', include('fileuploads.urls')),
    url('^', include('django.contrib.auth.urls')),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^policy/', include('policies.urls')),
    url(r'^groups/', include('groups.urls')),
    url(r'^signals/', include('signals.urls')),
    url(r'^reports/', include('reports.urls')),
] + static(settings.BOWER_COMPONENTS_URL,
           document_root=settings.BOWER_COMPONENTS_ROOT)
