from django.core.management.base import BaseCommand, CommandError

import unittest
import sys

from core import deploy_tests

class Command(BaseCommand):
    
    help = 'Inserts some values into the database'

    def handle(self, *args, **options):

        loader = unittest.TestLoader()
        
        suite = loader.loadTestsFromModule(deploy_tests)
        
        runner = unittest.TextTestRunner()
        
        runner.run(suite)

