
from quotes_app.views.podcast import (update_feed, PodcastCreateView)
from quotes_app.views.quote import QuoteCreateView

import unittest
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.client import RequestFactory, Client
from django.contrib.auth.models import User

from mock import patch, ANY, MagicMock

import feedparser

from quotes_app.models import Podcast, Episode
from quotes_app.services import PodcastSyndicationService
from quotes_app.widgets import EpisodeEstablisherWidget
from quotes_app.fields import EpisodeField

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
        
        self.test_podcast = Podcast.objects.create()
        
        # patch
        patcher = patch('quotes_app.views.podcast.get_object_or_404', 
            return_value=self.test_podcast)
        self.get_spy = patcher.start()
        self.addCleanup(patcher.stop)
        
        
        patcher = patch(
            'quotes_app.views.podcast.podcast_syndication_service.collect_episodes', 
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
        
        self.configure_request()
        
        # Mock/stub this call.. it's touching too many other things
        self.podcast_create_view.get_success_url = lambda: \
            "test_redirect_url"
            
        self.act()
        
    def configure_request(self):
        
        self.podcast_create_view.request = \
            RequestFactory().post('/what/ever/')
        
        # Make authenticated user for this request.
        self.podcast_create_view.request.user = User.objects.create()
    
    def patch_obtain_podcast_information(self):
        
        self.test_rss_title = title = 'TEST!'
        self.test_rss_description = description = 'TEST123!'
        self.test_rss_homepage = homepage = 'test123123123'
        
        patcher = patch(
            'quotes_app.views.podcast.podcast_syndication_service.' + 
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
        
        # The module under test
        self.quote_create_view = QuoteCreateView()
        
        # Mock/stub this call.. it's touching too many other things
        # and begins loading admin site crap *brain explode*
        self.quote_create_view.get_success_url = lambda: \
            "test_redirect_url"
        
    def act(self):

        request = self.request_factory.post('/whatever', self.form_data)
        request.user = User.objects.create()
        
        # Wire up class based view and process the test request.
        self.quote_create_view.request = request
        self.quote_create_view.dispatch(request)
    
    def test_no_error_case(self):
        """ Wiring test to exsiting code for the happy case."""

        self.form_data = {
            # Widget data
            'episode_episode_id': self.episode.podcast.pk,
            'episode_episode_title': self.episode.title,
            'episode_podcast_title': self.episode.podcast.title,
            'episode_podcast_id': self.episode.pk,
            
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

    @unittest.expectedFailure
    def test_success_currently_authenticated_user_added_as_mod(self):
        self.fail("Behavior not tested")

    @unittest.expectedFailure
    def test_success_redirects_to_success_url(self):
        self.fail("Behavior not tested")

class EpisodeFieldTests(TestCase):
    
    def setUp(self):
        
        podcast = Podcast.objects.create(
            id=300303,
            title='My_test_podcast'
        )
        
        Episode.objects.create(
            id=4034,
            podcast=podcast,
            title='Hork',
            episode_url='http://test'
        )
        
        self.field = EpisodeField()
    
    def test_that_no_provided_podcast_fails(self):
        
        value = ('', '', 234, 'myEpisode')
        
        def test():
            self.field.to_python(value)
            
        self.assertRaises(ValidationError, test)
        
    def test_that_no_provided_episode_fails(self):
        
        value = ('234', 'Rogannn', '', '')
        
        def test():
            self.field.to_python(value)
            
        self.assertRaises(ValidationError, test)
        
    
    def test_when_episode_doesnt_exist(self):
        
        value = ('300303', 'My_test_podcast', '', 'fff')
        
        return_value = self.field.to_python(value)
        
        # Asserts
        try:
            database_episode = Episode.objects.get(title='fff')
        except Episode.DoesNotExist:
            self.fail('Episode was not created when it should have.')
        
        self.assertEqual(return_value, database_episode,
            'to_python did not return the episode created')
        
    def test_when_episode_exists(self):
        
        value = ('300303', 'Fried Podcast', '4034', 'Flaffy!')
        
        result = self.field.to_python(value)
        
        self.assertIsEpisode(result,
            "to_python did not return an Episode")
        
        self.assertEqual(result.title, 'Hork')
        self.assertEqual(result.episode_url, 'http://test')
    
    def test_when_podcast_doesnt_exist(self):
        
        value = ('', 'This is a new podcast', '', 'FHHOO')
        
        result = self.field.to_python(value)


        try:
            episode = Episode.objects.get(title='FHHOO')
        except Episode.DoesNotExist:
            self.fail('episode was not created')
        
        self.assertEqual(episode.podcast.title, 
            'This is a new podcast')
                
        self.assertIsEpisode(result)
        self.assertEqual(result, episode)
        
    def test_that_invalid_podcast_pk_fails(self):
        value = ('999', '', '', 'Flaffy!')
        
        def test():
            self.field.to_python(value)

        self.assertRaises(ValidationError, test)
    
    def test_that_invalid_episode_pk_fails(self):
        
        value = ('999', '', '1234', 'Fluffy!')
        
        def test():
            self.field.to_python(value)
    
        self.assertRaises(ValidationError, test)
    #
    ## Helper assert methods
    #
    def assertIsEpisode(self, obj, msg='value is not an episode'):
        self.assertTrue(type(obj) is Episode, msg)
        

class EpisodeEstablisherWidgetTests(TestCase):
    
    def setUp(self):
        # Patch render_to_string at some point
        self.widget = EpisodeEstablisherWidget()
        
    def test_render_produces_html(self):
        name = 'foowidget'
        value = ('33', 'testpodcasttitle', '449', 'testepisodetitle')
        result = self.widget.render(name, value, attrs=None)
        
    def test_value_from_datadict_returns_tuple(self):
        
        name = 'foowidget'
        
        data = { 
            self.widget.get_episode_id_form_name(name): 'eid',
            self.widget.get_episode_title_form_name(name): 'etitle',
            self.widget.get_podcast_id_form_name(name): 'pid',
            self.widget.get_podcast_title_form_name(name): 'ptitle',
        }
        
        result = self.widget.value_from_datadict(data, None, name)
        
        self.assertEqual(result[0], 'pid')
        self.assertEqual(result[1], 'ptitle')
        self.assertEqual(result[2], 'eid')
        self.assertEqual(result[3], 'etitle')
        
    def test_when_render_is_passed_None_value(self):
        
        name = 'fooowidget'
        value = None
        
        result = self.widget.render(name, value)
        
    def test_x(self):
        pass
        #self.fail(self.widget.media)

from quotes_app.views.episode import thin_json_episode_query
from quotes_app.views.podcast import thin_json_podcast_query

import json

class EpisodeListJSONEndpointTests(TestCase):
    
    def setUp(self):
        
        self.test_podcast = Podcast.objects.create(title='TestPodcast')
        
        # Assemble
        
        for i in range(0,10):
            Episode.objects.create(
                podcast=self.test_podcast,
                title='Episode {0}'.format(i)
            )
        
        self.req_factory = RequestFactory()
        
    def perform_request(self, podcast_id, query):
        
        url = '/episodes/json?podcast_id={0}&q={1}' \
            .format(podcast_id, query)
            
        req = self.req_factory.get(url)
        
        resp = thin_json_episode_query(req)
        resp = json.loads(resp.content)
        
        return resp
    
    def test_basic_query(self):
    
        resp = self.perform_request(self.test_podcast.id, 'Episode')
        
        # Assert
        self.assertEqual(10, len(resp),
            "Didn't return 10 episodes")
        
        for e in resp:
            try:
                e['id']
                e['title']
            except KeyError as e:
                self.fail('Did not find key "{0}" in all episodes'\
                    .format(e.message))
    
    def test_no_podcast_query(self):
        
        resp = self.perform_request(9999, 'blah')
        
        self.assertEqual(0, len(resp),
            "It didn't return an empty array")
            
    def test_with_empty_podcast(self):
        
        resp = self.perform_request('', 'FASDF')
        
        # Shouldn't throw errors
            
    def test_endpoint_returns_200(self):
        c = Client()
        r = c.get('/episodes/json?podcast_id=1&q=Episode 3')
        
        self.assertEqual(200, r.status_code)
    
class PodcastListJSONEndpointTests(TestCase):
    
    def setUp(self):
        
        self.test_podcast = Podcast.objects.create(title='TestPodcast')
        
        # Assemble
        
        for i in range(0,10):
            Podcast.objects.create(
                title='Podcast {0}'.format(i)
            )
        
        self.req_factory = RequestFactory()
        
    def perform_request(self, query):
        
        url = '/podcasts/json?q={0}' \
            .format(query)
            
        req = self.req_factory.get(url)
        
        resp = thin_json_podcast_query(req)
        resp = json.loads(resp.content)
        
        return resp
    
    def test_basic_query(self):
    
        resp = self.perform_request('Podcast')
        
        # Assert
        self.assertEqual(10, len(resp),
            "Didn't return 10 podcasts")
        
        for e in resp:
            try:
                e['id']
                e['title']
            except KeyError as e:
                self.fail('Did not find key "{0}" in all episodes'\
                    .format(e.message))
    
    def test_endpoint_returns_200(self):
        c = Client()
        r = c.get('/podcasts/json?q=Podcast')
        
        self.assertEqual(200, r.status_code)
        
        
