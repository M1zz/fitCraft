from django.conf.urls import url
from . import views

urlpatterns = [
    # Example:
    url(r'^$', views.index),
    url(r'^oauth2callback', views.auth_return),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
                        {'template_name': 'plus/login.html'}),

    # (r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root': os.path.join(os.path.dirname(__file__), 'static')}),
   
    # Googlefit-xiaomi
    #url(r'^xiaomi$', views.xiaomi),
    url(r'^googlefit$', views.googlefit),
]
