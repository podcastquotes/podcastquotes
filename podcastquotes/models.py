from django.db import models
from time import time
from datetime import date
from django.core.urlresolvers import reverse
import urlparse

from urlparse import urlparse, parse_qs
 
from django.template import Template, Context
from django.conf import settings

# This doesn't belong here
def get_upload_file_name(instance, filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.', '_'), filename)


class Podcast(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.FileField(upload_to=get_upload_file_name, blank=True)
    homepage = models.URLField(blank=True)
    donate_url = models.URLField(blank=True)
    # hosts = ...
    # categories = ...
    # keywords = ...
    # followers = ...
    
    def get_absolute_url(self):
        return reverse('podcast_detail', kwargs={'pk': self.pk})

    def all_podcasts(self):
       return Podcast.objects.all()
    
    def all_podcast_quotes(self):
       return Quote.objects.filter(episode__podcast=self)
    
    def __unicode__(self):
        return unicode(self.title)

class Episode(models.Model):
    podcast = models.ForeignKey(Podcast)
    title = models.CharField(max_length=200)
    publication_date = models.DateField()
    description = models.TextField(blank=True)
    episode_link = models.URLField(blank=True)
    image = models.FileField(upload_to=get_upload_file_name, blank=True)
    video_link = models.URLField(blank=True) 
    audio_link = models.URLField(blank=True)
    # guests = ...
    # duration = what type of field for length of episode data? needs to match up with format for quote.time_quote_begins and quote.time_quote_ends
    # keywords = ...
 
    def video_id(self):
        """
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        query = urlparse(self.video_link)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        return None
     
     
    def parse(kwargs):
        url = kwargs.get('url')
        if not url:
            return "[Add video url]"
         
        id = video_id(url)
         
        if id is None:
            return "[Bad url]"
         
        width = int(kwargs.get('width', getattr(settings, 'SHORTCODES_YOUTUBE_WIDTH', 425)))
        height = int(kwargs.get('height', getattr(settings, 'SHORTCODES_YOUTUBE_HEIGHT', 0)))
         
        if height == 0:
            height = int(round(width / 425.0 * 344.0))
        
        return '<iframe width="%s" height="%s" src="http://www.youtube.com/embed/%s?wmode=opaque" frameborder="0" allowfullscreen></iframe>' % (width, height, id)
        
        # many thanks to Amit Agarwal aka @labnol for this snazzy YouTube parser   
        # https://gist.github.com/trojkat/1989762 
        # https://labnol.googlecode.com/files/youtube.js


    
    def all_episodes(self):
       return Episode.objects.filter(podcast__id=self.id)
    
    def all_episode_quotes(self):
       return Quote.objects.filter(episode__id=self.id)
    
    def __unicode__(self):
        return u'%s - %s' % (self.podcast.title, self.title)

class PersonQuoted(models.Model):
    person = models.CharField(max_length=100)
    
    def get_absolute_url(self):
        return reverse('home')
        
    def __unicode__(self):
        return unicode(self.person)
        
class Tag(models.Model):
    tag = models.CharField(max_length=100)
    
    def get_absolute_url(self):
        return reverse('home')
    
    def __unicode__(self):
        return unicode(self.tag)
        
class Quote(models.Model):
    episode = models.ForeignKey(Episode)
    persons_quoted = models.ManyToManyField(PersonQuoted)
    text = models.TextField(blank=True)
    time_quote_begins = models.IntegerField()
    time_quote_ends = models.IntegerField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    # submitted_by = ...
    # vote = ...
    
    def converted_time_begins(self):
        m, s = divmod(self.time_quote_begins, 60)
        h, m = divmod(m, 60)
        print "%d:%02d:%02d" % (h, m, s)
        return "%d:%02d:%02d" % (h, m, s)
        
    def converted_time_ends(self):
        m, s = divmod(self.time_quote_ends, 60)
        h, m = divmod(m, 60)
        print "%d:%02d:%02d" % (h, m, s)
        return "%d:%02d:%02d" % (h, m, s)
        
    def get_absolute_url(self):
        return reverse('home')
    
    def __unicode__(self):
        return u'%s - %s' % (self.episode.podcast.title, self.episode.title)