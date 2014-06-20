from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^home$', RedirectView.as_view(url='mymovements'), name='home'),
    url(r'^mymovements$', 'render.views.mymovements', name='mymovements'),
    url(r'^', RedirectView.as_view(url='mymovements')),
)
