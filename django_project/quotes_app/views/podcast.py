from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, Http404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.utils.decorators import method_decorator
from core.forms import PodcastCreateForm, PodcastForm
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile
from quotes_app.services import PodcastSyndicationService, save_image_from_url, get_upload_file_name
import json

podcast_syndication_service = PodcastSyndicationService()

@staff_member_required
def update_feed(request, podcast_id):
    p = get_object_or_404(Podcast, id=podcast_id)

    podcast_syndication_service.collect_episodes(p)
    
    # print podcast_syndication_service.collect_episodes(p)
    
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
        
        if feed['keywords_list'] == '':
            pass
        else:
            keywords_list = feed['keywords_list']
            
            # remove duplicates from keywords_list
            # this unique_list method is not suited for long lists
            ulist = []
            def unique_list(l):
                for x in l: 
                    keyword = x.term.lower()
                    if keyword not in ulist: 
                        ulist.append(keyword)
                return ulist
            unique_list(keywords_list)
            
            keywords = ''
            for t in ulist:
               keywords += t + ', '
            # remove the ', ' at the end of keywords string
            podcast.keywords = keywords[:-2]
        
        if feed['image_url'] == '':
            pass
        else:
        ### Tech Debt? See issue #80 in the issue tracker
            try:
                image_url = feed['image_url']
                save_image_from_url(podcast, image_url, podcast.title)
            except OSError:
                pass
        
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
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)

        return context

