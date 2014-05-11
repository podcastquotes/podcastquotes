from time import mktime
from datetime import datetime, date
import calendar
import pytz
from django.shortcuts import render_to_response, redirect, get_object_or_404, render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum
from quotes_app.models import Podcast, Episode, Quote, Vote
from core.forms import PodcastCreateForm, PodcastForm
from core.forms import EpisodeCreateForm, EpisodeForm
from core.forms import QuoteCreateForm, QuoteForm
import feedparser

today = date.today()

def home_hot(request):
    return render(request, 'home_hot.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 # Implement some kind of trending algorithm with exponential decay
                 # 'all_quotes_hot': Quote.objects.filter(),
                 'home_hot_is_active': Quote.objects.all().first()})
                             
def home_not(request):
    return render(request, 'home_not.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 # Reverse the hot algorithm results to determine not sorting
                 # 'all_quotes_not': Quote.objects.filter(),
                 'home_not_is_active': Quote.objects.all().first()})
                             
def home_controversial(request):
    return render(request, 'home_controversial.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 # Algorithm showing quotes that are diametrically in the middle of hot/not, with higher ranking going to quotes with the most overall votes
                 # 'all_quotes_controversial': Quote.objects.filter(),
                 'home_controversial_is_active': Quote.objects.all().first()})
                             
def home_new(request):
    return render(request, 'home_new.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 # Return quotes ordered by newest to oldest
                 'all_quotes_new': Quote.objects.order_by('-created_at'),
                 'home_new_is_active': Quote.objects.all().first()})

def home_top(request):
    return render(request, 'home_top.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 # Return quotes ordered by highest score to lowest score
                 'all_quotes_top': Quote.objects.annotate(vote_score=Sum('vote__vote_type')).order_by('-vote_score'),
                 'home_top_is_active': Quote.objects.all().first()})
                             
def home_bottom(request):
    return render(request, 'home_bottom.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 # Return quotes ordered by lowest score to highest score
                 'all_quotes_bottom': Quote.objects.annotate(vote_score=Sum('vote__vote_type')).order_by('vote_score'),
                 'home_bottom_is_active': Quote.objects.all().first()})
                             
def home_mainstream(request):
    return render(request, 'home_mainstream.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 # Return quotes ordered by total number of votes
                 'all_quotes_mainstream': Quote.objects.annotate(vote_total=Count('vote__vote_type')).order_by('vote_total'),
                 'home_mainstream_is_active': Quote.objects.all().first()})
                             
def home_underground(request):
    return render(request, 'home_underground.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 # Return quotes ordered by the ratio of upvotes to downvotes they have received (maybe 90% upvote to 10% downvote?) but limit query to only quotes that have received less than a certain # of votes...the # could be 10, 20, 50, etc. depending how how active the site is. Perhaps the # of votes could be 10% of whatever the average top quote of the day receives...
                 # 'all_quotes_underground': Quote.objects.filter(),
                 'home_underground_is_active': Quote.objects.all().first()})
                             
def home_chronological(request):
    return render(request, 'home_chronological.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 # Return quotes ordered by the time the quote begins in the podcast
                 'all_quotes_chronological': Quote.objects.order_by('time_quote_begins'),
                 'home_chronological_is_active': Quote.objects.all().first()})
                             
def home_ghosts(request):
    return render(request, 'home_ghosts.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 # Return quotes that have received no votes
                 # 'all_quotes_ghosts': Quote.objects.annotate(),
                 'home_ghosts_is_active': Quote.objects.all().first()})
                             
def home_birthdays(request):
    return render(request, 'home_birthdays.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 ### queryset below is not working
                 'all_quotes_birthdays': Quote.objects.filter(episode__publication_date=today),
                 'home_birthdays_is_active': Quote.objects.all().first()})

def podcast_hot(request, podcast_id):
    return render(request, 'podcast_hot.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 # Implement some kind of trending algorithm with exponential decay
                 # 'podcast_all_quotes_hot': Quote.objects.filter(),
                 'podcast_hot_is_active': Quote.objects.all().first()})
                             
def podcast_not(request, podcast_id):
    return render(request, 'podcast_not.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 # Reverse the hot algorithm results to determine not sorting
                 # 'podcast_all_quotes_not': Quote.objects.filter(),
                 'podcast_not_is_active': Quote.objects.all().first()})
                             
def podcast_controversial(request, podcast_id):
    return render(request, 'podcast_controversial.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 # Algorithm showing quotes that are diametrically in the middle of hot/not, with higher ranking going to quotes with the most overall votes
                 # 'podcast_all_quotes_controversial': Quote.objects.filter(),
                 'podcast_controversial_is_active': Quote.objects.all().first()})
                             
def podcast_new(request, podcast_id):
    return render(request, 'podcast_new.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 # Return quotes ordered by newest to oldest
                 'podcast_all_quotes_new': Quote.objects.order_by('-created_at'),
                 'podcast_new_is_active': Quote.objects.all().first()})

