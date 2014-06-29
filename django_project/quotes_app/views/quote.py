import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
        quote.save()
        vote = Vote.create(voter=self.request.user, quote=quote, vote_type=1)
        vote.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super(QuoteCreateView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        return context

class QuoteUpdateView(UpdateView):
    model = Quote
    template_name = 'quote_update.html'
    form_class = QuoteUpdateForm
    
    class Meta:
        model = Quote
        exclude = ['episode']
    
    def get_context_data(self, **kwargs):
        context = super(QuoteUpdateView, self).get_context_data(**kwargs)
        
        q = get_object_or_404(Quote, id=self.kwargs['pk'])
        podcast_id = q.episode.podcast.id
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        context['podcast'] = Podcast.objects.get(id=q.episode.podcast.id)
        
        all_episodes = Episode.objects.filter(podcast_id=podcast_id).order_by('-publication_date')
        all_episodes_with_quotes = [i for i in all_episodes if i.all_episode_quotes_property != 0]
        
        context['episodes'] = all_episodes_with_quotes
        
        context['episode'] = Episode.objects.get(id=q.episode.id)        
        return context
    
    def get_initial(self):
        q = Quote.objects.get(id=self.kwargs['pk'])
        return { 'podcast': q.episode.podcast, 'time_quote_begins': q.converted_time_begins, 'time_quote_ends': q.converted_time_ends }
    
    def get_object(self, *args, **kwargs):
        quote = super(QuoteUpdateView, self).get_object(*args, **kwargs)
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
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        context['podcast'] = Podcast.objects.get(id=q.episode.podcast.id)
        
        all_episodes = Episode.objects.filter(podcast_id=podcast_id).order_by('-publication_date')
        all_episodes_with_quotes = [i for i in all_episodes if i.all_episode_quotes_property != 0]
        
        context['episodes'] = all_episodes_with_quotes

        return context
        
    def get_object(self, *args, **kwargs):
        quote = super(QuoteDeleteView, self).get_object(*args, **kwargs)
        if self.request.user == quote.submitted_by:
            return quote
        elif self.request.user.is_superuser:
            return quote
        else:
            raise Http404

def quote(request, quote_id):
    ### TechDebt - list containing one object is needed to make
    # Mitch's kluge youtube.js file work on quote_detail pages
    q_list = Quote.objects.filter(id=quote_id)
    q_object = Quote.objects.get(id=quote_id)
    
    all_karma_leaders = sorted(User.objects.all(), key = lambda u: u.userprofile.leaderboard_karma_total, reverse=True)
    
    # take only the top 5 karma_leaders
    all_karma_leaders = all_karma_leaders[:5]
    
    # remove the users who have submitted 0 quotes
    # they may not want to have their username public
    all_karma_leaders = [i for i in all_karma_leaders if i.userprofile.leaderboard_karma_total != None]
    
    all_episodes = Episode.objects.filter(podcast_id=q_object.episode.podcast_id).order_by('-publication_date')
    all_episodes_with_quotes = [i for i in all_episodes if i.all_episode_quotes_property != 0]
    
    return render(request, 'quote.html',
                 {'podcasts': Podcast.objects.all().order_by('title'),
                 'podcast': Podcast.objects.get(id=q_object.episode.podcast.id),
                 'episodes': all_episodes_with_quotes,
                 ('karma_leaders'): all_karma_leaders,
                 'quote_list': q_list,
                 'quote': q_object,
                 'more_episode_quotes': Quote.quote_vote_manager.query_hot().filter(episode_id=q_object.episode.id)[:5],
                 'more_podcast_quotes': Quote.quote_vote_manager.query_hot().filter(episode__podcast_id=q_object.episode.podcast.id)[:5],
                 'is_quote_page': 1})