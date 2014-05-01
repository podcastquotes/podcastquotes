from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from podcastquotes.models import Podcast, Episode, Quote, Vote
from podcastquotes.forms import PodcastCreateForm, PodcastForm
from podcastquotes.forms import EpisodeCreateForm, EpisodeForm
from podcastquotes.forms import QuoteCreateForm, QuoteForm
import feedparser

def home(request):
    return render_to_response('home.html',
                             {'podcasts': Podcast.objects.all(),
                             'episodes': Episode.objects.all(),
                             'quotes': Quote.objects.annotate(vote_score=Sum('vote__vote_type')).order_by('-vote_score')},
                             context_instance=RequestContext(request))

@login_required
def vote(request, quote_id, vote_type_id):
    q = get_object_or_404(Quote, pk=quote_id)
    v = get_object_or_404(User, pk=request.user.id)
    t = vote_type_id
    vote, created = Vote.objects.get_or_create(voter=v, quote=q)
    vote.vote_type = t
    vote.save()
    return HttpResponseRedirect('/')

class PodcastDetailView(DetailView):
    model = Podcast
    context_object_name = 'podcast'
    
    def get_context_data(self, **kwargs):
        context = super(PodcastDetailView, self).get_context_data(**kwargs)
        context['podcasts'] = Podcast.objects.all()
        return context

class PodcastCreateView(CreateView):
    model = Podcast
    form_class = PodcastCreateForm
    context_object_name = 'podcast'
    
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
        return context

def getSec(hhmmss):
    l = map(int, hhmmss.split(':'))
    return sum(n * sec for n, sec in zip(l[::-1], (1, 60, 3600)))

@login_required
def quote_create(request):
    if request.method == "POST":
        qform = QuoteCreateForm(request.POST, instance=Quote())
        begins_with_delims = qform.data['time_quote_begins']
        qform.data['time_quote_begins'] = getSec(begins_with_delims)
        ends_with_delims = qform.data['time_quote_ends']
        qform.data['time_quote_ends'] = getSec(ends_with_delims)
        if qform.is_valid():
            new_quote = qform.save()
            return HttpResponseRedirect('/')
        else:
            raise Http404
    else:
        qform = QuoteCreateForm(instance=Quote())
    return render_to_response('quote_create.html', {'quote_form': qform}, context_instance=RequestContext(request))