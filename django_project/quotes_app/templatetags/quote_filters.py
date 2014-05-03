from django import template
from quotes_app.models import Podcast, Episode, Quote, Vote

register = template.Library()

# @register.filter(name='impression_enum_to_string')
# def impression_enum_to_string(val):
#    
#    if val == Review.POSITIVE_IMPRESSION:
#        return "Positive"
#    
#    elif val == Review.NEGATIVE_IMPRESSION:
#        return "Negative"
#    
#    else:
#        return ""

@register.filter(name='vote_is_upvote')
def vote_is_upvote(val):
    
    if val == Vote.UPVOTE:
        return "pq-upvote-active"
        
    else:
        return ""
        
@register.filter(name='vote_is_downvote')
def vote_is_downvote(val):

    if val == Vote.DOWNVOTE:
        return "pq-downvote-active"
        
    else:
        return ""
