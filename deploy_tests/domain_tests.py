import requests
import unittest

class TestDomainRedirections(unittest.TestCase):
    
    # Which domains should we test for 
    # redirects on www.domain.tld and domain.tld ?
    domains = [
        'podcastquotes.com', 
        'podquotes.org', 
        'podclips.us',
        'podcastquo.com', 
        'demipod.com']
    
    # Any additional uris to test explicitly?
    uris = ['http://www.podverse.tv']
    
    # Where should all these domain names go?
    redirect_uri = 'http://podverse.tv'
    
    def setUp(self):
        self.errors = []
    
    def _test_url_redirects(self, url):
        
        r = requests.get(url,
            allow_redirects=False)
        
        try:
            self.assertEqual(302, r.status_code,
                "{0} did not redirect to {1} :: {2}" \
                    .format(url, self.redirect_uri, r))
            self.assertEqual(r.headers['location'], self.redirect_uri)
            
        except AssertionError as e:
            self.errors.append(e)
    
    def _generate_uris_to_test(self):
        uri = '{proto}://{host}{domain}'
        
        uris = []
        
        for domain in self.domains:
            uris.append(uri.format(proto='http', host='', 
                domain=domain))
            uris.append(uri.format(proto='http', host='www.', 
                domain=domain))
            
        uris.extend(self.uris)
        
        for uri in uris:
            self._test_url_redirects(uri)

    def test_domain_redirections(self):
        
        uris = self._generate_uris_to_test()
        
        # Fail if it wasn't successful
        if len(self.errors) > 0:
            self.fail(self.errors)
        

if __name__ == '__main__':
    unittest.main()
