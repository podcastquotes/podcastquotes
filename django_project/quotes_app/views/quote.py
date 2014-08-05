import json
import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from core.forms import QuoteForm, QuoteCreateForm, QuoteUpdateForm
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile

def getSec(hhmmss):
    l = map(int, hhmmss.split(':'))
    return sum(n * sec for n, sec in zip(l[::-1], (1, 60, 3600)))
 
class QuoteCreateView(CreateView):
    model = Quote
    template_name = 'quote_create.html'
    form_class = QuoteCreateForm
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(QuoteCreateView, self).dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        self.object = quote = form.save(commit=False)
        quote.submitted_by = self.request.user
        if quote.time_quote_begins == 0 and quote.time_quote_ends is None:
            # Redirect to full episode clip page if the full episode clip already exists
            try:
                obj = Quote.objects.get(episode__id=quote.episode.id, is_full_episode=True)
                url = obj.get_absolute_url()
                return HttpResponseRedirect(url)
            except ObjectDoesNotExist:
                pass
                
            quote.summary = quote.episode.title
            quote.text = quote.episode.description
            quote.is_full_episode = True
            
        quote.save()
        vote = Vote.create(voter=self.request.user, quote=quote, vote_type=1)
        vote.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super(QuoteCreateView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        return context
    
    """
    THIS FUNCTION IS FLAWED. IF A URI HAS ?eid=### IN IT, THEN YOU CANNOT CHANGE THE
    PODCAST/EPISODE TO CREATE A QUOTE FOR A PODCAST/EPISODE OTHER THAN THE ONE SPECIFIED
    IN THE URI
    def get_episode_id(self):
        #
        # Robustly obtains a valid Episode id from the 'eid' uri param.
        # Returns None if it isn't valid (blank/not-exist/garbage/etc)
        #
        
        eid = None
        
        try:
            eid_uri_param = self.request.GET.get('eid')
            
            # Quit if the param doesn't exist
            if eid_uri_param == None:
                return None
            
            # Convert to int
            eid = int(eid_uri_param)
            
            # Quit if episode doesn't exist
            if not Episode.objects.filter(id=eid).exists():
                return None
            
        except ValueError:
            pass
            
        return eid
    
    def get_initial(self):
        #
        # Called in the Django view pipeline to obtain initial data for
        # a form.
        #
        return_val = {}
        
        episode_id = self.get_episode_id()
        
        if episode_id != None:
            return_val['episode'] = episode_id
        
        return return_val
    """
    
class QuoteUpdateView(UpdateView):
    model = Quote
    template_name = 'quote_update.html'
    form_class = QuoteUpdateForm
    
    class Meta:
        model = Quote
        exclude = ['episode', 'is_full_episode']
    
    def get_context_data(self, **kwargs):
        context = super(QuoteUpdateView, self).get_context_data(**kwargs)
        
        q = get_object_or_404(Quote, id=self.kwargs['pk'])
        podcast_id = q.episode.podcast.id
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['podcast'] = Podcast.objects.get(id=q.episode.podcast.id)
        
        all_episodes = Episode.objects.filter(podcast_id=podcast_id).order_by('-publication_date')
        context['episodes'] = all_episodes
        
        context['episode'] = Episode.objects.get(id=q.episode.id)        
        return context
    
    def form_valid(self, form):
        self.object = quote = form.save(commit=False)
        quote.submitted_by = self.request.user
        
        if quote.time_quote_begins == 0 and quote.time_quote_ends is None:
            # Redirect to full episode clip page if the full episode clip already exists
            try:
                obj = Quote.objects.get(episode__id=quote.episode.id, is_full_episode=True)
                url = obj.get_absolute_url()
                return HttpResponseRedirect(url)
            except ObjectDoesNotExist:
                pass
            quote.is_full_episode = True
            
        quote.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_initial(self):
        q = Quote.objects.get(id=self.kwargs['pk'])
        return { 'podcast': q.episode.podcast, 'time_quote_begins': q.converted_time_begins, 'time_quote_ends': q.converted_time_ends }
    
    def get_object(self, *args, **kwargs):
        quote = super(QuoteUpdateView, self).get_object(*args, **kwargs)
        q = get_object_or_404(Quote, id=self.kwargs['pk'])

        if q.episode.podcast.slug != self.kwargs['podcast_slug']:
            return Http404
        
        if self.request.user == quote.submitted_by:
            return quote
        elif self.request.user.is_superuser:
            return quote
        else:
            raise Http404

class QuoteDeleteView(DeleteView):
    model = Quote
    context_object_name = 'quote'
    success_url = reverse_lazy('home')
    template_name = 'quote_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super(QuoteDeleteView, self).get_context_data(**kwargs)
        
        q = get_object_or_404(Quote, id=self.kwargs['pk'])
        podcast_id = q.episode.podcast.id
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['podcast'] = Podcast.objects.get(id=q.episode.podcast.id)
        
        all_episodes = Episode.objects.filter(podcast_id=podcast_id).order_by('-publication_date')
        context['episodes'] = all_episodes

        return context
        
    def get_object(self, *args, **kwargs):
        quote = super(QuoteDeleteView, self).get_object(*args, **kwargs)
        q = get_object_or_404(Quote, id=self.kwargs['pk'])
        if q.episode.podcast.slug != self.kwargs['podcast_slug']:
            return Http404
            
        if self.request.user == quote.submitted_by:
            return quote
        elif self.request.user.is_superuser:
            return quote
        else:
            raise Http404

def quote(request, quote_id, podcast_slug):
    ### TechDebt - list containing one object is needed to make
    # Mitch's kluge youtube.js file work on quote_detail pages
    q = get_object_or_404(Quote, id=quote_id)
    if q.episode.podcast.slug != podcast_slug:
        return Http404
    
    q_pseudo_list = Quote.objects.filter(id=quote_id)
    q_object = Quote.objects.get(id=quote_id)
    
    q_objects = Quote.objects.filter(episode_id=q_object.episode.id).order_by('time_quote_begins')
    
    for idx, item in enumerate(q_objects):
        if item == q_object:
            q_object_index = idx
        else:
            pass
    
    q_object_prev = None
    q_object_next = None
    
    for idx, item in enumerate(q_objects):
        if idx == q_object_index - 1:
            q_object_prev = item
        if idx == q_object_index + 1:
            q_object_next = item
            break
    
    """
    all_karma_leaders = sorted(User.objects.exclude(id=1), key = lambda u: u.userprofile.leaderboard_karma_total, reverse=True)
    
    # take only the top 5 karma_leaders
    all_karma_leaders = all_karma_leaders[:5]
    
    # remove the users who have submitted 0 quotes
    # they may not want to have their username public
    all_karma_leaders = [i for i in all_karma_leaders if i.userprofile.leaderboard_karma_total != None]
    """
    
    all_episodes = Episode.objects.filter(podcast_id=q_object.episode.podcast_id).order_by('-publication_date')
    
    # this gives the top quotes that appear a degree of randomness
    more_episode_quotes = sorted(Quote.quote_vote_manager.query_top().exclude(is_full_episode=True).filter(episode_id=q_object.episode.id)[:10], key=lambda x: random.random())
    more_episode_quotes = more_episode_quotes[:10]
    
    # this gives the top quotes that appear a degree of randomness
    more_podcast_quotes = sorted(Quote.quote_vote_manager.query_top().filter(episode__podcast_id=q_object.episode.podcast.id)[:100], key=lambda x: random.random())
    more_podcast_quotes = more_podcast_quotes[:20]
    
    return render(request, 'quote.html',
                 {'podcasts': Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True),
                 'podcast': Podcast.objects.get(id=q_object.episode.podcast.id),
                 'episodes': all_episodes,
                 # ('karma_leaders'): all_karma_leaders,
                 'quote_pseudo_list': q_pseudo_list,
                 'quote': q_object,
                 'quote_previous': q_object_prev,
                 'quote_next': q_object_next,
                 'more_episode_quotes': more_episode_quotes,
                 'more_podcast_quotes': more_podcast_quotes,
                 'is_quote_page': 1})
