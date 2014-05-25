from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile

class HomeQuoteListView(ListView):
    model = Quote
    template_name = 'home.html'
    paginate_by = 10
    
    def get_queryset(self):
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False            
        
        if f == 'hot':
            return Quote.quote_vote_manager.query_hot()
        elif f == 'not':
            return Quote.quote_vote_manager.query_not()
        elif f == 'controversial':
            return Quote.quote_vote_manager.query_controversial()
        elif f == 'new':
            return Quote.quote_vote_manager.query_new()
        elif f == 'top':
            return Quote.quote_vote_manager.query_top()
        elif f == 'bottom':
            return Quote.quote_vote_manager.query_bottom()
        elif f == 'mainstream':
            return Quote.quote_vote_manager.query_mainstream()
        elif f == 'underground':
            return Quote.quote_vote_manager.query_underground()
        elif f == 'chronological':
            return Quote.quote_vote_manager.query_chronological()
        elif f == 'ghosts':
            return Quote.quote_vote_manager.query_ghosts()
        elif f == 'birthdays':
            return Quote.quote_vote_manager.query_birthdays()
        else:
            return Quote.quote_vote_manager.query_hot()
    
    def get_context_data(self, **kwargs):
        context = super(HomeQuoteListView, self).get_context_data(**kwargs)
        
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False   
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('title')
        
        # these allow the template to know if a breadcrumb should be displayed within quote divs
        context['is_home_page'] = True
        context['is_podcast_page'] = False
        context['is_episode_page'] = False
        context['is_quote_page'] = False
        context['is_user_page'] = False
        
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