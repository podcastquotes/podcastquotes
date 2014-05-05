from django.core.management.base import BaseCommand, CommandError
from ConfigParser import ConfigParser

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def init_configuration():
    
    ### Obtain Config Values ###
    config = ConfigParser()
    config.read('secrets.cfg')

    SITE_DOMAIN = config.get('django.contrib.sites', 'domain')

    GOOGLE_SECRET = config.get('GoogleAuth', 'secret')
    GOOGLE_CLIENT_ID = config.get('GoogleAuth', 'client_id')

    FACEBOOK_SECRET = config.get('FacebookApp', 'secret')
    FACEBOOK_CLIENT_ID = config.get('FacebookApp', 'client_id')
    
    ### ### ### ### ###


    # I'm going to assume that there is an existing site defined.
    # Lets obtain it and modify the values.
    site = Site.objects.get()
    site.domain = SITE_DOMAIN
    site.name = SITE_DOMAIN
    site.save()

    # Add Google SocialApp
    google = SocialApp(
        provider='google',
        secret=GOOGLE_SECRET,
        client_id=GOOGLE_CLIENT_ID,
        name='Google Auth'
    )
    google.save()

    # Add Facebook SocialApp
    facebook = SocialApp(
        provider = 'facebook',
        secret=FACEBOOK_SECRET,
        client_id=FACEBOOK_CLIENT_ID,
        name='Facebook App'
    )
    facebook.save()

    # Associate Django site with Apps
    google.sites.add(site)
    facebook.sites.add(site)


class Command(BaseCommand):
    
    help = 'Inserts some values into the database'

    def handle(self, *args, **options):
        init_configuration()
            
