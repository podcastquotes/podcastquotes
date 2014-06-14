from django.core.management.base import BaseCommand, CommandError
from quotes_app.tasks import update_rss_feeds
class Command(BaseCommand):
    
    help = 'Checks all RSS feeds and updates with new episodes.'

    def handle(self, *args, **options):
        update_rss_feeds()
            
