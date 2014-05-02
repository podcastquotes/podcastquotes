from django.contrib import admin
from quotes_app.models import Podcast, Episode, Quote, Vote

for model in [Podcast, Episode, Quote, Vote]:
    admin.site.register(model)