from django.conf.urls import url
from . import views

urlpatterns = [
    #url(r'^$', views.post_list, name='post_list'),
    url(r'^$', views.home, name='home'),
    url(r'^home$', views.home, name='home'),
    url(r'^register$', views.register, name='register'),
    url(r'^register_success$', views.register_success, name='register_success'),
    url(r'^login$', views.login, name='login'),
    url(r'^auth$', views.auth_view, name='auth_view'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^blog/loggedin$', views.loggedin, name='loggedin'),
    url(r'^blog/invalid$', views.invalid_login, name='invalid_login'),
]
