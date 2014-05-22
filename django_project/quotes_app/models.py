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
from django.utils.timezone import now

today = date.today()

# This doesn't belong here
def get_upload_file_name(instance, filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.', '_'), filename)

class QuoteVoteManager(models.Manager):
    
    def query_hot(self):
        ### need to implement hot algorithm
        ###
        # Most upvoted trending algorithm
        return super(QuoteVoteManager, self).get_query_set().annotate(vote_score=Sum('vote__vote_type')).order_by('-rank_score', '-vote_score')

    def query_not(self):
        ### need to implement not algorithm
        ###
        # Most downvoted trending algorithm
        return super(QuoteVoteManager, self).get_query_set().annotate(vote_score=Sum('vote__vote_type')).order_by('rank_score', 'vote_score')

    def query_controversial(self):
        ### need to implement controversial algorithm
        ###
        # Most evenly upvoted and downvoted trending algorithm
        return super(QuoteVoteManager, self).get_query_set()
        
    def query_new(self):
        # Order by most recently submitted to least recently submitted
        return super(QuoteVoteManager, self).get_query_set().order_by('-created_at')
        
    def query_top(self):
        # Order by highest vote_score to lowest vote_score
        return super(QuoteVoteManager, self).get_query_set().annotate(vote_score=Sum('vote__vote_type')).order_by('-vote_score')
        
    def query_bottom(self):
        # Order by lowest vote_score to highest vote_score
        return super(QuoteVoteManager, self).get_query_set().annotate(vote_score=Sum('vote__vote_type')).order_by('vote_score')
        
    def query_mainstream(self):
        # Order by total number of votes
        return super(QuoteVoteManager, self).get_query_set().annotate(vote_total=Count('vote__vote_type')).order_by('vote_total')
        
    def query_underground(self):
        ### need to implement underground algorithm
        ###
        # Order by the ratio of upvotes to downvotes they have received (maybe 90% upvote to 10% downvote?) but limit query to only quotes that have received less than a certain # of votes...the # could be 10, 20, 50, etc. depending how how active the site is. Perhaps the # of votes could be 10% of whatever the average top quote of the day receives...
        return super(QuoteVoteManager, self).get_query_set()
    
    def query_chronological(self):
        # Order by the time the quote begins in the podcast
        return super(QuoteVoteManager, self).get_query_set().order_by('time_quote_begins')
        
    def query_ghosts(self):
        ### need to implement ghosts algorithm
        ###
        # Quotes that have no votes
        return super(QuoteVoteManager, self).get_query_set()
        
    def query_birthdays(self):
        ### need to implement birthdays algorithm
        ### Quotes that were publicized on the same month/day as today in any year, ordered by highest vote_score to lowest vote_score
        return super(QuoteVoteManager, self).get_query_set()
    
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
        return reverse('podcast_quote_list_root', kwargs={'pk': self.pk})

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
    
    def karma_total(self):
        q_list = Quote.objects.filter(episode__podcast=self).annotate(karma_total=Sum('vote__vote_type'))
        
        ### Is there a more efficient way than running a for loop here to calculate total karma for all quotes of this Podcast?
        k = 0
        for q in q_list:
           k += q.karma_total
        return k

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

    def is_longer_than_200chars(self):
        if len(self.description) > 200:
            return 1
        else:
            return 0
        
    def all_episodes(self):
       return Episode.objects.filter(podcast__id=self.podcast.id)
    
    def all_episode_quotes(self):
       return Quote.objects.filter(episode__id=self.id)

    def all_episode_quotes_count(self):
       return Quote.objects.filter(episode__id=self.id).count()
    
    def karma_total(self):
        q_list = Quote.objects.filter(episode__id=self.id).annotate(karma_total=Sum('vote__vote_type'))
        
        ### Is there a more efficient way than running a for loop here to calculate total karma for all quotes of this Podcast?
        k = 0
        for q in q_list:
           k += q.karma_total
        return k
    
    def get_absolute_url(self):
        return reverse('episode_quote_list_root', kwargs={'pk': self.pk})

    def __unicode__(self):
        return u'%s - %s' % (self.podcast.title, self.title)

class Quote(models.Model):
    submitted_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rank_score = models.FloatField(default=0.0)
    episode = models.ForeignKey(Episode)
    summary = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    time_quote_begins = models.IntegerField(blank=True)
    time_quote_ends = models.IntegerField(blank=True)
    
    quote_vote_manager = QuoteVoteManager()
    objects = models.Manager() # default manager
    
    def vote_score(self):
        return Vote.objects.filter(quote__id=self.id).filter(vote_type=1).count() - Vote.objects.filter(quote__id=self.id).filter(vote_type=-1).count()
    
    def set_rank(self):
        # Based on HN ranking algo at http://amix.dk/blog/post/19574
        SECS_IN_HOUR = float(60*60)
        GRAVITY = 1.2
        
        delta = now() - self.created_at
        item_hour_age = delta.total_seconds() / SECS_IN_HOUR
        vote_score = self.vote_score()
        self.rank_score = vote_score / pow((item_hour_age+2), GRAVITY)
        print self.rank_score
        self.save()
    
    def is_longer_than_200chars(self):
        if len(self.text) > 200:
            return 1
        else:
            return 0
    
    def converted_time_begins(self):
        m, s = divmod(self.time_quote_begins, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)
        
    def converted_time_ends(self):
        m, s = divmod(self.time_quote_ends, 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)
        
    def get_absolute_url(self):
        return reverse('quote', kwargs={'quote_id': self.pk})
        
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
    
    @classmethod
    def create(cls, voter, quote, vote_type):
        vote = cls(voter=voter, quote=quote, vote_type=vote_type)
        return vote
    
    def __unicode__(self):
        return "Vote by: " + str(self.voter)  