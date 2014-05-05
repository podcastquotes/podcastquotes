import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProtectThePros.settings")

from ConfigParser import ConfigParser

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.conf import settings

import unittest


### Obtain Config Values ###
config = ConfigParser()
config.read('secrets.cfg')

SITE_DOMAIN = config.get('django.contrib.sites', 'domain')

GOOGLE_SECRET = config.get('GoogleAuth', 'secret')
GOOGLE_CLIENT_ID = config.get('GoogleAuth', 'client_id')

FACEBOOK_SECRET = config.get('FacebookApp', 'secret')
FACEBOOK_CLIENT_ID = config.get('FacebookApp', 'client_id')
### ### ### ### ###

class ConfigFileTests(unittest.TestCase):
    
    def test_that_secret_key_was_changed(self):
        self.assertNotEqual(
            settings.SECRET_KEY,
            'd4(k72p7w7cfm30hy58+ul2z%+k0rplz&79*p&i(t^54__8k6!'
        )
    
    def test_that_debug_is_false(self):
        self.assertEqual(settings.DEBUG, False)
    
    def test_that_template_debug_is_false(self):
        self.assertEqual(settings.TEMPLATE_DEBUG, False)

class SiteTests(unittest.TestCase):
    
    def test_only_one_site_configured(self):
        # I'm not going to handle cases where there is more than one site.
        self.assertEqual(Site.objects.all().count(), 1)
    
    def test_that_site_domain_is_configured(self):
        self.assertEqual(Site.objects.get().domain, SITE_DOMAIN)
        
    def test_that_django_configured_with_existing_site(self):
        self.assertEqual(Site.objects.get().pk, settings.SITE_ID)

class AllAuthConfigTests(unittest.TestCase):
    
    #
    # Google
    #
    
    def test_for_one_google_app(self):
        
        numGoogleApps = SocialApp.objects \
            .filter(provider='google') \
            .count()
        
        self.assertEqual(numGoogleApps, 1)
        
    def test_for_correct_google_secret(self):
        
        secret = SocialApp.objects.get(provider='google').secret
        
        self.assertEqual(secret, GOOGLE_SECRET)
        
    def test_for_correct_google_client_id(self):
        
        client_id = SocialApp.objects.get(provider='google').client_id
        
        self.assertEqual(client_id, GOOGLE_CLIENT_ID)
    
    def test_for_correct_googleapp_site(self):
        
        client_id = SocialApp.objects.get(provider='google').sites.get().pk
        self.assertEqual(client_id, settings.SITE_ID)
    
    #
    # Facebook
    #
    
    def test_for_one_facebook_app(self):
        
        numFacebookApps = SocialApp.objects\
            .filter(provider='facebook')\
            .count()
        
        self.assertEqual(numFacebookApps, 1)
    
    def test_for_correct_facebook_secret(self):
        
        secret = SocialApp.objects.get(provider='facebook').secret
        
        self.assertEqual(secret, FACEBOOK_SECRET)
        
    def test_for_correct_facebook_client_id(self):
        
        client_id = SocialApp.objects.get(provider='facebook').client_id
        
        self.assertEqual(client_id, FACEBOOK_CLIENT_ID)
        
    def test_for_correct_facebookapp_site(self):
        
        client_id = SocialApp.objects.get(provider='facebook').sites.get().pk
        self.assertEqual(client_id, settings.SITE_ID)
        
