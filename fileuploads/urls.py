from django.conf.urls import url, include

from . import views

app_name = 'fileuploads'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<filename_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<filename_id>[0-9]+)/results/$', views.results, name='results'),
    url(r'^list/$', views.list_file, name='list'),
    url(r'^about/$', views.about, name='about'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^process/$', views.process, name='process'),
    url(r'^status/$', views.status, name='status'),
    url(r'^search/$', views.search, name='search'),
    url(r'^show/(?P<video_videofile_name>[\w.]{0,256})$',
        views.show_video, name='show_video'),
    url(r'^list/show/(?P<video_videofile_name>[\w.]{0,256})$',
        views.show_video, name='show_video'),
    url(r'^list/show/result/(?P<video_videofile_name>[\w.]{0,256})$',
        views.show_result, name='show_result'),
    url(r'^delete-video/(?P<video_videofile_name>[\w.]{0,256})$',
        views.delete_video, name='delete_video'),
    url(r'^upload/(?P<filename>[^/]+)$', views.FileUploadView.as_view()),
    url(r'^check_exist/(?P<filename>[^/]+)$', views.FileUploadView.as_view()),
    url(r'^delete_file/$', views.FileDeleteView.as_view()),
]
