from django.db import models
from time import time
from datetime import date
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import urlparse

from urlparse import urlparse, parse_qs
 
from django.template import Template, Context
from django.conf import settings

# This doesn't belong here
def get_upload_file_name(instance, filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.', '_'), filename)

class Podcast(models.Model):
    rss_url = models.URLField(blank=True)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    image = models.FileField(upload_to=get_upload_file_name, blank=True)
    homepage = models.URLField(blank=True)
    donate_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    google_plus_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
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
    publication_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    episode_url = models.URLField(blank=True)
    donate_url = models.URLField(blank=True)
    image = models.FileField(upload_to=get_upload_file_name, blank=True)
    video_url = models.URLField(blank=True) 
    audio_url = models.URLField(blank=True)
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
        query = urlparse(self.video_url)
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
        
        # many thanks to Amit Agarwal aka @labnol for this snazzy YouTube parser, video_id, parse
        # https://gist.github.com/trojkat/1989762 
        # https://labnol.googlecode.com/files/youtube.js

    def all_episodes(self):
       return Episode.objects.filter(podcast__id=self.podcast.id)
    
    def all_episode_quotes(self):
       return Quote.objects.filter(episode__id=self.id)

    def get_absolute_url(self):
        return reverse('episode_detail', kwargs={'pk': self.pk})

    def __unicode__(self):
        return u'%s - %s' % (self.podcast.title, self.title)

class Quote(models.Model):
    episode = models.ForeignKey(Episode)
    summary = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    submitted_by = models.ForeignKey(User)
    submitted_time = models.DateTimeField(auto_now_add=True)
    time_quote_begins = models.IntegerField(blank=True)
    time_quote_ends = models.IntegerField(blank=True)
    
    def vote_score(self):
        return Vote.objects.filter(quote__id=self.id).filter(vote_type=1).count() - Vote.objects.filter(quote__id=self.id).filter(vote_type=-1).count()

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
        
class Vote(models.Model):
    voter = models.ForeignKey(User)
    quote = models.ForeignKey(Quote)
    UPVOTE = 1
    NOVOTE = 0
    DOWNVOTE = -1
    VOTE_CHOICES = (
        (UPVOTE, 'Upvote'),
        (NOVOTE, 'Novote'),
        (DOWNVOTE, 'Downvote'),
    )
    vote_type = models.IntegerField(choices=VOTE_CHOICES)
    
    class Meta:
        unique_together = (('voter', 'quote'),)
    
    @classmethod
    def create(cls, voter, quote, vote_type):
        vote = cls(voter=voter, quote=quote, vote_type=vote_type)
        return vote
    
    def __unicode__(self):
        return "Vote by: " + str(self.voter)
        