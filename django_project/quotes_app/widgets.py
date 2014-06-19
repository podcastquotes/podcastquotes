from django.forms.widgets import Widget
from django.template.loader import render_to_string
from quotes_app.models import Episode

class EpisodeEstablisherWidget(Widget):
    
    
    class Media():
        js = (
            'js/episodeEstablisherWidget.js', 'js/typeahead.bundle.js')
    
    #
    # Getters that will generate form names based on this 
    # widgets name.
    #
    
    def get_podcast_id_form_name(self, name):
        return name + '_podcast_id'
        
    def get_podcast_title_form_name(self, name):
        return name + '_podcast_title'
    
    def get_episode_id_form_name(self, name):
        return name + '_episode_id'
    
    def get_episode_title_form_name(self, name):
        return name + '_episode_title'
    
    def render(self, name, value, attrs=None):
        """
        Assume value is a tuple in this form:
        (podcast_id, podcast_title, episode_id, episode_title)
        """
        
        # Expand None into blank tuple.
        if (value == None):
            value = ('', '', '', '')
            
        # KLUGE ALERT TODO
        """ I don't like how the widget is touching the database here.
            It would be nice if the EpisodeField would do this 
            extrapolation """
        
        # If the value is an int, this is probably a pk for an episode.
        if type(value) is int:
            episode = Episode.objects.get(id=value)
            value = (
                episode.podcast.id, 
                episode.podcast.title,
                episode.id,
                episode.title)
        # END KLUGE
        
        podcast_id = value[0]
        podcast_title = value[1]
        episode_id = value[2]
        episode_title = value[3]
        
        widget_render_ctx = { 
            'wname': name,
            
            'podcast_id_value' : podcast_id,
            'podcast_title_value' : podcast_title,
            'episode_id_value' : episode_id,
            'episode_title_value' : episode_title,
            
            'podcast_id_form_name': 
                self.get_podcast_id_form_name(name),
            'podcast_title_form_name': 
                self.get_podcast_title_form_name(name),
            'episode_id_form_name':
                self.get_episode_id_form_name(name),
            'episode_title_form_name':
                self.get_episode_title_form_name(name)
            
        }
        
        return render_to_string(
            "widgets/episode_establisher_widget.html", 
            widget_render_ctx)
        
    def value_from_datadict(self, data, files, name):
        """
        Return the tuple of values from this widget.
        """

        return (
            data[self.get_podcast_id_form_name(name)],
            data[self.get_podcast_title_form_name(name)],
            data[self.get_episode_id_form_name(name)],
            data[self.get_episode_title_form_name(name)]
        )
