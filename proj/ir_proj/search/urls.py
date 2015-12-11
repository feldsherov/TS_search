from django.conf.urls import url

from . import views

__author__ = 'feldsherov'

urlpatterns = [
    url('^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^hello/$', views.hello, name='hello'),
]
