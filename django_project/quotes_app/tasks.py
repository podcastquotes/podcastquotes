from quotes_app.models import Quote, Podcast
from quotes_app.services import PodcastSyndicationService

podcast_syndication_service = PodcastSyndicationService()

def rank_all():
    
    for quote in Quote.quote_vote_manager.all():
        quote.set_rank()

def update_rss_feeds():
    
    rss_podcasts = Podcast.objects.exclude(rss_url__exact='')
    
    for podcast in rss_podcasts:
        podcast_syndication_service.collect_episodes(podcast)
