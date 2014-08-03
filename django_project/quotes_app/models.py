from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count, Sum
from django.template import Template, Context
from django.utils.timezone import now
from datetime import date, datetime
from time import time
import pytz
from urlparse import urlparse, parse_qs
from django_resized import ResizedImageField
 
today = date.today()

# This doesn't belong here
def get_upload_file_name(instance, filename):
    return "uploaded_files/%s_%s" % (str(time()).replace('.', '_'), filename)

class QuoteVoteManager(models.Manager):
    def query_hot(self):
        ### need to implement hot algorithm
        ###
        # Most upvoted trending algorithm
        return super(QuoteVoteManager, self).get_query_set().annotate(karma_total=Sum('vote__vote_type')).order_by('-is_full_episode', '-rank_score', '-karma_total')

    def query_controversial(self):
        ### need to implement controversial algorithm
        ###
        # Most evenly upvoted and downvoted trending algorithm
        return super(QuoteVoteManager, self).get_query_set()
    
    def query_ordered(self, type):
        # Order full episode querysets by publication_date from most recent to oldest, 
        # otherwise order highlight querysets by time quote begins from earliest to latest
        ### This will need some kind of smart filter to prevent quotes with
        ### significantly overlapping times from appearing right after one another
        if type == 'full_episodes':
            return super(QuoteVoteManager, self).get_query_set().order_by('-episode__publication_date')
        if type == 'highlights':
            return super(QuoteVoteManager, self).get_query_set().order_by('-is_full_episode', '-episode__publication_date', 'time_quote_begins')
        if type == 'episode_highlights':
            return super(QuoteVoteManager, self).get_query_set().order_by('-is_full_episode', 'time_quote_begins')
            
    
    def query_new(self):
        # Order by most recently submitted to least recently submitted
        return super(QuoteVoteManager, self).get_query_set().order_by('-is_full_episode', '-created_at')
    
    def query_top(self):
        # Order by highest karma_total to lowest karma_total
        return super(QuoteVoteManager, self).get_query_set().annotate(karma_total=Sum('vote__vote_type')).order_by('-is_full_episode', '-karma_total')
    
