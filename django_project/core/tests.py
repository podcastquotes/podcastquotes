from django.test import TestCase, Client
from django.contrib.admin.sites import AlreadyRegistered

class PageTest(TestCase):

    def test_app_configured_correctly(self):
        """
        Order of INSTALLED_APPS was causing the app not to work
        when making any request
        """
        
        client = Client()
        
        try:
            response = client.get('/')
        except AlreadyRegistered as e:
            self.fail('Admin model registrations are in conflict: ' 
                + str(e) + '. Ensure correct order of INSTALLED_APPS')
        
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.is_rendered)
        
    

    
      
        
    
        
    
