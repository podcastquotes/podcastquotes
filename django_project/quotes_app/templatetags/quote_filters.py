from django import template
from quotes_app.models import Podcast, Episode, Quote, Vote, SavedQuote
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()

@register.filter
def is_true(arg):
    return arg is True

@register.filter(name="is_saved_quote")
def is_saved_quote(quote_id, saver_id):
    try:
        sq = SavedQuote.objects.get(quote_id=quote_id, saver_id=saver_id)
        return True
    except ObjectDoesNotExist:
        return False

@register.filter(name="is_less_than_X_characters")
def is_less_than_X_characters(val, total_characters):
    q = Quote.objects.get(id=val)
    if len(q.text) < total_characters:
        return True
    else:
        return False

@register.filter(name='class_if_upvote_active')
def class_if_upvote_active(val, user_id):
    v = Vote.objects.filter(voter_id=user_id).filter(quote_id=val).first()
    if v == None:
        return ""
    else:
        if v.vote_type == 1:
            return "pq-quote-upvote-active"
        else:
            return ""
        
@register.filter(name='class_if_downvote_active')
def class_if_downvote_active(val, user_id):
    v = Vote.objects.filter(voter_id=user_id).filter(quote_id=val).first()
    if v == None:
        return ""
    else:
        if v.vote_type == -1:
            return "pq-quote-downvote-active"
        else:
            return ""