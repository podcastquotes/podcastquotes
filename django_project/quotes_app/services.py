import feedparser
from quotes_app.models import Episode
from django.utils.html import strip_tags
import calendar
from datetime import datetime
import pytz
from time import time
import requests
from django.core.files import File
from tempfile import NamedTemporaryFile

import logging

logger = logging.getLogger(__name__)

def get_upload_file_name(filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.', '_'), filename)

def save_image_from_url(model, url, podcast_title):
    r = requests.get(url)
    
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(r.content)
    img_temp.flush()
    
    model.image.save(get_upload_file_name(podcast_title), File(img_temp), save=True)

class PodcastSyndicationService():
        
    def obtain_podcast_information(self, uri):
        
        # Potential future caching
        # .parse can take more than just a uri.
        
        # self._queue_episode_extraction(uri)
        
        parsed_url = feedparser.parse(uri)
        
        feed = parsed_url.feed
        
        podcast_info = {
            'title': feed.title,
        }
        
        if hasattr(feed, 'description'):
            podcast_info['description'] = feed.description
        else: 
            podcast_info['description'] = ''
            
        if hasattr(feed, 'link'):
            podcast_info['homepage'] = feed.link
        else: 
            podcast_info['homepage'] = ''
            
        if hasattr(feed, 'tags'):
            podcast_info['keywords_list'] = feed.tags
        else: 
            podcast_info['keywords_list'] = ''
            
        if hasattr(feed, 'image.url'):
            podcast_info['image_url'] = feed.image.url
        else: 
            podcast_info['image_url'] = ''
        
        return podcast_info
    
    def collect_episodes(self, podcast_model):
        
        if not podcast_model:
            raise TypeError("podcast_model is not defined")
        
        logger.info('Starting to collect episodes for {0}'\
            .format(podcast_model.title))
        
        podcast_id = podcast_model.id
        rss_url = podcast_model.rss_url
        
        feed = feedparser.parse(rss_url)
        
        new_episode_count = 0
        
        for e in feed.entries:
            e_guid = e.guid
            episode, created = Episode.objects.get_or_create(podcast_id=podcast_id, guid=e_guid)
            
            if created == False:
                continue
            
            episode.title = e.title
            episode.publication_date = datetime.fromtimestamp(calendar.timegm(e.published_parsed), tz=pytz.utc)
            episode.description = strip_tags(e.description)
            episode.episode_url = e.link
            episode.save()
            
            new_episode_count = new_episode_count + 1
            
        logger.info('Found {0} episodes for {1}; {2} new.'\
            .format(
                len(feed.entries),
                    podcast_model.title,
                    new_episode_count))
        
    def _queue_episode_extraction(self, uri):
        """ 
        Eventually another thread/process/queue could perform
        the extraction of episodes for this podcast.
        """
        pass
