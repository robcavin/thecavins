from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    url(r'^$','thecavins.views.homepage'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )