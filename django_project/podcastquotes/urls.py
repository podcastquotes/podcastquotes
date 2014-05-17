from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from quotes_app.models import Podcast, Episode, Quote
from quotes_app.views import HomeQuoteListView
from quotes_app.views import PodcastQuoteListView, PodcastCreateView
from quotes_app.views import EpisodeQuoteListView
from quotes_app.views import quote_create
from quotes_app.views import VoteFormView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
 
    url(r'^$', HomeQuoteListView.as_view(), name='home'),
 
     
    url(r'^admin/', include(admin.site.urls)),
 
    url(r'^(?P<query_filter>\w+)/$', HomeQuoteListView.as_view(), name='home_quote_list'),
 
    url(r'^podcasts/(?P<pk>\d+)/(?P<query_filter>\w+)/$', PodcastQuoteListView.as_view(), name='podcast_quote_list'),
    
    url(r'^episodes/(?P<pk>\d+)/(?P<query_filter>\w+)/$', EpisodeQuoteListView.as_view(), name='episode_quote_list'),
    
    url(r'^podcasts/create/$', 
        PodcastCreateView.as_view(
            model=Podcast,
            template_name='podcast_create.html',
            context_object_name='podcast'),
        name='podcast_create',),

    url(r'^podcasts/(?P<podcast_id>\d+)/update_feed/$', 
        'quotes_app.views.update_feed', 
        name='update_feed',),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/quotes/(?P<quote_id>\d+)/$', 'quotes_app.views.quote', name='quote'),
    
    url(r'^quotes/create/', 'quotes_app.views.quote_create',
        name='quote_create',),
    
    url(r'^quotes/vote/$', login_required(VoteFormView.as_view()), name="quote_vote"),
   
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout_then_login'),
    
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
