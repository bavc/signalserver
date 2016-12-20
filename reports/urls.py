from django.conf.urls import url

from . import views

app_name = 'reports'
urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
]