class PodcastUpdateView(UpdateView):
    model = Podcast
    template_name = 'podcast_update.html'
    form_class = PodcastForm
    slug_field="slug"
    
    def get_context_data(self, **kwargs):
        context = super(PodcastUpdateView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['podcast'] = Podcast.objects.get(slug=self.kwargs['slug'])
        
        all_episodes = Episode.objects.filter(podcast__slug=self.kwargs['slug']).order_by('-publication_date')
        context['episodes'] = all_episodes
        return context
        
    def get_object(self, *args, **kwargs):
        podcast = super(PodcastUpdateView, self).get_object(*args, **kwargs)
        if self.request.user in podcast.moderators.all():
            return podcast
        elif self.request.user.is_superuser:
            return podcast
        else:
            raise Http404

class PodcastDeleteView(DeleteView):
    model = Podcast
    context_object_name = 'podcast'
    success_url = reverse_lazy('home')
    template_name = 'podcast_delete.html'
    slug_field="slug"
    
    def get_context_data(self, **kwargs):
        context = super(PodcastDeleteView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['podcast'] = Podcast.objects.get(slug=self.kwargs['slug'])
        
        all_episodes = Episode.objects.filter(podcast__slug=self.kwargs['slug']).order_by('-publication_date')
        context['episodes'] = all_episodes
        
        context['episodes'] = all_episodes
        return context

    def get_object(self, *args, **kwargs):
        podcast = super(PodcastDeleteView, self).get_object(*args, **kwargs)
        if self.request.user in podcast.moderators.all():
            return podcast
        elif self.request.user.is_superuser:
            return podcast
        else:
            raise Http404

class PodcastEpisodeListView(ListView):
    model = Quote
    slug_field="slug"
    
    def get_template_names(self):
        return 'podcast_detail.html'
    
    def get_paginate_by(self, queryset):
        return 20
    
    def get_context_data(self, **kwargs):
        context = super(PodcastEpisodeListView, self).get_context_data(**kwargs)
        
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        p = Podcast.objects.get(slug=self.kwargs['slug'])
        context['podcast'] = p
        
        all_episodes = Episode.objects.filter(podcast_id=p.id).order_by('-publication_date')
        context['episodes'] = all_episodes
        
        """
        all_karma_leaders = sorted(User.objects.exclude(id=1), key = lambda u: u.userprofile.leaderboard_karma_total, reverse=True)
        
        # take only the top 5 karma_leaders
        all_karma_leaders = all_karma_leaders[:5]
        
        # remove the users who have submitted 0 quotes
        # they may not want to have their username public
        all_karma_leaders = [i for i in all_karma_leaders if i.userprofile.leaderboard_karma_total != None]
        
        context['karma_leaders'] = all_karma_leaders
        """
        
        # these allow the template to know if a breadcrumb should be displayed within quote divs
        context['is_home_page'] = False
        context['is_podcast_page'] = True
        context['is_episode_page'] = False
        context['is_quote_page'] = False
        context['is_user_page'] = False
        
        # these allow the template to know if user is viewing episodes or clips
        context['is_podcast_episodes_page'] = True
        context['is_podcast_clips_page'] = False
        
        ### these allow the template to know which nav button (hot, not, top, etc.) to display as active
        context['podcast_hot_is_active'] = False
        context['podcast_not_is_active'] = False
        context['podcast_controversial_is_active'] = False
        context['podcast_ordered_is_active'] = False
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
        elif f == 'ordered':
            context['podcast_ordered_is_active'] = True
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
            context['podcast_ordered_is_active'] = True
        
        return context
    
    def get_queryset(self):
        p = get_object_or_404(Podcast, slug=self.kwargs['slug'])
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        if f == 'hot':
            return Quote.quote_vote_manager.query_hot().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'not':
            return Quote.quote_vote_manager.query_not().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'controversial':
            return Quote.quote_vote_manager.query_controversial().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'ordered':
            return Quote.quote_vote_manager.query_ordered('full_episodes').filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'new':
            return Quote.quote_vote_manager.query_new().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'top':
            return Quote.quote_vote_manager.query_top().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'bottom':
            return Quote.quote_vote_manager.query_bottom().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'mainstream':
            return Quote.quote_vote_manager.query_mainstream().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'underground':
            return Quote.quote_vote_manager.query_underground().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'chronological':
            return Quote.quote_vote_manager.query_chronological().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'ghosts':
            return Quote.quote_vote_manager.query_ghosts().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'birthdays':
            return Quote.quote_vote_manager.query_birthdays().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        else:
            return Quote.quote_vote_manager.query_ordered('full_episodes').filter(episode__podcast_id=p.id).exclude(is_full_episode=False)

# TECH DEBT - This view is exactly the same as PodcastEpisodeListView, but with no paginate_by.
# Should be using class inheritance.
class PodcastAllEpisodeListView(ListView):
    model = Quote
    slug_field="slug"
    
    def get_template_names(self):
        return 'podcast_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super(PodcastAllEpisodeListView, self).get_context_data(**kwargs)
        
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['podcast'] = Podcast.objects.get(slug=self.kwargs['slug'])
        
        all_episodes = Episode.objects.filter(podcast__slug=self.kwargs['slug']).order_by('-publication_date')
        context['episodes'] = all_episodes
        
        """
        all_karma_leaders = sorted(User.objects.exclude(id=1), key = lambda u: u.userprofile.leaderboard_karma_total, reverse=True)
        
        # take only the top 5 karma_leaders
        all_karma_leaders = all_karma_leaders[:5]
        
        # remove the users who have submitted 0 quotes
        # they may not want to have their username public
        all_karma_leaders = [i for i in all_karma_leaders if i.userprofile.leaderboard_karma_total != None]
        
        context['karma_leaders'] = all_karma_leaders
        """
        
        context['is_podcast_all_episodes_page'] = True
        
        # these allow the template to know if a breadcrumb should be displayed within quote divs
        context['is_home_page'] = False
        context['is_podcast_page'] = True
        context['is_episode_page'] = False
        context['is_quote_page'] = False
        context['is_user_page'] = False
        
        # these allow the template to know if user is viewing episodes or clips
        context['is_podcast_episodes_page'] = True
        context['is_podcast_clips_page'] = False
        
        ### these allow the template to know which nav button (hot, not, top, etc.) to display as active
        context['podcast_hot_is_active'] = False
        context['podcast_not_is_active'] = False
        context['podcast_controversial_is_active'] = False
        context['podcast_ordered_is_active'] = False
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
        elif f == 'ordered':
            context['podcast_ordered_is_active'] = True
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
            context['podcast_ordered_is_active'] = True
        
        return context
    
    def get_queryset(self):
        p = get_object_or_404(Podcast, slug=self.kwargs['slug'])
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        if f == 'hot':
            return Quote.quote_vote_manager.query_hot().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'not':
            return Quote.quote_vote_manager.query_not().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'controversial':
            return Quote.quote_vote_manager.query_controversial().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'ordered':
            return Quote.quote_vote_manager.query_ordered('full_episodes').filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'new':
            return Quote.quote_vote_manager.query_new().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'top':
            return Quote.quote_vote_manager.query_top().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'bottom':
            return Quote.quote_vote_manager.query_bottom().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'mainstream':
            return Quote.quote_vote_manager.query_mainstream().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'underground':
            return Quote.quote_vote_manager.query_underground().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'chronological':
            return Quote.quote_vote_manager.query_chronological().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'ghosts':
            return Quote.quote_vote_manager.query_ghosts().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        elif f == 'birthdays':
            return Quote.quote_vote_manager.query_birthdays().filter(episode__podcast_id=p.id).exclude(is_full_episode=False)
        else:
            return Quote.quote_vote_manager.query_ordered('full_episodes').filter(episode__podcast_id=p.id).exclude(is_full_episode=False)

class PodcastQuoteListView(ListView):
    model = Quote
    slug_field="slug"


    def get_template_names(self):
        return 'podcast_detail.html'

    def get_paginate_by(self, queryset):
        return 20
    
    def get_context_data(self, **kwargs):
        context = super(PodcastQuoteListView, self).get_context_data(**kwargs)
        
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['podcast'] = Podcast.objects.get(slug=self.kwargs['slug'])
        
        all_episodes = Episode.objects.filter(podcast__slug=self.kwargs['slug']).order_by('-publication_date')
        context['episodes'] = all_episodes
        
        """
        all_karma_leaders = sorted(User.objects.exclude(id=1), key = lambda u: u.userprofile.leaderboard_karma_total, reverse=True)
        
        # take only the top 5 karma_leaders
        all_karma_leaders = all_karma_leaders[:5]
        
        # remove the users who have submitted 0 quotes
        # they may not want to have their username public
        all_karma_leaders = [i for i in all_karma_leaders if i.userprofile.leaderboard_karma_total != None]
        
        context['karma_leaders'] = all_karma_leaders
        """
        
        # these allow the template to know if a breadcrumb should be displayed within quote divs
        context['is_home_page'] = False
        context['is_podcast_page'] = True
        context['is_episode_page'] = False
        context['is_quote_page'] = False
        context['is_user_page'] = False
        
        # these allow the template to know if user is viewing episodes or clips
        context['is_podcast_episodes_page'] = False
        context['is_podcast_clips_page'] = True
        
        ### these allow the template to know which nav button (hot, not, top, etc.) to display as active
        context['podcast_hot_is_active'] = False
        context['podcast_not_is_active'] = False
        context['podcast_controversial_is_active'] = False
        context['podcast_ordered_is_active'] = False
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
        elif f == 'ordered':
            context['podcast_ordered_is_active'] = True
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
    
    def get_queryset(self):
        p = get_object_or_404(Podcast, slug=self.kwargs['slug'])
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        if f == 'hot':
            return Quote.quote_vote_manager.query_hot().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        elif f == 'not':
            return Quote.quote_vote_manager.query_not().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        elif f == 'controversial':
            return Quote.quote_vote_manager.query_controversial().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        elif f == 'ordered':
            return Quote.quote_vote_manager.query_ordered('highlights').filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        elif f == 'new':
            return Quote.quote_vote_manager.query_new().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        elif f == 'top':
            return Quote.quote_vote_manager.query_top().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        elif f == 'bottom':
            return Quote.quote_vote_manager.query_bottom().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        elif f == 'mainstream':
            return Quote.quote_vote_manager.query_mainstream().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        elif f == 'underground':
            return Quote.quote_vote_manager.query_underground().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        elif f == 'chronological':
            return Quote.quote_vote_manager.query_chronological().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        elif f == 'ghosts':
            return Quote.quote_vote_manager.query_ghosts().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        elif f == 'birthdays':
            return Quote.quote_vote_manager.query_birthdays().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)
        else:
            return Quote.quote_vote_manager.query_hot().filter(episode__podcast_id=p.id).exclude(is_full_episode=True)

def thin_json_podcast_query(request):
    
    title_query = request.GET.get('q')
    
    podcast_queryset = Podcast.objects.filter(
        title__icontains=title_query).values('id', 'title')[:10]
    
    podcasts = [podcast for podcast in podcast_queryset]
    
    json_payload = json.dumps(podcasts)
    
    return HttpResponse(json_payload, content_type="application/json")
