from time import mktime
from datetime import datetime, date
import calendar
import pytz
from django.shortcuts import render_to_response, redirect, get_object_or_404, render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from quotes_app.models import Podcast, Episode, Quote, Vote
from core.forms import PodcastCreateForm, PodcastForm
from core.forms import EpisodeCreateForm, EpisodeForm
from core.forms import QuoteCreateForm, QuoteForm
from core.forms import VoteForm
import feedparser
import json

today = date.today()

def paginate(request, quote_list):
    paginator = Paginator(quote_list, 5)
    page = request.GET.get('page')
    try:
        quotes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        quotes = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page.
        quotes = paginator.page(paginator.num_pages)
    return (True, quotes)

class HomeQuoteListView(ListView):
    model = Quote
    template_name = 'home.html'
    paginate_by = 5
    
    def get_queryset(self):
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False            
        
        if f == 'hot':
            return Quote.objects.query_hot()
        elif f == 'not':
            return Quote.objects.query_not()
        elif f == 'controversial':
            return Quote.objects.query_controversial()
        elif f == 'new':
            return Quote.objects.query_new()
        elif f == 'top':
            return Quote.objects.query_top()
        elif f == 'bottom':
            return Quote.objects.query_bottom()
        elif f == 'mainstream':
            return Quote.objects.query_mainstream()
        elif f == 'underground':
            return Quote.objects.query_underground()
        elif f == 'chronological':
            return Quote.objects.query_chronological()
        elif f == 'ghosts':
            return Quote.objects.query_ghosts()
        elif f == 'birthdays':
            return Quote.objects.query_birthdays()
        else:
            return Quote.objects.query_hot()
    
    def get_context_data(self, **kwargs):
        context = super(HomeQuoteListView, self).get_context_data(**kwargs)
        
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False   
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all()
        
        # these allow the template to know if a breadcrumb should be displayed within quote divs
        context['is_home_page'] = True
        context['is_podcast_page'] = False
        context['is_episode_page'] = False
        
        # these allow the template to know which nav button (hot, not, top, etc.) to display as active
        context['home_hot_is_active'] = False
        context['home_not_is_active'] = False
        context['home_controversial_is_active'] = False
        context['home_new_is_active'] = False
        context['home_top_is_active'] = False
        context['home_bottom_is_active'] = False
        context['home_mainstream_is_active'] = False
        context['home_underground_is_active'] = False
        context['home_chronological_is_active'] = False
        context['home_ghosts_is_active'] = False
        context['home_birthdays_is_active'] = False
        
        if f == 'hot':
            context['home_hot_is_active'] = True
        elif f == 'not':
            context['home_not_is_active'] = True
        elif f == 'controversial':
            context['home_controversial_is_active'] = True
        elif f == 'new':
            context['home_new_is_active'] = True
        elif f == 'top':
            context['home_top_is_active'] = True
        elif f == 'bottom':
            context['home_bottom_is_active'] = True
        elif f == 'mainstream':
            context['home_mainstream_is_active'] = True
        elif f == 'underground':
            context['home_underground_is_active'] = True
        elif f == 'chronological':
            context['home_chronological_is_active'] = True
        elif f == 'ghosts':
            context['home_ghosts_is_active'] = True
        elif f == 'birthdays':
            context['home_birthdays_is_active'] = True
        else:
            context['home_hot_is_active'] = True
        
        return context

