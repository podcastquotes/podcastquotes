
from quotes_app.views.podcast import (update_feed, PodcastCreateView)
from quotes_app.views.quote import QuoteCreateView

import unittest
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User

from mock import patch, ANY, MagicMock

import feedparser

from quotes_app.models import Podcast, Episode
from quotes_app.services import PodcastSyndicationService

from core.forms import PodcastCreateForm


class MicroMock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class PatchFeedparserMixin():
    
    expected_feed_title = 'test'
    expected_feed_description = 'test2'
    expected_feed_homepage = 'test3'
    
    def _patch_feedparser(self, 
        path='quotes_app.services.feedparser.parse'):
        
        mock_feedparser_results = MicroMock(
            feed=MicroMock(
                title=self.expected_feed_title,
                description=self.expected_feed_description, 
                link=self.expected_feed_homepage
            ),
            entries=[MicroMock(
                title="Why is yoda so old?",
                publication_date="Thu, 04 Aug 2005 17:02:29 -0400",
                description="Lets find out why yoda won't die quickly.",
                link = "http://starwars.fke/ep/40",
                guid = "http://starwars.fke/ep/40",
                published_parsed=feedparser._parse_date("Thu, 04 Aug 2005 17:02:29 -0400")
            )]
        )

        patcher = patch(path, return_value=mock_feedparser_results)
        self.parse_spy = patcher.start()
        self.addCleanup(patcher.stop)


class UpdateFeedTests(TestCase):
    
    def setUp(self):
        
        self.test_podcast = Podcast()
        
        # patch
        patcher = patch('quotes_app.views.get_object_or_404', 
            return_value=self.test_podcast)
        self.get_spy = patcher.start()
        self.addCleanup(patcher.stop)
        
        
        patcher = patch(
            'quotes_app.views.podcast_syndication_service.collect_episodes', 
            return_value="hi")
        self.parse_spy = patcher.start()
        self.addCleanup(patcher.stop)
    
    def test_update_feed_invokes_episode_collection(self):
        
        # Arrange
        user=User()
        r=RequestFactory()
        r.user = user
        
        # Act
        update_feed(r, 0)
        
        # Assert
        self.assertTrue(self.get_spy.called)
        self.assertTrue(self.parse_spy.called)
        
        parse_call_arg = self.parse_spy.call_args[0][0]
        self.assertEqual(parse_call_arg, self.test_podcast,
            "Episodes collected for test_podcast")


class PodcastCreateViewTests(TestCase, PatchFeedparserMixin):
    """ 
    Adding tests to this module after it was built.  It's definitely
    not comprehensive
    """
    
    def setUp(self):
        
        self.patch_obtain_podcast_information()
        
        # Arrange the form inputs.
        self.test_create_form = {
            'rss_url': 'http://example.com/rss',
            'title': 'Example Podcast',
            'description': 'We study baboons.',
            'homepage': 'http://example.com',
            'donate_url': 'http://example.com/donate',
            'twitter_url': 'http://example.com/twitter',
            'facebook_url': 'http://example.com/facebook',
            'instagram_url': 'http://example.com/instagram',
            'google_plus_url': 'http://example.com/g+',
            'youtube_url': 'http://example.com/youtube',
        }
        
        self.form = PodcastCreateForm(self.test_create_form)
        
        # The module under test
        self.podcast_create_view = PodcastCreateView()
        
        # Mock/stub this call.. it's touching too many other things
        self.podcast_create_view.get_success_url = lambda: \
            "test_redirect_url"
            
        self.act()
        
    def patch_obtain_podcast_information(self):
        
        self.test_rss_title = title = 'TEST!'
        self.test_rss_description = description = 'TEST123!'
        self.test_rss_homepage = homepage = 'test123123123'
        
        patcher = patch(
            'quotes_app.views.podcast_syndication_service.' + 
            'obtain_podcast_information', 
            return_value={
                'title':       title,
                'description': description,
                'homepage':    homepage
            })
        self.obtain_info_spy = patcher.start()
        self.addCleanup(patcher.stop)

    def act(self):
        self.podcast_create_view.form_valid(self.form)

    def test_that_podcast_information_retrieved(self):
        
        self.assertTrue(self.obtain_info_spy.called, 
            "obtain_podcast_information never called")
        
        first_parameter = self.obtain_info_spy.call_args[0][0]
        self.assertEqual(first_parameter, 
            self.test_create_form['rss_url'],
            "rss_url from the form was not used with" +
            " the syndication service")
            
    def test_podcast_creation_w_rss_feed(self):

        # Get the only Podcast in the database
        podcast = Podcast.objects.all().first()

        # Assert that fields were populated with the rss feed
        self.assertEqual(podcast.rss_url, self.test_create_form['rss_url'],
            "rss_url not saved as intended")
            
        self.assertEqual(podcast.title, self.test_rss_title,
            "Podcast title should be from rss")
            
        self.assertEqual(
            podcast.description, 
            self.test_rss_description,
            "Podcast description should be from rss")
        
        self.assertEqual(podcast.homepage, self.test_rss_homepage,
            "Podcast homepage should be from rss")
        
        # Check that the other fields were populated
        for key in [
            'donate_url', 'twitter_url', 'facebook_url', 
            'instagram_url', 'google_plus_url', 'youtube_url']:
                
            self.assertEqual(getattr(podcast, key), 
                self.test_create_form[key])
                