class Podcast(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    moderators = models.ManyToManyField(User, blank=True)
    rss_url = models.URLField(blank=True)
    title = models.CharField(max_length=200, blank=True)
    alphabetical_title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    image = ResizedImageField(upload_to=get_upload_file_name, max_width=250, max_height=250, blank=True)
    homepage = models.URLField(blank=True)
    support_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    google_plus_url = models.URLField(blank=True)
    tumblr_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    reddit_url = models.URLField(blank=True)
    managed_by_superuser = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        non_alpha_title = self.title
        self.alphabetical_title = self.alphabetize_title(non_alpha_title)
        super(Podcast, self).save(*args, **kwargs)
    
    # Adapted from respondcreate's SO post 
    # http://stackoverflow.com/a/12062621/3791099
    def alphabetize_title(self, title):
        """
        Returns an alphabetical-friendly string of a title attribute.
        """
        title = self.title
        
        # A list of flags to check each 'title' against.
        starts_with_flags = [
            'the ',
            'an ',
            'a '
        ]
        
        # Check each flag to see if the title starts with one of it's contents.
        for flag in starts_with_flags:
            if title.lower().startswith(flag):
                # If the title does indeed start with a flag, return the title without
                # the flag appended to the end preceded by a comma.
                return "%s, %s" % (title[len(flag):], title[:len(flag)-1])
            else:
                pass
        # If the property did not return as a result of the previous for loop then
        # return the title.
        return self.title
    
    def get_absolute_url(self):
        return reverse('podcast_episode_list_root', kwargs={'slug': self.slug})

    def all_podcast_quotes(self):
       return Quote.objects.filter(episode__podcast=self)
    
    def all_podcast_quotes_count(self):
       return Quote.objects.filter(episode__podcast=self).exclude(is_full_episode=True).count()
    
    def all_episodes_count(self):
        return Episode.objects.filter(podcast_id=self.id).count()

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
    guid = models.CharField(max_length=200, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    publication_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    image = ResizedImageField(upload_to=get_upload_file_name, max_width=250, max_height=250, blank=True)
    episode_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    support_url = models.URLField(blank=True)
    support_recipient = models.CharField(max_length=100, blank=True)
    support_recipient_about = models.TextField(blank=True)
    # keywords = ... I think these are available in RSS feed episode data
    
    class Meta:
        ordering = ['-publication_date']
    
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

    def is_longer_than_400chars(self):
        if len(self.description) > 400:
            return 1
        else:
            return 0

    def all_episode_quotes(self):
       return Quote.objects.filter(episode__id=self.id)

    def all_episode_quotes_count(self):
       return Quote.objects.filter(episode__id=self.id).exclude(is_full_episode=True).count()
    
    all_episode_quotes_property = property(all_episode_quotes_count)
    
    def karma_total(self):
        q_list = Quote.objects.filter(episode__id=self.id).annotate(karma_total=Sum('vote__vote_type'))
        k = 0
        for q in q_list:
           k += q.karma_total
        return k
    
    def get_absolute_url(self):
        return reverse('episode_quote_list_root', kwargs={'podcast_slug': self.podcast.slug, 'pk': self.pk})
        
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
    time_quote_begins = models.IntegerField()
    time_quote_ends = models.IntegerField(null=True, blank=True)
    is_full_episode = models.BooleanField(default=False)
    
    quote_vote_manager = QuoteVoteManager()
    objects = models.Manager() # default manager
    
    def karma_total(self):
        return Vote.objects.filter(quote__id=self.id).filter(vote_type=1).count() - Vote.objects.filter(quote__id=self.id).filter(vote_type=-1).count()
    
    def set_rank(self):
        # Based on HN ranking algo at http://amix.dk/blog/post/19574
        SECS_IN_DAY = float(86400)
        GRAVITY = 1.1
        
        delta = now() - self.created_at
        item_week_age = delta.total_seconds() / SECS_IN_DAY
        karma_total = self.karma_total()
        self.rank_score = karma_total / pow((item_week_age+2), GRAVITY)
        self.save()
            
    def is_longer_than_240chars(self):
        if len(self.text) > 240:
            return 1
        else:
            return 0
            
    def is_longer_than_120chars(self):
        if len(self.text) > 120:
            return 1
        else:
            return 0
    
    def converted_time_begins(self):
        m, s = divmod(self.time_quote_begins, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return "%d:%02d:%02d" % (h, m, s)
        else:
            return "%02d:%02d" % (m, s)

        
    def converted_time_ends(self):
        if self.time_quote_ends == None:
            return None
        
        m, s = divmod(self.time_quote_ends, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return "%d:%02d:%02d" % (h, m, s)
        else:
            return "%02d:%02d" % (m, s)
    
    rank_score = models.FloatField(default=0.0)
    episode = models.ForeignKey(Episode)
    summary = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    time_quote_begins = models.IntegerField()
    time_quote_ends = models.IntegerField(null=True, blank=True)
    is_full_episode = models.BooleanField(default=False)    
    
    @classmethod
    def create(cls, submitted_by, rank_score, episode, summary, text, time_quote_begins, is_full_episode):
        quote = cls(submitted_by=submitted_by, rank_score=rank_score, episode=episode, summary=summary, text=text, time_quote_begins=time_quote_begins, is_full_episode=is_full_episode)
        return quote
    
    def duration(self):
        if self.time_quote_ends == None:
            pass
        
        duration = self.time_quote_ends - self.time_quote_begins
        m, s = divmod(duration, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return "%d:%02d:%02d" % (h, m, s)
        else:
            return "%02d:%02d" % (m, s)

    def get_absolute_url(self):
        return reverse('quote', kwargs={'podcast_slug': self.episode.podcast.slug, 'quote_id': self.pk})
        
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
    
class SavedQuote(models.Model):
    saver = models.ForeignKey(User)
    quote = models.ForeignKey(Quote)

class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True)
    image = ResizedImageField(upload_to=get_upload_file_name, max_width=250, max_height=250, blank=True)
    about = models.TextField(blank=True)
    homepage = models.URLField(blank=True)
    support_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    google_plus_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    reddit_url = models.URLField(blank=True)
    
    class Meta:
        ordering = ['user']
    
    def all_added_quotes_count(self):
        return Quote.objects.filter(submitted_by=self.user).count()
    
    leaderboard_all_added_quotes_count = property(all_added_quotes_count)
    
    def karma_total(self):
        q_list = Quote.objects.filter(submitted_by=self.user).annotate(karma_total=Sum('vote__vote_type'))
        
        ### Is there a more efficient way than running a for loop here to calculate total karma for all quotes of this Podcast?
        k = 0
        for q in q_list:
           k += q.karma_total
        if k > 0:
            return k
        else:
            pass
    # This property is too inefficient, removing karma leaderboard.   
    # leaderboard_karma_total = property(karma_total)
    
    def get_absolute_url(self):
        return reverse('user_quote_list_root', kwargs={'slug': self.user})
    
    def __unicode__(self):
        return unicode(self.user)

### This makes sure that a UserProfile is automatically created for a User.
### Is this an acceptable implementation?
User.userprofile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])