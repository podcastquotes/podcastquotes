from django import forms
from django.forms import ModelForm
from podcastquotes.models import Podcast, Episode, Quote

class PodcastCreateForm(forms.ModelForm):
    
    class Meta:
        model = Podcast
        exclude = ('',)
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder': ''}),
            'homepage': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'donate_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'twitter_url': forms.URLInput(attrs={'class':'form-control', 'placeholder':''}),
            'facebook_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'instagram_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'google_plus_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'youtube_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
        }

class PodcastForm(forms.ModelForm):
    
    class Meta:
        model = Podcast
        exclude = ('',)
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder': ''}),
            'homepage': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'donate_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'twitter_url': forms.URLInput(attrs={'class':'form-control', 'placeholder':''}),
            'facebook_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'instagram_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'google_plus_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'youtube_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
        }
        
class EpisodeCreateForm(forms.ModelForm):
    
    class Meta:
        model = Episode
        exclude = ('',)
        widgets = {
            'podcast': forms.Select(attrs={'class':'form-control', 'placeholder':''}),
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
            'publication_date': forms.DateInput(attrs={'class':'form-control', 'placeholder':''}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder': ''}),
            'episode_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'video_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'audio_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
        }

class EpisodeForm(forms.ModelForm):
    
    class Meta:
        model = Episode
        exclude = ('',)
        widgets = {
            'podcast': forms.Select(attrs={'class':'form-control', 'placeholder':''}),
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
            'publication_date': forms.DateInput(attrs={'class':'form-control', 'placeholder':''}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder': ''}),
            'episode_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'video_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'audio_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
        }

class QuoteCreateForm(forms.ModelForm):
    
    class Meta:
        model = Quote
        widgets = {
            'episode': forms.Select(attrs={'class':'form-control'}),
            'summary': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'max 116 characters'}),
            'text': forms.Textarea(attrs={'class':'form-control', 'rows':5, 'placeholder': 'Speaker Name: "Type quote in this format, with the name of the speaker followed by the colon symbol (:)."'}),
            'time_quote_begins': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'hh:mm:ss'}),
            'time_quote_ends': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'hh:mm:ss'}),
        }

class QuoteForm(forms.ModelForm):

    class Meta:
        model = Quote