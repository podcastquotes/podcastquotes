from django.shortcuts import render_to_response, redirect
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse_lazy
from podcastquotes.models import Podcast, Episode, Quote
from podcastquotes.forms import PodcastCreateForm, PodcastForm
from podcastquotes.forms import EpisodeCreateForm, EpisodeForm
from podcastquotes.forms import QuoteCreateForm, QuoteForm


def home(request):
    return render_to_response('home.html',
                              {'podcasts': Podcast.objects.all(),
                              'episodes': Episode.objects.all(),
                              'quotes': Quote.objects.all()},
                              context_instance=RequestContext(request))
                              
class PodcastDetailView(DetailView):
    model = Podcast
    context_object_name = 'podcast'
    
    def get_context_data(self, **kwargs):
        context = super(PodcastDetailView, self).get_context_data(**kwargs)
        context['podcasts'] = Podcast.objects.all()
        return context

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

class QuoteDetailView(DetailView):
    model = Quote
    context_object_name = "quote"
