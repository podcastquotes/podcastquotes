from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import RedirectView
from quotes_app.models import Podcast, Episode, Quote, UserProfile
from quotes_app.views.home import HomeQuoteListView
from quotes_app.views.podcast import PodcastQuoteListView, PodcastCreateView, PodcastUpdateView, PodcastDeleteView
from quotes_app.views.episode import EpisodeQuoteListView, EpisodeCreateView, EpisodeUpdateView, EpisodeDeleteView
from quotes_app.views.quote import quote_create, QuoteUpdateView, QuoteDeleteView
from quotes_app.views.user import UserQuoteListView, UserProfileUpdateView, UserProfileDeleteView
from quotes_app.views.rank import rank_all
from quotes_app.views.vote import VoteFormView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^people/(?P<slug>\w+)/$', UserQuoteListView.as_view(), name='user_quote_list_root'),
    
    url(r'^people/(?P<slug>\w+)/edit/$', UserProfileUpdateView.as_view(), name='user_update'),
    
    url(r'^people/(?P<slug>\w+)/delete/$', UserProfileDeleteView.as_view(), name='user_delete'),
    
    url(r'^people/(?P<slug>\w+)/(?P<query_filter>\w+)/$', UserQuoteListView.as_view(), name='user_quote_list'),
    
    url(r'^rerank/', 'quotes_app.views.rank.rank_all', name='rank_all_quotes'),
    
    url(r'^$', HomeQuoteListView.as_view(), name='home'),
 
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout_then_login'),
 
    url(r'^(?P<query_filter>\w+)/$', HomeQuoteListView.as_view(), name='home_quote_list'),
    
    url(r'^podcasts/(?P<pk>\d+)/$', PodcastQuoteListView.as_view(), name='podcast_quote_list_root'),
    
    url(r'^podcasts/(?P<pk>\d+)/edit/$', PodcastUpdateView.as_view(), name='podcast_update'),
    
    url(r'^podcasts/(?P<pk>\d+)/delete/$', PodcastDeleteView.as_view(), name='podcast_delete'),  
    
    url(r'^podcasts/(?P<pk>\d+)/(?P<query_filter>\w+)/$', PodcastQuoteListView.as_view(), name='podcast_quote_list'),
    
    url(r'^episodes/(?P<pk>\d+)/$', EpisodeQuoteListView.as_view(), name='episode_quote_list_root'),
    
    url(r'^episodes/create/$', EpisodeCreateView.as_view(), name='episode_create'),
    
    url(r'^episodes/(?P<pk>\d+)/edit/$', EpisodeUpdateView.as_view(), name='episode_update'),
    
    url(r'^episodes/(?P<pk>\d+)/delete/$', EpisodeDeleteView.as_view(), name='episode_delete'),  
    
    url(r'^episodes/(?P<pk>\d+)/(?P<query_filter>\w+)/$', EpisodeQuoteListView.as_view(), name='episode_quote_list'),
    
    url(r'^podcasts/create/$', 
        PodcastCreateView.as_view(
            model=Podcast,
            template_name='podcast_create.html',
            context_object_name='podcast'),
        name='podcast_create',),    

    url(r'^podcasts/(?P<podcast_id>\d+)/update_feed/$', 
        'quotes_app.views.podcast.update_feed', 
        name='update_feed',),
    
    url(r'^quotes/(?P<quote_id>\d+)/$', 'quotes_app.views.quote.quote', name='quote'),
    
    url(r'^quotes/(?P<pk>\d+)/edit/$', QuoteUpdateView.as_view(), name='quote_update'),
    
    url(r'^quotes/(?P<pk>\d+)/delete/$', QuoteDeleteView.as_view(), name='quote_delete'), 
    
    url(r'^quotes/create/', 'quotes_app.views.quote.quote_create',
        name='quote_create',),
    
    url(r'^quotes/vote/$', login_required(VoteFormView.as_view()), name="quote_vote"),
    
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
