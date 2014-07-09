from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.models import User
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile

class HomeEpisodeListView(ListView):
    model = Quote
    template_name = 'home.html'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super(HomeEpisodeListView, self).get_context_data(**kwargs)
        
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False   
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        all_karma_leaders = sorted(User.objects.all(), key = lambda u: u.userprofile.leaderboard_karma_total, reverse=True)
        
        # take only the top 5 karma_leaders
        all_karma_leaders = all_karma_leaders[:5]
        
        # remove the users who have submitted 0 quotes
        # they may not want to have their username public
        all_karma_leaders = [i for i in all_karma_leaders if i.userprofile.leaderboard_karma_total != None]
        
        context['karma_leaders'] = all_karma_leaders
        
        # these allow the template to know if a breadcrumb should be displayed within quote divs
        context['is_home_page'] = True
        context['is_podcast_page'] = False
        context['is_episode_page'] = False
        context['is_quote_page'] = False
        context['is_user_page'] = False
        
        # these allow the template to know if user is viewing episodes or clips
        context['is_home_episodes_page'] = True
        context['is_home_clips_page'] = False
        
        # these allow the template to know which nav button (hot, not, top, etc.) to display as active
        context['home_hot_is_active'] = False
        context['home_not_is_active'] = False
        context['home_controversial_is_active'] = False
        context['home_new_is_active'] = False
        context['home_top_is_active'] = False
        context['home_bottom_is_active'] = False
        context['home_mainstream_is_active'] = False
        context['home_underground_is_active'] = False
        context['home_chronological_is_active'] = False
        context['home_ghosts_is_active'] = False
        context['home_birthdays_is_active'] = False
        
        if f == 'hot':
            context['home_hot_is_active'] = True
        elif f == 'not':
            context['home_not_is_active'] = True
        elif f == 'controversial':
            context['home_controversial_is_active'] = True
        elif f == 'new':
            context['home_new_is_active'] = True
        elif f == 'top':
            context['home_top_is_active'] = True
        elif f == 'bottom':
            context['home_bottom_is_active'] = True
        elif f == 'mainstream':
            context['home_mainstream_is_active'] = True
        elif f == 'underground':
            context['home_underground_is_active'] = True
        elif f == 'chronological':
            context['home_chronological_is_active'] = True
        elif f == 'ghosts':
            context['home_ghosts_is_active'] = True
        elif f == 'birthdays':
            context['home_birthdays_is_active'] = True
        else:
            context['home_hot_is_active'] = True
        
        return context
    
    def get_queryset(self):
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False            
        
        if f == 'hot':
            return Quote.quote_vote_manager.query_hot().exclude(is_full_episode=False)
        elif f == 'not':
            return Quote.quote_vote_manager.query_not().exclude(is_full_episode=False)
        elif f == 'controversial':
            return Quote.quote_vote_manager.query_controversial().exclude(is_full_episode=False)
        elif f == 'new':
            return Quote.quote_vote_manager.query_new().exclude(is_full_episode=False)
        elif f == 'top':
            return Quote.quote_vote_manager.query_top().exclude(is_full_episode=False)
        elif f == 'bottom':
            return Quote.quote_vote_manager.query_bottom().exclude(is_full_episode=False)
        elif f == 'mainstream':
            return Quote.quote_vote_manager.query_mainstream().exclude(is_full_episode=False)
        elif f == 'underground':
            return Quote.quote_vote_manager.query_underground().exclude(is_full_episode=False)
        elif f == 'chronological':
            return Quote.quote_vote_manager.query_chronological().exclude(is_full_episode=False)
        elif f == 'ghosts':
            return Quote.quote_vote_manager.query_ghosts().exclude(is_full_episode=False)
        elif f == 'birthdays':
            return Quote.quote_vote_manager.query_birthdays().exclude(is_full_episode=False)
        else:
            return Quote.quote_vote_manager.query_hot().exclude(is_full_episode=False)

