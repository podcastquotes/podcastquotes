from django.conf.urls import patterns, include, url
from quotes_app.models import Podcast, Episode, Quote
from quotes_app.views import home
from quotes_app.views import PodcastDetailView, PodcastCreateView
from quotes_app.views import EpisodeDetailView
from quotes_app.views import quote_create
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
 
    url(r'^$', 'quotes_app.views.home', name='home'),
    
    url(r'^podcasts/create/$', 
        PodcastCreateView.as_view(
            model=Podcast,
            template_name='podcast_create.html',
            context_object_name='podcast'),
        name='podcast_create',),
    
    url(r'^podcasts/(?P<pk>\d+)/$', 
        PodcastDetailView.as_view(
            model=Podcast,
            template_name='podcast_detail.html',
            context_object_name='podcast'),
        name='podcast_detail',),

    url(r'^podcasts/(?P<podcast_id>\d+)/update_feed/$', 
        'quotes_app.views.update_feed', 
        name='update_feed',),
        
    url(r'^episodes/(?P<pk>\d+)/$', 
        EpisodeDetailView.as_view(
            model=Episode,
            template_name='episode_detail.html',
            context_object_name='episode'),
        name='episode_detail',),
    
    url(r'^quotes/create/', 'quotes_app.views.quote_create',
        name='quote_create',),
        
    url(r'^quotes/vote/(?P<quote_id>\d+)/(?P<vote_type_id>-?\d+)/$', 'quotes_app.views.vote', name='quote_vote'),
   
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout_then_login'),
    
    url(r'^admin/', include(admin.site.urls)),
    
    # Allauth urls
    (r'^accounts/', include('allauth.urls')),

)

# Serve static
from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
   )
