from django.views.generic import DetailView, ListView
from quotes_app.models import Podcast, Episode

# this view is useful for superuser to check for episodes which do not have a YouTube link for playing clips
class NeedYouTubeLinks(ListView):
    model = Episode
    template_name = 'need-youtube-links.html'
    
    def get_context_data(self, **kwargs):
        context = super(NeedYouTubeLinks, self).get_context_data(**kwargs)
        context['episodes_without_youtube_links'] = Episode.objects.filter(podcast__managed_by_superuser=True).filter(youtube_url='');
        return context

# this view is useful for Mitch to check the titles of a podcast's episodes
class PodcastEpisodeTitlePrint(ListView):
    model = Podcast
    template_name = 'podcast_episode_title_print.html'
    
    def get_context_data(self, **kwargs):
        context = super(PodcastEpisodeTitlePrint, self).get_context_data(**kwargs)
        context['podcast'] = Podcast.objects.get(id=self.kwargs['pk'])
        return context