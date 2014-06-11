from django.core.exceptions import ValidationError
from django.forms.fields import Field
from quotes_app.widgets import EpisodeEstablisherWidget
from quotes_app.models import Episode, Podcast

class EpisodeField(Field):
    
    widget = EpisodeEstablisherWidget
        
    def to_python(self, value):
        
        # Unpack value tuple
        podcast_id = self._parse_int_or_none(value[0])
        episode_id = self._parse_int_or_none(value[2])
        podcast_title, episode_title = value[1], value[3]
        
        #
        ## Check sanity of widget values.
        #
        
        # Does the widget have no podcast provided?
        if podcast_id == None and podcast_title.replace(' ', '') == '':
            raise ValidationError("A podcast is required.")
        
        # Does the widget have no episode provided?
        if episode_id == None and episode_title.replace(' ', '') == '':
            raise ValidationError("An episode is required.")
        
        #
        ## Define some boolean
        #
        making_new_episode = (episode_id == None)
        making_new_podcast = (podcast_id == None)
        
        #
        ## Retrieval / Creation logic
        #
        if not making_new_episode:
            
            # Obtain episode
            try:
                episode = Episode.objects.get(id=episode_id)
            except Episode.DoesNotExist:
                raise ValidationError(
                    'Could not find episode by provided ID.')
                    
        else: # making new episode
            
            if making_new_podcast:
                podcast_id = Podcast.objects \
                    .create(title=podcast_title).id
                    
            else: # using existing podcast
            
                # Might not need to do this case in production
                # because SQLite doesn't seem to care about 
                # foreign key constraints.
                
                try:
                    podcast_id = Podcast.objects \
                        .get(title=podcast_title).id
                except Podcast.DoesNotExist:
                    raise ValidationError(
                        'Could not find podcast by provided ID.')
            
            episode = Episode.objects.create(
                podcast_id = podcast_id,
                title = episode_title)
        
        return episode
    
    def _parse_int_or_none(self, value):
            
        result = None
        
        try:
            result = int(value)
        except ValueError:
            pass
        
        return result
