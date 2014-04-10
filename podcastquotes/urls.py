from django.conf.urls import patterns, include, url
from podcastquotes.models import Podcast, Episode, Quote
from podcastquotes.views import home
from podcastquotes.views import PodcastCreateView, PodcastDeleteView, PodcastUpdateView, PodcastDetailView, PodcastListView
from podcastquotes.views import EpisodeCreateView, EpisodeDeleteView, EpisodeUpdateView, EpisodeDetailView, EpisodeListView
from podcastquotes.views import quote_create, QuoteDeleteView, QuoteUpdateView, QuoteDetailView, QuoteListView
from podcastquotes.forms import PodcastCreateForm, PodcastForm
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'podcastquotes.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^$', 'podcastquotes.views.home', name='home'),
    
    # SHOW PODCAST
    url(r'^podcasts/(?P<pk>\d+)/$', PodcastDetailView.as_view(
        model=Podcast,
        template_name='podcast_detail.html',
        context_object_name='podcast'),
        name='podcast_detail',
        ),
        
    url(r'^podcasts/create', 'podcastquotes.views.podcast_create',
        name='podcast_create',
        ),
    
    url(r'^podcasts/delete/(?P<pk>\d+)/$', PodcastDeleteView.as_view(),
        name = 'podcast_delete',
        ),
    
    url(r'^episodes/create', 'podcastquotes.views.episode_create',
        name='episode_create',
        ),
    
    url(r'^episodes/delete/(?P<pk>\d+)/$', EpisodeDeleteView.as_view(),
        name = 'episode_delete',
        ),
    
    url(r'^episodes/(?P<pk>\d+)/$', EpisodeDetailView.as_view(
        model=Episode,
        template_name='episode_detail.html',
        context_object_name='episode'),
        name='episode_detail',
        ),
    
    url(r'^add-a-quote/$', 'podcastquotes.views.quote_create',
             name='create_quote',
             ),
        
    url(r'^admin/', include(admin.site.urls)),

)
