from django.conf.urls import url

from . import views


urlpatterns = [
    # fitbit page
    url(r'^home/$', views.home, name='fitbit-home'),

    # OAuth authentication
    url(r'^login/$', views.login, name='fitbit-login'),
    url(r'^complete/$', views.complete, name='fitbit-complete'),
    url(r'^error/$', views.error, name='fitbit-error'),
    url(r'^exist/$', views.exist, name='fitbit-exist'),
    url(r'^logout/$', views.logout, name='fitbit-logout'),

    # Subscriber callback for near realtime updates
    url(r'^update/$', views.update, name='fitbit-update'),

    # Fitbit data and visualization
    url(r'^get_data/(?P<category>[\w]+)/(?P<resource>[/\w]+)/$',
        views.get_data, name='fitbit-data'),
    url(r'^get_steps/$', views.get_steps, name='fitbit-steps'),
    url(r'^get_today_steps/$', views.get_today_steps, name='fitbit-today-steps'),
    url(r'^graph_sleep/$', views.graph_sleep, name='sleep-graph'),
    url(r'^graph_step/$', views.graph_step, name='sleep-step'),
    url(r'^status/$', views.status, name='status'),

]
