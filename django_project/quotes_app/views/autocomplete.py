from django import shortcuts

from quotes_app.models import Podcast, Episode

def navigation_autocomplete(request,
    template_name='navigation_autocomplete/autocomplete.html'):
    
    q = request.GET.get('q', '')
    context = {'q' : q}
    
    queries = {}
    queries['nav_podcasts'] = Podcast.objects.filter(title__icontains=q)[:5]
    queries['nav_episodes'] = Episode.objects.filter(title__icontains=q)[:10]
    context.update(queries)
    
    return shortcuts.render(request, template_name, context)