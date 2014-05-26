from django import forms
from django.db import models
from django.forms import ModelForm
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile
from captcha.fields import ReCaptchaField
from django.contrib.auth import get_user_model

def getSec(hhmmss):
    l = map(int, hhmmss.split(':'))
    return sum(n * sec for n, sec in zip(l[::-1], (1, 60, 3600)))

class PodcastCreateForm(forms.ModelForm):
    
    class Meta:
        model = Podcast
        exclude = ('',)
        widgets = {
            'rss_url': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
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
        exclude = ('moderators',)
        widgets = {
            'rss_url': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
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
            'youtube_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
        }

class EpisodeForm(forms.ModelForm):
    
    class Meta:
        model = Episode
        exclude = ('',)
        widgets = {
            'podcast': forms.Select(attrs={'class':'form-control', 'placeholder':''}),
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
            'guid': forms.TextInput(attrs={'class':'form-control', 'placeholder':'globally unique identifier'}),
            'publication_date': forms.DateInput(attrs={'class':'form-control', 'placeholder':'mm/dd/yy'}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder': ''}),
            'youtube_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': 'link to full-length, unedited episode on YouTube'}),
            'donate_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': 'link to donation page for this episode'}),
            'donation_recipient': forms.TextInput(attrs={'class':'form-control', 'placeholder':'name of donation recipient for this episode'}),
            'donation_recipient_about': forms.Textarea(attrs={'class':'form-control', 'placeholder': "text description of this episode's donation recipient"}),
        }

class QuoteForm(forms.ModelForm):

    # These are included for the dynamic podcast and episode dropdowns/comboboxes.
    podcast = forms.ModelChoiceField(queryset=Podcast.objects.all())
    
    # We must override time_quote_begins and time_quote_ends in order for form
    # to validate and clean successfully. If we do not label the fields as CharFields,
    # they will validate as IntegerFields, when the hh:mm:ss format is a string.
    time_quote_begins = forms.CharField(max_length=8)
    time_quote_ends = forms.CharField(max_length=8)
    
    class Meta:
        model = Quote
        exclude = ('rank_score', 'submitted_by',)
        widgets = {
            'episode': forms.Select(attrs={'class':'form-control', 'placeholder': ''}),
            'summary': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'max 200 characters'}),
            'text': forms.Textarea(attrs={'class':'form-control', 'rows':5, 'placeholder': 'Speaker Name: "Type quote in this format, with the name of the speaker followed by the colon symbol (:)."'}),
        }
    
    def __init__(self, *args, **kw):
        super(QuoteForm, self).__init__(*args, **kw)
        self.fields['podcast'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['time_quote_begins'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['time_quote_ends'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        
    def clean_episode(self):
        podcast = self.data.get('podcast')
        episode = self.cleaned_data.get('episode')
        episode_list = Episode.objects.filter(podcast=podcast)
        if episode in episode_list:
            return episode
        else:
            Http404
        
    def clean_time_quote_begins(self):
        begins_with_delims = self.cleaned_data['time_quote_begins']
        converted_time_begins = getSec(begins_with_delims)
        print converted_time_begins
        return converted_time_begins
        
    def clean_time_quote_ends(self):
        ends_with_delims = self.cleaned_data['time_quote_ends']
        converted_time_ends = getSec(ends_with_delims)
        return converted_time_ends

class VoteForm(forms.ModelForm):

    class Meta:
        model = Vote
        
class AllauthSignupForm(forms.Form):
    captcha = ReCaptchaField()
    
    def signup(self, request, user):
        pass

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    def __init__(self, *args, **kw):
        super(UserProfileForm, self).__init__(*args, **kw)
        self.fields['username'].initial = self.instance.username
        self.fields['first_name'].initial = self.instance.first_name
        self.fields['last_name'].initial = self.instance.last_name
        self.fields['email'].initial = self.instance.email
        self.fields['image'].initial = self.instance.userprofile.image
        self.fields['about'].initial = self.instance.userprofile.about
        self.fields['homepage'].initial = self.instance.userprofile.homepage
        self.fields['donate_url'].initial = self.instance.userprofile.donate_url
        self.fields['twitter_url'].initial = self.instance.userprofile.twitter_url
        self.fields['facebook_url'].initial = self.instance.userprofile.twitter_url
        self.fields['instagram_url'].initial = self.instance.userprofile.twitter_url
        self.fields['google_plus_url'].initial = self.instance.userprofile.twitter_url
        self.fields['youtube_url'].initial = self.instance.userprofile.twitter_url
        
        self.fields['username'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['first_name'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['last_name'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['email'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['about'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['homepage'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['donate_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['twitter_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['facebook_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['instagram_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['google_plus_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['youtube_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        
    def save(self, *args, **kw):
        super(UserProfileForm, self).save(*args, **kw)
        self.instance.username = self.cleaned_data.get('username')
        self.instance.first_name = self.cleaned_data.get('first_name')
        self.instance.last_name = self.cleaned_data.get('last_name')
        self.instance.email = self.cleaned_data.get('email')
        self.instance.userprofile.image = self.cleaned_data.get('image')
        self.instance.userprofile.about = self.cleaned_data.get('about')
        self.instance.userprofile.homepage = self.cleaned_data.get('homepage')
        self.instance.userprofile.donate_url = self.cleaned_data.get('donate_url')
        self.instance.userprofile.twitter_url = self.cleaned_data.get('twitter_url')
        self.instance.userprofile.facebook_url = self.cleaned_data.get('facebook_url')
        self.instance.userprofile.instagram_url = self.cleaned_data.get('instagram_url')
        self.instance.userprofile.google_plus_url = self.cleaned_data.get('google_plus_url')
        self.instance.userprofile.youtube_url = self.cleaned_data.get('youtube_url')
        self.instance.save()
        self.instance.userprofile.save()
    
    class Meta:
        model = UserProfile
        exclude = ('user',)
