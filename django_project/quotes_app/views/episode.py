from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, Http404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.http import HttpResponse
from core.forms import EpisodeCreateForm, EpisodeForm
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile
import json

class EpisodeCreateView(CreateView):
    model = Episode
    template_name = 'episode_create.html'
    form_class = EpisodeForm
    
    def get_context_data(self, **kwargs):
        context = super(EpisodeCreateView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')

        return context

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
        
    def get_object(self, *args, **kwargs):
        episode = super(EpisodeUpdateView, self).get_object(*args, **kwargs)
        if self.request.user in episode.podcast.moderators.all():
            return episode
        elif self.request.user.is_superuser:
            return episode
        else:
            raise Http404

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
        
    def get_object(self, *args, **kwargs):
        episode = super(EpisodeDeleteView, self).get_object(*args, **kwargs)
        if self.request.user in episode.podcast.moderators.all():
            return episode
        elif self.request.user.is_superuser:
            return episode
        else:
            raise Http404

class EpisodeQuoteListView(ListView):
    model = Quote
    template_name = 'episode_detail.html'
    paginate_by = 10

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
        context['is_user_page'] = False
        
        ### these allow the template to know which nav button (hot, not, top, etc.) to display as active
        context['episode_hot_is_active'] = False
        context['episode_not_is_active'] = False
        context['episode_controversial_is_active'] = False
        context['episode_ordered_is_active'] = False
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
        elif f == 'ordered':
            context['episode_ordered_is_active'] = True
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
        elif f == 'ordered':
            return Quote.quote_vote_manager.query_ordered().filter(episode_id=e.id)
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

def thin_json_episode_query(request):
    
    podcast_id = request.GET.get('podcast_id')
    title_query = request.GET.get('q')
    
    if podcast_id == '' or None:
        json_payload = '[]'
        
    else:
    
        episodes_queryset = Episode.objects.filter(
            podcast_id=podcast_id,
            title__icontains=title_query).values('id', 'title')[:10]
        
        episodes = [episode for episode in episodes_queryset]
        
        json_payload = json.dumps(episodes)
    
    return HttpResponse(json_payload, content_type="application/json")
   
