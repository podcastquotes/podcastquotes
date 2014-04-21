from django.conf.urls import patterns, include, url
from podcastquotes.models import Podcast, Episode, Quote
from podcastquotes.views import home
from podcastquotes.views import PodcastDetailView
from podcastquotes.views import EpisodeDetailView
from podcastquotes.views import quote_create, QuoteDetailView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'podcastquotes.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^$', 'podcastquotes.views.home', name='home'),
    
    url(r'^podcasts/(?P<pk>\d+)/$', 
        PodcastDetailView.as_view(
            model=Podcast,
            template_name='podcast_detail.html',
            context_object_name='podcast'),
        name='podcast_detail',),

    # url(r'^podcasts/create', 'podcastquotes.views.podcast_create',
    #    name='podcast_create',),
    
    # url(r'^podcasts/edit/(?P<pk>\d+)/$', PodcastUpdateView.as_view(),
    #    name = 'podcast_update',),
    
    # url(r'^podcasts/delete/(?P<pk>\d+)/$', PodcastDeleteView.as_view(),
    #    name = 'podcast_delete',),
    
    # url(r'^episodes/create', 'podcastquotes.views.episode_create',
    #    name='episode_create',),

    # url(r'^episodes/edit/(?P<pk>\d+)/$', EpisodeUpdateView.as_view(),
    #    name = 'episode_update',),

    # url(r'^episodes/delete/(?P<pk>\d+)/$', EpisodeDeleteView.as_view(),
    #    name = 'episode_delete',),

    url(r'^episodes/(?P<pk>\d+)/$', 
        EpisodeDetailView.as_view(
            model=Episode,
            template_name='episode_detail.html',
            context_object_name='episode'),
        name='episode_detail',),
    
    url(r'^quotes/create/', 'podcastquotes.views.quote_create',
        name='create_quote',),

    # url(r'^quotes/edit/(?P<pk>\d+)/$', QuoteUpdateView.as_view(),
    #    name = 'quote_update',),
   
    url(r'^admin/', include(admin.site.urls)),
)

# Serve static
from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
   )