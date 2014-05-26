from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile
from core.forms import QuoteForm
from django.shortcuts import render, render_to_response
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.utils.decorators import method_decorator

def getSec(hhmmss):
    l = map(int, hhmmss.split(':'))
    return sum(n * sec for n, sec in zip(l[::-1], (1, 60, 3600)))

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
    
    def get_initial(self):
        q = Quote.objects.get(id=self.kwargs['pk'])
        return { 'time_quote_begins': q.converted_time_begins, 'time_quote_ends': q.converted_time_ends }
    
    def get_context_data(self, **kwargs):
        context = super(QuoteUpdateView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        context['episodes'] = Episode.objects.filter(podcast_id=self.kwargs['pk'])
        return context

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

def quote(request, quote_id):
    q = Quote.objects.get(id=quote_id)
    
    return render(request, 'quote.html',
                 {'podcasts': Podcast.objects.all().order_by('title'),
                 'episodes': Episode.objects.filter(podcast_id=q.episode.podcast.id).exclude(youtube_url__exact='').order_by('-publication_date'),
                 'quote': q,
                 'is_quote_page': 1})