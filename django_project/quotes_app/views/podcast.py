from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile
from core.forms import PodcastCreateForm, PodcastForm
from django.shortcuts import get_object_or_404


from quotes_app.services import PodcastSyndicationService

podcast_syndication_service = PodcastSyndicationService()

@login_required
def update_feed(request, podcast_id):
    p = get_object_or_404(Podcast, pk=podcast_id)

    podcast_syndication_service.collect_episodes(p)
    
    return HttpResponseRedirect("/")
    
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
        podcast.rss_url = rss_url
        podcast.save()
        podcast.moderators.add(self.request.user)
        podcast.save()
        
        # Collect episodes (should be made asynchronous)
        podcast_syndication_service.collect_episodes(podcast)
        
        return HttpResponseRedirect(self.get_success_url())
        
    def get_context_data(self, **kwargs):
        context = super(PodcastCreateView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')

        return context


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
        context['is_user_page'] = False
        
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