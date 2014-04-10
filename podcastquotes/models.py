from django.db import models
from time import time
from datetime import date
from django.core.urlresolvers import reverse

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
    # guests = ...
    # duration = what type of field for length of episode data? needs to match up with format for quote.time_quote_begins and quote.time_quote_ends
    # keywords = ...
    
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