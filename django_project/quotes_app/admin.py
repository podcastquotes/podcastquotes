from django.contrib import admin
from django.contrib.auth.models import User
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    
class UserAdmin(admin.ModelAdmin):
    inlines = [UserProfileInline]

admin.site.register(User, UserAdmin)

class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('podcast', 'title', 'youtube_url')
    list_editable = ('youtube_url',)
    
admin.site.register(Episode, EpisodeAdmin)

for model in [Podcast, Quote, Vote]:
    admin.site.register(model)