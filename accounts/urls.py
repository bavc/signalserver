from django.conf.urls import url, include

from . import views

app_name = 'accounts'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^update/$', views.update, name='update'),
    url(r'^register/$', views.register, name='register'),
]
