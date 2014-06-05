from django.shortcuts import render
from quotes_app.models import Podcast

def about(request):
    return render(request, 'about.html',
                 {'podcasts': Podcast.objects.all().order_by('title')})
                 
def claim_page(request):
    return render(request, 'claim-page.html',
                 {'podcasts': Podcast.objects.all().order_by('title')})