def podcast_top(request, podcast_id):
    return render(request, 'podcast_top.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 # Return quotes ordered by highest score to lowest score
                 'podcast_all_quotes_top': Quote.objects.annotate(vote_score=Sum('vote__vote_type')).order_by('-vote_score'),
                 'podcast_top_is_active': Quote.objects.all().first()})
                             
def podcast_bottom(request, podcast_id):
    return render(request, 'podcast_bottom.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 # Return quotes ordered by lowest score to highest score
                 'podcast_all_quotes_bottom': Quote.objects.annotate(vote_score=Sum('vote__vote_type')).order_by('vote_score'),
                 'podcast_bottom_is_active': Quote.objects.all().first()})
                             
def podcast_mainstream(request, podcast_id):
    return render(request, 'podcast_mainstream.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 # Return quotes ordered by total number of votes
                 'podcast_all_quotes_mainstream': Quote.objects.annotate(vote_total=Count('vote__vote_type')).order_by('vote_total'),
                 'podcast_mainstream_is_active': Quote.objects.all().first()})
                             
def podcast_underground(request, podcast_id):
    return render(request, 'podcast_underground.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 # Return quotes ordered by the ratio of upvotes to downvotes they have received (maybe 90% upvote to 10% downvote?) but limit query to only quotes that have received less than a certain # of votes...the # could be 10, 20, 50, etc. depending how how active the site is. Perhaps the # of votes could be 10% of whatever the average top quote of the day receives...
                 # 'podcast_all_quotes_underground': Quote.objects.filter(),
                 'podcast_underground_is_active': Quote.objects.all().first()})
                             
def podcast_chronological(request, podcast_id):
    return render(request, 'podcast_chronological.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 # Return quotes ordered by the time the quote begins in the podcast
                 'podcast_all_quotes_chronological': Quote.objects.order_by('time_quote_begins'),
                 'podcast_chronological_is_active': Quote.objects.all().first()})
                             
def podcast_ghosts(request, podcast_id):
    return render(request, 'podcast_ghosts.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 # Return quotes that have received no votes
                 # 'podcast_all_quotes_ghosts': Quote.objects.annotate(),
                 'podcast_ghosts_is_active': Quote.objects.all().first()})
                             
def podcast_birthdays(request, podcast_id):
    return render(request, 'podcast_birthdays.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'podcast_all_quotes_birthdays': Quote.objects.filter(episode__publication_date=today),
                 'podcast_birthdays_is_active': Quote.objects.all().first()})

def episode_hot(request, podcast_id, episode_id):
    return render(request, 'episode_hot.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'episode': Episode.objects.get(id=episode_id),
                 # Implement some kind of trending algorithm with exponential decay
                 # 'episode_all_quotes_hot': Quote.objects.filter(),
                 'episode_hot_is_active': Quote.objects.all().first()})
                             
def episode_not(request, podcast_id, episode_id):
    return render(request, 'episode_not.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'episode': Episode.objects.get(id=episode_id),
                 # Reverse the hot algorithm results to determine not sorting
                 # 'episode_all_quotes_not': Quote.objects.filter(),
                 'episode_not_is_active': Quote.objects.all().first()})
                             
def episode_controversial(request, podcast_id, episode_id):
    return render(request, 'episode_controversial.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'episode': Episode.objects.get(id=episode_id),
                 # Algorithm showing quotes that are diametrically in the middle of hot/not, with higher ranking going to quotes with the most overall votes
                 # 'episode_all_quotes_controversial': Quote.objects.filter(),
                 'episode_controversial_is_active': Quote.objects.all().first()})
                             
def episode_new(request, podcast_id, episode_id):
    return render(request, 'episode_new.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'episode': Episode.objects.get(id=episode_id),
                 # Return quotes ordered by newest to oldest
                 'episode_all_quotes_new': Quote.objects.order_by('-created_at'),
                 'episode_new_is_active': Quote.objects.all().first()})

def episode_top(request, podcast_id, episode_id):
    return render(request, 'episode_top.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'episode': Episode.objects.get(id=episode_id),
                 # Return quotes ordered by highest score to lowest score
                 'episode_all_quotes_top': Quote.objects.annotate(vote_score=Sum('vote__vote_type')).order_by('-vote_score'),
                 'episode_top_is_active': Quote.objects.all().first()})
                             
def episode_bottom(request, podcast_id, episode_id):
    return render(request, 'episode_bottom.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'episode': Episode.objects.get(id=episode_id),
                 # Return quotes ordered by lowest score to highest score
                 'episode_all_quotes_bottom': Quote.objects.annotate(vote_score=Sum('vote__vote_type')).order_by('vote_score'),
                 'episode_bottom_is_active': Quote.objects.all().first()})
                             
