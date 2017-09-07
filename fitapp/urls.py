from django.conf.urls import url

from . import views


urlpatterns = [
    # fitness health page
    url(r'^home/$', views.home, name='fitness-home'),

    # google fit
    url(r'^howto$', views.howto, name='howto'),

    # OAuth authentication
    url(r'^login/$', views.login, name='fitbit-login'),
    url(r'^complete/$', views.complete, name='fitbit-complete'),
    url(r'^error/$', views.error, name='fitbit-error'),
    url(r'^exist/$', views.exist, name='fitbit-exist'),
    url(r'^logout/$', views.logout, name='fitbit-logout'),

    # Subscriber callback for near realtime updates
    url(r'^update/$', views.update, name='fitbit-update'),

    # Fitbit page
    url(r'^fitbit/$', views.fitbit, name='fitbit-home'),
    url(r'^get_data/(?P<category>[\w]+)/(?P<resource>[/\w]+)/$',views.get_data, name='fitbit-data'),
    url(r'^get_steps/$', views.get_steps, name='fitbit-steps'),
    url(r'^get_today_steps/$', views.get_today_steps, name='fitbit-today-steps'),
    url(r'^all_get_today_steps/$', views.all_get_today_steps, name='all-fitbit-today-steps'),
    url(r'^graph_sleep/$', views.graph_sleep, name='sleep-graph'),
    url(r'^graph_step/$', views.graph_step, name='sleep-step'),
    url(r'^status/$', views.status, name='status'),

    # google fit
    url(r'^googlefit$', views.googlefit, name='googlefit'),    

    # xiaomi
    url(r'^xiaomi$', views.xiaomi, name='xiaomi'),

    url(r'^worklog$', views.worklog, name='worklog'),

    # fitcraft
    #url(r'^fitpoint/(?P<user_id>[\w]+)/(?P<point>[/\w]+)/$',
    #    views.get_point, name='fitpoint'),    
    url(r'^fitpoint/(?P<user_id>[\w]+)/(?P<password>[\w]+)/(?P<point>[\w]+)', views.get_point, name='fitpoint'),
    url(r'^fitSleep/(?P<user_id>[\w]+)/(?P<password>[\w]+)/(?P<point>[\w]+)', views.get_sleep, name='fitSleep'),
    url(r'^fitHeart/(?P<user_id>[\w]+)/(?P<password>[\w]+)/(?P<point>[\w]+)', views.get_heart, name='fitHeart'),
]
