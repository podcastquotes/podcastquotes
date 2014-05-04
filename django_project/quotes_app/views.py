from time import mktime
from datetime import datetime
import calendar
import pytz
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.db.models import Sum
from quotes_app.models import Podcast, Episode, Quote, Vote
from core.forms import PodcastCreateForm, PodcastForm
from core.forms import EpisodeCreateForm, EpisodeForm
from core.forms import QuoteCreateForm, QuoteForm
import feedparser

def home(request):
    return render_to_response('home.html',
                             {'podcasts': Podcast.objects.all(),
                             'episodes': Episode.objects.all(),
                             'quotes': Quote.objects.annotate(vote_total=Sum('vote__vote_type')).order_by('-vote_total')},
                             context_instance=RequestContext(request))

@login_required
def update_feed(request, podcast_id):
    p = get_object_or_404(Podcast, pk=podcast_id)
    rss_feed = p.rss_url
    feed = feedparser.parse(rss_feed)

    for e in feed.entries:
        e_guid = e.guid
        episode, created = Episode.objects.get_or_create(podcast_id=podcast_id, guid=e_guid)
        episode.title = e.title
        print e.published_parsed
        episode.publication_date = datetime.fromtimestamp(calendar.timegm(e.published_parsed), tz=pytz.utc)
        episode.description = e.description
        episode.episode_url = e.link
        episode.save()

    return HttpResponseRedirect(rss_feed)

#    feed = feedparser.parse(rss_url)
    
#    info = []
#    for entry in feed.entries:
#        info.append(entry.title)
#        print info
#    return info


@login_required
def vote(request, quote_id, vote_type_id):
    q = get_object_or_404(Quote, pk=quote_id)
    v = get_object_or_404(User, pk=request.user.id)
    t = int(vote_type_id)
    vote, created = Vote.objects.get_or_create(voter=v, quote=q)
    print vote.vote_type
    print t
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

class PodcastDetailView(DetailView):
    model = Podcast
    context_object_name = 'podcast'
    
    def get_context_data(self, **kwargs):
        context = super(PodcastDetailView, self).get_context_data(**kwargs)
        context['podcasts'] = Podcast.objects.all()
        context['quotes'] = Quote.objects.filter(episode__podcast=self.get_object())
        return context

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
        self.object.title = feed.title
        self.object.description = feed.description
        self.object.homepage = feed.link
        print feed.author_detail
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
        
class EpisodeDetailView(DetailView):
    model = Episode
    context_object_name = "episode"
    
    def get_context_data(self, **kwargs):
        context = super(EpisodeDetailView, self).get_context_data(**kwargs)
        context['podcasts'] = Podcast.objects.all()
        context['podcast'] = Podcast.objects.filter(id=self.get_object().podcast.id)[0]
        context['quotes'] = Quote.objects.filter(episode__id=self.get_object().id)
        return context

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
            vote = Vote.create(voter=request.user, quote=new_quote, vote_type=1)
            vote.save()
            return HttpResponseRedirect('/')
        else:
            raise Http404
    else:
        qform = QuoteCreateForm(instance=Quote())
    return render_to_response('quote_create.html', {'quote_form': qform}, context_instance=RequestContext(request))