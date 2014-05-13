from django.db import models
from time import time
from datetime import date, datetime
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.models import Count, Sum
import urlparse

from urlparse import urlparse, parse_qs
 
from django.template import Template, Context
from django.conf import settings

today = date.today()

# This doesn't belong here
def get_upload_file_name(instance, filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.', '_'), filename)

class Podcast(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
        return reverse('podcast_top', kwargs={'podcast_id': self.pk})

    # Implement some kind of trending algorithm with exponential decay 
    # def all_podcast_quotes_hot(self):
    #    return Quote.objects.filter(episode__podcast=self).filter()
    
    # Reverse the hot algorithm results to determine not sorting
    # def all_podcast_quotes_not(self):
    #    return Quote.objects.filter(episode__podcast=self).filter()
    
    # Algorithm showing quotes that are diametrically in the middle 
    # of hot/not, with higher ranking going to quotes with the most overall votes
    # def all_podcast_quotes_controversial(self):
    #    return Quote.objects.filter(episode__podcast=self).filter()
    
    # Return podcast quotes ordered by newest to oldest
    def all_podcast_quotes_new(self):
        return Quote.objects.filter(episode__podcast=self).order_by('-created_at')
    
    # Return podcast quotes ordered by highest score to lowest score
    ### Eventually users should be able to check highest/lowest score
    ### filtered by date range: past hour, past day, past week, past month, past year
    def all_podcast_quotes_top(self):
        return Quote.objects.filter(episode__podcast=self).annotate(vote_score=Sum('vote__vote_type')).order_by('-vote_score')
    
    # Return podcast quotes ordered by lowest score to highest score
    ### Eventually users should be able to check highest/lowest score
    ### filtered by date range: past hour, past day, past week, past month, past year
    def all_podcast_quotes_bottom(self):
        return Quote.objects.filter(episode__podcast=self).annotate(vote_score=Sum('vote__vote_type')).order_by('vote_score')
    
    # Return podcast quotes ordered by the time the quote begins in the podcast
    def all_podcast_quotes_chronological(self):
        return Quote.objects.filter(episode__podcast=self).order_by('time_quote_begins')
    
    # Return podcast quotes ordered by total number of votes
    def all_podcast_quotes_mainstream(self):
        return Quote.objects.filter(episode__podcast=self).annotate(vote_total=Count('vote__vote_type')).order_by('vote_total')
    
    ### Return podcast quotes ordered by the ratio of upvotes to downvotes they have received
    ### but are below a threshold of total votes...threshold could be 10% of the average
    ### vote_total of the top mainstream quotes...or some better metric...
    ### def all_podcast_quotes_underground(self):
    ###     return Quote.objects.filter(episode__podcast=self)
    
    # Return podcast quotes that have received no votes
    # def all_podcast_quotes_ghosts(self):
    #    return Quote.objects.filter(episode__podcast=self).annotate(vote_total=Count('vote__vote_type')).filter('vote_total')
        
    # Return podcast quotes that are from an episode that was published
    # the same month and day as today
    # def all_podcast_quotes_birthdays(self):
    #    return Quote.objects.filter(episode__podcast=self).filter(episode__publication_date=today)
    
    ###
    ### Implement custom range filter solution
    ###
    
    def all_podcasts(self):
       return Podcast.objects.all()
    
    def all_podcast_quotes(self):
       return Quote.objects.filter(episode__podcast=self)
    
    def all_podcast_quotes_count(self):
       return Quote.objects.filter(episode__podcast=self).count()
    
    def all_episodes_count(self):
        return Episode.objects.filter(podcast_id=self.id).count()
    
    def all_episodes_with_youtube_urls(self):
        return Episode.objects.filter(podcast__id=self.id).exclude(youtube_url__exact='')
        
    def all_episodes_with_youtube_urls_count(self):
        return Episode.objects.filter(podcast__id=self.id).exclude(youtube_url__exact='').count()
    
    def __unicode__(self):
        return unicode(self.title)

class Episode(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    podcast = models.ForeignKey(Podcast)
    title = models.CharField(max_length=200)
    guid = models.URLField(blank=True)
    publication_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    episode_url = models.URLField(blank=True)
    donate_url = models.URLField(blank=True)
    donation_recipient = models.CharField(max_length=100, blank=True)
    donation_recipient_about = models.TextField(blank=True)
    image = models.FileField(upload_to=get_upload_file_name, blank=True)
    youtube_url = models.URLField(blank=True)
    # keywords = ... I think these are available in RSS feed episode data
 
    # Implement some kind of trending algorithm with exponential decay 
    # def all_episode_quotes_hot(self):
    #    return Quote.objects.filter(episode=self).filter()
    
    # Reverse the hot algorithm results to determine not sorting
    # def all_episode_quotes_not(self):
    #    return Quote.objects.filter(episode=self).filter()
    
    # Algorithm showing quotes that are diametrically in the middle 
    # of hot/not, with higher ranking going to quotes with the most overall votes
    # def all_episode_quotes_controversial(self):
    #    return Quote.objects.filter(episode=self).filter()
    
    # Return episode quotes ordered by newest to oldest
    def all_episode_quotes_new(self):
        return Quote.objects.filter(episode=self).order_by('-created_at')
    
    # Return episode quotes ordered by highest score to lowest score
    ### Eventually users should be able to check highest/lowest score
    ### filtered by date range: past hour, past day, past week, past month, past year
    def all_episode_quotes_top(self):
        return Quote.objects.filter(episode=self).annotate(vote_score=Sum('vote__vote_type')).order_by('-vote_score')
    
    # Return episode quotes ordered by lowest score to highest score
    ### Eventually users should be able to check highest/lowest score
    ### filtered by date range: past hour, past day, past week, past month, past year
    def all_episode_quotes_bottom(self):
        return Quote.objects.filter(episode=self).annotate(vote_score=Sum('vote__vote_type')).order_by('vote_score')
    
    # Return episode quotes ordered by the time the quote begins in the podcast
    def all_episode_quotes_chronological(self):
        return Quote.objects.filter(episode=self).order_by('time_quote_begins')
    
    # Return episode quotes ordered by total number of votes
    ### Eventually users should be able to check highest/lowest score
    ### filtered by date range: past hour, past day, past week, past month, past year
    def all_episode_quotes_mainstream(self):
        return Quote.objects.filter(episode=self).annotate(vote_total=Count('vote__vote_type')).order_by('vote_total')
    
    ### Return episode quotes ordered by the ratio of upvotes to downvotes they have received
    ### but are below a threshold of total votes...threshold could be 10% of the average
    ### vote_total of the top mainstream quotes...or some better idea...
    ### def all_episode_quotes_underground(self):
    ###     return Quote.objects.filter(episode=self)
    
    # Return episode quotes that have received no votes
    def all_episode_quotes_ghosts(self):
        return Quote.objects.filter(episode=self).annotate(vote_total=Count('vote__vote_type')).filter('vote_total')
        
    # Return podcast quotes that are from an episode that was published
    # the same month and day as today
    # def all_episode_quotes_birthdays(self):
    #    return Quote.objects.filter(episode=self).filter(episode__publication_date=today)
    
    ###
    ### Implement custom range filter solution
    ###
    
    def video_id(self):
        """
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        query = urlparse(self.youtube_url)
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

    def all_episode_quotes_count(self):
       return Quote.objects.filter(episode__id=self.id).count()
       
    def get_absolute_url(self):
        return reverse('episode_top', kwargs={'podcast_id': self.podcast.pk, 'episode_id': self.pk})

    def __unicode__(self):
        return u'%s - %s' % (self.podcast.title, self.title)

class Quote(models.Model):
    submitted_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    episode = models.ForeignKey(Episode)
    summary = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    time_quote_begins = models.IntegerField(blank=True)
    time_quote_ends = models.IntegerField(blank=True)
    
    def vote_score(self):
        return Vote.objects.filter(quote__id=self.id).filter(vote_type=1).count() - Vote.objects.filter(quote__id=self.id).filter(vote_type=-1).count()

    def converted_time_begins(self):
        m, s = divmod(self.time_quote_begins, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)
        
    def converted_time_ends(self):
        m, s = divmod(self.time_quote_ends, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)
        
    def get_absolute_url(self):
        return reverse('quote', kwargs={'podcast_id': self.episode.podcast.pk, 'episode_id': self.episode.pk, 'quote_id': self.pk})
        
    def __unicode__(self):
        return u'%s - %s' % (self.episode.podcast.title, self.episode.title)
        
class Vote(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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
    vote_type = models.IntegerField(choices=VOTE_CHOICES, null=True)
    
    class Meta:
        unique_together = (('voter', 'quote'),)
    
    @classmethod
    def create(cls, voter, quote, vote_type):
        vote = cls(voter=voter, quote=quote, vote_type=vote_type)
        return vote
    
    def __unicode__(self):
        return "Vote by: " + str(self.voter)  