from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from quotes_app.models import Podcast, Episode

# this view is useful for superuser to check for episodes which do not have a YouTube link for playing clips
class NeedYouTubeLinks(ListView):
    model = Episode
    template_name = 'need-youtube-links.html'
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(NeedYouTubeLinks, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(NeedYouTubeLinks, self).get_context_data(**kwargs)
        context['episodes_without_youtube_links'] = Episode.objects.filter(podcast__managed_by_superuser=True).filter(youtube_url='').order_by('podcast');
        return context

# this view is useful for Mitch to check the titles of a podcast's episodes
class PodcastEpisodeTitlePrint(ListView):
    model = Podcast
    template_name = 'podcast_episode_title_print.html'
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(PodcastEpisodeTitlePrint, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(PodcastEpisodeTitlePrint, self).get_context_data(**kwargs)
        context['podcast'] = Podcast.objects.get(id=self.kwargs['pk'])
        return context