class PodcastSyndicationService_podcast_info_Tests(TestCase, 
    PatchFeedparserMixin):
    
    def setUp(self):
        
        self.expected_feed_title = 'Star wars podcast!'
        self.expected_feed_description = 'It\'s a star wars podcast'
        self.expected_feed_homepage = 'http://starwars.fke'
    
        self._patch_feedparser()
        
        self.act()
    
    def act(self):
        
        self.svc = svc = PodcastSyndicationService()
        
        self.feed_url = 'http://starwars.fke/rss'
        
        self.podcast_info = \
            svc.obtain_podcast_information(self.feed_url)
    
    def test_feedparser_parse_called(self):
        
        self.assertTrue(self.parse_spy.called)
        
        feed_param = self.parse_spy.call_args[0][0]
        
        self.assertEqual(self.feed_url, feed_param)
    
    def test_returned_dictionary_correct(self):
        
        self.assertEqual(self.podcast_info.get('title'), 
            self.expected_feed_title)
            
        self.assertEqual(self.podcast_info.get('description'),
            self.expected_feed_description)
            
        self.assertEqual(self.podcast_info.get('homepage'),
            self.expected_feed_homepage)


class PodcastSyndicationServiceIntegrationTests(TestCase):
    
    test_title = "Winner Winner"
    test_url = "http://example.com/winner-winner"
    test_guid = "http://example.com/p/3"
    test_description = "<p>Chicken dinner.</p>"
    test_pubdate = "Thu, 04 Aug 2015 17:02:29 -0400"
    
    test_rss_document = """
    <?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">

    <channel>
      <title>Example RSS Feed</title>
      <link>http://example.com/rss</link>
      <description>Booyah</description>
      <item>
        <title>{title}</title>
        <link>{link}</link>
        <description>{description}</description>
        <guid>{guid}</guid>
        <pubDate>{pubdate}</pubDate>
      </item>
    </channel>

    </rss>
    """.format(
        title=test_title,
        link=test_url,
        description=test_description,
        pubdate=test_pubdate,
        guid=test_guid
    )
    
    def test_episode_collection_from_rss(self):
        
        # Arrange
        podcast = Podcast(id=0, rss_url=self.test_rss_document)
        podcast.save()
        
        # Act
        svc = PodcastSyndicationService()
        svc.collect_episodes(podcast)
        
        # Assert
        podcast_episodes = Episode.objects.filter(podcast=podcast)
        
        self.assertEqual(len(podcast_episodes), 1,
            "There should be one episode from this import")
        
        # Check to see if fields of episode are correct.
        episode = podcast_episodes[0]
        
        self.assertEqual(episode.title, self.test_title)
        self.assertEqual(episode.episode_url, self.test_url)
        self.assertEqual(episode.description, "Chicken dinner.",
            "HTML tags should be stripped from the description")
        self.assertEqual(episode.guid, self.test_guid)
        

class QuoteCreateTests(TestCase):
    
    def setUp(self):
        
        self.request_factory = RequestFactory()
        
        # Create a podcast and episode in the database.
        p = Podcast.objects.create()
        
        self.episode = Episode.objects.create(
            podcast=p, 
            # Form's queryset is filtered to only show with youtube url
            youtube_url="http://youtube.com/asdf")
        
    def act(self):

        request = self.request_factory.post('/whatever', self.form_data)
        request.user = User.objects.create()

        quote_create(request)
    
    def test_no_error_case(self):
        """ Wiring test to exsiting code for the happy case."""

        self.form_data = {
            'episode': self.episode.pk,
            'summary': 'asdf',
            'text': 'asdf',
            'time_quote_ends': '02:03:04',
            'time_quote_begins': '02:03:10' 
        }
        
        self.act()
        
    @unittest.expectedFailure
    def test_with_no_quote_end(self):
        
        self.form_data = {
            'episode': self.episode.pk,
            'summary': 'asdf',
            'text': 'asdf',
            'time_quote_ends': '02:03:04',
            'time_quote_begins': '' 
        }
        
        self.act()
