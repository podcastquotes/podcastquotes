from datetime import datetime, date
from time import mktime
from django.shortcuts import redirect
from quotes_app.models import Quote

today = date.today()

def rank_all(request):
    for quote in Quote.quote_vote_manager.all():
        quote.set_rank()

    return redirect('/')