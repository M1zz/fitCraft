from django.conf.urls import url
from . import views

urlpatterns = [
    # login logout basic
    url(r'^$', views.home, name='home'),
    url(r'^home$', views.home, name='home'),
    url(r'^register$', views.register, name='register'),
    url(r'^register_success$', views.register_success, name='register_success'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^blog/loggedin$', views.loggedin, name='loggedin'),
    url(r'^blog/invalid$', views.invalid_login, name='invalid_login'),
    url(r'^auth$', views.auth_view, name='auth_view'),
    
    # fitcraft
    url(r'^fitcraft$', views.fitcraft, name='fitcraft'),
    url(r'^fitcraft/item', views.item, name='item'),
    url(r'^fitcraft/sync', views.sync, name='sync'),
    url(r'^fitcraft/howToPlay', views.howToPlay, name='howToPlay'),
    url(r'^fitcraft/note', views.note, name='note'),

    # board
    url(r'^fit_board$', views.fit_board, name='fit_board'),
    url(r'^show_write_form$', views.show_write_form, name='board_write'),
    url(r'^DoWriteBoard$', views.DoWriteBoard, name='DoWriteBoard'),
    url(r'^listSpecificPageWork$', views.listSpecificPageWork,name ='listSpecificPageWork'),
    url(r'^viewWork', views.viewWork),
]
