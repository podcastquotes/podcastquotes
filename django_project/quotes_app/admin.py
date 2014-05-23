from django.contrib import admin
from django.contrib.auth.models import User
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    
class UserAdmin(admin.ModelAdmin):
    inlines = [UserProfileInline]

admin.site.register(User, UserAdmin)

for model in [Podcast, Episode, Quote, Vote]:
    admin.site.register(model)