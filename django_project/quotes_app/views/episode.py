from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, Http404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.utils.timezone import now
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
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['podcast'] = Podcast.objects.get(id=e.podcast.id)

        return context

class EpisodeUpdateView(UpdateView):
    model = Episode
    template_name = 'episode_update.html'
    form_class = EpisodeForm
    
    def form_valid(self, form):
        self.object = episode = form.save(commit=False)
        if episode.youtube_url or episode.episode_url:
            try:
                full_episode_quote = Quote.objects.get(episode__id=episode.id, is_full_episode=True)
            except ObjectDoesNotExist:
                # user with id=1 is the user "podverse" on podverse.tv
                user = User.objects.get(id=1)
                full_episode_quote = Quote.create(submitted_by=user,
                                              rank_score=float(0.0),
                                              episode=episode,
                                              summary=episode.title,
                                              text=episode.description,
                                              time_quote_begins=int(0),
                                              is_full_episode=True)
                full_episode_quote.save()
                vote = Vote.create(voter=user, quote=full_episode_quote, vote_type=1)
                vote.save()
        episode.save()
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs):
        context = super(EpisodeUpdateView, self).get_context_data(**kwargs)
        
        e = get_object_or_404(Episode, id=self.kwargs['pk'])
        podcast_id = e.podcast.id
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['podcast'] = Podcast.objects.get(id=e.podcast.id)
        
        all_episodes = Episode.objects.filter(podcast_id=podcast_id).order_by('-publication_date')
        context['episodes'] = all_episodes
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
        podcast_id = e.podcast.id
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['podcast'] = Podcast.objects.get(id=e.podcast.id)

        all_episodes = Episode.objects.filter(podcast_id=podcast_id).order_by('-publication_date')
        all_episodes_with_quotes = [i for i in all_episodes if i.all_episode_quotes_property != 0]
        
        context['episodes'] = all_episodes_with_quotes
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
    
    def get_template_names(self):
        return 'episode_detail.html'
        
    def get_paginate_by(self, queryset):
        return 20

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
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['podcast'] = Podcast.objects.get(id=e.podcast.id)
        
        all_episodes = Episode.objects.filter(podcast_id=podcast_id).order_by('-publication_date')
        
        context['episodes'] = all_episodes
        
        context['episode'] = Episode.objects.get(id=self.kwargs['pk'])
        
        """
        all_karma_leaders = sorted(User.objects.exclude(id=1), key = lambda u: u.userprofile.leaderboard_karma_total, reverse=True)
        
        # take only the top 5 karma_leaders
        all_karma_leaders = all_karma_leaders[:5]
        
        # remove the users who have submitted 0 quotes
        # they may not want to have their username public
        all_karma_leaders = [i for i in all_karma_leaders if i.userprofile.leaderboard_karma_total != None]
        
        context['karma_leaders'] = all_karma_leaders
        """
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

        if e.podcast.slug != self.kwargs['podcast_slug']:
            return Http404
        
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
            return Quote.quote_vote_manager.query_ordered('episode_highlights').filter(episode_id=e.id)
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