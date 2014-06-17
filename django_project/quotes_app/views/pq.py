from django.shortcuts import render
from quotes_app.models import Podcast

def about_pq(request):
    return render(request, 'about.html',
                 {'podcasts': Podcast.objects.all().order_by('title')})
                 
def claim_page(request):
    return render(request, 'claim-page.html',
                 {'podcasts': Podcast.objects.all().order_by('title')})
                 
def contact_pq(request):
    return render(request, 'contact.html',
                 {'podcasts': Podcast.objects.all().order_by('title')})
                 
def support_pv(request):
    return render(request, 'support-pv.html',
                 {'podcasts': Podcast.objects.all().order_by('title')})