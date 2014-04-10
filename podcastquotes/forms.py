from django import forms
from django.forms import ModelForm
from podcastquotes.models import Podcast, Episode, PersonQuoted, Tag, Quote

class PodcastCreateForm(forms.ModelForm):
    
    class Meta:
        model = Podcast
        exclude = ('',)
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder': ''}),
            'homepage': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'donate_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
        }

class PodcastForm(forms.ModelForm):
    
    class Meta:
        model = Podcast
        
class EpisodeCreateForm(forms.ModelForm):
    
    class Meta:
        model = Episode
        exclude = ('',)
        widgets = {
            'podcast': forms.Select(attrs={'class':'form-control', 'placeholder':''}),
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
            'publication_date': forms.DateInput(attrs={'class':'form-control', 'placeholder':''}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder': ''}),
            'episode_link': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
        }

class EpisodeForm(forms.ModelForm):
    
    class Meta:
        model = Episode

class QuoteForm(forms.ModelForm):

    class Meta:
        model = Quote

class QuoteCreateForm(forms.ModelForm):
    
    class Meta:
        model = Quote
        exclude = ('tags', 'persons_quoted',)
        widgets = {
            'episode': forms.Select(attrs={'class':'form-control'}),
            'text': forms.Textarea(attrs={'class':'form-control', 'placeholder': 'Speaker Name: "Type quote in this format, with the name of the speaker followed by the colon symbol (:). Use quotation marks (" ") accordingly, and ellipses (...) if you skip ahead in the quote."'}),
            'time_quote_begins': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'hh:mm:ss'}),
            'time_quote_ends': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'hh:mm:ss'}),
        }
        
class PersonQuotedCreateForm(forms.ModelForm):

    class Meta:
        model = PersonQuoted
        widgets = {
            'person': forms.TextInput(attrs={'class':'form-control', 'placeholder':"Type each person's name separated by commas"}),
        }

class TagCreateForm(forms.ModelForm):

    class Meta:
        model = Tag
        widgets = {
            'tag': forms.TextInput(attrs={'class':'form-control', 'placeholder':"Type each tag separated by commas"}),
        }