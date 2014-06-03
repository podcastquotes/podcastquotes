import json
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from core.forms import QuoteForm
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile

def getSec(hhmmss):
    l = map(int, hhmmss.split(':'))
    return sum(n * sec for n, sec in zip(l[::-1], (1, 60, 3600)))

def get_episodes(request, podcast_id):
    podcast = Podcast.objects.get(pk=podcast_id)
    episodes = Episode.objects.filter(podcast=podcast)
    episode_dict = {}
    for episode in episodes:
        episode_dict[episode.id] = episode.title
    return HttpResponse(json.dumps(episode_dict), content_type="application/json")
    
class QuoteCreateView(CreateView):
    model = Quote
    template_name = 'quote_create.html'
    form_class = QuoteForm
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(QuoteCreateView, self).dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        self.object = quote = form.save(commit=False)
        quote.submitted_by = self.request.user
        quote.save()
        vote = Vote.create(voter=self.request.user, quote=quote, vote_type=0)
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
    form_class = QuoteForm
    
    def get_context_data(self, **kwargs):
        context = super(QuoteUpdateView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        context['episodes'] = Episode.objects.filter(podcast_id=self.kwargs['pk'])
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
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')

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
    # this ghastly list containing one object is needed to make Mitch's kluge
    # youtube.js file work on quote_detail pages
    q_list = Quote.objects.filter(id=quote_id)
    q_object = Quote.objects.get(id=quote_id)
    
    return render(request, 'quote.html',
                 {'podcasts': Podcast.objects.all().order_by('title'),
                 'episodes': Episode.objects.filter(podcast_id=q_object.episode.podcast.id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'quote_list': q_list,
                 'quote': q_object,
                 'is_quote_page': 1})