from django.conf.urls import url

from . import views

app_name = 'groups'

urlpatterns = [
    url(r'^edit_group/(?P<group_id>[0-9]+)$', views.edit_group,
        name='edit_group'),
    url(r'^update_group/$', views.update_group, name='update_group'),
    url(r'^rename/$', views.rename_group, name='rename'),
    url(r'^delete_group/(?P<group_id>[0-9]+)$',
        views.delete_group, name='delete_group'),
    url(r'^delete_group_and_files/(?P<group_id>[0-9]+)$',
        views.delete_group_and_files, name='delete_group_and_files'),
    url(r'^save_group/$', views.save_group, name='save_group'),
    url(r'^search_group/$', views.search_group, name='search_group'),
    url(r'^group_process/$', views.group_process, name='group_process'),
    url(r'^group_process_status/$', views.group_process_status,
        name='group_process_status'),
    url(r'^result_graph/$', views.result_graph, name='result_graph'),
    url(r'^api/get_graph_data/$', views.get_graph_data, name='get_graph_data'),
    url(r'^api/get_group_process_status/$', views.get_group_process_status,
        name='get_group_process_status'),
    url(r'^remove-file/(?P<file_name>[\w.]{0,256})/(?P<group_id>[0-9]+)$',
        views.remove_file, name='remove_file'),
    url(r'^delete_group_result/(?P<process_id>[0-9]+)$',
        views.delete_group_result, name='delete_group_result'),
    url(r'^create_group/$', views.GroupCreateView.as_view()),
    url(r'^add_file/$', views.GroupAddFileView.as_view()),
]
