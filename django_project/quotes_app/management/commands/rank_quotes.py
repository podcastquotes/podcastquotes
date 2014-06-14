from django.core.management.base import BaseCommand, CommandError
from quotes_app.tasks import rank_all
class Command(BaseCommand):
    
    help = 'Runs reranking algorithms on the Quotes.'

    def handle(self, *args, **options):
        rank_all()
            
