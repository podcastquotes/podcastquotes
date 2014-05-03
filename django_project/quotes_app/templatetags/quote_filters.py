from django import template
from quotes_app.models import Podcast, Episode, Quote, Vote
from django.contrib.auth.models import User

register = template.Library()

@register.filter(name='class_if_upvote_active')
def class_if_upvote_active(val, user_id):
    v = Vote.objects.filter(voter_id=user_id).filter(quote_id=val).first()
    if v.vote_type == 1:
        return "pq-quote-upvote-active"
    else:
        return ""
        
@register.filter(name='class_if_downvote_active')
def class_if_downvote_active(val, user_id):
    v = Vote.objects.filter(voter_id=user_id).filter(quote_id=val).first()
    if v.vote_type == -1:
        return "pq-quote-downvote-active"
    else:
        return ""