class PodcastQuoteListView(ListView):
    model = Quote
    template_name = 'podcast_detail.html'
    paginate_by = 5
    
    def get_queryset(self):
        p = get_object_or_404(Podcast, id=self.kwargs['pk'])
        f = self.kwargs['query_filter']
        
        if f == 'hot':
            return Quote.objects.query_hot().filter(episode__podcast_id=p.id)
        elif f == 'not':
            return Quote.objects.query_not().filter(episode__podcast_id=p.id)
        elif f == 'controversial':
            return Quote.objects.query_controversial().filter(episode__podcast_id=p.id)
        elif f == 'new':
            return Quote.objects.query_new().filter(episode__podcast_id=p.id)
        elif f == 'top':
            return Quote.objects.query_top().filter(episode__podcast_id=p.id)
        elif f == 'bottom':
            return Quote.objects.query_bottom().filter(episode__podcast_id=p.id)
        elif f == 'mainstream':
            return Quote.objects.query_mainstream().filter(episode__podcast_id=p.id)
        elif f == 'underground':
            return Quote.objects.query_underground().filter(episode__podcast_id=p.id)
        elif f == 'chronological':
            return Quote.objects.query_chronological().filter(episode__podcast_id=p.id)
        elif f == 'ghosts':
            return Quote.objects.query_ghosts().filter(episode__podcast_id=p.id)
        elif f == 'birthdays':
            return Quote.objects.query_birthdays().filter(episode__podcast_id=p.id)
        else:
            return Quote.objects.query_hot().filter(episode__podcast_id=p.id)

    def get_context_data(self, **kwargs):
        context = super(PodcastQuoteListView, self).get_context_data(**kwargs)
        
        f = self.kwargs['query_filter']
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all()
        
        context['podcast'] = Podcast.objects.get(id=self.kwargs['pk'])
        context['episodes'] = Episode.objects.filter(podcast_id=self.kwargs['pk'])
        
        context['is_home_page'] = False
        context['is_podcast_page'] = True
        context['is_episode_page'] = False
        
        ### these allow the template to know which nav button (hot, not, top, etc.) to display as active
        context['podcast_hot_is_active'] = False
        context['podcast_not_is_active'] = False
        context['podcast_controversial_is_active'] = False
        context['podcast_new_is_active'] = False
        context['podcast_top_is_active'] = False
        context['podcast_bottom_is_active'] = False
        context['podcast_mainstream_is_active'] = False
        context['podcast_underground_is_active'] = False
        context['podcast_chronological_is_active'] = False
        context['podcast_ghosts_is_active'] = False
        context['podcast_birthdays_is_active'] = False
        
        if f == 'hot':
            context['podcast_hot_is_active'] = True
        elif f == 'not':
            context['podcast_not_is_active'] = True
        elif f == 'controversial':
            context['podcast_controversial_is_active'] = True
        elif f == 'new':
            context['podcast_new_is_active'] = True
        elif f == 'top':
            context['podcast_top_is_active'] = True
        elif f == 'bottom':
            context['podcast_bottom_is_active'] = True
        elif f == 'mainstream':
            context['podcast_mainstream_is_active'] = True
        elif f == 'underground':
            context['podcast_underground_is_active'] = True
        elif f == 'chronological':
            context['podcast_chronological_is_active'] = True
        elif f == 'ghosts':
            context['podcast_ghosts_is_active'] = True
        elif f == 'birthdays':
            context['podcast_birthdays_is_active'] = True
        else:
            pass
        
        return context
        
