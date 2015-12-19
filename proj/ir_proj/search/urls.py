from django.conf.urls import url

import views

__author__ = 'feldsherov'

urlpatterns = [
    url('^$', views.index, name='index'),
    url(r'^search/$', views.search, name='search'),
    url(r'^searchJSON/$', views.searchJSON, name='searchJSON'),
    url(r'^hello/$', views.hello, name='hello'),
]