class HomeQuoteListView(ListView):
    model = Quote
    template_name = 'home.html'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super(HomeQuoteListView, self).get_context_data(**kwargs)
        
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False   
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        all_karma_leaders = sorted(User.objects.all(), key = lambda u: u.userprofile.leaderboard_karma_total, reverse=True)
        
        # take only the top 5 karma_leaders
        all_karma_leaders = all_karma_leaders[:5]
        
        # remove the users who have submitted 0 quotes
        # they may not want to have their username public
        all_karma_leaders = [i for i in all_karma_leaders if i.userprofile.leaderboard_karma_total != None]
        
        context['karma_leaders'] = all_karma_leaders
        
        # these allow the template to know if a breadcrumb should be displayed within quote divs
        context['is_home_page'] = True
        context['is_podcast_page'] = False
        context['is_episode_page'] = False
        context['is_quote_page'] = False
        context['is_user_page'] = False
        
        # these allow the template to know if user is viewing episodes or clips
        context['is_home_episodes_page'] = False
        context['is_home_clips_page'] = True
        
        # these allow the template to know which nav button (hot, not, top, etc.) to display as active
        context['home_hot_is_active'] = False
        context['home_not_is_active'] = False
        context['home_controversial_is_active'] = False
        context['home_new_is_active'] = False
        context['home_top_is_active'] = False
        context['home_bottom_is_active'] = False
        context['home_mainstream_is_active'] = False
        context['home_underground_is_active'] = False
        context['home_chronological_is_active'] = False
        context['home_ghosts_is_active'] = False
        context['home_birthdays_is_active'] = False
        
        if f == 'hot':
            context['home_hot_is_active'] = True
        elif f == 'not':
            context['home_not_is_active'] = True
        elif f == 'controversial':
            context['home_controversial_is_active'] = True
        elif f == 'new':
            context['home_new_is_active'] = True
        elif f == 'top':
            context['home_top_is_active'] = True
        elif f == 'bottom':
            context['home_bottom_is_active'] = True
        elif f == 'mainstream':
            context['home_mainstream_is_active'] = True
        elif f == 'underground':
            context['home_underground_is_active'] = True
        elif f == 'chronological':
            context['home_chronological_is_active'] = True
        elif f == 'ghosts':
            context['home_ghosts_is_active'] = True
        elif f == 'birthdays':
            context['home_birthdays_is_active'] = True
        else:
            context['home_hot_is_active'] = True
        
        return context
    
    def get_queryset(self):
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False            
        
        if f == 'hot':
            return Quote.quote_vote_manager.query_hot().exclude(is_full_episode=True)
        elif f == 'not':
            return Quote.quote_vote_manager.query_not().exclude(is_full_episode=True)
        elif f == 'controversial':
            return Quote.quote_vote_manager.query_controversial().exclude(is_full_episode=True)
        elif f == 'new':
            return Quote.quote_vote_manager.query_new().exclude(is_full_episode=True)
        elif f == 'top':
            return Quote.quote_vote_manager.query_top().exclude(is_full_episode=True)
        elif f == 'bottom':
            return Quote.quote_vote_manager.query_bottom().exclude(is_full_episode=True)
        elif f == 'mainstream':
            return Quote.quote_vote_manager.query_mainstream().exclude(is_full_episode=True)
        elif f == 'underground':
            return Quote.quote_vote_manager.query_underground().exclude(is_full_episode=True)
        elif f == 'chronological':
            return Quote.quote_vote_manager.query_chronological().exclude(is_full_episode=True)
        elif f == 'ghosts':
            return Quote.quote_vote_manager.query_ghosts().exclude(is_full_episode=True)
        elif f == 'birthdays':
            return Quote.quote_vote_manager.query_birthdays().exclude(is_full_episode=True)
        else:
            return Quote.quote_vote_manager.query_hot().exclude(is_full_episode=True)