class EpisodeQuoteListView(ListView):
    model = Quote
    template_name = 'episode_detail.html'
    paginate_by = 5

    def get_queryset(self):
        e = get_object_or_404(Episode, id=self.kwargs['pk'])
        f = self.kwargs['query_filter']
        
        if f == 'hot':
            return Quote.objects.query_hot().filter(episode_id=e.id)
        elif f == 'not':
            return Quote.objects.query_not().filter(episode_id=e.id)
        elif f == 'controversial':
            return Quote.objects.query_controversial().filter(episode_id=e.id)
        elif f == 'new':
            return Quote.objects.query_new().filter(episode_id=e.id)
        elif f == 'top':
            return Quote.objects.query_top().filter(episode_id=e.id)
        elif f == 'bottom':
            return Quote.objects.query_bottom().filter(episode_id=e.id)
        elif f == 'mainstream':
            return Quote.objects.query_mainstream().filter(episode_id=e.id)
        elif f == 'underground':
            return Quote.objects.query_underground().filter(episode_id=e.id)
        elif f == 'chronological':
            return Quote.objects.query_chronological().filter(episode_id=e.id)
        elif f == 'ghosts':
            return Quote.objects.query_ghosts().filter(episode_id=e.id)
        elif f == 'birthdays':
            return Quote.objects.query_birthdays().filter(episode_id=e.id)
        else:
            return Quote.objects.query_hot().filter(episode_id=e.id)
        
    def get_context_data(self, **kwargs):
        context = super(EpisodeQuoteListView, self).get_context_data(**kwargs)
        
        e = get_object_or_404(Episode, id=self.kwargs['pk'])
        podcast_id = e.podcast.id
        f = self.kwargs['query_filter']
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all()
        
        context['podcast'] = Podcast.objects.get(id=e.podcast.id)
        context['episodes'] = Episode.objects.filter(podcast_id=self.kwargs['pk'])
        context['episode'] = Episode.objects.get(id=self.kwargs['pk'])
        
        context['is_home_page'] = False
        context['is_podcast_page'] = False
        context['is_episode_page'] = True
        
        ### these allow the template to know which nav button (hot, not, top, etc.) to display as active
        context['episode_hot_is_active'] = False
        context['episode_not_is_active'] = False
        context['episode_controversial_is_active'] = False
        context['episode_new_is_active'] = False
        context['episode_top_is_active'] = False
        context['episode_bottom_is_active'] = False
        context['episode_mainstream_is_active'] = False
        context['episode_underground_is_active'] = False
        context['episode_chronological_is_active'] = False
        context['episode_ghosts_is_active'] = False
        context['episode_birthdays_is_active'] = False
        
        if f == 'hot':
            context['episode_hot_is_active'] = True
        elif f == 'not':
            context['episode_not_is_active'] = True
        elif f == 'controversial':
            context['episode_controversial_is_active'] = True
        elif f == 'new':
            context['episode_new_is_active'] = True
        elif f == 'top':
            context['episode_top_is_active'] = True
        elif f == 'bottom':
            context['episode_bottom_is_active'] = True
        elif f == 'mainstream':
            context['episode_mainstream_is_active'] = True
        elif f == 'underground':
            context['episode_underground_is_active'] = True
        elif f == 'chronological':
            context['episode_chronological_is_active'] = True
        elif f == 'ghosts':
            context['episode_ghosts_is_active'] = True
        elif f == 'birthdays':
            context['episode_birthdays_is_active'] = True
        else:
            pass
        
        return context

def home_hot(request):
    return render(request, 'home_hot.html',
                 {'podcasts': Podcast.objects.all(),
                 # Implement some kind of trending algorithm with exponential decay
                 # 'all_quotes_hot': Quote.objects.filter(),
                 'home_hot_is_active': 1,
                 'is_home_page': 1})
                             
def home_not(request):
    return render(request, 'home_not.html',
                 {'podcasts': Podcast.objects.all(),
                 # Reverse the hot algorithm results to determine not sorting
                 # 'all_quotes_not': Quote.objects.filter(),
                 'home_not_is_active': 1,
                 'is_home_page': 1})
                             
def home_controversial(request):
    return render(request, 'home_controversial.html',
                 {'podcasts': Podcast.objects.all(),
                 # Algorithm showing quotes that are diametrically in the middle of hot/not, with higher ranking going to quotes with the most overall votes
                 # 'all_quotes_controversial': Quote.objects.filter(),
                 'home_controversial_is_active': 1,
                 'is_home_page': 1})
                             
def home_new(request):
    # Return quotes ordered by newest to oldest
    quote_list = Quote.objects.order_by('-created_at')
    
    success, quotes = paginate(request, quote_list)
    
    return render(request, 'home_new.html',
                 {'podcasts': Podcast.objects.all(),
                 'quotes': quotes,
                 'home_new_is_active': 1,
                 'is_home_page': 1})

def home_top(request):
    # Return quotes ordered by highest score to lowest score
    quote_list = Quote.objects.annotate(vote_score=Sum('vote__vote_type')).order_by('-vote_score')
    
    success, quotes = paginate(request, quote_list)
    
    return render(request, 'home_top.html',
                 {'podcasts': Podcast.objects.all(),
                 'quotes': quotes,
                 'home_top_is_active': 1,
                 'is_home_page': 1})

def home_bottom(request):
    # Return quotes ordered by lowest score to highest score
    quote_list = Quote.objects.annotate(vote_score=Sum('vote__vote_type')).order_by('vote_score')
    
    success, quotes = paginate(request, quote_list)
    
    return render(request, 'home_bottom.html',
                 {'podcasts': Podcast.objects.all(),
                 'quotes': quotes,
                 'home_bottom_is_active': 1,
                 'is_home_page': 1})
                             
