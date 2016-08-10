from django.conf.urls import url

from . import views

app_name = 'operations'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /operations/5/results/
    url(r'^(?P<operation_id>[0-9]+)/results/$', views.results, name='results'),
   url(r'^rename/$', views.rename, name='rename'),
    url(r'^delete-config/(?P<config_name>[\w.]{0,256})$',
        views.delete_config, name='delete_config'),
    url(r'^show/delete-op/(?P<op_id>[0-9]+)/(?P<config_name>[\w.]{0,256})$',
        views.delete_op, name='delete_op'),
    url(r'^show/(?P<config_name>[\w.]{0,256})$',
        views.show, name='show'),
]