def episode_mainstream(request, podcast_id, episode_id):
    return render(request, 'episode_mainstream.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'episode': Episode.objects.get(id=episode_id),
                 # Return quotes ordered by total number of votes
                 'episode_all_quotes_mainstream': Quote.objects.annotate(vote_total=Count('vote__vote_type')).order_by('vote_total'),
                 'episode_mainstream_is_active': Quote.objects.all().first()})
                             
def episode_underground(request, podcast_id, episode_id):
    return render(request, 'episode_underground.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'episode': Episode.objects.get(id=episode_id),
                 # Return quotes ordered by the ratio of upvotes to downvotes they have received (maybe 90% upvote to 10% downvote?) but limit query to only quotes that have received less than a certain # of votes...the # could be 10, 20, 50, etc. depending how how active the site is. Perhaps the # of votes could be 10% of whatever the average top quote of the day receives...
                 # 'episode_all_quotes_underground': Quote.objects.filter(),
                 'episode_underground_is_active': Quote.objects.all().first()})
                             
def episode_chronological(request, podcast_id, episode_id):
    return render(request, 'episode_chronological.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'episode': Episode.objects.get(id=episode_id),
                 # Return quotes ordered by the time the quote begins in the podcast
                 'episode_all_quotes_chronological': Quote.objects.order_by('time_quote_begins'),
                 'episode_chronological_is_active': Quote.objects.all().first()})
                             
def episode_ghosts(request, podcast_id, episode_id):
    return render(request, 'episode_ghosts.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'episode': Episode.objects.get(id=episode_id),
                 # Return quotes that have received no votes
                 # 'episode_all_quotes_ghosts': Quote.objects.annotate(),
                 'episode_ghosts_is_active': Quote.objects.all().first()})
                             
def episode_birthdays(request, podcast_id, episode_id):
    return render(request, 'episode_birthdays.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id),
                 'episode': Episode.objects.get(id=episode_id),
                 'episode_all_quotes_birthdays': Quote.objects.filter(episode__publication_date=today),
                 'episode_birthdays_is_active': Quote.objects.all().first()})
                 
from quotes_app.services import PodcastSyndicationService

podcast_syndication_service = PodcastSyndicationService()

@login_required
def update_feed(request, podcast_id):
    p = get_object_or_404(Podcast, pk=podcast_id)

    podcast_syndication_service.collect_episodes(p)
    
    return HttpResponseRedirect("/")

@login_required
def vote(request, quote_id, vote_type_id):
    q = get_object_or_404(Quote, pk=quote_id)
    v = get_object_or_404(User, pk=request.user.id)
    t = int(vote_type_id)
    vote, created = Vote.objects.get_or_create(voter=v, quote=q)
    if vote.vote_type == 1 and t == 1:
        vote.vote_type = 0
    elif vote.vote_type == 1 and t == -1:
        vote.vote_type = -1
    elif vote.vote_type == -1 and t == -1:
        vote.vote_type = 0
    elif vote.vote_type == -1 and t == 1:
        vote.vote_type = 1
    else:
        vote.vote_type = t
    vote.save()
    return HttpResponseRedirect('/')

class PodcastCreateView(CreateView):
    model = Podcast
    form_class = PodcastCreateForm
    context_object_name = 'podcast'
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(PodcastCreateView, self).dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        rss_url = form.cleaned_data['rss_url']
        feed = feedparser.parse(rss_url).feed
        try:
            obj = Podcast.objects.get(title=feed.title)
            url = obj.get_absolute_url()
            return HttpResponseRedirect(url)
        except ObjectDoesNotExist:
            pass
        self.object.title = feed.title
        self.object.description = feed.description
        self.object.homepage = feed.link
        self.object.save()
        p = Podcast.objects.get(id=self.object.id)
        podcast_syndication_service.collect_episodes(p)
        return HttpResponseRedirect(self.get_success_url())

def getSec(hhmmss):
    l = map(int, hhmmss.split(':'))
    return sum(n * sec for n, sec in zip(l[::-1], (1, 60, 3600)))

@login_required
def quote_create(request):
    if request.method == "POST":
        qform = QuoteCreateForm(request.POST, instance=Quote())
        qform.data['submitted_by'] = request.user.id
        begins_with_delims = qform.data['time_quote_begins']
        qform.data['time_quote_begins'] = getSec(begins_with_delims)
        ends_with_delims = qform.data['time_quote_ends']
        qform.data['time_quote_ends'] = getSec(ends_with_delims)
        if qform.is_valid():
            new_quote = qform.save()
            vote = Vote.create(voter=request.user, quote=new_quote, vote_type=0)
            vote.save()
            return HttpResponseRedirect('/')
        else:
            raise Http404
    else:
        qform = QuoteCreateForm(instance=Quote())
    
    return render(request, 'quote_create.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.all(),
                 'quote_form': qform})
    
    return render_to_response('quote_create.html', {'quote_form': qform}, context_instance=RequestContext(request))