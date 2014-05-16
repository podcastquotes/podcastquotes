from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from quotes_app.models import Podcast, Episode, Quote
from quotes_app.views import home_top
from quotes_app.views import QuoteTopListView
from quotes_app.views import PodcastQuoteTopListView, PodcastCreateView
from quotes_app.views import quote_create
from quotes_app.views import VoteFormView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
 
    url(r'^$', QuoteTopListView.as_view(), name='home_top'),
 
    url(r'^podcasts/(?P<pk>\d+)/$', PodcastQuoteTopListView.as_view(), name='podcast_top'),
 
    url(r'^hot/$', 'quotes_app.views.home_hot', name='home_hot'),
    
    url(r'^not/$', 'quotes_app.views.home_not', name='home_not'),
    
    url(r'^controversial/$', 'quotes_app.views.home_controversial', name='home_controversial'),
    
    url(r'^new/$', 'quotes_app.views.home_new', name='home_new'),
    
    url(r'^bottom/$', 'quotes_app.views.home_bottom', name='home_bottom'),
    
    url(r'^mainstream/$', 'quotes_app.views.home_mainstream', name='home_mainstream'),
    
    url(r'^underground/$', 'quotes_app.views.home_underground', name='home_underground'),
    
    url(r'^chronological/$', 'quotes_app.views.home_chronological', name='home_chronological'),
    
    url(r'^ghosts/$', 'quotes_app.views.home_ghosts', name='home_ghosts'),
    
    url(r'^birthdays/$', 'quotes_app.views.home_birthdays', name='home_birthdays'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/hot/$', 'quotes_app.views.podcast_hot', name='podcast_hot'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/not/$', 'quotes_app.views.podcast_not', name='podcast_not'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/controversial/$', 'quotes_app.views.podcast_controversial', name='podcast_controversial'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/new/$', 'quotes_app.views.podcast_new', name='podcast_new'),
    
    
    
    url(r'^podcasts/(?P<podcast_id>\d+)/bottom/$', 'quotes_app.views.podcast_bottom', name='podcast_bottom'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/chronological/$', 'quotes_app.views.podcast_chronological', name='podcast_chronological'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/mainstream/$', 'quotes_app.views.podcast_mainstream', name='podcast_mainstream'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/underground/$', 'quotes_app.views.podcast_underground', name='podcast_underground'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/ghosts/$', 'quotes_app.views.podcast_ghosts', name='podcast_ghosts'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/birthdays/$', 'quotes_app.views.podcast_birthdays', name='podcast_birthdays'),
    
    url(r'^podcasts/create/$', 
        PodcastCreateView.as_view(
            model=Podcast,
            template_name='podcast_create.html',
            context_object_name='podcast'),
        name='podcast_create',),

    url(r'^podcasts/(?P<podcast_id>\d+)/update_feed/$', 
        'quotes_app.views.update_feed', 
        name='update_feed',),

    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/hot/$', 'quotes_app.views.episode_hot', name='episode_hot'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/not/$', 'quotes_app.views.episode_not', name='episode_not'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/controversial/$', 'quotes_app.views.episode_controversial', name='episode_controversial'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/new/$', 'quotes_app.views.episode_new', name='episode_new'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/$', 'quotes_app.views.episode_top', name='episode_top'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/bottom/$', 'quotes_app.views.episode_bottom', name='episode_bottom'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/chronological/$', 'quotes_app.views.episode_chronological', name='episode_chronological'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/mainstream/$', 'quotes_app.views.episode_mainstream', name='episode_mainstream'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/underground/$', 'quotes_app.views.episode_underground', name='episode_underground'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/ghosts/$', 'quotes_app.views.episode_ghosts', name='episode_ghosts'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/birthdays/$', 'quotes_app.views.episode_birthdays', name='episode_birthdays'),
    
    url(r'^podcasts/(?P<podcast_id>\d+)/episodes/(?P<episode_id>\d+)/quotes/(?P<quote_id>\d+)/$', 'quotes_app.views.quote', name='quote'),
    
    url(r'^quotes/create/', 'quotes_app.views.quote_create',
        name='quote_create',),
    
    url(r'^quotes/vote/$', login_required(VoteFormView.as_view()), name="quote_vote"),
   
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
