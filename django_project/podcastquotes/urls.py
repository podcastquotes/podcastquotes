from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import RedirectView
from quotes_app.models import Podcast, Episode, Quote, UserProfile
from quotes_app.views.episode import EpisodeQuoteListView, EpisodeCreateView, EpisodeUpdateView, EpisodeDeleteView
from quotes_app.views.home import HomeEpisodeListView, HomeQuoteListView
from quotes_app.views.podcast import PodcastEpisodeListView, PodcastQuoteListView, PodcastCreateView, PodcastUpdateView, PodcastDeleteView
from quotes_app.views.quote import QuoteCreateView, QuoteUpdateView, QuoteDeleteView
from quotes_app.views.superuser_tools import NeedYouTubeLinks, PodcastEpisodeTitlePrint, create_full_episodes
from quotes_app.views.user import UserQuoteListView, UserProfileUpdateView, UserProfileDeleteView
from quotes_app.views.vote import VoteFormView


urlpatterns = patterns('',
    
    url(r'^about/$', 'quotes_app.views.pq.about_pq', name='about_pq'),
    
    url(r'^claim-your-page/$', 'quotes_app.views.pq.claim_page', name='claim_page'),
    
    url(r'^contact/$', 'quotes_app.views.pq.contact_pq', name='contact_pq'),
    
    url(r'^support-podverse/$', 'quotes_app.views.pq.support_pv', name='support_pv'),
    
    # this view helps mitch check for episodes which do not have a YouTube link for playing clips
    url(r'^need-youtube-links/$', NeedYouTubeLinks.as_view(), name='podcast_episode_title_print'),
    
    # this view checks if every episode with a youtube_url has a full episode clip,
    # if not, it creates one.
    url(r'^create-full-episodes/$', 'quotes_app.views.superuser_tools.create_full_episodes', name='create_full_episodes'),
    
    # this view helps Mitch check episodes in a podcast rss feed
    url(r'^podcasts/(?P<pk>\d+)/print-episodes/$', PodcastEpisodeTitlePrint.as_view(), name='podcast_episode_title_print'),
    
    url(r'^people/(?P<slug>\w+)/$', UserQuoteListView.as_view(), name='user_quote_list_root'),
    
    url(r'^people/(?P<slug>\w+)/edit/$', UserProfileUpdateView.as_view(), name='user_update'),
    
    url(r'^people/(?P<slug>\w+)/delete/$', UserProfileDeleteView.as_view(), name='user_delete'),
    
    url(r'^people/(?P<slug>\w+)/(?P<query_filter>\w+)/$', UserQuoteListView.as_view(), name='user_quote_list'),
        
    url(r'^$', HomeEpisodeListView.as_view(), name='home'),
    
    url(r'^episodes/$', HomeEpisodeListView.as_view(), name='home_episode_list'),
    
    url(r'^clips/$', HomeQuoteListView.as_view(), name='home_quote_list'),
    
    url(r'^clips/create/$', QuoteCreateView.as_view(), name='quote_create'),
    
    url(r'^clips/(?P<quote_id>\d+)/$', 'quotes_app.views.quote.quote', name='quote'),
    
    url(r'^quotes/(?P<quote_id>\d+)/$', 'quotes_app.views.quote.quote', name='quote_alternate'),
    
    url(r'^clips/(?P<pk>\d+)/edit/$', QuoteUpdateView.as_view(), name='quote_update'),
    
    url(r'^clips/(?P<pk>\d+)/delete/$', QuoteDeleteView.as_view(), name='quote_delete'), 
    
    url(r'^clips/vote/$', login_required(VoteFormView.as_view()), name="quote_vote"),
    
    url(r'^clips/(?P<query_filter>\w+)/$', HomeQuoteListView.as_view(), name='home_quote_list_filter'),

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout_then_login'),
    
    url(r'^podcasts/(?P<pk>\d+)/$', PodcastEpisodeListView.as_view(), name='podcast_episode_list_root'),
    
    url(r'^podcasts/(?P<pk>\d+)/edit/$', PodcastUpdateView.as_view(), name='podcast_update'),
    
    url(r'^podcasts/(?P<pk>\d+)/delete/$', PodcastDeleteView.as_view(), name='podcast_delete'),  
    
    url(r'^podcasts/create/$', 
        PodcastCreateView.as_view(
            model=Podcast,
            template_name='podcast_create.html',
            context_object_name='podcast'),
        name='podcast_create',),    

    url(r'^podcasts/(?P<podcast_id>\d+)/update_feed/$', 
        'quotes_app.views.podcast.update_feed', 
        name='update_feed',),
    
    url(r'^podcasts/(?P<pk>\d+)/clips/$', PodcastQuoteListView.as_view(), name='podcast_quote_list_root'),
    
    url(r'^podcasts/(?P<pk>\d+)/clips/(?P<query_filter>\w+)/$', PodcastQuoteListView.as_view(), name='podcast_quote_list_filter'),
    
    url(r'^podcasts/(?P<pk>\d+)/full-episodes/$', PodcastEpisodeListView.as_view(), name='podcast_episode_list_root'),
    
    url(r'^podcasts/(?P<pk>\d+)/full-episodes/(?P<query_filter>\w+)/$', PodcastEpisodeListView.as_view(), name='podcast_episode_list_filter'),
    
    url(r'^episodes/(?P<pk>\d+)/$', EpisodeQuoteListView.as_view(), name='episode_quote_list_root'),
    
    url(r'^episodes/(?P<query_filter>\w+)/$', HomeEpisodeListView.as_view(), name='home_episode_list_filter'),
    
    url(r'^episodes/create/$', EpisodeCreateView.as_view(), name='episode_create'),
    
    url(r'^episodes/(?P<pk>\d+)/edit/$', EpisodeUpdateView.as_view(), name='episode_update'),
    
    url(r'^episodes/(?P<pk>\d+)/delete/$', EpisodeDeleteView.as_view(), name='episode_delete'),  
    
    url(r'^episodes/(?P<pk>\d+)/(?P<query_filter>\w+)/$', EpisodeQuoteListView.as_view(), name='episode_quote_list'),
    
	# JSON Endpoints
    url(r'^episodes/json$', 'quotes_app.views.episode.thin_json_episode_query', name="thin_json_episode_query"),
    url(r'^podcasts/json$', 'quotes_app.views.podcast.thin_json_podcast_query', name="thin_json_podcast_query"),
    
    
    # Allauth urls
    (r'^accounts/', include('allauth.urls')),

)

# Serve static in development
from django.conf import settings

if settings.DEBUG:

    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT)
