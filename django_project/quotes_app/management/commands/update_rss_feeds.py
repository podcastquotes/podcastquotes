from django.core.management.base import BaseCommand, CommandError
from quotes_app.tasks import update_rss_feeds
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    
    help = 'Checks all RSS feeds and updates with new episodes.'

    def handle(self, *args, **options):
        logger.info('Running {0} management task.'.format(__name__))
        update_rss_feeds()
            
