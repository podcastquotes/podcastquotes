from django import forms
from django.db import models
from django.forms import ModelForm
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile
from captcha.fields import ReCaptchaField
from django.contrib.auth import get_user_model

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
            'youtube_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
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
            'youtube_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
        }

class QuoteCreateForm(forms.ModelForm):
    
    class Meta:
        model = Quote
        widgets = {
            'episode': forms.Select(attrs={'class':'form-control'}),
            'summary': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'max 200 characters'}),
            'text': forms.Textarea(attrs={'class':'form-control', 'rows':6, 'placeholder': 'Speaker Name: "Type quote in this format, with the name of the speaker followed by the colon symbol (:)."'}),
            'time_quote_begins': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'hh:mm:ss'}),
            'time_quote_ends': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'hh:mm:ss'}),
        }

class QuoteForm(forms.ModelForm):
   
    class Meta:
        model = Quote
        widgets = {
            'episode': forms.Select(attrs={'class':'form-control'}),
            'summary': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'max 200 characters'}),
            'text': forms.Textarea(attrs={'class':'form-control', 'rows':6, 'placeholder': 'Speaker Name: "Type quote in this format, with the name of the speaker followed by the colon symbol (:)."'}),
            'time_quote_begins': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'hh:mm:ss'}),
            'time_quote_ends': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'hh:mm:ss'}),
        }

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
