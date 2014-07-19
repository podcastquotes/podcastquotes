from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile

from django.utils.html import strip_tags
import feedparser
import calendar
from datetime import datetime
import pytz

# this view checks if every episode with a youtube_url has a full episode clip,
# if not, it creates one.
@user_passes_test(lambda u: u.is_staff)
def create_full_episodes(self):
    episodes = Episode.objects.all()
    for episode in episodes:
        if episode.youtube_url or episode.episode_url:
            try:
                full_episode_quote = Quote.objects.get(episode__id=episode.id, is_full_episode=True)
            except MultipleObjectsReturned:
                alert('Episode #' + str(episode.id) + 'returns multiple objects!')
                break
            except ObjectDoesNotExist:
                # user with id=1 is the user "podverse" on podverse.tv
                user = User.objects.get(id=1)
                full_episode_quote = Quote.create(submitted_by=user,
                                              rank_score=float(0.0),
                                              episode=episode,
                                              summary=episode.title,
                                              text=episode.description,
                                              time_quote_begins=int(0),
                                              is_full_episode=True)
                full_episode_quote.save()
                vote = Vote.create(voter=user, quote=full_episode_quote, vote_type=1)
                vote.save()
    return HttpResponseRedirect('/')

# this view updates the info on all episodes in the database.
@user_passes_test(lambda u: u.is_staff)
def update_all_existing_episodes(self):
    podcasts = Podcast.objects.all()
    for podcast in podcasts:
        podcast_id = podcast.id
        rss_url = podcast.rss_url
        
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
            
            try:
                episode.episode_url = e.enclosures[0].href
            except IndexError:
                pass
            
            episode.save()
    return HttpResponseRedirect('/')
    
# this view helps mitch check for episodes which do not have a YouTube link for playing clips
class NeedYouTubeLinks(ListView):
    model = Episode
    template_name = 'need-youtube-links.html'
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(NeedYouTubeLinks, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(NeedYouTubeLinks, self).get_context_data(**kwargs)
        context['episodes_without_youtube_links'] = Episode.objects.filter(podcast__managed_by_superuser=True).filter(youtube_url='').order_by('podcast');
        return context

# this view helps Mitch check episodes in a podcast rss feed
class PodcastEpisodeTitlePrint(ListView):
    model = Podcast
    template_name = 'podcast_episode_title_print.html'
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(PodcastEpisodeTitlePrint, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(PodcastEpisodeTitlePrint, self).get_context_data(**kwargs)
        context['podcast'] = Podcast.objects.get(id=self.kwargs['pk'])
        return context