def home_underground(request):
    return render(request, 'home_underground.html',
                 {'podcasts': Podcast.objects.all(),
                 # Return quotes ordered by the ratio of upvotes to downvotes they have received (maybe 90% upvote to 10% downvote?) but limit query to only quotes that have received less than a certain # of votes...the # could be 10, 20, 50, etc. depending how how active the site is. Perhaps the # of votes could be 10% of whatever the average top quote of the day receives...
                 # 'all_quotes_underground': Quote.objects.filter(),
                 'home_underground_is_active': 1,
                 'is_home_page': 1})

                             
def home_ghosts(request):
    return render(request, 'home_ghosts.html',
                 {'podcasts': Podcast.objects.all(),
                 # Return quotes that have received no votes
                 # 'all_quotes_ghosts': Quote.objects.annotate(),
                 'home_ghosts_is_active': 1,
                 'is_home_page': 1})
                             
def home_birthdays(request):
    return render(request, 'home_birthdays.html',
                 {'podcasts': Podcast.objects.all(),
                 # Return quotes that were publicized on the same month/day as today in any year
                 # 'quotes': Quote.objects.filter(),
                 'home_birthdays_is_active': 1,
                 'is_home_page': 1})

                 # Implement some kind of trending algorithm with exponential decay
                 # 'podcast_all_quotes_hot': Quote.objects.filter(),
                             
def episode_hot(request, podcast_id, episode_id):
    return render(request, 'episode_hot.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'episode': Episode.objects.get(id=episode_id),
                 # Implement some kind of trending algorithm with exponential decay
                 # 'episode_all_quotes_hot': Quote.objects.filter(),
                 'episode_hot_is_active': 1})
                             
def episode_not(request, podcast_id, episode_id):
    return render(request, 'episode_not.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'episode': Episode.objects.get(id=episode_id),
                 # Reverse the hot algorithm results to determine not sorting
                 # 'episode_all_quotes_not': Quote.objects.filter(),
                 'episode_not_is_active': 1})
                             
def episode_controversial(request, podcast_id, episode_id):
    return render(request, 'episode_controversial.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'episode': Episode.objects.get(id=episode_id),
                 # Algorithm showing quotes that are diametrically in the middle of hot/not, with higher ranking going to quotes with the most overall votes
                 # 'episode_all_quotes_controversial': Quote.objects.filter(),
                 'episode_controversial_is_active': 1})
                             
def episode_new(request, podcast_id, episode_id):
    # Return quotes ordered by newest to oldest
    quote_list = Quote.objects.filter(episode_id=episode_id).order_by('-created_at')
    
    success, quotes = paginate(request, quote_list)
        
    return render(request, 'episode_new.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'episode': Episode.objects.get(id=episode_id),
                 'quotes': quotes,
                 'episode_new_is_active': 1})
                 
def episode_top(request, podcast_id, episode_id):
    # Return quotes ordered by highest score to lowest score
    quote_list = Quote.objects.filter(episode_id=episode_id).annotate(vote_score=Sum('vote__vote_type')).order_by('-vote_score')
    
    success, quotes = paginate(request, quote_list)
    
    return render(request, 'episode_top.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'episode': Episode.objects.get(id=episode_id),
                 'quotes': quotes,
                 'episode_top_is_active': 1})
                             
def episode_bottom(request, podcast_id, episode_id):
    # Return quotes ordered by lowest score to highest score
    quote_list = Quote.objects.annotate(vote_score=Sum('vote__vote_type')).order_by('vote_score')
    
    success, quotes = paginate(request, quote_list)
    
    return render(request, 'episode_bottom.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'episode': Episode.objects.get(id=episode_id),
                 'quotes': quotes,
                 'episode_bottom_is_active': 1})
                             
def episode_mainstream(request, podcast_id, episode_id):
    # Return quotes ordered by total number of votes
    quote_list = Quote.objects.annotate(vote_total=Count('vote__vote_type')).order_by('vote_total')
    
    success, quotes = paginate(request, quote_list)
    
    return render(request, 'episode_mainstream.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'episode': Episode.objects.get(id=episode_id),
                 'quotes': quotes,
                 'episode_mainstream_is_active': 1})
                             
