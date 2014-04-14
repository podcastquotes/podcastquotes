from django.contrib import admin
from podcastquotes.models import Podcast, Episode, Quote

for model in [Podcast, Episode, Quote]:
    admin.site.register(model)