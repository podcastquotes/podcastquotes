from django.conf.urls import patterns, include, url
from quotes_app.models import Podcast, Episode, Quote
from quotes_app.views import home_top
from quotes_app.views import PodcastDetailView, PodcastCreateView
from quotes_app.views import EpisodeDetailView
from quotes_app.views import quote_create
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
 
    url(r'^hot/$', 'quotes_app.views.home_hot', name='home_hot'),
    
    url(r'^not/$', 'quotes_app.views.home_not', name='home_not'),
    
    url(r'^controversial/$', 'quotes_app.views.home_controversial', name='home_controversial'),
    
    url(r'^new/$', 'quotes_app.views.home_new', name='home_new'),
    
    url(r'^$', 'quotes_app.views.home_top', name='home_top'),
    
    url(r'^bottom/$', 'quotes_app.views.home_bottom', name='home_bottom'),
    
    url(r'^mainstream/$', 'quotes_app.views.home_mainstream', name='home_mainstream'),
    
    url(r'^underground/$', 'quotes_app.views.home_underground', name='home_underground'),
    
    url(r'^chronological/$', 'quotes_app.views.home_chronological', name='home_chronological'),
    
    url(r'^ghosts/$', 'quotes_app.views.home_ghosts', name='home_ghosts'),
    
    url(r'^birthdays/$', 'quotes_app.views.home_birthdays', name='home_birthdays'),
    
    url(r'^podcasts/create/$', 
        PodcastCreateView.as_view(
            model=Podcast,
            template_name='podcast_create.html',
            context_object_name='podcast'),
        name='podcast_create',),
    
    url(r'^podcasts/(?P<pk>\d+)/$', 
        PodcastDetailView.as_view(
            model=Podcast,
            template_name='podcast_top.html',
            context_object_name='podcast'),
        name='podcast_top',),

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
