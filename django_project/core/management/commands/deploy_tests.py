from django.core.management.base import BaseCommand, CommandError

import unittest
import sys

from core import deploy_tests

class Command(BaseCommand):
    
    help = 'Tests that configured deployment is working ' + \
           ' to some degree.'

    def handle(self, *args, **options):

        loader = unittest.TestLoader()
        
        suite = loader.loadTestsFromModule(deploy_tests)
        
        runner = unittest.TextTestRunner()
        
        runner.run(suite)

