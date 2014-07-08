from django import forms
from django.contrib.auth import get_user_model
from django.db import models
from django.forms import ModelForm
from django.http import Http404
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile
from quotes_app.fields import EpisodeField
from captcha.fields import ReCaptchaField

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
            'support_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'twitter_url': forms.URLInput(attrs={'class':'form-control', 'placeholder':''}),
            'facebook_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'instagram_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'google_plus_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'tumblr_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'youtube_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'reddit_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
        }

class PodcastForm(forms.ModelForm):
    
    class Meta:
        model = Podcast
        exclude = ('moderators',)
        widgets = {
            'rss_url': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder': ''}),
            'keywords': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
            'homepage': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'support_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'twitter_url': forms.URLInput(attrs={'class':'form-control', 'placeholder':''}),
            'facebook_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'instagram_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'google_plus_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'tumblr_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'youtube_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
            'reddit_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': ''}),
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
            'support_url': forms.URLInput(attrs={'class':'form-control', 'placeholder': 'link to support for this episode'}),
            'support_recipient': forms.TextInput(attrs={'class':'form-control', 'placeholder':'name of recipient (will appear as banner on clip page)'}),
            'support_recipient_about': forms.Textarea(attrs={'class':'form-control', 'placeholder': "description of recipient (will appear on banner on clip page)"}),
        }

class QuoteForm(forms.ModelForm):
    
    # We must override time_quote_begins and time_quote_ends in order for form
    # to validate and clean successfully. If we do not label the fields as CharFields,
    # they will validate as IntegerFields, when the hh:mm:ss format is a string.
    time_quote_begins = forms.CharField(max_length=8, required=True)
    time_quote_ends = forms.CharField(max_length=8, required=False)
    
    class Meta:
        model = Quote
        exclude = ('rank_score', 'submitted_by')
        widgets = {
            'summary': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'max 200 characters'}),
            'text': forms.Textarea(attrs={'class':'form-control', 'rows':5, 'placeholder': 'Speaker Name: "Type quote in this format."'}),
        }

    def __init__(self, *args, **kw):
        super(QuoteForm, self).__init__(*args, **kw)

        # Tech Debt? Do we have to do this now that I'm defining the
        # form explicitly?
        self.fields['time_quote_begins'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['time_quote_ends'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
    
    def clean_time_quote_begins(self):
        begins_with_delims = self.cleaned_data['time_quote_begins']
        converted_time_begins = getSec(begins_with_delims)
        return converted_time_begins
        
    def clean_time_quote_ends(self):
        if self.cleaned_data['time_quote_ends']:
            ends_with_delims = self.cleaned_data['time_quote_ends']
            converted_time_ends = getSec(ends_with_delims)
            return converted_time_ends

class QuoteCreateForm(QuoteForm):
    episode = EpisodeField()

class QuoteUpdateForm(QuoteForm):
    class Meta:
        model = Quote
        exclude = ('episode', 'rank_score', 'submitted_by')
        widgets = {
            'summary': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'max 200 characters'}),
            'text': forms.Textarea(attrs={'class':'form-control', 'rows':5, 'placeholder': 'Speaker Name: "Type quote in this format."'}),
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
        ### Stuff below can be revisited after AUTH_USER_MODEL is successfully configured.
        # self.fields['image'].initial = self.instance.userprofile.image
        # self.fields['about'].initial = self.instance.userprofile.about
        # self.fields['homepage'].initial = self.instance.userprofile.homepage
        # self.fields['support_url'].initial = self.instance.userprofile.support_url
        # self.fields['twitter_url'].initial = self.instance.userprofile.twitter_url
        # self.fields['facebook_url'].initial = self.instance.userprofile.twitter_url
        # self.fields['instagram_url'].initial = self.instance.userprofile.twitter_url
        # self.fields['google_plus_url'].initial = self.instance.userprofile.twitter_url
        # self.fields['youtube_url'].initial = self.instance.userprofile.twitter_url
        
        self.fields['username'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['first_name'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['last_name'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        self.fields['email'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        ### Stuff below can be revisited after AUTH_USER_MODEL is successfully configured.
        # self.fields['about'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        # elf.fields['homepage'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        # self.fields['support_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        # self.fields['twitter_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        # self.fields['facebook_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        # self.fields['instagram_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        # self.fields['google_plus_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        # self.fields['youtube_url'].widget.attrs.update({'class' : 'form-control', 'placeholder': ''})
        
    def save(self, *args, **kw):
        super(UserProfileForm, self).save(*args, **kw)
        self.instance.username = self.cleaned_data.get('username')
        self.instance.first_name = self.cleaned_data.get('first_name')
        self.instance.last_name = self.cleaned_data.get('last_name')
        self.instance.email = self.cleaned_data.get('email')
        self.instance.save()
        
        ### Stuff below can be revisited after AUTH_USER_MODEL is successfully configured.
        # self.instance.userprofile.image = self.cleaned_data.get('image')
        # self.instance.userprofile.about = self.cleaned_data.get('about')
        # self.instance.userprofile.homepage = self.cleaned_data.get('homepage')
        # self.instance.userprofile.support_url = self.cleaned_data.get('support_url')
        # self.instance.userprofile.twitter_url = self.cleaned_data.get('twitter_url')
        # self.instance.userprofile.facebook_url = self.cleaned_data.get('facebook_url')
        # self.instance.userprofile.instagram_url = self.cleaned_data.get('instagram_url')
        # self.instance.userprofile.google_plus_url = self.cleaned_data.get('google_plus_url')
        # self.instance.userprofile.youtube_url = self.cleaned_data.get('youtube_url')
        # self.instance.userprofile.save()
    
    class Meta:
        model = UserProfile
        exclude = ('user',)