def episode_underground(request, podcast_id, episode_id):
    return render(request, 'episode_underground.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'episode': Episode.objects.get(id=episode_id),
                 # Return quotes ordered by the ratio of upvotes to downvotes they have received (maybe 90% upvote to 10% downvote?) but limit query to only quotes that have received less than a certain # of votes...the # could be 10, 20, 50, etc. depending how how active the site is. Perhaps the # of votes could be 10% of whatever the average top quote of the day receives...
                 # 'episode_all_quotes_underground': Quote.objects.filter(),
                 'episode_underground_is_active': 1})
                             
def episode_chronological(request, podcast_id, episode_id):
    # Return quotes ordered by the time the quote begins in the podcast
    quote_list = Quote.objects.filter(episode_id=episode_id).order_by('time_quote_begins')
    
    success, quotes = paginate(request, quote_list)
    
    return render(request, 'episode_chronological.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'episode': Episode.objects.get(id=episode_id),
                 'quotes': quotes,
                 'episode_chronological_is_active': 1})
                             
def episode_ghosts(request, podcast_id, episode_id):
    return render(request, 'episode_ghosts.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'episode': Episode.objects.get(id=episode_id),
                 # Return quotes that have received no votes
                 # 'episode_all_quotes_ghosts': Quote.objects.annotate(),
                 'episode_ghosts_is_active': 1})
                             
def episode_birthdays(request, podcast_id, episode_id):
    return render(request, 'episode_birthdays.html',
                 {'podcasts': Podcast.objects.all(),
                 'podcast': Podcast.objects.get(id=podcast_id),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'episode': Episode.objects.get(id=episode_id),
                 # 'episode_all_quotes_birthdays': Quote.objects.filter(),
                 'episode_birthdays_is_active': 1})
                 
def quote(request, podcast_id, episode_id, quote_id):
    return render(request, 'quote.html',
                 {'podcasts': Podcast.objects.all(),
                 'episodes': Episode.objects.filter(podcast_id=podcast_id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'quote': Quote.objects.get(id=quote_id),
                 'is_quote_page': 1})
                 
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
        qform.data['rank_score'] = 0.0
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
                 'quote_form': qform})
    
    return render_to_response('quote_create.html', {'quote_form': qform}, context_instance=RequestContext(request))
    
class JSONFormMixin(object):
    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict), content_type='application/json')
        response.status = 200 if valid_form else 500
        return response
    
class VoteFormBaseView(FormView):
    form_class = VoteForm
    
    def create_response(self, vdict=dict(), valid_form=True):
        response = HttpResponse(json.dumps(vdict))
        response.status = 200 if valid_form else 500
        return response
    
    def form_valid(self, form):
        quote = get_object_or_404(Quote, pk=form.data["quote"])
        voter = get_object_or_404(User, pk=self.request.user.id)
        t = int(form.data["vote_type"])
        prev_votes = Vote.objects.filter(quote=quote, voter=voter)
        has_voted = (len(prev_votes) >0)
        
        ret = {"success": 1}
        if not has_voted:
            if t == 1:
                # create upvote
                v = Vote.objects.create(quote=quote, voter=voter, vote_type=t)
                ret["newupvoteobj"] = v.id
            elif t == -1:
                # create downvote
                v = Vote.objects.create(quote=quote, voter=voter, vote_type=t)
                ret["newdownvoteobj"] = v.id
        else:
            if prev_votes[0].vote_type == 1 and t == 1:
                prev_votes[0].delete()
                ret["un_upvoted"] = 1
            elif prev_votes[0].vote_type == 1 and t == -1:
                prev_votes[0].delete()
                v = Vote.objects.create(quote=quote, voter=voter, vote_type=t)
                ret["downvoteobj"] = v.id
            elif prev_votes[0].vote_type == -1 and t == 1:
                prev_votes[0].delete()
                v = Vote.objects.create(quote=quote, voter=voter, vote_type=t)
                ret["upvoteobj"] = v.id
            elif prev_votes[0].vote_type == -1 and t == -1:
                prev_votes[0].delete()
                ret["un_downvoted"] = 1
        return self.create_response(ret, True)
        
    def form_invalid(self, form):
        ret = {"success": 0, "form_errors": form.errors }
        return self.create_response(ret, False)
    
class VoteFormView(JSONFormMixin, VoteFormBaseView):
    pass