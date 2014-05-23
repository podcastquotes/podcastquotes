from time import mktime
from datetime import datetime, date
import calendar
import pytz
from django.shortcuts import render_to_response, redirect, get_object_or_404, render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse, reverse_lazy
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

def rank_all(request):
    for quote in Quote.quote_vote_manager.all():
        quote.set_rank()

    return redirect('/')

class HomeQuoteListView(ListView):
    model = Quote
    template_name = 'home.html'
    paginate_by = 10
    
    def get_queryset(self):
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False            
        
        if f == 'hot':
            return Quote.quote_vote_manager.query_hot()
        elif f == 'not':
            return Quote.quote_vote_manager.query_not()
        elif f == 'controversial':
            return Quote.quote_vote_manager.query_controversial()
        elif f == 'new':
            return Quote.quote_vote_manager.query_new()
        elif f == 'top':
            return Quote.quote_vote_manager.query_top()
        elif f == 'bottom':
            return Quote.quote_vote_manager.query_bottom()
        elif f == 'mainstream':
            return Quote.quote_vote_manager.query_mainstream()
        elif f == 'underground':
            return Quote.quote_vote_manager.query_underground()
        elif f == 'chronological':
            return Quote.quote_vote_manager.query_chronological()
        elif f == 'ghosts':
            return Quote.quote_vote_manager.query_ghosts()
        elif f == 'birthdays':
            return Quote.quote_vote_manager.query_birthdays()
        else:
            return Quote.quote_vote_manager.query_hot()
    
    def get_context_data(self, **kwargs):
        context = super(HomeQuoteListView, self).get_context_data(**kwargs)
        
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False   
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        # these allow the template to know if a breadcrumb should be displayed within quote divs
        context['is_home_page'] = True
        context['is_podcast_page'] = False
        context['is_episode_page'] = False
        context['is_quote_page'] = False
        
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
    paginate_by = 10
    
    def get_queryset(self):
        p = get_object_or_404(Podcast, id=self.kwargs['pk'])
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        if f == 'hot':
            return Quote.quote_vote_manager.query_hot().filter(episode__podcast_id=p.id)
        elif f == 'not':
            return Quote.quote_vote_manager.query_not().filter(episode__podcast_id=p.id)
        elif f == 'controversial':
            return Quote.quote_vote_manager.query_controversial().filter(episode__podcast_id=p.id)
        elif f == 'new':
            return Quote.quote_vote_manager.query_new().filter(episode__podcast_id=p.id)
        elif f == 'top':
            return Quote.quote_vote_manager.query_top().filter(episode__podcast_id=p.id)
        elif f == 'bottom':
            return Quote.quote_vote_manager.query_bottom().filter(episode__podcast_id=p.id)
        elif f == 'mainstream':
            return Quote.quote_vote_manager.query_mainstream().filter(episode__podcast_id=p.id)
        elif f == 'underground':
            return Quote.quote_vote_manager.query_underground().filter(episode__podcast_id=p.id)
        elif f == 'chronological':
            return Quote.quote_vote_manager.query_chronological().filter(episode__podcast_id=p.id)
        elif f == 'ghosts':
            return Quote.quote_vote_manager.query_ghosts().filter(episode__podcast_id=p.id)
        elif f == 'birthdays':
            return Quote.quote_vote_manager.query_birthdays().filter(episode__podcast_id=p.id)
        else:
            return Quote.quote_vote_manager.query_hot().filter(episode__podcast_id=p.id)

    def get_context_data(self, **kwargs):
        context = super(PodcastQuoteListView, self).get_context_data(**kwargs)
        
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        context['podcast'] = Podcast.objects.get(id=self.kwargs['pk'])
        context['episodes'] = Episode.objects.filter(podcast_id=self.kwargs['pk'])
        
        context['is_home_page'] = False
        context['is_podcast_page'] = True
        context['is_episode_page'] = False
        context['is_quote_page'] = False
        
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
            context['podcast_hot_is_active'] = True
        
        return context
        
class EpisodeQuoteListView(ListView):
    model = Quote
    template_name = 'episode_detail.html'
    paginate_by = 10

    def get_queryset(self):
        e = get_object_or_404(Episode, id=self.kwargs['pk'])
        
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        if f == 'hot':
            return Quote.quote_vote_manager.query_hot().filter(episode_id=e.id)
        elif f == 'not':
            return Quote.quote_vote_manager.query_not().filter(episode_id=e.id)
        elif f == 'controversial':
            return Quote.quote_vote_manager.query_controversial().filter(episode_id=e.id)
        elif f == 'new':
            return Quote.quote_vote_manager.query_new().filter(episode_id=e.id)
        elif f == 'top':
            return Quote.quote_vote_manager.query_top().filter(episode_id=e.id)
        elif f == 'bottom':
            return Quote.quote_vote_manager.query_bottom().filter(episode_id=e.id)
        elif f == 'mainstream':
            return Quote.quote_vote_manager.query_mainstream().filter(episode_id=e.id)
        elif f == 'underground':
            return Quote.quote_vote_manager.query_underground().filter(episode_id=e.id)
        elif f == 'chronological':
            return Quote.quote_vote_manager.query_chronological().filter(episode_id=e.id)
        elif f == 'ghosts':
            return Quote.quote_vote_manager.query_ghosts().filter(episode_id=e.id)
        elif f == 'birthdays':
            return Quote.quote_vote_manager.query_birthdays().filter(episode_id=e.id)
        else:
            return Quote.quote_vote_manager.query_hot().filter(episode_id=e.id)
        
    def get_context_data(self, **kwargs):
        context = super(EpisodeQuoteListView, self).get_context_data(**kwargs)
        
        e = get_object_or_404(Episode, id=self.kwargs['pk'])
        podcast_id = e.podcast.id
        
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        context['podcast'] = Podcast.objects.get(id=e.podcast.id)
        context['episodes'] = Episode.objects.filter(podcast_id=self.kwargs['pk'])
        context['episode'] = Episode.objects.get(id=self.kwargs['pk'])
        
        context['is_home_page'] = False
        context['is_podcast_page'] = False
        context['is_episode_page'] = True
        context['is_quote_page'] = False
        
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
            context['episode_hot_is_active'] = True
        
        return context
                 
