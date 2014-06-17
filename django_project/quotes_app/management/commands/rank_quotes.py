from django.core.management.base import BaseCommand, CommandError
from quotes_app.tasks import rank_all
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    
    help = 'Runs reranking algorithms on the Quotes.'

    def handle(self, *args, **options):
        logger.info('Running {0} management task.'.format(__name__))
        rank_all()
            
