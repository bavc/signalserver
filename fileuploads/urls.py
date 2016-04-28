from django.conf.urls import url

from . import views

app_name = 'fileuploads'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<filename_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<filename_id>[0-9]+)/results/$', views.results, name='results'),
    url(r'^list/$', views.list, name='list'),
    url(r'^list/videostorage/(?P<video_videofile_name>[\w.]{0,256})$',
        views.show_video, name='show_video')
]
