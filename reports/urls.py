from django.conf.urls import url

from . import views

app_name = 'reports'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^create_report/$', views.create_report,
        name='create_report'),
    url(r'^rename/$', views.rename, name='rename'),
    url(r'^delete_report/(?P<report_name>[\w.]{0,256})$',
        views.delete_report, name='delete_report'),
    url(r'^show/(?P<report_name>[\w.]{0,256})$',
        views.show, name='show'),
    url(r'^show/add_rule/(?P<report_name>[\w.]{0,256})$', views.add_rule,
        name='add_rule'),
    url(r'^show/delete_rule/(?P<rule_id>[0-9]+)/(?P<rule_name>[\w.]{0,256})$',
        views.delete_rule, name='delete_rule'),

    #url(r'^get_graph/$', views.get_graph, name='get_graph'),
    #url(r'^delete_output/(?P<output_pk>[\w.]{0,256})$',
    #    views.delete_output, name='delete_output'),
]
