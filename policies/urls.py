from django.conf.urls import url

from . import views

app_name = 'policies'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<operation_id>[0-9]+)/results/$', views.results, name='results'),
    url(r'^rename/$', views.rename, name='rename'),
    url(r'^delete_policy/(?P<policy_name>[\w.]{0,256})$',
        views.delete_policy, name='delete_policy'),
    url(r'^show/delete_rule/(?P<op_id>[0-9]+)/(?P<policy_name>[\w.]{0,256})$',
        views.delete_rule, name='delete_rule'),
    url(r'^show/(?P<policy_name>[\w.]{0,256})$',
        views.show, name='show'),
]
