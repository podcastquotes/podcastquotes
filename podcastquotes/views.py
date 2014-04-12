from django.shortcuts import render_to_response
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse_lazy
from podcastquotes.models import Podcast, Episode, PersonQuoted, Tag, Quote
from podcastquotes.forms import PodcastCreateForm, PodcastForm
from podcastquotes.forms import EpisodeCreateForm, EpisodeForm
from podcastquotes.forms import QuoteCreateForm, QuoteForm
from podcastquotes.forms import PersonQuotedCreateForm
from podcastquotes.forms import TagCreateForm


def home(request):
    return render_to_response('home.html',
                              {'podcasts': Podcast.objects.all(),
                              'episodes': Episode.objects.all(),
                              'quotes': Quote.objects.all()},
                              context_instance=RequestContext(request))

def podcast_create(request):
    if request.method == "POST":
        pform = PodcastCreateForm(request.POST, instance=Podcast())
        if pform.is_valid():
            new_podcast = pform.save()
            return HttpResponseRedirect('/')
        else:
            raise Http404
    else:
        pform = PodcastCreateForm(instance=Podcast())
    return render_to_response('podcast_create.html', {'podcast_form': pform}, context_instance=RequestContext(request))

class PodcastListView(ListView):
    model = Podcast

class PodcastDetailView(DetailView):
    model = Podcast
    context_object_name = 'podcast'
    
    def get_context_data(self, **kwargs):
        context = super(PodcastDetailView, self).get_context_data(**kwargs)
        context['podcasts'] = Podcast.objects.all()
        return context

class PodcastUpdateView(UpdateView):
    model = Podcast
    form_class = PodcastForm
    template_name = 'podcast_update.html'
    
    def get_context_data(self, **kwargs):
        context = super(PodcastUpdateView, self).get_context_data(**kwargs)
        context['podcasts'] = Podcast.objects.all()
        return context

class PodcastDeleteView(DeleteView):
    model = Podcast
    success_url = reverse_lazy('home')
    template_name = 'podcast_delete.html'

def episode_create(request):
    if request.method == "POST":
        eform = EpisodeCreateForm(request.POST, instance=Episode())
        if eform.is_valid():
            new_episode = eform.save()
            return HttpResponseRedirect('/')
        else:
            raise Http404
    else:
        eform = EpisodeCreateForm(instance=Episode())
    return render_to_response('episode_create.html', {'episode_form': eform}, context_instance=RequestContext(request))
    
class EpisodeListView(ListView):
    model = Episode

class EpisodeDetailView(DetailView):
    model = Episode
    context_object_name = "episode"

    def get_context_data(self, **kwargs):
        context = super(EpisodeDetailView, self).get_context_data(**kwargs)
        context['podcasts'] = Podcast.objects.all()
        return context

class EpisodeUpdateView(UpdateView):
    model = Episode
    form_class = EpisodeForm
    template_name = 'episode_update.html'
    
    def get_context_data(self, **kwargs):
        context = super(EpisodeUpdateView, self).get_context_data(**kwargs)
        context['podcasts'] = Podcast.objects.all()
        return context

class EpisodeDeleteView(DeleteView):
    model = Episode
    success_url = reverse_lazy('home')
    template_name = 'episode_delete.html'

def quote_create(request):
    if request.method == "POST":
        pform = PersonQuotedCreateForm(request.POST, instance=PersonQuoted())
        tform = TagCreateForm(request.POST, instance=Tag())
        qform = QuoteCreateForm(request.POST, instance=Quote())
        if pform.is_valid() and tform.is_valid() and qform.is_valid():
            new_personquoted = pform.save()
            new_tag = tform.save()
            new_quote = qform.save()
            return HttpResponseRedirect('/')
        else:
            raise Http404
    else:
        pform = PersonQuotedCreateForm(instance=PersonQuoted())
        tform = TagCreateForm(instance=Tag())
        qform = QuoteCreateForm(instance=Quote())
    return render_to_response('quote_create.html', {'personquoted_form': pform, 'tag_form': tform, 'quote_form': qform}, context_instance=RequestContext(request))

class QuoteListView(ListView):
    model = Quote

class QuoteDetailView(DetailView):
    model = Quote
    context_object_name = "quote"

class QuoteUpdateView(UpdateView):
    model = Quote
    form_class = QuoteForm
    template_name = 'quote_update.html'
    
    def get_context_data(self, **kwargs):
        context = super(QuoteUpdateView, self).get_context_data(**kwargs)
        context['podcasts'] = Podcast.objects.all()
        return context

class QuoteDeleteView(DeleteView):
    model = Quote
    success_url = reverse_lazy('home')
    template_name = 'quote_delete.html'