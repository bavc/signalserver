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
from groups import views

urlpatterns = [
    url(r'^$', views.show_graphs, name='show_graphs'),
    url(r'^fileuploads/', include('fileuploads.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^operations/', include('operations.urls')),
    url(r'^groups/', include('groups.urls')),
] + static(settings.BOWER_COMPONENTS_URL,
           document_root=settings.BOWER_COMPONENTS_ROOT)
