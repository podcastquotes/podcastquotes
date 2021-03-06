from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, Http404
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from core.forms import UserProfileForm
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile

class UserProfileUpdateView(UpdateView):
    model = get_user_model()
    slug_field = "username"
    template_name = 'user_update.html'
    form_class = UserProfileForm
    
    def dispatch(self, *args, **kwargs):
        u = get_object_or_404(User, username=self.kwargs['slug'])
        if self.request.user != u:
            return Http404
        else:
            return super(UserProfileUpdateView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(UserProfileUpdateView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['person'] = User.objects.get(username=self.kwargs['slug'])

        return context
    
    def get_object(self, *args, **kwargs):
        user = super(UserProfileUpdateView, self).get_object(*args, **kwargs)
        if self.request.user == user:
            return user
        elif self.request.user.is_superuser:
            return user
        else:
            raise Http404
    
    def get_success_url(self):
        user = super(UserProfileUpdateView, self).get_object()
        return reverse_lazy('user_quote_list_root', kwargs={'slug': user})

class UserProfileDeleteView(DeleteView):
    model = get_user_model()
    slug_field = "username"
    success_url = reverse_lazy('home')
    template_name = 'user_delete.html'
    
    def dispatch(self, *args, **kwargs):
        u = get_object_or_404(User, username=self.kwargs['slug'])
        if self.request.user != u:
            return Http404
        else:
            return super(UserProfileDeleteView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(UserProfileDeleteView, self).get_context_data(**kwargs)
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['person'] = User.objects.get(username=self.kwargs['slug'])

        return context
        
    def get_object(self, *args, **kwargs):
        user = super(UserProfileDeleteView, self).get_object(*args, **kwargs)
        if self.request.user == user:
            return user
        elif self.request.user.is_superuser:
            return user
        else:
            raise Http404

class UserQuoteListView(ListView):
    model = get_user_model()
    slug_field = "username"
    
    def get_template_names(self):
        return 'user_detail.html'

    def get_paginate_by(self, queryset):
        return 20
    
    def get_context_data(self, **kwargs):
        context = super(UserQuoteListView, self).get_context_data(**kwargs)
        
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['person'] = User.objects.get(username=self.kwargs['slug'])
        
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
        context['is_episode_page'] = False
        context['is_quote_page'] = False
        context['is_user_page'] = True
        
        context['user_posted_is_active'] = True
        context['user_saved_is_active'] = False
        
        ### these allow the template to know which nav button (hot, not, top, etc.) to display as active
        context['user_hot_is_active'] = False
        context['user_not_is_active'] = False
        context['user_controversial_is_active'] = False
        context['user_new_is_active'] = False
        context['user_top_is_active'] = False
        context['user_bottom_is_active'] = False
        context['user_mainstream_is_active'] = False
        context['user_underground_is_active'] = False
        context['user_chronological_is_active'] = False
        context['user_ghosts_is_active'] = False
        context['user_birthdays_is_active'] = False
        
        if f == 'hot':
            context['user_hot_is_active'] = True
        elif f == 'not':
            context['user_not_is_active'] = True
        elif f == 'controversial':
            context['user_controversial_is_active'] = True
        elif f == 'new':
            context['user_new_is_active'] = True
        elif f == 'top':
            context['user_top_is_active'] = True
        elif f == 'bottom':
            context['user_bottom_is_active'] = True
        elif f == 'mainstream':
            context['user_mainstream_is_active'] = True
        elif f == 'underground':
            context['user_underground_is_active'] = True
        elif f == 'chronological':
            context['user_chronological_is_active'] = True
        elif f == 'ghosts':
            context['user_ghosts_is_active'] = True
        elif f == 'birthdays':
            context['user_birthdays_is_active'] = True
        else:
            context['user_hot_is_active'] = True

        return context
    
    def get_object(self, queryset=None):
        user = super(UserProfileDetailView, self).get_object(queryset)
        UserProfile.objects.get_or_create(user=user)
        return user
        
    def get_queryset(self):
        u = get_object_or_404(User, username=self.kwargs['slug'])
        
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False
            
        if f == 'hot':
            return Quote.quote_vote_manager.query_hot().filter(submitted_by=u)
        elif f == 'not':
            return Quote.quote_vote_manager.query_not().filter(submitted_by=u)
        elif f == 'controversial':
            return Quote.quote_vote_manager.query_controversial().filter(submitted_by=u)
        elif f == 'new':
            return Quote.quote_vote_manager.query_new().filter(submitted_by=u)
        elif f == 'top':
            return Quote.quote_vote_manager.query_top().filter(submitted_by=u)
        elif f == 'bottom':
            return Quote.quote_vote_manager.query_bottom().filter(submitted_by=u)
        elif f == 'mainstream':
            return Quote.quote_vote_manager.query_mainstream().filter(submitted_by=u)
        elif f == 'underground':
            return Quote.quote_vote_manager.query_underground().filter(submitted_by=u)
        elif f == 'chronological':
            return Quote.quote_vote_manager.query_chronological().filter(submitted_by=u)
        elif f == 'ghosts':
            return Quote.quote_vote_manager.query_ghosts().filter(submitted_by=u)
        elif f == 'birthdays':
            return Quote.quote_vote_manager.query_birthdays().filter(submitted_by=u)
        else:
            return Quote.quote_vote_manager.query_hot().filter(submitted_by=u)
            
class UserSavedQuoteListView(ListView):
    model = get_user_model()
    slug_field = "username"
    
    def dispatch(self, *args, **kwargs):
        u = get_object_or_404(User, username=self.kwargs['slug'])
        if self.request.user != u:
            return HttpResponseRedirect(u.userprofile.get_absolute_url())
        else:
            return super(UserSavedQuoteListView, self).dispatch(*args, **kwargs)
    
    def get_template_names(self):
        return 'user_detail.html'

    def get_paginate_by(self, queryset):
        return 20
            
    def get_context_data(self, **kwargs):
        context = super(UserSavedQuoteListView, self).get_context_data(**kwargs)
        
        try: 
            self.kwargs['query_filter']
            f = self.kwargs['query_filter']
        except KeyError:
            f = 0
        
        ### context['podcasts'] must be refactored, this is passed to all views
        context['podcasts'] = Podcast.objects.all().order_by('alphabetical_title').exclude(is_hidden=True)
        
        context['person'] = User.objects.get(username=self.kwargs['slug'])
        
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
        context['is_episode_page'] = False
        context['is_quote_page'] = False
        context['is_user_page'] = True
        
        context['user_posted_is_active'] = False
        context['user_saved_is_active'] = True
        
        ### these allow the template to know which nav button (hot, not, top, etc.) to display as active
        context['user_hot_is_active'] = False
        context['user_not_is_active'] = False
        context['user_controversial_is_active'] = False
        context['user_new_is_active'] = False
        context['user_top_is_active'] = False
        context['user_bottom_is_active'] = False
        context['user_mainstream_is_active'] = False
        context['user_underground_is_active'] = False
        context['user_chronological_is_active'] = False
        context['user_ghosts_is_active'] = False
        context['user_birthdays_is_active'] = False
        
        if f == 'hot':
            context['user_hot_is_active'] = True
        elif f == 'not':
            context['user_not_is_active'] = True
        elif f == 'controversial':
            context['user_controversial_is_active'] = True
        elif f == 'new':
            context['user_new_is_active'] = True
        elif f == 'top':
            context['user_top_is_active'] = True
        elif f == 'bottom':
            context['user_bottom_is_active'] = True
        elif f == 'mainstream':
            context['user_mainstream_is_active'] = True
        elif f == 'underground':
            context['user_underground_is_active'] = True
        elif f == 'chronological':
            context['user_chronological_is_active'] = True
        elif f == 'ghosts':
            context['user_ghosts_is_active'] = True
        elif f == 'birthdays':
            context['user_birthdays_is_active'] = True
        else:
            context['user_hot_is_active'] = True

        return context
            
    def get_queryset(self):
        u = get_object_or_404(User, username=self.kwargs['slug'])
        
        try:
            f = self.kwargs['query_filter']
        except KeyError:
            f = False
            
        if f == 'hot':
            return Quote.quote_vote_manager.query_hot().filter(savedquote__saver=u)
        elif f == 'not':
            return Quote.quote_vote_manager.query_not().filter(savedquote__saver_id=u)
        elif f == 'controversial':
            return Quote.quote_vote_manager.query_controversial().filter(savedquote__saver_id=u)
        elif f == 'new':
            return Quote.quote_vote_manager.query_new().filter(savedquote__saver_id=u)
        elif f == 'top':
            return Quote.quote_vote_manager.query_top().filter(savedquote__saver_id=u)
        elif f == 'bottom':
            return Quote.quote_vote_manager.query_bottom().filter(savedquote__saver_id=u)
        elif f == 'mainstream':
            return Quote.quote_vote_manager.query_mainstream().filter(savedquote__saver_id=u)
        elif f == 'underground':
            return Quote.quote_vote_manager.query_underground().filter(savedquote__saver_id=u)
        elif f == 'chronological':
            return Quote.quote_vote_manager.query_chronological().filter(savedquote__saver_id=u)
        elif f == 'ghosts':
            return Quote.quote_vote_manager.query_ghosts().filter(savedquote__saver_id=u)
        elif f == 'birthdays':
            return Quote.quote_vote_manager.query_birthdays().filter(savedquote__saver_id=u)
        else:
            return Quote.quote_vote_manager.query_new().filter(savedquote__saver_id=u)