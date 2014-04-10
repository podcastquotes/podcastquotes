from django.contrib import admin
from podcastquotes.models import Podcast, Episode, PersonQuoted, Tag, Quote

for model in [Podcast, Episode, PersonQuoted, Tag, Quote]:
    admin.site.register(model)