from django.conf.urls import url

from . import views

app_name = 'groups'

urlpatterns = [
    url(r'^edit_group/(?P<group_name>[\w.]{0,256})$', views.edit_group,
        name='edit_group'),
    url(r'^update_group/$', views.update_group, name='update_group'),
    url(r'^rename/$', views.rename_group, name='rename'),
    url(r'^delete_group/(?P<group_name>[\w.]{0,256})$',
        views.delete_group, name='delete_group'),
    url(r'^save_group/$', views.save_group, name='save_group'),
    url(r'^search_group/$', views.search_group, name='search_group'),
    url(r'^group_process/$', views.group_process, name='group_process'),
    url(r'^result_graph/$', views.result_graph, name='result_graph'),
    url(r'^api/get_graph_data/$', views.get_graph_data, name='get_graph_data'),
    url(r'^remove-file/(?P<file_name>[\w.]{0,256})/(?P<group_name>[\w.]{0,256})$',
        views.remove_file, name='remove_file'),
]
