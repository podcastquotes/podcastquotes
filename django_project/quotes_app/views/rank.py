from datetime import datetime, date
from time import mktime


today = date.today()

def rank_all(request):
    for quote in Quote.quote_vote_manager.all():
        quote.set_rank()

    return redirect('/')