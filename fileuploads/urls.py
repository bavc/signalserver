from django.conf.urls import url

from . import views

app_name = 'fileuploads'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<filename_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<filename_id>[0-9]+)/results/$', views.results, name='results'),
    url(r'^list/$', views.list, name='list'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^process/$', views.process, name='process'),
    url(r'^status/$', views.status, name='status'),
    url(r'^search/$', views.search, name='search'),
    url(r'^edit_group/(?P<group_name>[\w.]{0,256})$', views.edit_group, name='edit_group'),
    url(r'^update_group/$', views.update_group, name='update_group'),
    url(r'^save_group/$', views.save_group, name='save_group'),
    url(r'^search_group/$', views.search_group, name='search_group'),
    url(r'^group_process/$', views.group_process, name='group_process'),
    url(r'^group_result/$', views.group_result, name='group_result'),
    url(r'^result_graph/$', views.result_graph, name='result_graph'),
    url(r'^bulk_process/$', views.bulk_process, name='bulk_process'),
    url(r'^api/get_graph_data/$', views.get_graph_data, name='get_graph_data'),
    url(r'^show/(?P<video_videofile_name>[\w.]{0,256})$',
        views.show_video, name='show_video'),
    url(r'^list/show/(?P<video_videofile_name>[\w.]{0,256})$',
        views.show_video, name='show_video'),
    url(r'^list/show/result/(?P<video_videofile_name>[\w.]{0,256})$',
        views.show_result, name='show_result'),
    url(r'^list/delete-video/(?P<video_videofile_name>[\w.]{0,256})$',
        views.delete_video, name='delete_video'),
    url(r'^remove-file/(?P<file_name>[\w.]{0,256})/(?P<group_name>[\w.]{0,256})$',
        views.remove_file, name='remove_file'),
]
