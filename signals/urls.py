from django.conf.urls import url

from . import views

app_name = 'signals'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^process/$', views.process, name='process'),
    url(r'^get_graph/$', views.get_graph, name='get_graph'),
    url(r'^api/get_graph_data/$', views.get_graph_data, name='get_graph_data'),
]