def quote(request, quote_id):
    q = Quote.objects.get(id=quote_id)
    
    return render(request, 'quote.html',
                 {'podcasts': Podcast.objects.all().order_by('title'),
                 'episodes': Episode.objects.filter(podcast_id=q.episode.podcast.id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'quote': q,
                 'is_quote_page': 1})
                 
class PodcastUpdateView(UpdateView):
    model = Podcast
    template_name = 'podcast_update.html'
    form_class = PodcastForm
    
    def get_context_data(self, **kwargs):
        context = super(PodcastUpdateView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')

        context['episodes'] = Episode.objects.filter(podcast_id=self.kwargs['pk'])
        return context
    
class PodcastDeleteView(DeleteView):
    model = Podcast
    context_object_name = 'podcast'
    success_url = reverse_lazy('home')
    template_name = 'podcast_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super(PodcastDeleteView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')

        context['episodes'] = Episode.objects.filter(podcast_id=self.kwargs['pk'])
        return context
    
class EpisodeDeleteView(DeleteView):
    model = Episode
    context_object_name = 'episode'
    success_url = reverse_lazy('home')
    template_name = 'episode_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super(EpisodeDeleteView, self).get_context_data(**kwargs)
        
        e = get_object_or_404(Episode, id=self.kwargs['pk'])
        p_id = e.podcast.id
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')

        context['episodes'] = Episode.objects.filter(podcast_id=p_id)
        return context
    
class QuoteDeleteView(DeleteView):
    model = Quote
    context_object_name = 'quote'
    success_url = reverse_lazy('home')
    template_name = 'quote_delete.html'
    
class EpisodeUpdateView(UpdateView):
    model = Episode
    template_name = 'episode_update.html'
    form_class = EpisodeForm
    
    def get_context_data(self, **kwargs):
        context = super(EpisodeUpdateView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        context['episodes'] = Episode.objects.filter(podcast_id=self.kwargs['pk'])
        return context
                 
class QuoteUpdateView(UpdateView):
    model = Quote
    template_name = 'quote_update.html'
    form_class = QuoteForm
    
    def get_initial(self):
        q = Quote.objects.get(id=self.kwargs['pk'])
        return { 'time_quote_begins': q.converted_time_begins, 'time_quote_ends': q.converted_time_ends }
    
    def get_context_data(self, **kwargs):
        context = super(QuoteUpdateView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        context['episodes'] = Episode.objects.filter(podcast_id=self.kwargs['pk'])
        return context
                 
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
        """
        This is called when a POST'ed form is valid.
        """
        
        # Create podcast model from form
        self.object = podcast = form.save(commit=False)
        
        # Parse feed
        rss_url = podcast.rss_url
        
        # Collect episodes (should be made asynchronous)
        feed = podcast_syndication_service \
            .obtain_podcast_information(rss_url)
            
        # Redirect to podcast page if the podcast already exists
        try:
            obj = Podcast.objects.get(title=feed['title'])
            url = obj.get_absolute_url()
            return HttpResponseRedirect(url)
        except ObjectDoesNotExist:
            pass
        
        # Map feed information to Podcast
        podcast.title = feed['title']
        podcast.description = feed['description']
        podcast.homepage = feed['homepage']
        podcast.save()
        
        # Collect episodes (should be made asynchronous)
        podcast_syndication_service.collect_episodes(podcast)
        
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
            return HttpResponseRedirect(reverse('quote', kwargs={'quote_id': vote.quote.id}))
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
                ret["newupvoteobj"] = 1
            elif t == -1:
                # create downvote
                v = Vote.objects.create(quote=quote, voter=voter, vote_type=t)
                ret["newdownvoteobj"] = 1
        else:
            if prev_votes[0].vote_type == 1 and t == 1:
                prev_votes[0].vote_type = 0
                ret["un_upvoted"] = 1
            elif prev_votes[0].vote_type == 1 and t == -1:
                prev_votes[0].vote_type = -1
                ret["downvoteobj"] = 1
            elif prev_votes[0].vote_type == -1 and t == 1:
                prev_votes[0].vote_type = 1
                ret["upvoteobj"] = 1
            elif prev_votes[0].vote_type == -1 and t == -1:
                prev_votes[0].vote_type = 0
                ret["un_downvoted"] = 1
            elif prev_votes[0].vote_type == 0 and t == 1:
                prev_votes[0].vote_type = 1
                ret["newupvoteobj"] = 1
            elif prev_votes[0].vote_type == 0 and t == -1:
                prev_votes[0].vote_type = -1
                ret["newdownvoteobj"] = 1
            prev_votes[0].save()
        return self.create_response(ret, True)
        
    def form_invalid(self, form):
        ret = {"success": 0, "form_errors": form.errors }
        return self.create_response(ret, False)
    
class VoteFormView(JSONFormMixin, VoteFormBaseView):
    pass
