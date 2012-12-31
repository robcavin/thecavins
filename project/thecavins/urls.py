from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'thecavins.views.root'),
    url(r'^about/$','thecavins.views.about'),
    url(r'^account/$','thecavins.views.account'),
   
    url(r'^stream/(?P<stream_id>\d+?)/post/?$','thecavins.views.post_to_stream'),
    url(r'^post/(?P<post_id>.*?)/comment/?$','thecavins.views.comment_to_post'),

    url(r'^stream/(?P<path>.*?)/?$','thecavins.views.stream'),
    
    url(r'^image/upload/$','thecavins.views.image_upload'),
    url(r'^image/(?P<image_id>\d+)/crop/$','thecavins.views.image_crop'),

    url(r'^login/$', 'django.contrib.auth.views.login'),    # registration/login.html
    url(r'^permission_login/$', 'django.contrib.auth.views.login',{'template_name':'registration/permission_login.html'}),    # registration/login.html
    url(r'^logout/$', 'django.contrib.auth.views.logout'),  # registration/logged_out.html
    url(r'^password_change/$', 'django.contrib.auth.views.password_change'),  # registration/password_change_form.html
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done'), # registration/password_done.html
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset'), # registration/password_reset_form.html, email from registration/password_reset_email.html, ..reset_subject.html
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done'), # registration/password_reset_done.html
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'django.contrib.auth.views.password_reset_confirm'), # registration/password_reset_confirm.html
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'), # registration/password_reset_complete.html   
 
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )