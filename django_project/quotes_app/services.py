import feedparser
from quotes_app.models import Episode
from django.utils.html import strip_tags
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from datetime import datetime
import calendar
import pytz

class PodcastSyndicationService():
        
    def obtain_podcast_information(self, uri):
        
        # Potential future caching
        # .parse can take more than just a uri.
        
        # self._queue_episode_extraction(uri)
        
        parsed_url = feedparser.parse(uri)
        
        img_url = parsed_url.feed.image
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urllib2.urlopen(img_url).read())
        img_temp.flush()
        
        podcast.image.save(img_filename, File(img_temp))
        
        podcast_info = {
            'title':       parsed_url.feed.title,
            'description': parsed_url.feed.description,
            'homepage':    parsed_url.feed.link,
            'image':       parsed_url.feed.image,
        }
        
        return podcast_info
    
        def collect_episodes(self, podcast_model):
            
            if not podcast_model:
                raise TypeError("podcast_model is not defined")
            
            podcast_id = podcast_model.id
            rss_url = podcast_model.rss_url
            
            feed = feedparser.parse(rss_url)
            
            for e in feed.entries:
                e_guid = e.guid
                episode, created = Episode.objects.get_or_create(podcast_id=podcast_id, guid=e_guid)
                episode.title = e.title
                episode.publication_date = datetime.fromtimestamp(calendar.timegm(e.published_parsed), tz=pytz.utc)
                episode.description = strip_tags(e.description)
                episode.episode_url = e.link
                
                ### below is the image save code, needs fixing. this is throwing this error:
                ### TypeError at /podcasts/1/update_feed/
                ### __init__() got an unexpected keyword argument 'delete'
                img_url = e.image
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(urllib2.urlopen(img_url).read())
                img_temp.flush()
                episode.image.save(img_filename, File(img_temp))
                
                episode.save()
        
    def _queue_episode_extraction(self, uri):
        """ 
        Eventually another thread/process/queue could perform
        the extraction of episodes for this podcast.
        """
        pass
