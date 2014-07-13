"""
I have not been able to figure out how to use a base class to inherit template_names for the full/slim view types. Will be using a WET solution to resolve this.

from django.views.generic import ListView
from quotes_app.models import Podcast, Episode, Quote, Vote, UserProfile

class PVListView(ListView):
    model = Quote
    
    def get_template_names(self):
        view_type = self.request.COOKIES.get('view_type')
        if view_type == 'full':
            return template_name
        elif view_type == 'slim':
            return 'slim_' + template_name
            
"""