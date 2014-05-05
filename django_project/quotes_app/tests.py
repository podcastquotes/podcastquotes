
from quotes_app.views import update_feed, PodcastCreateView


from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User

from mock import patch, ANY

import feedparser

from quotes_app.models import Podcast, Episode
from quotes_app.services import PodcastSyndicationService

class MicroMock(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


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
        


class PatchFeedparserMixin():
    
    def _patch_feedparser(self):
        
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

        patcher = patch('quotes_app.services.feedparser.parse', 
            return_value=mock_feedparser_results)
        self.parse_spy = patcher.start()
        self.addCleanup(patcher.stop)


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
        
        

    
    
